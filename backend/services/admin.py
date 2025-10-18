from django.contrib import admin
from .models import MetalPrice, CurrencyRate


@admin.register(MetalPrice)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price_usd', 'last_updated', 'measure_units', 'base_quantity')
    search_fields = ('name', 'symbol')


