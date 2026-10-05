import json
import uuid
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import Product, Category, Collection, Banner, Address, Customer, Subscriber, Metric, StoreSettings
from .forms import RegisterForm, EmailLoginForm, CheckoutForm, AddressForm, ProfileForm
from .services import (CommerceError, cart_lines, create_order, start_payment, eligible_shipping,
    owned_orders, owner_hash, handle_payment, settle, expire_demo_orders, coupon_discount)

def home(request):
    products = Product.objects.filter(active=True, featured=True).order_by('-created').prefetch_related('photos','variants')[:8]
    return render(request, 'home.html', {'products': products, 'banners': Banner.objects.filter(active=True).select_related('collection')[:3],
        'featured_collections':Collection.objects.filter(slug__in=['street-culture','alfaiataria-livre','denim','statement']).order_by('pk')})

def catalog(request):
    products = Product.objects.filter(active=True).select_related('category').prefetch_related('photos','variants')
    q = request.GET.get('q','')[:100]
    if q: products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    for param, field in [('category','category__slug'),('collection','collections__slug')]:
        if request.GET.get(param): products = products.filter(**{field:request.GET[param]})
    variants = Q()
    for param in ['size','color']:
        if request.GET.get(param): variants &= Q(**{f'variants__{param}': request.GET[param][:40]})
    if request.GET.get('available'): variants &= Q(variants__stock__gt=F('variants__reserved'))
    products = products.filter(variants)
    for param, field in [('min','price__gte'),('max','price__lte')]:
        try:
            if request.GET.get(param): products = products.filter(**{field:int(request.GET[param]) * 100})
        except ValueError: pass
    sort = request.GET.get('sort','new')
    products = products.distinct().order_by({'low':'price','high':'-price'}.get(sort,'-created'), 'pk')
    page = Paginator(products,12).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page',None)
    return render(request, 'catalog.html', {'page':page,'query':q, 'params':params.urlencode(), 'collections':Collection.objects.all()})

def product(request, slug):
    item = get_object_or_404(Product.objects.select_related('category').prefetch_related('photos','variants'), slug=slug, active=True)
    related = Product.objects.filter(active=True,category=item.category).exclude(pk=item.pk).prefetch_related('photos','variants')[:4]
    return render(request, 'product.html', {'product':item, 'related':related})

def collections(request): return render(request, 'collections.html', {'collections':Collection.objects.all()})

@require_POST
def cart_update(request):
    from .models import Variant
    try:
        variant = get_object_or_404(Variant, pk=int(request.POST.get('variant','0')))
        quantity = int(request.POST.get('quantity','1'))
        cart = request.session.get('cart',{}).copy()
        if request.POST.get('action') == 'add': quantity += cart.get(str(variant.pk),0)
        if quantity > 0 and not variant.product.active:
            raise CommerceError('Este produto está indisponível. Remova-o da seleção.')
        if quantity < 0 or quantity > 20 or quantity > variant.available:
            raise CommerceError('Quantidade indisponível. Confira o estoque da variante.')
        if quantity == 0: cart.pop(str(variant.pk),None)
        else: cart[str(variant.pk)] = quantity
        request.session['cart'] = cart
        request.session.pop('checkout_key',None)
        messages.success(request,'Sua seleção foi atualizada.')
    except (ValueError,CommerceError) as exc: messages.error(request,str(exc))
    return redirect('cart')

def cart(request):
    lines,total = cart_lines(request)
    return render(request,'cart.html',{'lines':lines,'subtotal':total})

def checkout(request):
    expire_demo_orders()
    owner_hash(request)
    lines,subtotal = cart_lines(request)
    if not lines: return redirect('cart')
    key = request.session.setdefault('checkout_key',str(uuid.uuid4()))
    from .models import Order
    pending = Order.objects.filter(checkout_key=key,owner_hash=owner_hash(request),status='pending').first()
    if pending: return redirect('order',pk=pending.pk)
    initial = {'checkout_key':key}
    if request.user.is_authenticated:
        initial.update(name=request.user.get_full_name(),email=request.user.email)
        address = Address.objects.filter(user=request.user).first()
        if address:
            initial.update({k:getattr(address,k) for k in ('postal_code','street','number','complement','city','state')})
    form = CheckoutForm(request.POST or None,initial=initial)
    from .models import ShippingMethod
    methods = ShippingMethod.objects.filter(active=True)
    if settings.PAYMENT_MODE != 'demo': methods = methods.filter(demo=False)
    form.fields['shipping_method'].choices = [(m.pk,f'{m.name} · R$ {m.price/100:.2f} · {m.days}') for m in methods]
    if request.method == 'POST' and form.is_valid():
        if str(form.cleaned_data['checkout_key']) != key: form.add_error(None,'Sessão de compra inválida. Recarregue a página.')
        else:
            try:
                order = create_order(request,form.cleaned_data,form.cleaned_data['checkout_key'])
                try: return redirect(start_payment(order))
                except CommerceError as exc:
                    messages.error(request,str(exc))
                    return redirect('order',pk=order.pk)
            except CommerceError as exc: form.add_error(None,str(exc))
    return render(request,'checkout.html',{'form':form,'lines':lines,'subtotal':subtotal,'methods':methods})

