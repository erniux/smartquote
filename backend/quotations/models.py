from django.db import models
from django.utils import timezone
from decimal import Decimal
from core.models import Product
from services.models import MetalPrice, CurrencyRate


class Quotation(models.Model):
    customer_name = models.CharField("Cliente", max_length=100)
    customer_email = models.EmailField("Correo del cliente", blank=True, null=True)
    date = models.DateField("Fecha", default=timezone.now)
    currency = models.CharField("Moneda", max_length=10, default="MXN")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField("IVA (%)", max_digits=5, decimal_places=2, default=16)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField("Notas", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cotización #{self.id} - {self.customer_name}"

    def calculate_totals(self):
        subtotal = Decimal("0.00")
        exchange_rate = Decimal("1.00")

        # Obtener tasa de cambio si no es USD
        if self.currency != "USD":
            try:
                rate = CurrencyRate.objects.filter(
                    base_currency="USD",
                    target_currency=self.currency
                ).latest("last_updated")
                exchange_rate = rate.rate
            except CurrencyRate.DoesNotExist:
                print("⚠️ No hay tasa de cambio actualizada, usando 1.00")

        for item in self.items.all():
            product = item.product
            unit_price_usd = Decimal(product.price)

            # Si tiene metal_symbol, actualiza con precio real
            if product.metal_symbol:
                metal = MetalPrice.objects.filter(symbol=product.metal_symbol).order_by("-last_updated").first()
                if metal:
                    unit_price_usd = Decimal(metal.price_usd)

            # Convertir a moneda local
            unit_price_local = unit_price_usd * exchange_rate
            item.unit_price = unit_price_local
            item.save()

            subtotal += item.unit_price * item.quantity

        self.subtotal = subtotal
        self.total = subtotal + (subtotal * self.tax / Decimal("100"))
        self.save()


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"
