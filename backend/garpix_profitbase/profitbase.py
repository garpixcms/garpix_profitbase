import django.core.exceptions
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from .models import Project, House, Property, HouseSection, PropertySpecialOffer, City, HouseFloor, LayoutPlan
from django.core.files.images import ImageFile
import os
import requests
import json
from io import BytesIO


class ProfitBase(object):
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
            house = House.objects.filter(profitbase_id=item['id']).first()
            data = {
                'name': item['title'],
                'title': item['title'],
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

    def get_properties(self):
        print('getting properties...')
        offset = 0
        limit = 1000
        properties_in_db = Property.objects.all()
        houses_in_db = House.objects.all()

        properties_create = []
        properties_update = []
        while True:
            url = f'{self.base_url}/property?access_token={self.token}&offset={offset}&limit={limit}&full=false'
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

                data = {
                    'number': item['number'],
                    'rooms': item['rooms_amount'],
                    'studio': item['studio'],
                    'free_layout': item['free_layout'],
                    'euro_layout': item['euro_layout'],
                    'has_related_preset_with_layout': item['has_related_preset_with_layout'],
                    'facing': item['facing'] if item['facing'] is not None else '',
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
                    'self_house': house
                }

                db_instance = list(
                    filter(lambda instance: instance.profitbase_id == item['id'], properties_in_db))
                if len(db_instance) > 0:
                    db_instance = db_instance[0]
                    for attr, value in data.items():
                        setattr(db_instance, attr, value)

                    properties_update.append(db_instance)
                else:
                    db_instance = Property.objects.create(profitbase_id=item['id'], **data)

        Property.objects.bulk_update(properties_update, ['number', 'rooms', "studio", "free_layout", "euro_layout",
                                                         "has_related_preset_with_layout", "facing", "area_total", "area_estimated",
                                                         "area_living", "area_kitchen", "area_balcony", "area_without_balcony",
                                                         "price", "price_per_meter", "status",
                                                         "title", "section", "floor", "self_house"])

    def get_layout_plans(self):

        print('getting layout plans...')

        url = f'{self.base_url}/plan?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)

        if 'data' not in response.json().keys():
            print("NO LAYOUTS DATA")
            return

        layout_data = response.json()['data']

        layouts_create = []
        layouts_update = []
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

            db_instance = list(
                filter(lambda instance: instance.profitbase_id == layout['id'], layouts_in_db))
            if len(db_instance) > 0:
                db_instance = db_instance[0]
                for attr, value in data.items():
                    setattr(db_instance, attr, value)

                layouts_update.append(db_instance)
            else:
                db_instance = LayoutPlan(profitbase_id=layout['id'], **data)
                layouts_create.append(db_instance)

            properties = list(
                filter(lambda property: str(property.profitbase_id) in layout['properties'], properties_in_db))

            if len(properties) > 0:
                for property in properties:
                    if property.layout_plan != db_instance:
                        property.layout_plan = db_instance
                    properties_update.append(property)

        LayoutPlan.objects.bulk_create(layouts_create)
        LayoutPlan.objects.bulk_update(layouts_update, ['rooms', 'area_total', "price", "name", "self_house"])
        Property.objects.bulk_update(properties_update, ['layout_plan'])

    def get_special_offers(self):
        print('getting special offers...')
        url = self.base_url + f'/special-offer?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for param in response.json():
            if not isinstance(param, dict):
                break
            data = {
                'title': param['name'],
                'description': param['description'],
                'start_date': param['startDate']['date'],
                'finish_date': param['finishDate']['date'],
                'discount': param['discount']['value'] if param['discount']['value'] > 0 else 0.,
            }
            try:
                offer = PropertySpecialOffer.objects.filter(profitbase_id=param['id']).first()

                if offer is None:
                    offer = PropertySpecialOffer.objects.create(
                        profitbase_id=param['id'],
                        **data
                    )
                else:
                    PropertySpecialOffer.objects.filter(profitbase_id=param['id']).update(**data)

                property_ids = param['propertyIds']
                properties = Property.objects.filter(profitbase_id__in=property_ids)
                for property in properties:
                    property.special_offer = offer
                    property.save()
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

    def get_properties_without_relationships(self):
        print('getting properties...')
        offset = 0
        limit = 1000
        while True:
            url = f'{self.base_url}/property?access_token={self.token}&offset={offset}&limit={limit}&full=false'
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
                data = {
                    'number': item['number'],
                    'rooms': item['rooms_amount'],
                    'studio': item['studio'],
                    'free_layout': item['free_layout'],
                    'euro_layout': item['euro_layout'],
                    'has_related_preset_with_layout': item['has_related_preset_with_layout'],
                    'facing': item['facing'] if item['facing'] is not None else '',
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
