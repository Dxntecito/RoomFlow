# Sistema de Autenticación - RoomFlow

## 📋 Descripción

Se ha implementado un sistema completo de autenticación y gestión de usuarios para el proyecto RoomFlow. Este sistema incluye:

- ✅ Inicio de sesión
- ✅ Registro de usuarios
- ✅ Gestión de perfil
- ✅ Cambio de contraseña
- ✅ Control de sesiones
- ✅ Roles de usuario
- ✅ Protección de rutas

## 🚀 Instalación

### 1. Ejecutar el script SQL de roles y usuarios

Antes de usar el sistema, debes ejecutar el script SQL que crea los roles básicos y usuarios de prueba:

```bash
mysql -u root -p roomflow < EXTRAS/INSERTS_USUARIOS.sql
```

O desde MySQL Workbench/phpMyAdmin, ejecuta el contenido del archivo `EXTRAS/INSERTS_USUARIOS.sql`

### 2. Verificar la configuración

Asegúrate de que la base de datos esté correctamente configurada en `bd.py`:

```python
def get_connection():
    conexion = pymysql.connect(
        host='localhost',
        user='root',
        port=3306,
        password='',
        db='roomflow',
        charset='utf8mb4'
    )
    return conexion
```

## 🔐 Credenciales de Prueba

Después de ejecutar el script SQL, podrás iniciar sesión con estas credenciales:

### Usuario Administrador
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Rol:** Administrador (acceso completo)

### Usuario Cliente
- **Usuario:** `cliente`
- **Contraseña:** `cliente123`
- **Rol:** Cliente (usuario normal)

## 📖 Rutas Disponibles

### Rutas Públicas (sin autenticación)
- `/auth/login` - Página de inicio de sesión
- `/auth/registro` - Página de registro de nuevos usuarios
- `/` o `/RoomFlow` - Página principal

### Rutas Protegidas (requieren login)
- `/auth/perfil` - Perfil del usuario
- `/auth/cambiar-contrasena` - Cambiar contraseña
- `/auth/logout` - Cerrar sesión

### Rutas Administrativas (requieren rol Admin)
- `/auth/usuarios` - Listar todos los usuarios (solo administradores)

### API Endpoints
- `/auth/api/verificar-usuario/<usuario>` - Verificar disponibilidad de usuario
- `/auth/api/verificar-email/<email>` - Verificar disponibilidad de email

## 🛠️ Uso del Sistema

### Para Usuarios

1. **Registrarse:**
   - Ir a `/auth/registro`
   - Completar el formulario con usuario, email y contraseña
   - La contraseña debe tener al menos 6 caracteres
   - El sistema validará que el usuario y email no estén en uso

2. **Iniciar Sesión:**
   - Ir a `/auth/login`
   - Ingresar usuario y contraseña
   - Al iniciar sesión exitosamente, se redirige al inicio

3. **Ver Perfil:**
   - Clic en el menú de usuario (esquina superior derecha)
   - Seleccionar "Mi Perfil"
   - Ver información personal y de la cuenta

4. **Cambiar Contraseña:**
   - Desde el perfil o el menú de usuario
   - Seleccionar "Cambiar Contraseña"
   - Ingresar contraseña actual y la nueva contraseña

5. **Cerrar Sesión:**
   - Clic en el menú de usuario
   - Seleccionar "Cerrar Sesión"

### Para Desarrolladores

#### Proteger Rutas

Para proteger una ruta y requerir autenticación, usa el decorador `@login_required`:

```python
from App.Rutas.R_Usuario import login_required

@tu_blueprint.route('/ruta-protegida')
@login_required
def ruta_protegida():
    # Esta ruta solo es accesible para usuarios autenticados
    return render_template('protegida.html')
```

Para rutas que requieren rol de administrador:

```python
from App.Rutas.R_Usuario import admin_required

@tu_blueprint.route('/admin')
@admin_required
def ruta_admin():
    # Esta ruta solo es accesible para administradores
    return render_template('admin.html')
```

