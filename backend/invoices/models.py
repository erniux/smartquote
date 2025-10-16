from django.db import models
from sales.models import Sale
from django.utils import timezone

class Invoice(models.Model):
    sale = models.OneToOneField("sales.Sale",
        on_delete=models.CASCADE,
        related_name="invoice", 
        verbose_name="Venta asociada",)
    invoice_number = models.CharField(max_length=20, unique=True)
    issue_date = models.DateField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    pdf_file = models.FileField(upload_to="invoices/pdfs/", blank=True, null=True)


    @staticmethod
    def next_invoice_number():
        """Genera el siguiente número de factura consecutivo."""
        last = Invoice.objects.order_by("-id").first()
        if not last:
            return "INV-0001"
        last_num = int(last.invoice_number.split("-")[1])
        return f"INV-{last_num+1:04d}"
    
    def __str__(self):
        return f"Factura {self.invoice_number} - {self.sale.quotation.customer_name}"

