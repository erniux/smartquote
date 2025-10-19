from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse

import csv
from io import TextIOWrapper

from .models import Product
from .serializers import ProductSerializer




class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    search_fields = ["name", "metal_symbol"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=["get"])
    def csv_layout(self, request):
        """
        Devuelve un archivo CSV plantilla con los encabezados correctos.
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="productos_layout.csv"'

        writer = csv.writer(response)
        headers = ["name", "description", "price", "margin", "unit", "metal_symbol"]
        writer.writerow(headers)
        writer.writerow(["Ejemplo Tornillo", "Acero galvanizado", "1.25", "5", "pieza", "IRON"])
        writer.writerow(["Ejemplo PVC", "Tubo presión", "0.95", "3", "metro", "PVC"])

        return response

    @action(detail=False, methods=["post"])
    def upload_csv(self, request):
        """
        Permite cargar un archivo CSV con productos masivamente.
        Espera columnas: name, description, price, margin, unit, metal_symbol
        """
        try:
            file = request.FILES.get("file")
            if not file:
                return Response({"error": "No se recibió ningún archivo CSV."},
                                status=status.HTTP_400_BAD_REQUEST)

            decoded_file = TextIOWrapper(file, encoding="utf-8")
            reader = csv.DictReader(decoded_file)

            created = []
            for row in reader:
                product = Product.objects.create(
                    name=row.get("name"),
                    description=row.get("description", ""),
                    price=row.get("price") or 0,
                    margin=row.get("margin") or 0,
                    unit=row.get("unit", "pieza"),
                    metal_symbol=row.get("metal_symbol", ""),
                )
                created.append(product.name)

            return Response(
                {"message": f"{len(created)} productos creados correctamente.", "productos": created},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": f"Error procesando CSV: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
