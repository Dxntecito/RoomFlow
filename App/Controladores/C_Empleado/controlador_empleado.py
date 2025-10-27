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

def generar_codigo_empleado(tipo_empleado_id, dni):
    """
    Generar código de empleado automáticamente basado en el rol y DNI
    """
    # Mapeo de tipos de empleado a prefijos
    prefijos = {
        1: 'RE',  # Recepcionista
        2: 'AD',  # Administrador
        3: 'LI'   # Limpieza
    }
    
    prefijo = prefijos.get(tipo_empleado_id, 'EM')
    
    return f"{prefijo}{dni}"

def insert_empleado_auto(dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id):
    """
    Insertar nuevo empleado con código generado automáticamente
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el DNI no exista
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE dni = %s", (dni,))
            if cursor.fetchone()[0] > 0:
                return False, "El DNI ya existe en la base de datos"
            
            # Generar código automáticamente
            cod_empleado = generar_codigo_empleado(tipo_empleado_id, dni)
            
            # Verificar que el código generado no exista (si existe, agregar número)
            codigo_original = cod_empleado
            contador = 1
            while True:
                cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE cod_empleado = %s", (cod_empleado,))
                if cursor.fetchone()[0] == 0:
                    break
                cod_empleado = f"{codigo_original}{contador:02d}"
                contador += 1
            
            # Insertar empleado
            query = """
                INSERT INTO EMPLEADO (cod_empleado, dni, ape_paterno, ape_materno, 
                                    nombres, sexo, movil, tipo_empleado_id, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
            """
            cursor.execute(query, (cod_empleado, dni, ape_paterno, ape_materno, 
                                  nombres, sexo, movil, tipo_empleado_id))
            connection.commit()
            return True, f"Empleado creado exitosamente con código: {cod_empleado}"
    except Exception as e:
        connection.rollback()
        return False, f"Error al crear empleado: {str(e)}"
    finally:
        connection.close()

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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activo')
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

def get_empleado_by_dni(dni):
    """
    Obtener un empleado específico por su DNI
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
                WHERE e.dni = %s
            """
            cursor.execute(query, (dni,))
            empleado = cursor.fetchone()
    finally:
        connection.close()
    return empleado


def asignar_turno_empleado(empleado_id, turno_id):
    """
    Asignar o actualizar un turno a un empleado en DETALLE_TURNO
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el empleado existe
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El empleado no existe"
            
            # Verificar que el turno existe
            cursor.execute("SELECT COUNT(*) FROM TURNO WHERE turno_id = %s", (turno_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El turno seleccionado no existe"
            
            # Verificar si ya existe un turno para este empleado hoy
            cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO WHERE empleado_id = %s AND fecha = CURDATE()", (empleado_id,))
            turno_existente = cursor.fetchone()[0] > 0
            
            if turno_existente:
                # Actualizar turno existente
                query = "UPDATE DETALLE_TURNO SET turno_id = %s WHERE empleado_id = %s AND fecha = CURDATE()"
                cursor.execute(query, (turno_id, empleado_id))
                message = "Turno actualizado exitosamente"
            else:
                # Insertar nuevo turno
                query = "INSERT INTO DETALLE_TURNO (empleado_id, turno_id, fecha) VALUES (%s, %s, CURDATE())"
                cursor.execute(query, (empleado_id, turno_id))
                message = "Turno asignado exitosamente"
            
            connection.commit()
            return True, message
    except Exception as e:
        connection.rollback()
        return False, f"Error al asignar turno: {str(e)}"
    finally:
        connection.close()


def get_turno_actual_empleado(empleado_id):
    """
    Obtener el turno actual de un empleado
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT dt.turno_id, t.nombre_turno 
                FROM DETALLE_TURNO dt 
                JOIN TURNO t ON dt.turno_id = t.turno_id 
                WHERE dt.empleado_id = %s 
                ORDER BY dt.fecha DESC 
                LIMIT 1
            """
            cursor.execute(query, (empleado_id,))
            turno = cursor.fetchone()
            return turno
    except Exception as e:
        print(f"Error al obtener turno actual: {e}")
        return None
    finally:
        connection.close()


def get_turnos():
    """
    Obtener todos los turnos disponibles
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT turno_id, nombre_turno FROM TURNO")
            turnos = cursor.fetchall()
            return turnos
    except Exception as e:
        print(f"Error al obtener turnos: {e}")
        return []
    finally:
        connection.close()

def delete_empleado(empleado_id):
    """
    Eliminar empleado (eliminación física - DELETE FROM)
    Elimina también todos los registros relacionados en DETALLE_TURNO
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el empleado existe
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El empleado no existe"
            
            # Primero, eliminar todos los registros relacionados en DETALLE_TURNO
            cursor.execute("DELETE FROM DETALLE_TURNO WHERE empleado_id = %s", (empleado_id,))
            
            # Luego, eliminar el empleado
            cursor.execute("DELETE FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            connection.commit()
            return True, "Empleado eliminado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al eliminar empleado: {str(e)}"
    finally:
        connection.close()


def update_empleado(empleado_id, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id, estado):
    """
    Actualizar empleado existente
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el empleado existe
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El empleado no existe"
            
            # Verificar que el DNI no exista en otro empleado
            cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE dni = %s AND empleado_id != %s", (dni, empleado_id))
            if cursor.fetchone()[0] > 0:
                return False, "El DNI ya existe en otro empleado"
            
            # Generar nuevo código si cambió el rol o DNI
            cursor.execute("SELECT cod_empleado, tipo_empleado_id, dni FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            empleado_actual = cursor.fetchone()
            
            if empleado_actual:
                codigo_actual = empleado_actual[0]
                rol_actual = empleado_actual[1]
                dni_actual = empleado_actual[2]
                
                # Si cambió el rol o DNI, generar nuevo código
                if rol_actual != tipo_empleado_id or dni_actual != dni:
                    nuevo_codigo = generar_codigo_empleado(tipo_empleado_id, dni)
                    
                    # Verificar que el nuevo código no exista
                    codigo_original = nuevo_codigo
                    contador = 1
                    while True:
                        cursor.execute("SELECT COUNT(*) FROM EMPLEADO WHERE cod_empleado = %s AND empleado_id != %s", (nuevo_codigo, empleado_id))
                        if cursor.fetchone()[0] == 0:
                            break
                        nuevo_codigo = f"{codigo_original}{contador:02d}"
                        contador += 1
                else:
                    nuevo_codigo = codigo_actual
            else:
                nuevo_codigo = generar_codigo_empleado(tipo_empleado_id, dni)
            
            # Actualizar empleado
            query = """
                UPDATE EMPLEADO SET 
                    cod_empleado = %s,
                    dni = %s,
                    ape_paterno = %s,
                    ape_materno = %s,
                    nombres = %s,
                    sexo = %s,
                    movil = %s,
                    tipo_empleado_id = %s,
                    estado = %s
                WHERE empleado_id = %s
            """
            cursor.execute(query, (nuevo_codigo, dni, ape_paterno, ape_materno, 
                                  nombres, sexo, movil, tipo_empleado_id, estado, empleado_id))
            connection.commit()
            return True, "Empleado actualizado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al actualizar empleado: {str(e)}"
    finally:
        connection.close()

def get_empleados_activos(limit=10, offset=0, search_term='', rol_filter=''):
    """
    Obtener todos los empleados (tanto Activos como Inactivos)
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
                    te.nombre_tipo AS tipo_empleado,
                    (SELECT t.nombre_turno FROM DETALLE_TURNO dt 
                    JOIN TURNO t ON dt.turno_id = t.turno_id 
                    WHERE dt.empleado_id = e.empleado_id 
                    ORDER BY dt.fecha DESC LIMIT 1) AS turno_actual
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