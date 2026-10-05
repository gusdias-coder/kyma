from django import template
from django.templatetags.static import static
register = template.Library()
@register.filter
def money(value):
    return 'R$ ' + f'{int(value)/100:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
@register.filter
def image_url(product):
    photos = list(product.photos.all())
    if photos: return photos[0].image.url
    legacy = {'demo-tee.svg':'graphic-back.webp','demo-blazer.svg':'graphic-red-product.webp',
              'demo-pants.svg':'cargo-street.webp','demo-hoodie.svg':'hoodie-black-product.webp',
              'demo-tee-ivory.svg':'graphic-cartoon.webp','demo-shirt.svg':'graphic-blue.webp',
              'demo-pants-sand.svg':'denim-street.webp','demo-jacket.svg':'denim-jacket.webp'}
    filename = 'streetwear/'+legacy[product.image] if product.image in legacy else product.image
    return static('images/' + filename)
@register.filter
def multiply(a,b): return a*b
@register.filter
def category_image(category):
    if category.image: return category.image.url
    images={'camisetas':'graphic-back.webp','alfaiataria':'graphic-red-product.webp',
            'calcas':'cargo-street.webp','camadas':'denim-jacket.webp'}
    expanded={'camisas':15965650,'alfaiataria-urbana':10619446,'moletons':5692478,'jaquetas':19392467}
    if category.slug in expanded: return static(f'images/expanded/photo-{expanded[category.slug]}.webp')
    return static('images/streetwear/'+images.get(category.slug,'graphic-back.webp'))

@register.filter
def collection_image(collection):
    from shop.reference_catalog import COLLECTIONS
    covers = {row[0]:row[3] for row in COLLECTIONS}
    return static('images/'+covers.get(collection.slug,'streetwear/graphic-back.webp'))

@register.filter
def purchasable_variants(product):
    return [variant for variant in product.variants.all() if variant.available > 0]
