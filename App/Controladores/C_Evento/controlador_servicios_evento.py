from bd import get_connection
from datetime import datetime
from decimal import Decimal
from flask import request, jsonify
from datetime import date
from pymysql.cursors import DictCursor

def get_tipos_servicio_evento(): 
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_tipo_servicio_evento, 
                nombre_tipo, 
                estado
            FROM TIPO_SERVICIO_EVENTO
            WHERE estado = 1
            ORDER BY nombre_tipo ASC
        """)
        tipos_servicio = cursor.fetchall()
    connection.close()
    return tipos_servicio



def get_todos_servicios_por_tipo_servicio():
    connection = get_connection()
    with connection.cursor(DictCursor) as cursor:
        cursor.execute("""
            SELECT 
                s.id_servicio_evento,
                s.nombre_servicio,
                s.descripcion,
                s.precio,
                s.estado,
                t.id_tipo_servicio_evento,
                t.nombre_tipo AS nombre_tipo
            FROM SERVICIO_EVENTO s
            INNER JOIN TIPO_SERVICIO_EVENTO t 
                ON s.tipo_servicio_evento_id = t.id_tipo_servicio_evento
            WHERE s.estado = 1
        """)
        servicios = cursor.fetchall()
    connection.close()
    return servicios


def get_servicios_por_tipo(tipo_id):
    connection = get_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT 
                id_servicio_evento,
                nombre_servicio,
                descripcion,
                precio,
                estado
            FROM SERVICIO_EVENTO
            WHERE tipo_servicio_evento_id = %s
              AND estado = 1
            ORDER BY nombre_servicio
        """, (tipo_id,))
        servicios = cursor.fetchall()
    connection.close()
    return servicios


def get_servicios_por_evento(evento_id):
    connection = get_connection()
    servicios = []
    with connection.cursor(DictCursor) as cursor:
        cursor.execute("""
            SELECT 
                ese.servicio_evento_id,
                ese.cantidad,
                ese.precio_unitario,
                se.nombre_servicio,
                se.descripcion,
                se.tipo_servicio_evento_id,
                tse.nombre_tipo
            FROM EVENTO_SERVICIO_EVENTO ese
            INNER JOIN SERVICIO_EVENTO se 
                ON ese.servicio_evento_id = se.id_servicio_evento
            INNER JOIN TIPO_SERVICIO_EVENTO tse
                ON se.tipo_servicio_evento_id = tse.id_tipo_servicio_evento
            WHERE ese.evento_id = %s
            ORDER BY tse.nombre_tipo, se.nombre_servicio
        """, (evento_id,))
        rows = cursor.fetchall()

    connection.close()

    for row in rows:
        servicios.append({
            "servicio_evento_id": row["servicio_evento_id"],
            "cantidad": row["cantidad"],
            "precio_unitario": float(row["precio_unitario"]) if row["precio_unitario"] is not None else 0.0,
            "nombre_servicio": row["nombre_servicio"],
            "descripcion": row.get("descripcion"),
            "tipo_servicio_evento_id": row["tipo_servicio_evento_id"],
            "nombre_tipo": row["nombre_tipo"]
        })

    return servicios


def _normalizar_servicios_ids(servicios_ids):
    if servicios_ids is None:
        return []

    normalizados = []
    for valor in servicios_ids:
        try:
            sid = int(valor)
            if sid not in normalizados:
                normalizados.append(sid)
        except (TypeError, ValueError):
            continue
    return normalizados


def calcular_total_servicios(servicios_ids):
    normalizados = _normalizar_servicios_ids(servicios_ids)
    if not normalizados:
        return Decimal('0')

    total = Decimal('0')
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            placeholders = ','.join(['%s'] * len(normalizados))
            cursor.execute(f"""
                SELECT precio
                FROM SERVICIO_EVENTO
                WHERE id_servicio_evento IN ({placeholders})
            """, tuple(normalizados))

            rows = cursor.fetchall()
            for row in rows:
                precio = row[0] if isinstance(row, (list, tuple)) else row.get('precio')
                if precio is None:
                    continue
                total += Decimal(str(precio))
    finally:
        connection.close()

    return total


def reemplazar_servicios_evento(evento_id, servicios_ids):
    normalizados = _normalizar_servicios_ids(servicios_ids)

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM EVENTO_SERVICIO_EVENTO WHERE evento_id = %s", (evento_id,))

            if not normalizados:
                connection.commit()
                return

            placeholders = ','.join(['%s'] * len(normalizados))
            cursor.execute(f"""
                SELECT id_servicio_evento, precio
                FROM SERVICIO_EVENTO
                WHERE id_servicio_evento IN ({placeholders})
            """, tuple(normalizados))

            precios = {row[0]: float(row[1]) if row[1] is not None else 0.0 for row in cursor.fetchall()}

            for servicio_id in normalizados:
                precio_unitario = precios.get(servicio_id, 0.0)
                cursor.execute("""
                    INSERT INTO EVENTO_SERVICIO_EVENTO (evento_id, servicio_evento_id, cantidad, precio_unitario)
                    VALUES (%s, %s, 1, %s)
                """, (evento_id, servicio_id, precio_unitario))

        connection.commit()
    finally:
        connection.close()



