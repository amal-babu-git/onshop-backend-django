from django.conf import settings
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from core.models import User


# Customizing djoser serializer()authetication , it have only email, username and password
# But we need first_name and last_name too..
# refer--> https://djoser.readthedocs.io/en/latest/settings.html?highlight=serializers#serializers
# after the creating of customized serialize replace the default one by adding djoser dict in settings

class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):

        fields = ['id', 'username', 'email', 'password',
                  'email', 'first_name', 'last_name']


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', ]
