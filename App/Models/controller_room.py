from bd import get_connection
from datetime import datetime

def get_rooms(limit=20, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                r.habitacion_id,
                r.numero,
                r.estado,
                r.piso_id,
                r.categoria_id,
                c.nombre_categoria
                
                FROM
                    HABITACION C
                INNER JOIN CATEGORIA C ON r.categoria_id = c.categoria_id
            """, (limit,offset))
        rooms = cursor.fetchall()
    connection.close()
    return rooms

def count_rooms():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM HABITACION")
        total = cursor.fetchone()[0]
    connection.close()
    return total