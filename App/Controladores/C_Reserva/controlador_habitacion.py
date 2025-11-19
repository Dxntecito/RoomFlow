from bd import get_connection
from datetime import datetime
# def get_available_rooms(limit=20, offset=0):
#     connection = get_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT
#                     h.habitacion_id,
#                     h.numero,
#                     h.estado,
#                     h.piso_id,
#                     h.id_categoria,
#                     (p.precio + c.precio_categoria) as precio_total,
#                     COALESCE(r.fecha_ingreso,'X') as f_ingreso,
#                     COALESCE(r.hora_entrada,'X') as f_ingreso,
#                     COALESCE(r.fecha_salida,'X') as f_salida,
#                     COALESCE(r.hora_salida,'X') as h_salida,
#                 FROM HABITACION h
#                 INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
#                 INNER JOIN PISO p ON h.piso_id = p.piso_id
#                 LEFT JOIN RESERVA_HABITACION rh ON rh.habitacion_id = h.habitacion_id
#                 LEFT JOIN RESERVA r ON r.reserva_id = rh.reserva_id
#                 LIMIT %s OFFSET %s
#             """, (limit, offset))
#             rooms = cursor.fetchall()
#     finally:
#         connection.close()
#     return rooms


# def get_available_rooms(start_date=None, end_date=None, limit=20, offset=0):
#     connection = get_connection()
#     try:
#         with connection.cursor() as cursor:
#             query = """
#                 SELECT
#                     h.habitacion_id,
#                     h.numero,
#                     h.estado,
#                     h.piso_id,
#                     h.id_categoria,
#                     (p.precio + c.precio_categoria) AS precio_total
#                     FROM HABITACION h
#                     INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
#                     INNER JOIN PISO p ON h.piso_id = p.piso_id
#                 WHERE h.habitacion_id NOT IN (
#                     SELECT h2.habitacion_id
#                     FROM HABITACION h2
#                     LEFT JOIN RESERVA_HABITACION rh2 ON rh2.habitacion_id = h2.habitacion_id
#                     LEFT JOIN RESERVA r2 ON r2.reserva_id = rh2.reserva_id
#                     WHERE 
#                         -- Colisión de fechas
#                         (r2.fecha_ingreso < %s AND r2.fecha_salida > %s)
#                         OR
#                         (r2.fecha_ingreso = %s AND r2.hora_ingreso <= %s)
#                         OR
#                         (r2.fecha_salida = %s AND r2.hora_salida >= %s)
#                 )
#                 LIMIT %s OFFSET %s
#             """
#             cursor.execute(query, (
#                 end_date, start_date,  # Para la comparación de rango
#                 start_date, "00:00:00",  # Hora mínima al ingresar
#                 end_date, "23:59:59",    # Hora máxima al salir
#                 limit, offset
#             ))
#             rooms = cursor.fetchall()
#     finally:
#         connection.close()
#     return rooms
def get_available_rooms(start_dt=None, end_dt=None, limit=20, offset=0):
    """
    Obtiene las habitaciones disponibles (no tienen reservas que colisionen con [start_dt, end_dt)).
    start_dt y end_dt son objetos datetime.datetime (o None).
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            if start_dt and end_dt:
                # convertimos a strings en formato MySQL
                start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')

                print("SQL Params (start,end,limit,offset):", start_str, end_str, limit, offset)

                sql = """
                    SELECT
                        h.habitacion_id,
                        h.numero,
                        h.estado,
                        h.piso_id,
                        h.id_categoria,
                        (p.precio + c.precio_categoria) AS precio_total
                    FROM HABITACION h
                    INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                    INNER JOIN PISO p ON h.piso_id = p.piso_id
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM RESERVA_HABITACION rh2
                        JOIN RESERVA r2 ON r2.reserva_id = rh2.reserva_id
                        WHERE rh2.habitacion_id = h.habitacion_id
                          -- existe colisión si: r2.start < end AND r2.end > start
                          AND TIMESTAMP(r2.fecha_ingreso, COALESCE(r2.hora_ingreso, '00:00:00')) < %s
                          AND TIMESTAMP(r2.fecha_salida, COALESCE(r2.hora_salida, '23:59:59')) > %s
                    )
                    LIMIT %s OFFSET %s
                """
                # parámetros: end_str (to compare r.start < end), start_str (to compare r.end > start)
                cursor.execute(sql, (end_str, start_str, limit, offset))

            else:
                sql = """
                    SELECT
                        h.habitacion_id,
                        h.numero,
                        h.estado,
                        h.piso_id,
                        h.id_categoria,
                        (p.precio + c.precio_categoria) AS precio_total
                    FROM HABITACION h
                    INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                    INNER JOIN PISO p ON h.piso_id = p.piso_id
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (limit, offset))

            rows = cursor.fetchall()
            print("Rooms fetched (count):", len(rows))
            columns = [
                "id",
                "numero",
                "estado",
                "piso_id",
                "categoria_id",
                "precio"
            ]
            rooms = [dict(zip(columns, row)) for row in rows]
    finally:
        connection.close()
    return rooms


