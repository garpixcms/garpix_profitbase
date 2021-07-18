from django.db import models
from .project import Project


class House(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Проект')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Дом'
        verbose_name_plural = 'Дома'
        ordering = ('title',)
