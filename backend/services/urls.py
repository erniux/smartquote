from django.urls import path
from .views import MetalPriceDetailView
from .views import get_yfinance_prices_view, MetalPriceDetailView, update_prices_view

urlpatterns = [
    path("metalprice/", MetalPriceDetailView.as_view(), name="metalprice-detail"),
    path("get_yfinance_prices/", get_yfinance_prices_view, name="get_yfinance_prices"),
    path("update_prices/", update_prices_view, name="update_prices"),
]
