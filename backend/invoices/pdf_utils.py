from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
import os
from decimal import Decimal, ROUND_HALF_UP




def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # === Datos simulados del emisor ===
    emisor = {
        "nombre": "La Esmeralda de la Decoración S.A. de C.V.",
        "rfc": "EDE010203ABC",
        "regimen": "601 - General de Ley Personas Morales",
        "domicilio": "Av. Reforma 123, CDMX, México",
    }

    # === Datos del receptor ===
    sale = invoice.sale
    quotation = sale.quotation
    receptor = {
        "nombre": quotation.customer_name,
        "rfc": "ESC210405MX9",  # ficticio
        "cp": "76000",
        "uso_cfdi": "G03 - Gastos en general",
    }

    # === Logo ===
    logo_path = os.path.join(settings.MEDIA_ROOT, "logos", "la_esmeralda_logo.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.MEDIA_ROOT, "logos", "default-logo.png")

    try:
        img = Image(logo_path, width=100, height=70)
        elements.append(img)
    except Exception:
        pass

    elements.append(Paragraph(f"<b>{emisor['nombre']}</b>", styles["Title"]))
    elements.append(Paragraph(f"RFC: {emisor['rfc']}<br/>Régimen Fiscal: {emisor['regimen']}<br/>{emisor['domicilio']}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # === Información de la factura ===
    elements.append(Paragraph(f"<b>Factura:</b> {invoice.invoice_number}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fecha de emisión:</b> {invoice.issue_date.strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # === Datos del receptor ===
    elements.append(Paragraph("<b>Datos del Cliente:</b>", styles["Heading4"]))
    elements.append(Paragraph(f"Nombre: {receptor['nombre']}<br/>RFC: {receptor['rfc']}<br/>CP: {receptor['cp']}<br/>Uso CFDI: {receptor['uso_cfdi']}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # === Tabla de conceptos ===
    data = [["Descripción", "Cantidad", "Precio Unitario", "Subtotal"]]
    for item in quotation.items.all():
        subtotal_item = Decimal(item.quantity) * item.unit_price
        data.append([
            item.product.name,
            f"{item.quantity}",
            f"${item.unit_price:,.2f}",
            f"${subtotal_item:,.2f}",
        ])

    subtotal = invoice.subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    tax = invoice.tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (subtotal + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # === Totales ===
    subtotal = invoice.subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    tax = invoice.tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (subtotal + tax).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Estilos
    bold_right = ParagraphStyle(name="BoldRight", alignment=2, fontName="Helvetica-Bold", fontSize=10)
    normal_right = ParagraphStyle(name="NormalRight", alignment=2, fontName="Helvetica", fontSize=10)

    # Filas finales
    data.append(["", "", Paragraph("Subtotal:", bold_right), Paragraph(f"${subtotal:,.2f}", normal_right)])
    data.append(["", "", Paragraph("IVA (16%):", bold_right), Paragraph(f"${tax:,.2f}", normal_right)])
    data.append(["", "", Paragraph("<b>Total:</b>", bold_right), Paragraph(f"<b>${total:,.2f}</b>", bold_right)])

    # === Construcción de tabla de totales ===
    table = Table(data, colWidths=[220, 70, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # === Total en letras (celda elegante) ===
    total_en_letras = numero_a_letras(total)

    # Crea tabla independiente para el texto
    letras_table = Table(
        [[Paragraph(f"<b>Total con letra:</b> {total_en_letras}", ParagraphStyle(
            name="TotalLetras",
            alignment=1,  # 0=izquierda, 1=centro, 2=derecha
            fontName="Helvetica",
            fontSize=10,
            textColor=colors.black,
            leading=14,
        ))]],
        colWidths=[490],
    )

    letras_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.Color(0.94, 0.94, 0.94)),  # gris suave
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))

    elements.append(letras_table)
    elements.append(Spacer(1, 25))

    # === Código QR simulado ===
    qr_code = qr.QrCodeWidget(f"Factura: {invoice.invoice_number} | RFC Emisor: {emisor['rfc']} | RFC Receptor: {receptor['rfc']} | Total: ${invoice.total:,.2f}")
    qr_drawing = Drawing(70, 70)
    qr_drawing.add(qr_code)
    elements.append(qr_drawing)
    elements.append(Spacer(1, 15))

    # === Sello digital simulado ===
    sello = "SELLO_DIGITAL_SIMULADO_ABC123XYZ4567890"
    elements.append(Paragraph("<b>Sello Digital del SAT:</b>", styles["Heading5"]))
    elements.append(Paragraph(f"<font size=8>{sello}</font>", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # === Pie ===
    footer = Paragraph(
        "<para align='center'><font size=9 color='grey'>Documento sin validez fiscal – generado automáticamente con SmartQuote © 2025</font></para>",
        ParagraphStyle(name="footer", alignment=1)
    )
    elements.append(footer)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="application/pdf")
    response.write(pdf)
    return response



def numero_a_letras(num):
    """
    Convierte un número decimal (hasta 999,999,999.99) a texto en pesos mexicanos.
    Ejemplo: 6823.18 -> 'Seis mil ochocientos veintitrés pesos 18/100 M.N.'
    """
    unidades = (
        "", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete",
        "ocho", "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
        "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte"
    )
    decenas = (
        "", "", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta",
        "setenta", "ochenta", "noventa"
    )
    centenas = (
        "", "ciento", "doscientos", "trescientos", "cuatrocientos",
        "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"
    )

    def convertir_entero(n):
        if n == 0:
            return "cero"
        if n == 100:
            return "cien"
        if n < 21:
            return unidades[n]
        if n < 100:
            d, u = divmod(n, 10)
            return decenas[d] + (f" y {unidades[u]}" if u else "")
        if n < 1000:
            c, r = divmod(n, 100)
            return centenas[c] + (f" {convertir_entero(r)}" if r else "")
        if n < 1_000_000:
            miles, resto = divmod(n, 1000)
            miles_texto = "mil" if miles == 1 else f"{convertir_entero(miles)} mil"
            return miles_texto + (f" {convertir_entero(resto)}" if resto else "")
        if n < 1_000_000_000:
            millones, resto = divmod(n, 1_000_000)
            millones_texto = "un millón" if millones == 1 else f"{convertir_entero(millones)} millones"
            return millones_texto + (f" {convertir_entero(resto)}" if resto else "")
        return str(n)

    n = Decimal(num).quantize(Decimal("0.01"))
    entero = int(n)
    centavos = int((n - entero) * 100)
    letras = convertir_entero(entero).capitalize()
    return f"{letras} pesos {centavos:02d}/100 M.N."

