from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "sale", "issue_date", "total")
    readonly_fields = ("invoice_number", "issue_date", "subtotal", "tax", "total", "pdf_file")
