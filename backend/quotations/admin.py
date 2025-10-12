from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from quotations.models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0
    readonly_fields = ["unit_price"]
    can_delete = False


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "currency", "subtotal", "total", "date", "updated_at")
    list_filter = ("currency", "date")
    inlines = [QuotationItemInline]
    actions = ["recalculate_prices_action"]

    @admin.action(description="🔁 Recalcular precios con valores del mercado")
    def recalculate_prices_action(self, request, queryset):
        """Recalcula precios según precios actuales de metales y tasa de cambio"""
        total_updated = 0
        for quotation in queryset:
            quotation.calculate_totals()
            total_updated += 1
        self.message_user(
            request,
            _(f"✅ {total_updated} cotización(es) actualizada(s) con los nuevos precios del mercado.")
        )
