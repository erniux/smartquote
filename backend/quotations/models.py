from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from core.models import Product
from services.models import MetalPrice, CurrencyRate
from companies.models import Company

MONEY_FIELD = dict(max_digits=14, decimal_places=2, default=0)

class Quotation(models.Model):
    customer_name = models.CharField("Cliente", max_length=100)
    customer_email = models.EmailField("Correo del cliente", blank=True, null=True)
    date = models.DateField("Fecha", default=timezone.now)
    currency = models.CharField("Moneda", max_length=10, default="MXN")
    subtotal = models.DecimalField(**MONEY_FIELD)
    tax = models.DecimalField("IVA (%)", **MONEY_FIELD)
    total = models.DecimalField(**MONEY_FIELD)
    notes = models.TextField("Notas", blank=True, null=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations",
        verbose_name="Empresa emisora"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
    max_length=20,
    choices=[
        ("draft", "Borrador"),
        ("confirmed", "Confirmada"),
        ("cancelled", "Cancelada"),
    ],
    default="draft"
)


    def __str__(self):
        return f"Cotización #{self.id} - {self.customer_name}"

    from decimal import Decimal, ROUND_HALF_UP

    def calculate_totals(self):
        """
        Calcula el subtotal, impuestos y total general de la cotización.
        Incluye tanto productos (QuotationItem) como insumos/servicios (QuotationExpense).
        """

        # --- Subtotales individuales ---
        subtotal_items = Decimal("0.00")
        subtotal_expenses = Decimal("0.00")

        # 🧱 Productos principales
        for item in self.items.all():
            subtotal_items += Decimal(item.quantity) * Decimal(item.unit_price)

        # 🧰 Insumos y servicios asociados
        if hasattr(self, "expenses"):
            for exp in self.expenses.all():
                subtotal_expenses += Decimal(exp.total_cost or 0)

        # --- Subtotal general ---
        subtotal = subtotal_items + subtotal_expenses

        # --- Impuesto (IVA 16%) ---
        tax_rate = Decimal("0.16")
        tax = (subtotal * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # --- Total general ---
        total = (subtotal + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # --- Guardar en el modelo ---
        self.subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.tax = tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.total = total
        self.save(update_fields=["subtotal", "tax", "total"])

        return subtotal, tax, total


    def confirm(self):
        """Confirma la cotización y crea una venta asociada."""
        from sales.models import Sale
        if not hasattr(self, "sale"):
            sale = Sale.objects.create(
                quotation=self,
                total_amount=self.total,
            )
            sale.set_delivery_and_warranty()
            self.status = "confirmed"
            self.save()
            return sale
        return self.sale



class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(**MONEY_FIELD)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"



class QuotationExpense(models.Model):
    quotation = models.ForeignKey("Quotation", on_delete=models.CASCADE, related_name="expenses")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(**MONEY_FIELD)
    unit_cost = models.DecimalField(**MONEY_FIELD)
    total_cost = models.DecimalField(**MONEY_FIELD)

    CATEGORY_CHOICES = [
        ("material", "Material"),
        ("service", "Servicio"),
        ("labor", "Mano de obra"),
        ("other", "Otro"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category})"

