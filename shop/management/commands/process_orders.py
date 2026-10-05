import stripe
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.core import signing
from django.urls import reverse
from django.db import transaction
from shop.models import Order,OrderNotice
from shop.services import expire_demo_orders,settle,CommerceError

class Command(BaseCommand):
    help='Reconcilia reservas Stripe e entrega avisos transacionais. Agendar a cada minuto em produção.'
    def handle(self,*args,**kwargs):
        expire_demo_orders()
        if settings.PAYMENT_MODE=='stripe' and settings.STRIPE_SECRET_KEY:
            for order in Order.objects.filter(provider='stripe',status='pending'):
                try:
                    if not order.provider_session:
                        # Lost responses are recovered with the original idempotency key.
                        from shop.services import start_payment
                        start_payment(order)
                        order.refresh_from_db()
                    session=stripe.checkout.Session.retrieve(order.provider_session,api_key=settings.STRIPE_SECRET_KEY)
                    if session.amount_total != order.total or session.currency != order.currency:
                        self.stderr.write('Reconciliação bloqueada: valores divergentes.'); continue
                    if session.payment_status=='paid':
                        Order.objects.filter(pk=order.pk).update(payment_intent=session.payment_intent or '')
                        settle(order.pk,'paid')
                    elif session.status=='expired': settle(order.pk,'expired')
                    # Completed asynchronous payments remain reserved until payment resolves.
                except (stripe.StripeError,CommerceError): self.stderr.write('Pedido pendente de reconciliação; verificar o provedor.')
        for pk in OrderNotice.objects.filter(sent=False).values_list('pk',flat=True):
            try:
                with transaction.atomic():
                    notice=OrderNotice.objects.select_for_update().select_related('order').get(pk=pk)
                    if notice.sent: continue
                    order=notice.order
                    demo='DEMONSTRAÇÃO, sem cobrança.\n' if order.provider=='demo' else ''
                    if order.user_id:
                        url=settings.SITE_URL+'/conta/'
                    else:
                        token=signing.dumps({'order':str(order.pk),'owner':order.owner_hash},salt='guest-tracking')
                        url=settings.SITE_URL+reverse('guest_tracking',args=[token])
                    send_mail('Seu pedido KYMA',f'{demo}Pedido {str(order.pk)[:8]}: {order.get_status_display()}.\nAcompanhe: {url}',
                        settings.DEFAULT_FROM_EMAIL,[order.email])
                    notice.sent=True;notice.save(update_fields=['sent'])
            except Exception: self.stderr.write('Aviso de pedido não entregue; será tentado novamente.')
