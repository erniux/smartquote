from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    search_fields = ["name", "metal_symbol"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

