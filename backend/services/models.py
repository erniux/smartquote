from django.db import models
from django.utils import timezone

class MetalPrice(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=20)
    price_usd = models.DecimalField(max_digits=12, decimal_places=4)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.symbol}) - {self.price_usd} USD"


class CurrencyRate(models.Model):
    base_currency = models.CharField(max_length=10, default="USD")
    target_currency = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.target_currency}"