######### MODULO TIPO SERVICIO EVENTO ###############
# OBTENER LISTA DE TIPOS DE SERVICIO
def get_tipos_servicios(limit=20, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_tipo_servicio_evento, nombre_tipo, estado
            FROM TIPO_SERVICIO_EVENTO
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()

        tipos = []
        for r in rows:
            tipos.append({
                'id_tipo_servicio_evento': r[0],
                'nombre_tipo': r[1],
                'estado': r[2]
            })
    connection.close()
    return tipos


# CONTAR TOTAL DE TIPOS DE SERVICIO
def count_tipos_servicios():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM TIPO_SERVICIO_EVENTO")
        total = cursor.fetchone()[0]
    connection.close()
    return total


# OBTENER UN TIPO DE SERVICIO POR ID
def get_one_tipo_servicio(id_tipo_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_tipo_servicio_evento, nombre_tipo, estado
            FROM TIPO_SERVICIO_EVENTO
            WHERE id_tipo_servicio_evento = %s
        """, (id_tipo_servicio_evento,))
        
        row = cursor.fetchone()
        if row:
            return {
                "id_tipo_servicio_evento": row[0],
                "nombre_tipo": row[1],
                "estado": row[2]
            }
    connection.close()
    return None


# INSERTAR NUEVO TIPO DE SERVICIO
def insert_tipo_servicio(nombre_tipo, estado):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO TIPO_SERVICIO_EVENTO (nombre_tipo, estado)
            VALUES (%s, %s)
        """, (nombre_tipo, estado))
    connection.commit()
    connection.close()


# ACTUALIZAR TIPO DE SERVICIO
def update_tipo_servicio(nombre_tipo, estado, id_tipo_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE TIPO_SERVICIO_EVENTO
            SET nombre_tipo = %s, estado = %s
            WHERE id_tipo_servicio_evento = %s
        """, (nombre_tipo, estado, id_tipo_servicio_evento))
    connection.commit()
    connection.close()


# ELIMINAR TIPO DE SERVICIO
def delete_tipo_servicio(id_tipo_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM TIPO_SERVICIO_EVENTO
            WHERE id_tipo_servicio_evento = %s
        """, (id_tipo_servicio_evento,))
    connection.commit()
    connection.close()

def baja_tipo_servicio(id_tipo_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE TIPO_SERVICIO_EVENTO set estado = 0
            WHERE id_tipo_servicio_evento = %s
        """, (id_tipo_servicio_evento,))
    connection.commit()
    connection.close()


# ORDENAR TIPOS DE SERVICIO
def order_tipo_servicio(filter_field, order):
    allowed_fields = ['id_tipo_servicio_evento', 'nombre_tipo', 'estado']
    if filter_field not in allowed_fields:
        filter_field = 'id_tipo_servicio_evento'
    if order.lower() not in ['asc', 'desc']:
        order = 'asc'

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT id_tipo_servicio_evento, nombre_tipo, estado
            FROM TIPO_SERVICIO_EVENTO
            ORDER BY {filter_field} {order.upper()}
        """)
        tipos = cursor.fetchall()
    connection.close()
    return tipos


# BUSCAR TIPO DE SERVICIO POR NOMBRE
def search_tipo_servicio(query):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_tipo_servicio_evento, nombre_tipo, estado
            FROM TIPO_SERVICIO_EVENTO
            WHERE REPLACE(LOWER(nombre_tipo), ' ', '') LIKE REPLACE(%s, ' ', '')
        """, ('%' + query.lower() + '%',))

        tipos = cursor.fetchall()
    connection.close()

    results = []
    for t in tipos:
        results.append({
            'id_tipo_servicio_evento': t[0],
            'nombre_tipo': t[1],
            'estado': t[2]
        })

    return results

#####################################################

######### MODULO SERVICIO EVENTO ###############

# OBTENER LISTA DE SERVICIOS
def get_servicios_evento(limit=8, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                se.id_servicio_evento, 
                se.tipo_servicio_evento_id, 
                se.nombre_servicio,
                se.descripcion, 
                se.precio, 
                se.estado,
                tse.nombre_tipo
            FROM SERVICIO_EVENTO se 
            INNER JOIN TIPO_SERVICIO_EVENTO tse
                ON se.tipo_servicio_evento_id = tse.id_tipo_servicio_evento
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cursor.fetchall()

        servicios = []
        for r in rows:
            servicios.append({
                'id_servicio_evento': r[0],
                'tipo_servicio_evento_id': r[1],
                'nombre_servicio': r[2],
                'descripcion': r[3],
                'precio': float(r[4]),
                'estado': r[5],
                'nombre_tipo': r[6]   # <-- agrego columna del join
            })
    connection.close()
    return servicios


# CONTAR TOTAL DE SERVICIOS
def count_servicios_evento():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM SERVICIO_EVENTO")
        total = cursor.fetchone()[0]
    connection.close()
    return total


# OBTENER UN SERVICIO POR ID
def get_one_servicio_evento(id_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                se.id_servicio_evento, 
                se.tipo_servicio_evento_id, 
                se.nombre_servicio,
                se.descripcion, 
                se.precio, 
                se.estado,
                tse.nombre_tipo
            FROM SERVICIO_EVENTO se 
            INNER JOIN TIPO_SERVICIO_EVENTO tse
                ON se.tipo_servicio_evento_id = tse.id_tipo_servicio_evento
            WHERE id_servicio_evento = %s
        """, (id_servicio_evento,))

        row = cursor.fetchone()
        if row:
            return {
                'id_servicio_evento': row[0],
                'tipo_servicio_evento_id': row[1],
                'nombre_servicio': row[2],
                'descripcion': row[3],
                'precio': float(row[4]),
                'estado': row[5],
                'nombre_tipo': row[6]
            }
    connection.close()
    return None


