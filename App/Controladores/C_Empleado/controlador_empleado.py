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
                WHERE e.estado = 1 AND (e.nombres LIKE %s OR e.ape_paterno LIKE %s)
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


def insert_empleado(cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id):
    """
    Insertar nuevo empleado en la base de datos
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el DNI no exista
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE dni = %s", (dni,))
            if cursor.fetchone()[0] > 0:
                return False, "El DNI ya existe en la base de datos"
            
            # Verificar que el código de empleado no exista
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE cod_empleado = %s", (cod_empleado,))
            if cursor.fetchone()[0] > 0:
                return False, "El código de empleado ya existe"
            
            # Insertar empleado
            query = """
                INSERT INTO EMPLEADO (cod_empleado, dni, ape_paterno, ape_materno, 
                                    nombres, sexo, movil, tipo_empleado_id, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            cursor.execute(query, (cod_empleado, dni, ape_paterno, ape_materno, 
                                  nombres, sexo, movil, tipo_empleado_id))
            connection.commit()
            return True, "Empleado creado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al crear empleado: {str(e)}"
    finally:
        connection.close()


def update_empleado(empleado_id, cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id):
    """
    Actualizar datos de empleado existente
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el empleado existe
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El empleado no existe"
            
            # Verificar que el DNI no esté en uso por otro empleado
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE dni = %s AND empleado_id != %s", (dni, empleado_id))
            if cursor.fetchone()[0] > 0:
                return False, "El DNI ya está en uso por otro empleado"
            
            # Verificar que el código de empleado no esté en uso por otro empleado
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE cod_empleado = %s AND empleado_id != %s", (cod_empleado, empleado_id))
            if cursor.fetchone()[0] > 0:
                return False, "El código de empleado ya está en uso"
            
            # Actualizar empleado
            query = """
                UPDATE EMPLEADO 
                SET cod_empleado = %s, dni = %s, ape_paterno = %s, ape_materno = %s,
                    nombres = %s, sexo = %s, movil = %s, tipo_empleado_id = %s
                WHERE empleado_id = %s
            """
            cursor.execute(query, (cod_empleado, dni, ape_paterno, ape_materno, 
                                  nombres, sexo, movil, tipo_empleado_id, empleado_id))
            connection.commit()
            return True, "Empleado actualizado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al actualizar empleado: {str(e)}"
    finally:
        connection.close()


def get_empleado_by_id(empleado_id):
    """
    Obtener un empleado específico por su ID
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
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
                    e.estado,
                    te.nombre_tipo
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE e.empleado_id = %s
            """
            cursor.execute(query, (empleado_id,))
            empleado = cursor.fetchone()
    finally:
        connection.close()
    return empleado


def delete_empleado(empleado_id):
    """
    Eliminar empleado (eliminación lógica - cambiar estado a 0)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el empleado existe
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El empleado no existe"
            
            # Eliminación lógica (cambiar estado a 0)
            cursor.execute("UPDATE EMPLEADO SET estado = 0 WHERE empleado_id = %s", (empleado_id,))
            connection.commit()
            return True, "Empleado eliminado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al eliminar empleado: {str(e)}"
    finally:
        connection.close()


def get_empleados_activos(limit=10, offset=0, search_term='', rol_filter=''):
    """
    Obtener solo empleados activos (estado = 1)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
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
                    e.estado,
                    te.nombre_tipo AS tipo_empleado
                FROM EMPLEADO e
                INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                WHERE e.estado = 1 AND (e.nombres LIKE %s OR e.ape_paterno LIKE %s)
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