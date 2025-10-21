from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Models.controller_empleado as controller_empleado

empleados_bp = Blueprint('empleados', __name__, template_folder='Templates', url_prefix='/Empleados')

@empleados_bp.route('/', methods=['GET'])
@empleados_bp.route('/Empleados', methods=['GET'])
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
    
    # Obtener empleados y total
    empleados = controller_empleado.get_empleados(limit, offset, search_term, rol_filter)
    total_empleados = controller_empleado.count_empleados(search_term, rol_filter)
    tipos_empleado = controller_empleado.get_tipos_empleado()
    
    # Calcular información de paginación
    total_pages = (total_empleados + limit - 1) // limit
    
    return render_template(
        "Empleados/Empleados.html",
        empleados=empleados,
        tipos_empleado=tipos_empleado,
        current_page=page,
        total_pages=total_pages,
        total_empleados=total_empleados,
        search_term=search_term,
        rol_filter=rol_filter
    )

@empleados_bp.route('/crear', methods=['GET', 'POST'])
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
            if controller_empleado.insert_empleado(
                cod_empleado, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id
            ):
                flash('Empleado creado exitosamente', 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash('Error al crear empleado', 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener tipos de empleado para el formulario
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("Empleados/CrearEmpleado.html", tipos_empleado=tipos_empleado)

@empleados_bp.route('/editar/<int:empleado_id>', methods=['GET', 'POST'])
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
            if controller_empleado.update_empleado(
                empleado_id, cod_empleado, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id
            ):
                flash('Empleado actualizado exitosamente', 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash('Error al actualizar empleado', 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener datos del empleado
    empleado = controller_empleado.get_empleado_by_id(empleado_id)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados.Empleados'))
    
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("Empleados/EditarEmpleado.html", empleado=empleado, tipos_empleado=tipos_empleado)

@empleados_bp.route('/eliminar/<int:empleado_id>', methods=['POST'])
def EliminarEmpleado(empleado_id):
    """
    Eliminar empleado
    """
    try:
        if controller_empleado.delete_empleado(empleado_id):
            flash('Empleado eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar empleado', 'error')
    except Exception as ex:
        flash(f'Error: {str(ex)}', 'error')
    
    return redirect(url_for('empleados.Empleados'))

@empleados_bp.route('/actualizar/<int:empleado_id>', methods=['GET', 'POST'])
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
            if controller_empleado.update_empleado(
                empleado_id, empleado_id, dni, ape_paterno, ape_materno, 
                nombres, sexo, movil, tipo_empleado_id
            ):
                flash('Empleado actualizado exitosamente', 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash('Error al actualizar empleado', 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    # Obtener datos del empleado
    empleado = controller_empleado.get_empleado_by_id(empleado_id)
    if not empleado:
        flash('Empleado no encontrado', 'error')
        return redirect(url_for('empleados.Empleados'))
    
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("Empleados/ActualizarEmpleado.html", empleado=empleado, tipos_empleado=tipos_empleado)

@empleados_bp.route('/registro', methods=['GET', 'POST'])
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
            if controller_empleado.insert_empleado(
                num_documento, num_documento, ape_paterno, ape_materno, 
                nombres, 'M', movil, tipo_empleado_id
            ):
                flash('Empleado registrado exitosamente', 'success')
                return redirect(url_for('empleados.Empleados'))
            else:
                flash('Error al registrar empleado', 'error')
        except Exception as ex:
            flash(f'Error: {str(ex)}', 'error')
    
    tipos_empleado = controller_empleado.get_tipos_empleado()
    return render_template("Empleados/RegistroEmpleado.html", tipos_empleado=tipos_empleado)

@empleados_bp.route('/asignar-turno/<int:empleado_id>', methods=['GET', 'POST'])
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
    
    return render_template("Empleados/AsignarTurno.html", empleado=empleado, turnos=turnos)
