import hashlib
import secrets
import uuid
from datetime import timedelta
import stripe
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import F
from django.utils import timezone
from .models import Variant, Coupon, Order, OrderItem, ShippingMethod, PaymentEvent, OrderNotice, Metric

class CommerceError(Exception): pass

def owner_hash(request):
    token = request.session.get('order_owner')
    if not token:
        token = secrets.token_urlsafe(32)
        request.session['order_owner'] = token
    return hashlib.sha256(token.encode()).hexdigest()

def owned_orders(request):
    if request.user.is_authenticated:
        return Order.objects.filter(user=request.user)
    from django.db.models import Q
    return Order.objects.filter(user__isnull=True).filter(Q(owner_hash=owner_hash(request)) | Q(pk__in=request.session.get('guest_orders',[])))

def cart_lines(request):
    cart = request.session.get('cart', {})
    variants = list(Variant.objects.filter(pk__in=cart.keys()).select_related('product').prefetch_related('product__photos'))
    existing = {str(v.pk) for v in variants}
    if set(cart) != existing:
        cart = {key:quantity for key,quantity in cart.items() if key in existing}
        request.session['cart'] = cart
        request.session.pop('checkout_key',None)
    lines = [{'variant': v, 'quantity': cart[str(v.pk)], 'total': v.product.price * cart[str(v.pk)]} for v in variants]
    return lines, sum(line['total'] for line in lines)

def coupon_discount(code, subtotal):
    if not code: return 0
    c = Coupon.objects.filter(code=code.upper().strip(), active=True).first()
    if not c or (c.expires and c.expires <= timezone.now()):
        raise CommerceError('Cupom inválido ou expirado.')
    return subtotal * c.percent // 100

def eligible_shipping(state):
    methods = ShippingMethod.objects.filter(active=True)
    if settings.PAYMENT_MODE != 'demo': methods = methods.filter(demo=False)
    return [m for m in methods if not m.states or state.upper() in [x.strip().upper() for x in m.states.split(',')]]

@transaction.atomic
def settle(order_id, status):
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status != 'pending': return order
    if status not in ('paid', 'failed', 'expired', 'canceled'):
        raise CommerceError('Transição de pagamento inválida.')
    for item in order.items.select_related('variant').order_by('variant_id'):
        updates = {'reserved': F('reserved') - item.quantity}
        if status == 'paid': updates['stock'] = F('stock') - item.quantity
        changed = Variant.objects.filter(pk=item.variant_id, reserved__gte=item.quantity).update(**updates)
        if not changed: raise CommerceError('Reserva de estoque inconsistente.')
    order.status = status
    order.save(update_fields=['status'])
    OrderNotice.objects.get_or_create(order=order, status=status)
    if status == 'paid' and settings.ANALYTICS_ENABLED:
        Metric.objects.get_or_create(order=order, defaults={'event': 'purchase'})
    return order

def expire_demo_orders():
    for pk in Order.objects.filter(provider='demo', status='pending', expires__lte=timezone.now()).values_list('pk', flat=True):
        settle(pk, 'expired')

