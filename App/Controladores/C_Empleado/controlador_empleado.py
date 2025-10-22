from bd import get_connection

def get_empleados(limit=10, offset=0, search_term='', rol_filter=''):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    e.empleado_id,
                    e.nombres,
                    e.ape_paterno,
                    e.ape_materno,
                    e.dni,
                    e.movil,
                    te.nombre_tipo AS tipo_empleado
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE (e.nombres LIKE %s OR e.ape_paterno LIKE %s)
            """
            params = [f"%{search_term}%", f"%{search_term}%"]

            if rol_filter:
                query += " AND te.tipo_id = %s"
                params.append(rol_filter)

            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            empleados = cursor.fetchall()
    finally:
        connection.close()
    return empleados


def count_empleados(search_term='', rol_filter=''):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT COUNT(*)
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE (e.nombres LIKE %s OR e.ape_paterno LIKE %s)
            """
            params = [f"%{search_term}%", f"%{search_term}%"]

            if rol_filter:
                query += " AND te.tipo_id = %s"
                params.append(rol_filter)

            cursor.execute(query, params)
            total = cursor.fetchone()[0]
    finally:
        connection.close()
    return total


def get_tipos_empleado():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tipo_id, nombre_tipo FROM TIPO_EMPLEADO")
            tipos = cursor.fetchall()
    finally:
        connection.close()
    return tipos
