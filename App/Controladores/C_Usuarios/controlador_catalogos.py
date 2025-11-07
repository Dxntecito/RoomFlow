"""
Controlador para gestionar catálogos relacionados con usuarios:
- PAIS
- ROL
- TIPO_DOCUMENTO
- TIPO_CLIENTE
- TIPO_EMPRESA
"""

from bd import get_connection

# ========================================
# CATÁLOGO: PAIS
# ========================================

def get_paises():
    """Obtiene todos los países"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT pais_id, nombre, estado FROM PAIS ORDER BY nombre"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            paises = []
            for row in resultados:
                paises.append({
                    'pais_id': row[0],
                    'nombre': row[1],
                    'estado': row[2]
                })
            return {'success': True, 'paises': paises}
    except Exception as e:
        print(f"Error al obtener países: {e}")
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def insert_pais(nombre, estado):
    """Inserta un nuevo país"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO PAIS (nombre, estado) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, estado))
            conexion.commit()
            return {'success': True, 'message': 'País creado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def update_pais(pais_id, nombre, estado):
    """Actualiza un país"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "UPDATE PAIS SET nombre = %s, estado = %s WHERE pais_id = %s"
            cursor.execute(sql, (nombre, estado, pais_id))
            conexion.commit()
            return {'success': True, 'message': 'País actualizado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def delete_pais(pais_id):
    """Elimina un país"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "DELETE FROM PAIS WHERE pais_id = %s"
            cursor.execute(sql, (pais_id,))
            conexion.commit()
            return {'success': True, 'message': 'País eliminado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': 'No se puede eliminar: ' + str(e)}
    finally:
        if conexion:
            conexion.close()

# ========================================
# CATÁLOGO: ROL
# ========================================

def get_roles():
    """Obtiene todos los roles"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT rol_id, nombre_rol, descripcion, estado FROM ROL ORDER BY rol_id"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            roles = []
            for row in resultados:
                roles.append({
                    'rol_id': row[0],
                    'nombre_rol': row[1],
                    'descripcion': row[2],
                    'estado': row[3]
                })
            return {'success': True, 'roles': roles}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def insert_rol(nombre_rol, descripcion, estado):
    """Inserta un nuevo rol"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO ROL (nombre_rol, descripcion, estado) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre_rol, descripcion, estado))
            conexion.commit()
            return {'success': True, 'message': 'Rol creado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def update_rol(rol_id, nombre_rol, descripcion, estado):
    """Actualiza un rol"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "UPDATE ROL SET nombre_rol = %s, descripcion = %s, estado = %s WHERE rol_id = %s"
            cursor.execute(sql, (nombre_rol, descripcion, estado, rol_id))
            conexion.commit()
            return {'success': True, 'message': 'Rol actualizado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def delete_rol(rol_id):
    """Elimina un rol"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "DELETE FROM ROL WHERE rol_id = %s"
            cursor.execute(sql, (rol_id,))
            conexion.commit()
            return {'success': True, 'message': 'Rol eliminado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': 'No se puede eliminar: ' + str(e)}
    finally:
        if conexion:
            conexion.close()

# ========================================
# CATÁLOGO: TIPO_DOCUMENTO
# ========================================

def get_tipos_documento():
    """Obtiene todos los tipos de documento"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT tipo_doc_id, nombre_tipo_doc, estado FROM TIPO_DOCUMENTO ORDER BY nombre_tipo_doc"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            tipos = []
            for row in resultados:
                tipos.append({
                    'tipo_doc_id': row[0],
                    'nombre_tipo_doc': row[1],
                    'estado': row[2]
                })
            return {'success': True, 'tipos': tipos}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def insert_tipo_documento(nombre_tipo_doc, estado):
    """Inserta un nuevo tipo de documento"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO TIPO_DOCUMENTO (nombre_tipo_doc, estado) VALUES (%s, %s)"
            cursor.execute(sql, (nombre_tipo_doc, estado))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de documento creado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def update_tipo_documento(tipo_doc_id, nombre_tipo_doc, estado):
    """Actualiza un tipo de documento"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "UPDATE TIPO_DOCUMENTO SET nombre_tipo_doc = %s, estado = %s WHERE tipo_doc_id = %s"
            cursor.execute(sql, (nombre_tipo_doc, estado, tipo_doc_id))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de documento actualizado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def delete_tipo_documento(tipo_doc_id):
    """Elimina un tipo de documento"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "DELETE FROM TIPO_DOCUMENTO WHERE tipo_doc_id = %s"
            cursor.execute(sql, (tipo_doc_id,))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de documento eliminado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': 'No se puede eliminar: ' + str(e)}
    finally:
        if conexion:
            conexion.close()

# ========================================
# CATÁLOGO: TIPO_CLIENTE
# ========================================

def get_tipos_cliente():
    """Obtiene todos los tipos de cliente"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT tipo_cliente_id, descripcion, estado FROM TIPO_CLIENTE ORDER BY descripcion"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            tipos = []
            for row in resultados:
                tipos.append({
                    'tipo_cliente_id': row[0],
                    'descripcion': row[1],
                    'estado': row[2]
                })
            return {'success': True, 'tipos': tipos}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def insert_tipo_cliente(tipo_cliente_id, descripcion, estado):
    """Inserta un nuevo tipo de cliente"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO TIPO_CLIENTE (tipo_cliente_id, descripcion, estado) VALUES (%s, %s, %s)"
            cursor.execute(sql, (tipo_cliente_id, descripcion, estado))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de cliente creado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def update_tipo_cliente(old_id, new_id, descripcion, estado):
    """Actualiza un tipo de cliente"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "UPDATE TIPO_CLIENTE SET tipo_cliente_id = %s, descripcion = %s, estado = %s WHERE tipo_cliente_id = %s"
            cursor.execute(sql, (new_id, descripcion, estado, old_id))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de cliente actualizado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def delete_tipo_cliente(tipo_cliente_id):
    """Elimina un tipo de cliente"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "DELETE FROM TIPO_CLIENTE WHERE tipo_cliente_id = %s"
            cursor.execute(sql, (tipo_cliente_id,))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de cliente eliminado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': 'No se puede eliminar: ' + str(e)}
    finally:
        if conexion:
            conexion.close()

# ========================================
# CATÁLOGO: TIPO_EMPRESA
# ========================================

def get_tipos_empresa():
    """Obtiene todos los tipos de empresa"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT tipo_id, nombre_tipo, estado FROM TIPO_EMPRESA ORDER BY nombre_tipo"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            tipos = []
            for row in resultados:
                tipos.append({
                    'tipo_id': row[0],
                    'nombre_tipo': row[1],
                    'estado': row[2]
                })
            return {'success': True, 'tipos': tipos}
    except Exception as e:
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def insert_tipo_empresa(nombre_tipo, estado):
    """Inserta un nuevo tipo de empresa"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO TIPO_EMPRESA (nombre_tipo, estado) VALUES (%s, %s)"
            cursor.execute(sql, (nombre_tipo, estado))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de empresa creado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def update_tipo_empresa(tipo_id, nombre_tipo, estado):
    """Actualiza un tipo de empresa"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "UPDATE TIPO_EMPRESA SET nombre_tipo = %s, estado = %s WHERE tipo_id = %s"
            cursor.execute(sql, (nombre_tipo, estado, tipo_id))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de empresa actualizado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        if conexion:
            conexion.close()

def delete_tipo_empresa(tipo_id):
    """Elimina un tipo de empresa"""
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "DELETE FROM TIPO_EMPRESA WHERE tipo_id = %s"
            cursor.execute(sql, (tipo_id,))
            conexion.commit()
            return {'success': True, 'message': 'Tipo de empresa eliminado exitosamente'}
    except Exception as e:
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': 'No se puede eliminar: ' + str(e)}
    finally:
        if conexion:
            conexion.close()

