from bd import get_connection

def get_available_rooms(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    h.habitacion_id,
                    h.numero,
                    h.estado,
                    h.piso_id,
                    h.id_categoria,
                    (p.precio + c.precio_categoria) as precio_total
                FROM HABITACION h
                INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                INNER JOIN PISO p ON h.piso_id = p.piso_id
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rooms = cursor.fetchall()
    finally:
        connection.close()
    return rooms

