import os
import json
import requests

from datetime import datetime

from django.conf import settings
from django.db import IntegrityError
from django.utils.timezone import make_aware
from django.utils.module_loading import import_string
from django.core.exceptions import MultipleObjectsReturned

from .models import Project, House, Property, HouseSection, PropertySpecialOffer, City, HouseFloor, LayoutPlan, Config


class ProfitBase:
    def __init__(self, init_projects=False, init_special_offers=False, pb_company_id=os.getenv('PROFITBASE_COMPANY_ID'),
                 api_key=os.getenv('PROFITBASE_API_KEY'),
                 client_name=os.getenv('PROFITBASE_CLIENT_NAME')):
        self.base_url = f'https://pb{pb_company_id}.profitbase.ru/api/v4/json'
        self.api_key = api_key
        self.token = None
        self.client_name = client_name
        self.default_header = {
            'Content-Type': 'application/json',
        }
        self.auth_body = {
            "type": "api-app",
            "credentials": {
                "pb_api_key": self.api_key,
            }
        }
        self.init_projects = init_projects
        self.init_special_offers = init_special_offers

    def update_base(self):
        self.authenticate()
        if self.init_projects:
            self.get_projects()
        self.get_houses()
        self.get_layout_plans()
        self.get_properties()
        if self.init_special_offers:
            self.get_special_offers()

    def create_booking(self, name, phone, email, property_id, comment):
        self.authenticate()
        self.send_booking_order(name, phone, email, property_id, comment)

    def send_booking_order(self, name, phone, email, property_id, comment):
        url = self.base_url + f'/orders?access_token={self.token}'
        data = {
            'order': {
                'name': name,
                'phone': phone,
                'email': email,
                'apartment': property_id,
                'comment': comment,
                'widget_id': 1,
            }
        }
        response = requests.post(url, headers=self.default_header, data=json.dumps(data))
        return response.status_code

    def authenticate(self):
        print('authenticating...')
        if self.token is None:
            url = self.base_url + '/authentication'
            response = requests.post(url, data=json.dumps(self.auth_body), headers=self.default_header)
            if response.status_code != 200:
                raise PermissionError(response.text)
            self.token = response.json()['access_token']

    def delete_non_existent_object(self, DbModel, pb_ids):
        try:
            if Config.get_solo().profitbase_delete_data:
                db_elements = DbModel.objects.all()
                for elem in db_elements:
                    if elem.profitbase_id not in pb_ids:
                        elem.delete()
        except Exception as e:
            print(e)

    def get_projects(self):
        print('getting projects...')
        url = self.base_url + f'/projects?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for item in response.json():
            if not isinstance(item, dict):
                break
            project = Project.objects.filter(profitbase_id=item['id']).first()
            try:
                city = City.objects.get_or_create(title=item['locality'])[0]
                data = {
                    'title': item['title'],
                    'name': item['title'],
                    'city': city,
                }
                if project is None:
                    Project.objects.create(
                        profitbase_id=item['id'],
                        **data,
                    )
            except (MultipleObjectsReturned, IntegrityError):
                print("Элемент проекта не создан\n", data, "\n")
            else:
                Project.objects.filter(profitbase_id=item['id']).update(**data)

    def get_houses(self):
        print('getting houses...')
        url = self.base_url + f'/house?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for item in response.json()['data']:
            if not isinstance(item, dict):
                break
            self.delete_non_existent_object(House, [item['id'] for item in response.json()['data']])
            house = House.objects.filter(profitbase_id=item['id']).first()
            data = {
                'name': item['title'],
                'title': item['title'],
                'material': item.get('material')
            }
            try:
                if house is None:
                    House.objects.create(
                        profitbase_id=item['id'],
                        **data,
                    )
                else:
                    House.objects.filter(profitbase_id=item['id']).update(**data)
            except (MultipleObjectsReturned, IntegrityError):
                print("Элемент дома не создан\n", data, "\n")

    def get_properties(self):  # noqa
        print('getting properties...')
        offset = 0
        limit = 100
        properties_in_db = Property.objects.all()
        houses_in_db = House.objects.all()

        property_fields = get_model_fields_list(Property)
        pb_ids = []
        while True:
            url = f'{self.base_url}/property?access_token={self.token}&offset={offset}&limit={limit}&full=true'
            response = requests.get(url, headers=self.default_header)
            if 'data' not in response.json().keys():
                break
            else:
                if len(response.json()['data']) == 0:
                    break

            offset += 100
            limit += 100
            pb_ids.extend([item['id'] for item in response.json()['data']])
            for item in response.json()['data']:

                if not isinstance(item, dict):
                    break

                house = list(
                    filter(lambda house: house.profitbase_id == item['house_id'], houses_in_db))

                if len(house) > 0:
                    house_title = house[0].name
                    house = house[0]
                else:
                    house_title = 'Помещение'
                    house = None

                area = get_areas(item)

                section = HouseSection.objects.get_or_create(house=house,
                                                             number=item['sectionName'],
                                                             )[0]
                floor = HouseFloor.objects.get_or_create(house=house,
                                                         section=section,
                                                         number=item['floor'],
                                                         )[0]
                attributes = item['attributes']
                custom_fields = get_custom_fields(item)
                data = {
                    'number': item['number'],
                    'rooms': item['rooms_amount'],
                    'studio': item['studio'],
                    'free_layout': item['free_layout'],
                    'euro_layout': item['euro_layout'],
                    'has_related_preset_with_layout':
                        item['has_related_preset_with_layout'] if item[
                                                                      'has_related_preset_with_layout'] is not None else False,
                    'facing': attributes['facing'] if attributes['facing'] is not None and attributes[
                        'facing'] != '' else 'Нет',
                    'combined_bathroom_count': attributes['combined_bathroom_count'] if attributes[
                                                                                            'combined_bathroom_count'] is not None else 0,  # noqa
                    'separated_bathroom_count': attributes['separated_bathroom_count'] if attributes[
                                                                                              'separated_bathroom_count'] is not None else 0,  # noqa
                    'code': attributes['code'],
                    'description': attributes['description'],
                    'bti_number': attributes['bti_number'],
                    'bti_area': attributes['bti_area'],
                    'area_total': area['area_total'],
                    'area_estimated': area['area_estimated'],
                    'area_living': area['area_living'],
                    'area_kitchen': area['area_kitchen'],
                    'area_balcony': area['area_balcony'],
                    'area_without_balcony': area['area_without_balcony'],
                    'price': item['price']['value']
                    if item['price']['value'] is not None else 0,

                    'price_per_meter': item['price']['pricePerMeter']
                    if item['price']['pricePerMeter'] is not None else 0,

                    'status': item['status'],
                    'title': house_title,
                    'section': section,
                    'floor': floor,
                    'self_house': house,
                }

                data.update(set_model_custom_fields(property_fields, custom_fields))

                fields_to_update = []

                try:
                    db_instance = list(
                        filter(lambda instance: instance.profitbase_id == item['id'], properties_in_db))
                    if len(db_instance) > 0:
                        db_instance = db_instance[0]
                        for attr, value in data.items():
                            if getattr(db_instance, attr) != value:
                                setattr(db_instance, attr, value)
                                fields_to_update.append(attr)
                        if len(fields_to_update) > 0:
                            db_instance.save(update_fields=fields_to_update)

                    else:
                        db_instance = Property.objects.create(profitbase_id=item['id'], **data)
                except Exception as e:
                    print(e)
        self.delete_non_existent_object(Property, pb_ids)

    def get_layout_plans(self):  # noqa

        print('getting layout plans...')

        url = f'{self.base_url}/plan?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)

        if 'data' not in response.json().keys():
            print("NO LAYOUTS DATA")
            return

        layout_data = response.json()['data']
        self.delete_non_existent_object(LayoutPlan, [item['id'] for item in response.json()['data']])
        properties_update = []

        layouts_in_db = LayoutPlan.objects.all()
        houses_in_db = House.objects.all()

        properties_in_db = Property.objects.all()

        for layout in layout_data:

            if not isinstance(layout, dict):
                break
            house = list(
                filter(lambda house: house.profitbase_id == layout['houseId'], houses_in_db))

            if len(house) > 0:
                house = house[0]
            else:
                house = None

            data = {
                "rooms": layout['roomsAmount'],
                "area_total": layout['areaRange']['min'],
                "price": layout['priceRange']['min'],
                "name": layout['code'],
                "self_house": house
            }

            fields_to_update = []

            db_instance = list(
                filter(lambda instance: instance.profitbase_id == layout['id'], layouts_in_db))
            try:
                if len(db_instance) > 0:
                    db_instance = db_instance[0]
                    for attr, value in data.items():
                        if getattr(db_instance, attr) != value:
                            setattr(db_instance, attr, value)
                            fields_to_update.append(attr)

                    if len(fields_to_update) > 0:
                        db_instance.save()

                else:
                    db_instance = LayoutPlan.objects.create(profitbase_id=layout['id'], **data)

                properties = list(
                    filter(lambda property: str(property.profitbase_id) in layout['properties'], properties_in_db))

                if len(properties) > 0:
                    for property in properties:
                        if property.layout_plan != db_instance:
                            property.layout_plan = db_instance
                        properties_update.append(property)
            except Exception as e:
                print(e)

        Property.objects.bulk_update(properties_update, ['layout_plan'])

    def get_special_offers(self):
        print('getting special offers...')
        url = self.base_url + f'/special-offer?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        special_offers_in_db = PropertySpecialOffer.objects.all()

        self.delete_non_existent_object(PropertySpecialOffer, [item['id'] for item in response.json()])

        def data_datetime(str_time: str):
            new_time: datetime = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f')
            return make_aware(new_time)

        for param in response.json():
            if not isinstance(param, dict):
                break
            data = {
                'title': param['name'],
                'description': param['description'],
                'start_date': data_datetime(param['startDate']['date']),
                'finish_date': data_datetime(param['finishDate']['date']),
                'discount': param['discount']['value'],
                'discount_type': param['discount'].get('type', None),
                'discount_unit': param['discount'].get('unit', None),
                'is_active': param['discount'].get('active', False),
            }

            try:
                db_instance = list(
                    filter(lambda instance: instance.profitbase_id == param['id'], special_offers_in_db))
                if len(db_instance) > 0:
                    db_instance = db_instance[0]
                    for attr, value in data.items():
                        setattr(db_instance, attr, value)
                else:
                    db_instance = PropertySpecialOffer(profitbase_id=param['id'], **data)
                db_instance.save()

                property_ids = param['propertyIds']
                properties = Property.objects.filter(profitbase_id__in=property_ids)
                db_instance.properties.set(properties, clear=True)
                db_instance.save()

                if (hasattr(settings, 'GARPIX_PROFITBASE_RECALCULATE_NEW_PRICE')
                        and settings.GARPIX_PROFITBASE_RECALCULATE_NEW_PRICE is not None):
                    recalculate_new_price = import_string(settings.GARPIX_PROFITBASE_RECALCULATE_NEW_PRICE)
                    if recalculate_new_price:
                        # Отправялем на перерасчет ценники квартир, участвующие в акции
                        recalculate_new_price(properties)

                        # Дополнительная проверка, остались ли в БД квартиры с акцией
                        need_recalculate_remove = (
                            Property.objects.filter(special_offer=db_instance).exclude(id__in=properties)
                        )

                        if need_recalculate_remove.exists():
                            for element_remove in need_recalculate_remove:
                                element_remove.special_offer.remove(db_instance)
                                element_remove.save()

                            recalculate_new_price(need_recalculate_remove)

            except (MultipleObjectsReturned, IntegrityError):
                print("Элемент спецпредложения не создан\n", data, "\n")

    def get_houses_without_relationships(self):
        print('getting houses...')
        url = self.base_url + f'/house?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for item in response.json()['data']:
            try:
                if not isinstance(item, dict):
                    break
                house = House.objects.filter(profitbase_id=item['id']).first()
                data = {
                    'name': item['title'],
                    'title': item['title'],
                }
                if house is None:
                    House.objects.create(
                        profitbase_id=item['id'],
                        **data,
                    )
                else:
                    House.objects.filter(profitbase_id=item['id']).update(**data)
            except (MultipleObjectsReturned, IntegrityError):
                print("Элемент дома не создан\n", data, "\n")

    def get_properties_without_relationships(self):  # noqa
        print('getting properties...')
        offset = 0
        limit = 1000
        propertiy_fields = get_model_fields_list(Property)
        while True:
            url = f'{self.base_url}/property?access_token={self.token}&offset={offset}&limit={limit}&full=true'
            response = requests.get(url, headers=self.default_header)

            if 'data' not in response.json().keys():
                break
            else:
                if len(response.json()['data']) == 0:
                    break

            offset += 1000
            limit += 1000

            for item in response.json()['data']:
                if not isinstance(item, dict):
                    break
                property = Property.objects.filter(profitbase_id=item['id']).first()
                house = House.objects.filter(profitbase_id=item['house_id']).first()
                area = get_areas(item)
                attributes = item['planImages']
                custom_fields = get_custom_fields(item)
                data = {
                    'number': item['number'],
                    'rooms': item['rooms_amount'],
                    'studio': item['studio'],
                    'free_layout': item['free_layout'],
                    'euro_layout': item['euro_layout'],
                    'has_related_preset_with_layout':
                        item['has_related_preset_with_layout'] if item[
                                                                      'has_related_preset_with_layout'] is not None else False,
                    # noqa
                    'facing': attributes['facing'] if attributes['facing'] is not None else 'Нет',
                    'combined_bathroom_count':
                        attributes['combined_bathroom_count'] if attributes[
                                                                     'combined_bathroom_count'] is not None else 0,
                    # noqa
                    'separated_bathroom_count':
                        attributes['separated_bathroom_count'] if attributes[
                                                                      'separated_bathroom_count'] is not None else 0,
                    # noqa
                    'code': attributes['code'],
                    'description': attributes['description'],
                    'bti_number': attributes['bti_number'],
                    'bti_area': attributes['bti_area'],
                    'area_total': area['area_total'],
                    'area_estimated': area['area_estimated'],
                    'area_living': area['area_living'],
                    'area_kitchen': area['area_kitchen'],
                    'area_balcony': area['area_balcony'],
                    'area_without_balcony': area['area_without_balcony'],
                    'price': item['price']['value']
                    if item['price']['value'] is not None else 0,

                    'price_per_meter': item['price']['pricePerMeter']
                    if item['price']['pricePerMeter'] is not None else 0,

                    'status': item['status'],
                }

                for field_key, field_value in custom_fields:
                    if field_key in propertiy_fields.keys():
                        data.update({propertiy_fields[field_key]: field_value})
                data.update({'title': house.name if house.name else 'Помещение'})

                try:
                    if property is None:
                        Property.objects.create(
                            profitbase_id=item['id'],
                            **data,
                        )
                    else:
                        Property.objects.filter(profitbase_id=item['id']).update(**data)
                except (MultipleObjectsReturned, IntegrityError):
                    print("Элемент помещения не создан\n", data, "\n")


