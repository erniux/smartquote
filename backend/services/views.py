from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import MetalPrice
from .serializers import MetalPriceSerializer
from .api_clients import get_yfinance_prices
from rest_framework.decorators import api_view
from django.core.management import call_command



class MetalPriceDetailView(APIView):
    def get(self, request):
        symbol = request.query_params.get("symbol")
        if not symbol:
            return Response({"error": "symbol parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            metal = MetalPrice.objects.filter(symbol__iexact=symbol).order_by("-last_updated").first()
            if not metal:
                return Response({"error": f"No se encontró precio para {symbol}"}, status=status.HTTP_404_NOT_FOUND)
        except MetalPrice.DoesNotExist:
            return Response({"error": f"Metal {symbol} no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MetalPriceSerializer(metal, context={"request": request})
        return Response(serializer.data)

from rest_framework import generics

class MetalPriceListView(generics.ListAPIView):
    """
    Lista todos los metales registrados en la base de datos.
    """
    queryset = MetalPrice.objects.all().order_by("-last_updated")
    serializer_class = MetalPriceSerializer


@api_view(["GET"])
def get_yfinance_prices_view(request):
    """
    Endpoint que obtiene los precios más recientes de metales desde Yahoo Finance
    (sin depender de la base de datos).
    """
    try:
        data = get_yfinance_prices()  # Llama a tu función del api_clients.py
        response = {
            "prices": data,
            "timestamp": timezone.now().isoformat()
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": f"Error al obtener precios de Yahoo Finance: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@api_view(["POST"])
def update_prices_view(request):
    """
    Ejecuta el comando `update_prices` desde el backend y devuelve el resultado.
    """
    try:
        call_command("update_prices")  # Llama el management command
        return Response({"message": "Precios y tasas actualizados correctamente"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["GET"])
def get_price_local_view(request):
    """
    Retorna los precios locales (convertidos a MXN u otra moneda) usando el serializer.
    """
    metals = MetalPrice.objects.all()
    serializer = MetalPriceSerializer(metals, many=True, context={"request": request})
    return Response(serializer.data)