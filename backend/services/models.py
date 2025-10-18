from django.db import models
from django.utils import timezone

class MetalPrice(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=20)
    price_usd = models.DecimalField(max_digits=12, decimal_places=4)
    measure_units = models.CharField(max_length=20, default="")
    base_quantity = models.DecimalField(max_digits=12, decimal_places=4, default=0)
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


# LBR -> 1.000 bd. ft. Un pie tablar es una unidad de volumen estándar en la industria de la madera
# PVC -> 1 tonelada métrica = 1,000 kg
# ALM -> 1 tonelada métrica = 1,000 kg
# IRON -> 1 tonelada métrica = 1,000 kg
# COPPER -> 1 libra = 0.453592 kg
# GOLD -> 1 onza troy = 31.1035 gramos
# SILVER -> 1 onza troy = 31.1035 gramos    