from celery import shared_task
from core.models import Product

@shared_task
def update_dynamic_prices():
    for product in Product.objects.exclude(dynamic_price_source__isnull=True):
        product.update_dynamic_price()
