"""
Script de configuración para el sistema de usuarios
RoomFlow - Sistema de Gestión Hotelera

Este script crea los roles básicos y usuarios de prueba en la base de datos.
"""

import pymysql
import hashlib
from datetime import date

def hash_password(password):
    """Hashea una contraseña usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    """Configura la base de datos con roles y usuarios de prueba"""
    try:
        # Conectar a la base de datos
        conexion = pymysql.connect(
            host='localhost',
            user='root',
            port=3306,
            password='',
            db='roomflow',
            charset='utf8mb4'
        )
        
        print("✓ Conexión a la base de datos exitosa")
        
        with conexion.cursor() as cursor:
            # Insertar roles básicos
            print("\n📋 Insertando roles básicos...")
            
            roles = [
                (1, 'Administrador', 'Acceso completo al sistema', 1),
                (2, 'Cliente', 'Usuario cliente del hostal', 1),
                (3, 'Empleado', 'Empleado del hostal', 1),
                (4, 'Recepcionista', 'Personal de recepción', 1)
            ]
            
            for rol_id, nombre, descripcion, estado in roles:
                try:
                    sql = """
                        INSERT INTO ROL (rol_id, nombre_rol, descripcion, estado) 
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            nombre_rol = VALUES(nombre_rol),
                            descripcion = VALUES(descripcion),
                            estado = VALUES(estado)
                    """
                    cursor.execute(sql, (rol_id, nombre, descripcion, estado))
                    print(f"  ✓ Rol '{nombre}' insertado/actualizado")
                except Exception as e:
                    print(f"  ✗ Error con rol '{nombre}': {e}")
            
            conexion.commit()
            
            # Insertar usuarios de prueba
            print("\n👤 Insertando usuarios de prueba...")
            
            # Usuario administrador
            admin_password = hash_password('admin123')
            try:
                sql = """
                    INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        contrasena = VALUES(contrasena),
                        email = VALUES(email),
                        estado = VALUES(estado)
                """
                cursor.execute(sql, ('admin', admin_password, 'admin@hostalbolivar.com', 1, date.today(), 1))
                print("  ✓ Usuario 'admin' insertado/actualizado")
                print("    - Usuario: admin")
                print("    - Contraseña: admin123")
            except Exception as e:
                print(f"  ✗ Error al crear usuario admin: {e}")
            
            # Usuario cliente
            cliente_password = hash_password('cliente123')
            try:
                sql = """
                    INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        contrasena = VALUES(contrasena),
                        email = VALUES(email),
                        estado = VALUES(estado)
                """
                cursor.execute(sql, ('cliente', cliente_password, 'cliente@example.com', 1, date.today(), 2))
                print("  ✓ Usuario 'cliente' insertado/actualizado")
                print("    - Usuario: cliente")
                print("    - Contraseña: cliente123")
            except Exception as e:
                print(f"  ✗ Error al crear usuario cliente: {e}")
            
            conexion.commit()
            
            # Crear tabla PERFIL_USUARIO
            print("\n📊 Creando tabla PERFIL_USUARIO...")
            try:
                sql_perfil = """
                    CREATE TABLE IF NOT EXISTS PERFIL_USUARIO (
                        perfil_id INT(10) NOT NULL AUTO_INCREMENT,
                        usuario_id INT(10) NOT NULL,
                        nombres VARCHAR(50),
                        apellido_paterno VARCHAR(50),
                        apellido_materno VARCHAR(50),
                        tipo_documento_id INT(10),
                        num_documento VARCHAR(20),
                        sexo CHAR(1),
                        telefono VARCHAR(9),
                        PRIMARY KEY (perfil_id),
                        UNIQUE KEY unique_usuario (usuario_id),
                        FOREIGN KEY (usuario_id) REFERENCES USUARIO(usuario_id) ON DELETE CASCADE,
                        FOREIGN KEY (tipo_documento_id) REFERENCES TIPO_DOCUMENTO(tipo_doc_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
                cursor.execute(sql_perfil)
                print("  ✓ Tabla PERFIL_USUARIO creada")
                
                # Insertar tipos de documento
                print("\n📄 Insertando tipos de documento...")
                tipos_doc = [
                    ('DNI', 1),
                    ('Pasaporte', 1),
                    ('Carnet de Extranjería', 1),
                    ('RUC', 1)
                ]
                for nombre, estado in tipos_doc:
                    try:
                        sql_tipo = """
                            INSERT INTO TIPO_DOCUMENTO (nombre_tipo_doc, estado) 
                            VALUES (%s, %s)
                            ON DUPLICATE KEY UPDATE nombre_tipo_doc = VALUES(nombre_tipo_doc)
                        """
                        cursor.execute(sql_tipo, (nombre, estado))
                        print(f"  ✓ Tipo documento '{nombre}' insertado/actualizado")
                    except Exception as e:
                        print(f"  ⚠ Tipo documento '{nombre}': {e}")
                
                conexion.commit()
            except Exception as e:
                print(f"  ⚠ Advertencia al crear PERFIL_USUARIO: {e}")
                print("  (Puede ser normal si ya existe)")
            
            print("\n" + "="*50)
            print("✅ Configuración completada exitosamente")
            print("="*50)
            print("\n🚀 Puedes iniciar el servidor con:")
            print("   python main.py")
            print("\n🔐 Credenciales de prueba:")
            print("   Admin: usuario='admin', contraseña='admin123'")
            print("   Cliente: usuario='cliente', contraseña='cliente123'")
            print("\n📍 Rutas disponibles:")
            print("   - http://localhost:8000/auth/login")
            print("   - http://localhost:8000/auth/registro")
            print("="*50)
            
    except pymysql.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
        print("\nAsegúrate de que:")
        print("  1. MySQL esté ejecutándose")
        print("  2. La base de datos 'roomflow' exista")
        print("  3. Las credenciales en bd.py sean correctas")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
    finally:
        if conexion:
            conexion.close()
            print("\n✓ Conexión cerrada")

if __name__ == "__main__":
    print("="*50)
    print("CONFIGURACIÓN DEL SISTEMA DE USUARIOS - ROOMFLOW")
    print("="*50)
    print("\nEste script configurará:")
    print("  - Roles básicos del sistema")
    print("  - Usuarios de prueba")
    print()
    
    respuesta = input("¿Deseas continuar? (s/n): ").lower()
    
    if respuesta == 's' or respuesta == 'si' or respuesta == 'sí':
        print("\n🔄 Iniciando configuración...\n")
        setup_database()
    else:
        print("\n❌ Configuración cancelada")

