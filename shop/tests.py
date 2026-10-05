import io
import json
import uuid
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from PIL import Image
from django.test import TestCase, TransactionTestCase, Client, override_settings, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.tokens import default_token_generator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import close_old_connections, connections
from django.core.management import call_command, CommandError
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import totp
from .models import (Customer,Category,Collection,StoreSettings,Product,Variant,ShippingMethod,Order,PaymentEvent,Coupon,Subscriber,Audit)
from .services import create_order,settle,handle_payment,CommerceError,expire_demo_orders,fulfillment,start_payment
from .forms import SafeImageForm

FAST = ['django.contrib.auth.hashers.PBKDF2PasswordHasher']
def fixture():
    category=Category.objects.create(name='Camisetas',slug='camisetas')
    product=Product.objects.create(name='Sample',slug='sample',category=category,price=10000,description='Demo',composition='Demo',care='Demo')
    variant=Variant.objects.create(product=product,size='M',color='Preto',stock=1)
    shipping=ShippingMethod.objects.create(name='Local',price=1900,days='Simulado',active=True,demo=True)
    return product,variant,shipping

def data(shipping):
    return {'name':'Teste Local','email':'test@example.test','postal_code':'90000-000','street':'Rua Exemplo',
        'number':'10','complement':'','city':'Cidade','state':'RS','shipping_method':str(shipping.pk),'coupon':''}

def request(variant):
    r=RequestFactory().get('/')
    r.user=AnonymousUser()
    r.session={'cart':{str(variant.pk):1}}
    return r

