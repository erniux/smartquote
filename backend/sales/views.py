# sales/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Sale
from .serializers import SaleSerializer, PaymentSerializer
from .permissions import SalePermission



class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().select_related("quotation").prefetch_related("payments")
    serializer_class = SaleSerializer
    permission_classes = [SalePermission, SalePermission]

    @action(detail=True, methods=["post"])
    def mark_delivered(self, request, pk=None):
        """Acción: Marcar venta como entregada."""
        sale = self.get_object()
        serializer = self.get_serializer()
        serializer.mark_as_delivered(sale)
        return Response({"message": "Venta marcada como entregada"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def mark_closed(self, request, pk=None):
        """Acción: Cerrar venta, generar factura y enviar correo."""
        sale = self.get_object()
        serializer = self.get_serializer()
        serializer.mark_as_closed(sale)
        return Response({"message": "Venta cerrada y factura generada"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def add_payment(self, request, pk=None):
        """Permite agregar un pago a la venta."""
        sale = self.get_object()
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sale=sale)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
