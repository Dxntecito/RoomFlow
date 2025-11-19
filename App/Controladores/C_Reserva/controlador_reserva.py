# controllers/controlador_reserva.py
from datetime import date, datetime, time, timedelta
from bd import get_connection
from flask import jsonify, request
import traceback
import App.Controladores.C_Cliente.controlador_cliente as controller_client 
from App.Controladores.C_Cliente.controlador_cliente import (guardar_cliente, buscar_cliente_natural, buscar_cliente_juridico, registrar_cliente_natural,registrar_cliente_juridico)
def guardar_reserva_s_usuario(data):
    """
    Guarda una reserva completa:
      - Valida el payload
      - Busca o crea cliente (natural/jurídico)
      - Inserta reserva, habitaciones y huéspedes
      - Devuelve reserva_id si todo fue exitoso
    """
    connection = None
    reserva_id = None  # 👈 inicializamos aquí

    try:
        connection = get_connection()
        print("✅ Conexión obtenida correctamente")

        with connection.cursor() as cursor:
            # --- Validación del payload ---
            if not isinstance(data, dict):
                raise ValueError("Payload inválido: se esperaba un objeto JSON/dict")

            cliente = data.get('cliente', {})
            habitaciones = data.get('habitaciones', [])
            fecha_ingreso = data.get('fecha_ingreso')
            hora_ingreso = data.get('hora_ingreso')
            fecha_salida = data.get('fecha_salida')
            hora_salida = data.get('hora_salida')
            total = data.get('total', 0)
            motivo_viaje = (data.get('motivo_viaje') or '').strip() or "Sin especificar"
            servicios = data.get('servicios', [])

            print(f"📦 Cliente recibido: {cliente}")
            print(f"📦 Habitaciones recibidas: {len(habitaciones)}")

            # --- Buscar o crear cliente ---
            num_doc = cliente.get('num_doc') or cliente.get('dni')
            if not num_doc:
                raise ValueError("Falta num_doc o dni del cliente")

            pais_id_raw = cliente.get('pais_id') or cliente.get('id_pais') or cliente.get('pais')
            try:
                pais_id = int(pais_id_raw) if pais_id_raw not in (None, '', []) else None
            except Exception:
                pais_id = None

            tipo_raw = cliente.get('tipo') or cliente.get('id_tipo_cliente') or 'N'
            tipo = 'N' if str(tipo_raw).lower().startswith('n') else 'J'

            cliente_id = controller_client.buscar_cliente_por_documento(num_doc)
            if cliente_id:
                print(f"👤 Cliente existente id={cliente_id}")
            else:
                if tipo == 'N':
                    c = {
                        'num_doc': num_doc,
                        'nombres': cliente.get('nombres'),
                        'ape_paterno': cliente.get('ape_paterno'),
                        'ape_materno': cliente.get('ape_materno'),
                        'telefono': cliente.get('telefono'),
                        'pais_id': pais_id,
                        'tipo': 'N',
                        'tipo_doc_id': cliente.get('tipo_doc_id')
                    }
                    cliente_id = registrar_cliente_natural(cursor, c)
                else:
                    c = {
                        'num_doc': num_doc,
                        'ruc': num_doc,
                        'razon_social': cliente.get('razon_social') or cliente.get('nombres'),
                        'telefono': cliente.get('telefono'),
                        'pais_id': pais_id,
                        'tipo': 'J',
                        'direccion': cliente.get('direccion'),
                        'tipoemp_id': cliente.get('tipoemp_id'),
                        'tipo_doc_id': 2
                    }
                    cliente_id = registrar_cliente_juridico(cursor, c)

                if not cliente_id:
                    raise ValueError("❌ No se pudo registrar cliente")

            # --- Insertar RESERVA ---
            total_val = float(total) if total not in (None, '') else 0.0
            cursor.execute("""
                INSERT INTO RESERVA (
                    fecha_registro, hora_registro, cliente_id, monto_total, estado,
                    fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, tipo_reserva, motivo
                ) VALUES (CURDATE(), CURTIME(), %s, %s, 1, %s, %s, %s, %s, 'H', %s)
            """, (cliente_id, total_val, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, motivo_viaje))

            reserva_id = cursor.lastrowid  # 👈 obtenemos el ID de la reserva
            print(f"✅ RESERVA insertada con ID: {reserva_id}")

            # --- Insertar habitaciones y huéspedes ---
            for habitacion in habitaciones:
                habitacion_id = habitacion.get('id_habitacion') or habitacion.get('id')
                if not habitacion_id:
                    raise ValueError("Falta id_habitacion en habitaciones")

                cursor.execute(
                    "INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id) VALUES (%s, %s)",
                    (reserva_id, habitacion_id)
                )
                reserva_hab_id = cursor.lastrowid
                print(f"  -> RESERVA_HABITACION creada ID={reserva_hab_id}")

                for huesped in habitacion.get('huespedes', []):
                    doc = huesped.get('documento') or huesped.get('num_doc')
                    nombre = huesped.get('nombre') or huesped.get('nombres', '')
                    ape_pat = huesped.get('apellido') or huesped.get('ape_paterno', '')
                    ape_mat = huesped.get('ape_materno', '')

                    cursor.execute("""
                        INSERT INTO HUESPED (num_doc, nombre, ape_paterno, ape_materno, id_cliente, reserva_habitacion_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (doc, nombre, ape_pat, ape_mat, cliente_id, reserva_hab_id))
                    print(f"    -> HUESPED insertado para hab {habitacion_id}")

            for servicio in servicios:
                servicio_id = servicio.get('servicio_id') or servicio.get('id')
                if not servicio_id:
                    continue
                cantidad = servicio.get('cantidad') or 1
                try:
                    cantidad = int(cantidad)
                except Exception:
                    cantidad = 1
                precio_unitario = servicio.get('precio_unitario') or servicio.get('precio') or 0
                try:
                    precio_unitario = float(precio_unitario)
                except Exception:
                    precio_unitario = 0.0
                cursor.execute(
                    """
                    INSERT INTO RESERVA_SERVICIO (reserva_id, servicio_id, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (reserva_id, servicio_id, cantidad, precio_unitario)
                )
                print(f"  -> SERVICIO agregado ID={servicio_id}")

            # --- Guardar cambios ---
            connection.commit()
            print("💾 Cambios confirmados correctamente")
            return reserva_id  # 👈 devolvemos el id sí o sí

    except Exception as e:
        print(f"❌ [ERROR guardar_reserva]: {e}")
        traceback.print_exc()
        if connection:
            connection.rollback()
        return None

    finally:
        if connection:
            connection.close()
            print("🔚 Conexión cerrada correctamente")

def guardar_reserva_c_usuario(data):
    """
    Guarda una reserva completa:
      - Valida el payload
      - Inserta reserva, habitaciones y huéspedes
      - Devuelve reserva_id si todo fue exitoso
    """
    connection = None
    reserva_id = None  # 👈 inicializamos aquí

    try:
        connection = get_connection()
        print("✅ Conexión obtenida correctamente")

        with connection.cursor() as cursor:
            # --- Validación del payload ---
            if not isinstance(data, dict):
                raise ValueError("Payload inválido: se esperaba un objeto JSON/dict")

            usuario_id =data.get('usuario_id')
            habitaciones = data.get('habitaciones', [])
            fecha_ingreso = data.get('fecha_ingreso')
            hora_ingreso = data.get('hora_ingreso')
            fecha_salida = data.get('fecha_salida')
            hora_salida = data.get('hora_salida')
            total = data.get('total', 0)
            motivo_viaje = (data.get('motivo_viaje') or '').strip() or "Sin especificar"
            servicios = data.get('servicios', [])
            print(f"📦 Habitaciones recibidas: {len(habitaciones)}")

            cliente_id = controller_client.buscar_cliente_por_idusuario(usuario_id)
            print(f"Cliente_id encontrado {cliente_id}")
            # --- Insertar RESERVA ---
            total_val = float(total) if total not in (None, '') else 0.0
            cursor.execute("""
                INSERT INTO RESERVA (
                    fecha_registro, hora_registro, cliente_id, monto_total, estado,
                    fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, tipo_reserva, motivo
                ) VALUES (CURDATE(), CURTIME(), %s, %s, 1, %s, %s, %s, %s, 'H', %s)
            """, (cliente_id, total_val, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, motivo_viaje))

            reserva_id = cursor.lastrowid  # 👈 obtenemos el ID de la reserva
            print(f"✅ RESERVA insertada con ID: {reserva_id}")

            # --- Insertar habitaciones y huéspedes ---
            for habitacion in habitaciones:
                habitacion_id = habitacion.get('id_habitacion') or habitacion.get('id')
                if not habitacion_id:
                    raise ValueError("Falta id_habitacion en habitaciones")

                cursor.execute(
                    "INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id) VALUES (%s, %s)",
                    (reserva_id, habitacion_id)
                )
                reserva_hab_id = cursor.lastrowid
                print(f"  -> RESERVA_HABITACION creada ID={reserva_hab_id}")

                for huesped in habitacion.get('huespedes', []):
                    doc = huesped.get('documento') or huesped.get('num_doc')
                    nombre = huesped.get('nombre') or huesped.get('nombres', '')
                    ape_pat = huesped.get('apellido') or huesped.get('ape_paterno', '')
                    ape_mat = huesped.get('ape_materno', '')

                    cursor.execute("""
                        INSERT INTO HUESPED (num_doc, nombre, ape_paterno, ape_materno, id_cliente, reserva_habitacion_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (doc, nombre, ape_pat, ape_mat, cliente_id, reserva_hab_id))
                    print(f"    -> HUESPED insertado para hab {habitacion_id}")

            for servicio in servicios:
                servicio_id = servicio.get('servicio_id') or servicio.get('id')
                if not servicio_id:
                    continue
                cantidad = servicio.get('cantidad') or 1
                try:
                    cantidad = int(cantidad)
                except Exception:
                    cantidad = 1
                precio_unitario = servicio.get('precio_unitario') or servicio.get('precio') or 0
                try:
                    precio_unitario = float(precio_unitario)
                except Exception:
                    precio_unitario = 0.0
                cursor.execute(
                    """
                    INSERT INTO RESERVA_SERVICIO (reserva_id, servicio_id, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (reserva_id, servicio_id, cantidad, precio_unitario)
                )
                print(f"  -> SERVICIO agregado ID={servicio_id}")

            # --- Guardar cambios ---
            connection.commit()
            print("💾 Cambios confirmados correctamente")
            return reserva_id  # 👈 devolvemos el id sí o sí

    except Exception as e:
        print(f"❌ [ERROR guardar_reserva]: {e}")
        traceback.print_exc()
        if connection:
            connection.rollback()
        return None

    finally:
        if connection:
            connection.close()
            print("🔚 Conexión cerrada correctamente")


def obtener_estado_validado(reserva_id):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT validado FROM RESERVA WHERE reserva_id = %s",
                (reserva_id,)
            )
            row = cursor.fetchone()
            if row:
                return str(row[0]).strip() if row[0] is not None else None
            return None
    finally:
        if connection:
            connection.close()


def listar_reservas_pendientes_validacion():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.reserva_id,
                    r.fecha_registro,
                    r.hora_registro,
                    r.monto_total,
                    r.fecha_ingreso,
                    r.fecha_salida,
                    r.validado,
                    c.nombres,
                    c.ape_paterno,
                    c.ape_materno,
                    c.num_doc
                FROM RESERVA r
                LEFT JOIN CLIENTE c ON c.cliente_id = r.cliente_id
                WHERE r.validado = '0' OR r.validado IS NULL
                ORDER BY r.fecha_registro DESC, r.hora_registro DESC
            """)
            rows = cursor.fetchall()
            pendientes = []
            for row in rows:
                fecha_registro = _format_date(row[1])
                hora_registro = _format_time(row[2])
                fecha_ingreso = _format_date(row[4])
                fecha_salida = _format_date(row[5])
                pendientes.append({
                    "reserva_id": row[0],
                    "fecha_registro": fecha_registro,
                    "hora_registro": hora_registro,
                    "monto_total": float(row[3]) if row[3] is not None else 0.0,
                    "fecha_ingreso": fecha_ingreso,
                    "fecha_salida": fecha_salida,
                    "validado": str(row[6]).strip() if row[6] is not None else "0",
                    "cliente": " ".join(filter(None, [row[7], row[8], row[9]])).strip() or "Sin nombre",
                    "documento": row[10]
                })
            return pendientes
    finally:
        if connection:
            connection.close()


def actualizar_validado_reserva(reserva_id, valor="1"):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE RESERVA SET validado = %s WHERE reserva_id = %s",
                (valor, reserva_id)
            )
        connection.commit()
        return True
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Error actualizando validado reserva {reserva_id}: {e}")
        return False
    finally:
        if connection:
            connection.close()


def eliminar_reserva_completa(reserva_id):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM HUESPED
                WHERE reserva_habitacion_id IN (
                    SELECT reserva_habitacion_id FROM RESERVA_HABITACION WHERE reserva_id = %s
                )
            """, (reserva_id,))
            cursor.execute("DELETE FROM RESERVA_HABITACION WHERE reserva_id = %s", (reserva_id,))
            cursor.execute("DELETE FROM RESERVA_SERVICIO WHERE reserva_id = %s", (reserva_id,))
            cursor.execute("DELETE FROM RESERVA WHERE reserva_id = %s", (reserva_id,))
        connection.commit()
        return True
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Error eliminando reserva {reserva_id}: {e}")
        return False
    finally:
        if connection:
            connection.close()


