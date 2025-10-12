from django.contrib import admin, messages
from django.core.files.base import ContentFile
from .models import Sale, Payment 
from invoices.models import Invoice
from datetime import date
from decimal import Decimal
from quotations.pdf_utils import generate_quotation_pdf
from invoices.email_utils import send_invoice_email
from invoices.pdf_utils import generate_invoice_pdf  

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ["payment_date"]
    can_delete = False

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quotation",
        "total_amount",
        "status",
        "sale_date",
        "delivery_date",
        "warranty_end",
    )
    list_filter = ("status",)
    inlines = [PaymentInline]
    actions = ["mark_as_delivered", "mark_as_closed"]

    # 🚚 Acción: Marcar como entregada
    @admin.action(description="🚚 Marcar como entregada")
    def mark_as_delivered(self, request, queryset):
        updated = 0
        for sale in queryset:
            if sale.status in ["pending", "partially_paid", "paid"]:
                sale.status = "delivered"
                sale.delivery_date = date.today()
                sale.save()
                updated += 1
        self.message_user(
            request,
            f"{updated} venta(s) marcada(s) como entregada(s).",
            messages.SUCCESS
        )

    # ✅ Acción: Cerrar venta y generar factura
    @admin.action(description="✅ Cerrar venta y generar factura")
    def mark_as_closed(self, request, queryset):

        updated = 0
        for sale in queryset:
            if sale.status == "delivered":
                sale.status = "closed"
                sale.warranty_end = date.today()
                sale.save()

                iva = Decimal("1.16")  # 👈 ahora el IVA es Decimal
                subtotal = sale.total_amount / iva
                tax = sale.total_amount - subtotal

                # Crear factura
                invoice = Invoice.objects.create(
                    sale=sale,
                    invoice_number=Invoice.next_invoice_number(),
                    subtotal=subtotal,
                    tax=tax,
                    total=sale.total_amount,
                )

                print("✅ Factura creada:", invoice.invoice_number) 

                # Generar PDF
                pdf_response = generate_invoice_pdf(invoice)
                invoice.pdf_file.save(
                    f"{invoice.invoice_number}.pdf",
                    ContentFile(pdf_response.content),
                    save=True
                )

                # 🚀 Enviar correo al cliente
                send_invoice_email(invoice)
                updated += 1

        self.message_user(
            request,
            f"{updated} venta(s) cerrada(s), factura(s) generada(s) y correo(s) enviados.",
            messages.SUCCESS
        )

