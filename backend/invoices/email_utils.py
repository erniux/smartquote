from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def send_invoice_email(invoice):
    """Envía la factura por correo al cliente."""
    quotation = invoice.sale.quotation
    customer_email = quotation.customer_email

    if not customer_email:
        return False

    subject = f"Factura {invoice.invoice_number} – {quotation.customer_name}"
    body = render_to_string(
        "emails/invoice_email.html",
        {
            "customer": quotation.customer_name,
            "invoice_number": invoice.invoice_number,
            "total": f"${invoice.total:,.2f}",
            "issue_date": invoice.issue_date,
        },
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[customer_email],
    )

    if invoice.pdf_file:
        email.attach_file(invoice.pdf_file.path)

    email.content_subtype = "html"
    #email.send(fail_silently=False)
    return True