def _format_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _format_time(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%H:%M:%S")
    if isinstance(value, time):
        return value.strftime("%H:%M:%S")
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return str(value)


def count_reservas():
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM RESERVA")
            row = cursor.fetchone()
            return row[0] if row else 0
    finally:
        if connection:
            connection.close()


def get_reservas(limit=20, offset=0):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.reserva_id,
                    r.fecha_registro,
                    r.hora_registro,
                    r.fecha_ingreso,
                    r.hora_ingreso,
                    r.fecha_salida,
                    r.hora_salida,
                    r.monto_total,
                    r.estado,
                    r.motivo,
                    c.nombres,
                    c.ape_paterno,
                    c.ape_materno,
                    c.num_doc
                FROM RESERVA r
                LEFT JOIN CLIENTE c ON c.cliente_id = r.cliente_id
                ORDER BY r.fecha_registro DESC, r.hora_registro DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cursor.fetchall()
            reservas = []
            for row in rows:
                reservas.append({
                    "id": row[0],
                    "fecha_registro": _format_date(row[1]),
                    "hora_registro": _format_time(row[2]),
                    "fecha_ingreso": _format_date(row[3]),
                    "hora_ingreso": _format_time(row[4]),
                    "fecha_salida": _format_date(row[5]),
                    "hora_salida": _format_time(row[6]),
                    "monto_total": float(row[7]) if row[7] is not None else 0.0,
                    "estado": row[8],
                    "motivo": row[9],
                    "cliente": " ".join(filter(None, [row[10], row[11], row[12]])).strip() or "Sin nombre",
                    "documento": row[13]
                })
            return reservas
    finally:
        if connection:
            connection.close()


def order_reservas(field="reserva_id", order="desc"):
    valid_fields = {
        "reserva_id": "r.reserva_id",
        "fecha_ingreso": "r.fecha_ingreso",
        "fecha_salida": "r.fecha_salida",
        "monto_total": "r.monto_total",
        "estado": "r.estado"
    }
    field_db = valid_fields.get(field, "r.reserva_id")
    order_db = "ASC" if str(order).lower() == "asc" else "DESC"

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    r.reserva_id,
                    r.fecha_registro,
                    r.hora_registro,
                    r.fecha_ingreso,
                    r.hora_ingreso,
                    r.fecha_salida,
                    r.hora_salida,
                    r.monto_total,
                    r.estado,
                    r.motivo,
                    c.nombres,
                    c.ape_paterno,
                    c.ape_materno,
                    c.num_doc
                FROM RESERVA r
                LEFT JOIN CLIENTE c ON c.cliente_id = r.cliente_id
                ORDER BY {field_db} {order_db}
            """)
            rows = cursor.fetchall()
            reservas = []
            for row in rows:
                reservas.append({
                    "id": row[0],
                    "fecha_registro": _format_date(row[1]),
                    "hora_registro": _format_time(row[2]),
                    "fecha_ingreso": _format_date(row[3]),
                    "hora_ingreso": _format_time(row[4]),
                    "fecha_salida": _format_date(row[5]),
                    "hora_salida": _format_time(row[6]),
                    "monto_total": float(row[7]) if row[7] is not None else 0.0,
                    "estado": row[8],
                    "motivo": row[9],
                    "cliente": " ".join(filter(None, [row[10], row[11], row[12]])).strip() or "Sin nombre",
                    "documento": row[13]
                })
            return reservas
    finally:
        if connection:
            connection.close()


def search_reservas(query):
    wildcard = f"%{query}%"
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.reserva_id,
                    r.fecha_registro,
                    r.hora_registro,
                    r.fecha_ingreso,
                    r.hora_ingreso,
                    r.fecha_salida,
                    r.hora_salida,
                    r.monto_total,
                    r.estado,
                    r.motivo,
                    c.nombres,
                    c.ape_paterno,
                    c.ape_materno,
                    c.num_doc
                FROM RESERVA r
                LEFT JOIN CLIENTE c ON c.cliente_id = r.cliente_id
                WHERE c.nombres LIKE %s
                   OR c.ape_paterno LIKE %s
                   OR c.ape_materno LIKE %s
                   OR c.num_doc LIKE %s
                   OR r.reserva_id LIKE %s
            """, (wildcard, wildcard, wildcard, wildcard, wildcard))
            rows = cursor.fetchall()
            reservas = []
            for row in rows:
                reservas.append({
                    "id": row[0],
                    "fecha_registro": _format_date(row[1]),
                    "hora_registro": _format_time(row[2]),
                    "fecha_ingreso": _format_date(row[3]),
                    "hora_ingreso": _format_time(row[4]),
                    "fecha_salida": _format_date(row[5]),
                    "hora_salida": _format_time(row[6]),
                    "monto_total": float(row[7]) if row[7] is not None else 0.0,
                    "estado": row[8],
                    "motivo": row[9],
                    "cliente": " ".join(filter(None, [row[10], row[11], row[12]])).strip() or "Sin nombre",
                    "documento": row[13]
                })
            return reservas
    finally:
        if connection:
            connection.close()


