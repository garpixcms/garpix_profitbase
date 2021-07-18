from .models import Project, House, Property, HouseSection, PropertySpecialOffer, City
import os
import requests
import json
from transliterate import translit
from django.contrib.sites.models import Site
import uuid


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
        self.limit = 1000

    def update_base(self):
        self.authenticate()
        self.get_projects()
        self.get_houses()
        # self.get_properties()
        # self.get_special_offers()

    # def create_booking(self, data):
    #     self.authenticate()
    #     self.send_booking_order(data)
    #
    # def send_booking_order(self, data):
    #     url = self.base_url + f'/orders?access_token={self.token}'
    #     response = requests.post(url, headers=self.default_header, data=json.dumps(data))
    #     return response.status_code
    #
    def authenticate(self):
        print('authenticating...')
        url = self.base_url + '/authentication'
        response = requests.post(url, data=json.dumps(self.auth_body), headers=self.default_header)
        self.token = response.json()['access_token']

    def get_projects(self):
        print('getting projects...')
        url = self.base_url + f'/projects?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for item in response.json():
            project = Project.objects.filter(profitbase_id=item['id']).first()
            city = City.objects.get_or_create(title=item['locality'])
            data = {
                'title': item['title'],
                'city': city,
            }
            if project is None:
                # create
                Project.objects.create(
                    profitbase_id=item['id'],
                    **data,
                )
            else:
                # update
                Project.objects.filter(profitbase_id=item['id']).update(**data)

    def get_houses(self):
        print('getting houses...')
        url = self.base_url + f'/house?access_token={self.token}'
        response = requests.get(url, headers=self.default_header)
        for item in response.json()['data']:
            house = House.objects.filter(profitbase_id=item['id']).first()
            project = Project.objects.filter(profitbase_id=item['projectId']).first()
            data = {
                'project': project,
                'title': item['title'],
            }
            if house is None:
                # create
                House.objects.create(
                    profitbase_id=item['id'],
                    **data,
                )
            else:
                # update
                House.objects.filter(profitbase_id=item['id']).update(**data)

    def get_properties(self):
        print('getting properties...')
        offset = 0
        while True:
            url = f'{self.base_url}/property?access_token={self.token}&offset={offset}&limit={self.limit}&full=false'
            response = requests.get(url, headers=self.default_header)

            if len(response.json()['data']) == 0:
                break

            offset += 1000

            for item in response.json()['data']:
                property = Property.objects.filter(profitbase_id=item['id']).first()
                house = House.objects.filter(profitbase_id=item['house_id']).first()

                area_total_decimal = float(item['area']['area_total']) if item['area']['area_total'] is not None else 0
                area_kitchen_decimal = float(item['area']['area_kitchen']) if item['area']['area_kitchen'] is not None else 0

                section = HouseSection.objects.get_or_create(house=house, title=item['sectionName'])
                # floor = HouseFloor.objects.filter(section=section, title=item['floor'], property=self)

                # if floor is None:
                #     floor = HouseFloor(section=section, number=param['floor'])
                #     floor.save()
                #     self.floor = floor
                #     self.save()

                data = {
                    'house': house,
                    'title': item['title'],
                    'number': item['number'],
                    'rooms_amount': item['rooms_amount'],
                    'section': item['sectionName'],
                #     'floor': param['floor'], # !!!
                # self.is_studio = param['studio']
                # self.is_free_layout = param['free_layout']
                # self.is_euro_layout = param['euro_layout']
                # self.has_related_preset_with_layout = param['has_related_preset_with_layout']
                # self.facing = param['facing']
                # self.area_total = param['area']['area_total']
                # if param['area']['area_total'] is not None:
                #     self.area_total_decimal = float(param['area']['area_total'])
                # self.area_estimated = param['area']['area_estimated']
                # self.area_living = param['area']['area_living']
                # self.area_kitchen = param['area']['area_kitchen']
                # if param['area']['area_kitchen'] is not None:
                #     self.area_kitchen_decimal = float(param['area']['area_kitchen'])
                # self.area_balcony = param['area']['area_balcony']
                # self.area_without_balcony = param['area']['area_without_balcony']
                # self.price = param['price']['value']
                # self.price_per_meter = param['price']['pricePerMeter']
                # self.status = param['status']
                }

                if property is None:
                    # create
                    Property.objects.create(
                        profitbase_id=item['id'],
                        **data,
                    )
                else:
                    # update
                    Property.objects.filter(profitbase_id=item['id']).update(**data)

    #
    # def get_special_offers(self):
    #     print('getting special offers...')
    #     url = self.base_url + f'/special-offer?access_token={self.token}'
    #     response = requests.get(url, headers=self.default_header)
    #     for param in response.json():
    #         offer = PropertySpecialOffer.objects.filter(
    #             offer_id=param['id']
    #         ).first()
    #         if not offer:
    #             print('creating offer...')
    #             offer = PropertySpecialOffer().set_self_data(param=param)
    #         else:
    #             print('updating offer...')
    #             offer.set_self_data(param=param)
