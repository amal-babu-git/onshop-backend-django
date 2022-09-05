
import uuid
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.core.validators import MinValueValidator

from store.validators import validate_file_size


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1),  # can provide custom message as second parameter
                    ])
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='store/images',
                              validators=[validate_file_size])


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]

    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True,  unique=True, editable=False,)

    phone = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)

    # connecting with user model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display(ordering='user__username')
    def username(self):
        return self.user.username

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    @admin.display(ordering='user__email')
    def email(self):
        return self.user.email

    @admin.display(ordering='user__is_staff')
    def is_staff(self):
        return self.user.is_staff

    def __str__(self) -> str:
        return (f'{self.user.first_name} {self.user.last_name}')

    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        permissions = [
            ('view_history', 'Can view history')
        ]


class Order(models.Model):

    placed_at = models.DateTimeField(auto_now_add=True)

    is_delivered = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    total_price = models.DecimalField(
        default=0.00, max_digits=10, decimal_places=2)

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        # Custom permission for cancel order
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=50, default=None)
    city = models.CharField(max_length=50, default=None)
    postal = models.PositiveBigIntegerField(default=None)
    house_no = models.PositiveSmallIntegerField(default=None)
    land_mark = models.CharField(max_length=50, default=None)
    phone_no = models.CharField(null=True, blank=True, max_length=12)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='address')


class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)])

    class Meta:
        # No duplicated records for the same product in the same cart
        # if user want multiple same product just increase the quantity.
        unique_together = [['cart', 'product']]


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

