"""Add a larger local reference assortment without resetting existing stock/orders."""
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from shop.models import Category, Collection, Product, Variant, StoreSettings
from shop.reference_catalog import COLLECTIONS, PRODUCTS

class Command(BaseCommand):
    help = 'Amplia o catálogo demonstrativo local para 24 peças e oito coleções.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not settings.DEBUG or not StoreSettings.objects.filter(pk=1, demo=True).exists():
            raise CommandError('A ampliação de referência exige uma loja demonstrativa local.')
        for row in PRODUCTS:
            if not (Path(settings.BASE_DIR) / f'static/images/expanded/photo-{row[4]}.webp').exists():
                raise CommandError('Fotografias empacotadas ausentes; nenhuma peça foi criada.')
        categories = {}
        for slug, name, image in [
            ('camisetas','Camisetas','streetwear/graphic-back.webp'),
            ('alfaiataria','Estampas','streetwear/graphic-red-product.webp'),
            ('calcas','Calças','streetwear/cargo-street.webp'),
            ('camadas','Camadas','streetwear/denim-jacket.webp'),
            ('camisas','Camisas','expanded/photo-15965650.webp'),
            ('alfaiataria-urbana','Alfaiataria','expanded/photo-10619446.webp'),
            ('moletons','Moletons','expanded/photo-5692478.webp'),
            ('jaquetas','Jaquetas','expanded/photo-19392467.webp'),
        ]:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name':name})
            categories[slug] = cat
        collections = {}
        for slug, name, description, image in COLLECTIONS:
            collections[slug], _ = Collection.objects.get_or_create(slug=slug, defaults={'name':name,'description':description})
        created_count = 0
        for name, slug, category, price, photo, color, groups in PRODUCTS:
            item, created = Product.objects.get_or_create(slug=slug, defaults={
                'name':name, 'category':categories[category], 'price':price,
                'image':f'expanded/photo-{photo}.webp', 'demo':True, 'featured':True,
                'description':'Fotografia real de referência para explorar este estilo. Produto demonstrativo: detalhes e disponibilidade comercial serão definidos pela KYMA.',
                'composition':'Composição de referência — preencher a partir da etiqueta da mercadoria real.',
                'care':'Cuidados de referência — consultar a etiqueta da mercadoria real.',
                'size_guide':'Tamanhos demonstrativos PP, P, M, G e GG. Consulte as medidas reais antes de vender.',
            })
            if created:
                created_count += 1
                item.collections.add(*(collections[group] for group in groups))
                for size in ['PP','P','M','G','GG']:
                    Variant.objects.create(product=item, size=size, color=color, stock=6)
        for slug, groups in {
            'camiseta-essencial':['street-culture','noite-urbana'],
            'blazer-linha-livre':['statement','street-culture'],
            'calca-forma':['street-culture','movimento'],
            'moletom-horizonte':['noite-urbana','essenciais'],
            'camiseta-contorno':['street-culture','statement'],
            'camisa-traco':['statement'],
            'calca-horizonte':['denim','essenciais'],
            'jaqueta-intervalo':['denim','nova-perspectiva'],
        }.items():
            item = Product.objects.filter(slug=slug, demo=True).first()
            if item:
                item.collections.add(*(collections[group] for group in groups))
        self.stdout.write(self.style.SUCCESS(f'{created_count} peças de referência adicionadas; estoque e pedidos existentes preservados.'))
