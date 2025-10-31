# App/Rutas/crear_comprobante.py
from flask import Blueprint, send_file, make_response, current_app
from bd import get_connection
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import traceback

crear_comprobante_bp = Blueprint('rutas', __name__, url_prefix='/Rutas')

@crear_comprobante_bp.route('/crear_comprobante/<int:reserva_id>', methods=['GET'])
def crear_comprobante(reserva_id):
    connection = get_connection()
    if not connection:
        return make_response("Error al conectar con la base de datos", 500)

    try:
        with connection.cursor() as cursor:
            # 1) Reserva + cliente (se asume que cursor devuelve tuplas)
            cursor.execute("""
                SELECT 
                    r.reserva_id, r.fecha_registro, r.hora_registro,
                    r.fecha_ingreso, r.hora_ingreso, r.fecha_salida, r.hora_salida,
                    r.monto_total, c.cliente_id, c.nombres, c.ape_paterno, c.ape_materno,
                    c.razon_social, c.num_doc, c.telefono
                FROM RESERVA r
                JOIN CLIENTE c ON r.cliente_id = c.cliente_id
                WHERE r.reserva_id = %s
            """, (reserva_id,))
            reserva_row = cursor.fetchone()

            if not reserva_row:
                return make_response("Reserva no encontrada", 404)

            # Desempaquetar (según orden del SELECT)
            (r_reserva_id, r_fecha_reg, r_hora_reg,
             r_fecha_ing, r_hora_ing, r_fecha_sal, r_hora_sal,
             r_monto_total, c_cliente_id, c_nombres, c_ape_p, c_ape_m,
             c_razon, c_num_doc, c_telefono) = reserva_row

            # 2) Obtener habitaciones y calcular precio (piso + categoria)
            cursor.execute("""
                SELECT h.habitacion_id, h.numero,
                       COALESCE(p.precio, 0) as piso_precio,
                       COALESCE(ca.precio_categoria, 0) as categoria_precio
                FROM RESERVA_HABITACION rh
                JOIN HABITACION h ON rh.habitacion_id = h.habitacion_id
                LEFT JOIN PISO p ON h.piso_id = p.piso_id
                LEFT JOIN CATEGORIA ca ON h.id_categoria = ca.categoria_id
                WHERE rh.reserva_id = %s
            """, (reserva_id,))
            habitaciones = cursor.fetchall()  # lista de tuplas

            # 3) Obtener huéspedes asociados a la reserva
            cursor.execute("""
                SELECT h.nombre, h.ape_paterno, h.ape_materno, h.num_doc, rh.habitacion_id
                FROM HUESPED h
                JOIN RESERVA_HABITACION rh ON h.reserva_habitacion_id = rh.reserva_habitacion_id
                WHERE rh.reserva_id = %s
            """, (reserva_id,))
            huespedes = cursor.fetchall()  # lista de tuplas

        # === Generar PDF (ReportLab) ===
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Estilos / posiciones
        x_margin = 50
        y = height - 50

        # Encabezado
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(width / 2, y, "COMPROBANTE DE RESERVA")
        y -= 18
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width / 2, y, "RoomFlow - Sistema de Reservas")
        pdf.line(x_margin, y - 6, width - x_margin, y - 6)
        y -= 20

        # Datos del cliente
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x_margin, y, "Datos del Cliente:")
        y -= 14
        pdf.setFont("Helvetica", 10)
        if c_razon:  # cliente jurídico
            pdf.drawString(x_margin + 10, y, f"Razón social: {c_razon}")
            y -= 12
            pdf.drawString(x_margin + 10, y, f"RUC: {c_num_doc}   Tel: {c_telefono or ''}")
            y -= 18
        else:  # cliente natural
            nombre_full = " ".join(filter(None, [c_nombres, c_ape_p, c_ape_m]))
            pdf.drawString(x_margin + 10, y, f"Nombre: {nombre_full}")
            y -= 12
            pdf.drawString(x_margin + 10, y, f"DNI: {c_num_doc or ''}   Tel: {c_telefono or ''}")
            y -= 18

        # Datos de la reserva
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x_margin, y, "Datos de la Reserva:")
        y -= 14
        pdf.setFont("Helvetica", 10)
        pdf.drawString(x_margin + 10, y, f"ID Reserva: {r_reserva_id}")
        y -= 12
        pdf.drawString(x_margin + 10, y, f"Fecha Registro: {r_fecha_reg} {r_hora_reg}")
        y -= 12
        pdf.drawString(x_margin + 10, y, f"Check-In: {r_fecha_ing or ''} {r_hora_ing or ''}")
        y -= 12
        pdf.drawString(x_margin + 10, y, f"Check-Out: {r_fecha_sal or ''} {r_hora_sal or ''}")
        y -= 18

        # Tabla de habitaciones
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x_margin, y, "Habitaciones:")
        y -= 14
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x_margin + 10, y, "Nro")
        pdf.drawString(x_margin + 110, y, "Precio (S/)")
        pdf.setFont("Helvetica", 10)
        y -= 12

        for hab in habitaciones:
            # hab: (habitacion_id, numero, piso_precio, categoria_precio)
            hab_id = hab[0]
            hab_num = hab[1]
            piso_precio = float(hab[2] or 0)
            cat_precio = float(hab[3] or 0)
            precio_calc = piso_precio + cat_precio
            pdf.drawString(x_margin + 10, y, f"{hab_num}")
            pdf.drawRightString(width - x_margin, y, f"S/. {precio_calc:.2f}")
            y -= 12
            if y < 120:
                pdf.showPage()
                y = height - 50

        y -= 6

        # Huespedes
        if huespedes:
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(x_margin, y, "Huéspedes:")
            y -= 14
            pdf.setFont("Helvetica", 10)
            for hu in huespedes:
                # hu: (nombre, ape_paterno, ape_materno, num_doc, habitacion_id)
                nombre = " ".join(filter(None, [hu[0], hu[1], hu[2]]))
                num_doc_h = hu[3] or ""
                hab_rel = hu[4]
                pdf.drawString(x_margin + 10, y, f"{nombre}  (DNI: {num_doc_h}) - Hab: {hab_rel}")
                y -= 12
                if y < 120:
                    pdf.showPage()
                    y = height - 50
            y -= 6

        # Monto total
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(x_margin, y, "Monto Total:")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(x_margin + 100, y, f"S/. {float(r_monto_total or 0):.2f}")
        y -= 24

        # Pie
        pdf.setFont("Helvetica", 9)
        pdf.line(x_margin, 60, width - x_margin, 60)
        pdf.drawCentredString(width / 2, 48, f"Emitido el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        pdf.drawCentredString(width / 2, 34, "Gracias por confiar en RoomFlow 🏨")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        filename = f"Comprobante_{reserva_id}.pdf"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )

    except Exception as e:
        current_app.logger.exception("❌ Error generando comprobante:")
        # imprimir para consola en desarrollo
        print("❌ Error generando comprobante:", e)
        traceback.print_exc()
        return make_response("Error generando comprobante", 500)
    finally:
        try:
            connection.close()
        except Exception:
            pass
