from rest_framework import routers
from quotations.views import QuotationViewSet

router = routers.DefaultRouter()
router.register(r'quotations', QuotationViewSet, basename='quotation')

urlpatterns = router.urls
