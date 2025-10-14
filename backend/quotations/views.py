from rest_framework import viewsets
from quotations.models import Quotation
from quotations.serializers import QuotationSerializer


class QuotationViewSet(viewsets.ModelViewSet):
    serializer_class = QuotationSerializer

    def get_queryset(self):
        queryset = (
            Quotation.objects.all()
            .prefetch_related("items", "expenses")
            .order_by("-date")
        )

        # 🧩 Obtener parámetro de filtro desde la URL (?status=cancelled)
        status_param = self.request.query_params.get("status")
        print("🔍 Filtro recibido:", status_param)

        if status_param and status_param != "all":
            queryset = queryset.filter(status=status_param)

        return queryset