def get_reserva_detalle(reserva_id):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.reserva_id,
                    r.fecha_registro,
                    r.hora_registro,
                    r.fecha_ingreso,
                    r.hora_ingreso,
                    r.fecha_salida,
                    r.hora_salida,
                    r.monto_total,
                    r.estado,
                    r.motivo,
                    c.cliente_id,
                    c.nombres,
                    c.ape_paterno,
                    c.ape_materno,
                    c.num_doc
                FROM RESERVA r
                LEFT JOIN CLIENTE c ON c.cliente_id = r.cliente_id
                WHERE r.reserva_id = %s
            """, (reserva_id,))
            row = cursor.fetchone()
            if not row:
                return None

            detalle = {
                "id": row[0],
                "fecha_registro": _format_date(row[1]),
                "hora_registro": _format_time(row[2]),
                "fecha_ingreso": _format_date(row[3]),
                "hora_ingreso": _format_time(row[4]),
                "fecha_salida": _format_date(row[5]),
                "hora_salida": _format_time(row[6]),
                "monto_total": float(row[7]) if row[7] is not None else 0.0,
                "estado": row[8],
                "motivo": row[9],
                "cliente_id": row[10],
                "cliente": " ".join(filter(None, [row[11], row[12], row[13]])).strip() or "Sin nombre",
                "documento": row[14]
            }

            cursor.execute("""
                SELECT
                    rh.reserva_habitacion_id,
                    h.habitacion_id,
                    h.numero,
                    c.nombre_categoria,
                    p.numero AS numero_piso
                FROM RESERVA_HABITACION rh
                LEFT JOIN HABITACION h ON h.habitacion_id = rh.habitacion_id
                LEFT JOIN CATEGORIA c ON c.categoria_id = h.id_categoria
                LEFT JOIN PISO p ON p.piso_id = h.piso_id
                WHERE rh.reserva_id = %s
            """, (reserva_id,))
            detalle["habitaciones"] = [
                {
                    "reserva_habitacion_id": hab[0],
                    "habitacion_id": hab[1],
                    "numero": hab[2],
                    "categoria": hab[3],
                    "piso": hab[4]
                }
                for hab in cursor.fetchall()
            ]

            cursor.execute("""
                SELECT
                    rs.reserva_servicio_id,
                    rs.servicio_id,
                    s.nombre_servicio,
                    rs.cantidad,
                    rs.precio_unitario
                FROM RESERVA_SERVICIO rs
                LEFT JOIN SERVICIO s ON s.servicio_id = rs.servicio_id
                WHERE rs.reserva_id = %s
            """, (reserva_id,))
            detalle["servicios"] = [
                {
                    "reserva_servicio_id": serv[0],
                    "servicio_id": serv[1],
                    "nombre": serv[2],
                    "cantidad": serv[3],
                    "precio_unitario": float(serv[4]) if serv[4] is not None else 0.0
                }
                for serv in cursor.fetchall()
            ]

            return detalle
    finally:
        if connection:
            connection.close()


def update_reserva(reserva_id, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, estado, monto_total, motivo, servicios):
    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE RESERVA
                SET fecha_ingreso = %s,
                    hora_ingreso = %s,
                    fecha_salida = %s,
                    hora_salida = %s,
                    estado = %s,
                    monto_total = %s,
                    motivo = %s
                WHERE reserva_id = %s
            """, (fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, estado, monto_total, motivo, reserva_id))

            cursor.execute("DELETE FROM RESERVA_SERVICIO WHERE reserva_id = %s", (reserva_id,))

            for servicio in servicios:
                servicio_id = servicio.get("servicio_id")
                if not servicio_id:
                    continue
                cantidad = servicio.get("cantidad") or 1
                precio_unitario = servicio.get("precio_unitario") or 0
                cursor.execute("""
                    INSERT INTO RESERVA_SERVICIO (reserva_id, servicio_id, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (reserva_id, servicio_id, cantidad, precio_unitario))

        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()

