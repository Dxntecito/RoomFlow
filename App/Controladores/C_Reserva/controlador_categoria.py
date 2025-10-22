from bd import get_connection

def get_categories(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    c.categoria_id,
                    c.nombre_categoria,
                    c.precio_categoria,
                    c.estado,
                    c.capacidad
                FROM CATEGORIA c
                LIMIT %s OFFSET %s
            """, (limit, offset))
            categories = cursor.fetchall()
    finally:
        connection.close()
    return categories

