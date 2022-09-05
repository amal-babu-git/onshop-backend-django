from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# Custimmizing user model
class User(AbstractUser):
    email = models.EmailField(unique=True)

    