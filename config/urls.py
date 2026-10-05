from django.urls import path
from django.contrib.auth import views as auth
from shop import views
from shop.admin import site

urlpatterns = [
    path('acompanhar/<str:token>/',views.guest_tracking,name='guest_tracking'),
    path('',views.home,name='home'), path('loja/',views.catalog,name='catalog'),
    path('colecoes/',views.collections,name='collections'), path('produto/<slug:slug>/',views.product,name='product'),
    path('carrinho/',views.cart,name='cart'), path('carrinho/atualizar/',views.cart_update,name='cart_update'),
    path('checkout/',views.checkout,name='checkout'), path('checkout/total/',views.quote,name='quote'),
    path('pedido/<uuid:pk>/',views.order_detail,name='order'), path('pedido/<uuid:pk>/pagar/',views.retry_payment,name='retry_payment'),
    path('pagamento/demo/<uuid:pk>/',views.demo_payment,name='demo_payment'),
    path('webhooks/stripe/',views.webhook,name='webhook'),
    path('conta/',views.account,name='account'), path('conta/criar/',views.register,name='register'),
    path('conta/entrar/',views.sign_in,name='login'), path('conta/sair/',views.sign_out,name='logout'),
    path('conta/ativar/<uid>/<token>/',views.verify,name='verify'),
    path('conta/reenviar/',views.resend_verification,name='resend'),
    path('conta/endereco/',views.address,name='address_new'), path('conta/endereco/<int:pk>/',views.address,name='address'),
    path('conta/endereco/<int:pk>/remover/',views.remove_address,name='address_remove'),
    path('conta/senha/',views.password_change,name='password_change'),
    path('conta/recuperar/',auth.PasswordResetView.as_view(template_name='form.html',extra_context={'title':'Recuperar acesso','button':'Enviar link'},
        email_template_name='registration/reset_email.txt',subject_template_name='registration/reset_subject.txt'),name='password_reset'),
    path('conta/recuperar/enviado/',auth.PasswordResetDoneView.as_view(template_name='message.html',extra_context={'title':'Confira seu e-mail','text':'Se houver uma conta ativa, enviaremos as instruções.'}),name='password_reset_done'),
    path('conta/nova-senha/<uidb64>/<token>/',auth.PasswordResetConfirmView.as_view(template_name='form.html',extra_context={'title':'Nova senha','button':'Salvar senha'}),name='password_reset_confirm'),
    path('conta/nova-senha/concluido/',auth.PasswordResetCompleteView.as_view(template_name='message.html',extra_context={'title':'Senha atualizada','text':'Você já pode entrar com sua nova senha.'}),name='password_reset_complete'),
    path('novidades/',views.subscribe,name='subscribe'), path('novidades/<uuid:token>/',views.subscription,name='subscription'),
    path('eventos/',views.metric,name='metric'), path('gestao/',site.urls), path('info/<slug:slug>/',views.page,name='page'),
]
# Only registered, re-encoded product images are served, never arbitrary filesystem files.
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from shop.models import ProductImage,Category,StoreSettings,Banner
def product_media(request,filename):
    photo = get_object_or_404(ProductImage,image=f'products/{filename}',product__active=True)
    response = FileResponse(photo.image.open('rb'),content_type='image/webp')
    response['X-Content-Type-Options'] = 'nosniff'
    return response
urlpatterns += [path('media/products/<str:filename>',product_media)]
def editorial_media(request,folder,filename):
    from django.db.models import Q
    from django.http import Http404
    value=f'{folder}/{filename}'
    if folder=='categories': obj=get_object_or_404(Category,image=value); file=obj.image
    elif folder=='banners': obj=get_object_or_404(Banner,image=value,active=True); file=obj.image
    elif folder=='editorials':
        obj=get_object_or_404(StoreSettings,Q(hero_image=value)|Q(hero_mobile=value),pk=1)
        file=obj.hero_image if obj.hero_image.name==value else obj.hero_mobile
    else: raise Http404
    response=FileResponse(file.open('rb'),content_type='image/webp')
    response['X-Content-Type-Options']='nosniff'
    return response
urlpatterns += [path('media/<str:folder>/<str:filename>',editorial_media)]
