from django.core.management.base import BaseCommand
from services.api_clients import get_yfinance_prices, get_currency_rates
from services.models import MetalPrice, CurrencyRate
from django.utils import timezone

class Command(BaseCommand):
    help = "Actualiza precios de metales y divisas usando Yahoo Finance"

    def handle(self, *args, **options):
        self.stdout.write("⏳ Obteniendo precios de metales y commodities desde Yahoo Finance...")
        metals = get_yfinance_prices()
        for name, value in metals.items():
            MetalPrice.objects.update_or_create(
                symbol=name,
                defaults={
                    "name": name.title(),
                    "price_usd": value,
                    "last_updated": timezone.now()
                },
            )
        self.stdout.write(f"✅ Metales actualizados: {', '.join(metals.keys())}")

        self.stdout.write("⏳ Obteniendo tasas de cambio...")
        currencies = get_currency_rates()
        for name, value in currencies.items():
            base, target = name.split("/")
            CurrencyRate.objects.update_or_create(
                base_currency=base,
                target_currency=target,
                defaults={
                    "rate": value,
                    "last_updated": timezone.now()
                },
            )
        self.stdout.write(f"✅ Tasas actualizadas: {', '.join(currencies.keys())}")