@require_POST
def quote(request):
    _,subtotal = cart_lines(request)
    try:
        methods = eligible_shipping(request.POST.get('state',''))
        selected = next((m for m in methods if str(m.pk) == request.POST.get('shipping_method')),None)
        if not selected: raise CommerceError('Escolha uma entrega disponível para o estado.')
        discount = coupon_discount(request.POST.get('coupon',''),subtotal)
        return JsonResponse({'subtotal':subtotal,'discount':discount,'shipping':selected.price,'total':subtotal-discount+selected.price})
    except CommerceError as exc: return JsonResponse({'error':str(exc)},status=400)

def order_detail(request, pk):
    expire_demo_orders()
    order = get_object_or_404(owned_orders(request).prefetch_related('items'),pk=pk)
    if order.status in ('paid','preparing','shipped','completed') and request.session.get('checkout_key') == str(order.checkout_key):
        cart = request.session.get('cart',{}).copy()
        for item in order.items.all():
            remaining = cart.get(str(item.variant_id),0) - item.quantity
            if remaining > 0: cart[str(item.variant_id)] = remaining
            else: cart.pop(str(item.variant_id),None)
        request.session['cart'] = cart
        request.session.pop('checkout_key',None)
    if order.status in ('failed','expired','canceled') and request.session.get('checkout_key') == str(order.checkout_key):
        request.session.pop('checkout_key',None)
    return render(request,'order.html',{'order':order})

@require_POST
def retry_payment(request,pk):
    order = get_object_or_404(owned_orders(request),pk=pk,status='pending')
    try: return redirect(start_payment(order))
    except CommerceError as exc:
        messages.error(request,str(exc))
        return redirect('order',pk=pk)

def demo_payment(request,pk):
    if not settings.DEBUG or settings.PAYMENT_MODE != 'demo': raise Http404
    expire_demo_orders()
    order = get_object_or_404(owned_orders(request),pk=pk,provider='demo')
    if request.method == 'POST':
        status = request.POST.get('status')
        if status not in ('paid','failed','expired','canceled'): return HttpResponse(status=400)
        settle(order.pk,status)
        return redirect('order',pk=pk)
    return render(request,'demo-payment.html',{'order':order})

@csrf_exempt
@require_POST
def webhook(request):
    if not settings.STRIPE_WEBHOOK_SECRET: return HttpResponse(status=503)
    try:
        event = stripe.Webhook.construct_event(request.body, request.headers.get('Stripe-Signature',''), settings.STRIPE_WEBHOOK_SECRET)
        handle_payment(event)
    except (ValueError,stripe.SignatureVerificationError,CommerceError): return HttpResponse(status=400)
    return HttpResponse(status=200)

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        uid,token = urlsafe_base64_encode(force_bytes(user.pk)),default_token_generator.make_token(user)
        url = settings.SITE_URL + reverse('verify',args=[uid,token])
        send_mail('Confirme seu e-mail — KYMA',f'Para ativar sua conta, abra: {url}',settings.DEFAULT_FROM_EMAIL,[user.email])
        return render(request,'message.html',{'title':'Confira seu e-mail','text':'Enviamos um link para ativar sua conta.'})
    return render(request,'form.html',{'title':'Entre no universo KYMA','form':form,'button':'Criar conta'})

def verify(request,uid,token):
    try: user = Customer.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
    except (ValueError,Customer.DoesNotExist,OverflowError): raise Http404
    if not default_token_generator.check_token(user,token):
        return render(request,'message.html',{'title':'Link inválido ou expirado','text':'Solicite um novo link de ativação.'},status=400)
    if request.method == 'POST':
        user.is_active,user.email_verified = True,True
        user.save(update_fields=['is_active','email_verified'])
        login(request,user)
        return redirect('account')
    return render(request,'form.html',{'title':'Confirmar seu e-mail','button':'Ativar conta'})

