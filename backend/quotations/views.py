from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from quotations.models import Quotation
from quotations.serializers import QuotationSerializer
from sales.models import Sale  # 👈 asegúrate de que la app se llame “sales”
from django.db import transaction

class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all().prefetch_related("items", "expenses").order_by("-date")
    serializer_class = QuotationSerializer

    @action(detail=True, methods=["post"], url_path="generate-sale")
    def generate_sale(self, request, pk=None):
        """
        Genera una venta a partir de una cotización.
        """
        quotation = self.get_object()

        # 🚫 Evitar duplicados
        if hasattr(quotation, "sale"):
            return Response(
                {"detail": "Esta cotización ya tiene una venta generada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Crear la venta
        sale = Sale.objects.create(
            quotation=quotation,
            total_amount=quotation.total,
            notes=f"Venta generada automáticamente desde cotización #{quotation.id}",
        )

        # Establecer fechas de entrega y garantía
        sale.set_delivery_and_warranty(delivery_days=7, warranty_days=90)

        # Serializar respuesta
        serializer_data = {
            "sale_id": sale.id,
            "quotation_id": quotation.id,
            "total_amount": sale.total_amount,
            "status": sale.status,
            "delivery_date": sale.delivery_date,
            "warranty_end": sale.warranty_end,
        }

        return Response(serializer_data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """
        Duplica una cotización (cliente, items, expenses) en estado 'draft'
        """
        original = self.get_object()

        with transaction.atomic():
            # Crear nueva cotización
            new_quotation = Quotation.objects.create(
                customer_name=original.customer_name,
                customer_email=original.customer_email,
                currency=original.currency,
                notes=original.notes,
                subtotal=original.subtotal,
                tax=original.tax,
                total=original.total,
                status="draft",  # 👈 siempre borrador
            )

            # Duplicar items
            for item in original.items.all():
                QuotationItem.objects.create(
                    quotation=new_quotation,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

            # Duplicar gastos
            for exp in original.expenses.all():
                QuotationExpense.objects.create(
                    quotation=new_quotation,
                    name=exp.name,
                    description=exp.description,
                    category=exp.category,
                    quantity=exp.quantity,
                    unit_cost=exp.unit_cost,
                    total_cost=exp.total_cost,
                )

        return Response(
            {"detail": f"Cotización duplicada (ID {new_quotation.id})", "new_id": new_quotation.id},
            status=status.HTTP_201_CREATED,
        )
