from bd import get_connection
from datetime import datetime, date

def get_detalles_turno(empleado_id=None, turno_id=None, fecha=None):
    """
    Obtener todos los detalles de turno
    Puede filtrar por empleado_id, turno_id o fecha
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    dt.empleado_id,
                    dt.turno_id,
                    dt.fecha,
                    e.nombres,
                    e.ape_paterno,
                    e.ape_materno,
                    e.cod_empleado,
                    t.nombre_turno,
                    t.hora_inicio,
                    t.hora_fin
                FROM DETALLE_TURNO dt
                INNER JOIN EMPLEADO e ON dt.empleado_id = e.empleado_id
                INNER JOIN TURNO t ON dt.turno_id = t.turno_id
                WHERE 1=1
            """
            params = []
            
            if empleado_id:
                query += " AND dt.empleado_id = %s"
                params.append(empleado_id)
            
            if turno_id:
                query += " AND dt.turno_id = %s"
                params.append(turno_id)
            
            if fecha:
                query += " AND dt.fecha = %s"
                params.append(fecha)
            
            query += " ORDER BY dt.turno_id, dt.fecha DESC, e.ape_paterno, e.nombres"
            
            cursor.execute(query, tuple(params))
            detalles = cursor.fetchall()
            return detalles
    finally:
        connection.close()

def get_detalle_turno_by_id(empleado_id, turno_id, fecha):
    """
    Obtener un detalle de turno específico
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    dt.empleado_id,
                    dt.turno_id,
                    dt.fecha,
                    e.nombres,
                    e.ape_paterno,
                    e.ape_materno,
                    e.cod_empleado,
                    t.nombre_turno,
                    t.hora_inicio,
                    t.hora_fin
                FROM DETALLE_TURNO dt
                INNER JOIN EMPLEADO e ON dt.empleado_id = e.empleado_id
                INNER JOIN TURNO t ON dt.turno_id = t.turno_id
                WHERE dt.empleado_id = %s AND dt.turno_id = %s AND dt.fecha = %s
            """
            cursor.execute(query, (empleado_id, turno_id, fecha))
            detalle = cursor.fetchone()
            return detalle
    finally:
        connection.close()

