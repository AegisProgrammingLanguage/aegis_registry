import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from .managers import UserManager


class User(AbstractUser):
    objects = UserManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class GroupProxy(Group):
    class Meta:
        proxy = True
        app_label = 'authentication'
        verbose_name = Group._meta.verbose_name
        verbose_name_plural = Group._meta.verbose_name_plural
        