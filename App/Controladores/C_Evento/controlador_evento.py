from bd import get_connection
from datetime import datetime
from decimal import Decimal
from flask import request, jsonify
from datetime import date
import json


def inactivar_eventos_vencidos():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE EVENTO
            SET estado = 0
            WHERE fecha < CURDATE() AND estado = 1
        """)
    connection.commit()
    connection.close()

def get_tipos_eventos1():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento,precio_por_hora FROM TIPO_EVENTO WHERE estado = 1
        """)
        tipos_evento = cursor.fetchall()
    connection.close()
    return tipos_evento

def get_tipos_eventos2():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento, precio_por_hora 
            FROM TIPO_EVENTO 
            WHERE estado = 1
        """)
        rows = cursor.fetchall()

    connection.close()

    tipos_evento = []
    for r in rows:
        tipos_evento.append({
            "tipo_evento_id": r[0],
            "nombre_tipo_evento": r[1],
            "precio_por_hora": r[2]
        })

    return tipos_evento


def get_tipo_evento_by_id(tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento, precio_por_hora
            FROM TIPO_EVENTO
            WHERE tipo_evento_id = %s
        """, (tipo_evento_id,))
        tipo = cursor.fetchone()
    connection.close()
    return tipo


def get_tipo_por_evento():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            select tp.tipo_evento_id,tp.nombre_tipo_evento,precio_por_hora  from TIPO_EVENTO tp inner 
            join EVENTO ev on tp.tipo_evento_id=ev.tipo_evento_id
        """)
        tipos_evento = cursor.fetchall()
    connection.close()
    return tipos_evento


def get_metodos_pago():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_metodo_pago, nombre 
            FROM METODO_PAGO where id_metodo_pago in (2,3)
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
        # ========= 1️ OBTENER DATOS DEL FORMULARIO ==========
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
        capacidad = request.form.get("capacidad")
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
        servicios = json.loads(request.form.get("servicios", "[]"))


        print(" Datos recibidos:")
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
            "capacidad":capacidad,
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

        # ========= 2️ INICIAR TRANSACCIÓN ==========
        conexion.begin()

        # ========= 3️ CLIENTE ==========
        cursor.execute("SELECT cliente_id FROM CLIENTE WHERE num_doc = %s", (nro_doc,))
        cliente = cursor.fetchone()
        if cliente:
            cliente_id = cliente[0]
            print(f" Cliente existente: ID {cliente_id}")
        else:
            cursor.execute("""
                INSERT INTO CLIENTE (
                    direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, tipo_doc_id, 
                    ape_paterno, ape_materno, nombres, razon_social
                ) VALUES (%s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s)
            """, (direccion, telefono, nro_doc, tipo_cliente, pais_id, tipo_doc_id,
                  ape_pat, ape_mat, nombres, razon_social))
            cliente_id = cursor.lastrowid
            print(f" Cliente insertado con ID {cliente_id}")

        # ========= 4️ RESERVA ==========
        cursor.execute("""
            INSERT INTO RESERVA (fecha_registro, hora_registro, monto_total, cliente_id, tipo_reserva, estado)
            VALUES (CURDATE(), CURTIME(), %s, %s, 'E', 1)
        """, (precio_final, cliente_id))
        reserva_id = cursor.lastrowid
        print(f" Reserva creada con ID {reserva_id}")

        # ========= 5️ EVENTO ==========
        cursor.execute("""
            INSERT INTO EVENTO (nombre_evento, fecha, hora_inicio, hora_fin, numero_horas, precio_final, tipo_evento_id, reserva_id,capacidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre_evento, fecha_evento, hora_inicio, hora_fin, numero_horas,
              precio_final, tipo_evento_id, reserva_id,capacidad))
        evento_id = cursor.lastrowid
        print(f" Evento creado con ID {evento_id}")

        # ========= 5.1️ SERVICIOS DEL EVENTO (EVENTO_SERVICIO_EVENTO) ==========
        servicios = json.loads(request.form.get("servicios", "[]"))
        print(" Servicios recibidos del front:", servicios)

        if servicios:
            print(" Insertando servicios seleccionados...")
            for s in servicios:
                cursor.execute("""
                    INSERT INTO EVENTO_SERVICIO_EVENTO (evento_id, servicio_evento_id, cantidad, precio_unitario)
                    VALUES (%s, %s, 1, %s)
                """, (evento_id, s["id"], s["precio"]))

            print(f" {len(servicios)} servicios insertados.")
        else:
            print(" No se seleccionaron servicios para este evento.")


        # ========= 6️ TRANSACCIÓN ==========
        cursor.execute("""
            INSERT INTO TRANSACCION (metodo_pago_id, fecha_pago, monto, estado, reserva_id)
            VALUES (%s, CURDATE(), %s, 1, %s)
        """, (metodo_pago_id, precio_final, reserva_id))
        transaccion_id = cursor.lastrowid
        print(f" Transacción creada con ID {transaccion_id}")

        # ========= 7️ COMPROBANTE ==========
        cursor.execute("""
            INSERT INTO COMPROBANTE (tipo_comprobante, numero_comprobante, fecha_comprobante, hora_comprobante, monto_total, transaccion_id)
            VALUES (%s, %s, CURDATE(), CURTIME(), %s, %s)
        """, (tipo_comprobante, numero_comprobante, precio_final, transaccion_id))
        comprobante_id = cursor.lastrowid
        print(f" Comprobante creado con ID {comprobante_id}")

        # ========= 8️ DETALLE ==========
        cursor.execute("""
            INSERT INTO DETALLE_COMPROBANTE (comprobante_id, evento_id, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, 1, %s, %s)
        """, (comprobante_id, evento_id, precio_final, precio_final))
        print(" Detalle comprobante insertado correctamente.")

        # ========= 9️ CONFIRMAR ==========
        conexion.commit()
        print(" Transacción completada y confirmada.")

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
        print(" Cerrando conexión y cursor.")


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


