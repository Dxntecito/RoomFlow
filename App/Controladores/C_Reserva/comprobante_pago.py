# rutas_comprobante.py (añádelo a tu app / blueprint)
from flask import Blueprint, send_file, current_app, Response
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import qrcode

# Importa tu controlador o función que devuelve la info de la reserva
# from App.Controladores.C_Reserva.controlador_reserva import get_reserva_by_id

comprobante_bp = Blueprint('comprobante', __name__, url_prefix='/Rutas')

def generar_qr_imagen(texto):
    """Genera una imagen QR en memoria (PIL) y la devuelve como BytesIO PNG."""
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return bio

def crear_pdf_comprobante(reserva):
    """
    Crea un PDF (bytes) con diseño básico tipo comprobante.
    'reserva' debe ser un dict con los campos que uses abajo.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    styles = getSampleStyleSheet()
    normal = styles['Normal']
    bold = styles['Heading4']

    # Margen
    left_margin = 18 * mm
    top = height - 20 * mm

    # Encabezado - empresa
    empresa = reserva.get('empresa', 'Mi Hotel S.A.C.')
    direccion = reserva.get('empresa_direccion', 'Av. Ejemplo 123, Lima')
    ruc = reserva.get('empresa_ruc', '20123456789')
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, top, empresa)
    c.setFont("Helvetica", 9)
    c.drawString(left_margin, top - 12, direccion)
    c.drawString(left_margin, top - 24, f"RUC: {ruc}")

    # Título comprobante
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - left_margin, top, f"COMPROBANTE DE PAGO")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - left_margin, top - 12, f"No. {reserva.get('comprobante_numero', 'B001-0001')}")

    # Línea separadora
    c.setStrokeColor(colors.grey)
    c.setLineWidth(0.5)
    c.line(left_margin, top - 36, width - left_margin, top - 36)

    # Datos cliente / reserva
    y = top - 50
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, y, "Cliente:")
    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 60, y, reserva.get('cliente_nombre', 'N/A'))
    c.drawString(width/2, y, f"Reserva ID: {reserva.get('reserva_id', '')}")

    y -= 14
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, y, "Documento:")
    c.setFont("Helvetica", 9)
    c.drawString(left_margin + 60, y, reserva.get('cliente_doc', 'N/A'))
    c.drawString(width/2, y, f"Fecha registro: {reserva.get('fecha_registro', '')}")

    y -= 18

    # Tabla de habitaciones
    table_data = [["Habitación", "Categoría", "Capacidad", "Precio S/"]]
    rooms = reserva.get('habitaciones', [])
    for r in rooms:
        table_data.append([r.get('numero', ''), r.get('categoria', ''), str(r.get('capacidad','')), f"{float(r.get('precio',0)):.2f}"])

    # Total fila
    total = float(reserva.get('total', 0) or 0)
    table_data.append(["", "", "TOTAL", f"S/. {total:.2f}"])

    table = Table(table_data, colWidths=[60*mm, 60*mm, 30*mm, 30*mm])
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-2), 0.25, colors.grey),
        ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
        ('SPAN', (0,-1), (2,-1)),
        ('ALIGN', (3,-1), (3,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ])
    table.setStyle(table_style)

    # Determinar posición e imprimir tabla (usar platypus drawOn)
    w_table, h_table = table.wrapOn(c, width - 2*left_margin, 0)
    table.drawOn(c, left_margin, y - h_table)

    # QR con metadata/pago (ej: enlace o id de comprobante)
    qr_text = reserva.get('qr_text', f"RESERVA:{reserva.get('reserva_id','')};TOTAL:{total:.2f}")
    qr_imgio = generar_qr_imagen(qr_text)
    qr_x = width - left_margin - (35*mm)
    qr_y = y - h_table - (5*mm) - (35*mm)
    c.drawImage(qr_imgio, qr_x, qr_y, width=35*mm, height=35*mm)

    # Notas / condiciones
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(left_margin, qr_y + 6, "Gracias por su preferencia. Este comprobante es válido para respaldo de pago.")
    c.drawString(left_margin, qr_y - 8, f"Fecha ingreso: {reserva.get('fecha_ingreso','-')}  Hora ingreso: {reserva.get('hora_ingreso','-')}")
    c.drawString(left_margin, qr_y - 20, f"Fecha salida: {reserva.get('fecha_salida','-')}  Hora salida: {reserva.get('hora_salida','-')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@comprobante_bp.route('/comprobante/<int:reserva_id>', methods=['GET'])
def descargar_comprobante(reserva_id):
    """
    Endpoint que crea el PDF del comprobante para la reserva dada.
    Debes reemplazar get_reserva_by_id por tu función real que consulte la BD
    y devuelva un dict con la estructura esperada (ver ejemplo abajo).
    """
    # --- OBTENER DATOS DE LA RESERVA (reemplaza con tu controlador) ---
    # reserva = get_reserva_by_id(reserva_id)
    # Ejemplo dummy (si no existe tu función aún), BORRAR en producción:
    reserva = {
        'reserva_id': reserva_id,
        'empresa': 'Hostal Bolívar',
        'empresa_direccion': 'Jr. Falsa 123, Lima',
        'empresa_ruc': '20123456789',
        'comprobante_numero': f'B001-{reserva_id:04d}',
        'cliente_nombre': 'Felix Zuniga',
        'cliente_doc': '87654321',
        'fecha_registro': '2025-10-27 16:00',
        'fecha_ingreso': '2025-11-01',
        'hora_ingreso': '14:00:00',
        'fecha_salida': '2025-11-03',
        'hora_salida': '12:00:00',
        'habitaciones': [
            {'numero': '101', 'categoria': 'Económica', 'capacidad': 2, 'precio': 120.00},
            {'numero': '102', 'categoria': 'Suite', 'capacidad': 3, 'precio': 200.00}
        ],
        'total': 320.00,
        'qr_text': f"RESERVA:{reserva_id};TOTAL:320.00"
    }

    # --- CREAR PDF ---
    try:
        pdf_io = crear_pdf_comprobante(reserva)
        filename = f"Comprobante_{reserva_id}.pdf"
        return send_file(pdf_io, mimetype='application/pdf',
                         as_attachment=True,
                         download_name=filename)
    except Exception as e:
        current_app.logger.exception("Error generando comprobante")
        return Response("Error generando comprobante", status=500)
