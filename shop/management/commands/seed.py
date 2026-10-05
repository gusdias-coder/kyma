from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from shop.models import Category, Collection, Product, Variant, StoreSettings, ShippingMethod, Banner

class Command(BaseCommand):
    help = 'Cria apenas dados demonstrativos; nunca substitui produtos existentes.'
    def handle(self,*args,**kwargs):
        if not settings.DEBUG: raise CommandError('Seed demonstrativo é permitido apenas localmente.')
        StoreSettings.objects.get_or_create(pk=1)
        cats = {}
        for slug,name in [('camisetas','Camisetas'),('alfaiataria','Estampas'),('calcas','Calças'),('camadas','Camadas')]:
            cats[slug],_ = Category.objects.get_or_create(slug=slug,defaults={'name':name})
        collections = []
        for slug,name,description in [('essenciais','Essenciais','A base para diferentes formas de vestir.'),
            ('nova-perspectiva','Nova perspectiva','Linhas, texturas e novas combinações.'),
            ('movimento','Em movimento','Conforto para acompanhar seu ritmo.')]:
            c,_=Collection.objects.get_or_create(slug=slug,defaults={'name':name,'description':description})
            collections.append(c)
            Banner.objects.get_or_create(collection=c,defaults={'title':name,'subtitle':description})
        samples = [('Camiseta Essencial','camiseta-essencial','camisetas',12900,'streetwear/graphic-back.webp','Preto'),
            ('Camiseta Gráfica Solar','blazer-linha-livre','alfaiataria',32900,'streetwear/graphic-red-product.webp','Laranja'),
            ('Calça Forma','calca-forma','calcas',21900,'streetwear/cargo-street.webp','Verde'),
            ('Moletom Horizonte','moletom-horizonte','camadas',24900,'streetwear/hoodie-black-product.webp','Preto'),
            ('Camiseta Contorno','camiseta-contorno','camisetas',13900,'streetwear/graphic-cartoon.webp','Branco'),
            ('Camiseta Gráfica Azul','camisa-traco','alfaiataria',18900,'streetwear/graphic-blue.webp','Azul'),
            ('Camiseta Base','calca-horizonte','camisetas',23900,'streetwear/denim-street.webp','Preto'),
            ('Jaqueta Intervalo','jaqueta-intervalo','camadas',35900,'streetwear/denim-jacket.webp','Denim')]
        for i,(name,slug,cat,price,image,color) in enumerate(samples):
            p,created=Product.objects.get_or_create(slug=slug,defaults={'name':name,'category':cats[cat],'price':price,
                'image':image,'featured':True,'description':'Peça conceitual para demonstrar a experiência KYMA. Substitua pelos detalhes do produto real antes de vender.',
                'composition':'Composição demonstrativa — preencher com a etiqueta real.',
                'care':'Cuidados demonstrativos — consultar a etiqueta do produto real.',
                'size_guide':'Medidas ilustrativas: P 88–94 cm / M 95–101 cm / G 102–108 cm. Não usar como referência de compra real.'})
            if created:
                p.collections.add(collections[i % 3])
                for size in ['P','M','G']: Variant.objects.create(product=p,size=size,color=color,stock=5)
        ShippingMethod.objects.get_or_create(name='Entrega demonstrativa',defaults={'price':1900,'days':'3–7 dias (simulação)','active':True,'demo':True})
        from django.core.management import call_command
        call_command('streetwear_photos', stdout=self.stdout)
        call_command('expand_catalog', stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS('Catálogo demonstrativo preparado.'))