#  OBTENER UN TIPO DE EVENTO POR ID
def get_one_tipo_evento(tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento,estado, precio_por_hora
            FROM TIPO_EVENTO WHERE tipo_evento_id = %s
        """, (tipo_evento_id,))
        row = cursor.fetchone()
        if row:
            return {
                "tipo_evento_id": row[0],
                "nombre_tipo_evento": row[1],
                "estado": row[2],
                "precio_por_hora":row[3]
            }
    connection.close()
    return None


#  INSERTAR NUEVO TIPO DE EVENTO
def insert_tipo_evento(nombre_tipo_evento, estado, precio_por_hora):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO TIPO_EVENTO (nombre_tipo_evento, estado,precio_por_hora)
            VALUES (%s, %s,%s)
        """, (nombre_tipo_evento, estado,precio_por_hora))
    connection.commit()
    connection.close()


#  ACTUALIZAR TIPO DE EVENTO EXISTENTE
def update_tipo_evento(nombre_tipo_evento, estado,precio_por_hora, tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE TIPO_EVENTO
            SET nombre_tipo_evento = %s, estado = %s, precio_por_hora = %s
            WHERE tipo_evento_id = %s
        """, (nombre_tipo_evento, estado,precio_por_hora, tipo_evento_id))
    connection.commit()
    connection.close()


#  ELIMINAR TIPO DE EVENTO
def delete_tipo_evento(tipo_evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM TIPO_EVENTO WHERE tipo_evento_id = %s", (tipo_evento_id,))
    connection.commit()
    connection.close()


#  ORDENAR TIPOS DE EVENTO
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


#  BUSCAR TIPO DE EVENTO POR NOMBRE
def search_tipo_evento(query):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tipo_evento_id, nombre_tipo_evento, estado
            FROM TIPO_EVENTO
            WHERE REPLACE(LOWER(nombre_tipo_evento), ' ', '') LIKE REPLACE(%s, ' ', '')
        """, ('%' + query.lower() + '%',))

        tipos = cursor.fetchall()
    connection.close()

    #  Convertir resultados a diccionarios como tu otra función
    results = []
    for t in tipos:
        results.append({
            'tipo_evento_id': t[0],
            'nombre_tipo_evento': t[1],
            'estado': t[2]
        })

    return results



##CONTROLADOR EVENTO

from datetime import date, time, timedelta

def formatear_fecha(valor):
    if isinstance(valor, date):
        return valor.isoformat()
    return valor  # deja None o strings

def formatear_hora(valor):
    if valor is None:
        return None
    val_str = str(valor)           # convierte time o timedelta a string
    return val_str.split('.')[0]   # elimina microsegundos si los hubiera

