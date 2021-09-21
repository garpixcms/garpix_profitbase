from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string
from .city import City

ProjectMixin = import_string(settings.GARPIX_PROFITBASE_PROJECT_MIXIN)


class Project(ProjectMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    profitbase_id = models.IntegerField(verbose_name='ProfitBase ID', blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город', related_name='project')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ('title',)
