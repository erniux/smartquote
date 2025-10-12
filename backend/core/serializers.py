from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "margin",
            "unit",
            "image",
            "image_url",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        """Devuelve la URL completa de la imagen"""
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
