from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Customer

# This function works using django signals.
# After creating this function , this file shoud import app config- inside ready method


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    """"
    This function automatically create customer when new user signup(register)
    Args ,
    sender : sender app 
    **kwargs : contain the instance,created..
    """
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])
    
