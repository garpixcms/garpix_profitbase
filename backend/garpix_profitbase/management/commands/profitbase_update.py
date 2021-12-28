import time
from django.core.management.base import BaseCommand
from ...profitbase import ProfitBase


class Command(BaseCommand):
    help = 'Get profitbase data'

    def add_arguments(self, parser):
        parser.add_argument('--init-projects',
                            action='store_true',
                            help='Опция для подгрузки данных проектов')
        parser.add_argument('--init-special-offers',
                            action='store_true',
                            help='Опция для подгрузки спецпредложений')
        
    def handle(self, *args, **kwargs):
        while True:
            print('start get profitbase data')
            start_time = time.time()
            pb = ProfitBase(init_projects=kwargs['init_projects'], 
                            init_special_offers=kwargs['init_special_offers'])
            pb.update_base()
            print('end get profitbase data')
            print('wait 20 minutes until the next iteration')
            print(f'it takes a {time.time() - start_time} sec')
            time.sleep(1200)

