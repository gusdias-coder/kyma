import io
import re
from PIL import Image
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.files.base import ContentFile
from .models import Customer, Address, ProductImage, Category, StoreSettings, Banner

STATES = 'AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split()

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=80)
    email = forms.EmailField(label='E-mail')
    class Meta:
        model = Customer
        fields = ['first_name', 'email', 'password1', 'password2']
    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if Customer.objects.filter(email=email).exists(): raise forms.ValidationError('Não foi possível usar este e-mail. Tente recuperar seu acesso.')
        return email
    def save(self, commit=True):
        import uuid
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex
        user.is_active = False
        if commit: user.save()
        return user

class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label='E-mail')
    def clean(self):
        email = self.cleaned_data.get('username', '').lower().strip()
        user = Customer.objects.filter(email=email).first()
        self.cleaned_data['username'] = user.username if user else 'nonexistent-account'
        return super().clean()

class CheckoutForm(forms.Form):
    name = forms.CharField(label='Nome completo', max_length=100)
    email = forms.EmailField(label='E-mail')
    postal_code = forms.CharField(label='CEP', max_length=9)
    street = forms.CharField(label='Rua', max_length=150)
    number = forms.CharField(label='Número', max_length=20)
    complement = forms.CharField(label='Complemento', max_length=80, required=False)
    city = forms.CharField(label='Cidade', max_length=80)
    state = forms.ChoiceField(label='Estado', choices=[(s,s) for s in STATES])
    shipping_method = forms.ChoiceField(label='Entrega', choices=[])
    coupon = forms.CharField(label='Cupom (opcional)', max_length=30, required=False)
    accept = forms.BooleanField(label='Revisei os dados, a entrega e o total do pedido.')
    checkout_key = forms.UUIDField(widget=forms.HiddenInput)
    def clean_postal_code(self):
        value = self.cleaned_data['postal_code']
        if not re.fullmatch(r'\d{5}-?\d{3}', value): raise forms.ValidationError('Informe um CEP com 8 dígitos.')
        return value

class AddressForm(forms.ModelForm):
    state = forms.ChoiceField(label='Estado', choices=[(s,s) for s in STATES])
    class Meta:
        model = Address
        fields = ['name','postal_code','street','number','complement','city','state']
        labels = {'name':'Nome do endereço','postal_code':'CEP','street':'Rua','number':'Número','complement':'Complemento','city':'Cidade'}
    def clean_postal_code(self):
        value = self.cleaned_data['postal_code']
        if not re.fullmatch(r'\d{5}-?\d{3}', value): raise forms.ValidationError('CEP inválido.')
        return value

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name','last_name']
        labels = {'first_name':'Nome','last_name':'Sobrenome'}

class SafeImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
    def clean_image(self):
        return safe_image(self.cleaned_data['image'])

def safe_image(image):
    if not hasattr(image, 'content_type'): return image
    if image.size > 5 * 1024 * 1024: raise forms.ValidationError('Limite de 5 MB.')
    try:
        original = Image.open(image)
        if original.format not in ('JPEG','PNG','WEBP') or original.width * original.height > 16000000:
            raise ValueError()
        original.load()
        original.thumbnail((1800,1800))
        out = io.BytesIO()
        original.convert('RGB').save(out, 'WEBP', quality=85)
        return ContentFile(out.getvalue(), name='product.webp')
    except Exception as exc: raise forms.ValidationError('Envie uma imagem JPEG, PNG ou WebP válida.') from exc

class CategoryImageForm(SafeImageForm):
    class Meta:
        model = Category
        fields = '__all__'

class BannerImageForm(SafeImageForm):
    class Meta:
        model = Banner
        fields = '__all__'

class StoreImageForm(forms.ModelForm):
    class Meta:
        model = StoreSettings
        fields = '__all__'
    def clean_hero_image(self): return safe_image(self.cleaned_data['hero_image'])
    def clean_hero_mobile(self): return safe_image(self.cleaned_data['hero_mobile'])
