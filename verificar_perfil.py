"""
Script para verificar si los datos del perfil se guardaron en la BD
"""
import pymysql

def verificar_datos():
    try:
        conexion = pymysql.connect(
            host='localhost',
            user='root',
            port=3306,
            password='',
            db='roomflow',
            charset='utf8mb4'
        )
        
        print("=" * 60)
        print("VERIFICACIÓN DE DATOS EN LA BASE DE DATOS")
        print("=" * 60)
        
        with conexion.cursor() as cursor:
            # Verificar usuarios
            print("\n1. USUARIOS REGISTRADOS:")
            print("-" * 60)
            cursor.execute("SELECT usuario_id, usuario, email FROM USUARIO")
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                print(f"  ID: {usuario[0]} | Usuario: {usuario[1]} | Email: {usuario[2]}")
            
            # Verificar si existe la tabla PERFIL_USUARIO
            print("\n2. TABLA PERFIL_USUARIO:")
            print("-" * 60)
            try:
                cursor.execute("SHOW TABLES LIKE 'PERFIL_USUARIO'")
                tabla_existe = cursor.fetchone()
                if tabla_existe:
                    print("  ✓ La tabla PERFIL_USUARIO existe")
                    
                    cursor.execute("SELECT * FROM PERFIL_USUARIO")
                    perfiles = cursor.fetchall()
                    if perfiles:
                        print(f"\n  Perfiles guardados: {len(perfiles)}")
                        for perfil in perfiles:
                            print(f"\n  Perfil ID: {perfil[0]}")
                            print(f"    Usuario ID: {perfil[1]}")
                            print(f"    Nombres: {perfil[2]}")
                            print(f"    Ap. Paterno: {perfil[3]}")
                            print(f"    Ap. Materno: {perfil[4]}")
                            print(f"    Tipo Doc ID: {perfil[5]}")
                            print(f"    Núm. Doc: {perfil[6]}")
                            print(f"    Sexo: {perfil[7]}")
                            print(f"    Teléfono: {perfil[8]}")
                    else:
                        print("  ⚠ La tabla existe pero está VACÍA")
                else:
                    print("  ✗ La tabla PERFIL_USUARIO NO EXISTE")
                    print("  → Ejecuta: python setup_usuarios.py")
            except Exception as e:
                print(f"  ✗ Error al verificar tabla: {e}")
            
            # Verificar tipos de documento
            print("\n3. TIPOS DE DOCUMENTO:")
            print("-" * 60)
            try:
                cursor.execute("SELECT * FROM TIPO_DOCUMENTO")
                tipos = cursor.fetchall()
                if tipos:
                    for tipo in tipos:
                        print(f"  ID: {tipo[0]} | Nombre: {tipo[1]} | Estado: {tipo[2]}")
                else:
                    print("  ⚠ No hay tipos de documento")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        print("\n" + "=" * 60)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\nVerifica que:")
        print("  1. MySQL esté ejecutándose")
        print("  2. La base de datos 'roomflow' exista")
        print("  3. Las credenciales sean correctas")
    finally:
        if conexion:
            conexion.close()

if __name__ == "__main__":
    verificar_datos()