#### Acceder a Datos del Usuario en Sesión

En las vistas, puedes acceder a los datos del usuario desde la sesión:

```python
from flask import session

# En una ruta
@app.route('/mi-ruta')
def mi_ruta():
    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        usuario = session['usuario']
        rol_id = session['rol_id']
        rol_nombre = session['rol_nombre']
        email = session['email']
```

En templates HTML:

```html
{% if session.get('usuario_id') %}
    <p>Bienvenido, {{ session.get('usuario') }}!</p>
    <p>Tu rol es: {{ session.get('rol_nombre') }}</p>
{% else %}
    <p>Por favor, inicia sesión</p>
{% endif %}
```

## 🔒 Seguridad

### Características de Seguridad Implementadas:

1. **Hash de Contraseñas:** Las contraseñas se almacenan hasheadas con SHA256
2. **Validación de Formularios:** Validación tanto en cliente como en servidor
3. **Protección CSRF:** Flask maneja automáticamente con `app.secret_key`
4. **Control de Sesiones:** Sistema de sesiones seguro de Flask
5. **Validación de Email y Usuario:** No se permiten duplicados

### Recomendaciones:

- Cambiar `app.secret_key` en `main.py` por una clave más segura
- En producción, usar HTTPS
- Implementar límite de intentos de inicio de sesión
- Considerar agregar verificación de email
- Implementar recuperación de contraseña

## 📁 Estructura de Archivos

```
RoomFlow/
├── App/
│   ├── Controladores/
│   │   └── C_Usuarios/
│   │       └── controlador_usuario.py    # Lógica de negocio de usuarios
│   └── Rutas/
│       ├── R_Usuario.py                  # Rutas de autenticación
│       └── TEMPLATES/
│           ├── Login.html                # Página de inicio de sesión
│           ├── Registro.html             # Página de registro
│           ├── Perfil.html               # Página de perfil
│           ├── CambiarContrasena.html    # Cambiar contraseña
│           └── Master.html               # Template base (actualizado)
├── EXTRAS/
│   └── INSERTS_USUARIOS.sql              # Script de inserción de roles
└── main.py                               # Aplicación principal (actualizado)
```

## 🎨 Diseño

El sistema de autenticación mantiene el diseño consistente con el resto del proyecto:
- Formularios modernos con gradientes
- Animaciones suaves
- Diseño responsive
- Validación en tiempo real
- Mensajes flash informativos
- Iconos de Font Awesome

## ❓ Solución de Problemas

### Error: "No module named 'App.Controladores.C_Usuarios'"
- Verifica que todos los archivos se hayan creado correctamente
- Reinicia el servidor Flask

### Error al iniciar sesión: "Usuario o contraseña incorrectos"
- Verifica que hayas ejecutado el script SQL de inserción
- Verifica las credenciales de prueba
- Revisa la conexión a la base de datos

### El menú de usuario no aparece
- Verifica que estés usando el template `Master.html` actualizado
- Asegúrate de que el usuario haya iniciado sesión correctamente

### Contraseña hasheada incorrecta
- El sistema usa SHA256 para hashear contraseñas
- Las contraseñas del script SQL ya están hasheadas

## 🔄 Próximas Mejoras Sugeridas

1. Recuperación de contraseña por email
2. Verificación de email al registrarse
3. Autenticación de dos factores (2FA)
4. Gestión de permisos más granular
5. Historial de inicio de sesión
6. Bloqueo de cuenta por intentos fallidos
7. OAuth (Google, Facebook, etc.)
8. Remember me (mantener sesión)

## 📞 Soporte

Si tienes problemas o preguntas sobre el sistema de autenticación, contacta al equipo de desarrollo.

---

**Fecha de implementación:** Octubre 2025  
**Versión:** 1.0  
**Desarrollado para:** RoomFlow - Sistema de Gestión Hotelera

