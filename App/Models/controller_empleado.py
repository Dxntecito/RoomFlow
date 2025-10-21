from bd import get_connection
from datetime import datetime
# controller_empleado.py


from bd import get_connection

def get_empleados(limit=20, offset=0, search_term=None, rol_filter=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Base query
            query = """
                SELECT
                    e.empleado_id,
                    e.cod_empleado,
                    e.dni,
                    e.ape_paterno,
                    e.ape_materno,
                    e.nombres,
                    e.sexo,
                    e.movil,
                    e.tipo_empleado_id,
                    e.estado
                FROM EMPLEADO e
                WHERE 1=1
            """
            params = []

            # Filtro por búsqueda (nombre o apellidos o DNI)
            if search_term:
                query += """
                    AND (
                        e.nombres LIKE %s OR
                        e.ape_paterno LIKE %s OR
                        e.ape_materno LIKE %s OR
                        e.dni LIKE %s
                    )
                """
                term = f"%{search_term}%"
                params.extend([term, term, term, term])

            # Filtro por rol (tipo_empleado_id)
            if rol_filter:
                query += " AND e.tipo_empleado_id = %s"
                params.append(rol_filter)

            # Paginación
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, tuple(params))
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
                WHERE (
                    e.nombres LIKE %s OR
                    e.ape_paterno LIKE %s OR
                    e.ape_materno LIKE %s OR
                    e.dni LIKE %s
                )
            """
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]

            if rol_filter:
                query += " AND e.tipo_empleado_id = %s"
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
