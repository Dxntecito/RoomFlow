from datetime import date, datetime
from bd import get_connection
from flask import jsonify, request,url_for
import pymysql
def get_reserva_por_fecha_usuario(fecha_ingreso, usuario_id):
    connection = get_connection()
    reserva = None
    try:
        # 👇 aquí usamos DictCursor para obtener resultados como diccionarios
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    r.fecha_ingreso, 
                    r.fecha_salida, 
                    r.hora_ingreso, 
                    r.hora_salida,
                    h.numero AS numero_habitacion,
                    rh.reserva_habitacion_id
                FROM RESERVA r
                INNER JOIN RESERVA_HABITACION rh ON rh.reserva_id = r.reserva_id
                INNER JOIN HABITACION h ON h.habitacion_id = rh.habitacion_id
                INNER JOIN CLIENTE c ON c.cliente_id = r.cliente_id
                INNER JOIN USUARIO u ON u.cliente_id = c.cliente_id
                WHERE DATE(r.fecha_ingreso) = %s
                  AND u.usuario_id = %s
                  AND r.tipo_reserva = 'H'
                  AND DATE(r.fecha_salida) >= CURDATE()
            """, (fecha_ingreso, usuario_id))

            rows = cursor.fetchall()
            if rows:
                reserva = {
                    'fecha_ingreso': str(rows[0]['fecha_ingreso']) if rows[0]['fecha_ingreso'] else '',
                    'fecha_salida': str(rows[0]['fecha_salida']) if rows[0]['fecha_salida'] else '',
                    'hora_ingreso': str(rows[0]['hora_ingreso']) if rows[0]['hora_ingreso'] else '',
                    'hora_salida': str(rows[0]['hora_salida']) if rows[0]['hora_salida'] else '',
                    'habitaciones': [
                        {
                            'numero': r['numero_habitacion'],
                            'reserva_habitacion_id': r['reserva_habitacion_id']
                        }
                        for r in rows
                    ]
                }

    except Exception as e:
        print("❌ Error al obtener la reserva:", e)
    finally:
        connection.close()

    return reserva

def get_amenidades():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            select * from AMENIDAD;
        """)
        amenidades = cursor.fetchall()
    connection.close()
    return amenidades

def procesar_pago_roomservice(data):
    """
    Controlador que procesa el pago de RoomService en una sola transacción.
    Inserta en: cliente (si no existe), reserva, room_service, room_service_amenidad,
    transaccion, comprobante y detalle_comprobante.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # =============================
        # 1️⃣ Datos base
        # =============================
        usuario_id = data.get('usuario_id')
        if not usuario_id:
            return jsonify({
                "success": False,
                "error": "Usuario no autenticado."
            }), 401

        metodo_pago_id = data.get('metodo_pago_id')
        tipo_comprobante = data.get('tipo_comprobante')
        total_general = data.get('total_general')
        productos = data.get('productos', [])
        reserva_habitacion_id = data.get('reserva_habitacion_id')


        fecha_actual = datetime.now().date()
        hora_actual = datetime.now().strftime('%H:%M:%S')

        # =============================
        # =============================
        # 2️⃣ Obtener cliente desde usuario autenticado
        # =============================
        cursor.execute("""
            SELECT c.cliente_id, COALESCE(c.id_tipo_cliente, 'N')
            FROM USUARIO u
            INNER JOIN CLIENTE c ON c.cliente_id = u.cliente_id
            WHERE u.usuario_id = %s
        """, (usuario_id,))
        cliente = cursor.fetchone()

        if not cliente:
            return jsonify({
                "success": False,
                "error": "No se encontró un cliente asociado al usuario."
            }), 400

        cliente_id = cliente[0]

        # =============================
        # 3️⃣ Crear reserva
        # =============================
        cursor.execute("""
            INSERT INTO RESERVA (fecha_registro, hora_registro, monto_total,
                                 cliente_id, tipo_reserva, estado)
            VALUES (%s, %s, %s, %s, 'R', 1)
        """, (fecha_actual, hora_actual, total_general, cliente_id))
        reserva_id = cursor.lastrowid

        # =============================
        # 4️⃣ Crear room_service
        # =============================
        cursor.execute("""
            INSERT INTO ROOM_SERVICE (reserva_id, reserva_habitacion_id, fecha_pedido, hora_pedido)
            VALUES (%s, %s, %s, %s)
        """, (reserva_id, reserva_habitacion_id, fecha_actual, hora_actual))  # reserva_habitacion_id se puede cambiar luego
        room_service_id = cursor.lastrowid

        # =============================
        # 5️⃣ Detalle de productos
        # =============================
        for prod in productos:
            cursor.execute("""
                INSERT INTO ROOM_SERVICE_AMENIDAD (room_service_id, amenidad_id, cantidad)
                VALUES (%s, %s, %s)
            """, (room_service_id, prod['amenidad_id'], prod['cantidad']))


        # =============================
        # 6️⃣ Crear transacción
        # =============================
        cursor.execute("""
            INSERT INTO TRANSACCION (metodo_pago_id, fecha_pago, monto, estado, reserva_id)
            VALUES (%s, %s, %s, 1, %s)
        """, (metodo_pago_id, fecha_actual, total_general, reserva_id))
        transaccion_id = cursor.lastrowid

        # =============================
        # 7️⃣ Crear comprobante
        # =============================
        cursor.execute("SELECT IFNULL(MAX(comprobante_id), 0) + 1 FROM COMPROBANTE")
        nuevo_numero = cursor.fetchone()[0]
        numero_comprobante = f"{'B' if tipo_comprobante == 'B' else 'F'}001-{str(nuevo_numero).zfill(6)}"

        cursor.execute("""
            INSERT INTO COMPROBANTE (tipo_comprobante, numero_comprobante, fecha_comprobante,
                                     hora_comprobante, monto_total, transaccion_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            tipo_comprobante,
            numero_comprobante,
            fecha_actual,
            hora_actual,
            total_general,
            transaccion_id
        ))
        comprobante_id = cursor.lastrowid

        # =============================
        # 8️⃣ Detalle comprobante
        # =============================
        for prod in productos:
            cursor.execute("""
                INSERT INTO DETALLE_COMPROBANTE (
                    comprobante_id,
                    room_service_id,
                    amenidad_id,
                    reserva_habitacion_id,
                    evento_id,
                    habitacion_id,
                    cantidad,
                    precio_unitario,
                    subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                comprobante_id,
                room_service_id,                      
                prod['amenidad_id'],         # amenidad_id → del producto seleccionado
                reserva_habitacion_id,                           # reserva_habitacion_id → reemplázalo por el valor real
                None,                        # evento_id → no aplica
                None,                        # habitacion_id → no aplica
                prod['cantidad'],
                round(prod['subtotal'], 2),
                round(prod['total'], 2)
            ))

        # =============================
        # ✅ Confirmar transacción
        # =============================
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Pago procesado correctamente",
            "comprobante": numero_comprobante,
            "redirect_url": url_for("Index")
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        })
    finally:
        cursor.close()
        conn.close()

