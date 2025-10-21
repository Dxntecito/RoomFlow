from bd import get_connection
from datetime import datetime

def get_rooms(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.habitacion_id,
                    r.numero,
                    r.estado,
                    r.piso_id,
                    r.categoria_id,
                    c.nombre_categoria
                FROM HABITACION r
                INNER JOIN CATEGORIA c ON r.categoria_id = c.categoria_id
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rooms = cursor.fetchall()
    finally:
        connection.close()
    return rooms
