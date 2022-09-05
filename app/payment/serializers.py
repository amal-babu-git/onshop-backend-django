
from pyexpat import model
from store.models import Customer
from rest_framework import serializers
from store.models import Customer
from . import models


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id']



# this serializer also used inside store app
class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Payment
        fields = ['total_amount', 'transaction_id',
                  'username', 'payment_method', 'payment_status']


