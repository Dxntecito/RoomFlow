from bd import get_connection
from datetime import timedelta

def formatear_hora(hora):
    """
    Formatear hora (time, timedelta o string) a formato HH:MM
    """
    if hora is None:
        return ''
    
    # Si es string, ya está formateado, solo tomar HH:MM
    if isinstance(hora, str):
        if not hora or hora.strip() == '':
            return ''
        return hora[:5] if len(hora) > 5 else hora
    
    # Si es timedelta, convertir a HH:MM
    if isinstance(hora, timedelta):
        total_seconds = int(hora.total_seconds())
        # Manejar casos donde los segundos pueden ser negativos o muy grandes
        if total_seconds < 0:
            total_seconds = total_seconds % (24 * 3600)  # Normalizar a un día
        hours = (total_seconds // 3600) % 24
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    
    # Si es time object, usar strftime
    if hasattr(hora, 'strftime'):
        return hora.strftime('%H:%M')
    
    # Cualquier otro caso, convertir a string y tomar HH:MM
    hora_str = str(hora)
    if not hora_str or hora_str.strip() == '':
        return ''
    return hora_str[:5] if len(hora_str) > 5 else hora_str

def get_turnos():
    """
    Obtener todos los turnos
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT turno_id, nombre_turno, hora_inicio, hora_fin FROM TURNO ORDER BY turno_id"
            cursor.execute(query)
            turnos = cursor.fetchall()
            # Formatear las horas
            turnos_formateados = []
            for turno in turnos:
                turno_id = turno[0]
                nombre = turno[1]
                hora_inicio = formatear_hora(turno[2])
                hora_fin = formatear_hora(turno[3])
                turnos_formateados.append((turno_id, nombre, hora_inicio, hora_fin))
            return turnos_formateados
    finally:
        connection.close()

def get_turno_by_id(turno_id):
    """
    Obtener un turno específico por su ID
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT turno_id, nombre_turno, hora_inicio, hora_fin FROM TURNO WHERE turno_id = %s"
            cursor.execute(query, (turno_id,))
            turno = cursor.fetchone()
            if turno:
                # Formatear las horas
                turno_id_val = turno[0]
                nombre = turno[1]
                hora_inicio = formatear_hora(turno[2])
                hora_fin = formatear_hora(turno[3])
                return (turno_id_val, nombre, hora_inicio, hora_fin)
            return None
    finally:
        connection.close()

def insert_turno(nombre_turno, hora_inicio, hora_fin):
    """
    Insertar nuevo turno en la base de datos
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el nombre del turno no exista
            cursor.execute("SELECT COUNT(*) FROM TURNO WHERE nombre_turno = %s", (nombre_turno,))
            if cursor.fetchone()[0] > 0:
                return False, "El nombre del turno ya existe"
            
            # Validar que las horas sean válidas (excepto si hora_fin es 00:00:00 que significa medianoche)
            if hora_fin != "00:00:00" and hora_inicio >= hora_fin:
                return False, "La hora de inicio debe ser menor que la hora de fin"
            
            # Insertar turno
            query = """
                INSERT INTO TURNO (nombre_turno, hora_inicio, hora_fin)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (nombre_turno, hora_inicio, hora_fin))
            connection.commit()
            return True, "Turno creado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al crear turno: {str(e)}"
    finally:
        connection.close()

def update_turno(turno_id, nombre_turno, hora_inicio, hora_fin):
    """
    Actualizar turno existente
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el turno existe
            cursor.execute("SELECT COUNT(*) FROM TURNO WHERE turno_id = %s", (turno_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El turno no existe"
            
            # Verificar que el nombre del turno no exista en otro turno
            cursor.execute("SELECT COUNT(*) FROM TURNO WHERE nombre_turno = %s AND turno_id != %s", (nombre_turno, turno_id))
            if cursor.fetchone()[0] > 0:
                return False, "El nombre del turno ya existe en otro turno"
            
            # Validar que las horas sean válidas
            if hora_fin != "00:00:00" and hora_inicio >= hora_fin:
                return False, "La hora de inicio debe ser menor que la hora de fin"
            
            # Actualizar turno
            query = """
                UPDATE TURNO 
                SET nombre_turno = %s, hora_inicio = %s, hora_fin = %s
                WHERE turno_id = %s
            """
            cursor.execute(query, (nombre_turno, hora_inicio, hora_fin, turno_id))
            connection.commit()
            return True, "Turno actualizado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al actualizar turno: {str(e)}"
    finally:
        connection.close()

def delete_turno(turno_id):
    """
    Eliminar turno (solo si no tiene detalles asociados)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Verificar que el turno existe
            cursor.execute("SELECT COUNT(*) FROM TURNO WHERE turno_id = %s", (turno_id,))
            if cursor.fetchone()[0] == 0:
                return False, "El turno no existe"
            
            # Verificar si tiene detalles de turno asociados
            cursor.execute("SELECT COUNT(*) FROM DETALLE_TURNO WHERE turno_id = %s", (turno_id,))
            if cursor.fetchone()[0] > 0:
                return False, "No se puede eliminar el turno porque tiene asignaciones de empleados asociadas"
            
            # Eliminar turno
            cursor.execute("DELETE FROM TURNO WHERE turno_id = %s", (turno_id,))
            connection.commit()
            return True, "Turno eliminado exitosamente"
    except Exception as e:
        connection.rollback()
        return False, f"Error al eliminar turno: {str(e)}"
    finally:
        connection.close()

def count_turnos():
    """
    Contar el total de turnos
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM TURNO")
            count = cursor.fetchone()[0]
            return count
    finally:
        connection.close()
