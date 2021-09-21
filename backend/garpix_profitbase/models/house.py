from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string
from .project import Project

HouseMixin = import_string(settings.GARPIX_PROFITBASE_HOUSE_MIXIN)


class House(HouseMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    profitbase_id = models.IntegerField(verbose_name='ProfitBase ID', blank=True, null=True)
    self_project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                     verbose_name='Проект', related_name='house',
                                     blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Дом'
        verbose_name_plural = 'Дома'
        ordering = ('title',)
