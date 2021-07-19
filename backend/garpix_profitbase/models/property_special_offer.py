from django.db import models  # noqa
from django.conf import settings
from django.utils.module_loading import import_string

EmptyMixin = import_string(settings.EMPTY_MIXIN)


class PropertySpecialOffer(EmptyMixin, models.Model):
    is_active = models.BooleanField(default=False, verbose_name='Акция активна?')
    title = models.CharField(max_length=256, verbose_name='Название акции', blank=True, default='')
    profitbase_id = models.IntegerField(verbose_name='ID акции', blank=True, null=True)
    description = models.CharField(max_length=500, verbose_name='описание акции', blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала ивента')
    finish_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания ивента')
    discount = models.DecimalField(max_digits=3, decimal_places=1,
                                   verbose_name='Скидка', default=0.0)

    class Meta:
        verbose_name = 'Специальное предложение'
        verbose_name_plural = 'Специальные предложения'

    def __str__(self):
        return self.title
