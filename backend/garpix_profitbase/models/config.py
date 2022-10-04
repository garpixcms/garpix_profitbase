from django.db import models
from solo.models import SingletonModel


class Config(SingletonModel):
    profitbase_update_interval = models.PositiveIntegerField(
        verbose_name='Частота обновления данных из ProfitBase (в минутах)', default=120)
    profitbase_delete_data = models.BooleanField(
        verbose_name='Удалять из БД данные, которых нет в ПБ при обновлении', default=True)

    def __str__(self):
        return 'Настройки ProfitBase'

    class Meta:
        verbose_name = 'Настройки ProfitBase'
        verbose_name_plural = 'Настройки ProfitBase'
