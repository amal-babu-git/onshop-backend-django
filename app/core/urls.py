from django.views.generic import TemplateView
from django.urls import path




# Cutomized jwt auth with simple jwt TODO: Experimental
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import MyTokenObtainPairView

urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html')),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/',TokenRefreshView.as_view(), name='token_refresh'),
]
