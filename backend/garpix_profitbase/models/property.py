from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string

PropertyMixin = import_string(settings.GARPIX_PROFITBASE_PROPERTY_MIXIN)


class Property(PropertyMixin, models.Model):
    profitbase_id = models.IntegerField(verbose_name='ProfitBase ID')
    layout_plan = models.ForeignKey('LayoutPlan', on_delete=models.SET_NULL, verbose_name='Планировка',
                                    related_name='property', blank=True, null=True)
    self_house = models.ForeignKey('House', on_delete=models.CASCADE, verbose_name='Дом', related_name='property',
                                   blank=True, null=True)
    number = models.CharField(max_length=256, verbose_name='Номер помещения', blank=True, default='')
    rooms = models.IntegerField(verbose_name='Количество комнат', blank=True, default=1)
    studio = models.BooleanField(default=False, verbose_name='Студия')
    free_layout = models.BooleanField(default=False, verbose_name='Свободная планировка')
    euro_layout = models.BooleanField(default=False, verbose_name='Европланировка')
    has_related_preset_with_layout = models.BooleanField(default=False,
                                                         verbose_name='Имеет связанную предустановку с макетом')
    facing = models.CharField(max_length=350, verbose_name='Отделка', blank=True, null=True)
    area_total = models.FloatField(verbose_name='Суммарная площадь', blank=True, null=True)
    area_estimated = models.FloatField(verbose_name='Оценочная площадь', blank=True, null=True)
    area_living = models.FloatField(verbose_name='Жилая площадь', blank=True, null=True)
    area_kitchen = models.FloatField(verbose_name='Площадь кухни', blank=True, null=True)
    area_balcony = models.FloatField(verbose_name='Площадь балкона/ов', blank=True, null=True)
    area_without_balcony = models.FloatField(verbose_name='Площадь за вычетом балконов', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2,
                                verbose_name='Цена', blank=True, null=True)
    price_per_meter = models.DecimalField(max_digits=12, decimal_places=2,
                                          verbose_name='Цена за метр', blank=True, null=True)
    status = models.CharField(max_length=350, verbose_name='Статус', blank=True, null=True)

    section = models.ForeignKey('HouseSection', verbose_name='Секция',
                                related_name='property', on_delete=models.CASCADE,
                                blank=True, null=True)
    floor = models.ForeignKey('HouseFloor', verbose_name='Этаж на шахматке',
                              related_name='property', on_delete=models.CASCADE,
                              blank=True, null=True)
    special_offer = models.ForeignKey('PropertySpecialOffer', on_delete=models.CASCADE,
                                      blank=True, null=True, related_name='property')

    def __str__(self):
        return str(self.profitbase_id)

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'
        ordering = ('number',)
