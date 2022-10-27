from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Address, Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage, Review
from store.pagination import DefaultPagination
from store.permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission
from store.serializers import AddAddressSerializer, AddCartItemSerilizer, AddressSerializer, CancelOrderSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, ReviewSerializer, AddAddressSerializer, UpdateAddressSerializer, UpdateCartItemSerilizer, UpdateOrderSerializer
from store.filters import ProductFilter
from django.db.models import Count


# Create your views here.

class ProductViewSet(ModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    -- get, post, put, delete.....

    override the methodes if any cusomization needed
    """
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    # Using django filter library for filtering product based on the collection
    # define filterbackend and filteing logic in a class
    # e.g: url--> http://127.0.0.1:8000/store/products/?collection_id=4 , filtering query is-->products/?collection_id=4
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    # sorting based on unit_price and last_update
    ordering_fields = ['unit_price', 'last_update']
    pagination_class = DefaultPagination

    # overrid

    def get_serializer_context(self):
        return {'request': self.request}

    # overrid destroy to delete
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': "Can't delete , product associated with an order"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):

    serializer_class = CollectionSerializer
    queryset = Collection.objects.annotate(
        product_count=Count('products')).all().order_by('title')
    permission_classes = [IsAdminOrReadOnly]

    # Override
    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection.objects.annotate(
            product_count=Count('products')), pk=kwargs['pk'])

        if collection.products.count() > 0:
            return Response({'error': "Can't delete , it includes one or more products"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


# TODO: update http methos when client app have fecility to update comment
class ReviewViewSet(ModelViewSet):

    # permission_classes=[IsAuthenticated]
    http_method_names = ['get', 'post',
                         'options', 'headers']  # +['put', 'delete', ]

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return [IsAuthenticated()]
        return super().get_permissions()

    serializer_class = ReviewSerializer

    def get_queryset(self):
        # product_pk is from url
        return Review.objects.filter(product_id=self.kwargs['product_pk']).order_by('-id')

    # form this view class we can access url parameters;
    # and send it to serializer by using get_serializer_context()
    # Overriding ; send to serializer ; for getting product_id
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin,  # create cart with id, pass post request with empty ,
                  RetrieveModelMixin,  # ../carts/id/ retriving a spesific cart
                  DestroyModelMixin,  # delete a 'cart/id/'
                  GenericViewSet
                  ):

    # prefetch_related used for fetch child table items, in foreignkey realation we use select_related
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):

    # must be lowercase in the list
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerilizer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerilizer
        return CartItemSerializer

    def get_queryset(self):

        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')

    # cart_pk value from url; add to context dict ; so we can access this value in serializer for creating custom save methode(override save methode)
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


# TODO : add adress post method FIXME : handle permission
class AddressViewSet(ModelViewSet):

    http_method_names = ['get', 'put', 'post', 'delete']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(customer_id=self.kwargs['customer_pk'])

    def get_serializer_context(self):
        return {'customer_id': self.kwargs['customer_pk']}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddAddressSerializer
        elif self.request.method == 'PUT':
            return UpdateAddressSerializer
        return AddressSerializer


class CustomerViewSet(ModelViewSet):

    queryset = Customer.objects.prefetch_related('address').all()
    serializer_class = CustomerSerializer
    # Allow all operation to admin user. TODO: FullDjangoModelPermission (our customized permission class ) can also use here
    permission_classes = [IsAdminUser]

    # Define a  custom action get customer profile
    # here detail=Flase , so it is avalilable in the list view
    # list-view means store/customers/me , detail-view means store/customers/id/me
    # this method only available for autheticated user, overrided the permission class to Is Autheticated

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(
            user_id=request.user.id)
        if request.method == 'GET':
            serilalizer = CustomerSerializer(customer)
            return Response(serilalizer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # implimetaion of custom permission for view history . TODO:
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('Ok')


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch',
                         'delete', 'head', 'options']

    # def get_permissions(self):
    #     if self.request.method in ['PATCH', 'DELETE']:
    #         return [IsAdminUser()]
    #     return [IsAuthenticated()]
    permission_classes=[IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        # admin or staff are able to see all orders
        if user.is_staff:
            return Order.objects.prefetch_related('items').all().order_by('-id')

        customer_id = Customer.objects \
            .only('id').get(user_id=user.id)

        return Order.objects.filter(customer_id=customer_id).order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id': self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        # deserialize the saved order using order serializer ; CreateOrderSerializer only for creating and returning with cart_id
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class ProductImageViewSet(ModelViewSet):

    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
