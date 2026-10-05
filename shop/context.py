from django.conf import settings
from .models import StoreSettings, Category, Collection

def store(request):
    return {'store': StoreSettings.objects.filter(pk=1).first(), 'categories': Category.objects.all(),
        'nav_collections': Collection.objects.all().order_by('pk'),
        'cart_count': sum(request.session.get('cart', {}).values()), 'demo_mode': settings.PAYMENT_MODE == 'demo',
        'analytics_enabled': settings.ANALYTICS_ENABLED}
