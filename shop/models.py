import uuid
from django.db import models
from django.db.models import Q, F
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    def save(self,*args,**kwargs):
        self.email = self.email.lower().strip()
        super().save(*args,**kwargs)

class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/',blank=True)
    def __str__(self): return self.name

class Collection(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    collections = models.ManyToManyField(Collection, blank=True)
    price = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text='Preço em centavos')
    description = models.TextField()
    composition = models.CharField(max_length=250)
    care = models.CharField(max_length=300)
    size_guide = models.TextField(blank=True)
    image = models.CharField(max_length=250, default='demo-tee.svg', help_text='Arquivo do catálogo demonstrativo')
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    demo = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Variant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=40)
    stock = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100000)])
    reserved = models.PositiveIntegerField(default=0)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['product', 'size', 'color'], name='unique_variant'),
            models.CheckConstraint(condition=Q(reserved__lte=F('stock')), name='reserved_within_stock')]
    @property
    def available(self): return self.stock - self.reserved
    def __str__(self): return f'{self.product} · {self.size} · {self.color}'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt = models.CharField(max_length=200)

class Address(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=9)
    street = models.CharField(max_length=150)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=2)
    def __str__(self): return f'{self.name} · {self.city}'

class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    percent = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    active = models.BooleanField(default=False)
    expires = models.DateTimeField(null=True, blank=True)

class ShippingMethod(models.Model):
    name = models.CharField(max_length=80)
    price = models.PositiveIntegerField(help_text='Centavos')
    days = models.CharField(max_length=60)
    states = models.CharField(max_length=120, blank=True, help_text='UFs separadas por vírgula; vazio = todas')
    active = models.BooleanField(default=False)
    demo = models.BooleanField(default=True)
    def __str__(self): return self.name

class StoreSettings(models.Model):
    announcement = models.CharField(max_length=180, default='KYMA — encontre sua próxima expressão')
    hero_title = models.CharField(max_length=100, default='SEU ESTILO. SUA PRESENÇA.')
    hero_text = models.CharField(max_length=200, default='Diferentes formas de vestir. A mesma liberdade de ser você.')
    hero_image = models.ImageField(upload_to='editorials/',blank=True)
    hero_mobile = models.ImageField(upload_to='editorials/',blank=True)
    about = models.TextField(default='A KYMA reúne diferentes estilos em um espaço para descobrir sua próxima expressão.')
    contact_email = models.EmailField(blank=True)
    company_details = models.TextField(blank=True)
    shipping_policy = models.TextField(blank=True)
    returns_policy = models.TextField(blank=True)
    privacy_policy = models.TextField(blank=True)
    demo = models.BooleanField(default=True)
    def __str__(self): return 'Configurações KYMA'
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

class Banner(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=160)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='banners/',blank=True)

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    checkout_key = models.UUIDField(unique=True)
    owner_hash = models.CharField(max_length=64)
    email = models.EmailField()
    name = models.CharField(max_length=100)
    address = models.JSONField()
    shipping_name = models.CharField(max_length=80)
    shipping_days = models.CharField(max_length=60)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(default=0)
    shipping = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    coupon_code = models.CharField(max_length=30, blank=True)
    currency = models.CharField(max_length=3, default='brl')
    status = models.CharField(max_length=20, default='pending', choices=[(s,l) for s,l in [
        ('pending','Aguardando pagamento'), ('paid','Pagamento aprovado'), ('preparing','Em preparação'),
        ('shipped','Enviado'), ('completed','Entregue'), ('failed','Pagamento recusado'),
        ('expired','Pagamento expirado'), ('canceled','Cancelado'), ('refund_pending','Reembolso em análise'), ('refunded','Reembolsado')]])
    provider = models.CharField(max_length=10, default='demo')
    provider_session = models.CharField(max_length=200, blank=True)
    payment_intent = models.CharField(max_length=200, blank=True)
    payment_url = models.URLField(max_length=1000, blank=True)
    tracking = models.CharField(max_length=200, blank=True)
    expires = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{str(self.id)[:8]} · {self.get_status_display()}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()

class PaymentEvent(models.Model):
    event_id = models.CharField(max_length=200, unique=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

class OrderNotice(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)
    sent = models.BooleanField(default=False)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['order','status'], name='unique_notice')]

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class Audit(models.Model):
    actor = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=180)
    object_id = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

class RateBucket(models.Model):
    key = models.CharField(max_length=64, unique=True)
    started = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)

class Metric(models.Model):
    event = models.CharField(max_length=30)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    order = models.OneToOneField(Order, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
