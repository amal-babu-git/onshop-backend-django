from django_filters.rest_framework import FilterSet
from .models import Product

# ref-->https://django-filter.readthedocs.io/

# Filtering product based on collection , unit_price with range
# By using django-filter library


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id': ['exact'],
            'unit_price': ['gt', 'lt']
        }
