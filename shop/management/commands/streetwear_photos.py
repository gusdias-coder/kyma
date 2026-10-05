"""Install bundled real photography into the local reference catalog, preserving uploads."""
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from shop.models import Product, Category, Banner, StoreSettings

CATALOG = [
    ('camiseta-essencial', 'Camiseta Gráfica Noturna', 'graphic-back.webp'),
    ('blazer-linha-livre', 'Camiseta Gráfica Solar', 'graphic-red-product.webp'),
    ('calca-forma', 'Calça Cargo Urbana', 'cargo-street.webp'),
    ('moletom-horizonte', 'Moletom Horizonte', 'hoodie-black-product.webp'),
    ('camiseta-contorno', 'Camiseta Cartoon', 'graphic-cartoon.webp'),
    ('camisa-traco', 'Camiseta Gráfica Azul', 'graphic-blue.webp'),
    ('calca-horizonte', 'Camiseta Base', 'denim-street.webp'),
    ('jaqueta-intervalo', 'Jaqueta Denim', 'denim-jacket.webp'),
]

class Command(BaseCommand):
    help = 'Aplica fotos reais de referência somente ao catálogo demonstrativo local.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError('Fotografias de referência são instaladas apenas no ambiente local.')
        source = Path(settings.BASE_DIR) / 'static/images'
        store = StoreSettings.objects.filter(pk=1, demo=True).first()
        if not store:
            self.stdout.write('Loja real preservada; nenhuma referência aplicada.')
            return

        def install(instance, field_name, filename, folder, label):
            field = getattr(instance, field_name)
            if field and not Path(field.name).name.startswith('kyma-reference-'):
                return  # A photo uploaded by the owner always wins.
            target_name = f'{folder}/kyma-reference-{label}.webp'
            destination = Path(settings.MEDIA_ROOT) / target_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((source / filename).read_bytes())
            setattr(instance, field_name, target_name)
            instance.save(update_fields=[field_name])

        install(store, 'hero_image', 'hero.webp', 'editorials', 'hero-hoodie')
        install(store, 'hero_mobile', 'hero-mobile.webp', 'editorials', 'hero-hoodie-mobile')
        for slug, name, filename in CATALOG:
            product = Product.objects.filter(slug=slug, demo=True).first()
            if product and (product.image.startswith('demo-') or product.image.startswith('streetwear/')):
                product.image = 'streetwear/' + filename
                product.name = name
                product.description = 'Fotografia real de referência para explorar a experiência KYMA. Esta peça integra o catálogo demonstrativo; os detalhes de mercadoria serão definidos pela loja.'
                if slug == 'calca-horizonte':
                    product.category = Category.objects.get(slug='camisetas')
                product.save(update_fields=['image', 'name', 'description', 'category'])
                colors = {'blazer-linha-livre': ('Areia', 'Laranja'), 'moletom-horizonte': ('Cinza', 'Preto'),
                          'camiseta-contorno': ('Off-white', 'Branco'), 'camisa-traco': ('Branco', 'Azul'),
                          'calca-horizonte': ('Areia', 'Preto'), 'jaqueta-intervalo': ('Grafite', 'Denim'),
                          'calca-forma': ('Preto', 'Verde')}
                if slug in colors:
                    old, new = colors[slug]
                    for variant in product.variants.filter(color=old):
                        if not product.variants.filter(size=variant.size, color=new).exists():
                            variant.color = new
                            variant.save(update_fields=['color'])
        categories = {
            'camisetas': ('Camisetas', 'graphic-back.webp'),
            'alfaiataria': ('Estampas', 'graphic-red-product.webp'),
            'calcas': ('Calças', 'cargo-street.webp'),
            'camadas': ('Camadas', 'denim-jacket.webp'),
        }
        for slug, (name, filename) in categories.items():
            category = Category.objects.filter(slug=slug).first()
            if category:
                if not category.image or Path(category.image.name).name.startswith('kyma-reference-'):
                    category.name = name
                    category.save(update_fields=['name'])
                install(category, 'image', 'streetwear/' + filename, 'categories', slug)
        for banner in Banner.objects.select_related('collection'):
            filename = {'essenciais': 'graphic-cartoon.webp', 'nova-perspectiva': 'graphic-blue.webp',
                        'movimento': 'denim-jacket.webp'}.get(banner.collection.slug)
            if filename:
                install(banner, 'image', 'streetwear/' + filename, 'banners', banner.collection.slug)
        self.stdout.write(self.style.SUCCESS('Fotos reais aplicadas. Pedidos, estoque e uploads próprios preservados.'))
