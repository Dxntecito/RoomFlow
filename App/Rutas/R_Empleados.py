from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_Empleado.controlador_empleado as controller_empleado
from functools import wraps

empleados_bp = Blueprint('empleados', __name__, template_folder='CRUDS/Empleados', url_prefix='/Cruds/Empleados')

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
            flash('No tienes permisos para acceder a esta página. Solo administradores pueden gestionar empleados.', 'danger')
            return redirect(url_for('Index'))
        return f(*args, **kwargs)
    return decorated_function

@empleados_bp.route('/', methods=['GET'])
@empleados_bp.route('/Empleados', methods=['GET'])
@admin_required
def Empleados():
    """
    Página principal del módulo de empleados
    """
    # Obtener parámetros de filtrado y paginación
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    rol_filter = request.args.get('rol', '', type=str)
    
    # Configurar paginación
    limit = 10
    offset = (page - 1) * limit
    
    # Obtener empleados activos y total
    empleados = controller_empleado.get_empleados_activos(limit, offset, search_term, rol_filter)
    total_empleados = controller_empleado.count_empleados(search_term, rol_filter)
    tipos_empleado = controller_empleado.get_tipos_empleado()
    
    # Calcular información de paginación
    total_pages = (total_empleados + limit - 1) // limit
    
    return render_template(
        "Empleados.html",
        empleados=empleados,
        tipos_empleado=tipos_empleado,
        current_page=page,
        total_pages=total_pages,
        total_empleados=total_empleados,
        search_term=search_term,
        rol_filter=rol_filter
    )

