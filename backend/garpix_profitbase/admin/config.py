from django.contrib import admin
from solo.admin import SingletonModelAdmin
from ..models.config import Config


@admin.register(Config)
class ConfigAdmin(SingletonModelAdmin):
    pass
