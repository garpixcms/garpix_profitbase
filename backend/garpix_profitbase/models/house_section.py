from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string

HouseSectionMixin = import_string(settings.GARPIX_PROFITBASE_HOUSE_SECTION_MIXIN)


class HouseSection(HouseSectionMixin, models.Model):
    number = models.CharField(max_length=256, verbose_name='Номер подъезда', blank=True, default='')
    house = models.ForeignKey('House', verbose_name='Дом', related_name='section', on_delete=models.CASCADE,
                              null=True, blank=True)

    class Meta:
        verbose_name = 'Подьезд'
        verbose_name_plural = 'Подьезды'

    def __str__(self):
        return str(self.number)
