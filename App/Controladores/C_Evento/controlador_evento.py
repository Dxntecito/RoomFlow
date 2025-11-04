from bd import get_connection
from datetime import datetime
from flask import request, jsonify



def get_tipos_eventos():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento FROM TIPO_EVENTO WHERE estado = 1
        """)
        tipos_evento = cursor.fetchall()
    connection.close()
    return tipos_evento

def get_metodos_pago():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_metodo_pago, nombre 
            FROM METODO_PAGO
        """)
        metodos_pago = cursor.fetchall()
    connection.close()
    return metodos_pago

def get_tipo_documento():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM TIPO_DOCUMENTO WHERE tipo_doc_id IN (1, 3);

        """)
        tipo_documento = cursor.fetchall()
    connection.close()
    return tipo_documento


def generar_numero_comprobante(tipo):
    conexion = get_connection()
    with conexion.cursor() as cursor:
        # Buscar el último comprobante del mismo tipo
        cursor.execute("SELECT numero_comprobante FROM COMPROBANTE WHERE numero_comprobante LIKE %s ORDER BY comprobante_id DESC LIMIT 1", (f"{tipo}%",))
        ultimo = cursor.fetchone()
        
        if ultimo:
            # Extraer el número correlativo (últimos 8 dígitos)
            ultimo_numero = int(ultimo[0].split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1

    # Serie fija (podrías hacerla dinámica si quieres)
    serie = "001"
    
    # Generar el formato realista: B001-00000001
    return f"{tipo}{serie}-{nuevo_numero:08d}"



def procesar_pago():
    print("➡️ Iniciando procesar_pago()")

    conexion = get_connection()
    cursor = conexion.cursor()

    try:
        # ========= 1️⃣ OBTENER DATOS DEL FORMULARIO ==========
        print("📥 Obteniendo datos del formulario...")

        tipo_cliente = request.form.get("tipo_cliente")  # 'N' o 'J'
        nro_doc = request.form.get("nro_doc") or request.form.get("ruc")
        tipo_doc_id = request.form.get("tipo_doc_id")
        pais_id = request.form.get("pais_id")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")
        nombres = request.form.get("nombres")
        ape_pat = request.form.get("ape_paterno")
        ape_mat = request.form.get("ape_materno")
        razon_social = request.form.get("razon_social")
        numero_horas = request.form.get("numero_horas")
        precio_final = request.form.get("precio_final")
        tipo_evento_id = request.form.get("tipo_evento_id")
        nombre_evento = request.form.get("nombre_evento")
        fecha_evento = request.form.get("fecha_evento")
        hora_inicio = request.form.get("hora_inicio")
        hora_fin = request.form.get("hora_fin")
        metodo_pago_id = request.form.get("metodo_pago_id")
        tipo_comprobante = request.form.get("tipo_comprobante")
        numero_comprobante = generar_numero_comprobante(tipo_comprobante)

        print("📦 Datos recibidos:")
        print({
            "tipo_cliente": tipo_cliente,
            "nro_doc": nro_doc,
            "tipo_doc_id": tipo_doc_id,
            "pais_id": pais_id,
            "telefono": telefono,
            "direccion": direccion,
            "nombres": nombres,
            "ape_pat": ape_pat,
            "ape_mat": ape_mat,
            "razon_social": razon_social,
            "tipo_evento_id": tipo_evento_id,
            "nombre_evento": nombre_evento,
            "fecha_evento": fecha_evento,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "numero_horas": numero_horas,
            "precio_final": precio_final,
            "metodo_pago_id": metodo_pago_id,
            "tipo_comprobante": tipo_comprobante
        })

        # ========= 2️⃣ INICIAR TRANSACCIÓN ==========
        conexion.begin()

        # ========= 3️⃣ CLIENTE ==========
        cursor.execute("SELECT cliente_id FROM CLIENTE WHERE num_doc = %s", (nro_doc,))
        cliente = cursor.fetchone()
        if cliente:
            cliente_id = cliente[0]
            print(f"✅ Cliente existente: ID {cliente_id}")
        else:
            cursor.execute("""
                INSERT INTO CLIENTE (
                    direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, tipo_doc_id, 
                    ape_paterno, ape_materno, nombres, razon_social
                ) VALUES (%s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s)
            """, (direccion, telefono, nro_doc, tipo_cliente, pais_id, tipo_doc_id,
                  ape_pat, ape_mat, nombres, razon_social))
            cliente_id = cursor.lastrowid
            print(f"✅ Cliente insertado con ID {cliente_id}")

        # ========= 4️⃣ RESERVA ==========
        cursor.execute("""
            INSERT INTO RESERVA (fecha_registro, hora_registro, monto_total, cliente_id, tipo_reserva, estado)
            VALUES (CURDATE(), CURTIME(), %s, %s, 'E', 1)
        """, (precio_final, cliente_id))
        reserva_id = cursor.lastrowid
        print(f"✅ Reserva creada con ID {reserva_id}")

        # ========= 5️⃣ EVENTO ==========
        cursor.execute("""
            INSERT INTO EVENTO (nombre_evento, fecha, hora_inicio, hora_fin, numero_horas, precio_final, tipo_evento_id, reserva_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre_evento, fecha_evento, hora_inicio, hora_fin, numero_horas,
              precio_final, tipo_evento_id, reserva_id))
        evento_id = cursor.lastrowid
        print(f"✅ Evento creado con ID {evento_id}")

        # ========= 6️⃣ TRANSACCIÓN ==========
        cursor.execute("""
            INSERT INTO TRANSACCION (metodo_pago_id, fecha_pago, monto, estado, reserva_id)
            VALUES (%s, CURDATE(), %s, 1, %s)
        """, (metodo_pago_id, precio_final, reserva_id))
        transaccion_id = cursor.lastrowid
        print(f"✅ Transacción creada con ID {transaccion_id}")

        # ========= 7️⃣ COMPROBANTE ==========
        cursor.execute("""
            INSERT INTO COMPROBANTE (tipo_comprobante, numero_comprobante, fecha_comprobante, hora_comprobante, monto_total, transaccion_id)
            VALUES (%s, %s, CURDATE(), CURTIME(), %s, %s)
        """, (tipo_comprobante, numero_comprobante, precio_final, transaccion_id))
        comprobante_id = cursor.lastrowid
        print(f"✅ Comprobante creado con ID {comprobante_id}")

        # ========= 8️⃣ DETALLE ==========
        cursor.execute("""
            INSERT INTO DETALLE_COMPROBANTE (comprobante_id, evento_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, 1, %s, %s)
        """, (comprobante_id, evento_id, precio_final, precio_final))
        print("✅ Detalle comprobante insertado correctamente.")

        # ========= 9️⃣ CONFIRMAR ==========
        conexion.commit()
        print("✅ Transacción completada y confirmada.")

        return jsonify({
            "success": True,
            "message": "Pago procesado correctamente",
            "reserva_id": reserva_id,
            "comprobante": numero_comprobante
        })

    except Exception as e:
        print("Errorcito en procesar_pago:", e)
        conexion.rollback()
        return jsonify({"success": False, "error": str(e)})

    finally:
        cursor.close()
        conexion.close()
        print("🔚 Cerrando conexión y cursor.")


