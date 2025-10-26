from bd import get_connection

def get_countries(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    p.pais_id,
                    p.nombre,
                    p.estado
                FROM pais p
                LIMIT %s OFFSET %s
            """, (limit, offset))
            countries = cursor.fetchall()
    finally:
        connection.close()
    return countries