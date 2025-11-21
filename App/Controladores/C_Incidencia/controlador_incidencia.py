from bd import get_connection
from datetime import datetime
import base64
import traceback
import pymysql.cursors

class ControladorIncidencia:
    """Controlador para gestionar las incidencias del sistema"""
    
    @staticmethod
    def obtener_tipos_incidencia():
        """Obtiene todos los tipos de incidencia activos"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT id_tipo, nombre, estado 
                    FROM TIPO_INCIDENCIA 
                    WHERE estado = 1
                    ORDER BY nombre
                """
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener tipos de incidencia: {e}")
            traceback.print_exc()
            return []
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def obtener_todas_incidencias():
        """Obtiene todas las incidencias (para administradores)"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                # --- CORRECCIÓN 1: Se quitó 'i.numero_comprobante' ---
                # --- CORRECCIÓN 2: Se cambió '%%d/%%m/%%Y' a '%d/%m/%Y' (un solo %) ---
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia,
                        i.mensaje,
                        DATE_FORMAT(i.fecha_envio, '%d/%m/%Y') AS fecha_envio,
                        DATE_FORMAT(i.fecha_resolucion, '%d/%m/%Y') AS fecha_resolucion,
                        i.estado,
                        CASE i.estado
                            WHEN 1 THEN 'Aprobado'
                            WHEN 2 THEN 'Rechazado'
                            ELSE 'En proceso'
                        END AS estado_texto,
                        i.respuesta,
                        t.nombre as tipo_incidencia,
                        CONCAT(c.nombres, ' ', c.ape_paterno) as cliente_nombre,
                        i.cliente_id
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    LEFT JOIN CLIENTE c ON i.cliente_id = c.cliente_id
                    ORDER BY i.fecha_envio DESC
                """
                cursor.execute(sql) # Sin parámetros, por eso se usa un solo %
                incidencias = cursor.fetchall()
                # Agregar alias 'titulo' para compatibilidad
                for inc in incidencias:
                    inc['titulo'] = inc.get('nombre_incidencia', '')
                return incidencias
        except Exception as e:
            print(f"Error al obtener todas las incidencias: {e}")
            traceback.print_exc()
            return []
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def obtener_incidencias_pendientes():
        """Obtiene solo las incidencias pendientes (estado = 3) para empleados/administradores"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia AS titulo,
                        i.mensaje AS descripcion,
                        DATE_FORMAT(i.fecha_envio, '%d/%m/%Y') AS fecha_envio,
                        DATE_FORMAT(i.fecha_resolucion, '%d/%m/%Y') AS fecha_resolucion,
                        i.estado,
                        CASE i.estado
                            WHEN 1 THEN 'Aprobado'
                            WHEN 2 THEN 'Rechazado'
                            ELSE 'En proceso'
                        END AS estado_texto,
                        i.respuesta,
                        i.tipo_incidencia_id,
                        t.nombre as tipo_incidencia,
                        CONCAT(c.nombres, ' ', c.ape_paterno) as cliente_nombre,
                        i.cliente_id,
                        i.empleado_id,
                        i.prueba
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    LEFT JOIN CLIENTE c ON i.cliente_id = c.cliente_id
                    WHERE i.estado = 3
                    ORDER BY i.fecha_envio DESC
                """
                cursor.execute(sql)
                incidencias = cursor.fetchall()
                
                # Convertir BLOB a base64 para cada incidencia
                for inc in incidencias:
                    if inc['prueba']:
                        inc['imagen'] = base64.b64encode(inc['prueba']).decode('utf-8')
                    else:
                        inc['imagen'] = None
                    del inc['prueba']
                
                return incidencias
        except Exception as e:
            print(f"Error al obtener incidencias pendientes: {e}")
            traceback.print_exc()
            return []
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_incidencias_cliente(cliente_id):
        """Obtiene todas las incidencias de un cliente"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                # --- CORRECCIÓN: Se quitó 'i.numero_comprobante' ---
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia,
                        i.mensaje,
                        DATE_FORMAT(i.fecha_envio, '%%d/%%m/%%Y') AS fecha_envio,
                        DATE_FORMAT(i.fecha_resolucion, '%%d/%%m/%%Y') AS fecha_resolucion,
                        i.estado,
                        CASE i.estado
                            WHEN 1 THEN 'Aprobado'
                            WHEN 2 THEN 'Rechazado'
                            ELSE 'En proceso'
                        END AS estado_texto,
                        i.respuesta,
                        t.nombre as tipo_incidencia,
                        i.prueba
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    WHERE i.cliente_id = %s
                    ORDER BY i.fecha_envio DESC
                """
                cursor.execute(sql, (cliente_id,)) # Con parámetros, por eso '%%' está bien
                incidencias = cursor.fetchall()
                
                for inc in incidencias:
                    if inc['prueba']:
                        inc['imagen'] = base64.b64encode(inc['prueba']).decode('utf-8')
                    else:
                        inc['imagen'] = None
                    del inc['prueba'] 

                return incidencias
        except Exception as e:
            print(f"Error al obtener incidencias del cliente: {e}")
            traceback.print_exc()
            return []
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def crear_incidencia(datos):
        """Crea una nueva incidencia"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                # --- CORRECCIÓN: Se quitó 'numero_comprobante' ---
                sql = """
                    INSERT INTO INCIDENCIA 
                    (nombre_incidencia, mensaje, fecha_envio, estado, 
                     tipo_incidencia_id, prueba, cliente_id, empleado_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    datos['titulo'],
                    datos['descripcion'],
                    datetime.now(),
                    3,  # Estado: En proceso
                    datos['tipo_incidencia_id'],
                    datos.get('evidencia', None),
                    datos.get('cliente_id', None),
                    datos.get('empleado_id', None)
                    # Se quitó 'datos.get('numero_comprobante', None)'
                )
                cursor.execute(sql, valores)
                conexion.commit()
                return {
                    'success': True,
                    'message': 'Incidencia creada exitosamente',
                    'incidencia_id': cursor.lastrowid
                }
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error al crear incidencia: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error al crear incidencia: {str(e)}'
            }
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def actualizar_incidencia(incidencia_id, datos):
        """Actualiza una incidencia existente"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                campos = []
                valores = []
                
                if 'titulo' in datos:
                    campos.append("nombre_incidencia = %s")
                    valores.append(datos['titulo'])
                if 'descripcion' in datos:
                    campos.append("mensaje = %s")
                    valores.append(datos['descripcion'])
                if 'tipo_incidencia_id' in datos:
                    campos.append("tipo_incidencia_id = %s")
                    valores.append(datos['tipo_incidencia_id'])
                
                # --- CORRECCIÓN: Se quitó el bloque de 'numero_comprobante' ---
                
                if 'evidencia' in datos:
                    campos.append("prueba = %s")
                    valores.append(datos['evidencia'])
                if 'estado' in datos:
                    campos.append("estado = %s")
                    valores.append(datos['estado'])
                    if datos['estado'] in [1, 2]:
                        campos.append("fecha_resolucion = %s")
                        valores.append(datetime.now())
                if 'respuesta' in datos:
                    campos.append("respuesta = %s")
                    valores.append(datos['respuesta'])
                if 'empleado_id' in datos:
                    campos.append("empleado_id = %s")
                    valores.append(datos['empleado_id'])
                
                if not campos:
                    return {'success': False, 'message': 'No hay datos para actualizar'}
                
                valores.append(incidencia_id)
                sql = f"UPDATE INCIDENCIA SET {', '.join(campos)} WHERE incidencia_id = %s"
                cursor.execute(sql, valores)
                conexion.commit()
                return {
                    'success': True,
                    'message': 'Incidencia actualizada exitosamente'
                }
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error al actualizar incidencia: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error al actualizar incidencia: {str(e)}'
            }
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def obtener_incidencia(incidencia_id):
        """Obtiene una incidencia específica por su ID"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                # --- CORRECCIÓN: Se quitó 'i.numero_comprobante' ---
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia AS titulo,
                        i.mensaje AS descripcion,
                        DATE_FORMAT(i.fecha_envio, '%%d/%%m/%%Y') AS fecha_envio,
                        DATE_FORMAT(i.fecha_resolucion, '%%d/%%m/%%Y') AS fecha_resolucion,
                        i.estado,
                        CASE i.estado
                            WHEN 1 THEN 'Aprobado'
                            WHEN 2 THEN 'Rechazado'
                            ELSE 'En proceso'
                        END AS estado_texto,
                        i.respuesta,
                        i.tipo_incidencia_id,
                        t.nombre as tipo_incidencia,
                        CONCAT(c.nombres, ' ', c.ape_paterno) as cliente_nombre,
                        i.prueba,
                        i.cliente_id
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    LEFT JOIN CLIENTE c ON i.cliente_id = c.cliente_id
                    WHERE i.incidencia_id = %s
                """
                cursor.execute(sql, (incidencia_id,)) # Con parámetros, '%%' está bien
                inc = cursor.fetchone()
                
                if not inc:
                    return None
                
                if inc['prueba']:
                    inc['imagen'] = base64.b64encode(inc['prueba']).decode('utf-8')
                else:
                    inc['imagen'] = None
                del inc['prueba']

                return inc
        except Exception as e:
            print(f"Error al obtener incidencia: {e}")
            traceback.print_exc()
            return None
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def eliminar_incidencia(incidencia_id):
        """Elimina una incidencia"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = "DELETE FROM INCIDENCIA WHERE incidencia_id = %s"
                cursor.execute(sql, (incidencia_id,))
                conexion.commit()
                return {
                    'success': True,
                    'message': 'Incidencia eliminada exitosamente'
                }
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error al eliminar incidencia: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Error al eliminar incidencia: {str(e)}'
            }
        finally:
            if conexion:
                conexion.close()