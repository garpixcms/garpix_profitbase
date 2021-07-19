from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string
from .project import Project

PageMixin = import_string(settings.PAGE_MIXIN)


class House(PageMixin, models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    profitbase_id = models.IntegerField(verbose_name='ProfitBase ID', blank=True, null=True)
    self_project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Проект')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Дом'
        verbose_name_plural = 'Дома'
        ordering = ('title',)
