from bd import get_connection
import traceback
import pymysql.cursors # <--- 1. IMPORTA EL CURSOR DE DICCIONARIO

class ControladorPromocion:
    
    @staticmethod
    def listar_promociones():
        """Lista todas las promociones con su tipo"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                # --- SOLUCIÓN AQUÍ: Cambiado de %% a % ---
                sql = """
                    SELECT 
                        P.id_promocion, P.porcentaje, P.descripcion, P.estado,
                        DATE_FORMAT(P.fecha_inicio, '%d/%m/%Y') AS fecha_inicio,
                        DATE_FORMAT(P.fecha_fin, '%d/%m/%Y') AS fecha_fin,
                        TP.nombre AS tipo_promocion,
                        IF(P.estado = 1, 'Activa', 'Inactiva') AS nombre_estado
                    FROM PROMOCION P
                    JOIN TIPO_PROMOCION TP ON P.tipo_promocion_id = TP.id_tipo_promocion
                    ORDER BY P.fecha_inicio DESC
                """
                # --- FIN DE LA SOLUCIÓN ---
                cursor.execute(sql)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar promociones: {e}")
            traceback.print_exc()
            return []
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def get_tipos_promocion():
        """Obtiene todos los tipos de promoción activos para un dropdown"""
        conexion = None
        try:
            conexion = get_connection()
            # 2. USA EL CURSOR DE DICCIONARIO
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id_tipo_promocion, nombre FROM TIPO_PROMOCION WHERE estado = 1")
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener tipos de promoción: {e}")
            traceback.print_exc()
            return []
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def crear_promocion(datos):
        """Guarda una nueva promoción en la base de datos"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor: # No necesita DictCursor
                sql = """
                    INSERT INTO PROMOCION
                    (porcentaje, descripcion, estado, fecha_inicio, fecha_fin, tipo_promocion_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (
                    datos.get('porcentaje'),
                    datos.get('descripcion'),
                    1,
                    datos.get('fecha_inicio'),
                    datos.get('fecha_fin'),
                    datos.get('tipo_promocion_id')
                )
                cursor.execute(sql, valores)
                conexion.commit()
                return {'success': True, 'message': 'Promoción creada exitosamente.', 'id_promocion': cursor.lastrowid}
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error al crear promoción: {e}")
            traceback.print_exc()
            return {'success': False, 'message': f'Error al crear promoción: {str(e)}'}
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def cambiar_estado_promocion(promocion_id, nuevo_estado):
        """Actualiza el estado de una promoción (0=Inactiva, 1=Activa)"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor: # No necesita DictCursor
                sql = "UPDATE PROMOCION SET estado = %s WHERE id_promocion = %s"
                cursor.execute(sql, (nuevo_estado, promocion_id))
                conexion.commit()
                
                if cursor.rowcount == 0:
                     return {'success': False, 'message': 'No se encontró la promoción.'}
                return {'success': True, 'message': 'Estado actualizado.'}
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error al cambiar estado de promoción: {e}")
            traceback.print_exc()
            return {'success': False, 'message': f'Error al cambiar estado: {str(e)}'}
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def obtener_promocion(promocion_id):
        """Obtiene una promoción específica por su ID"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                # --- SOLUCIÓN AQUÍ: Cambiado de %% a % ---
                sql = """
                    SELECT 
                        P.id_promocion, P.porcentaje, P.descripcion, P.estado,
                        DATE_FORMAT(P.fecha_inicio, '%d/%m/%Y') AS fecha_inicio,
                        DATE_FORMAT(P.fecha_fin, '%d/%m/%Y') AS fecha_fin,
                        P.tipo_promocion_id,
                        TP.nombre AS tipo_promocion
                    FROM PROMOCION P
                    JOIN TIPO_PROMOCION TP ON P.tipo_promocion_id = TP.id_tipo_promocion
                    WHERE P.id_promocion = %s
                """
                # --- FIN DE LA SOLUCIÓN ---
                
                # ¡OJO! Aquí SÍ usamos %s para el ID, así que pasamos los parámetros
                cursor.execute(sql, (promocion_id,))
                promocion = cursor.fetchone()
                
                if not promocion:
                    return None
                return promocion
        except Exception as e:
            print(f"Error al obtener promoción: {e}")
            traceback.print_exc()
            return None
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def actualizar_promocion(promocion_id, datos):
        """Actualiza los datos de una promoción"""
        conexion = None
        try:
            conexion = get_connection()
            with conexion.cursor() as cursor: # No necesita DictCursor
                campos = []
                valores = []
                
                if 'porcentaje' in datos:
                    campos.append("porcentaje = %s")
                    valores.append(datos['porcentaje'])
                if 'descripcion' in datos:
                    campos.append("descripcion = %s")
                    valores.append(datos['descripcion'])
                if 'fecha_inicio' in datos:
                    campos.append("fecha_inicio = %s")
                    valores.append(datos['fecha_inicio'])
                if 'fecha_fin' in datos:
                    campos.append("fecha_fin = %s")
                    valores.append(datos['fecha_fin'])
                if 'tipo_promocion_id' in datos:
                    campos.append("tipo_promocion_id = %s")
                    valores.append(datos['tipo_promocion_id'])
                
                if not campos:
                    return {'success': False, 'message': 'No hay datos para actualizar'}

                valores.append(promocion_id)
                sql = f"UPDATE PROMOCION SET {', '.join(campos)} WHERE id_promocion = %s"
                
                cursor.execute(sql, valores)
                conexion.commit()
                return {'success': True, 'message': 'Promoción actualizada.'}
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error al actualizar promoción: {e}")
            traceback.print_exc()
            return {'success': False, 'message': f'Error al actualizar: {str(e)}'}
        finally:
            if conexion:
                conexion.close()