from flask import Blueprint, request, jsonify, session
from App.Controladores.C_Promocion.controlador_promocion import ControladorPromocion
from functools import wraps
import traceback

promocion_bp = Blueprint('promociones', __name__, url_prefix='/promociones')

# --- Roles (para legibilidad) ---
ADMIN_ROLE = 1
ADMIN_ROLE_ALT = 4  # Rol alternativo de administrador

# --- Decorador de Administrador ---
def admin_required(f):
    """
    Decorador que verifica que el usuario sea Administrador (rol_id == 1 o rol_id == 4)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        rol_id = session.get('rol_id')
        if 'usuario_id' not in session or rol_id not in [ADMIN_ROLE, ADMIN_ROLE_ALT]:
            return jsonify({'success': False, 'message': 'Acceso denegado. Se requieren permisos de administrador.'}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DE PROMOCIONES (Solo Admin) ---

@promocion_bp.route('/todas', methods=['GET'])
@admin_required
def obtener_todas_promociones():
    """Obtiene TODAS las promociones"""
    try:
        promociones = ControladorPromocion.listar_promociones()
        return jsonify({'success': True, 'promociones': promociones})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@promocion_bp.route('/tipos', methods=['GET'])
@admin_required
def obtener_tipos_promocion():
    """Obtiene los tipos de promoción disponibles"""
    try:
        tipos = ControladorPromocion.get_tipos_promocion()
        return jsonify({'success': True, 'tipos': tipos})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@promocion_bp.route('/crear', methods=['POST'])
@admin_required
def crear_promocion():
    """Crea una nueva promoción"""
    try:
        datos = request.form.to_dict()
        
        # Validación básica de campos
        requeridos = ['porcentaje', 'descripcion', 'fecha_inicio', 'fecha_fin', 'tipo_promocion_id']
        if not all(k in datos for k in requeridos):
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
        
        resultado = ControladorPromocion.crear_promocion(datos)
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

@promocion_bp.route('/<int:promocion_id>', methods=['GET'])
@admin_required
def obtener_promocion(promocion_id):
    """Obtiene una promoción específica"""
    try:
        promocion = ControladorPromocion.obtener_promocion(promocion_id)
        if not promocion:
            return jsonify({'success': False, 'message': 'Promoción no encontrada'}), 404
        return jsonify({'success': True, 'promocion': promocion})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@promocion_bp.route('/<int:promocion_id>/actualizar', methods=['POST', 'PUT'])
@admin_required
def actualizar_promocion(promocion_id):
    """Actualiza una promoción"""
    try:
        datos = request.form.to_dict()
        if not datos:
            return jsonify({'success': False, 'message': 'No se enviaron datos'}), 400
            
        resultado = ControladorPromocion.actualizar_promocion(promocion_id, datos)
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@promocion_bp.route('/<int:promocion_id>/cambiar_estado', methods=['POST'])
@admin_required
def cambiar_estado_promocion(promocion_id):
    """Activa o desactiva una promoción"""
    try:
        nuevo_estado = request.form.get('estado')
        if nuevo_estado not in ['0', '1']:
            return jsonify({'success': False, 'message': "El estado debe ser '0' o '1'"}), 400
            
        resultado = ControladorPromocion.cambiar_estado_promocion(promocion_id, int(nuevo_estado))
        return jsonify(resultado)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500