def get_rooms(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    h.habitacion_id,
                    h.numero,
                    h.estado,
                    h.id_categoria,
                    c.nombre_categoria,
                    h.piso_id,
                    p.numero AS numero_piso
                FROM HABITACION h
                LEFT JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                LEFT JOIN PISO p ON h.piso_id = p.piso_id
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cursor.fetchall()
            rooms = []
            for row in rows:
                rooms.append({
                    "id": row[0],
                    "numero": row[1],
                    "estado": row[2],
                    "categoria_id": row[3],
                    "categoria": row[4],
                    "piso_id": row[5],
                    "piso": row[6]
                })
            return rooms
    finally:
        connection.close()


def count_rooms():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM HABITACION")
            row = cursor.fetchone()
            return row[0] if row else 0
    finally:
        connection.close()


def order_rooms(field="habitacion_id", order="asc"):
    valid_fields = {
        "habitacion_id": "habitacion_id",
        "numero": "numero",
        "estado": "estado",
        "categoria": "id_categoria",
        "piso": "piso_id"
    }
    field_db = valid_fields.get(field, "habitacion_id")
    order_db = "DESC" if str(order).lower() == "desc" else "ASC"

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    h.habitacion_id,
                    h.numero,
                    h.estado,
                    h.id_categoria,
                    c.nombre_categoria,
                    h.piso_id,
                    p.numero AS numero_piso
                FROM HABITACION h
                LEFT JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                LEFT JOIN PISO p ON h.piso_id = p.piso_id
                ORDER BY {field_db} {order_db}
            """)
            rows = cursor.fetchall()
            rooms = []
            for row in rows:
                rooms.append({
                    "id": row[0],
                    "numero": row[1],
                    "estado": row[2],
                    "categoria_id": row[3],
                    "categoria": row[4],
                    "piso_id": row[5],
                    "piso": row[6]
                })
            return rooms
    finally:
        connection.close()


def get_room(habitacion_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    h.habitacion_id,
                    h.numero,
                    h.estado,
                    h.id_categoria,
                    c.nombre_categoria,
                    h.piso_id,
                    p.numero AS numero_piso
                FROM HABITACION h
                LEFT JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                LEFT JOIN PISO p ON h.piso_id = p.piso_id
                WHERE h.habitacion_id = %s
            """, (habitacion_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "numero": row[1],
                "estado": row[2],
                "categoria_id": row[3],
                "categoria": row[4],
                "piso_id": row[5],
                "piso": row[6]
            }
    finally:
        connection.close()


def insert_room(numero, estado, categoria_id, piso_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO HABITACION (numero, estado, id_categoria, piso_id)
                VALUES (%s, %s, %s, %s)
            """, (numero, estado, categoria_id, piso_id))
        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        connection.close()


def update_room(habitacion_id, numero, estado, categoria_id, piso_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE HABITACION
                SET numero = %s,
                    estado = %s,
                    id_categoria = %s,
                    piso_id = %s
                WHERE habitacion_id = %s
            """, (numero, estado, categoria_id, piso_id, habitacion_id))
        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        connection.close()


def delete_room(habitacion_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM HABITACION WHERE habitacion_id = %s", (habitacion_id,))
        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        connection.close()


def search_rooms(query):
    connection = get_connection()
    try:
        wildcard = f"%{query}%"
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    h.habitacion_id,
                    h.numero,
                    h.estado,
                    h.id_categoria,
                    c.nombre_categoria,
                    h.piso_id,
                    p.numero AS numero_piso
                FROM HABITACION h
                LEFT JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                LEFT JOIN PISO p ON h.piso_id = p.piso_id
                WHERE h.numero LIKE %s
                   OR c.nombre_categoria LIKE %s
                   OR p.numero LIKE %s
            """, (wildcard, wildcard, wildcard))
            rows = cursor.fetchall()
            rooms = []
            for row in rows:
                rooms.append({
                    "id": row[0],
                    "numero": row[1],
                    "estado": row[2],
                    "categoria_id": row[3],
                    "categoria": row[4],
                    "piso_id": row[5],
                    "piso": row[6]
                })
            return rooms
    finally:
        connection.close()
