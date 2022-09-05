from typing import Any, Optional, Sequence
from django.db.models.query import QuerySet
from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

from . import models
from payment.models import Payment


# Custom filter for product model in admin panel -- inventory filter
class InventoryFilter(admin.SimpleListFilter):
    title: str = 'inventory'
    parameter_name: str = 'inventory'

    # lookup  methode is for -- display filter values
    def lookups(self, request: Any, model_admin: Any):
        return [
            ('<10', 'Low'),
        ]

    # queryset is for impliment filtering logic
    def queryset(self, request: Any, queryset: QuerySet) -> Optional[QuerySet]:
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields: Sequence[str] = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail">')
        return ''

    class Media:
        css = {
            'all': ['store/styles.css']
        }

#FIXME:NOT WORKING
# class ReviewInline(admin.StackedInline):
#     model=models.Review
#     min_num=1

#FIXME : Review not displaying TODO : problem solved tesing mode
@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product','name','description', ]

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):

    # Product admin form customization
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ['collection']
    inlines = [ProductImageInline]
    #exclude: Optional[Sequence[str]] = ['promotions']
    # Admin Product panel customization
    list_display = ['id', 'title', 'unit_price', 'inventory',
                    'inventory_status', 'collection_title']
    list_editable = ['unit_price', 'inventory']
    list_filter = ['last_update', 'collection', InventoryFilter]
    actions = ['clear_inventory']
    search_fields: Sequence[str] = ['title', 'id']
    list_per_page = 20
    # For preloading related
    list_select_related = ['collection']

    # Responsible for show collection_title in list_display
    def collection_title(self, product):
        return product.collection.title

    # Responsible for show inventory_status in list_display
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    # Create custom action for clear inventory
    @admin.action(description='Clear inventoty')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products ware successfully updated',
            messages.SUCCESS
        )


class AddressInline(admin.StackedInline):
    model = models.Address
    min_num = 1
    max_num = 1


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):

    # Customizing table view of customers in admin panel
    list_display = ['id', 'first_name',
                    'last_name', 'membership', 'order_count']
    list_editable = ['membership']
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    # __startswith is a lookup , __istarstwith means the etra 'i' add for  make it case insensitive
    # results firstname start with given search leter...
    search_fields = ['user__first_name__istartswith',
                     'user__last_name__istartswith']
    inlines = [AddressInline]

    list_per_page: int = 20

    @admin.display(ordering='order_count')
    def order_count(self, customer):
        # When click the order_count linkto-> order page of that customer
        url = (reverse('admin:store_order_changelist')
               + '?'
               + urlencode({'customer__id': str(customer.id)}))

        return format_html(f'<a href={url}>{customer.order_count} order(s)</a>')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            order_count=Count('order')
        )


class PaymentInline(admin.StackedInline):
    model = Payment
    max_num=1

# OrderItem inline class is for show the item form inside order admin form
# Here TabularInline is used , StackedInline is also available


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product']
    extra: int = 0
    min_num = 1
    max_num = 20

# TODO: Add a calculated field to see total bill of order


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id',
                    'customer', 'total_price','is_delivered', 'is_shipped',  'is_cancelled']
    list_editable: Sequence[str] = [
        'is_delivered', 'is_shipped', 'is_cancelled']

    list_per_page = 10
    # Form customization
    autocomplete_fields: Sequence[str] = ['customer']
    inlines = [OrderItemInline,PaymentInline]


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Actually we don't have product_count 
    field in our database , so we just 
    create a methode for display product count,
    : collection table does't have that field 
    since we annotate that field by overrding
    get_queryset methode in ModelAdmin class

    """
    list_display = ['title', 'product_count']
    search_fields = ['title']

    @admin.display(ordering='product_count')
    def product_count(self, collection):
        # url=reverse('admin:app_model_page)
        url = (reverse('admin:store_product_changelist') +
               '?' +
               urlencode({
                   'collection__id': str(collection.id)
               }))

        return format_html(f'<a href="{url}">{collection.product_count}</a>')

    # overriding get_queryset methode from ModelAdmin class for calculate count of product in a collection
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )
