import hashlib
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from .models import RateBucket

class SecurityMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith(('/conta/', '/gestao/', '/novidades/', '/checkout/', '/eventos/')):
            # REMOTE_ADDR is deliberately not replaced by user-controlled proxy headers.
            key = hashlib.sha256(f"{request.META.get('REMOTE_ADDR')}:{request.path}".encode()).hexdigest()
            with transaction.atomic():
                bucket, _ = RateBucket.objects.get_or_create(key=key, defaults={'started': timezone.now()})
                bucket = RateBucket.objects.select_for_update().get(pk=bucket.pk)
                if (timezone.now() - bucket.started).total_seconds() > 900:
                    bucket.started, bucket.count = timezone.now(), 0
                bucket.count += 1
                bucket.save()
                if bucket.count > 25:
                    return HttpResponse('Muitas tentativas. Aguarde 15 minutos.', status=429)
        response = self.get_response(request)
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        if not request.path.startswith('/gestao/'):
            response['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
        else:
            response['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
        if request.path.startswith(('/conta/', '/pedido/', '/checkout/', '/carrinho/', '/gestao/', '/pagamento/','/acompanhar/','/novidades/')):
            response['Cache-Control'] = 'private, no-store'
            # Preserve same-origin form checks; never send private URLs to other origins.
            response['Referrer-Policy'] = 'same-origin'
        return response
