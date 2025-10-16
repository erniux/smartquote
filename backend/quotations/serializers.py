from rest_framework import serializers
from decimal import Decimal
from django.db.models import Sum
from services.models import MetalPrice, CurrencyRate
from core.models import Product
from quotations.models import Quotation, QuotationItem, QuotationExpense


# ============================================================
# 🧱 QuotationItemSerializer (acepta payload plano)
# ============================================================
class QuotationItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(source="product.name", required=False, allow_blank=True)
    metal_symbol = serializers.CharField(source="product.metal_symbol", required=False, allow_blank=True)
    price = serializers.DecimalField(source="product.price", required=False, max_digits=14, decimal_places=2)
    quantity = serializers.DecimalField(required=True, max_digits=14, decimal_places=2)
    unit_price = serializers.DecimalField(required=False, max_digits=14, decimal_places=2)

    class Meta:
        model = QuotationItem
        fields = ["id", "name", "metal_symbol", "price", "quantity", "unit_price"]


# ============================================================
# 🧾 QuotationExpenseSerializer
# ============================================================
class QuotationExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationExpense
        fields = ["id", "name", "description", "category", "quantity", "unit_cost", "total_cost"]


# ============================================================
# 💰 QuotationSerializer
# ============================================================
class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)
    expenses = QuotationExpenseSerializer(many=True, required=False)

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
            "status",
        ]
        read_only_fields = []

    # ============================================================
    # CREATE
    # ============================================================
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        expenses_data = validated_data.pop("expenses", [])
        quotation = Quotation.objects.create(**validated_data)

        for item_data in items_data:
            product_id = item_data.get("id")
            product_instance = Product.objects.filter(id=product_id).first()
            if not product_instance:
                continue

            QuotationItem.objects.create(
                quotation=quotation,
                product=product_instance,
                quantity=item_data.get("quantity", 1),
                unit_price=item_data.get("unit_price", item_data.get("price", 0)),
            )

        for exp_data in expenses_data:
            QuotationExpense.objects.create(
                quotation=quotation,
                name=exp_data.get("name", ""),
                description=exp_data.get("description", ""),
                category=exp_data.get("category", "other"),
                quantity=Decimal(exp_data.get("quantity", 1)),
                unit_cost=Decimal(exp_data.get("unit_cost", 0)),
                total_cost=Decimal(exp_data.get("total_cost", 0)),
            )

        return quotation

    # ============================================================
    # UPDATE (agregar, modificar y borrar items/expenses)
    # ============================================================
    def update(self, instance, validated_data):
        items_data = self.initial_data.get("items", [])
        expenses_data = self.initial_data.get("expenses", [])

        # 🔁 Actualizar campos principales de la cotización
        for field in ["customer_name", "customer_email", "currency", "notes", "subtotal", "tax", "total", "status"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()

        # ========== ITEMS ==========
        existing_items = {item.id: item for item in instance.items.all()}
        sent_item_ids = []

        for item_data in items_data:
            item_id = item_data.get("id")
            product_instance = Product.objects.filter(id=item_data.get("id")).first()
            if not product_instance:
                continue

            if item_id and item_id in existing_items:
                # 🔄 actualizar item existente
                item = existing_items[item_id]
                item.product = product_instance
                item.quantity = Decimal(item_data.get("quantity", 1))
                item.unit_price = Decimal(item_data.get("unit_price", item_data.get("price", 0)))
                item.save()
                sent_item_ids.append(item_id)
            else:
                # ➕ crear nuevo item
                new_item = QuotationItem.objects.create(
                    quotation=instance,
                    product=product_instance,
                    quantity=Decimal(item_data.get("quantity", 1)),
                    unit_price=Decimal(item_data.get("unit_price", item_data.get("price", 0))),
                )
                sent_item_ids.append(new_item.id)

        # ❌ eliminar los items que no vienen en el payload
        for item_id, item in existing_items.items():
            if item_id not in sent_item_ids:
                item.delete()

        # ========== EXPENSES ==========
        existing_expenses = {exp.id: exp for exp in instance.expenses.all()}
        sent_expense_ids = []

        for exp_data in expenses_data:
            exp_id = exp_data.get("id")
            if exp_id and exp_id in existing_expenses:
                # 🔄 actualizar gasto existente
                exp = existing_expenses[exp_id]
                exp.name = exp_data.get("name", exp.name)
                exp.description = exp_data.get("description", exp.description)
                exp.category = exp_data.get("category", exp.category)
                exp.quantity = Decimal(exp_data.get("quantity", exp.quantity))
                exp.unit_cost = Decimal(exp_data.get("unit_cost", exp.unit_cost))
                exp.total_cost = Decimal(exp_data.get("total_cost", exp.total_cost))
                exp.save()
                sent_expense_ids.append(exp_id)
            else:
                # ➕ crear nuevo gasto
                new_exp = QuotationExpense.objects.create(
                    quotation=instance,
                    name=exp_data.get("name", ""),
                    description=exp_data.get("description", ""),
                    category=exp_data.get("category", "other"),
                    quantity=Decimal(exp_data.get("quantity", 1)),
                    unit_cost=Decimal(exp_data.get("unit_cost", 0)),
                    total_cost=Decimal(exp_data.get("total_cost", 0)),
                )
                sent_expense_ids.append(new_exp.id)

        # ❌ eliminar los gastos que no vienen en el payload
        for exp_id, exp in existing_expenses.items():
            if exp_id not in sent_expense_ids:
                exp.delete()

        instance.save()
        return instance
