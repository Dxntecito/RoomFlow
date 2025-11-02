# controllers/controlador_reserva.py
from datetime import date, datetime
from bd import get_connection
from flask import jsonify, request
import traceback
import App.Controladores.C_Cliente.controlador_cliente as controller_client 
from App.Controladores.C_Cliente.controlador_cliente import (guardar_cliente, buscar_cliente_natural, buscar_cliente_juridico, registrar_cliente_natural,registrar_cliente_juridico)
def guardar_reserva(data):
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
                    fecha_ingreso, hora_ingreso, fecha_salida, hora_salida, tipo_reserva
                ) VALUES (CURDATE(), CURTIME(), %s, %s, 1, %s, %s, %s, %s, 'H')
            """, (cliente_id, total_val, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida))

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

