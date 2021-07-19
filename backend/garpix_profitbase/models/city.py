from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string

EmptyMixin = import_string(settings.EMPTY_MIXIN)


class City(EmptyMixin, models.Model):
    title = models.CharField(max_length=100, verbose_name='Название города')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ('title',)
