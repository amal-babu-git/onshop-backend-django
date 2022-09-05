from django.db import models
from store.models import Order
# Create your models here.


class Payment(models.Model):

    PAYMENT_METHOD_PAY_ON_DELIVERY = 'OFF'
    PAYMENT_METHOD_PAY_ONLINE = 'ON'

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_PAY_ON_DELIVERY, 'Pay on delivery'),
        (PAYMENT_METHOD_PAY_ONLINE, 'Online payment'),
    ]

    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
    ]

    total_amount = models.DecimalField(default=None,
                                       max_digits=10,
                                       decimal_places=2)
    payment_method = models.CharField(
        max_length=3, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_PAY_ON_DELIVERY)

    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)

    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    customer_id = models.CharField(
        max_length=255, default='Not required for pay on delivary')

    username = models.CharField(
        max_length=255, default=None, null=True, blank=True)

    created_at=models.DateTimeField(auto_now=True)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='payment')