def resend_verification(request):
    from django import forms
    class EmailForm(forms.Form): email = forms.EmailField(label='E-mail')
    form = EmailForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = Customer.objects.filter(email=form.cleaned_data['email'].lower(),is_active=False,is_staff=False).first()
        if user:
            url = settings.SITE_URL + reverse('verify',args=[urlsafe_base64_encode(force_bytes(user.pk)), default_token_generator.make_token(user)])
            send_mail('Ative sua conta — KYMA',url,settings.DEFAULT_FROM_EMAIL,[user.email])
        return render(request,'message.html',{'title':'Confira seu e-mail','text':'Se houver uma conta aguardando ativação, enviaremos um novo link.'})
    return render(request,'form.html',{'title':'Reenviar ativação','form':form,'button':'Enviar link'})

def sign_in(request):
    form = EmailLoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request,form.get_user())
        return redirect('account')
    return render(request,'form.html',{'title':'Bem-vindo de volta','form':form,'button':'Entrar','login_form':True})

@require_POST
def sign_out(request):
    logout(request)
    return redirect('home')

@login_required
def account(request):
    form = ProfileForm(request.POST or None,instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Perfil atualizado.')
        return redirect('account')
    return render(request,'account.html',{'form':form,'orders':owned_orders(request).order_by('-created')[:50],
        'addresses':Address.objects.filter(user=request.user)})

@login_required
def address(request,pk=None):
    instance = get_object_or_404(Address,pk=pk,user=request.user) if pk else None
    form = AddressForm(request.POST or None,instance=instance)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect('account')
    return render(request,'form.html',{'title':'Seu endereço','form':form,'button':'Salvar endereço'})

@login_required
@require_POST
def remove_address(request,pk):
    get_object_or_404(Address,pk=pk,user=request.user).delete()
    return redirect('account')

@login_required
def password_change(request):
    form = PasswordChangeForm(request.user,request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request,user)
        messages.success(request,'Senha atualizada.')
        return redirect('account')
    return render(request,'form.html',{'title':'Alterar senha','form':form,'button':'Atualizar senha'})

def page(request,slug):
    store = StoreSettings.objects.filter(pk=1).first()
    options = {'sobre':('Universo KYMA',store.about if store else ''), 'entrega':('Entrega',store.shipping_policy if store else ''),
        'trocas':('Trocas e devoluções',store.returns_policy if store else ''),
        'privacidade':('Privacidade',store.privacy_policy if store else ''),
        'contato':('Fale com a KYMA',store.contact_email if store else '')}
    if slug not in options: raise Http404
    title,text = options[slug]
    return render(request,'message.html',{'title':title,'text':text or 'Informações comerciais ainda em preparação. Esta é uma loja demonstrativa.'})

@require_POST
def subscribe(request):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    email = request.POST.get('email','').lower().strip()
    try:
        validate_email(email)
        if request.POST.get('consent') != 'yes': raise ValidationError('Consentimento obrigatório.')
        sub,_ = Subscriber.objects.get_or_create(email=email)
        url = settings.SITE_URL + reverse('subscription',args=[sub.token])
        send_mail('Confirme novidades da KYMA',f'Confirme sua inscrição ou cancele por este link: {url}',settings.DEFAULT_FROM_EMAIL,[email])
        messages.success(request,'Confira seu e-mail para confirmar a inscrição.')
    except ValidationError: messages.error(request,'Informe um e-mail válido e aceite receber novidades.')
    return redirect('home')

def subscription(request,token):
    sub = get_object_or_404(Subscriber,token=token)
    if request.method == 'POST':
        sub.active = request.POST.get('action') == 'confirm'
        sub.save(update_fields=['active'])
        return render(request,'message.html',{'title':'Preferência atualizada','text':'Inscrição confirmada.' if sub.active else 'Você não receberá novidades.'})
    return render(request,'subscription.html')

def guest_tracking(request,token):
    from django.core import signing
    from .models import Order
    try:
        payload=signing.loads(token,salt='guest-tracking',max_age=30*24*3600)
        order=get_object_or_404(Order,pk=payload['order'],owner_hash=payload['owner'],user__isnull=True)
    except (signing.BadSignature,ValueError,KeyError): raise Http404
    if request.method=='POST':
        grants=request.session.get('guest_orders',[])
        if str(order.pk) not in grants: grants.append(str(order.pk))
        request.session['guest_orders']=grants[-30:]
        return redirect('order',pk=order.pk)
    return render(request,'form.html',{'title':'Acompanhar seu pedido','button':'Abrir acompanhamento'})

@require_POST
def metric(request):
    if settings.ANALYTICS_ENABLED and request.COOKIES.get('analytics_consent') == 'yes':
        allowed = {'hero_click','product_view','variant_selection','add_to_cart','checkout_start'}
        name = request.POST.get('event')
        if name in allowed:
            Metric.objects.create(event=name)
    return HttpResponse(status=204)
