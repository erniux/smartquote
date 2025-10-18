from django.core.management.base import BaseCommand
from services.api_clients import get_yfinance_prices, get_currency_rates
from services.models import MetalPrice, CurrencyRate
from django.utils import timezone


class Command(BaseCommand):
    help = "💰 Actualiza precios de metales y tasas de cambio usando Yahoo Finance"

    # Diccionario de unidades por símbolo
    UNIT_MAP = {
        "PVC": "toneladas",
        "GOLD": "onza troy",
        "SILVER": "onza troy",
        "COPPER": "libras",
        "ALUMINUM": "toneladas",
        "IRON": "toneladas",
        "LUMBER": "bd. ft.",
    }

    # Cantidades base por símbolo
    BASE_QTY_MAP = {
        "PVC": 1,
        "GOLD": 1,
        "SILVER": 1,
        "COPPER": 1,
        "ALUMINUM": 1,
        "IRON": 1,
        "LUMBER": 1,
    }

    def handle(self, *args, **options):
        self.stdout.write("⏳ Obteniendo precios de metales y commodities desde Yahoo Finance...")

        metals = get_yfinance_prices()
        self.stdout.write(str(metals))
        updated_symbols = []

        for name, value in metals.items():
            # Asignamos valores con fallback por defecto
            unidades = self.UNIT_MAP.get(name, "kg")
            cantidad = self.BASE_QTY_MAP.get(name, 1)

            MetalPrice.objects.update_or_create(
                symbol=name,
                defaults={
                    "name": name.title(),
                    "price_usd": value,
                    "last_updated": timezone.now(),
                    "measure_units": unidades,
                    "base_quantity": cantidad,
                },
            )
            updated_symbols.append(name)

        if updated_symbols:
            self.stdout.write(f"✅ Metales actualizados correctamente: {', '.join(updated_symbols)}")
        else:
            self.stdout.write("⚠️ No se encontraron metales para actualizar.")

        # ---------------------------------------------------------------------
        # TASAS DE CAMBIO
        # ---------------------------------------------------------------------
        self.stdout.write("\n⏳ Obteniendo tasas de cambio...")

        currencies = get_currency_rates()
        updated_currencies = []

        for name, value in currencies.items():
            try:
                base, target = name.split("/")
            except ValueError:
                self.stdout.write(f"⚠️ Formato inválido en par de divisas: {name}")
                continue

            CurrencyRate.objects.update_or_create(
                base_currency=base,
                target_currency=target,
                defaults={
                    "rate": value,
                    "last_updated": timezone.now(),
                },
            )
            updated_currencies.append(name)

        if updated_currencies:
            self.stdout.write(f"✅ Tasas de cambio actualizadas: {', '.join(updated_currencies)}")
        else:
            self.stdout.write("⚠️ No se encontraron tasas de cambio para actualizar.")

        self.stdout.write("\n🎯 Proceso completado exitosamente.")
