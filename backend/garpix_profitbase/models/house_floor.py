from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string

HouseFloorMixin = import_string(settings.GARPIX_PROFITBASE_HOUSE_FLOOR_MIXIN)


class HouseFloor(HouseFloorMixin, models.Model):
    number = models.IntegerField(verbose_name='Номер Этажа', blank=True, default=1)
    section = models.ForeignKey('HouseSection', verbose_name='Секция',
                                related_name='floor', on_delete=models.CASCADE)
    house = models.ForeignKey('House', verbose_name='Дом', related_name='floor', on_delete=models.CASCADE,
                              blank=True, null=True)

    class Meta:
        verbose_name = 'Этаж'
        verbose_name_plural = 'Этажи'

    def __str__(self):
        return str(self.number)
