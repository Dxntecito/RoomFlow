from bd import get_connection
from datetime import datetime

def get_empleados(limit=10, offset=0, search_term="", rol_filter=""):
    """
    Obtiene la lista de empleados con filtros de búsqueda y paginación
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Construir la consulta base
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
                    te.nombre_tipo,
                    e.estado,
                    CONCAT(e.nombres, ' ', e.ape_paterno, ' ', e.ape_materno) as nombre_completo
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtro de búsqueda
            if search_term:
                query += " AND (e.nombres LIKE %s OR e.ape_paterno LIKE %s OR e.ape_materno LIKE %s OR e.dni LIKE %s)"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param, search_param])
            
            # Aplicar filtro de rol
            if rol_filter:
                query += " AND te.tipo_id = %s"
                params.append(rol_filter)
            
            # Ordenar y paginar
            query += " ORDER BY e.ape_paterno, e.ape_materno, e.nombres LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            empleados = cursor.fetchall()
            
        return empleados
    except Exception as ex:
        print(f"Error al obtener empleados: {ex}")
        return []
    finally:
        connection.close()

def count_empleados(search_term="", rol_filter=""):
    """
    Cuenta el total de empleados con filtros aplicados
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT COUNT(*)
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE 1=1
            """
            params = []
            
            if search_term:
                query += " AND (e.nombres LIKE %s OR e.ape_paterno LIKE %s OR e.ape_materno LIKE %s OR e.dni LIKE %s)"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param, search_param])
            
            if rol_filter:
                query += " AND te.tipo_id = %s"
                params.append(rol_filter)
            
            cursor.execute(query, params)
            total = cursor.fetchone()[0]
            return total
    except Exception as ex:
        print(f"Error al contar empleados: {ex}")
        return 0
    finally:
        connection.close()

def get_tipos_empleado():
    """
    Obtiene todos los tipos de empleado para el filtro
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tipo_id, nombre_tipo FROM TIPO_EMPLEADO WHERE 1=1 ORDER BY nombre_tipo")
            tipos = cursor.fetchall()
            return tipos
    except Exception as ex:
        print(f"Error al obtener tipos de empleado: {ex}")
        return []
    finally:
        connection.close()

def get_empleado_by_id(empleado_id):
    """
    Obtiene un empleado específico por su ID
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
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
                    te.nombre_tipo,
                    e.estado
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE e.empleado_id = %s
            """, (empleado_id,))
            empleado = cursor.fetchone()
            return empleado
    except Exception as ex:
        print(f"Error al obtener empleado: {ex}")
        return None
    finally:
        connection.close()

def insert_empleado(cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id):
    """
    Inserta un nuevo empleado
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO EMPLEADO (
                    cod_empleado, dni, ape_paterno, ape_materno, nombres, 
                    sexo, movil, tipo_empleado_id, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            """, (cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al insertar empleado: {ex}")
        return False
    finally:
        connection.close()

def update_empleado(empleado_id, cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id):
    """
    Actualiza un empleado existente
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE EMPLEADO SET 
                    cod_empleado = %s,
                    dni = %s,
                    ape_paterno = %s,
                    ape_materno = %s,
                    nombres = %s,
                    sexo = %s,
                    movil = %s,
                    tipo_empleado_id = %s
                WHERE empleado_id = %s
            """, (cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id, empleado_id))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al actualizar empleado: {ex}")
        return False
    finally:
        connection.close()

def delete_empleado(empleado_id):
    """
    Elimina un empleado (cambia estado a inactivo)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE EMPLEADO SET estado = 0 WHERE empleado_id = %s", (empleado_id,))
        connection.commit()
        return True
    except Exception as ex:
        print(f"Error al eliminar empleado: {ex}")
        return False
    finally:
        connection.close()
