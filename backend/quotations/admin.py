from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect
from quotations.pdf_utils import generate_quotation_pdf
from quotations.models import Quotation, QuotationItem, QuotationExpense
from decimal import Decimal,ROUND_HALF_UP


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 0
    readonly_fields = ["unit_price"]
    can_delete = False

class QuotationExpenseInline(admin.TabularInline):
    model = QuotationExpense
    extra = 1
    readonly_fields = ["total_cost"]
    can_delete = True


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "currency", "subtotal", "total", "date", "status", "updated_at")
    list_filter = ("currency", "date", "status")
    inlines = [QuotationItemInline, QuotationExpenseInline]
    actions = ["recalculate_prices_action", "confirm_quotation_action"]


    @admin.action(description="🔁 Recalcular precios con valores del mercado")
    def recalculate_prices_action(self, request, queryset):
        total_updated = 0
        for quotation in queryset:
            quotation.calculate_totals()
            total_updated += 1
        self.message_user(request, f"✅ {total_updated} cotización(es) actualizada(s) con los nuevos precios del mercado.", messages.SUCCESS)
    
    @admin.action(description="✅ Confirmar cotización y generar venta")
    def confirm_quotation_action(modeladmin, request, queryset):
        from sales.models import Sale
        total_confirmed = 0
        for quotation in queryset:
            sale = quotation.confirm()
            total_confirmed += 1
        modeladmin.message_user(
            request,
            f"{total_confirmed} cotización(es) confirmada(s) y convertida(s) en venta(s).",
            messages.SUCCESS
        )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:quotation_id>/recalculate/",
                self.admin_site.admin_view(self.recalculate_now),
                name="quotation-recalculate",
            ),
        ]
        return custom_urls + urls

    def recalculate_now(self, request, quotation_id):
        quotation = Quotation.objects.get(pk=quotation_id)
        quotation.calculate_totals()
        self.message_user(request, "✅ Cotización actualizada con precios del mercado.", messages.SUCCESS)

        # Redirección correcta al formulario actual
        change_url = reverse("admin:quotations_quotation_change", args=[quotation_id])
        return redirect(change_url)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:quotation_id>/recalculate/",
                self.admin_site.admin_view(self.recalculate_now),
                name="quotation-recalculate",
            ),
            path(
                "<int:quotation_id>/pdf/",
                self.admin_site.admin_view(self.download_pdf),
                name="quotation-pdf",
            ),
        ]
        return custom_urls + urls

    def download_pdf(self, request, quotation_id):
        quotation = self.get_object(request, quotation_id)
        return generate_quotation_pdf(quotation)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        recalc_url = reverse("admin:quotation-recalculate", args=[object_id])
        pdf_url = reverse("admin:quotation-pdf", args=[object_id])
        extra_context["recalculate_url"] = recalc_url
        extra_context["pdf_url"] = pdf_url
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    