def get_tipos_eventos(limit=20, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento, estado 
            FROM TIPO_EVENTO
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()
        tipos = []
        for r in rows:
            tipos.append({
                'tipo_evento_id': r[0],
                'nombre_tipo_evento': r[1],
                'estado': r[2]
            })
    connection.close()
    return tipos


# CONTAR TOTAL DE TIPOS DE EVENTO
def count_tipos_eventos():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM TIPO_EVENTO")
        total = cursor.fetchone()[0]
    connection.close()
    return total


# ✅ OBTENER UN TIPO DE EVENTO POR ID
def get_one_tipo_evento(tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento, estado
            FROM TIPO_EVENTO WHERE tipo_evento_id = %s
        """, (tipo_evento_id,))
        row = cursor.fetchone()
        if row:
            return {
                "tipo_evento_id": row[0],
                "nombre_tipo_evento": row[1],
                "estado": row[2]
            }
    connection.close()
    return None


# ✅ INSERTAR NUEVO TIPO DE EVENTO
def insert_tipo_evento(nombre_tipo_evento, estado):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO TIPO_EVENTO (nombre_tipo_evento, estado)
            VALUES (%s, %s)
        """, (nombre_tipo_evento, estado))
    connection.commit()
    connection.close()


# ✅ ACTUALIZAR TIPO DE EVENTO EXISTENTE
def update_tipo_evento(nombre_tipo_evento, estado, tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE TIPO_EVENTO
            SET nombre_tipo_evento = %s, estado = %s
            WHERE tipo_evento_id = %s
        """, (nombre_tipo_evento, estado, tipo_evento_id))
    connection.commit()
    connection.close()


# ✅ ELIMINAR TIPO DE EVENTO
def delete_tipo_evento(tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM TIPO_EVENTO WHERE tipo_evento_id = %s", (tipo_evento_id,))
    connection.commit()
    connection.close()


# ✅ ORDENAR TIPOS DE EVENTO
def order_tipo_evento(filter_field, order):
    allowed_fields = ['tipo_evento_id', 'nombre_tipo_evento', 'estado']
    if filter_field not in allowed_fields:
        filter_field = 'tipo_evento_id'
    if order.lower() not in ['asc', 'desc']:
        order = 'asc'

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT tipo_evento_id, nombre_tipo_evento, estado 
            FROM TIPO_EVENTO
            ORDER BY {filter_field} {order.upper()}
        """)
        tipos = cursor.fetchall()
    connection.close()
    return tipos


# ✅ BUSCAR TIPO DE EVENTO POR NOMBRE
def search_tipo_evento(query):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento, estado
            FROM TIPO_EVENTO
            WHERE LOWER(nombre_tipo_evento) LIKE %s
        """, ('%' + query.lower() + '%',))
        tipos = cursor.fetchall()
    connection.close()
    return tipos