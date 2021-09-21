from .models import Project, House, Property, HouseSection, PropertySpecialOffer, City, HouseFloor, LayoutPlan
import os
import requests
import json


class ProfitBase(object):
    def __init__(self, pb_company_id=os.getenv('PROFITBASE_COMPANY_ID'), api_key=os.getenv('PROFITBASE_API_KEY'),
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

    def update_base(self):
        self.authenticate()
        self.get_projects()
        self.get_houses()
        self.get_properties()
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
            self.token = response.json()['access_token']

    def get_projects(self):
        print('getting projects...')
        url = self.base_url + f'/projects?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for item in response.json():
            if not isinstance(item, dict):
                break
            project = Project.objects.filter(profitbase_id=item['id']).first()
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
            project = Project.objects.get_or_create(profitbase_id=item['projectId'])[0]
            data = {
                'self_project': project,
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

    def get_properties(self):
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

                if property is None:
                    Property.objects.create(
                        profitbase_id=item['id'],
                        self_house=house,
                        **data,
                    )
                    section = HouseSection.objects.get_or_create(house=house,
                                                                 number=item['sectionName'],
                                                                 )[0]
                    floor = HouseFloor.objects.get_or_create(house=house,
                                                             section=section,
                                                             number=item['floor'],
                                                             )[0]
                    property_data = {
                        'section': section,
                        'floor': floor
                    }
                    Property.objects.filter(
                        profitbase_id=item['id']).update(**property_data)
                else:
                    Property.objects.filter(profitbase_id=item['id']).update(**data)
                    section = HouseSection.objects.get_or_create(house=house,
                                                                 number=item['sectionName'],
                                                                 )[0]
                    floor = HouseFloor.objects.get_or_create(house=house,
                                                             section=section,
                                                             number=item['floor'],
                                                             )[0]
                    property_data = {
                        'section': section,
                        'floor': floor
                    }
                    Property.objects.filter(
                        profitbase_id=item['id']).update(**property_data)

    def get_properties_with_layout_plan(self):
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

                if property is None:
                    Property.objects.create(
                        profitbase_id=item['id'],
                        self_house=house,
                        **data,
                    )
                    section = HouseSection.objects.get_or_create(house=house,
                                                                 number=item['sectionName'],
                                                                 )[0]
                    floor = HouseFloor.objects.get_or_create(house=house,
                                                             section=section,
                                                             number=item['floor'],
                                                             )[0]
                    layout_plan = LayoutPlan.objects.get_or_create(
                        rooms=item['rooms_amount'],
                        area_total=area['area_total'],
                        price=item['price']['value'],
                        self_house=house,
                        floor=floor,
                    )[0]
                    property_data = {
                        'section': section,
                        'floor': floor,
                        'layout_plan': layout_plan
                    }
                    Property.objects.filter(
                        profitbase_id=item['id']).update(**property_data)
                else:
                    Property.objects.filter(profitbase_id=item['id']).update(**data)
                    section = HouseSection.objects.get_or_create(house=house,
                                                                 number=item['sectionName'],
                                                                 )[0]
                    floor = HouseFloor.objects.get_or_create(house=house,
                                                             section=section,
                                                             number=item['floor'],
                                                             )[0]
                    layout_plan = LayoutPlan.objects.get_or_create(
                        rooms=item['rooms_amount'],
                        area_total=area['area_total'],
                        price=item['price']['value'],
                        self_house=house,
                        floor=floor,
                    )[0]
                    property_data = {
                        'section': section,
                        'floor': floor,
                        'layout_plan': layout_plan
                    }
                    Property.objects.filter(
                        profitbase_id=item['id']).update(**property_data)

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
                'discount': param['discount']['value'],
            }

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

    def get_houses_without_relationships(self):
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
            if house is None:
                House.objects.create(
                    profitbase_id=item['id'],
                    **data,
                )
            else:
                House.objects.filter(profitbase_id=item['id']).update(**data)

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

                if property is None:
                    Property.objects.create(
                        profitbase_id=item['id'],
                        **data,
                    )
                else:
                    Property.objects.filter(profitbase_id=item['id']).update(**data)


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
