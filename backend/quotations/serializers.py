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
    expenses = QuotationExpenseSerializer(many=True, required=False)
    has_sale = serializers.SerializerMethodField()
    sale = serializers.SerializerMethodField()

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
            "has_sale",
            "sale",
            "status",
        ]
        read_only_fields = ["subtotal", "total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        expenses_data = validated_data.pop("expenses", [])
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

        # 🧮 Crear los productos (QuotationItem)
        for item_data in items_data:
            product_instance = item_data.get("product")
            if isinstance(product_instance, int):  # Si viene como ID
                try:
                    product_instance = Product.objects.get(id=product_instance)
                except Product.DoesNotExist:
                    print(f"⚠️ Producto con ID {product_instance} no encontrado.")
                    continue

            quantity = Decimal(item_data.get("quantity", 1))

            # --- 🪙 Buscar precio del metal actual ---
            unit_price_usd = Decimal(product_instance.price or 0)
            if getattr(product_instance, "metal_symbol", None):
                metal = (
                    MetalPrice.objects.filter(symbol=product_instance.metal_symbol)
                    .order_by("-last_updated")
                    .first()
                )
                if metal:
                    # 💰 Calcular precio con margen de ganancia
                    base_price = Decimal(metal.price_usd or 0)
                    margin = Decimal(product_instance.margin or 0)
                    unit_price_usd = base_price * (Decimal("1.00") + (margin / Decimal("100")))
                else:
                    print(f"⚠️ No se encontró precio de metal para {product_instance.metal_symbol}")

            # --- Convertir a moneda local ---
            unit_price_local = (unit_price_usd * exchange_rate).quantize(Decimal("0.01"))
            subtotal += (unit_price_local * quantity).quantize(Decimal("0.01"))


            QuotationItem.objects.create(
                quotation=quotation,
                product=product_instance,
                quantity=quantity,
                unit_price=unit_price_local.quantize(Decimal("0.01")),
            )

        # 🧾 Crear los gastos adicionales (QuotationExpense)
        for exp_data in expenses_data:
            quantity = Decimal(exp_data.get("quantity", 1))
            unit_cost = Decimal(exp_data.get("unit_cost", 0))
            total_cost = quantity * unit_cost

            QuotationExpense.objects.create(
                quotation=quotation,
                name=exp_data.get("name", ""),
                description=exp_data.get("description", ""),
                category=exp_data.get("category", "other"),
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=total_cost,
            )

            subtotal += total_cost

        # 🧾 Calcular subtotal + IVA + total
        tax_rate = Decimal("0.16")
        tax = (subtotal * tax_rate).quantize(Decimal("0.01"))
        total = (subtotal + tax).quantize(Decimal("0.01"))

        quotation.subtotal = subtotal.quantize(Decimal("0.01"))
        quotation.tax = tax
        quotation.total = total
        quotation.save(update_fields=["subtotal", "tax", "total"])

        return quotation
    
    def update(self, instance, validated_data):
        # Actualiza solo campos básicos
        instance.customer_name = validated_data.get("customer_name", instance.customer_name)
        instance.customer_email = validated_data.get("customer_email", instance.customer_email)
        instance.currency = validated_data.get("currency", instance.currency)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.save(update_fields=["customer_name", "customer_email", "currency", "notes"])
        return instance

    
    def get_has_sale(self, obj):
        return hasattr(obj, "sale")

    def get_sale(self, obj):
        sale = getattr(obj, "sale", None)
        if sale:
            return {
                "id": sale.id,
                "status": sale.status,
                "total_amount": str(sale.total_amount),
            }
        return None

