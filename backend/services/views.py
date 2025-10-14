from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MetalPrice
from .serializers import MetalPriceSerializer


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
