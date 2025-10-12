from django.db import models
from quotations.models import Quotation
from datetime import timedelta, date

class Sale(models.Model):
    quotation = models.OneToOneField(
        Quotation,
        on_delete=models.CASCADE,
        related_name="sale",
        verbose_name="Cotización origen"
    )
    sale_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pendiente"),
            ("partially_paid", "Parcialmente pagada"),
            ("paid", "Pagada"),
            ("delivered", "Entregada"),
            ("closed", "Cerrada"),
        ],
        default="pending"
    )
    delivery_date = models.DateField(blank=True, null=True)
    warranty_end = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def set_delivery_and_warranty(self, delivery_days=7, warranty_days=90):
        """Calcula fechas estimadas de entrega y garantía."""
        self.delivery_date = date.today() + timedelta(days=delivery_days)
        self.warranty_end = date.today() + timedelta(days=warranty_days)
        self.save()

    def update_status(self):
        """Actualiza el estado según los pagos registrados."""
        total_paid = sum(p.amount for p in self.payments.all())
        if total_paid == 0:
            self.status = "pending"
        elif total_paid < self.total_amount:
            self.status = "partially_paid"
        elif total_paid >= self.total_amount:
            self.status = "paid"
        self.save()

    def __str__(self):
        return f"Venta #{self.id} - {self.quotation.customer_name}"


class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=50,
        choices=[
            ("transfer", "Transferencia"),
            ("cash", "Efectivo"),
            ("credit", "Crédito"),
        ],
        default="transfer"
    )

    def save(self, *args, **kwargs):
        """Guarda el pago y actualiza automáticamente el estado de la venta."""
        super().save(*args, **kwargs)
        self.sale.update_status()

    def __str__(self):
        return f"Pago de ${self.amount:,.2f} ({self.method})"
