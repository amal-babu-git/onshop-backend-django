# Generated by Django 4.1 on 2022-08-19 07:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_remove_order_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
