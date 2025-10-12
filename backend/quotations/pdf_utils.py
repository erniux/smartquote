from io import BytesIO
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from datetime import datetime

def generate_quotation_pdf(quotation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()
    elements = []

    # --- Logo y encabezado ---
    # --- Logo y encabezado ---
   # --- Encabezado con logo y datos de empresa emisora ---
    company = quotation.company

    if company and company.logo:
        elements.append(Image(company.logo.path, width=1.3 * inch, height=1.3 * inch))
    else:
        # Logo por defecto si no hay imagen cargada
        elements.append(Image("static/img/default_logo.png", width=1.3 * inch, height=1.3 * inch))

    elements.append(Spacer(1, 0.1 * inch))

    company_name = company.name if company else "Empresa no especificada"
    company_info = f"""
    <para alignment='center'>
    <b><font size=16 color='#007BFF'>{company_name}</font></b><br/>
    {company.address or ''}<br/>
    {company.phone or ''}  |  {company.email or ''}<br/>
    <font size=10 color='grey'>{company.website or ''}</font>
    </para>
    """
    elements.append(Paragraph(company_info, styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    title = "Cotización"  # Puedes personalizar el título aquí
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 0.2 * inch))

    # --- Datos del cliente ---
    client_info = f"""
    <b>Cliente:</b> {quotation.customer_name}<br/>
    <b>Correo:</b> {quotation.customer_email or '-'}<br/>
    <b>Moneda:</b> {quotation.currency}<br/>
    <b>Fecha:</b> {quotation.date.strftime('%d/%m/%Y')}<br/>
    """
    elements.append(Paragraph(client_info, styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # --- Tabla de productos ---
    data = [["Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
    for item in quotation.items.all():
        subtotal_item = round(float(item.unit_price) * item.quantity, 2)
        unit_fmt = f"${float(item.unit_price):,.2f}"
        subtotal_fmt = f"${subtotal_item:,.2f}"
        data.append([
            item.product.name[:30],
            str(item.quantity),
            unit_fmt,
            subtotal_fmt,
        ])

    table = Table(data, colWidths=[2.5 * inch, 1 * inch, 1.3 * inch, 1.3 * inch])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.0, 0.47, 0.75)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ])
    )
    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # --- Totales ---
    tax_amount = round(float(quotation.subtotal) * float(quotation.tax) / 100, 2)
    total_amount = float(quotation.total)

    subtotal_fmt = f"${float(quotation.subtotal):,.2f}"
    tax_fmt = f"${tax_amount:,.2f}"
    total_fmt = f"${total_amount:,.2f}"

    summary_data = [
        ["", "", "Subtotal:", subtotal_fmt],
        ["", "", f"IVA ({quotation.tax}%):", tax_fmt],
        ["", "", "TOTAL:", total_fmt],
    ]

    summary_table = Table(summary_data, colWidths=[2.5 * inch, 1 * inch, 1.3 * inch, 1.3 * inch])
    summary_table.setStyle(
        TableStyle([
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("TEXTCOLOR", (2, 0), (-1, -2), colors.black),
            ("LINEABOVE", (2, -1), (-1, -1), 1, colors.grey),

            # 🔹 Fila TOTAL destacada
            ("BACKGROUND", (2, -1), (-1, -1), colors.Color(0.0, 0.47, 0.75)),
            ("TEXTCOLOR", (2, -1), (-1, -1), colors.white),
            ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (2, -1), (-1, -1), 12),
            ("BOTTOMPADDING", (2, -1), (-1, -1), 8),
        ])
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.4 * inch))

    # --- Condiciones de pago ---
    condition_style = ParagraphStyle(
        name="ConditionStyle",
        fontSize=10,
        leading=14,
        textColor=colors.black,
        spaceAfter=10,
    )

    conditions_text = """
    <b>Condiciones de pago:</b><br/>
    - 50% de anticipo para iniciar el trabajo.<br/>
    - 50% contra entrega.<br/>
    - Los precios están sujetos a variación según cotización de materiales.<br/><br/>
    <b>Validez de cotización:</b><br/>
    Esta cotización tiene una validez de <b>15 días naturales</b> a partir de la fecha de emisión.<br/>
    """
    elements.append(Paragraph(conditions_text, condition_style))
    elements.append(Spacer(1, 0.3 * inch))

    # --- Notas personalizadas ---
    if quotation.notes:
        elements.append(Paragraph(f"<b>Notas adicionales:</b><br/>{quotation.notes}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

    # --- Pie ---
    footer = f"<para alignment='center'><font size=9 color='grey'>Generado automáticamente por SmartQuote © {datetime.now().year}</font></para>"
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(footer, styles["Normal"]))

    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="cotizacion_{quotation.id}.pdf"'
    return response
