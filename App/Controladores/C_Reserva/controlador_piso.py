from bd import get_connection

def get_floors(limit=10, offset=0):
    connection = get_connection()
    floors = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                p.piso_id,
                p.numero,
                p.estado
            FROM PISO p
            LIMIT %s OFFSET %s
        """, (limit, offset))
        floors = cursor.fetchall()
    connection.close()
    return floors