# INSERTAR NUEVO SERVICIO
def insert_servicio_evento(tipo_servicio_evento_id, nombre_servicio, descripcion, precio, estado):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO SERVICIO_EVENTO
            (tipo_servicio_evento_id, nombre_servicio, descripcion, precio, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (tipo_servicio_evento_id, nombre_servicio, descripcion, precio, estado))
    connection.commit()
    connection.close()


# ACTUALIZAR SERVICIO
def update_servicio_evento(id_servicio_evento, tipo_servicio_evento_id, nombre_servicio, descripcion, precio, estado):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE SERVICIO_EVENTO
            SET tipo_servicio_evento_id = %s,
                nombre_servicio = %s,
                descripcion = %s,
                precio = %s,
                estado = %s
            WHERE id_servicio_evento = %s
        """, (tipo_servicio_evento_id, nombre_servicio, descripcion,
              precio, estado, id_servicio_evento))
    connection.commit()
    connection.close()


# ELIMINAR SERVICIO
def delete_servicio_evento(id_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM SERVICIO_EVENTO
            WHERE id_servicio_evento = %s
        """, (id_servicio_evento,))
    connection.commit()
    connection.close()


# BAJA LÓGICA DEL SERVICIO
def baja_servicio_evento(id_servicio_evento):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE SERVICIO_EVENTO SET estado = 0
            WHERE id_servicio_evento = %s
        """, (id_servicio_evento,))
    connection.commit()
    connection.close()


# ORDENAR SERVICIOS
def order_servicio_evento(filter_field, order):
    allowed_fields = [
        'id_servicio_evento',
        'tipo_servicio_evento_id',
        'nombre_servicio',
        'precio',
        'estado'
    ]
    if filter_field not in allowed_fields:
        filter_field = 'id_servicio_evento'
    if order.lower() not in ['asc', 'desc']:
        order = 'asc'

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT id_servicio_evento, tipo_servicio_evento_id, nombre_servicio,
                   descripcion, precio, estado
            FROM SERVICIO_EVENTO
            ORDER BY {filter_field} {order.upper()}
        """)
        servicios = cursor.fetchall()

    connection.close()

    results = []
    for s in servicios:
        results.append({
            'id_servicio_evento': s[0],
            'tipo_servicio_evento_id': s[1],
            'nombre_servicio': s[2],
            'descripcion': s[3],
            'precio': float(s[4]),
            'estado': s[5]
        })

    return results


# BUSCAR SERVICIO POR NOMBRE
def search_servicio_evento(query):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                se.id_servicio_evento, 
                se.tipo_servicio_evento_id, 
                se.nombre_servicio,
                se.precio, 
                se.estado,
                tse.nombre_tipo
            FROM SERVICIO_EVENTO se 
            INNER JOIN TIPO_SERVICIO_EVENTO tse
                ON se.tipo_servicio_evento_id = tse.id_tipo_servicio_evento
            WHERE REPLACE(LOWER(nombre_servicio), ' ', '') LIKE REPLACE(%s, ' ', '')
        """, ('%' + query.lower() + '%',))

        servicios = cursor.fetchall()
    connection.close()

    results = []
    for s in servicios:
        results.append({
            'id_servicio_evento': s[0],
            'tipo_servicio_evento_id': s[1],
            'nombre_servicio': s[2],
            'precio': float(s[3]),
            'estado': s[4],
            "nombre_tipo":s[5]
        })

    return results


def get_tipos_servicio_evento2():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_tipo_servicio_evento, nombre_tipo, estado
            FROM TIPO_SERVICIO_EVENTO
            ORDER BY nombre_tipo ASC
        """)
        
        rows = cursor.fetchall()
        
        tipos = []
        for r in rows:
            tipos.append({
                'id_tipo_servicio_evento': r[0],
                'nombre_tipo': r[1],
                'estado': r[2]
            })
    
    connection.close()
    return tipos
