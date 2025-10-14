from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from services.models import MetalPrice, CurrencyRate
from core.models import Product
from quotations.models import Quotation, QuotationItem, QuotationExpense


class QuotationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    metal_symbol = serializers.CharField(source="product.metal_symbol", read_only=True)

    class Meta:
        model = QuotationItem
        fields = ["id", "product", "product_name", "metal_symbol", "quantity", "unit_price"]
        read_only_fields = ["unit_price"]


class QuotationExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationExpense
        fields = ["id", "name", "description", "category", "quantity", "unit_cost", "total_cost"]


class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)
    expenses = QuotationExpenseSerializer(many=True, required=False)  # ✅ <--- ahora sí

    class Meta:
        model = Quotation
        fields = [
            "id",
            "customer_name",
            "customer_email",
            "currency",
            "date",
            "subtotal",
            "tax",
            "total",
            "notes",
            "items",
            "expenses",
        ]
        read_only_fields = ["subtotal", "total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        quotation = Quotation.objects.create(**validated_data)

        # 💱 Obtener tasa de cambio actual
        exchange_rate = Decimal("1.00")
        currency = quotation.currency or "USD"

        if currency != "USD":
            try:
                rate = CurrencyRate.objects.filter(
                    base_currency="USD", target_currency=currency
                ).latest("last_updated")
                exchange_rate = rate.rate
            except CurrencyRate.DoesNotExist:
                print(f"⚠️ No hay tasa USD/{currency}, usando 1.00")

        subtotal = Decimal("0.00")

        # 🧮 Calcular precios dinámicos de productos
        for item_data in items_data:
            product = item_data["product"]
            quantity = Decimal(item_data.get("quantity", 1))
            unit_price_usd = Decimal(product.price)

            if product.metal_symbol:
                metal = MetalPrice.objects.filter(
                    symbol=product.metal_symbol
                ).order_by("-last_updated").first()
                if metal:
                    unit_price_usd = Decimal(metal.price_usd)

            # Convertir el precio a moneda local (ej. MXN)
            unit_price_local = unit_price_usd * exchange_rate
            subtotal += unit_price_local * quantity

            QuotationItem.objects.create(
                quotation=quotation,
                product=product,
                quantity=quantity,
                unit_price=unit_price_local,
            )

        # 🧾 Agregar gastos adicionales (QuotationExpense)
        expenses_total = (
            QuotationExpense.objects.filter(quotation=quotation)
            .aggregate(total=Sum("total_cost"))
            .get("total")
            or Decimal("0.00")
        )

        subtotal += expenses_total

        # 🧾 Calcular subtotal + IVA + total
        quotation.subtotal = subtotal
        quotation.total = subtotal + (subtotal * quotation.tax / Decimal("100"))
        quotation.save()

        return quotation
