from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from services.models import MetalPrice, CurrencyRate
from core.models import Product
from quotations.models import Quotation, QuotationItem, QuotationExpense


# 🧩 Serializer anidado para producto
class NestedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "metal_symbol", "price"]


class QuotationItemSerializer(serializers.ModelSerializer):
    product = NestedProductSerializer()
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

    # =====================================================
    # 🟢 CREATE: crea cotización con items y expenses anidados
    # =====================================================
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        expenses_data = validated_data.pop("expenses", [])
        quotation = Quotation.objects.create(**validated_data)

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

        # 🧮 Crear items
        for item_data in items_data:
            product_instance = item_data.get("product")

            # ✅ Soporta ID o dict
            if isinstance(product_instance, dict):
                product_id = product_instance.get("id")
                product_instance = Product.objects.filter(id=product_id).first()
            elif isinstance(product_instance, int):
                product_instance = Product.objects.filter(id=product_instance).first()

            if not product_instance:
                print("⚠️ Producto no encontrado, se omite item.")
                continue

            quantity = Decimal(item_data.get("quantity", 1))

            # --- Precio ---
            unit_price_usd = Decimal(product_instance.price or 0)
            if getattr(product_instance, "metal_symbol", None):
                metal = (
                    MetalPrice.objects.filter(symbol=product_instance.metal_symbol)
                    .order_by("-last_updated")
                    .first()
                )
                if metal:
                    base_price = Decimal(metal.price_usd or 0)
                    margin = Decimal(getattr(product_instance, "margin", 0))
                    unit_price_usd = base_price * (Decimal("1.00") + (margin / Decimal("100")))

            unit_price_local = (unit_price_usd * exchange_rate).quantize(Decimal("0.01"))
            subtotal += (unit_price_local * quantity).quantize(Decimal("0.01"))

            QuotationItem.objects.create(
                quotation=quotation,
                product=product_instance,
                quantity=quantity,
                unit_price=unit_price_local.quantize(Decimal("0.01")),
            )

        # 🧾 Crear expenses
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

        # Totales
        tax_rate = Decimal("0.16")
        tax = (subtotal * tax_rate).quantize(Decimal("0.01"))
        total = (subtotal + tax).quantize(Decimal("0.01"))

        quotation.subtotal = subtotal
        quotation.tax = tax
        quotation.total = total
        quotation.save(update_fields=["subtotal", "tax", "total"])

        return quotation

    # =====================================================
    # 🟡 UPDATE: actualiza campos, items y expenses
    # =====================================================
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", [])
        expenses_data = validated_data.pop("expenses", [])

        # 1️⃣ Actualizar campos básicos
        instance.customer_name = validated_data.get("customer_name", instance.customer_name)
        instance.customer_email = validated_data.get("customer_email", instance.customer_email)
        instance.currency = validated_data.get("currency", instance.currency)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.status = validated_data.get("status", instance.status)
        instance.save()

        # 2️⃣ Items existentes en BD
        existing_items = {item.id: item for item in instance.items.all()}

        # 3️⃣ Recorrer items enviados en el payload
        seen_item_ids = set()
        for item_data in items_data:
            item_id = item_data.get("id")
            product_data = item_data.get("product")

            # Buscar o crear product
            if isinstance(product_data, dict):
                product_id = product_data.get("id")
                product_instance = Product.objects.filter(id=product_id).first()
            elif isinstance(product_data, int):
                product_instance = Product.objects.filter(id=product_data).first()
            else:
                product_instance = None

            if not product_instance:
                continue

            quantity = Decimal(item_data.get("quantity", 1))
            unit_price = item_data.get("unit_price")

            if item_id and item_id in existing_items:
                # 🧩 Actualizar item existente
                item = existing_items[item_id]
                item.product = product_instance
                item.quantity = quantity
                if unit_price:
                    item.unit_price = Decimal(unit_price)
                item.save()
                seen_item_ids.add(item_id)
            else:
                # ➕ Crear nuevo item
                QuotationItem.objects.create(
                    quotation=instance,
                    product=product_instance,
                    quantity=quantity,
                    unit_price=Decimal(unit_price or product_instance.price or 0),
                )

        # 4️⃣ Eliminar items que no vienen en el payload
        for item_id, item in existing_items.items():
            if item_id not in seen_item_ids:
                item.delete()

        # 5️⃣ Expenses existentes
        existing_expenses = {exp.id: exp for exp in instance.expenses.all()}
        seen_expense_ids = set()

        for exp_data in expenses_data:
            exp_id = exp_data.get("id")
            quantity = Decimal(exp_data.get("quantity", 1))
            unit_cost = Decimal(exp_data.get("unit_cost", 0))
            total_cost = quantity * unit_cost

            if exp_id and exp_id in existing_expenses:
                exp = existing_expenses[exp_id]
                exp.name = exp_data.get("name", exp.name)
                exp.description = exp_data.get("description", exp.description)
                exp.category = exp_data.get("category", exp.category)
                exp.quantity = quantity
                exp.unit_cost = unit_cost
                exp.total_cost = total_cost
                exp.save()
                seen_expense_ids.add(exp_id)
            else:
                # ➕ Crear nuevo gasto
                QuotationExpense.objects.create(
                    quotation=instance,
                    name=exp_data.get("name", ""),
                    description=exp_data.get("description", ""),
                    category=exp_data.get("category", "other"),
                    quantity=quantity,
                    unit_cost=unit_cost,
                    total_cost=total_cost,
                )

        # Eliminar gastos no incluidos
        for exp_id, exp in existing_expenses.items():
            if exp_id not in seen_expense_ids:
                exp.delete()

        # 6️⃣ Recalcular totales
        subtotal_items = instance.items.aggregate(total=Sum("unit_price"))["total"] or Decimal("0.00")
        subtotal_expenses = instance.expenses.aggregate(total=Sum("total_cost"))["total"] or Decimal("0.00")
        subtotal = subtotal_items + subtotal_expenses
        tax = (subtotal * Decimal("0.16")).quantize(Decimal("0.01"))
        total = (subtotal + tax).quantize(Decimal("0.01"))

        instance.subtotal = subtotal
        instance.tax = tax
        instance.total = total
        instance.save(update_fields=["subtotal", "tax", "total"])

        return instance

    # =====================================================
    # 🔵 CAMPOS COMPUTADOS
    # =====================================================
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