def get_areas(item):
    area = {
        'area_total': item['area']['area_total'],
        'area_estimated': item['area']['area_estimated'],
        'area_living': item['area']['area_living'],
        'area_kitchen': item['area']['area_kitchen'],
        'area_balcony': item['area']['area_balcony'],
        'area_without_balcony': item['area']['area_without_balcony'],
    }
    for key, value in area.items():
        if value is None:
            area[key] = 0.0
        else:
            area[key] = float(value)
    return area


def get_custom_fields(item):
    custom_fields = {}
    for field in item['custom_fields']:
        custom_fields.update({field['name']: field['value']})
    return custom_fields


def get_model_fields_list(Model):
    prop_fields = {}
    for f in Model._meta.get_fields():
        if hasattr(f, 'verbose_name'):
            prop_fields.update({f.verbose_name: {'name': f.name, 'field': f}})
    return prop_fields


def set_model_custom_fields(model_fields, custom_fields):
    from django.db.models import FloatField, BooleanField
    data = {}
    for custom_field_key, field_value in custom_fields.items():
        if custom_field_key in model_fields.keys():
            model_field_name = model_fields[custom_field_key]['name']
            if field_value is not None:
                if isinstance(model_fields[custom_field_key]['field'], FloatField):
                    field_value = float(field_value.replace(',', '.'))
                elif isinstance(model_fields[custom_field_key]['field'], BooleanField):
                    if field_value == 'Нет' or field_value == 'нет':
                        field_value = False
                    elif field_value == 'Да' or field_value == 'да':
                        field_value = True
                data.update({model_field_name: field_value})

    return data


def property_standart_fields():
    return ['number', 'rooms', "studio", "free_layout", "euro_layout",
            "has_related_preset_with_layout", "facing", "area_total",
            "area_estimated",
            "area_living", "area_kitchen", "area_balcony",
            "area_without_balcony",
            "price", "price_per_meter", "status",
            "title", "section", "floor", "self_house",
            "combined_bathroom_count", "separated_bathroom_count", "code",
            "description", "bti_number", "bti_area"]
