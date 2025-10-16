# sales/serializers.py
from rest_framework import serializers
from .models import Sale, Payment
from invoices.models import Invoice
from invoices.pdf_utils import generate_invoice_pdf
from invoices.email_utils import send_invoice_email
from django.core.files.base import ContentFile
from decimal import Decimal
from datetime import date

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "payment_date", "amount", "method"]

class SaleSerializer(serializers.ModelSerializer):
    quotation_id = serializers.PrimaryKeyRelatedField(source="quotation", read_only=True)
    quotation_name = serializers.CharField(source="quotation.customer_name", read_only=True)
    quotation_email = serializers.EmailField(source="quotation.customer_email", read_only=True)
    quotation_company = serializers.CharField(source="quotation.company", read_only=True)
    invoice_id = serializers.SerializerMethodField()
    invoice_pdf_url = serializers.SerializerMethodField()

    def get_invoice_pdf_url(self, obj):
        """Devuelve la URL del PDF de la factura si existe."""
        if hasattr(obj, "invoice") and getattr(obj.invoice, "pdf_file", None):
            return obj.invoice.pdf_file.url
        return None

    def get_invoice_id(self, obj):
        """Devuelve el ID de la factura si existe."""
        if hasattr(obj, "invoice"):
            return obj.invoice.id
        return None

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "quotation_id",
            "quotation_name",
            "quotation_email",
            "quotation_company",
            "total_amount",
            "status",
            "sale_date",
            "delivery_date",
            "warranty_end",
            "notes",
            "payments",
            "invoice_id"
        ]

    def update(self, instance, validated_data):
        """Permite actualizar estado o notas desde el frontend."""
        instance.status = validated_data.get("status", instance.status)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.save()
        return instance

    # --- Acciones especiales ---
    def mark_as_delivered(self, sale: Sale):
        if sale.status in ["pending", "partially_paid", "paid"]:
            sale.status = "delivered"
            sale.delivery_date = date.today()
            sale.save()
        return sale

    def mark_as_closed(self, sale: Sale):
        """Cierra venta, genera factura y envía correo."""
        if sale.status == "delivered":
            sale.status = "closed"
            sale.warranty_end = date.today()
            sale.save()

            iva = Decimal("1.16")
            subtotal = sale.total_amount / iva
            tax = sale.total_amount - subtotal

            invoice = Invoice.objects.create(
                sale=sale,
                invoice_number=Invoice.next_invoice_number(),
                subtotal=subtotal,
                tax=tax,
                total=sale.total_amount,
            )

            pdf_response = generate_invoice_pdf(invoice)
            invoice.pdf_file.save(
                f"{invoice.invoice_number}.pdf",
                ContentFile(pdf_response.content),
                save=True,
            )

            send_invoice_email(invoice)

        return sale
    
    def get_invoice_id(self, obj):
        return getattr(obj.invoice, "id", None) if hasattr(obj, "invoice") else None
