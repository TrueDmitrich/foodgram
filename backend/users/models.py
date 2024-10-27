from django.contrib.auth.models import AbstractUser
from django.db import models

# Наверное убрать
class AuthUser(AbstractUser):
    # дописать
    """Дополнение ."""

    avatar = models.ImageField(upload_to='media/users', blank=True)

    class Meta:
        abstract = True

