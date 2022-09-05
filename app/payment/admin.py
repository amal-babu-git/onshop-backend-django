from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['username', 'total_amount', 'payment_method',
                    'payment_status', 'transaction_id', 'created_at']
    search_fields = ['username', 'total_amount',
                     'transaction_id', 'customer_id']
