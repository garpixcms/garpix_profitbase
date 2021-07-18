from django.contrib import admin
from ..models.city import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass
