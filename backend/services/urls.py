from django.urls import path
from .views import MetalPriceDetailView

urlpatterns = [
    path("metalprice/", MetalPriceDetailView.as_view(), name="metalprice-detail"),
]
