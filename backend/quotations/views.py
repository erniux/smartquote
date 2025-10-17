from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend 
from django.db import transaction
from django.utils import timezone

from quotations.serializers import QuotationSerializer
from sales.models import Sale 
from quotations.models import Quotation, QuotationItem, QuotationExpense
from users.permissions import IsCompanyMemberOrAdmin
from quotations.permissions import QuotationPermission


class QuotationViewSet(viewsets.ModelViewSet):

    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated, QuotationPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['customer_name', 'customer_email']
    filterset_fields = {'date': ['gte', 'lte'], 'status': ['exact']}

    def get_queryset(self):
        user = self.request.user
        if user.role in ["admin", "soporte"]:
            queryset = Quotation.objects.all().prefetch_related("items", "expenses").order_by("-date")
        else:
            queryset = Quotation.objects.filter(company=user.company).prefetch_related("items", "expenses").order_by("-date")

        return queryset
    


    @action(detail=True, methods=["post"], url_path="generate-sale")
    def generate_sale(self, request, pk=None):
        quotation = self.get_object()

        if request.user.role not in ["manager", "admin"]:
            return Response({"detail": "No tiene permiso para realizar esta acción."},
                    status=status.HTTP_403_FORBIDDEN)

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
            status="pending",
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

        quotation.status = "confirmed"
        quotation.confirmed_at = timezone.now()
        quotation.save(update_fields=["status", "confirmed_at"])

        quotation.refresh_from_db()

        serializer = self.get_serializer(quotation)

        return Response(
        {
            "message": "Venta generada correctamente.",
            "quotation": serializer.data,
            "sale_id": sale.id,
        },
        status=status.HTTP_201_CREATED,
    )

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """
        Duplica una cotización (cliente, items, expenses) en estado 'draft'
        """
        original = self.get_object()

        if request.user.role not in ["manager", "admin"]:
            return Response({"detail": "No tiene permiso para realizar esta acción."},
                    status=status.HTTP_403_FORBIDDEN)

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
                status="draft",  
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


    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_quotation(self, request, pk=None):
        quotation = self.get_object()

        if request.user.role not in ["manager", "admin"]:
            return Response({"detail": "No tiene permiso para realizar esta acción."},
                    status=status.HTTP_403_FORBIDDEN)

        if quotation.status == "cancelled":
            return Response({"detail": "Esta cotización ya está cancelada."},
                            status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get("reason", "").strip()
        if not reason:
            return Response({"error": "Debe proporcionar una razón de cancelación."},
                            status=status.HTTP_400_BAD_REQUEST)

        quotation.status = "cancelled"
        quotation.cancellation_reason = reason
        quotation.cancelled_at = timezone.now()
        quotation.save(update_fields=["status", "cancellation_reason", "cancelled_at"])

        serializer = self.get_serializer(quotation)
        return Response({
            "message": "Cotización cancelada correctamente.",
            "quotation": serializer.data
        }, status=status.HTTP_200_OK)
