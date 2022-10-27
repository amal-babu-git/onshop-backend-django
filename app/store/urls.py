from django import views
from django.urls import path, include
from rest_framework_nested import routers
from .import views

# base routes
router = routers.DefaultRouter()
# this route will handle store/products and store/products/product_id
router.register('products', views.ProductViewSet, basename='products')
# this router contain 2 functionality with basename , i.e: it will handle store/collections/ and store/collection/collection_id
router.register('collections', views.CollectionViewSet, basename='collections')
router.register('carts', viewset=views.CartViewSet, basename='carts')
router.register('customers', viewset=views.CustomerViewSet,
                basename='customers')
router.register('orders', viewset=views.OrderViewSet, basename='orders')


# Create child router to show review , refer--> https://github.com/alanjds/drf-nested-routers
# the url include product/product_pk/reviews/pk/ , this url parameters can access in viewset class
products_router = routers.NestedDefaultRouter(
    parent_router=router, parent_prefix='products', lookup='product')
# register
products_router.register(
    prefix='reviews', viewset=views.ReviewViewSet, basename='product-reviews')
products_router.register(
    prefix='images', viewset=views.ProductImageViewSet, basename='product-images')

carts_router = routers.NestedDefaultRouter(
    parent_router=router, parent_prefix='carts', lookup='cart')
carts_router.register(
    prefix='items', viewset=views.CartItemViewSet, basename='cart-items')


customer_address_router = routers.NestedDefaultRouter(
    parent_router=router, parent_prefix='customers', lookup='customer'
)
customer_address_router.register(
    prefix='address', viewset=views.AddressViewSet, basename='customer-address')

urlpatterns = router.urls + products_router.urls + \
    carts_router.urls  + customer_address_router.urls


# urlpatterns = [

#     path('', include(router.urls))
# ]
