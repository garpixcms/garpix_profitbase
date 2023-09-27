from django.db import models
from solo.models import SingletonModel


class Config(SingletonModel):
    profitbase_update_interval = models.PositiveIntegerField(
        verbose_name='Частота обновления данных из ProfitBase (в минутах)', default=120)
    profitbase_delete_special_offers = models.BooleanField(
        verbose_name='Удалять из БД акции, которых нет в ПБ при обновлении', default=True)
    profitbase_delete_layout_plans = models.BooleanField(
        verbose_name='Удалять из БД планировки, которых нет в ПБ при обновлении', default=True)
    profitbase_delete_projects = models.BooleanField(
        verbose_name='Удалять из БД проекты, которых нет в ПБ при обновлении', default=False)
    profitbase_delete_houses = models.BooleanField(
        verbose_name='Удалять из БД дома, которых нет в ПБ при обновлении', default=False)
    profitbase_delete_properties = models.BooleanField(
        verbose_name='Удалять из БД помещения, которых нет в ПБ при обновлении', default=False)

    def __str__(self):
        return 'Настройки ProfitBase'

    class Meta:
        verbose_name = 'Настройки ProfitBase'
        verbose_name_plural = 'Настройки ProfitBase'
