from bd import get_connection
from datetime import datetime
import base64

class ControladorIncidencia:
    """Controlador para gestionar las incidencias del sistema"""
    
    @staticmethod
    def obtener_tipos_incidencia():
        """Obtiene todos los tipos de incidencia activos"""
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = """
                    SELECT id_tipo, nombre, estado 
                    FROM TIPO_INCIDENCIA 
                    WHERE estado = 1
                    ORDER BY nombre
                """
                cursor.execute(sql)
                tipos = cursor.fetchall()
                
                resultado = []
                for tipo in tipos:
                    resultado.append({
                        'id_tipo': tipo[0],
                        'nombre': tipo[1],
                        'estado': tipo[2]
                    })
                
                return resultado
        except Exception as e:
            print(f"Error al obtener tipos de incidencia: {e}")
            return []
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def obtener_todas_incidencias():
        """Obtiene todas las incidencias del sistema (para administradores)"""
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia,
                        i.mensaje,
                        i.fecha_envio,
                        i.fecha_resolucion,
                        i.estado,
                        i.numero_comprobante,
                        i.respuesta,
                        ti.nombre as tipo_incidencia,
                        c.nombres,
                        c.ape_paterno,
                        c.ape_materno,
                        c.num_doc,
                        c.telefono
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA ti ON i.id_tipo_incidencia = ti.id_tipo
                    INNER JOIN CLIENTE c ON i.id_cliente = c.cliente_id
                    ORDER BY i.fecha_envio DESC
                """
                cursor.execute(sql)
                incidencias = cursor.fetchall()
                
                resultado = []
                for inc in incidencias:
                    # Determinar estado
                    estado_texto = "En proceso"
                    if inc[5] == 1:
                        estado_texto = "Aprobado"
                    elif inc[5] == 2:
                        estado_texto = "Rechazado"
                    
                    resultado.append({
                        'incidencia_id': inc[0],
                        'titulo': inc[1],
                        'descripcion': inc[2],
                        'fecha_envio': inc[3].strftime('%d/%m/%Y %H:%M') if inc[3] else '',
                        'fecha_resolucion': inc[4].strftime('%d/%m/%Y %H:%M') if inc[4] else '',
                        'estado': inc[5],
                        'estado_texto': estado_texto,
                        'numero_comprobante': inc[6],
                        'respuesta': inc[7],
                        'tipo_incidencia': inc[8],
                        'tipo_incidencia_id': inc[8],
                        'cliente_nombre': f"{inc[9]} {inc[10]} {inc[11]}",
                        'cliente_documento': inc[12],
                        'cliente_telefono': inc[13]
                    })
                
                return resultado
        except Exception as e:
            print(f"Error al obtener todas las incidencias: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_incidencias_cliente(cliente_id):
        """Obtiene todas las incidencias de un cliente"""
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia,
                        i.mensaje,
                        i.fecha_envio,
                        i.fecha_resolucion,
                        i.estado,
                        i.numero_comprobante,
                        i.respuesta,
                        t.nombre as tipo_incidencia,
                        i.prueba
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    WHERE i.cliente_id = %s
                    ORDER BY i.fecha_envio DESC
                """
                cursor.execute(sql, (cliente_id,))
                incidencias = cursor.fetchall()
                
                resultado = []
                for inc in incidencias:
                    # Estado: 1=Aprobado, 2=Rechazado, 3=En proceso
                    estado_texto = {1: 'Aprobado', 2: 'Rechazado', 3: 'En proceso'}.get(inc[5], 'En proceso')
                    
                    # Convertir imagen blob a base64 si existe
                    imagen_base64 = None
                    if inc[9]:
                        imagen_base64 = base64.b64encode(inc[9]).decode('utf-8')
                    
                    resultado.append({
                        'incidencia_id': inc[0],
                        'titulo': inc[1],
                        'descripcion': inc[2],
                        'fecha_envio': inc[3].strftime('%d/%m/%Y') if inc[3] else '',
                        'fecha_resolucion': inc[4].strftime('%d/%m/%Y') if inc[4] else '',
                        'estado': inc[5],
                        'estado_texto': estado_texto,
                        'numero_comprobante': inc[6] if inc[6] else '',
                        'respuesta': inc[7] if inc[7] else '',
                        'tipo_incidencia': inc[8],
                        'imagen': imagen_base64
                    })
                
                return resultado
        except Exception as e:
            print(f"Error al obtener incidencias del cliente: {e}")
            return []
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def crear_incidencia(datos):
        """Crea una nueva incidencia"""
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO INCIDENCIA 
                    (nombre_incidencia, mensaje, fecha_envio, estado, 
                     tipo_incidencia_id, numero_comprobante, prueba, cliente_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Estado por defecto: 3 (En proceso)
                valores = (
                    datos['titulo'],
                    datos['descripcion'],
                    datetime.now().date(),
                    3,  # Estado: En proceso
                    datos['tipo_incidencia_id'],
                    datos.get('numero_comprobante', None),
                    datos.get('evidencia', None),  # Blob de la imagen
                    datos['cliente_id']
                )
                
                cursor.execute(sql, valores)
                conexion.commit()
                
                return {
                    'success': True,
                    'message': 'Incidencia creada exitosamente',
                    'incidencia_id': cursor.lastrowid
                }
        except Exception as e:
            print(f"Error al crear incidencia: {e}")
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
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                # Construir query dinámicamente según los datos recibidos
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
                
                if 'numero_comprobante' in datos:
                    campos.append("numero_comprobante = %s")
                    valores.append(datos['numero_comprobante'])
                
                if 'evidencia' in datos:
                    campos.append("prueba = %s")
                    valores.append(datos['evidencia'])
                
                if 'estado' in datos:
                    campos.append("estado = %s")
                    valores.append(datos['estado'])
                    
                    # Si se está aprobando o rechazando, agregar fecha de resolución
                    if datos['estado'] in [1, 2]:
                        campos.append("fecha_resolucion = %s")
                        valores.append(datetime.now().date())
                
                if 'respuesta' in datos:
                    campos.append("respuesta = %s")
                    valores.append(datos['respuesta'])
                
                if not campos:
                    return {'success': False, 'message': 'No hay datos para actualizar'}
                
                valores.append(incidencia_id)
                
                sql = f"""
                    UPDATE INCIDENCIA 
                    SET {', '.join(campos)}
                    WHERE incidencia_id = %s
                """
                
                cursor.execute(sql, valores)
                conexion.commit()
                
                return {
                    'success': True,
                    'message': 'Incidencia actualizada exitosamente'
                }
        except Exception as e:
            print(f"Error al actualizar incidencia: {e}")
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
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia,
                        i.mensaje,
                        i.fecha_envio,
                        i.fecha_resolucion,
                        i.estado,
                        i.numero_comprobante,
                        i.respuesta,
                        i.tipo_incidencia_id,
                        t.nombre as tipo_incidencia,
                        i.prueba,
                        i.cliente_id
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    WHERE i.incidencia_id = %s
                """
                cursor.execute(sql, (incidencia_id,))
                inc = cursor.fetchone()
                
                if not inc:
                    return None
                
                # Estado: 1=Aprobado, 2=Rechazado, 3=En proceso
                estado_texto = {1: 'Aprobado', 2: 'Rechazado', 3: 'En proceso'}.get(inc[5], 'En proceso')
                
                # Convertir imagen blob a base64 si existe
                imagen_base64 = None
                if inc[10]:
                    imagen_base64 = base64.b64encode(inc[10]).decode('utf-8')
                
                return {
                    'incidencia_id': inc[0],
                    'titulo': inc[1],
                    'descripcion': inc[2],
                    'fecha_envio': inc[3].strftime('%d/%m/%Y') if inc[3] else '',
                    'fecha_resolucion': inc[4].strftime('%d/%m/%Y') if inc[4] else '',
                    'estado': inc[5],
                    'estado_texto': estado_texto,
                    'numero_comprobante': inc[6] if inc[6] else '',
                    'respuesta': inc[7] if inc[7] else '',
                    'tipo_incidencia_id': inc[8],
                    'tipo_incidencia': inc[9],
                    'imagen': imagen_base64,
                    'cliente_id': inc[11]
                }
        except Exception as e:
            print(f"Error al obtener incidencia: {e}")
            return None
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def eliminar_incidencia(incidencia_id):
        """Elimina una incidencia"""
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
            print(f"Error al eliminar incidencia: {e}")
            return {
                'success': False,
                'message': f'Error al eliminar incidencia: {str(e)}'
            }
        finally:
            if conexion:
                conexion.close()
    
    @staticmethod
    def obtener_todas_incidencias():
        """Obtiene todas las incidencias (para administradores)"""
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor:
                sql = """
                    SELECT 
                        i.incidencia_id,
                        i.nombre_incidencia,
                        i.mensaje,
                        i.fecha_envio,
                        i.fecha_resolucion,
                        i.estado,
                        i.numero_comprobante,
                        i.respuesta,
                        t.nombre as tipo_incidencia,
                        CONCAT(c.nombres, ' ', c.ape_paterno, ' ', c.ape_materno) as cliente_nombre,
                        i.cliente_id
                    FROM INCIDENCIA i
                    INNER JOIN TIPO_INCIDENCIA t ON i.tipo_incidencia_id = t.id_tipo
                    LEFT JOIN CLIENTE c ON i.cliente_id = c.cliente_id
                    ORDER BY i.fecha_envio DESC
                """
                cursor.execute(sql)
                incidencias = cursor.fetchall()
                
                resultado = []
                for inc in incidencias:
                    # Estado: 1=Aprobado, 2=Rechazado, 3=En proceso
                    estado_texto = {1: 'Aprobado', 2: 'Rechazado', 3: 'En proceso'}.get(inc[5], 'En proceso')
                    
                    resultado.append({
                        'incidencia_id': inc[0],
                        'titulo': inc[1],
                        'descripcion': inc[2],
                        'fecha_envio': inc[3].strftime('%d/%m/%Y') if inc[3] else '',
                        'fecha_resolucion': inc[4].strftime('%d/%m/%Y') if inc[4] else '',
                        'estado': inc[5],
                        'estado_texto': estado_texto,
                        'numero_comprobante': inc[6] if inc[6] else '',
                        'respuesta': inc[7] if inc[7] else '',
                        'tipo_incidencia': inc[8],
                        'cliente_nombre': inc[9],
                        'cliente_id': inc[10]
                    })
                
                return resultado
        except Exception as e:
            print(f"Error al obtener todas las incidencias: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

