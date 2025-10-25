from bd import get_connection
import hashlib
from datetime import date

def hash_password(password):
    """
    Hashea la contraseña usando SHA256
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_usuario(usuario, contrasena):
    """
    Verifica las credenciales del usuario
    Retorna el usuario si es válido, None si no
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            contrasena_hash = hash_password(contrasena)
            sql = """
                SELECT u.usuario_id, u.usuario, u.email, u.estado, r.rol_id, r.nombre_rol
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                WHERE u.usuario = %s AND u.contrasena = %s AND u.estado = 1
            """
            cursor.execute(sql, (usuario, contrasena_hash))
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'usuario_id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2],
                    'estado': resultado[3],
                    'rol_id': resultado[4],
                    'rol_nombre': resultado[5]
                }
            return None
    except Exception as ex:
        print(f"Error al verificar usuario: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def get_usuario_by_id(usuario_id):
    """
    Obtiene un usuario por su ID
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = """
                SELECT u.usuario_id, u.usuario, u.email, u.estado, u.fecha_creacion, 
                       r.rol_id, r.nombre_rol
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                WHERE u.usuario_id = %s
            """
            cursor.execute(sql, (usuario_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'usuario_id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2],
                    'estado': resultado[3],
                    'fecha_creacion': resultado[4],
                    'rol_id': resultado[5],
                    'rol_nombre': resultado[6]
                }
            return None
    except Exception as ex:
        print(f"Error al obtener usuario: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def get_usuario_by_username(usuario):
    """
    Obtiene un usuario por su nombre de usuario
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT usuario_id, usuario, email FROM USUARIO WHERE usuario = %s"
            cursor.execute(sql, (usuario,))
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'usuario_id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2]
                }
            return None
    except Exception as ex:
        print(f"Error al buscar usuario: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def get_usuario_by_email(email):
    """
    Obtiene un usuario por su email
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT usuario_id, usuario, email FROM USUARIO WHERE email = %s"
            cursor.execute(sql, (email,))
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'usuario_id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2]
                }
            return None
    except Exception as ex:
        print(f"Error al buscar usuario por email: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def insert_usuario(usuario, contrasena, email, id_rol=2, nombres='', apellido_paterno='', 
                   apellido_materno='', tipo_documento_id=1, num_documento='', sexo='M', telefono=''):
    """
    Inserta un nuevo usuario en la base de datos con sus datos personales
    Por defecto, id_rol=2 (cliente/usuario normal)
    """
    conexion = None
    try:
        # Verificar si el usuario o email ya existen
        if get_usuario_by_username(usuario):
            return {'success': False, 'message': 'El nombre de usuario ya existe'}
        
        if get_usuario_by_email(email):
            return {'success': False, 'message': 'El email ya está registrado'}
        
        conexion = get_connection()
        with conexion.cursor() as cursor:
            contrasena_hash = hash_password(contrasena)
            fecha_actual = date.today()
            
            # Insertar usuario
            sql = """
                INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol)
                VALUES (%s, %s, %s, 1, %s, %s)
            """
            cursor.execute(sql, (usuario, contrasena_hash, email, fecha_actual, id_rol))
            usuario_id = cursor.lastrowid  # Obtener el ID del usuario recién creado
            
            print(f"✓ Usuario creado con ID: {usuario_id}")
            
            # Insertar perfil (si hay datos personales y la tabla existe)
            if nombres and apellido_paterno and num_documento:
                try:
                    # Convertir tipo_documento_id a int
                    tipo_doc_id = int(tipo_documento_id) if tipo_documento_id else 1
                    
                    sql_perfil = """
                        INSERT INTO PERFIL_USUARIO 
                        (usuario_id, nombres, apellido_paterno, apellido_materno,
                         tipo_documento_id, num_documento, sexo, telefono)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_perfil, (usuario_id, nombres, apellido_paterno, apellido_materno,
                                               tipo_doc_id, num_documento, sexo, telefono or None))
                    print(f"✓ Perfil creado para usuario_id: {usuario_id}")
                    print(f"  - Nombres: {nombres} {apellido_paterno} {apellido_materno}")
                    print(f"  - Documento: {num_documento}")
                except Exception as e:
                    print(f"⚠ Error al crear PERFIL_USUARIO: {e}")
                    print(f"  Datos: usuario_id={usuario_id}, nombres={nombres}")
                    # No es crítico, el usuario se creó correctamente
            else:
                print(f"⚠ No se creó perfil (faltan datos personales)")
            
            conexion.commit()
            return {'success': True, 'message': 'Usuario registrado exitosamente', 'usuario_id': usuario_id}
    except Exception as ex:
        print(f"❌ Error al insertar usuario: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al registrar usuario: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

def update_usuario(usuario_id, usuario, email, id_rol):
    """
    Actualiza los datos de un usuario
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = """
                UPDATE USUARIO 
                SET usuario = %s, email = %s, id_rol = %s
                WHERE usuario_id = %s
            """
            cursor.execute(sql, (usuario, email, id_rol, usuario_id))
            conexion.commit()
            return True
    except Exception as ex:
        print(f"Error al actualizar usuario: {ex}")
        if conexion:
            conexion.rollback()
        return False
    finally:
        if conexion:
            conexion.close()

def cambiar_contrasena(usuario_id, contrasena_actual, contrasena_nueva):
    """
    Cambia la contraseña de un usuario
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Verificar contraseña actual
            contrasena_actual_hash = hash_password(contrasena_actual)
            sql_verificar = "SELECT usuario_id FROM USUARIO WHERE usuario_id = %s AND contrasena = %s"
            cursor.execute(sql_verificar, (usuario_id, contrasena_actual_hash))
            
            if not cursor.fetchone():
                return {'success': False, 'message': 'Contraseña actual incorrecta'}
            
            # Actualizar contraseña
            contrasena_nueva_hash = hash_password(contrasena_nueva)
            sql_actualizar = "UPDATE USUARIO SET contrasena = %s WHERE usuario_id = %s"
            cursor.execute(sql_actualizar, (contrasena_nueva_hash, usuario_id))
            conexion.commit()
            return {'success': True, 'message': 'Contraseña actualizada exitosamente'}
    except Exception as ex:
        print(f"Error al cambiar contraseña: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al cambiar contraseña: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

def get_roles():
    """
    Obtiene todos los roles disponibles
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT rol_id, nombre_rol, descripcion FROM ROL WHERE estado = 1"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            roles = []
            for row in resultados:
                roles.append({
                    'rol_id': row[0],
                    'nombre_rol': row[1],
                    'descripcion': row[2]
                })
            return roles
    except Exception as ex:
        print(f"Error al obtener roles: {ex}")
        return []
    finally:
        if conexion:
            conexion.close()

def get_usuarios(limit=10, offset=0, search_term=''):
    """
    Obtiene una lista de usuarios con paginación y búsqueda
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            if search_term:
                sql = """
                    SELECT u.usuario_id, u.usuario, u.email, u.estado, u.fecha_creacion, r.nombre_rol
                    FROM USUARIO u
                    INNER JOIN ROL r ON u.id_rol = r.rol_id
                    WHERE u.usuario LIKE %s OR u.email LIKE %s
                    ORDER BY u.usuario_id DESC
                    LIMIT %s OFFSET %s
                """
                search_pattern = f"%{search_term}%"
                cursor.execute(sql, (search_pattern, search_pattern, limit, offset))
            else:
                sql = """
                    SELECT u.usuario_id, u.usuario, u.email, u.estado, u.fecha_creacion, r.nombre_rol
                    FROM USUARIO u
                    INNER JOIN ROL r ON u.id_rol = r.rol_id
                    ORDER BY u.usuario_id DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (limit, offset))
            
            resultados = cursor.fetchall()
            usuarios = []
            for row in resultados:
                usuarios.append({
                    'usuario_id': row[0],
                    'usuario': row[1],
                    'email': row[2],
                    'estado': row[3],
                    'fecha_creacion': row[4],
                    'rol_nombre': row[5]
                })
            return usuarios
    except Exception as ex:
        print(f"Error al obtener usuarios: {ex}")
        return []
    finally:
        if conexion:
            conexion.close()

def count_usuarios(search_term=''):
    """
    Cuenta el total de usuarios
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            if search_term:
                sql = "SELECT COUNT(*) FROM USUARIO WHERE usuario LIKE %s OR email LIKE %s"
                search_pattern = f"%{search_term}%"
                cursor.execute(sql, (search_pattern, search_pattern))
            else:
                sql = "SELECT COUNT(*) FROM USUARIO"
                cursor.execute(sql)
            
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
    except Exception as ex:
        print(f"Error al contar usuarios: {ex}")
        return 0
    finally:
        if conexion:
            conexion.close()

def get_perfil_completo(usuario_id):
    """
    Obtiene el perfil completo del usuario con datos personales
    """
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Primero obtener datos del usuario
            sql = """
                SELECT u.usuario_id, u.usuario, u.email, u.estado, u.fecha_creacion,
                       r.rol_id, r.nombre_rol
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                WHERE u.usuario_id = %s
            """
            cursor.execute(sql, (usuario_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                print(f"⚠ No se encontró usuario con ID: {usuario_id}")
                return None
            
            perfil = {
                'usuario_id': resultado[0],
                'usuario': resultado[1],
                'email': resultado[2],
                'estado': resultado[3],
                'fecha_creacion': resultado[4],
                'rol_id': resultado[5],
                'rol_nombre': resultado[6],
                'nombres': '',
                'apellido_paterno': '',
                'apellido_materno': '',
                'tipo_documento_id': 1,
                'num_documento': '',
                'sexo': 'M',
                'telefono': ''
            }
            
            print(f"✓ Usuario encontrado: {resultado[1]} (ID: {resultado[0]})")
            
            # Intentar obtener datos del perfil (si existe la tabla)
            try:
                sql_perfil = """
                    SELECT nombres, apellido_paterno, apellido_materno, 
                           tipo_documento_id, num_documento, sexo, telefono
                    FROM PERFIL_USUARIO
                    WHERE usuario_id = %s
                """
                cursor.execute(sql_perfil, (usuario_id,))
                perfil_data = cursor.fetchone()
                
                if perfil_data:
                    print(f"✓ Perfil encontrado en PERFIL_USUARIO")
                    perfil['nombres'] = perfil_data[0] or ''
                    perfil['apellido_paterno'] = perfil_data[1] or ''
                    perfil['apellido_materno'] = perfil_data[2] or ''
                    perfil['tipo_documento_id'] = perfil_data[3] or 1
                    perfil['num_documento'] = perfil_data[4] or ''
                    perfil['sexo'] = perfil_data[5] or 'M'
                    perfil['telefono'] = perfil_data[6] or ''
                    print(f"  - Nombres: {perfil['nombres']} {perfil['apellido_paterno']}")
                    print(f"  - Documento: {perfil['num_documento']}")
                else:
                    print(f"⚠ No hay perfil en PERFIL_USUARIO para usuario_id: {usuario_id}")
            except Exception as e:
                print(f"⚠ Error al buscar en PERFIL_USUARIO: {e}")
                # No es un error crítico, continuar con valores por defecto
            
            return perfil
    except Exception as ex:
        print(f"❌ Error al obtener perfil completo: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def update_perfil_usuario(usuario_id, email, nombres, apellido_paterno, apellido_materno, 
                          tipo_documento_id, num_documento, sexo, telefono):
    """
    Actualiza los datos del perfil del usuario
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Actualizar email en USUARIO
            sql_usuario = "UPDATE USUARIO SET email = %s WHERE usuario_id = %s"
            cursor.execute(sql_usuario, (email, usuario_id))
            
            # Intentar actualizar/crear perfil (si la tabla existe)
            try:
                # Verificar si existe perfil
                sql_check = "SELECT perfil_id FROM PERFIL_USUARIO WHERE usuario_id = %s"
                cursor.execute(sql_check, (usuario_id,))
                perfil_existe = cursor.fetchone()
                
                if perfil_existe:
                    # Actualizar perfil existente
                    sql_perfil = """
                        UPDATE PERFIL_USUARIO 
                        SET nombres = %s, apellido_paterno = %s, apellido_materno = %s,
                            tipo_documento_id = %s, num_documento = %s, sexo = %s, telefono = %s
                        WHERE usuario_id = %s
                    """
                    cursor.execute(sql_perfil, (nombres, apellido_paterno, apellido_materno,
                                               tipo_documento_id, num_documento, sexo, telefono,
                                               usuario_id))
                else:
                    # Crear nuevo perfil
                    sql_insert = """
                        INSERT INTO PERFIL_USUARIO 
                        (usuario_id, nombres, apellido_paterno, apellido_materno,
                         tipo_documento_id, num_documento, sexo, telefono)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (usuario_id, nombres, apellido_paterno, apellido_materno,
                                               tipo_documento_id, num_documento, sexo, telefono))
            except Exception as e:
                print(f"Nota: No se pudo actualizar PERFIL_USUARIO (tabla no existe): {e}")
                # Solo actualizar el email es suficiente por ahora
            
            conexion.commit()
            return {'success': True, 'message': 'Perfil actualizado exitosamente'}
    except Exception as ex:
        print(f"Error al actualizar perfil: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al actualizar perfil: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

def get_tipos_documento():
    """
    Obtiene todos los tipos de documento
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = "SELECT tipo_doc_id, nombre_tipo_doc FROM TIPO_DOCUMENTO WHERE estado = 1"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            
            tipos = []
            for row in resultados:
                tipos.append({
                    'tipo_doc_id': row[0],
                    'nombre_tipo_doc': row[1]
                })
            
            # Si no hay tipos, devolver al menos uno por defecto
            if not tipos:
                tipos = [{'tipo_doc_id': 1, 'nombre_tipo_doc': 'DNI'}]
            
            return tipos
    except Exception as ex:
        print(f"Error al obtener tipos de documento: {ex}")
        # Devolver tipo por defecto si hay error
        return [{'tipo_doc_id': 1, 'nombre_tipo_doc': 'DNI'}]
    finally:
        if conexion:
            conexion.close()

