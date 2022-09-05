
from .import views
from rest_framework import routers

router=routers.DefaultRouter()
# Braintree
router.register('braintree', views.PaymentBApiViewSet, basename='braintree')
#razorpay
router.register('razorpay', views.PaymentRApiViewSet, basename='razorpay')


# urlpatterns = [
#     path('gettoken/', view=views.PaymentApiView.as_view(), name='token-generate'),
#     # path('process/', view=views.process_payment, name='payment-process'),
#     # path('process/', views.PaymentAPIView.as_view()),
# ]

urlpatterns = router.urls
