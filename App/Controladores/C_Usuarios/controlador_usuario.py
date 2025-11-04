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
    Verifica las credenciales del usuario y obtiene datos del cliente asociado
    Retorna el usuario con datos del cliente si es válido, None si no
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            contrasena_hash = hash_password(contrasena)
            sql = """
                SELECT u.usuario_id, u.usuario, u.email, u.estado, r.rol_id, r.nombre_rol,
                       c.nombres, c.ape_paterno, c.ape_materno, c.num_doc, c.telefono
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                LEFT JOIN CLIENTE c ON u.cliente_id = c.cliente_id
                WHERE u.usuario = %s AND u.contrasena = %s AND u.estado = 1
            """
            cursor.execute(sql, (usuario, contrasena_hash))
            resultado = cursor.fetchone()
            
            if resultado:
                usuario_data = {
                    'usuario_id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2],
                    'estado': resultado[3],
                    'rol_id': resultado[4],
                    'rol_nombre': resultado[5],
                    'nombres': resultado[6] or '',
                    'apellido_paterno': resultado[7] or '',
                    'apellido_materno': resultado[8] or '',
                    'num_documento': resultado[9] or '',
                    'telefono': resultado[10] or ''
                }
                
                if resultado[6]:  # Si tiene nombres (datos de cliente)
                    print(f"✓ Datos del cliente cargados para usuario: {usuario}")
                else:
                    print(f"⚠ No se encontraron datos del cliente para usuario: {usuario}")
                
                return usuario_data
            return None
    except Exception as ex:
        print(f"Error al verificar usuario: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def get_usuario_by_id(usuario_id):
    """
    Obtiene un usuario por su ID con datos del cliente asociado
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = """
                SELECT u.usuario_id, u.usuario, u.email, u.estado, u.fecha_creacion, 
                       r.rol_id, r.nombre_rol,
                       c.nombres, c.ape_paterno, c.ape_materno, c.num_doc, c.telefono
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                LEFT JOIN CLIENTE c ON u.cliente_id = c.cliente_id
                WHERE u.usuario_id = %s
            """
            cursor.execute(sql, (usuario_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                usuario_data = {
                    'usuario_id': resultado[0],
                    'usuario': resultado[1],
                    'email': resultado[2],
                    'estado': resultado[3],
                    'fecha_creacion': resultado[4],
                    'rol_id': resultado[5],
                    'rol_nombre': resultado[6],
                    'nombres': resultado[7] or '',
                    'apellido_paterno': resultado[8] or '',
                    'apellido_materno': resultado[9] or '',
                    'num_documento': resultado[10] or '',
                    'telefono': resultado[11] or ''
                }
                
                if resultado[7]:  # Si tiene nombres (datos de cliente)
                    print(f"✓ Datos del cliente cargados para usuario_id: {usuario_id}")
                else:
                    print(f"⚠ No se encontraron datos del cliente para usuario_id: {usuario_id}")
                
                return usuario_data
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
                   apellido_materno='', tipo_documento_id=1, num_documento='', telefono='', direccion=''):
    """
    Inserta un nuevo usuario en la base de datos con sus datos personales de cliente
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
            
            cliente_id = None
            
            # Insertar cliente primero (si hay datos personales)
            if nombres and apellido_paterno and num_documento:
                try:
                    # Convertir tipo_documento_id a int
                    tipo_doc_id = int(tipo_documento_id) if tipo_documento_id else 1
                    
                    # Convertir telefono a None si está vacío para evitar problemas con UNIQUE
                    telefono_valor = telefono if telefono and telefono.strip() else None
                    direccion_valor = direccion if direccion and direccion.strip() else None
                    
                    sql_cliente = """
                        INSERT INTO CLIENTE 
                        (nombres, ape_paterno, ape_materno, num_doc, telefono, direccion,
                         f_registro, id_tipo_cliente, id_pais, tipo_doc_id)
                        VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), 'N', 1, %s)
                    """
                    cursor.execute(sql_cliente, (nombres, apellido_paterno, apellido_materno, 
                                               num_documento, telefono_valor, direccion_valor,
                                               tipo_doc_id))
                    cliente_id = cursor.lastrowid
                    print(f"✓ Cliente creado con ID: {cliente_id}")
                    print(f"  - Nombres: {nombres} {apellido_paterno} {apellido_materno}")
                    print(f"  - Documento: {num_documento}")
                except Exception as e:
                    print(f"❌ ERROR CRÍTICO al crear CLIENTE: {e}")
                    import traceback
                    traceback.print_exc()
                    # Si falla la creación del cliente, fallar todo el registro
                    if conexion:
                        conexion.rollback()
                    return {'success': False, 'message': f'Error al registrar cliente: {str(e)}'}
            
            # Insertar usuario con referencia al cliente
            sql_usuario = """
                INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol, cliente_id)
                VALUES (%s, %s, %s, 1, %s, %s, %s)
            """
            cursor.execute(sql_usuario, (usuario, contrasena_hash, email, fecha_actual, id_rol, cliente_id))
            usuario_id = cursor.lastrowid
            
            print(f"✓ Usuario creado con ID: {usuario_id}")
            if cliente_id:
                print(f"  - Asociado con cliente_id: {cliente_id}")
            
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
    Obtiene el perfil completo del usuario con datos personales del cliente o empleado
    """
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Primero obtener datos básicos del usuario para determinar si es cliente o empleado
            sql_usuario = """
                SELECT u.usuario_id, u.usuario, u.email, u.estado, u.fecha_creacion,
                       r.rol_id, r.nombre_rol, u.cliente_id, u.empleado_id
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                WHERE u.usuario_id = %s
            """
            cursor.execute(sql_usuario, (usuario_id,))
            resultado_usuario = cursor.fetchone()
            
            if not resultado_usuario:
                print(f"⚠ No se encontró usuario con ID: {usuario_id}")
                return None
            
            perfil = {
                'usuario_id': resultado_usuario[0],
                'usuario': resultado_usuario[1],
                'email': resultado_usuario[2],
                'estado': resultado_usuario[3],
                'fecha_creacion': resultado_usuario[4],
                'rol_id': resultado_usuario[5],
                'rol_nombre': resultado_usuario[6],
                'tipo_perfil': None,  # 'cliente' o 'empleado'
                'nombres': '',
                'apellido_paterno': '',
                'apellido_materno': '',
                'tipo_documento_id': 1,
                'num_documento': '',
                'telefono': '',
                'direccion': '',
                'id_pais': 1,
                # Campos específicos de empleado
                'cod_empleado': '',
                'sexo': '',
                'tipo_empleado_id': None,
                'tipo_empleado': '',
                'estado_empleado': ''
            }
            
            cliente_id = resultado_usuario[7]
            empleado_id = resultado_usuario[8]
            
            print(f"✓ Usuario encontrado: {resultado_usuario[1]} (ID: {resultado_usuario[0]})")
            print(f"  - cliente_id: {cliente_id}, empleado_id: {empleado_id}")
            
            # Determinar si es empleado o cliente y obtener sus datos
            if empleado_id:
                # Es un empleado
                sql_empleado = """
                    SELECT e.cod_empleado, e.dni, e.ape_paterno, e.ape_materno, e.nombres,
                           e.sexo, e.movil, e.tipo_empleado_id, e.estado,
                           te.nombre_tipo
                    FROM EMPLEADO e
                    INNER JOIN TIPO_EMPLEADO te ON e.tipo_empleado_id = te.tipo_id
                    WHERE e.empleado_id = %s
                """
                cursor.execute(sql_empleado, (empleado_id,))
                resultado_empleado = cursor.fetchone()
                
                if resultado_empleado:
                    perfil['tipo_perfil'] = 'empleado'
                    perfil['cod_empleado'] = resultado_empleado[0] or ''
                    perfil['num_documento'] = resultado_empleado[1] or ''
                    perfil['apellido_paterno'] = resultado_empleado[2] or ''
                    perfil['apellido_materno'] = resultado_empleado[3] or ''
                    perfil['nombres'] = resultado_empleado[4] or ''
                    perfil['sexo'] = resultado_empleado[5] or ''
                    perfil['telefono'] = resultado_empleado[6] or ''
                    perfil['tipo_empleado_id'] = resultado_empleado[7]
                    perfil['estado_empleado'] = resultado_empleado[8] or ''
                    perfil['tipo_empleado'] = resultado_empleado[9] or ''
                    
                    print(f"✓ Empleado encontrado en EMPLEADO")
                    print(f"  - Nombres: {perfil['nombres']} {perfil['apellido_paterno']}")
                    print(f"  - Código: {perfil['cod_empleado']}")
                    print(f"  - Tipo: {perfil['tipo_empleado']}")
                else:
                    print(f"⚠ No se encontraron datos del empleado para empleado_id: {empleado_id}")
                    
            elif cliente_id:
                # Es un cliente
                sql_cliente = """
                    SELECT c.nombres, c.ape_paterno, c.ape_materno, c.tipo_doc_id, 
                           c.num_doc, c.telefono, c.direccion, c.id_pais
                    FROM CLIENTE c
                    WHERE c.cliente_id = %s
                """
                cursor.execute(sql_cliente, (cliente_id,))
                resultado_cliente = cursor.fetchone()
                
                if resultado_cliente:
                    perfil['tipo_perfil'] = 'cliente'
                    perfil['nombres'] = resultado_cliente[0] or ''
                    perfil['apellido_paterno'] = resultado_cliente[1] or ''
                    perfil['apellido_materno'] = resultado_cliente[2] or ''
                    perfil['tipo_documento_id'] = resultado_cliente[3] or 1
                    perfil['num_documento'] = resultado_cliente[4] or ''
                    perfil['telefono'] = resultado_cliente[5] or ''
                    perfil['direccion'] = resultado_cliente[6] or ''
                    perfil['id_pais'] = resultado_cliente[7] or 1
                    
                    print(f"✓ Cliente encontrado en CLIENTE")
                    print(f"  - Nombres: {perfil['nombres']} {perfil['apellido_paterno']}")
                    print(f"  - Documento: {perfil['num_documento']}")
                else:
                    print(f"⚠ No se encontraron datos del cliente para cliente_id: {cliente_id}")
            else:
                print(f"⚠ Usuario sin cliente_id ni empleado_id asociado")
            
            return perfil
    except Exception as ex:
        print(f"❌ Error al obtener perfil completo: {ex}")
        return None
    finally:
        if conexion:
            conexion.close()

def update_perfil_usuario(usuario_id, email, nombres, apellido_paterno, apellido_materno, 
                          tipo_documento_id, num_documento, telefono, direccion=''):
    """
    Actualiza los datos del perfil del usuario y su cliente asociado
    """
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Actualizar email en USUARIO
            sql_usuario = "UPDATE USUARIO SET email = %s WHERE usuario_id = %s"
            cursor.execute(sql_usuario, (email, usuario_id))
            
            # Obtener el cliente_id asociado al usuario
            sql_get_cliente = "SELECT cliente_id FROM USUARIO WHERE usuario_id = %s"
            cursor.execute(sql_get_cliente, (usuario_id,))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0]:
                # El usuario ya tiene un cliente asociado, actualizarlo
                cliente_id = resultado[0]
                sql_update_cliente = """
                    UPDATE CLIENTE 
                    SET nombres = %s, ape_paterno = %s, ape_materno = %s,
                        tipo_doc_id = %s, num_doc = %s, telefono = %s, direccion = %s
                    WHERE cliente_id = %s
                """
                cursor.execute(sql_update_cliente, (nombres, apellido_paterno, apellido_materno,
                                                   tipo_documento_id, num_documento, telefono, 
                                                   direccion, cliente_id))
                print(f"✓ Cliente actualizado (ID: {cliente_id})")
            else:
                # El usuario no tiene cliente asociado, crear uno nuevo
                sql_insert_cliente = """
                    INSERT INTO CLIENTE 
                    (nombres, ape_paterno, ape_materno, num_doc, telefono, direccion,
                     f_registro, id_tipo_cliente, id_pais, tipo_doc_id)
                    VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), 'N', 1, %s)
                """
                cursor.execute(sql_insert_cliente, (nombres, apellido_paterno, apellido_materno,
                                                   num_documento, telefono, direccion, tipo_documento_id))
                nuevo_cliente_id = cursor.lastrowid
                
                # Asociar el cliente con el usuario
                sql_link = "UPDATE USUARIO SET cliente_id = %s WHERE usuario_id = %s"
                cursor.execute(sql_link, (nuevo_cliente_id, usuario_id))
                print(f"✓ Cliente creado y asociado (ID: {nuevo_cliente_id})")
            
            conexion.commit()
            return {'success': True, 'message': 'Perfil actualizado exitosamente'}
    except Exception as ex:
        print(f"❌ Error al actualizar perfil: {ex}")
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

def get_usuarios_admin(limit=100, offset=0, search_term='', rol_filter='', estado_filter=''):
    """
    Obtiene usuarios para la gestión administrativa con más detalles
    """
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            query = """
                SELECT 
                    u.usuario_id,
                    u.usuario,
                    u.email,
                    u.estado,
                    u.fecha_creacion,
                    r.rol_id,
                    r.nombre_rol,
                    CASE 
                        WHEN c.cliente_id IS NOT NULL THEN CONCAT(c.nombres, ' ', c.ape_paterno, ' ', c.ape_materno)
                        WHEN e.empleado_id IS NOT NULL THEN CONCAT(e.nombres, ' ', e.ape_paterno, ' ', e.ape_materno)
                        ELSE NULL
                    END as nombre_completo
                FROM USUARIO u
                INNER JOIN ROL r ON u.id_rol = r.rol_id
                LEFT JOIN CLIENTE c ON u.cliente_id = c.cliente_id
                LEFT JOIN EMPLEADO e ON u.empleado_id = e.empleado_id
                WHERE 1=1
            """
            params = []

            if search_term:
                query += " AND (u.usuario LIKE %s OR u.email LIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern])

            if rol_filter:
                query += " AND r.rol_id = %s"
                params.append(rol_filter)
            
            if estado_filter != '':
                query += " AND u.estado = %s"
                params.append(estado_filter)

            query += " ORDER BY u.usuario_id DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            usuarios = cursor.fetchall()
            
            usuarios_list = []
            for row in usuarios:
                usuarios_list.append({
                    'usuario_id': row[0],
                    'usuario': row[1],
                    'email': row[2],
                    'estado': row[3],
                    'fecha_creacion': str(row[4]) if row[4] else None,
                    'rol_id': row[5],
                    'rol_nombre': row[6],
                    'nombre_completo': row[7]
                })
            return usuarios_list
    except Exception as ex:
        print(f"Error al obtener usuarios: {ex}")
        return []
    finally:
        if conexion:
            conexion.close()

def insert_usuario_admin(usuario, contrasena, email, id_rol, estado=1):
    """
    Inserta un nuevo usuario desde el panel administrativo
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
            
            sql = """
                INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (usuario, contrasena_hash, email, estado, fecha_actual, id_rol))
            usuario_id = cursor.lastrowid
            
            conexion.commit()
            return {'success': True, 'message': 'Usuario creado exitosamente', 'usuario_id': usuario_id}
    except Exception as ex:
        print(f"Error al insertar usuario: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al crear usuario: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

def update_usuario_admin(usuario_id, usuario, email, id_rol, estado):
    """
    Actualiza un usuario desde el panel administrativo
    """
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Verificar que el usuario existe
            cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE usuario_id = %s", (usuario_id,))
            if cursor.fetchone()[0] == 0:
                return {'success': False, 'message': 'El usuario no existe'}
            
            # Verificar que el nombre de usuario no esté en uso por otro usuario
            cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE usuario = %s AND usuario_id != %s", (usuario, usuario_id))
            if cursor.fetchone()[0] > 0:
                return {'success': False, 'message': 'El nombre de usuario ya está en uso'}
            
            # Verificar que el email no esté en uso por otro usuario
            cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE email = %s AND usuario_id != %s", (email, usuario_id))
            if cursor.fetchone()[0] > 0:
                return {'success': False, 'message': 'El email ya está en uso'}
            
            # Actualizar usuario
            sql = """
                UPDATE USUARIO 
                SET usuario = %s, email = %s, id_rol = %s, estado = %s
                WHERE usuario_id = %s
            """
            cursor.execute(sql, (usuario, email, id_rol, estado, usuario_id))
            conexion.commit()
            return {'success': True, 'message': 'Usuario actualizado exitosamente'}
    except Exception as ex:
        print(f"Error al actualizar usuario: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al actualizar usuario: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

def resetear_contrasena_admin(usuario_id, nueva_contrasena):
    """
    Resetea la contraseña de un usuario (solo administrador)
    """
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Verificar que el usuario existe
            cursor.execute("SELECT COUNT(*) FROM USUARIO WHERE usuario_id = %s", (usuario_id,))
            if cursor.fetchone()[0] == 0:
                return {'success': False, 'message': 'El usuario no existe'}
            
            # Actualizar contraseña
            contrasena_hash = hash_password(nueva_contrasena)
            sql = "UPDATE USUARIO SET contrasena = %s WHERE usuario_id = %s"
            cursor.execute(sql, (contrasena_hash, usuario_id))
            conexion.commit()
            return {'success': True, 'message': 'Contraseña reseteada exitosamente'}
    except Exception as ex:
        print(f"Error al resetear contraseña: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al resetear contraseña: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

def eliminar_usuario_admin(usuario_id):
    """
    Elimina un usuario (versión administrativa)
    Elimina el usuario y todos sus datos asociados
    """
    return eliminar_usuario(usuario_id)

def eliminar_usuario(usuario_id):
    """
    Elimina un usuario y todos sus datos asociados (cliente o empleado)
    ADVERTENCIA: Esta acción es irreversible
    """
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            # Obtener el cliente_id y empleado_id asociados al usuario
            sql_get_usuario = "SELECT cliente_id, empleado_id FROM USUARIO WHERE usuario_id = %s"
            cursor.execute(sql_get_usuario, (usuario_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            cliente_id = resultado[0]
            empleado_id = resultado[1]
            
            # Si es un empleado
            if empleado_id:
                print(f"🗑️ Iniciando eliminación de usuario {usuario_id} (empleado {empleado_id})")
                
                # 1. Eliminar turnos del empleado
                try:
                    sql_delete_turnos = "DELETE FROM DETALLE_TURNO WHERE empleado_id = %s"
                    cursor.execute(sql_delete_turnos, (empleado_id,))
                    print(f"  ✓ Turnos eliminados")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar turnos: {e}")
                
                # 2. Eliminar incidencias del empleado
                try:
                    sql_delete_incidencias = "DELETE FROM INCIDENCIA WHERE empleado_id = %s"
                    cursor.execute(sql_delete_incidencias, (empleado_id,))
                    print(f"  ✓ Incidencias eliminadas")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar incidencias: {e}")
                
                # 3. Actualizar reservas para quitar referencia al empleado
                try:
                    sql_update_reservas = "UPDATE RESERVA SET empleado_id = NULL WHERE empleado_id = %s"
                    cursor.execute(sql_update_reservas, (empleado_id,))
                    print(f"  ✓ Referencias en reservas actualizadas")
                except Exception as e:
                    print(f"  ⚠ Error al actualizar reservas: {e}")
                
                # 4. Eliminar el empleado
                try:
                    sql_delete_empleado = "DELETE FROM EMPLEADO WHERE empleado_id = %s"
                    cursor.execute(sql_delete_empleado, (empleado_id,))
                    print(f"  ✓ Empleado eliminado")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar empleado: {e}")
            
            # Si es un cliente
            elif cliente_id:
                print(f"🗑️ Iniciando eliminación de usuario {usuario_id} y cliente {cliente_id}")
                
                # 1. Eliminar incidencias del cliente
                try:
                    sql_delete_incidencias = "DELETE FROM INCIDENCIA WHERE cliente_id = %s"
                    cursor.execute(sql_delete_incidencias, (cliente_id,))
                    print(f"  ✓ Incidencias eliminadas")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar incidencias: {e}")
                
                # 2. Eliminar huéspedes asociados al cliente
                try:
                    sql_delete_huespedes = "DELETE FROM HUESPED WHERE id_cliente = %s"
                    cursor.execute(sql_delete_huespedes, (cliente_id,))
                    print(f"  ✓ Huéspedes eliminados")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar huéspedes: {e}")
                
                # 3. Obtener reservas del cliente para eliminar datos relacionados
                try:
                    sql_get_reservas = "SELECT reserva_id FROM RESERVA WHERE cliente_id = %s"
                    cursor.execute(sql_get_reservas, (cliente_id,))
                    reservas = cursor.fetchall()
                    
                    for reserva in reservas:
                        reserva_id = reserva[0]
                        
                        # Eliminar eventos de la reserva
                        sql_delete_eventos = "DELETE FROM EVENTO WHERE reserva_id = %s"
                        cursor.execute(sql_delete_eventos, (reserva_id,))
                        
                        # Eliminar servicios de la reserva
                        sql_delete_servicios = "DELETE FROM RESERVA_SERVICIO WHERE reserva_id = %s"
                        cursor.execute(sql_delete_servicios, (reserva_id,))
                        
                        # Obtener transacciones de la reserva para eliminar comprobantes
                        sql_get_transaccion = "SELECT transaccion_id FROM TRANSACCION WHERE reserva_id = %s"
                        cursor.execute(sql_get_transaccion, (reserva_id,))
                        transaccion = cursor.fetchone()
                        
                        if transaccion:
                            transaccion_id = transaccion[0]
                            
                            # Obtener comprobante para eliminar detalles
                            sql_get_comprobante = "SELECT comprobante_id FROM COMPROBANTE WHERE transaccion_id = %s"
                            cursor.execute(sql_get_comprobante, (transaccion_id,))
                            comprobante = cursor.fetchone()
                            
                            if comprobante:
                                comprobante_id = comprobante[0]
                                
                                # Eliminar detalles del comprobante
                                sql_delete_detalles = "DELETE FROM DETALLE_COMPROBANTE WHERE comprobante_id = %s"
                                cursor.execute(sql_delete_detalles, (comprobante_id,))
                                
                                # Eliminar notas de crédito
                                sql_delete_notas = "DELETE FROM NOTA_CREDITO WHERE comprobante_id = %s"
                                cursor.execute(sql_delete_notas, (comprobante_id,))
                                
                                # Eliminar comprobante
                                sql_delete_comprobante = "DELETE FROM COMPROBANTE WHERE comprobante_id = %s"
                                cursor.execute(sql_delete_comprobante, (comprobante_id,))
                            
                            # Eliminar transacción
                            sql_delete_transaccion = "DELETE FROM TRANSACCION WHERE transaccion_id = %s"
                            cursor.execute(sql_delete_transaccion, (transaccion_id,))
                        
                        # Obtener reservas de habitación para eliminar room service
                        sql_get_reservas_hab = "SELECT reserva_habitacion_id FROM RESERVA_HABITACION WHERE reserva_id = %s"
                        cursor.execute(sql_get_reservas_hab, (reserva_id,))
                        reservas_hab = cursor.fetchall()
                        
                        for reserva_hab in reservas_hab:
                            reserva_habitacion_id = reserva_hab[0]
                            
                            # Obtener room services
                            sql_get_room_services = "SELECT room_service_id FROM ROOM_SERVICE WHERE reserva_habitacion_id = %s"
                            cursor.execute(sql_get_room_services, (reserva_habitacion_id,))
                            room_services = cursor.fetchall()
                            
                            for room_service in room_services:
                                room_service_id = room_service[0]
                                
                                # Eliminar amenidades del room service
                                sql_delete_amenidades = "DELETE FROM ROOM_SERVICE_AMENIDAD WHERE room_service_id = %s"
                                cursor.execute(sql_delete_amenidades, (room_service_id,))
                                
                                # Eliminar room service
                                sql_delete_room_service = "DELETE FROM ROOM_SERVICE WHERE room_service_id = %s"
                                cursor.execute(sql_delete_room_service, (room_service_id,))
                        
                        # Eliminar reservas de habitación
                        sql_delete_reservas_hab = "DELETE FROM RESERVA_HABITACION WHERE reserva_id = %s"
                        cursor.execute(sql_delete_reservas_hab, (reserva_id,))
                    
                    # Eliminar todas las reservas del cliente
                    sql_delete_reservas = "DELETE FROM RESERVA WHERE cliente_id = %s"
                    cursor.execute(sql_delete_reservas, (cliente_id,))
                    print(f"  ✓ Reservas y datos relacionados eliminados")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar reservas: {e}")
                
                # 4. Eliminar el cliente
                try:
                    sql_delete_cliente = "DELETE FROM CLIENTE WHERE cliente_id = %s"
                    cursor.execute(sql_delete_cliente, (cliente_id,))
                    print(f"  ✓ Cliente eliminado")
                except Exception as e:
                    print(f"  ⚠ Error al eliminar cliente: {e}")
            
            # 5. Finalmente, eliminar el usuario
            sql_delete_usuario = "DELETE FROM USUARIO WHERE usuario_id = %s"
            cursor.execute(sql_delete_usuario, (usuario_id,))
            print(f"  ✓ Usuario eliminado")
            
            conexion.commit()
            print(f"✅ Cuenta eliminada exitosamente")
            return {'success': True, 'message': 'Cuenta eliminada exitosamente'}
            
    except Exception as ex:
        print(f"❌ Error al eliminar usuario: {ex}")
        if conexion:
            conexion.rollback()
        return {'success': False, 'message': f'Error al eliminar la cuenta: {str(ex)}'}
    finally:
        if conexion:
            conexion.close()

