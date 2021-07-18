from django.db import models  # noqa
from .property import Property


class PropertySpecialOffer(models.Model):
    title = models.CharField(max_length=256, verbose_name='Название акции', blank=True, default='')
    # offer_id = models.IntegerField(verbose_name='ID акции', blank=True, null=True)
    # archive = models.BooleanField(default=False, verbose_name='в архиве?')
    # color = models.CharField(max_length=50, verbose_name='Цвет акции', blank=True, null=True)
    # description = models.CharField(max_length=500, verbose_name='описание акции', blank=True, null=True)
    # description_active = models.BooleanField(default=False, verbose_name='Активное описание?')
    # start_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата начала ивента')
    # close_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания ивента')
    # badge_icon = models.CharField(max_length=50, verbose_name='Иконка значка', blank=True, null=True)
    # badge_label = models.CharField(max_length=50, verbose_name='Текст значка', blank=True, null=True)
    # banner_text = models.CharField(max_length=350, verbose_name='Текст на баннере', blank=True, null=True)
    # banner_is_active = models.BooleanField(default=False, verbose_name='Активное описание?')
    # banner_text_button = models.CharField(max_length=350, verbose_name='Текст на кнопке баннера',
    #                                       blank=True, null=True)
    # discount = models.DecimalField(max_digits=3, decimal_places=1,
    #                                verbose_name='Скидка', default=0.0)
    # discount_is_active = models.BooleanField(default=False, verbose_name='Скидка активна?')

    class Meta:
        verbose_name = 'Специальное предложение'
        verbose_name_plural = 'Специальные предложения'

    def __str__(self):
        return self.title

    # def set_self_data(self, param):
    #     # data = {k: v for k, v in param.items() if v is not None}
    #     # if data['id']:
    #     self.offer_id = param['id']
    #     # if data['name']:
    #     self.name = param['name']
    #     # if data['archive']:
    #     self.archive = param['archive']
    #     # if data['color']:
    #     self.color = param['color']
    #     # if data['badgeTextColor']:
    #     self.badge_color = param['badgeTextColor']
    #     # if data['description']:
    #     self.description = param['description']
    #     # if data['descriptionActive']:
    #     self.description_active = param['descriptionActive']
    #     # if data['startDate']:
    #     self.start_date = param['startDate']['date']
    #     # if data['finishDate']:
    #     self.close_date = param['finishDate']['date']
    #     # if data['badge']:
    #     self.badge_icon = param['badge']['icon']
    #     self.badge_label = param['badge']['label']
    #     # if data['banner']:
    #     self.banner_is_active = param['banner']['active']
    #     self.banner_text = param['banner']['text']
    #     self.banner_text_button = param['banner']['buttonText']
    #     # if data['discount']:
    #     self.discount = param['discount']['value']
    #     self.discount_is_active = param['discount']['active']
    #     # if data['propertyIds']:
    #     for property in param['propertyIds']:
    #         apartment = Property.objects.filter(
    #             profitbase_id=property
    #         ).first()
    #         if not apartment:
    #             apartment = Property(
    #                 profitbase_id=property,
    #                 special_offers=self,
    #             )
    #
    #         else:
    #             apartment.special_offers = self
    #
    #     print('done')
    #     self.save()
