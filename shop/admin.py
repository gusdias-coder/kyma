from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django_otp.admin import OTPAdminSite
from .models import (Customer, Category, Collection, Product, Variant, ProductImage, Coupon, ShippingMethod,
    StoreSettings, Banner, Order, OrderItem, Audit, Subscriber, Metric)
from .forms import SafeImageForm,CategoryImageForm,BannerImageForm,StoreImageForm
from .services import fulfillment, CommerceError

site = OTPAdminSite(name='kyma_admin')
site.site_header = 'KYMA · Gestão'
site.site_title = 'KYMA'
site.index_title = 'Sua loja, em um só lugar'

class SuperuserOnly:
    def has_module_permission(self,request): return request.user.is_superuser
    def has_view_permission(self,request,obj=None): return request.user.is_superuser
    def has_add_permission(self,request): return request.user.is_superuser
    def has_change_permission(self,request,obj=None): return request.user.is_superuser
    def has_delete_permission(self,request,obj=None): return request.user.is_superuser

class CustomerAdmin(SuperuserOnly,UserAdmin):
    list_display = ('email','first_name','is_active','is_staff')
    fieldsets = UserAdmin.fieldsets + (('Verificação',{'fields':('email_verified',)}),)

site.register(Customer,CustomerAdmin)
site.register(Group,type('ProtectedGroups',(SuperuserOnly,GroupAdmin),{}))

class AuditedAdmin(admin.ModelAdmin):
    def save_model(self,request,obj,form,change):
        super().save_model(request,obj,form,change)
        Audit.objects.create(actor=request.user,action=f'{obj._meta.model_name}:save',object_id=str(obj.pk))
    def delete_model(self,request,obj):
        Audit.objects.create(actor=request.user,action=f'{obj._meta.model_name}:delete',object_id=str(obj.pk))
        super().delete_model(request,obj)
    def delete_queryset(self,request,qs):
        for obj in qs:
            Audit.objects.create(actor=request.user,action=f'{obj._meta.model_name}:delete',object_id=str(obj.pk))
        super().delete_queryset(request,qs)

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    readonly_fields = ('reserved',)

class PhotoInline(admin.TabularInline):
    model = ProductImage
    form = SafeImageForm
    extra = 0

@admin.register(Product,site=site)
class ProductAdmin(AuditedAdmin):
    list_display = ('name','category','price','active','demo')
    list_filter = ('category','active','demo')
    search_fields = ('name','slug')
    prepopulated_fields = {'slug':('name',)}
    inlines = (VariantInline,PhotoInline)
    filter_horizontal = ('collections',)
    def save_formset(self,request,form,formset,change):
        # Never overwrite reservation counters loaded before a concurrent checkout.
        if formset.model is Variant:
            from django.db import transaction
            from django.core.exceptions import ValidationError
            with transaction.atomic():
                instances = formset.save(commit=False)
                for obj in instances:
                    if obj.pk:
                        locked = Variant.objects.select_for_update().get(pk=obj.pk)
                        if obj.stock < locked.reserved:
                            raise ValidationError('Estoque não pode ficar abaixo das reservas atuais.')
                        obj.reserved = locked.reserved
                    obj.save()
                for obj in formset.deleted_objects: obj.delete()
                formset.save_m2m()
        else: super().save_formset(request,form,formset,change)

class ItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('name','quantity','price')
    readonly_fields = fields
    def has_add_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False

def transition_action(status,label):
    def action(modeladmin,request,queryset):
        for order in queryset:
            try: fulfillment(order.pk,status,request.user)
            except CommerceError as exc: modeladmin.message_user(request,str(exc),messages.ERROR)
    action.__name__ = 'mark_' + status
    action.short_description = label
    action.allowed_permissions = ['change']
    return action

@admin.register(Order,site=site)
class OrderAdmin(AuditedAdmin):
    list_display = ('id','name','status','total','provider','created')
    list_filter = ('status','provider')
    search_fields = ('name','email','id')
    readonly_fields = tuple(f.name for f in Order._meta.fields if f.name != 'tracking')
    inlines = (ItemInline,)
    actions = [transition_action(s,l) for s,l in [('canceled','Cancelar pedido não pago'),('preparing','Preparar pedido'),('shipped','Confirmar envio'),
        ('completed','Confirmar entrega'),('refund_pending','Abrir análise de reembolso'),('refunded','Executar reembolso integral')]]
    def has_add_permission(self,request): return False
    def has_delete_permission(self,request,obj=None): return False
    def save_model(self,request,obj,form,change):
        # Tracking edits must not overwrite a payment transition received concurrently.
        Order.objects.filter(pk=obj.pk).update(tracking=obj.tracking)
        Audit.objects.create(actor=request.user,action='order:tracking',object_id=str(obj.pk))

@admin.register(Audit,site=site)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('created','actor','action','object_id')
    readonly_fields = ('created','actor','action','object_id')
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False

@admin.register(Metric,site=site)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('event','created')
    exclude = ('order',)
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False

site.register([Collection,Coupon,ShippingMethod],AuditedAdmin)
site.register(Category,type('CategoryAdmin',(AuditedAdmin,),{'form':CategoryImageForm}))
site.register(Banner,type('BannerAdmin',(AuditedAdmin,),{'form':BannerImageForm}))
site.register(StoreSettings,type('StoreAdmin',(AuditedAdmin,),{'form':StoreImageForm}))
@admin.register(Subscriber,site=site)
class SubscriberAdmin(AuditedAdmin):
    list_display = ('email','active','created')
    readonly_fields = ('token','created')
    def has_add_permission(self,request): return False
