import time
from django.core.management.base import BaseCommand
from ...profitbase import ProfitBase


class Command(BaseCommand):
    help = 'Get profitbase data'

    def handle(self, *args, **kwargs):
        while True:
            print('start get profitbase data')
            start_time = time.time()
            pb = ProfitBase()
            pb.update_base()
            print('end get profitbase data')
            print('wait 20 minutes until the next iteration')
            print(f'it takes a {time.time() - start_time} sec')
            time.sleep(1200)
