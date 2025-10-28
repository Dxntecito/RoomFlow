from bd import get_connection

def get_types_emp(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    T.tipo_id,
                    T.nombre_tipo,
                    T.estado
                FROM TIPO_EMPRESA T
                LIMIT %s OFFSET %s
            """, (limit, offset))
            types_emp = cursor.fetchall()
    finally:
        connection.close()
    return types_emp