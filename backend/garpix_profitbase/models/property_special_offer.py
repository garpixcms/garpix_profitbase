from django.db import models  # noqa
from django.conf import settings
from django.utils.module_loading import import_string

SpecialOfferMixin = import_string(settings.GARPIX_PROFITBASE_SPECIAL_OFFER_MIXIN)


class PropertySpecialOffer(SpecialOfferMixin, models.Model):
    class TYPE:
        FULL_PRICE = 'FULL_PRICE'
        METER_PRICE = 'METER_PRICE'
        CHOICES = (
            (FULL_PRICE, 'Скидка на общую стоимость'),
            (METER_PRICE, 'Скидка на 1 кв.м. помещения')
        )

    class UNIT:
        PERCENT = 'PERCENT'
        VALUE = 'VALUE'
        CHOICES = (
            (PERCENT, '%'),
            (VALUE, 'руб.')
        )
    is_active = models.BooleanField(default=False, verbose_name='Акция активна?')
    title = models.CharField(max_length=256, verbose_name='Название акции', blank=True, default='')
    profitbase_id = models.IntegerField(verbose_name='ID акции', blank=True, null=True)
    description = models.TextField(verbose_name='Описание акции', blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала ивента')
    finish_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания ивента')
    discount = models.DecimalField(max_digits=10, decimal_places=1,
                                   verbose_name='Скидка', default=0.0)
    discount_type = models.CharField(choices=TYPE.CHOICES, default=TYPE.FULL_PRICE, max_length=50)
    discount_unit = models.CharField(choices=UNIT.CHOICES, default=UNIT.PERCENT, max_length=50)

    class Meta:
        verbose_name = 'Специальное предложение'
        verbose_name_plural = 'Специальные предложения'

    def __str__(self):
        return self.title
