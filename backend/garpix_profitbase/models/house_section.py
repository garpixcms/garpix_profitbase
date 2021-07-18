from django.db import models


class HouseSection(models.Model):
    title = models.CharField(max_length=256, verbose_name='Номер подъезда', blank=True, default='')
    house = models.ForeignKey('House', verbose_name='Дом', related_name='section', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Подьезд'
        verbose_name_plural = 'Подьезды'

    def __str__(self):
        return str(self.title)
