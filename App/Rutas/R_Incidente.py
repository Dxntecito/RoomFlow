from flask import Blueprint, request, jsonify, session, abort
from App.Controladores.C_Incidencia.controlador_incidencia import ControladorIncidencia
from functools import wraps
from bd import get_connection
import traceback
import pymysql.cursors # <--- 1. IMPORTA EL CURSOR DE DICCIONARIO

incidentes_bp = Blueprint('incidentes', __name__, url_prefix='/incidentes')

# --- Roles (para legibilidad) ---
ADMIN_ROLE = 1
EMPLEADO_ROLE = 2
CLIENTE_ROLE = 3

# --- Decorador de autenticación ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or 'rol_id' not in session:
            return jsonify({'success': False, 'message': 'Debe iniciar sesión'}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Función Helper (Tu Función Original) ---
def obtener_cliente_id_usuario():
    """Obtiene el cliente_id asociado al usuario_id de la sesión."""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None
    
    conexion = None
    try:
        conexion = get_connection() 
        # 2. USA EL CURSOR DE DICCIONARIO
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor: 
            sql = "SELECT cliente_id FROM USUARIO WHERE usuario_id = %s LIMIT 1"
            cursor.execute(sql, (usuario_id,))
            resultado = cursor.fetchone()
            return resultado['cliente_id'] if (resultado and resultado['cliente_id']) else None 
    except Exception as e:
        print(f"Error al obtener cliente_id desde USUARIO: {e}")
        traceback.print_exc()
        return None
    finally:
        if conexion:
            conexion.close()

def obtener_empleado_id_usuario():
    """Obtiene el empleado_id asociado al usuario_id de la sesión."""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None
    
    conexion = None
    try:
        conexion = get_connection() 
        with conexion.cursor(pymysql.cursors.DictCursor) as cursor: 
            sql = "SELECT empleado_id FROM USUARIO WHERE usuario_id = %s LIMIT 1"
            cursor.execute(sql, (usuario_id,))
            resultado = cursor.fetchone()
            return resultado['empleado_id'] if (resultado and resultado['empleado_id']) else None 
    except Exception as e:
        print(f"Error al obtener empleado_id desde USUARIO: {e}")
        traceback.print_exc()
        return None
    finally:
        if conexion:
            conexion.close()

# --- Función Helper de Permisos ---
def _get_and_check_permission(incidencia_id):
    """Obtiene una incidencia y verifica el permiso del usuario actual."""
    incidencia = ControladorIncidencia.obtener_incidencia(incidencia_id)
    if not incidencia:
        return None, (jsonify({'success': False, 'message': 'Incidencia no encontrada'}), 404)
    
    rol_id = session.get('rol_id')
    
    # Roles 1, 2 y 4 pueden ver cualquier incidencia
    if rol_id in [ADMIN_ROLE, EMPLEADO_ROLE, 4]:
        return incidencia, None
    
    # Clientes solo pueden ver sus propias incidencias
    cliente_id_actual = obtener_cliente_id_usuario()
    if rol_id == CLIENTE_ROLE and incidencia['cliente_id'] == cliente_id_actual:
        return incidencia, None
    
    return None, (jsonify({'success': False, 'message': 'No tiene permisos sobre esta incidencia'}), 403)


# --- RUTAS DE INCIDENCIAS ---

@incidentes_bp.route('/tipos', methods=['GET'])
@login_required
def obtener_tipos_incidencia():
    """Obtiene los tipos de incidencia disponibles (Ruta única)"""
    try:
        tipos = ControladorIncidencia.obtener_tipos_incidencia()
        return jsonify({'success': True, 'tipos': tipos})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/mis-incidencias', methods=['GET'])
@login_required
def obtener_mis_incidencias():
    """Obtiene las incidencias del CLIENTE actual"""
    try:
        if session.get('rol_id') != CLIENTE_ROLE:
            return jsonify({'success': False, 'message': 'Esta ruta es solo para clientes'}), 403
            
        cliente_id = obtener_cliente_id_usuario()
        if not cliente_id:
            # CAMBIO: Devuelve éxito pero con lista vacía y un mensaje claro para el frontend
            return jsonify({'success': True, 'incidencias': [], 'message': 'Este usuario no está asociado a un cliente'})
        
        incidencias = ControladorIncidencia.obtener_incidencias_cliente(cliente_id)
        return jsonify({'success': True, 'incidencias': incidencias})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/todas', methods=['GET'])
@login_required
def obtener_todas_incidencias():
    """Obtiene TODAS las incidencias (solo para administradores/empleados/rol 4)"""
    try:
        rol_id = session.get('rol_id')
        if rol_id not in [ADMIN_ROLE, EMPLEADO_ROLE, 4]:
            return jsonify({'success': False, 'message': 'No tiene permisos para ver todas las incidencias'}), 403
        
        incidencias = ControladorIncidencia.obtener_todas_incidencias()
        return jsonify({'success': True, 'incidencias': incidencias})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/pendientes', methods=['GET'])
@login_required
def obtener_incidencias_pendientes():
    """Obtiene solo las incidencias pendientes (estado = 3) para empleados/administradores/rol 4"""
    try:
        rol_id = session.get('rol_id')
        if rol_id not in [ADMIN_ROLE, EMPLEADO_ROLE, 4]:
            return jsonify({'success': False, 'message': 'No tiene permisos para ver incidencias'}), 403
        
        incidencias = ControladorIncidencia.obtener_incidencias_pendientes()
        return jsonify({'success': True, 'incidencias': incidencias})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/crear', methods=['POST'])
@login_required
def crear_incidencia():
    """Crea una nueva incidencia (solo para clientes)"""
    try:
        if session.get('rol_id') != CLIENTE_ROLE:
            return jsonify({'success': False, 'message': 'Solo los clientes pueden reportar incidencias'}), 403

        cliente_id = obtener_cliente_id_usuario()
        if not cliente_id:
            return jsonify({'success': False, 'message': 'No se encontró el cliente asociado a su cuenta.'}), 400
        
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        tipo_incidencia_id = request.form.get('tipo_incidencia_id')
        
        if not titulo or not descripcion or not tipo_incidencia_id:
            return jsonify({'success': False, 'message': 'Faltan campos requeridos (título, descripción, tipo)'}), 400
        
        datos = {
            'titulo': titulo,
            'descripcion': descripcion,
            'tipo_incidencia_id': int(tipo_incidencia_id),
            'numero_comprobante': request.form.get('numero_comprobante'),
            'cliente_id': cliente_id,
            'empleado_id': None
        }

        if 'evidencia' in request.files:
            archivo = request.files['evidencia']
            if archivo and archivo.filename != '':
                datos['evidencia'] = archivo.read()
        
        resultado = ControladorIncidencia.crear_incidencia(datos)
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@incidentes_bp.route('/<int:incidencia_id>', methods=['GET'])
@login_required
def obtener_incidencia(incidencia_id):
    """Obtiene una incidencia específica (dueño, admin, empleado o rol 4)"""
    try:
        incidencia, error = _get_and_check_permission(incidencia_id) 
        if error:
            return error
        return jsonify({'success': True, 'incidencia': incidencia})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/<int:incidencia_id>/actualizar', methods=['POST', 'PUT'])
@login_required
def actualizar_incidencia(incidencia_id):
    """Actualiza una incidencia (solo dueño o admin)"""
    try:
        incidencia, error = _get_and_check_permission(incidencia_id)
        if error:
            return error
        
        datos = {}
        if 'titulo' in request.form:
            datos['titulo'] = request.form.get('titulo')
        if 'descripcion' in request.form:
            datos['descripcion'] = request.form.get('descripcion')
        if 'tipo_incidencia_id' in request.form:
            datos['tipo_incidencia_id'] = int(request.form.get('tipo_incidencia_id'))
        if 'numero_comprobante' in request.form:
            datos['numero_comprobante'] = request.form.get('numero_comprobante')
        
        if 'evidencia' in request.files:
            archivo = request.files['evidencia']
            if archivo and archivo.filename != '':
                datos['evidencia'] = archivo.read()
        
        if not datos:
            return jsonify({'success': False, 'message': 'No se enviaron datos para actualizar'}), 400

        resultado = ControladorIncidencia.actualizar_incidencia(incidencia_id, datos)
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error al actualizar incidencia: {str(e)}'}), 500

@incidentes_bp.route('/<int:incidencia_id>/responder', methods=['POST'])
@login_required
def responder_incidencia(incidencia_id):
    """Responde y actualiza el estado (solo para admin/empleado/rol 4)"""
    try:
        rol_id = session.get('rol_id')
        if rol_id not in [ADMIN_ROLE, EMPLEADO_ROLE, 4]:
            return jsonify({'success': False, 'message': 'No tiene permisos para responder incidencias'}), 403
        
        respuesta = request.form.get('respuesta')
        estado = request.form.get('estado')
        
        if not respuesta or not estado:
            return jsonify({'success': False, 'message': 'Faltan campos (respuesta, estado)'}), 400
        
        # Obtener empleado_id del usuario actual
        empleado_id = obtener_empleado_id_usuario()
        
        datos = {
            'respuesta': respuesta,
            'estado': int(estado),
            'empleado_id': empleado_id
        }
        
        resultado = ControladorIncidencia.actualizar_incidencia(incidencia_id, datos)
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/<int:incidencia_id>/eliminar', methods=['POST', 'DELETE'])
@login_required
def eliminar_incidencia(incidencia_id):
    """Elimina una incidencia (solo dueño o admin)"""
    try:
        incidencia, error = _get_and_check_permission(incidencia_id)
        if error:
            return error
        
        resultado = ControladorIncidencia.eliminar_incidencia(incidencia_id)
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500