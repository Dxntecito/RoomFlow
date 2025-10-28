from bd import get_connection

def get_types_doc(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    TD.tipo_doc_id,
                    TD.nombre_tipo_doc,
                    TD.estado
                FROM TIPO_DOCUMENTO TD
                LIMIT %s OFFSET %s
            """, (limit, offset))
            types_doc = cursor.fetchall()
    finally:
        connection.close()
    return types_doc