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

            (r_reserva_id, r_fecha_reg, r_hora_reg,
             r_fecha_ing, r_hora_ing, r_fecha_sal, r_hora_sal,
             r_monto_total, c_cliente_id, c_nombres, c_ape_p, c_ape_m,
             c_razon, c_num_doc, c_telefono) = reserva_row

            cursor.execute("""
                SELECT h.habitacion_id, h.numero,
                       COALESCE(p.precio, 0), COALESCE(ca.precio_categoria, 0)
                FROM RESERVA_HABITACION rh
                JOIN HABITACION h ON rh.habitacion_id = h.habitacion_id
                LEFT JOIN PISO p ON h.piso_id = p.piso_id
                LEFT JOIN CATEGORIA ca ON h.id_categoria = ca.categoria_id
                WHERE rh.reserva_id = %s
            """, (reserva_id,))
            habitaciones = cursor.fetchall()

            cursor.execute("""
                SELECT h.nombre, h.ape_paterno, h.ape_materno, h.num_doc, rh.habitacion_id
                FROM HUESPED h
                JOIN RESERVA_HABITACION rh ON h.reserva_habitacion_id = rh.reserva_habitacion_id
                WHERE rh.reserva_id = %s
            """, (reserva_id,))
            huespedes = cursor.fetchall()

        # === Generar PDF ===
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        x_margin = 50
        right_margin = width - 50
        y = height - 60

        # ==== ENCABEZADO ====
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(width / 2, y, "ROOMFLOW S.A.C.")
        y -= 22
        pdf.setFont("Helvetica", 10)
        pdf.drawCentredString(width / 2, y, "RUC: 20608999991")
        y -= 14
        pdf.drawCentredString(width / 2, y, "Av. Los Olivos 245 - Lima, Perú")
        y -= 14
        pdf.drawCentredString(width / 2, y, "Tel: (01) 456-7890 | Email: contacto@roomflow.pe")
        y -= 22
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(width / 2, y, "BOLETA DE RESERVA")
        y -= 25
        pdf.line(x_margin, y, right_margin, y)
        y -= 28

        # ==== DATOS DEL CLIENTE ====
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x_margin, y, "Datos del Cliente:")
        y -= 18
        pdf.setFont("Helvetica", 10)
        if c_razon:
            pdf.drawString(x_margin + 10, y, f"Razón Social: {c_razon}")
            y -= 16
            pdf.drawString(x_margin + 10, y, f"RUC: {c_num_doc}   Teléfono: {c_telefono or '-'}")
            y -= 22
        else:
            nombre_full = " ".join(filter(None, [c_nombres, c_ape_p, c_ape_m]))
            pdf.drawString(x_margin + 10, y, f"Nombre: {nombre_full}")
            y -= 16
            pdf.drawString(x_margin + 10, y, f"DNI: {c_num_doc or '-'}   Teléfono: {c_telefono or '-'}")
            y -= 22

        # ==== DATOS DE LA RESERVA ====
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x_margin, y, "Datos de la Reserva:")
        y -= 18
        pdf.setFont("Helvetica", 10)
        pdf.drawString(x_margin + 10, y, f"ID Reserva: {r_reserva_id}")
        y -= 15
        pdf.drawString(x_margin + 10, y, f"Fecha de Registro: {r_fecha_reg} {r_hora_reg}")
        y -= 15
        pdf.drawString(x_margin + 10, y, f"Check-In: {r_fecha_ing or '-'} {r_hora_ing or '-'}")
        y -= 15
        pdf.drawString(x_margin + 10, y, f"Check-Out: {r_fecha_sal or '-'} {r_hora_sal or '-'}")
        y -= 25

        # ==== HABITACIONES ====
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(x_margin, y, "Habitaciones y Huéspedes:")
        y -= 18
        pdf.line(x_margin, y, right_margin, y)
        y -= 20

        huespedes_por_habitacion = {}
        for hu in huespedes:
            nombre = " ".join(filter(None, [hu[0], hu[1], hu[2]]))
            num_doc_h = hu[3] or ""
            hab_rel = hu[4]
            huespedes_por_habitacion.setdefault(hab_rel, []).append((nombre, num_doc_h))

        pdf.setFont("Helvetica", 10)
        for hab in habitaciones:
            hab_id, hab_num, piso_precio, cat_precio = hab
            precio_calc = float(piso_precio or 0) + float(cat_precio or 0)

            # Línea de habitación
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(x_margin + 10, y, f"Habitación {hab_num}")
            pdf.drawRightString(right_margin, y, f"S/. {precio_calc:.2f}")
            y -= 16

            # Huéspedes
            pdf.setFont("Helvetica", 10)
            if hab_id in huespedes_por_habitacion:
                for nombre, num_doc_h in huespedes_por_habitacion[hab_id]:
                    pdf.drawString(x_margin + 25, y, f"- {nombre} (DNI: {num_doc_h})")
                    y -= 14
                    if y < 100:
                        pdf.showPage()
                        y = height - 60
            else:
                pdf.drawString(x_margin + 25, y, "- Sin huéspedes registrados")
                y -= 14

            y -= 10

        # ==== MONTOS TOTALES ====
        pdf.line(x_margin, y, right_margin, y)
        y -= 22
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(x_margin, y, "MONTO TOTAL:")
        pdf.drawRightString(right_margin, y, f"S/. {float(r_monto_total or 0):.2f}")
        y -= 35

        # ==== PIE ====
        pdf.setFont("Helvetica", 9)
        pdf.line(x_margin, 70, right_margin, 70)
        pdf.drawCentredString(width / 2, 56, f"Emitido el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        pdf.drawCentredString(width / 2, 42, "Documento generado electrónicamente por RoomFlow S.A.C.")
        pdf.drawCentredString(width / 2, 28, "Gracias por su preferencia 🇵🇪")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        filename = f"Boleta_{reserva_id}.pdf"
        return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")

    except Exception as e:
        current_app.logger.exception("❌ Error generando boleta:")
        traceback.print_exc()
        return make_response("Error generando boleta", 500)
    finally:
        try:
            connection.close()
        except Exception:
            pass
