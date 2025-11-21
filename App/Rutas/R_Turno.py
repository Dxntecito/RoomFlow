from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_Turno.controlador_turno as controller_turno
import App.Controladores.C_Turno.controlador_detalle_turno as controller_detalle_turno
from functools import wraps
import App.Rutas.R_Modulos as modulos_module

turno_bp = Blueprint('turno', __name__, template_folder='TEMPLATES/MODULO_TURNO', url_prefix='/Cruds/Turno')

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

def empleado_module_required(f):
    """
    Decorador para proteger rutas que requieren permiso al módulo de empleado
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.Login'))
        # Verificar permiso al módulo de empleado usando la función de R_Modulos
        if not modulos_module._tiene_permiso_modulo('empleado'):
            flash('No tienes permisos para acceder a esta página.', 'danger')
            return redirect(url_for('Index'))
        return f(*args, **kwargs)
    return decorated_function

# ============== RUTAS PARA TURNOS ==============

@turno_bp.route('/GestionarTurno', methods=['GET'])
@empleado_module_required
def GestionarTurno():
    """
    Página para gestionar turnos
    """
    turnos = controller_turno.get_turnos()
    return render_template("Gestionar_Turno.html", turnos=turnos)

@turno_bp.route('/crear-turno', methods=['POST'])
@empleado_module_required
def crear_turno():
    """
    Crear nuevo turno
    """
    try:
        nombre_turno = request.form.get('nombre_turno')
        hora_inicio = request.form.get('hora_inicio')
        hora_fin = request.form.get('hora_fin')
        
        if not nombre_turno or not hora_inicio or not hora_fin:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
        
        success, message = controller_turno.insert_turno(nombre_turno, hora_inicio, hora_fin)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al crear turno: {str(e)}'
        })

@turno_bp.route('/actualizar-turno/<int:turno_id>', methods=['POST'])
@empleado_module_required
def actualizar_turno(turno_id):
    """
    Actualizar turno existente
    """
    try:
        nombre_turno = request.form.get('nombre_turno')
        hora_inicio = request.form.get('hora_inicio')
        hora_fin = request.form.get('hora_fin')
        
        if not nombre_turno or not hora_inicio or not hora_fin:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
        
        success, message = controller_turno.update_turno(turno_id, nombre_turno, hora_inicio, hora_fin)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar turno: {str(e)}'
        })

@turno_bp.route('/eliminar-turno/<int:turno_id>', methods=['POST'])
@empleado_module_required
def eliminar_turno(turno_id):
    """
    Eliminar turno
    """
    try:
        success, message = controller_turno.delete_turno(turno_id)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al eliminar turno: {str(e)}'
        })

@turno_bp.route('/api/turno/<int:turno_id>', methods=['GET'])
@empleado_module_required
def api_turno(turno_id):
    """
    Obtener un turno específico en formato JSON
    """
    try:
        turno = controller_turno.get_turno_by_id(turno_id)
        if turno:
            return jsonify({
                'success': True,
                'turno': {
                    'turno_id': turno[0],
                    'nombre_turno': turno[1],
                    'hora_inicio': str(turno[2]),
                    'hora_fin': str(turno[3])
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Turno no encontrado'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener turno: {str(e)}'
        })

# ============== RUTAS PARA DETALLE DE TURNOS ==============

@turno_bp.route('/GestionarDetalleTurno', methods=['GET'])
@empleado_module_required
def GestionarDetalleTurno():
    """
    Página para gestionar detalles de turno (asignaciones)
    """
    return render_template("Gestionar_Detalle_Turno.html")

@turno_bp.route('/crear-detalle-turno', methods=['POST'])
@empleado_module_required
def crear_detalle_turno():
    """
    Crear nuevo detalle de turno (asignar turno a empleado)
    """
    try:
        empleado_id = request.form.get('empleado_id')
        turno_id = request.form.get('turno_id')
        fecha = request.form.get('fecha')
        
        if not empleado_id or not turno_id or not fecha:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
        
        success, message = controller_detalle_turno.insert_detalle_turno(empleado_id, turno_id, fecha)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al asignar turno: {str(e)}'
        })

@turno_bp.route('/actualizar-detalle-turno', methods=['POST'])
@empleado_module_required
def actualizar_detalle_turno():
    """
    Actualizar detalle de turno existente
    """
    try:
        empleado_id_original = request.form.get('empleado_id_original')
        turno_id_original = request.form.get('turno_id_original')
        fecha_original = request.form.get('fecha_original')
        empleado_id = request.form.get('empleado_id')
        turno_id = request.form.get('turno_id')
        fecha = request.form.get('fecha')
        
        if not empleado_id_original or not turno_id_original or not fecha_original:
            return jsonify({
                'success': False,
                'message': 'Datos originales no proporcionados'
            })
        
        if not empleado_id or not turno_id or not fecha:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
        
        success, message = controller_detalle_turno.update_detalle_turno(
            empleado_id_original, turno_id_original, fecha_original,
            empleado_id, turno_id, fecha
        )
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al actualizar asignación: {str(e)}'
        })

@turno_bp.route('/eliminar-detalle-turno', methods=['POST'])
@empleado_module_required
def eliminar_detalle_turno():
    """
    Eliminar detalle de turno (desasignar turno de empleado)
    """
    try:
        empleado_id = request.form.get('empleado_id')
        turno_id = request.form.get('turno_id')
        fecha = request.form.get('fecha')
        
        if not empleado_id or not turno_id or not fecha:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
        
        success, message = controller_detalle_turno.delete_detalle_turno(empleado_id, turno_id, fecha)
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al desasignar turno: {str(e)}'
        })

@turno_bp.route('/api/detalles-turno', methods=['GET'])
@empleado_module_required
def api_detalles_turno():
    """
    Obtener todos los detalles de turno en formato JSON
    """
    try:
        empleado_id = request.args.get('empleado_id', type=int)
        turno_id = request.args.get('turno_id', type=int)
        fecha = request.args.get('fecha')
        
        detalles = controller_detalle_turno.get_detalles_turno(empleado_id, turno_id, fecha)
        
        detalles_formateados = []
        for detalle in detalles:
            detalles_formateados.append({
                'empleado_id': detalle[0],
                'turno_id': detalle[1],
                'fecha': str(detalle[2]),
                'nombres': detalle[3],
                'ape_paterno': detalle[4],
                'ape_materno': detalle[5],
                'cod_empleado': detalle[6],
                'nombre_turno': detalle[7],
                'hora_inicio': str(detalle[8]),
                'hora_fin': str(detalle[9]),
                'nombre_completo': f"{detalle[3]} {detalle[4]} {detalle[5]}"
            })
        
        return jsonify({
            'success': True,
            'detalles': detalles_formateados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles: {str(e)}'
        })

@turno_bp.route('/api/empleados-activos', methods=['GET'])
@empleado_module_required
def api_empleados_activos():
    """
    Obtener lista de empleados activos para selectores
    """
    try:
        empleados = controller_detalle_turno.get_empleados_activos()
        empleados_formateados = []
        for emp in empleados:
            empleados_formateados.append({
                'empleado_id': emp[0],
                'cod_empleado': emp[1],
                'dni': emp[2],
                'nombres': emp[3],
                'ape_paterno': emp[4],
                'ape_materno': emp[5],
                'nombre_completo': f"{emp[3]} {emp[4]} {emp[5]}"
            })
        return jsonify({
            'success': True,
            'empleados': empleados_formateados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener empleados: {str(e)}'
        })

@turno_bp.route('/api/turnos-disponibles', methods=['GET'])
@empleado_module_required
def api_turnos_disponibles():
    """
    Obtener lista de turnos disponibles para selectores
    """
    try:
        turnos = controller_detalle_turno.get_turnos_disponibles()
        turnos_formateados = []
        for turno in turnos:
            turnos_formateados.append({
                'turno_id': turno[0],
                'nombre_turno': turno[1]
            })
        return jsonify({
            'success': True,
            'turnos': turnos_formateados
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener turnos: {str(e)}'
        })
