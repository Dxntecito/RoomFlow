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
    empleados = controller_empleado.get_empleados(limit, offset, search_term, rol_filter)
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
            # Aceptar tanto 'movil' como 'telefono' del formulario
            movil = request.form.get('movil') or request.form.get('telefono')
            # Aceptar tanto 'tipo_empleado_id' como 'rol' del formulario
            tipo_empleado_id = request.form.get('tipo_empleado_id') or request.form.get('rol')
            email = request.form.get('email', None)  # Email opcional
            
            # Validar datos requeridos
            if not all([dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id]):
                return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
            
            # Insertar empleado (ahora también crea el usuario automáticamente)
            success, message, cod_empleado = controller_empleado.insert_empleado_auto(
                dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id, email
            )
            
            # Si fue exitoso, mostrar información de las credenciales
            return jsonify({'success': success, 'message': message, 'codigo': cod_empleado})
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error al crear empleado: {str(e)}'})
    
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
            dni = request.form.get('dni')
            ape_paterno = request.form.get('ape_paterno')
            ape_materno = request.form.get('ape_materno')
            nombres = request.form.get('nombres')
            sexo = request.form.get('sexo')
            movil = request.form.get('movil')
            tipo_empleado_id = request.form.get('tipo_empleado_id')
            estado = request.form.get('estado', 'Activo')  # Por defecto 'Activo' si no se proporciona
            
            # Validar datos requeridos
            if not all([dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id]):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('empleados.EditarEmpleado', empleado_id=empleado_id))
            
            # Actualizar empleado (la función genera el código automáticamente)
            success, message = controller_empleado.update_empleado(
                empleado_id, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id, estado
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
        return jsonify({'success': success, 'message': message})
    except Exception as ex:
        return jsonify({'success': False, 'message': f'Error: {str(ex)}'})

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
            # Aceptar tanto 'movil' como 'telefono' del formulario
            movil = request.form.get('movil') or request.form.get('telefono')
            sexo = request.form.get('sexo')
            # Aceptar tanto 'tipo_empleado_id' como 'rol' del formulario
            tipo_empleado_id = request.form.get('tipo_empleado_id') or request.form.get('rol')
            estado = request.form.get('estado')
            
            # Validar datos requeridos
            if not all([ape_paterno, ape_materno, nombres, dni, movil, sexo, tipo_empleado_id, estado]):
                return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
            
            # Actualizar empleado
            success, message = controller_empleado.update_empleado(
                empleado_id, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id, estado
            )
            return jsonify({'success': success, 'message': message})
        except Exception as ex:
            return jsonify({'success': False, 'message': f'Error: {str(ex)}'})
    
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
            
            # Insertar empleado con código generado automáticamente
            success, message, cod_empleado = controller_empleado.insert_empleado_auto(
                num_documento, ape_paterno, ape_materno, nombres, 'M', movil, tipo_empleado_id, email
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
            
            # Asignar turno usando el controlador
            success, message = controller_empleado.asignar_turno_empleado(empleado_id, turno_id)
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
            return redirect(url_for('empleados.Empleados'))
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener datos del empleado
    empleado = controller_empleado.get_empleado_by_id(empleado_id)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados.Empleados'))
    
    # Obtener turnos disponibles desde la base de datos
    turnos = controller_empleado.get_turnos()
    
    return render_template("AsignarTurno.html", empleado=empleado, turnos=turnos)

@empleados_bp.route('/api/empleados', methods=['GET'])
@admin_required
def api_empleados():
    """
    API endpoint para obtener empleados en formato JSON
    """
    try:
        # Obtener todos los empleados activos
        empleados = controller_empleado.get_empleados(limit=100, offset=0, search_term='', rol_filter='')
        tipos_empleado = controller_empleado.get_tipos_empleado()
        
        # Crear diccionario de tipos para mapear IDs a nombres
        tipos_dict = {tipo[0]: tipo[1] for tipo in tipos_empleado}
        
        # Formatear datos para el frontend
        empleados_formateados = []
        for empleado in empleados:
            empleados_formateados.append({
                'id': empleado[0],  # empleado_id
                'codigo': empleado[1],  # cod_empleado
                'dni': empleado[2],  # dni
                'ape_paterno': empleado[3],  # ape_paterno
                'ape_materno': empleado[4],  # ape_materno
                'nombres': empleado[5],  # nombres
                'sexo': empleado[6],  # sexo
                'telefono': empleado[7],  # movil
                'rol_id': empleado[8],  # tipo_empleado_id
                'estado': empleado[9],  # estado
                'rol': empleado[10],  # nombre_tipo (ya viene del JOIN)
                'nombre': f"{empleado[5]} {empleado[3]} {empleado[4]}",  # nombres + ape_paterno + ape_materno
                'turno': empleado[11] if empleado[11] else 'Sin turno'  # Turno real o 'Sin turno'
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

@empleados_bp.route('/buscar/<dni>', methods=['GET'])
@admin_required
def buscar_empleado(dni):
    """
    Buscar empleado por DNI
    """
    try:
        empleado = controller_empleado.get_empleado_by_dni(dni)
        if empleado:
            return jsonify({
                'success': True,
                'empleado': {
                    'id': empleado[0],
                    'nombre': f"{empleado[5]} {empleado[3]} {empleado[4]}",
                    'dni': empleado[2]
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Empleado no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al buscar empleado: {str(e)}'
        })

@empleados_bp.route('/asignar-turno', methods=['POST'])
@admin_required
def asignar_turno():
    """
    Asignar turno a empleado
    """
    try:
        empleado_id = request.form.get('empleado_id')
        turno_id = request.form.get('turno')
        
        if not empleado_id or not turno_id:
            return jsonify({
                'success': False,
                'message': 'Empleado y turno son requeridos'
            })
        
        # Asignar turno usando el controlador
        success, message = controller_empleado.asignar_turno_empleado(empleado_id, turno_id)
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al asignar turno: {str(e)}'
        })

@empleados_bp.route('/turnos', methods=['GET'])
@admin_required
def get_turnos_api():
    """
    Obtener la lista de turnos para el frontend
    """
    try:
        turnos = controller_empleado.get_turnos()
        turnos_list = [{'id': t[0], 'nombre': t[1]} for t in turnos]
        return jsonify({
            'success': True,
            'turnos': turnos_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener turnos: {str(e)}'
        })

@empleados_bp.route('/turno-actual/<int:empleado_id>', methods=['GET'])
@admin_required
def get_turno_actual_api(empleado_id):
    """
    Obtener el turno actual de un empleado
    """
    try:
        turno = controller_empleado.get_turno_actual_empleado(empleado_id)
        if turno:
            return jsonify({
                'success': True,
                'turno': {
                    'id': turno[0],
                    'nombre': turno[1]
                }
            })
        else:
            return jsonify({
                'success': True,
                'turno': None
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener turno actual: {str(e)}'
        })