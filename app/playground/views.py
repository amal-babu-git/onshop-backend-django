import django
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import mail_admins, EmailMessage, BadHeaderError
# from store.models import Product, Order, OrderItem
from django.contrib.contenttypes.models import ContentType
import requests
from playground.tasks import notify_customers
from store.models import Collection, Product
from tags.models import TaggedItem
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView





def send_email(request):

    try:

        message = EmailMessage('subject', 'message', 'onshop.online.in@gmail.com',
                               ['amalbabu1200@gmail.com'])
        message.attach_file('playground/static/images/d4.jpg')
        message.send()

    except BadHeaderError:
        print('error')



    return render(request, 'hello.html', {'Email': 'onshop'})

# chache


class HelloView(APIView):
    # this decorator will take care of chaching data from requests.get()
    # timeout 5*60 , i.e " 5 minutes"
    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        response = requests.get('http://httpbin.org/delay/2')
        data = response.json()
        return render(request, 'hello.html', {'name': data})


def say_hello(req):
    notify_customers.delay('Hello')
    return render(req, 'hello.html', {'name': 'Amal'})


def insert_update_example(request):
    # insering data
    collection = Collection()
    collection.title = "Video game"
    collection.featured_product = None
    collection.save()
    # another methode is Collection.objects.create(title="video Game",..)

    # updating data
    collection = Collection.objects.get(pk=15)
    collection.featured_product = None
    collection.save()
    # another methode is Collection.objects.filter(pk=1).update(title="video Game",..)

    return render(request, 'hello.html', {'name': 'Amal'})


# def say_hello(request):
#     # ContentType id of  product model
#     queryset=TaggedItem.objects.get_tags_for(Product,1)

#     return render(request, 'hello.html', {'tags': list(queryset)})


# def say_hello(request):

#     products = Product.objects.filter(
#         id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

#     # orederItem = OrderItem.objects.values('product_id').distinct()

#     return render(request, 'hello.html', {'products': list(products)})
