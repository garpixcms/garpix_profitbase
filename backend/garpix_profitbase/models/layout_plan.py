from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string

LayoutPlanMixin = import_string(settings.GARPIX_PROFITBASE_LAYOUT_PLAN_MIXIN)


class LayoutPlan(LayoutPlanMixin, models.Model):
    profitbase_id = models.IntegerField(blank=True, null=True, verbose_name='ProfitBase ID')
    name = models.CharField(max_length=256, verbose_name='Название планировки', blank=True, default='LayoutPlanName')
    is_active = models.BooleanField(default=True, verbose_name='Планировка активна?')
    rooms = models.IntegerField(verbose_name='Количество комнат', blank=True, default=1)
    area_total = models.FloatField(verbose_name='Суммарная площадь', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=4,
                                verbose_name='Цена', blank=True, null=True)

    self_house = models.ForeignKey('House', on_delete=models.SET_NULL, verbose_name='Дом', related_name='layout_plan',
                                   blank=True, null=True)


    class Meta:
        verbose_name = 'Планировка'
        verbose_name_plural = 'Планировки'

