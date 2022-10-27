
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from store.models import Address, Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage, Review
from store.signals import order_created
from payment.serializers import PaymentSerializer
from payment.models import Payment


class CollectionSerializer(serializers.ModelSerializer):
    # This field a custom field , so read_only should be True, dont need to send it ti the server
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
        # read_only_fields = ['product_count']


class ProductImageSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    collection = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'last_update', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection', 'images']

    # CustomSerializerField
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return round((product.unit_price * Decimal(1.1)), 2)


class ReviewSerializer(serializers.ModelSerializer):

    product = serializers.CharField(read_only=True)

    # Overriding create methode and save data manually with product id
    # Because we have additional data -product_id -for add to database
    def create(self, validated_data):
        # Accessing product_id from context object, product id add to this dict in viewset class by overring get_setalizer_context()
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description', 'product']


# this for show product details in CartItemSerializer
class SimpleProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):

    product = SimpleProductSerializer()
    # custom field for show total price
    total_price = serializers.SerializerMethodField()

    # define custom methode for show total price
    # get_total_price name is a convention : get_ followed by method_name
    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):

    # We dont want to send id to server, just read from server
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    # calculate total price of a cart
    def get_total_price(self, cart: Cart):
        return sum([(item.quantity * item.product.unit_price) for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerilizer(serializers.ModelSerializer):

    # product_id declaration
    product_id = serializers.IntegerField()

    # Validating product_id, if it is not exists then rise an error message
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No products with given id')
        return value

    # Override, create a new cartitem or update an existing one
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            # update an item
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            # create an item
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerilizer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = ['quantity']


# FIXME: Working Test
class AddressSerializer(serializers.ModelSerializer):

    customer = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'postal',
                  'house_no', 'land_mark', 'phone_no', 'customer']

# FIXME: Testing


class AddAddressSerializer(serializers.ModelSerializer):

    customer = serializers.CharField(read_only=True)

    def create(self, validated_data):
        customer_id = self.context['customer_id']
        return Address.objects.create(customer_id=customer_id, **validated_data)

    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'postal',
                  'house_no', 'land_mark', 'phone_no', 'customer']


class UpdateAddressSerializer(serializers.ModelSerializer):

    customer = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'postal',
                  'house_no', 'land_mark', 'phone_no', 'customer']


class CustomerSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(read_only=True)
    # username=serializers.ReadOnlyField(read_only=True)
    address = AddressSerializer(read_only=True, many=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'username', 'first_name', 'last_name', 'email',
                  'phone', 'birth_date', 'membership', 'address', 'is_staff']


class OrderItemSerializer(serializers.ModelSerializer):

    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


# FIXME: 94 quries executing while send get
class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    payment = PaymentSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'total_price', 'items',
                  'is_delivered', 'is_shipped', 'is_cancelled', 'payment']


# FIXME: TODO :remove later
class UpdateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['is_delivered']

# FIXME: TODO : Not done


class CancelOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['is_cancelled']


# Create a custom serializer class for Add an order , beacause we need cart_id also while creating an order,
# cart_id is not the part of order model, and override the save method .
# From post method for create order fetch cart_id
# from request.user.id select customer of the order
# then create an order , after that  fetch cart items by using cart id
# create create order_items list, then create order_items in db by using create_bulk method.
# In any cause any step of this operation fails that leads to  db and app  in inconsistent state
# thats why we use transaction.

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    payment = PaymentSerializer()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('Cart does not exists')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cart is empty')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            # Get cart id from validated data; from client side
            cart_id = self.validated_data['cart_id']
            # Fetch customer using user_id from request ; set it in views
            customer = Customer.objects.get(
                user_id=self.context['user_id'])

            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)

            total_price = sum([(item.quantity * item.product.unit_price)
                               for item in cart_items])
            print('toatalprice', total_price)
            # Create an order
            order = Order.objects.create(
                customer=customer, total_price=total_price)

            # create payment child table
            payment = Payment.objects.create(
                order=order, **self.validated_data['payment'])

            # create order item list
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity

                ) for item in cart_items
            ]

            # create order items in db
            OrderItem.objects.bulk_create(order_items)
            # delete cart
            Cart.objects.filter(pk=cart_id).delete()

            # send signal
            order_created.send_robust(sender=self.__class__, order=order)

            return order
