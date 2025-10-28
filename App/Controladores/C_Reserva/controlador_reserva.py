# controllers/controlador_reserva.py
from datetime import date, datetime
from bd import get_connection
from flask import jsonify, request
import traceback
import App.Controladores.C_Cliente.controlador_cliente as controller_client 

# def guardar_reserva(data):
#     print("🟢 [DEBUG] Entrando a guardar_reserva()")

#     conn = None
#     cursor = None

#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         print("✅ Conexión obtenida correctamente")

#         cliente = data.get('cliente', {})
#         habitaciones = data.get('habitaciones', [])
#         fecha_ingreso = data.get("fecha_ingreso")
#         hora_ingreso = data.get("hora_ingreso")
#         total = data.get("total", 0)
#         fecha_salida = data.get("fecha_salida")
#         hora_salida = data.get("hora_salida")

#         if not cliente:
#             raise ValueError("Datos de cliente no enviados.")

#         # -----------------
#         #  Inserción / obtención cliente según tipo
#         # -----------------
#         tipo_cliente = cliente.get('tipo')  # 'natural' / 'juridica' o 'N'/'J'
#         tipo_lower = (tipo_cliente or "").lower()
        
#         if tipo_lower in ('natural', 'n'):
#             cliente_id = registrar_cliente_natural({
#                 'num_doc': cliente.get('num_doc') or cliente.get('dni'),
#                 'nombres': cliente.get('nombres'),
#                 'ape_paterno': cliente.get('ape_paterno'),
#                 'ape_materno': cliente.get('ape_materno'),
#                 'telefono': cliente.get('telefono'),
#                 'pais_id': cliente.get('pais_id'),
#                 'correo': cliente.get('correo')
#             }, cursor)
#         elif tipo_lower in ('juridica', 'juridico', 'j'):
#             cliente_id = registrar_cliente_juridico({
#                 'num_doc': cliente.get('num_doc') or cliente.get('ruc'),
#                 'razon_social': cliente.get('razon_social'),
#                 'direccion': cliente.get('direccion'),
#                 'tipo_empresa_id': cliente.get('tipo_empresa_id'),
#                 'telefono': cliente.get('telefono'),
#                 'pais_id': cliente.get('pais_id'),
#                 'correo': cliente.get('correo')
#             }, cursor)
#         else:
#             # si no llega tipo, asumir natural o lanzar error
#             raise ValueError("Tipo de cliente no reconocido. Use 'natural' o 'juridica'.")

#         print(f"✅ Cliente final ID: {cliente_id}")

#         # ==============================
#         #  Insertar RESERVA
#         # ==============================
#         sql_reserva = """
#             INSERT INTO RESERVA
#             (fecha_registro, hora_registro, cliente_id, monto_total, estado, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida)
#             VALUES (CURDATE(), CURTIME(), %s, %s, 1, %s, %s, %s, %s)
#         """
#         cursor.execute(sql_reserva, (cliente_id, total, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida))
#         reserva_id = cursor.lastrowid
#         print(f"✅ RESERVA insertada correctamente con ID: {reserva_id}")

#         # ==============================
#         #  Insertar RESERVA_HABITACION + HUESPEDES
#         # ==============================
#         for habitacion in habitaciones:
#             habitacion_id = habitacion.get('id_habitacion')
#             if not habitacion_id:
#                 raise ValueError("id_habitacion faltante en uno de los elementos 'habitaciones'.")

#             sql_res_hab = """
#                 INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id)
#                 VALUES (%s, %s)
#             """
#             cursor.execute(sql_res_hab, (reserva_id, habitacion_id))
#             reserva_hab_id = cursor.lastrowid
#             print(f"✅ RESERVA_HABITACION creada con ID: {reserva_hab_id} para habitacion {habitacion_id}")

#             # Huespedes (si vienen)
#             for huesped in habitacion.get('huespedes', []):
#                 # mapear campos potenciales
#                 doc = huesped.get('documento') or huesped.get('num_doc')
#                 nombre = huesped.get('nombre') or ''
#                 apellido = huesped.get('apellido') or huesped.get('ape_paterno') or ''
#                 ape_materno = huesped.get('ape_materno') or ''

#                 sql_huesped = """
#                     INSERT INTO HUESPED (num_doc, nombre, ape_paterno, ape_materno, id_cliente, reserva_habitacion_id)
#                     VALUES (%s, %s, %s, %s, %s, %s)
#                 """
#                 val_huesped = (doc, nombre, apellido, ape_materno, cliente_id, reserva_hab_id)
#                 cursor.execute(sql_huesped, val_huesped)
#                 print(f"✅ HUESPED insertado correctamente para habitación {habitacion_id}")

