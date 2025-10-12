from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "margin", "unit", "metal_symbol", "created_at")
    search_fields = ("name", "description", "metal_symbol")
    list_filter = ("unit", "metal_symbol")

