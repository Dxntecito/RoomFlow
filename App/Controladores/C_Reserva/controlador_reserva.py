# controllers/controlador_reserva.py
from datetime import date, datetime
from bd import get_connection
from flask import jsonify, request
import traceback

def guardar_reserva(data):
    print("🟢 [DEBUG] Entrando a guardar_reserva()")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        print("✅ Conexión obtenida correctamente")

        cliente = data.get('cliente', {})
        habitaciones = data.get('habitaciones', [])
        fecha_ingreso = data.get("fecha_ingreso")
        hora_ingreso = data.get("hora_ingreso")
        total = data.get("total")
        fecha_salida = data.get("fecha_salida")
        hora_salida = data.get("hora_salida")

        print(f"📦 Datos del cliente recibidos: {cliente}")
        print(f"📦 Habitaciones recibidas: {len(habitaciones)}")

        # ==============================
        # 1️⃣ Insertar CLIENTE
        # ==============================
        sql_cliente = """
            INSERT INTO CLIENTE (nombres, num_doc, telefono, f_registro, id_tipo_cliente, id_pais)
            VALUES (%s, %s, %s, CURDATE(), %s, %s)
        """
        val_cliente = (
            cliente.get('nombre'),
            cliente.get('dni'),
            cliente.get('telefono'),
            'N',  # Natural
            1     # país por defecto
        )

        print("📝 Ejecutando SQL CLIENTE:", sql_cliente)
        cursor.execute(sql_cliente, val_cliente)
        cliente_id = cursor.lastrowid
        print(f"✅ CLIENTE insertado correctamente con ID: {cliente_id}")

        # ==============================
        # 2️⃣ Insertar RESERVA
        # ==============================

        sql_reserva = """
        INSERT INTO RESERVA (fecha_registro, hora_registro, cliente_id, monto_total, estado,
                                 fecha_ingreso, hora_ingreso, fecha_salida, hora_salida)
            VALUES (CURDATE(), CURTIME(), %s, %s, 1, %s, %s, %s, %s)
        """
        print("📝 Ejecutando SQL RESERVA:", sql_reserva)
        cursor.execute(sql_reserva, (cliente_id,total, fecha_ingreso,hora_ingreso,fecha_salida,hora_salida))
        reserva_id = cursor.lastrowid
        print(f"✅ RESERVA insertada correctamente con ID: {reserva_id}")

        # ==============================
        # 3️⃣ Insertar RESERVA_HABITACION + HUESPEDES
        # ==============================
        for habitacion in habitaciones:
            habitacion_id = habitacion.get('id_habitacion')
            print(f"➡️ Procesando habitación ID: {habitacion_id}")

            sql_res_hab = """
                INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id)
                VALUES (%s, %s)
            """
            cursor.execute(sql_res_hab, (reserva_id, habitacion_id))
            reserva_hab_id = cursor.lastrowid
            print(f"✅ RESERVA_HABITACION creada con ID: {reserva_hab_id}")

            for huesped in habitacion.get('huespedes', []):
                print(f"👤 Insertando huésped: {huesped}")

                sql_huesped = """
                    INSERT INTO HUESPED (num_doc, nombre, ape_paterno, ape_materno, id_cliente, reserva_habitacion_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                val_huesped = (
                    huesped.get('documento'),
                    huesped.get('nombre'),
                    huesped.get('apellido', ''),
                    '',
                    cliente_id,
                    reserva_hab_id
                )

                cursor.execute(sql_huesped, val_huesped)
                print(f"✅ HUESPED insertado correctamente en habitación {habitacion_id}")

        conn.commit()
        print("💾 Cambios guardados correctamente en la base de datos")
        return reserva_id

    except Exception as e:
        print("❌ [ERROR en guardar_reserva]:", e)
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()
        print("🔚 Conexión cerrada correctamente")