#         # commit y devolver id
#         conn.commit()
#         print("💾 Cambios guardados correctamente en la base de datos")
#         return reserva_id

#     except Exception as e:
#         print("❌ [ERROR en guardar_reserva]:", e)
#         if conn:
#             conn.rollback()
#         # Lanzamos la excepción para que la ruta maneje el jsonify y el status code
#         raise

#     finally:
#         if cursor: cursor.close()
#         if conn: conn.close()
#         print("🔚 Conexión cerrada correctamente")

def guardar_reserva(data):
    """
    Guardar reserva completa:
     - valida payload
     - busca o crea cliente (natural/juridico)
     - inserta reserva, reserva_habitacion y huespedes
     - devuelve reserva_id o None
    """
    connection = None
    try:
        connection = get_connection()
        print("✅ Conexión obtenida correctamente")
        with connection.cursor() as cursor:
            # validar payload
            if not isinstance(data, dict):
                raise ValueError("Payload inválido - se esperaba JSON/dict")

            cliente = data.get('cliente') or {}
            habitaciones = data.get('habitaciones') or []
            fecha_ingreso = data.get('fecha_ingreso')
            hora_ingreso = data.get('hora_ingreso')
            fecha_salida = data.get('fecha_salida')
            hora_salida = data.get('hora_salida')
            total = data.get('total', 0)

            print(f"📦 Datos del cliente recibidos: {cliente}")
            print(f"📦 Habitaciones recibidas: {len(habitaciones)}")

            # comprobar cliente mínimo
            num_doc = cliente.get('num_doc') or cliente.get('dni')
            if not num_doc:
                raise ValueError("Falta num_doc/dni en cliente")

            # normalizar pais_id y tipo en el dict que se enviará a registrar
            pais_id_raw = cliente.get('pais_id') or cliente.get('id_pais') or cliente.get('pais') or None
            try:
                pais_id = int(pais_id_raw) if pais_id_raw not in (None, '', []) else None
            except Exception:
                pais_id = None

            tipo_raw = cliente.get('tipo') or cliente.get('id_tipo_cliente') or 'N'
            tipo = 'N' if str(tipo_raw).lower().startswith('n') else 'J'

            # buscar cliente existente
            cliente_id = controller_client.buscar_cliente_por_documento(num_doc)
            if cliente_id:
                print(f"👤 Cliente existente id={cliente_id}")
            else:
                # construir dict consistente para la función de registro
                if tipo == 'N':
                    c = {
                        'num_doc': num_doc,
                        'nombres': cliente.get('nombres'),
                        'ape_paterno': cliente.get('ape_paterno'),
                        'ape_materno': cliente.get('ape_materno'),
                        'telefono': cliente.get('telefono'),
                        'pais_id': pais_id,
                        'tipo': 'N',
                        'tipo_doc_id':cliente.get('tipo_doc_id')
                    }
                    cliente_id = registrar_cliente_natural(cursor, c)
                    if not cliente_id:
                        raise ValueError("No se pudo insertar cliente natural (ver logs).")
                else:
                    c = {
                        'num_doc': num_doc,
                        'ruc': num_doc,
                        'razon_social': cliente.get('razon_social') or cliente.get('nombres'),
                        'telefono': cliente.get('telefono'),
                        'pais_id': pais_id,
                        'tipo': 'J',
                        'direccion': cliente.get('direccion'),
                        'tipoemp_id': cliente.get('tipo_emp_id'),
                        'tipo_doc_id': 2
                    }
                    cliente_id = registrar_cliente_juridico(cursor, c)
                    if not cliente_id:
                        raise ValueError("No se pudo insertar cliente jurídico (ver logs).")

            # insertar reserva
            try:
                total_val = float(total) if total not in (None, '') else 0.0
            except Exception:
                total_val = 0.0

            cursor.execute("""
                INSERT INTO RESERVA (fecha_registro, hora_registro, cliente_id, monto_total, estado,
                                     fecha_ingreso, hora_ingreso, fecha_salida, hora_salida,tipo_reserva)
                VALUES (CURDATE(), CURTIME(), %s, %s, 1, %s, %s, %s, %s, 'H' )
            """, (cliente_id, total_val, fecha_ingreso, hora_ingreso, fecha_salida, hora_salida))

            reserva_id = cursor.lastrowid
            print(f"✅ RESERVA insertada correctamente con ID: {reserva_id}")

            # insertar reserva_habitacion y huespedes
            for habitacion in habitaciones:
                if not isinstance(habitacion, dict):
                    raise ValueError("Cada habitacion debe ser un objeto/dict")

                habitacion_id = habitacion.get('id_habitacion') or habitacion.get('id') or None
                if not habitacion_id:
                    raise ValueError("Falta id_habitacion en una entrada de 'habitaciones'")

                cursor.execute("INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id) VALUES (%s, %s)",
                               (reserva_id, habitacion_id))
                reserva_hab_id = cursor.lastrowid
                print(f"  -> RESERVA_HABITACION creada (id: {reserva_hab_id}) para habitacion {habitacion_id}")

                for huesped in habitacion.get('huespedes', []):
                    if not isinstance(huesped, dict):
                        continue
                    doc = huesped.get('documento') or huesped.get('num_doc') or None
                    nombre = huesped.get('nombre') or huesped.get('nombres') or ''
                    apellido = huesped.get('apellido') or huesped.get('ape_paterno') or ''
                    ape_materno = huesped.get('ape_materno') or ''

                    cursor.execute("""
                        INSERT INTO HUESPED (num_doc, nombre, ape_paterno, ape_materno, id_cliente, reserva_habitacion_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (doc, nombre, apellido, ape_materno, cliente_id, reserva_hab_id))
                    print(f"    -> HUESPED insertado para habitación {habitacion_id}")

            # commit y cerrar
            connection.commit()
            print("💾 Cambios guardados correctamente en la base de datos")
            return reserva_id

    except Exception as e:
        print(f"❌ [ERROR en guardar_reserva]: {e}")
        traceback.print_exc()
        try:
            if connection:
                connection.rollback()
        except Exception:
            pass
        return None
    finally:
        if connection:
            connection.close()
            print("🔚 Conexión cerrada correctamente")

def registrar_cliente_natural(cursor, cliente):
    """
    Registra un cliente persona natural (acepta dict, tupla o Row-like).
    Retorna lastrowid si se inserta correctamente, o None.
    """
    try:
        if not cliente:
            print("⚠️ [registrar_cliente_natural] cliente vacío")
            return None

        # Normalizar a dict (si viene tupla/row)
        if isinstance(cliente, dict):
            data = cliente
        else:
            # intentar convertir Row/tupla a dict con keys comunes
            try:
                if hasattr(cliente, "_mapping"):
                    data = dict(cliente._mapping)
                else:
                    # si es tupla/lista asumimos orden (ajusta si tu orden es distinto)
                    keys = ['num_doc', 'nombres', 'ape_paterno', 'ape_materno', 'telefono', 'pais_id', 'correo', 'tipo' ,'tipo_doc_id']
                    data = {k: (cliente[i] if i < len(cliente) else None) for i, k in enumerate(keys)}
            except Exception as e:
                print(f"⚠️ [registrar_cliente_natural] no pude normalizar entrada: {e}")
                return None

        # Extraer campos (aceptar alias para compatibilidad)
        num_doc = data.get('num_doc') or data.get('dni') or None
        nombres = data.get('nombres') or data.get('nombre') or None
        ape_paterno = data.get('ape_paterno') or data.get('apellido') or None
        ape_materno = data.get('ape_materno') or data.get('apeMaterno') or None
        telefono = data.get('telefono') or data.get('movil') or None
        correo = data.get('correo') or data.get('email') or None
        tipo_doc_id = data.get('tipo_doc_id') or None

        # Normalizar pais_id (acepta 'pais_id' o 'id_pais' o 'pais')
        pais_id_raw = data.get('pais_id') or data.get('id_pais') or data.get('pais') or None
        try:
            pais_id = int(pais_id_raw) if pais_id_raw not in (None, '', []) else None
        except Exception:
            pais_id = None

        # Normalizar tipo cliente (guardar 'N' o 'J')
        tipo_cliente = data.get('tipo') or data.get('id_tipo_cliente') or 'N'
        if isinstance(tipo_cliente, str):
            if tipo_cliente.lower().startswith('n'):
                tipo_cliente = 'N'
            elif tipo_cliente.lower().startswith('j'):
                tipo_cliente = 'J'
            else:
                tipo_cliente = 'N'
        else:
            tipo_cliente = 'N'

        # Validaciones mínimas
        if not num_doc or not nombres:
            print("⚠️ [registrar_cliente_natural] faltan datos obligatorios (num_doc o nombres).")
            print("DEBUG data:", data)
            return None

        if pais_id is None:
            print("⚠️ [registrar_cliente_natural] pais_id es None. data:", data)
            # Si quieres asignar por defecto: pais_id = 1
            return None

        # Preparar tuple de insert — ajustado a tu esquema CLIENTE
        # Tabla CLIENTE (según tu DDL): direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, id_tipoemp, ape_paterno, ape_materno, nombres, razon_social
        # Vamos a insertar sólo los campos esenciales (otros NULL)
        params = (num_doc, nombres, ape_paterno, ape_materno, telefono, pais_id, tipo_cliente,tipo_doc_id)
        print("DEBUG [registrar_cliente_natural] params a insertar (num_doc,nombres,ape_p,ape_m,pais_id,tipo):", params)

        # Inserción: usar columnas explícitas para evitar desorden
        cursor.execute("""
            INSERT INTO CLIENTE (num_doc, nombres, ape_paterno, ape_materno, telefono, id_pais, id_tipo_cliente, tipo_doc_id,f_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s ,CURDATE())
        """, params)

        last_id = cursor.lastrowid
        print(f"✅ Cliente persona natural registrado correctamente. id={last_id}")
        return last_id

    except Exception as e:
        print(f"❌ [ERROR en registrar_cliente_natural]: {e}")
        traceback.print_exc()
        return None

def registrar_cliente_juridico(cursor, cliente):
    """
    Registra un cliente persona jurídica (acepta dict/tupla/row).
    Retorna lastrowid o None.
    """
    try:
        if not cliente:
            return None

        if isinstance(cliente, dict):
            data = cliente
        else:
            try:
                if hasattr(cliente, "_mapping"):
                    data = dict(cliente._mapping)
                else:
                    keys = ['ruc', 'razon_social', 'telefono', 'pais_id', 'correo', 'tipo']
                    data = {k: (cliente[i] if i < len(cliente) else None) for i, k in enumerate(keys)}
            except Exception as e:
                print(f"⚠️ [registrar_cliente_juridico] no pude normalizar entrada: {e}")
                return None

        ruc = data.get('ruc') or data.get('num_doc') or None
        razon_social = data.get('razon_social') or data.get('razon') or data.get('nombre') or None
        telefono = data.get('telefono') or None
        pais_id_raw = data.get('pais_id') or data.get('id_pais') or None
        direccion = data.get('direccion') or None
        tipoemp_id = data.get('tipoemp_id') or None
        tipo_doc_id = data.get('tipo_doc_id') or None
        try:
            pais_id = int(pais_id_raw) if pais_id_raw not in (None, '', []) else None
        except Exception:
            pais_id = None

        tipo_cliente = data.get('tipo') or data.get('id_tipo_cliente') or 'J'
        if isinstance(tipo_cliente, str):
            if tipo_cliente.lower().startswith('n'):
                tipo_cliente = 'N'
            elif tipo_cliente.lower().startswith('j'):
                tipo_cliente = 'J'
            else:
                tipo_cliente = 'J'
        else:
            tipo_cliente = 'J'

        if not ruc or not razon_social:
            print("⚠️ [registrar_cliente_juridico] faltan ruc o razon_social. data:", data)
            return None

        if pais_id is None:
            print("⚠️ [registrar_cliente_juridico] pais_id es None. data:", data)
            return None

        params = (ruc, razon_social,direccion, telefono, pais_id, tipo_cliente,tipoemp_id,tipo_doc_id)
        print("DEBUG [registrar_cliente_juridico] params a insertar (ruc,razon,telefono,pais_id,tipo):", params)

        # Insertar: guardamos razon_social en campo 'nombres' para unificar tabla CLIENTE
        cursor.execute("""
            INSERT INTO CLIENTE (num_doc, razon_social, direccion, telefono, id_pais, id_tipo_cliente, tipoemp_id, tipo_doc_id, f_registro)
            VALUES (%s, %s, %s, %s, %s, %s , %s, %s ,CURDATE())
        """, (ruc, razon_social, direccion, telefono, pais_id, tipo_cliente,))

        last_id = cursor.lastrowid
        print(f"✅ Cliente persona jurídica registrado correctamente. id={last_id}")
        return last_id

    except Exception as e:
        print(f"❌ [ERROR en registrar_cliente_juridico]: {e}")
        traceback.print_exc()
        return None
