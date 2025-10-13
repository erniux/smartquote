from rest_framework import viewsets
from quotations.models import Quotation
from quotations.serializers import QuotationSerializer


class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all().prefetch_related("items", "expenses").order_by("-date")
    serializer_class = QuotationSerializer

