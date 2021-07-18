from django.db import models
from .house import House


class Property(models.Model):
    profitbase_id = models.IntegerField(verbose_name='ProfitBase ID')
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name='Дом')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    number = models.CharField(max_length=256, verbose_name='Номер помещения', blank=True, default='')
    rooms_amount = models.IntegerField(verbose_name='Количество комнат', default=0)
    section = models.CharField(max_length=256, verbose_name='Имя номера подъезда', blank=True, default='')
    floor = models.ForeignKey('HouseFloor', verbose_name='Этаж на шахматке',
                              related_name='property_floor', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.profitbase_id)

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'
        ordering = ('title',)