@transaction.atomic
def _create_order(request, data, checkout_key):
    owner = owner_hash(request)
    previous = Order.objects.filter(checkout_key=checkout_key).first()
    if previous:
        if previous.owner_hash != owner: raise CommerceError('Pedido inválido.')
        return previous
    lines, subtotal = cart_lines(request)
    if not lines or len(lines) != len(request.session.get('cart', {})):
        raise CommerceError('Revise o carrinho: algum produto não está disponível.')
    if any(not line['variant'].product.active for line in lines):
        raise CommerceError('Remova os produtos indisponíveis antes de continuar.')
    if settings.PAYMENT_MODE != 'demo':
        from .models import StoreSettings
        store = StoreSettings.objects.filter(pk=1,demo=False).first()
        if not store or not all([store.company_details,store.contact_email,store.shipping_policy,store.returns_policy,store.privacy_policy]):
            raise CommerceError('A loja ainda precisa concluir suas informações comerciais.')
        if any(line['variant'].product.demo or not line['variant'].product.photos.exists() for line in lines):
            raise CommerceError('Produtos demonstrativos não podem ser pagos no provedor.')
    method = next((m for m in eligible_shipping(data['state']) if m.pk == int(data['shipping_method'])), None)
    if not method: raise CommerceError('Entrega indisponível para este endereço.')
    discount = coupon_discount(data.get('coupon', ''), subtotal)
    for line in sorted(lines, key=lambda x: x['variant'].pk):
        v, qty = line['variant'], line['quantity']
        if qty < 1 or qty > 20: raise CommerceError('Quantidade inválida.')
        updated = Variant.objects.filter(pk=v.pk, stock__gte=F('reserved') + qty, product__active=True).update(reserved=F('reserved') + qty)
        if not updated: raise CommerceError(f'{v.product.name}: estoque insuficiente. Revise o carrinho.')
    order = Order.objects.create(checkout_key=checkout_key, owner_hash=owner,
        user=request.user if request.user.is_authenticated else None, email=data['email'], name=data['name'],
        address={k: data[k] for k in ('postal_code','street','number','complement','city','state')},
        shipping_name=method.name, shipping_days=method.days, subtotal=subtotal, discount=discount,
        shipping=method.price, total=subtotal - discount + method.price, coupon_code=data.get('coupon','').upper(),
        provider=settings.PAYMENT_MODE, expires=timezone.now() + timedelta(minutes=35))
    for line in lines:
        v = line['variant']
        OrderItem.objects.create(order=order, variant=v, name=f'{v.product.name} · {v.size} · {v.color}', quantity=line['quantity'], price=v.product.price)
    OrderNotice.objects.get_or_create(order=order, status='pending')
    return order

def create_order(request, data, checkout_key):
    try:
        return _create_order(request,data,checkout_key)
    except (CommerceError,IntegrityError):
        # A concurrent repeated submission may finish while this transaction waits.
        previous = Order.objects.filter(checkout_key=checkout_key,owner_hash=owner_hash(request)).first()
        if previous: return previous
        raise

def start_payment(order):
    if order.provider == 'demo': return f'/pagamento/demo/{order.pk}/'
    if order.status != 'pending': return f'/pedido/{order.pk}/'
    if order.payment_url: return order.payment_url
    if not settings.STRIPE_SECRET_KEY:
        raise CommerceError('Pagamento não configurado. Entre em contato com a loja.')
    # One aggregated server-calculated total avoids rounding ambiguity with coupons.
    try:
        session = stripe.checkout.Session.create(api_key=settings.STRIPE_SECRET_KEY, mode='payment',
            client_reference_id=str(order.pk), customer_email=order.email, metadata={'order_id': str(order.pk)},
            payment_intent_data={'metadata': {'order_id': str(order.pk)}},
            line_items=[{'price_data': {'currency': order.currency, 'unit_amount': order.total,
                'product_data': {'name': f'Pedido KYMA {str(order.pk)[:8]}'}}, 'quantity': 1}],
            success_url=f'{settings.SITE_URL}/pedido/{order.pk}/', cancel_url=f'{settings.SITE_URL}/pedido/{order.pk}/',
            expires_at=int((order.created + timedelta(minutes=30)).timestamp()),
            idempotency_key=f'kyma-checkout-{order.pk}')
    except stripe.StripeError as exc:
        raise CommerceError('Não foi possível abrir o pagamento. Tente novamente no pedido.') from exc
    Order.objects.filter(pk=order.pk).update(provider_session=session.id, payment_url=session.url)
    return session.url

