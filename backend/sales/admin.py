from django.contrib import admin, messages
from .models import Sale, Payment
from datetime import date

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ["payment_date"]
    can_delete = False

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quotation",
        "total_amount",
        "status",
        "sale_date",
        "delivery_date",
        "warranty_end",
    )
    list_filter = ("status",)
    inlines = [PaymentInline]
    actions = ["mark_as_delivered", "mark_as_closed"]

    # 🚚 Acción: Marcar como entregada
    @admin.action(description="🚚 Marcar como entregada")
    def mark_as_delivered(self, request, queryset):
        updated = 0
        for sale in queryset:
            if sale.status in ["pending", "partially_paid", "paid"]:
                sale.status = "delivered"
                sale.delivery_date = date.today()
                sale.save()
                updated += 1
        self.message_user(
            request,
            f"{updated} venta(s) marcada(s) como entregada(s).",
            messages.SUCCESS
        )

    # ✅ Acción: Cerrar venta
    @admin.action(description="✅ Cerrar venta")
    def mark_as_closed(self, request, queryset):
        updated = 0
        for sale in queryset:
            if sale.status == "delivered":
                sale.status = "closed"
                sale.warranty_end = date.today()
                sale.save()
                updated += 1
        self.message_user(
            request,
            f"{updated} venta(s) cerrada(s) correctamente.",
            messages.SUCCESS
        )
