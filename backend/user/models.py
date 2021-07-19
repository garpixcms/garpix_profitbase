from django.db import models  # noqa
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # noqa
from garpix_notify.mixins import UserNotifyMixin


class User(AbstractUser, UserNotifyMixin):
    pass

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