def get_eventos(limit=20, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_evento, nombre_evento, fecha, hora_inicio, hora_fin, estado
            FROM EVENTO
            ORDER BY id_evento DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()

        eventos = []
        for r in rows:
            eventos.append({
                'id_evento': r[0],
                'nombre_evento': r[1],
                'fecha': formatear_fecha(r[2]),
                'hora_inicio': formatear_hora(r[3]),
                'hora_fin': formatear_hora(r[4]),
                'estado': int(r[5])
            })

    connection.close()
    return eventos




#  OBTENER UN TIPO DE EVENTO POR ID
def get_one_evento(id_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.id_evento,
                e.nombre_evento,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                e.numero_horas,
                e.precio_final,
                e.tipo_evento_id,
                e.reserva_id,
                e.estado
            FROM EVENTO e
            WHERE e.id_evento = %s
        """, (id_evento,))
        evento = cursor.fetchone()
    connection.close()
    return evento


#UPDATE EVENTO

def get_evento_by_id(id_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                e.id_evento,
                e.nombre_evento,
                e.fecha,
                e.hora_inicio,
                e.hora_fin,
                e.numero_horas,
                e.precio_final,
                e.tipo_evento_id,
                e.reserva_id,
                e.estado
            FROM EVENTO e
            WHERE e.id_evento = %s
        """, (id_evento,))
        row = cursor.fetchone()

    connection.close()
    
    if row:
        return {
            "id_evento": row[0],
            "nombre_evento": row[1],
            "fecha": row[2],
            "hora_inicio": row[3],
            "hora_fin": row[4],
            "numero_horas": row[5],
            "precio_final": row[6],
            "tipo_evento_id": row[7],
            "reserva_id": row[8],
            "estado": row[9]
        }
    return None

def update_evento(nombre_evento, fecha, hora_inicio, hora_fin, 
                  numero_horas, precio_final, tipo_evento_id, id_evento, motivo):

    print("\n Ejecutando update_evento()")
    print("Recibido:")
    print(" -> nombre:", nombre_evento)
    print(" -> fecha:", fecha)
    print(" -> horas:", numero_horas)
    print(" -> precio_final:", precio_final)
    print(" -> tipo_evento:", tipo_evento_id)
    print(" -> evento_id:", id_evento)

    evento_actual = get_evento_by_id(id_evento)
    print("Evento antes:", evento_actual)



    old_numero_horas = evento_actual['numero_horas']
    old_precio_final = evento_actual['precio_final']

    precio_cambiado = (old_precio_final != precio_final)

    print("Precio anterior:", old_precio_final)
    print("Precio nuevo:", precio_final)
    print("¿Precio cambió?:", precio_cambiado)

    connection = get_connection()
    with connection.cursor() as cursor:

        print(" Ejecutando UPDATE en BD")
        cursor.execute("""
            UPDATE EVENTO
            SET nombre_evento=%s, fecha=%s, hora_inicio=%s, hora_fin=%s,
              numero_horas=%s, precio_final=%s, tipo_evento_id=%s
            WHERE id_evento=%s
        """, (nombre_evento, fecha, hora_inicio, hora_fin, 
              numero_horas, precio_final, tipo_evento_id, id_evento))

        if precio_cambiado:
            precio_final = Decimal(str(precio_final))
            old_precio_final = Decimal(str(old_precio_final))
            diferencia = precio_final - old_precio_final
            diferencia = precio_final - old_precio_final
            print("Diferencia:", diferencia)

            cursor.execute("""
                SELECT c.comprobante_id
                FROM EVENTO e
                JOIN RESERVA r ON e.reserva_id = r.reserva_id
                JOIN TRANSACCION t ON r.reserva_id = t.reserva_id
                JOIN COMPROBANTE c ON t.transaccion_id = c.transaccion_id
                WHERE e.id_evento = %s;
            """, (id_evento,))
            comprobante = cursor.fetchone()

            print("Comprobante:", comprobante)

            if comprobante:
                comprobante_id = comprobante[0]
                print("Insertando NOTA_CREDITO...")

                cursor.execute("""
                    INSERT INTO NOTA_CREDITO (comprobante_id, fecha_emision, motivo, monto_credito, estado)
                    VALUES (%s, CURDATE(), %s, %s, 1)
                """, (comprobante_id, motivo, abs(diferencia)))

    connection.commit()
    connection.close()
    print(" UPDATE COMPLETO\n")


#id de reserva por evento

def reserva_por_evento(evento_id):
    connection = get_connection()
    with connection.cursor() as cursor:
         cursor.execute("""
                   select reserva_id from EVENTO where id_evento = %s
                """, (evento_id,))
         comprobante = cursor.fetchone()


def count_eventos():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM EVENTO")
        total = cursor.fetchone()[0]
    connection.close()
    return total
def order_evento(filter, order):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT id_evento, nombre_evento, fecha, hora_inicio, hora_fin, numero_horas, precio_final, estado
            FROM EVENTO
            ORDER BY {filter} {order}
        """)
        rows = cursor.fetchall()
    connection.close()
    return rows
def search_evento(query):
    query_param = f"%{query}%"
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_evento, nombre_evento, fecha, hora_inicio, hora_fin, estado
            FROM EVENTO
            WHERE nombre_evento LIKE %s
        """, (query_param,))
        rows = cursor.fetchall()
    connection.close()

    results = []

    for r in rows:

        # ---------- DEBUG PARA IDENTIFICAR EL ERROR ----------
        print("DEBUG RAW ROW:", r)
        print("TIPOS:", type(r[0]), type(r[1]), type(r[2]), type(r[3]), type(r[4]), type(r[5]))
        # ------------------------------------------------------

        fecha = r[2].isoformat() if r[2] is not None else None

        def convertir_hora(valor):
            if valor is None:
                return None
            val_str = str(valor)
            return val_str.split('.')[0]  # Quitar microsegundos si los hay

        hora_inicio = convertir_hora(r[3])
        hora_fin = convertir_hora(r[4])

        results.append({
            "id_evento": r[0],
            "nombre_evento": r[1],
            "fecha": fecha,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "estado": r[5]
        })

    return results





