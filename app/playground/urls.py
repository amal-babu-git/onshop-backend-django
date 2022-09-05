from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('hello/', views.say_hello),
    path('email/', views.send_email),
    path('ch_test/', views.HelloView.as_view())

]

