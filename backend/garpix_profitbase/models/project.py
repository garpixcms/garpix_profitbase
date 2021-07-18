from django.db import models
from .city import City


class Project(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    profitbase_id = models.IntegerField(verbose_name='ProfitBase ID')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('title',)