###CAMBIO DE ESTADO

def marcar_eventos_con_nota_credito_por_id(eventos):
    """
    Agrega un atributo 'tiene_nota_credito' a cada evento de la lista,
    usando solo el id_evento.
    """
    connection = get_connection()
    with connection.cursor() as cursor:
        for evento in eventos:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM NOTA_CREDITO nc
                JOIN COMPROBANTE c ON nc.comprobante_id = c.comprobante_id
                JOIN TRANSACCION t ON c.transaccion_id = t.transaccion_id
                JOIN RESERVA r ON t.reserva_id = r.reserva_id
                JOIN EVENTO e ON r.reserva_id = e.reserva_id
                WHERE e.id_evento = %s
            """, (evento['id_evento'],))
            evento['tiene_nota_credito'] = cursor.fetchone()[0] > 0

    connection.close()
    return eventos



def baja_evento(evento_id, motivo_cancelacion):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # 1) Obtener reserva vinculada
            cursor.execute("SELECT reserva_id, precio_final FROM EVENTO WHERE id_evento  = %s", (evento_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Evento {evento_id} no encontrado")
            reserva_id, monto_credito = row

            # 2) Cancelar evento
            cursor.execute("UPDATE EVENTO SET estado = 0 WHERE id_evento  = %s", (evento_id,))

            # 3) Cancelar reserva
            cursor.execute("UPDATE RESERVA SET estado = 0 WHERE reserva_id = %s",
                           (reserva_id))
            #4) Cancelar comprobante
            cursor.execute("UPDATE TRANSACCION SET estado = 0 WHERE reserva_id = %s",
                           (reserva_id))

            # 4) Crear nota de crédito
            cursor.execute("""
                INSERT INTO NOTA_CREDITO (comprobante_id, fecha_emision, motivo, monto_credito, estado)
                SELECT c.comprobante_id, CURDATE(), %s, %s, 1
                FROM COMPROBANTE c
                JOIN TRANSACCION t ON c.transaccion_id = t.transaccion_id
                WHERE t.reserva_id = %s
            """, (motivo_cancelacion, monto_credito, reserva_id))

        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()



def obtener_evento(fecha):
    conexion = get_connection()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT hora_inicio, hora_fin
            FROM EVENTO
            WHERE fecha = %s AND estado = 1
        """, (fecha,))
        reservas = cursor.fetchall()
    return reservas