@empleados_bp.route('/crear', methods=['GET', 'POST'])
@admin_required
def CrearEmpleado():
    """
    Crear nuevo empleado
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cod_empleado = request.form.get('cod_empleado')
            dni = request.form.get('dni')
            ape_paterno = request.form.get('ape_paterno')
            ape_materno = request.form.get('ape_materno')
            nombres = request.form.get('nombres')
            sexo = request.form.get('sexo')
            movil = request.form.get('movil')
            tipo_empleado_id = request.form.get('tipo_empleado_id')
            
            # Validar datos requeridos
            if not all([cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('empleados.CrearEmpleado'))
            
            # Insertar empleado
            success, message = controller_empleado.insert_empleado(
                cod_empleado, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id
            )
            if success:
                flash(message, 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash(message, 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener tipos de empleado para el formulario
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("CrearEmpleado.html", tipos_empleado=tipos_empleado)

@empleados_bp.route('/editar/<int:empleado_id>', methods=['GET', 'POST'])
@admin_required
def EditarEmpleado(empleado_id):
    """
    Editar empleado existente
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cod_empleado = request.form.get('cod_empleado')
            dni = request.form.get('dni')
            ape_paterno = request.form.get('ape_paterno')
            ape_materno = request.form.get('ape_materno')
            nombres = request.form.get('nombres')
            sexo = request.form.get('sexo')
            movil = request.form.get('movil')
            tipo_empleado_id = request.form.get('tipo_empleado_id')
            
            # Validar datos requeridos
            if not all([cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('empleados.EditarEmpleado', empleado_id=empleado_id))
            
            # Actualizar empleado
            success, message = controller_empleado.update_empleado(
                empleado_id, cod_empleado, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id
            )
            if success:
                flash(message, 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash(message, 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener datos del empleado
    empleado = controller_empleado.get_empleado_by_id(empleado_id)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados.Empleados'))
    
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("EditarEmpleado.html", empleado=empleado, tipos_empleado=tipos_empleado)

@empleados_bp.route('/eliminar/<int:empleado_id>', methods=['POST'])
@admin_required
def EliminarEmpleado(empleado_id):
    """
    Eliminar empleado
    """
    try:
        success, message = controller_empleado.delete_empleado(empleado_id)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    except Exception as ex:
        flash(f'Error: {str(ex)}', 'error')
    
    return redirect(url_for('empleados.Empleados'))

@empleados_bp.route('/actualizar/<int:empleado_id>', methods=['GET', 'POST'])
@admin_required
def ActualizarEmpleado(empleado_id):
    """
    Actualizar datos de empleado (versión simplificada)
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            ape_paterno = request.form.get('ape_paterno')
            ape_materno = request.form.get('ape_materno')
            nombres = request.form.get('nombres')
            dni = request.form.get('dni')
            movil = request.form.get('movil')
            sexo = request.form.get('sexo')
            tipo_empleado_id = request.form.get('tipo_empleado_id')
            
            # Validar datos requeridos
            if not all([ape_paterno, ape_materno, nombres, dni, movil, sexo, tipo_empleado_id]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('empleados.ActualizarEmpleado', empleado_id=empleado_id))
            
            # Actualizar empleado
            success, message = controller_empleado.update_empleado(
                empleado_id, empleado_id, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id
            )
            if success:
                flash(message, 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash(message, 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener datos del empleado
    empleado = controller_empleado.get_empleado_by_id(empleado_id)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados.Empleados'))
    
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("ActualizarEmpleado.html", empleado=empleado, tipos_empleado=tipos_empleado)

@empleados_bp.route('/registro', methods=['GET', 'POST'])
@admin_required
def RegistroEmpleado():
    """
    Registro de nuevo empleado (versión simplificada)
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            ape_paterno = request.form.get('ape_paterno')
            ape_materno = request.form.get('ape_materno')
            nombres = request.form.get('nombres')
            num_documento = request.form.get('num_documento')
            movil = request.form.get('movil')
            email = request.form.get('email')
            tipo_empleado_id = request.form.get('tipo_empleado_id')
            
            # Validar datos requeridos
            if not all([ape_paterno, ape_materno, nombres, num_documento, movil, email, tipo_empleado_id]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('empleados.RegistroEmpleado'))
            
            # Insertar empleado (usando DNI como código temporal)
            success, message = controller_empleado.insert_empleado(
                num_documento, num_documento, ape_paterno, ape_materno, 
                nombres, 'M', movil, tipo_empleado_id
            )
            if success:
                flash(message, 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash(message, 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("RegistroEmpleado.html", tipos_empleado=tipos_empleado)

@empleados_bp.route('/asignar-turno/<int:empleado_id>', methods=['GET', 'POST'])
@admin_required
def AsignarTurno(empleado_id):
    """
    Asignar turno a empleado
    """
    if request.method == 'POST':
        try:
            turno_id = request.form.get('turno_id')
            if not turno_id:
                flash('Debe seleccionar un turno', 'error')
                return redirect(url_for('empleados.AsignarTurno', empleado_id=empleado_id))
            
            # TODO: Implementar lógica de asignación de turnos en la BD
            flash('Turno asignado exitosamente', 'success')
            return redirect(url_for('empleados.Empleados'))
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener datos del empleado
    empleado = controller_empleado.get_empleado_by_id(empleado_id)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados.Empleados'))
    
    # Obtener turnos disponibles (simulado)
    turnos = [
        (1, 'Mañana'),
        (2, 'Tarde'),
        (3, 'Noche')
    ]
    
    return render_template("AsignarTurno.html", empleado=empleado, turnos=turnos)

@empleados_bp.route('/api/empleados', methods=['GET'])
@admin_required
def api_empleados():
    """
    API endpoint para obtener empleados en formato JSON
    """
    try:
        # Obtener todos los empleados activos
        empleados = controller_empleado.get_empleados_activos(limit=100, offset=0, search_term='', rol_filter='')
        tipos_empleado = controller_empleado.get_tipos_empleado()
        
        # Crear diccionario de tipos para mapear IDs a nombres
        tipos_dict = {tipo[0]: tipo[1] for tipo in tipos_empleado}
        
        # Formatear datos para el frontend
        empleados_formateados = []
        for empleado in empleados:
            empleados_formateados.append({
                'id': empleado[0],  # empleado_id
                'telefono': empleado[7],  # movil
                'nombre': f"{empleado[5]} {empleado[3]} {empleado[4]}",  # nombres + ape_paterno + ape_materno
                'turno': 'Tarde',  # TODO: Implementar lógica de turnos
                'rol': empleado[10]  # nombre_tipo (ya viene del JOIN)
            })
        
        return jsonify({
            'success': True,
            'empleados': empleados_formateados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