@transaction.atomic
def handle_payment(event):
    obj = event['data']['object']
    kind = event['type']
    if kind == 'charge.refunded':
        order = Order.objects.select_for_update().filter(provider='stripe',payment_intent=obj.get('payment_intent')).first()
        if not order: raise CommerceError('Reembolso desconhecido.')
        if obj.get('currency') != order.currency or obj.get('amount') != order.total or obj.get('amount_refunded') != order.total or not obj.get('refunded'):
            raise CommerceError('Reembolso parcial ou divergente exige análise manual.')
        if bool(obj.get('livemode')) != settings.STRIPE_SECRET_KEY.startswith('sk_live_'):
            raise CommerceError('Ambiente de reembolso incorreto.')
        if PaymentEvent.objects.filter(event_id=event['id']).exists(): return
        if order.status in ('paid','preparing','shipped','completed','refund_pending','refunded'):
            order.status='refunded';order.save(update_fields=['status'])
            OrderNotice.objects.get_or_create(order=order,status='refunded')
            PaymentEvent.objects.create(event_id=event['id'],order=order)
        else: raise CommerceError('Pedido não elegível para reembolso.')
        return
    allowed = {'checkout.session.completed': 'paid', 'checkout.session.async_payment_succeeded': 'paid',
        'checkout.session.async_payment_failed': 'failed', 'checkout.session.expired': 'expired'}
    if kind not in allowed: return
    order = Order.objects.select_for_update().filter(provider_session=obj.get('id'), provider='stripe').first()
    if not order: raise CommerceError('Sessão de pagamento desconhecida.')
    if (obj.get('client_reference_id') != str(order.pk) or obj.get('metadata', {}).get('order_id') != str(order.pk)
        or obj.get('amount_total') != order.total or obj.get('currency') != order.currency):
        raise CommerceError('Pagamento não corresponde ao pedido.')
    if bool(obj.get('livemode')) != settings.STRIPE_SECRET_KEY.startswith('sk_live_'):
        raise CommerceError('Ambiente de pagamento incorreto.')
    if PaymentEvent.objects.filter(event_id=event['id']).exists(): return
    status = allowed[kind]
    if status == 'paid' and obj.get('payment_status') != 'paid':
        PaymentEvent.objects.create(event_id=event['id'], order=order)
        return
    if status == 'paid' and order.status in ('expired','canceled','failed'):
        raise CommerceError('Pagamento tardio exige reconciliação; reserva já liberada.')
    settle(order.pk, status)
    if obj.get('payment_intent'):
        Order.objects.filter(pk=order.pk).update(payment_intent=obj['payment_intent'])
    PaymentEvent.objects.create(event_id=event['id'], order=order)

@transaction.atomic
def fulfillment(order_id, status, actor):
    from .models import Audit
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status == 'pending' and status == 'canceled':
        if order.provider == 'stripe':
            if not order.provider_session: raise CommerceError('Reconcilie a sessão antes de cancelar.')
            try:
                stripe.checkout.Session.expire(order.provider_session,api_key=settings.STRIPE_SECRET_KEY)
            except stripe.StripeError as exc: raise CommerceError('Sessão não cancelada; confira a situação no provedor.') from exc
        order=settle(order.pk,'canceled')
        Audit.objects.create(actor=actor,action='order:canceled',object_id=str(order.pk))
        return order
    transitions = {'paid': {'preparing','refund_pending'}, 'preparing': {'shipped','refund_pending'},
        'shipped': {'completed','refund_pending'}, 'completed': {'refund_pending'}, 'refund_pending': {'refunded'}}
    if status not in transitions.get(order.status, set()): raise CommerceError('Etapa de pedido inválida.')
    if status == 'shipped' and not order.tracking: raise CommerceError('Informe o rastreamento antes de enviar.')
    if status == 'refunded' and order.provider == 'stripe':
        if not order.payment_intent: raise CommerceError('Pagamento não conciliado.')
        try:
            result = stripe.Refund.create(payment_intent=order.payment_intent, api_key=settings.STRIPE_SECRET_KEY,
                idempotency_key=f'kyma-refund-{order.pk}')
        except stripe.StripeError as exc: raise CommerceError('O provedor não confirmou o reembolso.') from exc
        if result.status != 'succeeded': raise CommerceError('Reembolso ainda pendente no provedor. Tente reconciliar depois.')
    # Returned merchandise is inspected before stock is manually replenished.
    order.status = status
    order.save(update_fields=['status'])
    Audit.objects.create(actor=actor, action=f'order:{status}', object_id=str(order.pk))
    OrderNotice.objects.get_or_create(order=order, status=status)
    return order
