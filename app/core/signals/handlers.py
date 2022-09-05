from django.dispatch import receiver
from store.signals import order_created


@receiver(order_created)
def on_order_created(sender, **kwargs):
    # when an order is placed, this app will get a signal 
    # do anything with that
    print(kwargs['order'])
