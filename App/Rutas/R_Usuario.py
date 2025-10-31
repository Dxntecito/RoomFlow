from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_Usuarios.controlador_usuario as controller_usuario
from functools import wraps

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/auth')

def login_required(f):
    """
    Decorador para proteger rutas que requieren autenticación
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.Login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorador para proteger rutas que requieren rol de administrador
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.Login'))
        if session.get('rol_id') != 1:  # Asumiendo que rol_id=1 es administrador
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('Index'))
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def Login():
    """
    Página de inicio de sesión
    """
    # Si ya hay sesión activa, redirigir al inicio
    if 'usuario_id' in session:
        return redirect(url_for('Index'))
    
    if request.method == 'POST':
        try:
            usuario = request.form.get('usuario')
            contrasena = request.form.get('contrasena')
            
            # Validar campos requeridos
            if not usuario or not contrasena:
                flash('Usuario y contraseña son obligatorios', 'error')
                return render_template('Login.html')
            
            # Verificar credenciales
            usuario_data = controller_usuario.verificar_usuario(usuario, contrasena)
            
            if usuario_data:
                # Crear sesión
                session['usuario_id'] = usuario_data['usuario_id']
                session['usuario'] = usuario_data['usuario']
                session['email'] = usuario_data['email']
                session['rol_id'] = usuario_data['rol_id']
                session['rol_nombre'] = usuario_data['rol_nombre']
                
                flash(f'Bienvenido {usuario_data["usuario"]}!', 'success')
                return redirect(url_for('Index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        except Exception as ex:
            flash(f'Error al iniciar sesión: {str(ex)}', 'error')
    
    return render_template('Login.html')

@usuarios_bp.route('/registro', methods=['GET', 'POST'])
def Registro():
    """
    Página de registro de nuevos usuarios
    """
    # Si ya hay sesión activa, redirigir al inicio
    if 'usuario_id' in session:
        return redirect(url_for('Index'))
    
    if request.method == 'POST':
        try:
            # Datos de cuenta
            usuario = request.form.get('usuario')
            email = request.form.get('email')
            contrasena = request.form.get('contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')
            
            # Datos personales
            nombres = request.form.get('nombres', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            tipo_documento_id = request.form.get('tipo_documento_id', 1)
            num_documento = request.form.get('num_documento', '').strip()
            telefono = request.form.get('telefono', '').strip()
            direccion = request.form.get('direccion', '').strip()
            
            # Validar campos requeridos de cuenta
            if not all([usuario, email, contrasena, confirmar_contrasena]):
                flash('Usuario, email y contraseña son obligatorios', 'error')
                return render_template('Registro.html')
            
            # Validar campos requeridos de datos personales
            if not all([nombres, apellido_paterno, apellido_materno, num_documento]):
                flash('Todos los datos personales marcados con * son obligatorios', 'error')
                return render_template('Registro.html')
            
            # Validar que las contraseñas coincidan
            if contrasena != confirmar_contrasena:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('Registro.html')
            
            # Validar longitud de contraseña
            if len(contrasena) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('Registro.html')
            
            # Validar formato de email (básico)
            if '@' not in email or '.' not in email:
                flash('Email inválido', 'error')
                return render_template('Registro.html')
            
            # Registrar usuario con datos personales
            resultado = controller_usuario.insert_usuario(
                usuario=usuario,
                contrasena=contrasena,
                email=email,
                id_rol=3,  # Rol Cliente
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                tipo_documento_id=tipo_documento_id,
                num_documento=num_documento,
                telefono=telefono,
                direccion=direccion
            )
            
            if resultado['success']:
                flash('¡Registro exitoso! Ya puedes iniciar sesión con tus credenciales.', 'success')
                return redirect(url_for('usuarios.Login'))
            else:
                flash(resultado['message'], 'error')
        except Exception as ex:
            flash(f'Error al registrar usuario: {str(ex)}', 'error')
    
    return render_template('Registro.html')

@usuarios_bp.route('/logout')
def Logout():
    """
    Cerrar sesión
    """
    session.clear()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('usuarios.Login'))

@usuarios_bp.route('/perfil')
@login_required
def Perfil():
    """
    Página de perfil del usuario
    """
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    return render_template('Perfil.html', perfil=perfil, tipos_documento=tipos_documento)

@usuarios_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def ActualizarPerfil():
    """
    Actualiza los datos del perfil del usuario
    """
    try:
        usuario_id = session.get('usuario_id')
        email = request.form.get('email')
        nombres = request.form.get('nombres')
        apellido_paterno = request.form.get('apellido_paterno')
        apellido_materno = request.form.get('apellido_materno')
        tipo_documento_id = request.form.get('tipo_documento_id')
        num_documento = request.form.get('num_documento')
        telefono = request.form.get('telefono', '')
        direccion = request.form.get('direccion', '')
        
        # Validar campos requeridos
        if not all([email, nombres, apellido_paterno, apellido_materno, num_documento]):
            return jsonify({'success': False, 'message': 'Todos los campos obligatorios deben estar completos'})
        
        # Actualizar perfil
        resultado = controller_usuario.update_perfil_usuario(
            usuario_id, email, nombres, apellido_paterno, apellido_materno,
            tipo_documento_id, num_documento, telefono, direccion
        )
        
        if resultado['success']:
            # Actualizar email en sesión
            session['email'] = email
        
        return jsonify(resultado)
    except Exception as ex:
        return jsonify({'success': False, 'message': f'Error: {str(ex)}'})

@usuarios_bp.route('/eliminar-cuenta', methods=['POST'])
@login_required
def EliminarCuenta():
    """
    Elimina la cuenta del usuario actual y todos sus datos asociados
    """
    try:
        usuario_id = session.get('usuario_id')
        
        # Eliminar cuenta
        resultado = controller_usuario.eliminar_usuario(usuario_id)
        
        if resultado['success']:
            # Limpiar sesión
            session.clear()
            return jsonify(resultado)
        else:
            return jsonify(resultado)
    except Exception as ex:
        return jsonify({'success': False, 'message': f'Error al eliminar cuenta: {str(ex)}'})

@usuarios_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def CambiarContrasena():
    """
    Cambiar contraseña del usuario
    """
    if request.method == 'POST':
        try:
            contrasena_actual = request.form.get('contrasena_actual')
            contrasena_nueva = request.form.get('contrasena_nueva')
            confirmar_contrasena = request.form.get('confirmar_contrasena')
            
            # Validar campos requeridos
            if not all([contrasena_actual, contrasena_nueva, confirmar_contrasena]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('CambiarContrasena.html')
            
            # Validar que las contraseñas nuevas coincidan
            if contrasena_nueva != confirmar_contrasena:
                flash('Las contraseñas nuevas no coinciden', 'error')
                return render_template('CambiarContrasena.html')
            
            # Validar longitud de contraseña
            if len(contrasena_nueva) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('CambiarContrasena.html')
            
            # Cambiar contraseña
            usuario_id = session.get('usuario_id')
            resultado = controller_usuario.cambiar_contrasena(
                usuario_id, contrasena_actual, contrasena_nueva
            )
            
            if resultado['success']:
                flash('Contraseña actualizada exitosamente', 'success')
                return redirect(url_for('usuarios.Perfil'))
            else:
                flash(resultado['message'], 'error')
        except Exception as ex:
            flash(f'Error al cambiar contraseña: {str(ex)}', 'error')
    
    return render_template('CambiarContrasena.html')

@usuarios_bp.route('/usuarios')
@admin_required
def ListarUsuarios():
    """
    Listar todos los usuarios (solo administradores)
    """
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    
    limit = 10
    offset = (page - 1) * limit
    
    usuarios = controller_usuario.get_usuarios(limit, offset, search_term)
    total_usuarios = controller_usuario.count_usuarios(search_term)
    total_pages = (total_usuarios + limit - 1) // limit
    
    return render_template(
        'Usuarios.html',
        usuarios=usuarios,
        current_page=page,
        total_pages=total_pages,
        total_usuarios=total_usuarios,
        search_term=search_term
    )

# API endpoints para AJAX
@usuarios_bp.route('/api/verificar-usuario/<usuario>')
def verificar_disponibilidad_usuario(usuario):
    """
    Verifica si un nombre de usuario está disponible
    """
    usuario_existente = controller_usuario.get_usuario_by_username(usuario)
    return jsonify({
        'disponible': usuario_existente is None
    })

@usuarios_bp.route('/api/verificar-email/<email>')
def verificar_disponibilidad_email(email):
    """
    Verifica si un email está disponible
    """
    email_existente = controller_usuario.get_usuario_by_email(email)
    return jsonify({
        'disponible': email_existente is None
    })