class StorefrontIntegrationTests(TestCase):
    def setUp(self):
        self.product, self.variant, self.shipping = fixture()
        self.product.featured = True
        self.product.save(update_fields=['featured'])

    def test_photographic_editorial_has_local_purchase_routes(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="hero-photo"')
        self.assertNotContains(response, '<video ')
        self.assertContains(response, 'href="/loja/"')
        self.assertContains(response, 'action="/carrinho/atualizar/"')
        self.assertNotContains(response, 'https://app.ltx.io/')
        policy = response['Content-Security-Policy']
        self.assertIn('media-src', policy)
        self.assertNotIn('https://pub-86dc5b5484314368ac5436a674b0d919.r2.dev', policy)
        self.assertIn("script-src 'self'", policy)
        self.assertNotIn('unsafe-inline', policy)

    def test_quick_add_uses_server_price_and_checkout(self):
        response = self.client.post('/carrinho/atualizar/', {
            'variant': self.variant.pk, 'action': 'add', 'quantity': 1, 'price': 1,
        })
        self.assertRedirects(response, '/carrinho/')
        self.assertEqual(self.client.session['cart'][str(self.variant.pk)], 1)
        self.assertContains(self.client.get('/carrinho/'), 'R$ 100,00')
        self.assertEqual(self.client.get('/checkout/').status_code, 200)

    def test_reserved_last_unit_is_not_offered_in_quick_add(self):
        self.variant.reserved = self.variant.stock
        self.variant.save(update_fields=['reserved'])
        response = self.client.get('/loja/')
        self.assertContains(response, 'Esgotado no momento')
        self.assertNotContains(response, 'class="quick-add"')

@override_settings(DEBUG=True)
class ReferenceAssortmentTests(TestCase):
    def test_expansion_is_idempotent_and_preserves_stock(self):
        StoreSettings.objects.create(demo=True)
        product, variant, shipping = fixture()
        variant.stock, variant.reserved = 2, 1
        variant.save()
        output = io.StringIO()
        call_command('expand_catalog', stdout=output)
        added = Product.objects.get(slug='moletom-atlantico')
        added_variant = added.variants.get(size='M')
        added_variant.stock = 3
        added_variant.save(update_fields=['stock'])
        call_command('expand_catalog', stdout=output)
        self.assertEqual(Product.objects.count(),17)
        self.assertEqual(Collection.objects.count(),8)
        self.assertEqual(added.variants.count(),5)
        variant.refresh_from_db(); added_variant.refresh_from_db(); product.refresh_from_db()
        self.assertEqual((variant.stock,variant.reserved),(2,1))
        self.assertEqual(added_variant.stock,3)
        self.assertEqual(product.name,'Sample')
        self.assertContains(self.client.get('/loja/?collection=alfaiataria-livre'),'Blazer Arquitetura')

    def test_expansion_refuses_real_store_and_production(self):
        store = StoreSettings.objects.create(demo=False)
        with self.assertRaises(CommandError): call_command('expand_catalog', stdout=io.StringIO())
        store.demo=True; store.save()
        with override_settings(DEBUG=False):
            with self.assertRaises(CommandError): call_command('expand_catalog', stdout=io.StringIO())
        self.assertEqual(Product.objects.count(),0)

@override_settings(PASSWORD_HASHERS=FAST,EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class StoreTests(TestCase):
    def setUp(self):
        self.product,self.variant,self.shipping=fixture()
        self.customer=Customer.objects.create_user(username='one',email='one@example.test',password='A-long-test-password',email_verified=True)
    def new_order(self):
        r=request(self.variant)
        return r,create_order(r,data(self.shipping),uuid.uuid4())
    def test_render_pages_and_escape(self):
        self.product.name='<script>alert(1)</script>';self.product.save()
        for url in ['/','/loja/','/produto/sample/','/colecoes/','/carrinho/','/conta/entrar/','/conta/criar/','/gestao/login/','/info/privacidade/']:
            response=self.client.get(url)
            self.assertEqual(response.status_code,200,url)
            self.assertNotContains(response,'<script>alert(1)</script>')
    def test_registration_cannot_escalate_and_verification_single_use(self):
        response=self.client.post('/conta/criar/',{'first_name':'Tester','email':'new@example.test','password1':'Unique-long-password!234','password2':'Unique-long-password!234','is_staff':'true','is_superuser':'true'})
        self.assertEqual(response.status_code,200)
        user=Customer.objects.get(email='new@example.test')
        self.assertFalse(user.is_staff);self.assertFalse(user.is_active)
        token=default_token_generator.make_token(user)
        url=f'/conta/ativar/{urlsafe_base64_encode(force_bytes(user.pk))}/{token}/'
        self.assertEqual(self.client.get(url).status_code,200)
        user.refresh_from_db();self.assertFalse(user.is_active)
        self.assertEqual(self.client.post(url).status_code,302)
        user.refresh_from_db();self.assertTrue(user.email_verified)
        self.assertEqual(self.client.post(url).status_code,400)
    def test_login_logout(self):
        self.assertEqual(self.client.post('/conta/entrar/',{'username':self.customer.email,'password':'A-long-test-password'}).status_code,302)
        self.assertEqual(self.client.get('/conta/').status_code,200)
        self.client.post('/conta/sair/')
        self.assertEqual(self.client.get('/conta/').status_code,302)
    def test_password_reset_invalid_and_single_use(self):
        token=default_token_generator.make_token(self.customer)
        url=f'/conta/nova-senha/{urlsafe_base64_encode(force_bytes(self.customer.pk))}/{token}/'
        response=self.client.get(url)
        self.assertEqual(response.status_code,302)
        response=self.client.post(response.url,{'new_password1':'New-unique-password!12','new_password2':'New-unique-password!12'})
        self.assertEqual(response.status_code,302)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.check_password('New-unique-password!12'))
        self.assertFalse(default_token_generator.check_token(self.customer,token))
    def test_order_ownership(self):
        _,order=self.new_order();order.user=self.customer;order.save()
        other=Customer.objects.create_user(username='other',email='other@example.test',password='Other-long-password')
        self.client.force_login(other)
        self.assertEqual(self.client.get(f'/pedido/{order.pk}/').status_code,404)
        self.client.force_login(self.customer)
        response=self.client.get(f'/pedido/{order.pk}/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response['Cache-Control'],'private, no-store')
    def test_guest_order_not_public(self):
        _,order=self.new_order()
        self.assertEqual(self.client.get(f'/pedido/{order.pk}/').status_code,404)
    def test_guest_tracking_signed_and_tamper_protected(self):
        from django.core import signing
        _,order=self.new_order()
        token=signing.dumps({'order':str(order.pk),'owner':order.owner_hash},salt='guest-tracking')
        self.assertEqual(self.client.post('/acompanhar/'+token+'/').status_code,302)
        self.assertEqual(self.client.get(f'/pedido/{order.pk}/').status_code,200)
        self.assertEqual(self.client.post('/acompanhar/'+token+'x/').status_code,404)
    def test_guest_cart_clears_only_after_verified_payment(self):
        self.client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':1})
        self.client.get('/checkout/')
        key=self.client.session['checkout_key']
        from .services import owner_hash
        r=request(self.variant)
        r.session=dict(self.client.session)
        order=create_order(r,data(self.shipping),uuid.UUID(key))
        session=self.client.session;session['order_owner']=r.session['order_owner'];session.save()
        self.client.get(f'/pedido/{order.pk}/')
        self.assertTrue(self.client.session['cart'])
        settle(order.pk,'paid')
        self.client.get(f'/pedido/{order.pk}/')
        self.assertEqual(self.client.session['cart'],{})
    def test_address_ownership(self):
        from .models import Address
        address=Address.objects.create(user=self.customer,name='Home',postal_code='90000-000',street='Sample',number='1',city='Test',state='RS')
        other=Customer.objects.create_user(username='other',email='other@example.test')
        self.client.force_login(other)
        self.assertEqual(self.client.get(f'/conta/endereco/{address.pk}/').status_code,404)
        self.assertEqual(self.client.post(f'/conta/endereco/{address.pk}/remover/').status_code,404)
    def test_admin_requires_otp_even_for_owner(self):
        self.customer.is_staff=True;self.customer.is_superuser=True;self.customer.save()
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get('/gestao/').status_code,302)
        device=TOTPDevice.objects.create(user=self.customer,name='Test',confirmed=True)
        session=self.client.session;session['otp_device_id']=device.persistent_id;session.save()
        self.assertEqual(self.client.get('/gestao/').status_code,200)
    def test_admin_totp_login(self):
        self.customer.is_staff=True;self.customer.is_superuser=True;self.customer.save()
        device=TOTPDevice.objects.create(user=self.customer,name='Test',confirmed=True)
        code=totp(device.bin_key,step=device.step,t0=device.t0,digits=device.digits,drift=device.drift)
        response=self.client.post('/gestao/login/',{'username':'one','password':'A-long-test-password','otp_device':device.persistent_id,'otp_token':str(code).zfill(device.digits),'next':'/gestao/'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.client.get('/gestao/').status_code,200)
    def test_customer_cannot_access_admin(self):
        self.client.force_login(self.customer)
        self.assertEqual(self.client.get('/gestao/shop/product/').status_code,302)
    def test_catalog_staff_cannot_change_permissions(self):
        from django.contrib.auth.models import Permission
        self.customer.is_staff=True;self.customer.save()
        self.customer.user_permissions.add(Permission.objects.get(codename='view_product',content_type__app_label='shop'))
        device=TOTPDevice.objects.create(user=self.customer,name='Test',confirmed=True)
        self.client.force_login(self.customer)
        session=self.client.session;session['otp_device_id']=device.persistent_id;session.save()
        self.assertEqual(self.client.get('/gestao/shop/product/').status_code,200)
        self.assertEqual(self.client.get('/gestao/shop/customer/').status_code,403)
        self.assertEqual(self.client.get('/gestao/auth/group/').status_code,403)
    def test_profile_cannot_escalate_role(self):
        self.client.force_login(self.customer)
        self.client.post('/conta/',{'first_name':'Updated','last_name':'Name','is_staff':'true','is_superuser':'true'})
        self.customer.refresh_from_db();self.assertFalse(self.customer.is_staff);self.assertFalse(self.customer.is_superuser)
    def test_csrf_and_private_files(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':1}).status_code,403)
        for path in ['/.env','/.git/config','/db.sqlite3','/private-mail/test.log','/media/../.env','/static/.env']:
            self.assertEqual(self.client.get(path).status_code,404,path)
    def test_cart_persistence_and_limits(self):
        self.client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':1,'action':'add'})
        self.assertEqual(self.client.session['cart'],{str(self.variant.pk):1})
        self.assertContains(self.client.get('/carrinho/'),'Sample')
        self.client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':2})
        self.assertEqual(self.client.session['cart'][str(self.variant.pk)],1)
    def test_inactive_item_can_be_removed_and_cannot_be_purchased(self):
        self.client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':1})
        self.product.active=False;self.product.save()
        self.assertContains(self.client.get('/carrinho/'),'Sample')
        with self.assertRaises(CommerceError):create_order(request(self.variant),data(self.shipping),uuid.uuid4())
        self.client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':0})
        self.assertEqual(self.client.session['cart'],{})
    def test_server_totals_and_idempotency(self):
        r=request(self.variant);key=uuid.uuid4();values=data(self.shipping);values['total']=1
        order=create_order(r,values,key)
        self.assertEqual(order.total,11900)
        self.assertEqual(create_order(r,values,key).pk,order.pk)
        self.variant.refresh_from_db();self.assertEqual(self.variant.reserved,1)
    @override_settings(DEBUG=True)
    def test_checkout_form_full_flow(self):
        self.client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':1,'action':'add'})
        self.assertEqual(self.client.get('/checkout/').status_code,200)
        key=self.client.session['checkout_key']
        values=data(self.shipping);values.update(checkout_key=key,accept=True)
        response=self.client.post('/checkout/',values)
        self.assertEqual(response.status_code,302)
        self.assertIn('/pagamento/demo/',response.url)
        response=self.client.post(response.url,{'status':'paid'})
        self.assertEqual(response.status_code,302)
        self.assertContains(self.client.get(response.url),'Pagamento aprovado')
    def test_quote_and_coupon(self):
        Coupon.objects.create(code='TEST',percent=10,active=True)
        session=self.client.session;session['cart']={str(self.variant.pk):1};session.save()
        response=self.client.post('/checkout/total/',{'state':'RS','shipping_method':self.shipping.pk,'coupon':'TEST'})
        self.assertEqual(response.json()['total'],10900)
        self.assertEqual(self.client.post('/checkout/total/',{'state':'RS','shipping_method':self.shipping.pk,'coupon':'INVALID'}).status_code,400)
    def test_shipping_region_server_validation(self):
        self.shipping.states='SP';self.shipping.save()
        with self.assertRaises(CommerceError): create_order(request(self.variant),data(self.shipping),uuid.uuid4())
        self.variant.refresh_from_db();self.assertEqual(self.variant.reserved,0)
    def test_payment_duplicate_deducts_once(self):
        _,order=self.new_order()
        settle(order.pk,'paid');settle(order.pk,'paid')
        self.variant.refresh_from_db()
        self.assertEqual((self.variant.stock,self.variant.reserved),(0,0))
    def test_fail_expire_cancel_release(self):
        for status in ['failed','expired','canceled']:
            _,order=self.new_order();settle(order.pk,status)
            self.variant.refresh_from_db();self.assertEqual((self.variant.stock,self.variant.reserved),(1,0))
    def test_automatic_demo_expiration(self):
        _,order=self.new_order();order.expires=timezone.now()-timedelta(seconds=1);order.save()
        expire_demo_orders();order.refresh_from_db();self.assertEqual(order.status,'expired')
    def event(self,order,**overrides):
        obj={'id':'cs_test_123','amount_total':order.total,'currency':'brl','payment_status':'paid','client_reference_id':str(order.pk),
            'metadata':{'order_id':str(order.pk)},'payment_intent':'pi_test','livemode':False}
        obj.update(overrides)
        return {'id':'evt_test','type':'checkout.session.completed','data':{'object':obj}}
    def stripe_order(self):
        _,order=self.new_order();order.provider='stripe';order.provider_session='cs_test_123';order.save();return order
    @override_settings(STRIPE_SECRET_KEY='sk_test_not_a_real_key')
    def test_webhook_reconciles_and_deduplicates(self):
        order=self.stripe_order();event=self.event(order)
        handle_payment(event);handle_payment(event)
        self.assertEqual(PaymentEvent.objects.count(),1)
        order.refresh_from_db();self.assertEqual(order.status,'paid')
        self.variant.refresh_from_db();self.assertEqual(self.variant.stock,0)
    def test_mismatched_payment_does_not_settle(self):
        order=self.stripe_order()
        for changes in [{'amount_total':1},{'currency':'usd'},{'client_reference_id':'wrong'},{'metadata':{}}]:
            with self.assertRaises(CommerceError): handle_payment(self.event(order,**changes))
        order.refresh_from_db();self.assertEqual(order.status,'pending')
    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_test_placeholder')
    def test_invalid_webhook_signature(self):
        response=self.client.post('/webhooks/stripe/',json.dumps({'type':'checkout.session.completed'}),content_type='application/json',HTTP_STRIPE_SIGNATURE='invalid')
        self.assertEqual(response.status_code,400)
    def test_async_unpaid_stays_reserved(self):
        order=self.stripe_order();handle_payment(self.event(order,payment_status='unpaid'))
        order.refresh_from_db();self.assertEqual(order.status,'pending')
        self.variant.refresh_from_db();self.assertEqual(self.variant.reserved,1)
    def test_fulfillment_states_and_audit(self):
        _,order=self.new_order();settle(order.pk,'paid')
        fulfillment(order.pk,'preparing',self.customer)
        with self.assertRaises(CommerceError): fulfillment(order.pk,'shipped',self.customer)
        Order.objects.filter(pk=order.pk).update(tracking='TEST123')
        fulfillment(order.pk,'shipped',self.customer);fulfillment(order.pk,'completed',self.customer)
        fulfillment(order.pk,'refund_pending',self.customer);fulfillment(order.pk,'refunded',self.customer)
        self.assertEqual(Audit.objects.count(),5)
        order.refresh_from_db();self.assertEqual(order.status,'refunded')
    def test_pending_cancel_audited(self):
        _,order=self.new_order();fulfillment(order.pk,'canceled',self.customer)
        order.refresh_from_db();self.assertEqual(order.status,'canceled')
        self.variant.refresh_from_db();self.assertEqual(self.variant.reserved,0)
    def test_refund_webhook_full_only(self):
        order=self.stripe_order();handle_payment(self.event(order))
        event={'id':'evt_refund','type':'charge.refunded','data':{'object':{'payment_intent':'pi_test','amount':order.total,
            'amount_refunded':1,'currency':'brl','refunded':False,'livemode':False}}}
        with self.assertRaises(CommerceError):handle_payment(event)
        event['data']['object'].update(amount_refunded=order.total,refunded=True)
        handle_payment(event);handle_payment(event)
        order.refresh_from_db();self.assertEqual(order.status,'refunded')
    def test_upload_rejects_non_image_and_reencodes(self):
        form=SafeImageForm(data={'product':self.product.pk,'alt':'Test'},files={'image':SimpleUploadedFile('evil.svg',b'<svg><script>alert(1)</script></svg>',content_type='image/svg+xml')})
        self.assertFalse(form.is_valid())
        out=io.BytesIO();Image.new('RGB',(10,10)).save(out,'PNG')
        form=SafeImageForm(data={'product':self.product.pk,'alt':'Test'},files={'image':SimpleUploadedFile('good.png',out.getvalue(),content_type='image/png')})
        self.assertTrue(form.is_valid(),form.errors)
        self.assertEqual(form.cleaned_data['image'].name,'product.webp')
    def test_newsletter_double_opt_in_and_unsubscribe(self):
        self.client.post('/novidades/',{'email':'news@example.test','consent':'yes'})
        sub=Subscriber.objects.get(email='news@example.test');self.assertFalse(sub.active)
        self.client.post(f'/novidades/{sub.token}/',{'action':'confirm'});sub.refresh_from_db();self.assertTrue(sub.active)
        self.client.post(f'/novidades/{sub.token}/',{'action':'cancel'});sub.refresh_from_db();self.assertFalse(sub.active)
    def test_rate_limit(self):
        for _ in range(25): self.client.post('/conta/entrar/',{'username':'wrong@example.test','password':'wrong'})
        self.assertEqual(self.client.post('/conta/entrar/',{}).status_code,429)
    def test_real_csrf_form_accepts_same_origin_only(self):
        client=Client(enforce_csrf_checks=True)
        response=client.get('/produto/sample/')
        token=client.cookies['csrftoken'].value
        response=client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':1,'csrfmiddlewaretoken':token},HTTP_ORIGIN='http://testserver')
        self.assertEqual(response.status_code,302)
        response=client.post('/carrinho/atualizar/',{'variant':self.variant.pk,'quantity':0,'csrfmiddlewaretoken':token},HTTP_ORIGIN='http://evil.example.test')
        self.assertEqual(response.status_code,403)
        self.assertEqual(client.get('/carrinho/')['Referrer-Policy'],'same-origin')
    @override_settings(DEBUG=False)
    def test_demo_disabled_without_debug(self):
        _,order=self.new_order()
        self.assertEqual(self.client.get(f'/pagamento/demo/{order.pk}/').status_code,404)
    @override_settings(PAYMENT_MODE='stripe')
    def test_real_payment_rejects_demo_catalog(self):
        with self.assertRaises(CommerceError): create_order(request(self.variant),data(self.shipping),uuid.uuid4())

@override_settings(PASSWORD_HASHERS=FAST)
class ConcurrentStockTests(TransactionTestCase):
    def test_two_checkouts_for_last_unit(self):
        _,variant,shipping=fixture()
        def buy():
            close_old_connections()
            try:
                create_order(request(variant),data(shipping),uuid.uuid4());return 'reserved'
            except CommerceError: return 'unavailable'
            finally: connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:buy(),range(2)))
        self.assertEqual(sorted(results),['reserved','unavailable'])
        variant.refresh_from_db();self.assertEqual(variant.reserved,1)
        self.assertEqual(Order.objects.count(),1)
