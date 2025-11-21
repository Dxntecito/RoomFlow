from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_Usuarios.controlador_usuario as controller_usuario
from functools import wraps
import re

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

def _get_safe_return_url(value):
    if not value:
        return None
    if value.startswith('/'):
        return value
    return None

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def Login():
    """
    Página de inicio de sesión
    """
    return_url = _get_safe_return_url(request.args.get('return_url'))
    # Si ya hay sesión activa, redirigir al inicio
    if 'usuario_id' in session:
        if return_url:
            return redirect(return_url)
        return redirect(url_for('Index'))
    
    if request.method == 'POST':
        try:
            usuario = request.form.get('usuario')
            contrasena = request.form.get('contrasena')
            return_url = _get_safe_return_url(request.form.get('return_url')) or return_url
            
            # Validar campos requeridos
            if not usuario or not contrasena:
                flash('Usuario y contraseña son obligatorios', 'error')
                return render_template('Login.html', return_url=return_url)
            
            # Verificar credenciales
            usuario_data = controller_usuario.verificar_usuario(usuario, contrasena)
            
            if usuario_data:
                # Crear sesión
                session['usuario_id'] = usuario_data['usuario_id']
                session['usuario'] = usuario_data['usuario']
                session['email'] = usuario_data['email']
                session['rol_id'] = usuario_data['rol_id']
                session['rol_nombre'] = usuario_data['rol_nombre']
                session['rol_modulos'] = usuario_data.get('rol_modulos', 'SSSSSS')
                session['rol_editar'] = usuario_data.get('rol_editar', 1)
                session['rol_eliminar'] = usuario_data.get('rol_eliminar', 1)
                
                # Debug: mostrar información del login
                print(f"[LOGIN] Usuario: {usuario_data['usuario']}, Rol ID: {usuario_data['rol_id']}, Permisos: {session['rol_modulos']}, Editar: {session['rol_editar']}, Eliminar: {session['rol_eliminar']}")
                
                flash(f'Bienvenido {usuario_data["usuario"]}!', 'success')
                if return_url:
                    return redirect(return_url)
                return redirect(url_for('Index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        except Exception as ex:
            flash(f'Error al iniciar sesión: {str(ex)}', 'error')
    
    return render_template('Login.html', return_url=return_url)

def validar_usuario_registro(usuario):
    """Valida el nombre de usuario"""
    if not usuario or len(usuario) < 3:
        return False, 'El usuario debe tener al menos 3 caracteres'
    if len(usuario) > 50:
        return False, 'El usuario no debe exceder 50 caracteres'
    if not re.match(r'^[a-zA-Z0-9_]{3,50}$', usuario):
        return False, 'El usuario solo puede contener letras, números y guiones bajos'
    return True, ''

def validar_email_formato(email):
    """Valida el formato del email"""
    if not email:
        return False, 'El email es obligatorio'
    patron = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, email):
        return False, 'Formato de email inválido'
    return True, ''

def validar_nombres_apellidos(texto, campo):
    """Valida que nombres y apellidos solo contengan letras"""
    if not texto or len(texto) < 2:
        return False, f'{campo} debe tener al menos 2 caracteres'
    if len(texto) > 50:
        return False, f'{campo} no debe exceder 50 caracteres'
    # Permitir letras con tildes, espacios y ñ
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', texto):
        return False, f'{campo} solo debe contener letras y espacios'
    if re.search(r'\d', texto):
        return False, f'{campo} no debe contener números'
    return True, ''

def validar_numero_documento(num_doc, tipo_doc_id):
    """Valida el número de documento según el tipo"""
    if not num_doc:
        return False, 'El número de documento es obligatorio'
    
    tipo_doc_id = str(tipo_doc_id)
    
    if tipo_doc_id == '1':  # DNI
        if not re.match(r'^\d{8}$', num_doc):
            return False, 'El DNI debe tener exactamente 8 dígitos'
    elif tipo_doc_id == '2':  # Pasaporte
        if not re.match(r'^[A-Z0-9]{6,20}$', num_doc.upper()):
            return False, 'El Pasaporte debe tener entre 6 y 20 caracteres alfanuméricos'
    elif tipo_doc_id == '3':  # Carnet de Extranjería
        if not re.match(r'^[A-Z0-9]{9,12}$', num_doc.upper()):
            return False, 'El Carnet de Extranjería debe tener entre 9 y 12 caracteres alfanuméricos'
    elif tipo_doc_id == '4':  # RUC
        if not re.match(r'^\d{11}$', num_doc):
            return False, 'El RUC debe tener exactamente 11 dígitos'
    
    return True, ''

def validar_telefono(telefono):
    """Valida el formato del teléfono (opcional)"""
    if not telefono:  # El teléfono es opcional
        return True, ''
    if not re.match(r'^9\d{8}$', telefono):
        return False, 'El teléfono debe comenzar con 9 y tener exactamente 9 dígitos'
    return True, ''

@usuarios_bp.route('/registro', methods=['GET', 'POST'])
def Registro():
    """
    Página de registro de nuevos usuarios con validaciones completas
    """
    return_url = _get_safe_return_url(request.args.get('return_url'))
    # Si ya hay sesión activa, redirigir al inicio
    if 'usuario_id' in session:
        if return_url:
            return redirect(return_url)
        return redirect(url_for('Index'))

    form_data = {
        'usuario': '',
        'email': '',
        'nombres': '',
        'apellido_paterno': '',
        'apellido_materno': '',
        'tipo_documento_id': '1',
        'num_documento': '',
        'telefono': '',
        'sexo': 'M',
        'direccion': ''
    }
    errors = {}

    def render_registro_template():
        return render_template('Registro.html', form_data=form_data, errors=errors, return_url=return_url)

    if request.method == 'POST':
        try:
            return_url = _get_safe_return_url(request.form.get('return_url')) or return_url
            # Datos de cuenta
            form_data['usuario'] = request.form.get('usuario', '').strip()
            form_data['email'] = request.form.get('email', '').strip()
            contrasena = request.form.get('contrasena', '')
            confirmar_contrasena = request.form.get('confirmar_contrasena', '')

            # Datos personales
            form_data['nombres'] = request.form.get('nombres', '').strip()
            form_data['apellido_paterno'] = request.form.get('apellido_paterno', '').strip()
            form_data['apellido_materno'] = request.form.get('apellido_materno', '').strip()
            form_data['tipo_documento_id'] = request.form.get('tipo_documento_id', '1')
            form_data['num_documento'] = request.form.get('num_documento', '').strip().upper()
            form_data['telefono'] = request.form.get('telefono', '').strip()
            form_data['sexo'] = request.form.get('sexo', 'M')
            form_data['direccion'] = request.form.get('direccion', '').strip()
            
            # Validar aceptación de términos y condiciones
            aceptar_terminos = request.form.get('aceptar_terminos')
            if not aceptar_terminos or aceptar_terminos != '1':
                errors['aceptar_terminos'] = 'Debes aceptar los términos y condiciones para continuar'
                flash('Debes aceptar los términos y condiciones para continuar', 'error')
                return render_registro_template()

            # Validar campos requeridos básicos
            if not form_data['usuario']:
                errors['usuario'] = 'El usuario es obligatorio'
            if not form_data['email']:
                errors['email'] = 'El correo electrónico es obligatorio'
            if not contrasena:
                errors['contrasena'] = 'La contraseña es obligatoria'
            if not confirmar_contrasena:
                errors['confirmar_contrasena'] = 'Debes confirmar la contraseña'
            if not form_data['nombres']:
                errors['nombres'] = 'Los nombres son obligatorios'
            if not form_data['apellido_paterno']:
                errors['apellido_paterno'] = 'El apellido paterno es obligatorio'
            if not form_data['apellido_materno']:
                errors['apellido_materno'] = 'El apellido materno es obligatorio'
            if not form_data['num_documento']:
                errors['num_documento'] = 'El número de documento es obligatorio'

            if errors:
                flash('Por favor, corrija los campos marcados en rojo.', 'error')
                return render_registro_template()

            # Validar usuario
            valido, mensaje = validar_usuario_registro(form_data['usuario'])
            if not valido:
                errors['usuario'] = mensaje
                flash(mensaje, 'error')
                return render_registro_template()

            # Validar email
            valido, mensaje = validar_email_formato(form_data['email'])
            if not valido:
                errors['email'] = mensaje
                flash(mensaje, 'error')
                return render_registro_template()

            # Validar contraseñas
            if contrasena != confirmar_contrasena:
                errors['confirmar_contrasena'] = 'Las contraseñas no coinciden'
                flash('Las contraseñas no coinciden', 'error')
                return render_registro_template()

            if len(contrasena) < 6:
                errors['contrasena'] = 'La contraseña debe tener al menos 6 caracteres'
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_registro_template()

            # Validar nombres
            valido, mensaje = validar_nombres_apellidos(form_data['nombres'], 'Nombres')
            if not valido:
                errors['nombres'] = mensaje
                flash(mensaje, 'error')
                return render_registro_template()

            # Validar apellidos
            valido, mensaje = validar_nombres_apellidos(form_data['apellido_paterno'], 'Apellido paterno')
            if not valido:
                errors['apellido_paterno'] = mensaje
                flash(mensaje, 'error')
                return render_registro_template()

            valido, mensaje = validar_nombres_apellidos(form_data['apellido_materno'], 'Apellido materno')
            if not valido:
                errors['apellido_materno'] = mensaje
                flash(mensaje, 'error')
                return render_registro_template()

            # Validar número de documento
            valido, mensaje = validar_numero_documento(form_data['num_documento'], form_data['tipo_documento_id'])
            if not valido:
                errors['num_documento'] = mensaje
                flash(mensaje, 'error')
                return render_registro_template()

            # Validar teléfono (si se proporciona)
                if form_data['telefono']:
                    valido, mensaje = validar_telefono(form_data['telefono'])
                    if not valido:
                        errors['telefono'] = mensaje
                        flash(mensaje, 'error')
                        return render_registro_template()

            # Registrar usuario con datos personales
            resultado = controller_usuario.insert_usuario(
                usuario=form_data['usuario'],
                contrasena=contrasena,
                email=form_data['email'],
                id_rol=3,  # Rol Cliente
                nombres=form_data['nombres'],
                apellido_paterno=form_data['apellido_paterno'],
                apellido_materno=form_data['apellido_materno'],
                tipo_documento_id=form_data['tipo_documento_id'],
                num_documento=form_data['num_documento'],
                telefono=form_data['telefono'] if form_data['telefono'] else None,
                direccion=form_data['direccion'] if form_data['direccion'] else None
            )

            if resultado['success']:
                if return_url:
                    nuevo_usuario = controller_usuario.verificar_usuario(form_data['usuario'], contrasena)
                    if nuevo_usuario:
                        session['usuario_id'] = nuevo_usuario['usuario_id']
                        session['usuario'] = nuevo_usuario['usuario']
                        session['email'] = nuevo_usuario['email']
                        session['rol_id'] = nuevo_usuario['rol_id']
                        session['rol_nombre'] = nuevo_usuario['rol_nombre']
                        session['rol_modulos'] = nuevo_usuario.get('rol_modulos', 'SSSSSS')
                        session['rol_editar'] = nuevo_usuario.get('rol_editar', 1)
                        session['rol_eliminar'] = nuevo_usuario.get('rol_eliminar', 1)
                        flash('¡Registro exitoso! Bienvenido a Hostal Bolívar.', 'success')
                        return redirect(return_url)
                flash('¡Registro exitoso! Ya puedes iniciar sesión con tus credenciales.', 'success')
                return redirect(url_for('usuarios.Login'))
            else:
                errors[resultado.get('field', 'general')] = resultado['message']
                flash(resultado['message'], 'error')
                return render_registro_template()
        except Exception as ex:
            flash(f'Error al registrar usuario: {str(ex)}', 'error')
            errors['general'] = f'Error al registrar usuario: {str(ex)}'
            return render_registro_template()

    return render_registro_template()


@usuarios_bp.route('/registro/verificar-usuario')
def verificar_usuario_disponible():
    """Endpoint para validar disponibilidad de nombre de usuario."""
    usuario = request.args.get('usuario', '').strip()

    if not usuario:
        return jsonify({'available': False, 'message': 'El usuario es obligatorio.'})

    valido, mensaje = validar_usuario_registro(usuario)
    if not valido:
        return jsonify({'available': False, 'message': mensaje})

    existente = controller_usuario.get_usuario_by_username(usuario)
    if existente:
        return jsonify({'available': False, 'message': 'El nombre de usuario ya existe'})

    return jsonify({'available': True, 'message': 'Usuario disponible'})

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
    
    # Verificar si el usuario cliente no tiene datos de perfil
    if perfil['rol_nombre'] == 'Cliente' and not perfil['nombres']:
        flash('Por favor, completa tu información de perfil para poder usar todas las funcionalidades del sistema.', 'warning')
    
    return render_template('Perfil.html', perfil=perfil, tipos_documento=tipos_documento)

@usuarios_bp.route('/mis-reservas', methods=['GET'])
@login_required
def MisReservas():
    """
    Endpoint para obtener las reservas del usuario actual usando su usuario_id de la sesión
    """
    try:
        import App.Controladores.C_Reserva.controlador_reserva as controller_reserva
        
        usuario_id = session.get('usuario_id')
        
        if not usuario_id:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado'
            }), 401
        
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        
        # Filtros de fecha
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        resultado = controller_reserva.get_reservas_por_usuario(
            usuario_id=usuario_id,
            limit=limit,
            offset=offset,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
        
        return jsonify({
            'success': True,
            'reservas': resultado['reservas'],
            'total': resultado['total'],
            'page': page,
            'limit': limit,
            'total_pages': (resultado['total'] + limit - 1) // limit if resultado['total'] > 0 else 0
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al obtener reservas: {str(e)}'
        }), 500

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

# ============================================
# RUTAS PARA RECUPERACIÓN DE CONTRASEÑA
# ============================================

# Variable global para el objeto mail (se asigna desde main.py)
mail = None

@usuarios_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def RecuperarContrasena():
    """
    Paso 1: Solicitar recuperación de contraseña (ingresa email)
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            
            if not email:
                flash('El email es obligatorio', 'error')
                return render_template('RecuperarContrasena.html')
            
            # Verificar que el email existe
            usuario_data = controller_usuario.get_usuario_by_email(email)
            if not usuario_data:
                # Por seguridad, no revelamos si el email existe o no
                flash('Si el email existe en nuestro sistema, recibirás un código de recuperación en unos momentos.', 'info')
                return render_template('RecuperarContrasena.html')
            
            usuario_id = usuario_data['usuario_id']
            nombre_usuario = usuario_data.get('usuario', 'Usuario')  # Obtener el nombre de usuario
            
            # Generar código de recuperación
            resultado = controller_usuario.crear_codigo_recuperacion(usuario_id)
            
            if not resultado['success']:
                flash('Error al generar código de recuperación', 'error')
                return render_template('RecuperarContrasena.html')
            
            codigo = resultado['codigo']
            
            # Enviar email con el código
            try:
                from flask_mail import Message
                
                msg = Message(
                    subject='Código de Recuperación de Contraseña - Hotel RoomFlow',
                    recipients=[email]
                )
                
                msg.html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                        .header {{ background: #328336; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                        .code {{ font-size: 32px; font-weight: bold; color: #328336; text-align: center; padding: 20px; background: #f0f8f0; border-radius: 10px; letter-spacing: 10px; margin: 20px 0; }}
                        .warning {{ color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
                        .username {{ font-weight: bold; color: #328336; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🏨 Hotel RoomFlow</h1>
                            <p>Recuperación de Contraseña</p>
                        </div>
                        
                        <p>Hola <span class="username">{nombre_usuario}</span>,</p>
                        <p>Has solicitado recuperar tu contraseña. Tu código de recuperación es:</p>
                        
                        <div class="code">{codigo}</div>
                        
                        <p>Este código es válido por <strong>10 minutos</strong>.</p>
                        
                        <div class="warning">
                            <strong>⚠️ Importante:</strong> Si no solicitaste este código, ignora este mensaje. Tu cuenta permanece segura.
                        </div>
                        
                        <p>Para continuar, ingresa este código en la página de recuperación de contraseña.</p>
                        
                        <div class="footer">
                            <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
                            <p>&copy; 2025 Hotel RoomFlow - Sistema de Gestión Hotelera</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                mail.send(msg)
                
                flash('Se ha enviado un código de recuperación a tu email. Revisa tu bandeja de entrada.', 'success')
                # Guardar email en sesión para el siguiente paso
                session['email_recuperacion'] = email
                return redirect(url_for('usuarios.ValidarCodigo'))
                
            except Exception as e:
                print(f"Error al enviar email: {e}")
                flash('Error al enviar el email. Intenta nuevamente más tarde.', 'error')
                return render_template('RecuperarContrasena.html')
                
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
            return render_template('RecuperarContrasena.html')
    
    return render_template('RecuperarContrasena.html')

@usuarios_bp.route('/validar-codigo', methods=['GET', 'POST'])
def ValidarCodigo():
    """
    Paso 2: Validar el código recibido por email
    """
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo', '').strip()
            
            if not codigo:
                flash('Debes ingresar el código', 'error')
                return render_template('ValidarCodigo.html')
            
            # Validar el código
            resultado = controller_usuario.validar_codigo_recuperacion(codigo)
            
            if not resultado['success']:
                flash(resultado['message'], 'error')
                return render_template('ValidarCodigo.html')
            
            # Código válido, guardar en sesión y redirigir a cambio de contraseña
            session['codigo_recuperacion'] = codigo
            return redirect(url_for('usuarios.NuevaContrasena'))
            
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
            return render_template('ValidarCodigo.html')
    
    # Verificar que viene del paso anterior
    if 'email_recuperacion' not in session:
        flash('Sesión expirada. Solicita un nuevo código.', 'warning')
        return redirect(url_for('usuarios.RecuperarContrasena'))
    
    return render_template('ValidarCodigo.html')

@usuarios_bp.route('/nueva-contrasena', methods=['GET', 'POST'])
def NuevaContrasena():
    """
    Paso 3: Establecer nueva contraseña
    """
    # Verificar que viene del paso anterior
    if 'codigo_recuperacion' not in session:
        flash('Sesión inválida. Solicita un nuevo código.', 'warning')
        return redirect(url_for('usuarios.RecuperarContrasena'))
    
    if request.method == 'POST':
        try:
            nueva_contrasena = request.form.get('nueva_contrasena', '')
            confirmar_contrasena = request.form.get('confirmar_contrasena', '')
            
            if not nueva_contrasena or not confirmar_contrasena:
                flash('Ambos campos son obligatorios', 'error')
                return render_template('NuevaContrasena.html')
            
            if nueva_contrasena != confirmar_contrasena:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('NuevaContrasena.html')
            
            if len(nueva_contrasena) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('NuevaContrasena.html')
            
            # Cambiar contraseña
            codigo = session['codigo_recuperacion']
            resultado = controller_usuario.cambiar_contrasena_con_codigo(codigo, nueva_contrasena)
            
            if not resultado['success']:
                flash(resultado['message'], 'error')
                return render_template('NuevaContrasena.html')
            
            # Limpiar sesión
            session.pop('email_recuperacion', None)
            session.pop('codigo_recuperacion', None)
            
            flash('¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('usuarios.Login'))
            
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
            return render_template('NuevaContrasena.html')
    
    return render_template('NuevaContrasena.html')

@usuarios_bp.route('/reenviar-codigo', methods=['POST'])
def ReenviarCodigo():
    """
    Reenvía el código de recuperación
    """
    try:
        if 'email_recuperacion' not in session:
            return jsonify({'success': False, 'message': 'Sesión expirada'})
        
        email = session['email_recuperacion']
        usuario_data = controller_usuario.get_usuario_by_email(email)
        
        if not usuario_data:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
        
        # Generar nuevo código
        resultado = controller_usuario.crear_codigo_recuperacion(usuario_data['usuario_id'])
        
        if not resultado['success']:
            return jsonify({'success': False, 'message': 'Error al generar código'})
        
        codigo = resultado['codigo']
        
        # Enviar email
        from flask_mail import Message
        
        msg = Message(
            subject='Nuevo Código de Recuperación - Hotel RoomFlow',
            recipients=[email]
        )
        
        msg.html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: #328336; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; margin: -30px -30px 30px -30px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #328336; text-align: center; padding: 20px; background: #f0f8f0; border-radius: 10px; letter-spacing: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏨 Hotel RoomFlow</h1>
                    <p>Nuevo Código de Recuperación</p>
                </div>
                <p>Has solicitado un nuevo código de recuperación:</p>
                <div class="code">{codigo}</div>
                <p>Este código es válido por <strong>10 minutos</strong>.</p>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        
        return jsonify({'success': True, 'message': 'Código reenviado exitosamente'})
        
    except Exception as e:
        print(f"Error al reenviar código: {e}")
        return jsonify({'success': False, 'message': 'Error al enviar el código'})

