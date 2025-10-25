"""
EJEMPLO: Cómo proteger rutas en RoomFlow
==========================================

Este archivo muestra ejemplos de cómo proteger rutas usando
los decoradores del sistema de autenticación.
"""

from flask import Blueprint, render_template, session
from App.Rutas.R_Usuario import login_required, admin_required

# Crear un blueprint de ejemplo
ejemplo_bp = Blueprint('ejemplo', __name__, url_prefix='/ejemplo')

# =============================================================================
# EJEMPLO 1: Ruta pública (sin protección)
# =============================================================================

@ejemplo_bp.route('/publica')
def ruta_publica():
    """
    Esta ruta es accesible para todos, con o sin sesión
    """
    return render_template('publica.html')


# =============================================================================
# EJEMPLO 2: Ruta protegida (requiere login)
# =============================================================================

@ejemplo_bp.route('/protegida')
@login_required  # <-- Decorador que requiere autenticación
def ruta_protegida():
    """
    Esta ruta solo es accesible para usuarios autenticados
    Si el usuario no ha iniciado sesión, será redirigido a /auth/login
    """
    usuario = session.get('usuario')
    return render_template('protegida.html', usuario=usuario)


# =============================================================================
# EJEMPLO 3: Ruta administrativa (requiere rol Admin)
# =============================================================================

@ejemplo_bp.route('/admin')
@admin_required  # <-- Decorador que requiere rol de administrador
def ruta_admin():
    """
    Esta ruta solo es accesible para usuarios con rol_id = 1 (Administrador)
    Si el usuario no es admin, será redirigido al inicio con un mensaje de error
    """
    return render_template('admin.html')


# =============================================================================
# EJEMPLO 4: Ruta con verificación manual de rol
# =============================================================================

@ejemplo_bp.route('/empleados')
@login_required
def ruta_empleados():
    """
    Esta ruta requiere login y verifica manualmente el rol
    """
    rol_id = session.get('rol_id')
    
    # Solo administradores y empleados (rol_id 1 o 3)
    if rol_id not in [1, 3]:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('Index'))
    
    return render_template('empleados.html')


# =============================================================================
# EJEMPLO 5: Ruta con acceso a datos del usuario en sesión
# =============================================================================

@ejemplo_bp.route('/mi-dashboard')
@login_required
def mi_dashboard():
    """
    Acceso a todos los datos del usuario en sesión
    """
    usuario_id = session.get('usuario_id')
    usuario = session.get('usuario')
    email = session.get('email')
    rol_id = session.get('rol_id')
    rol_nombre = session.get('rol_nombre')
    
    # Puedes usar estos datos para personalizar la vista
    return render_template('dashboard.html',
                         usuario=usuario,
                         email=email,
                         rol=rol_nombre)


# =============================================================================
# EJEMPLO 6: Ruta que verifica si el usuario está logueado
# =============================================================================

@ejemplo_bp.route('/mixta')
def ruta_mixta():
    """
    Esta ruta es accesible para todos, pero muestra contenido diferente
    según si el usuario está autenticado o no
    """
    if 'usuario_id' in session:
        # Usuario autenticado
        usuario = session.get('usuario')
        return render_template('mixta.html', autenticado=True, usuario=usuario)
    else:
        # Usuario no autenticado
        return render_template('mixta.html', autenticado=False)


# =============================================================================
# EJEMPLO 7: Proteger métodos específicos (POST)
# =============================================================================

@ejemplo_bp.route('/formulario', methods=['GET', 'POST'])
@login_required
def formulario_protegido():
    """
    Protege tanto GET como POST
    """
    if request.method == 'POST':
        # Procesar el formulario
        usuario_id = session.get('usuario_id')
        # ... tu lógica aquí
        pass
    
    return render_template('formulario.html')


# =============================================================================
# EJEMPLO 8: Decoradores múltiples
# =============================================================================

from functools import wraps

def verificar_propiedad(f):
    """
    Decorador personalizado que verifica si el usuario
    es dueño del recurso que intenta acceder
    """
    @wraps(f)
    def decorated_function(recurso_id, *args, **kwargs):
        usuario_id = session.get('usuario_id')
        
        # Verificar si el recurso pertenece al usuario
        # (esto es un ejemplo, adapta a tu lógica)
        if not es_dueno(usuario_id, recurso_id):
            flash('No tienes acceso a este recurso', 'danger')
            return redirect(url_for('Index'))
        
        return f(recurso_id, *args, **kwargs)
    return decorated_function

@ejemplo_bp.route('/recurso/<int:recurso_id>')
@login_required
@verificar_propiedad
def ver_recurso(recurso_id):
    """
    Esta ruta requiere login Y que el usuario sea dueño del recurso
    """
    return render_template('recurso.html', recurso_id=recurso_id)


# =============================================================================
# EJEMPLO DE TEMPLATE HTML
# =============================================================================

"""
Ejemplo de uso en templates HTML:

<!-- Mostrar nombre de usuario si está logueado -->
{% if session.get('usuario_id') %}
    <p>Bienvenido, {{ session.get('usuario') }}!</p>
{% else %}
    <p><a href="{{ url_for('usuarios.Login') }}">Inicia sesión</a></p>
{% endif %}

<!-- Mostrar contenido solo para administradores -->
{% if session.get('rol_id') == 1 %}
    <div class="admin-panel">
        <h3>Panel de Administración</h3>
        <!-- Contenido solo para admins -->
    </div>
{% endif %}

<!-- Mostrar diferentes opciones según el rol -->
{% if session.get('rol_nombre') == 'Administrador' %}
    <a href="{{ url_for('admin.panel') }}">Panel Admin</a>
{% elif session.get('rol_nombre') == 'Empleado' %}
    <a href="{{ url_for('empleados.panel') }}">Panel Empleado</a>
{% else %}
    <a href="{{ url_for('clientes.panel') }}">Mi Cuenta</a>
{% endif %}
"""

# =============================================================================
# CÓMO REGISTRAR ESTE BLUEPRINT EN main.py
# =============================================================================

"""
En tu archivo main.py, agrega:

from App.Rutas.ejemplo import ejemplo_bp

app.register_blueprint(ejemplo_bp)
"""

# =============================================================================
# NOTAS IMPORTANTES
# =============================================================================

"""
1. Los decoradores SIEMPRE van DESPUÉS de @route, pero ANTES de la función

   CORRECTO:
   @app.route('/ruta')
   @login_required
   def mi_ruta():
       pass
   
   INCORRECTO:
   @login_required
   @app.route('/ruta')
   def mi_ruta():
       pass

2. Puedes combinar múltiples decoradores

3. Los decoradores se ejecutan de abajo hacia arriba:
   @app.route('/ruta')
   @decorador1  # Se ejecuta primero
   @decorador2  # Se ejecuta segundo
   def mi_ruta():
       pass

4. Siempre importa flash y redirect si los usas:
   from flask import flash, redirect, url_for

5. Para verificar roles personalizados, accede a session.get('rol_id')
   - 1 = Administrador
   - 2 = Cliente
   - 3 = Empleado
   - 4 = Recepcionista
"""

