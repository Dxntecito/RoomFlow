from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from App.Controladores.C_Incidencia.controlador_incidencia import ControladorIncidencia
from functools import wraps
from bd import get_connection

incidentes_bp = Blueprint('incidentes', __name__, url_prefix='/incidentes')

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'success': False, 'message': 'Debe iniciar sesión'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Función helper para obtener cliente_id del usuario actual
def obtener_cliente_id_usuario():
    """
    Obtiene el cliente_id asociado al usuario_id de la sesión.
    Retorna None si no encuentra un cliente asociado.
    """
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return None
    
    conexion = None
    try:
        conexion = get_connection()
        with conexion.cursor() as cursor:
            sql = """
                SELECT cliente_id 
                FROM CLIENTE
                WHERE usuario_id = %s
                LIMIT 1
            """
            cursor.execute(sql, (usuario_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                return resultado[0]
            return None
    except Exception as e:
        print(f"Error al obtener cliente_id: {e}")
        return None
    finally:
        if conexion:
            conexion.close()

@incidentes_bp.route('/tipos', methods=['GET'])
@login_required
def obtener_tipos():
    """Obtiene los tipos de incidencia"""
    try:
        tipos = ControladorIncidencia.obtener_tipos_incidencia()
        return jsonify({'success': True, 'tipos': tipos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/mis-incidencias', methods=['GET'])
@login_required
def obtener_mis_incidencias():
    """Obtiene las incidencias del cliente actual"""
    try:
        # Obtener el cliente_id del usuario actual
        cliente_id = obtener_cliente_id_usuario()
        
        # Si no hay cliente_id, retornar lista vacía (no es un error)
        if not cliente_id:
            return jsonify({'success': True, 'incidencias': []})
        
        incidencias = ControladorIncidencia.obtener_incidencias_cliente(cliente_id)
        return jsonify({'success': True, 'incidencias': incidencias})
    except Exception as e:
        print(f"Error en obtener_mis_incidencias: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/crear', methods=['POST'])
@login_required
def crear_incidencia():
    """Crea una nueva incidencia"""
    try:
        # Obtener el cliente_id del usuario actual
        cliente_id = obtener_cliente_id_usuario()
        
        if not cliente_id:
            return jsonify({'success': False, 'message': 'No se encontró el cliente asociado a su cuenta. Por favor contacte al administrador.'}), 400
        
        # Obtener datos del formulario
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        tipo_incidencia_id = request.form.get('tipo_incidencia_id')
        numero_comprobante = request.form.get('numero_comprobante')
        
        # Validar campos requeridos
        if not titulo or not descripcion or not tipo_incidencia_id:
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
        
        # Obtener archivo de evidencia si existe
        evidencia = None
        if 'evidencia' in request.files:
            archivo = request.files['evidencia']
            if archivo and archivo.filename != '':
                # Leer el archivo como bytes para guardarlo en BLOB
                evidencia = archivo.read()
        
        # Preparar datos para crear incidencia
        datos = {
            'titulo': titulo,
            'descripcion': descripcion,
            'tipo_incidencia_id': int(tipo_incidencia_id),
            'numero_comprobante': numero_comprobante if numero_comprobante else None,
            'evidencia': evidencia,
            'cliente_id': cliente_id
        }
        
        resultado = ControladorIncidencia.crear_incidencia(datos)
        
        if resultado['success']:
            return jsonify(resultado), 201
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        print(f"Error al crear incidencia: {e}")
        return jsonify({'success': False, 'message': f'Error al crear incidencia: {str(e)}'}), 500

@incidentes_bp.route('/actualizar/<int:incidencia_id>', methods=['PUT', 'POST'])
@login_required
def actualizar_incidencia(incidencia_id):
    """Actualiza una incidencia existente"""
    try:
        # Verificar que la incidencia pertenezca al cliente actual
        incidencia = ControladorIncidencia.obtener_incidencia(incidencia_id)
        
        if not incidencia:
            return jsonify({'success': False, 'message': 'Incidencia no encontrada'}), 404
        
        # Obtener el cliente_id del usuario actual
        cliente_id = obtener_cliente_id_usuario()
        rol_id = session.get('rol_id')
        
        # Solo el dueño o un admin pueden actualizar
        if incidencia['cliente_id'] != cliente_id and rol_id != 1:
            return jsonify({'success': False, 'message': 'No tiene permisos para actualizar esta incidencia'}), 403
        
        # Obtener datos del formulario
        datos = {}
        
        if request.form.get('titulo'):
            datos['titulo'] = request.form.get('titulo')
        
        if request.form.get('descripcion'):
            datos['descripcion'] = request.form.get('descripcion')
        
        if request.form.get('tipo_incidencia_id'):
            datos['tipo_incidencia_id'] = int(request.form.get('tipo_incidencia_id'))
        
        if request.form.get('numero_comprobante'):
            datos['numero_comprobante'] = request.form.get('numero_comprobante')
        
        if request.form.get('estado'):
            datos['estado'] = int(request.form.get('estado'))
        
        if request.form.get('respuesta'):
            datos['respuesta'] = request.form.get('respuesta')
        
        # Obtener archivo de evidencia si existe
        if 'evidencia' in request.files:
            archivo = request.files['evidencia']
            if archivo and archivo.filename != '':
                datos['evidencia'] = archivo.read()
        
        resultado = ControladorIncidencia.actualizar_incidencia(incidencia_id, datos)
        
        return jsonify(resultado)
            
    except Exception as e:
        print(f"Error al actualizar incidencia: {e}")
        return jsonify({'success': False, 'message': f'Error al actualizar incidencia: {str(e)}'}), 500

@incidentes_bp.route('/obtener/<int:incidencia_id>', methods=['GET'])
@login_required
def obtener_incidencia(incidencia_id):
    """Obtiene una incidencia específica"""
    try:
        incidencia = ControladorIncidencia.obtener_incidencia(incidencia_id)
        
        if not incidencia:
            return jsonify({'success': False, 'message': 'Incidencia no encontrada'}), 404
        
        # Obtener el cliente_id del usuario actual
        cliente_id = obtener_cliente_id_usuario()
        rol_id = session.get('rol_id')
        
        # Verificar permisos
        if incidencia['cliente_id'] != cliente_id and rol_id != 1:
            return jsonify({'success': False, 'message': 'No tiene permisos para ver esta incidencia'}), 403
        
        return jsonify({'success': True, 'incidencia': incidencia})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/eliminar/<int:incidencia_id>', methods=['DELETE', 'POST'])
@login_required
def eliminar_incidencia(incidencia_id):
    """Elimina una incidencia"""
    try:
        # Verificar que la incidencia pertenezca al cliente actual
        incidencia = ControladorIncidencia.obtener_incidencia(incidencia_id)
        
        if not incidencia:
            return jsonify({'success': False, 'message': 'Incidencia no encontrada'}), 404
        
        # Obtener el cliente_id del usuario actual
        cliente_id = obtener_cliente_id_usuario()
        rol_id = session.get('rol_id')
        
        # Solo el dueño o un admin pueden eliminar
        if incidencia['cliente_id'] != cliente_id and rol_id != 1:
            return jsonify({'success': False, 'message': 'No tiene permisos para eliminar esta incidencia'}), 403
        
        resultado = ControladorIncidencia.eliminar_incidencia(incidencia_id)
        return jsonify(resultado)
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/todas', methods=['GET'])
@login_required
def obtener_todas_incidencias():
    """Obtiene todas las incidencias (solo para administradores)"""
    try:
        rol_id = session.get('rol_id')
        print(f"🔍 Debug obtener_todas_incidencias:")
        print(f"- rol_id: {rol_id}")
        print(f"- session: {dict(session)}")
        
        if rol_id != 1:
            print(f"❌ Usuario no es administrador (rol_id: {rol_id})")
            return jsonify({'success': False, 'message': 'No tiene permisos para ver todas las incidencias'}), 403
        
        incidencias = ControladorIncidencia.obtener_todas_incidencias()
        return jsonify({'success': True, 'incidencias': incidencias})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/tipos', methods=['GET'])
@login_required
def obtener_tipos_incidencia():
    """Obtiene los tipos de incidencia disponibles"""
    try:
        tipos = ControladorIncidencia.obtener_tipos_incidencia()
        return jsonify({'success': True, 'tipos': tipos})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@incidentes_bp.route('/responder/<int:incidencia_id>', methods=['POST'])
@login_required
def responder_incidencia(incidencia_id):
    """Responde y actualiza el estado de una incidencia (para administradores/empleados)"""
    try:
        rol_id = session.get('rol_id')
        
        # Solo administradores y empleados pueden responder
        if rol_id not in [1, 2]:
            return jsonify({'success': False, 'message': 'No tiene permisos para responder incidencias'}), 403
        
        respuesta = request.form.get('respuesta')
        estado = request.form.get('estado')
        
        if not respuesta or not estado:
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
        
        datos = {
            'respuesta': respuesta,
            'estado': int(estado)
        }
        
        resultado = ControladorIncidencia.actualizar_incidencia(incidencia_id, datos)
        return jsonify(resultado)
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