def insert_detalle_turno(empleado_id, turno_id, fecha):
    """
    Insertar nuevo detalle de turno (asignar turno a empleado)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Normalizar fecha si viene con componente de tiempo
            if isinstance(fecha, str) and 'T' in fecha:
                fecha = fecha.split('T')[0]
            
            # Verificar que el empleado existe y está activo
            cursor.execute("SELECT estado FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "El empleado no existe"
            
            if resultado[0] != 'Activo':
                return False, "No se puede asignar turno a un empleado inactivo"
            
            # Verificar que el turno existe
            cursor.execute("SELECT COUNT(*) FROM TURNO WHERE turno_id = %s", (turno_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El turno seleccionado no existe"
            
            # Verificar si ya existe una asignación para este empleado en esta fecha
            cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO WHERE empleado_id = %s AND fecha = %s", (empleado_id, fecha))
            if cursor.fetchone()[0] > 0:
                return False, "El empleado ya tiene un turno asignado para esta fecha"
            
            # Insertar detalle de turno
            query = "INSERT INTO DETALLE_TURNO (empleado_id, turno_id, fecha) VALUES (%s, %s, %s)"
            cursor.execute(query, (empleado_id, turno_id, fecha))
            connection.commit()
            return True, "Turno asignado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al asignar turno: {str(e)}"
    finally:
        connection.close()

def update_detalle_turno(empleado_id_original, turno_id_original, fecha_original, empleado_id, turno_id, fecha):
    """
    Actualizar detalle de turno existente
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Normalizar fechas si vienen con componente de tiempo
            if isinstance(fecha_original, str) and 'T' in fecha_original:
                fecha_original = fecha_original.split('T')[0]
            if isinstance(fecha, str) and 'T' in fecha:
                fecha = fecha.split('T')[0]
            
            # Verificar que el detalle original existe
            cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO WHERE empleado_id = %s AND turno_id = %s AND fecha = %s", 
                         (empleado_id_original, turno_id_original, fecha_original))
            if cursor.fetchone()[0] == 0:
                return False, "La asignación de turno no existe"
            
            # Verificar que el empleado nuevo existe y está activo (si cambió)
            if empleado_id != empleado_id_original:
                cursor.execute("SELECT estado FROM EMPLEADO WHERE empleado_id = %s", (empleado_id,))
                resultado = cursor.fetchone()
                if not resultado:
                    return False, "El empleado no existe"
                if resultado[0] != 'Activo':
                    return False, "No se puede asignar turno a un empleado inactivo"
            
            # Verificar que el turno existe (si cambió)
            if turno_id != turno_id_original:
                cursor.execute("SELECT COUNT(*) FROM TURNO WHERE turno_id = %s", (turno_id,))
                if cursor.fetchone()[0] == 0:
                    return False, "El turno seleccionado no existe"
            
            # Verificar si ya existe otra asignación para este empleado en la nueva fecha (si cambió)
            if empleado_id != empleado_id_original or fecha != fecha_original:
                cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO WHERE empleado_id = %s AND fecha = %s AND (empleado_id != %s OR turno_id != %s OR fecha != %s)", 
                             (empleado_id, fecha, empleado_id_original, turno_id_original, fecha_original))
                if cursor.fetchone()[0] > 0:
                    return False, "El empleado ya tiene un turno asignado para esta fecha"
            
            # Si todo cambió, eliminar el registro original e insertar uno nuevo
            if empleado_id != empleado_id_original or turno_id != turno_id_original or fecha != fecha_original:
                cursor.execute("DELETE FROM DETALLE_TURNO WHERE empleado_id = %s AND turno_id = %s AND fecha = %s", 
                             (empleado_id_original, turno_id_original, fecha_original))
                cursor.execute("INSERT INTO DETALLE_TURNO (empleado_id, turno_id, fecha) VALUES (%s, %s, %s)", 
                             (empleado_id, turno_id, fecha))
            else:
                # Si nada cambió, no hacer nada (pero retornar éxito)
                pass
            
            connection.commit()
            return True, "Asignación de turno actualizada exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al actualizar asignación de turno: {str(e)}"
    finally:
        connection.close()

def delete_detalle_turno(empleado_id, turno_id, fecha):
    """
    Eliminar detalle de turno (desasignar turno de empleado)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Normalizar fecha si viene con componente de tiempo
            if isinstance(fecha, str) and 'T' in fecha:
                fecha = fecha.split('T')[0]
            
            # Verificar que el detalle existe
            cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO WHERE empleado_id = %s AND turno_id = %s AND fecha = %s", 
                         (empleado_id, turno_id, fecha))
            if cursor.fetchone()[0] == 0:
                return False, "La asignación de turno no existe"
            
            # Eliminar detalle
            cursor.execute("DELETE FROM DETALLE_TURNO WHERE empleado_id = %s AND turno_id = %s AND fecha = %s", 
                         (empleado_id, turno_id, fecha))
            connection.commit()
            return True, "Turno desasignado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al desasignar turno: {str(e)}"
    finally:
        connection.close()

def count_detalles_turno():
    """
    Contar el total de detalles de turno
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO")
            count = cursor.fetchone()[0]
            return count
    finally:
        connection.close()

def get_empleados_activos():
    """
    Obtener lista de empleados activos para los selectores
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    empleado_id,
                    cod_empleado,
                    dni,
                    nombres,
                    ape_paterno,
                    ape_materno
                FROM EMPLEADO
                WHERE estado = 'Activo'
                ORDER BY ape_paterno, nombres
            """
            cursor.execute(query)
            empleados = cursor.fetchall()
            return empleados
    finally:
        connection.close()

def get_turnos_disponibles():
    """
    Obtener lista de turnos disponibles para los selectores
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT turno_id, nombre_turno FROM TURNO ORDER BY hora_inicio"
            cursor.execute(query)
            turnos = cursor.fetchall()
            return turnos
    finally:
        connection.close()
