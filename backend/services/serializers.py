from rest_framework import serializers
from decimal import Decimal
from .models import MetalPrice
from .models import CurrencyRate


class MetalPriceSerializer(serializers.ModelSerializer):
    price_with_margin_usd = serializers.SerializerMethodField()
    price_local = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = MetalPrice
        fields = [
            "symbol",
            "price_usd",
            "price_with_margin_usd",
            "price_local",
            "currency",
            "last_updated",
        ]

    def get_price_with_margin_usd(self, obj):
        # 👇 Si el producto tiene margen, se calculará más adelante en Product
        margin = Decimal("0.00")
        request = self.context.get("request")
        if request:
            margin_param = request.query_params.get("margin")
            if margin_param:
                try:
                    margin = Decimal(margin_param)
                except:
                    pass
        return (obj.price_usd * (Decimal("1.00") + margin / Decimal("100"))).quantize(Decimal("0.01"))

    def get_currency(self, obj):
        request = self.context.get("request")
        return request.query_params.get("currency", "MXN")

    def get_price_local(self, obj):
        request = self.context.get("request")
        currency = request.query_params.get("currency", "MXN")
        rate = Decimal("1.00")

        # Buscar tipo de cambio USD -> currency
        if currency != "USD":
            rate_obj = (
                CurrencyRate.objects.filter(base_currency="USD", target_currency=currency)
                .order_by("-last_updated")
                .first()
            )
            if rate_obj:
                rate = rate_obj.rate

        margin_param = request.query_params.get("margin")
        margin = Decimal(margin_param) if margin_param else Decimal("0.00")

        price_with_margin_usd = obj.price_usd * (Decimal("1.00") + margin / Decimal("100"))
        price_local = price_with_margin_usd * rate
        return price_local.quantize(Decimal("0.01"))
