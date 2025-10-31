from flask import Blueprint, request, jsonify, current_app
from App.Controladores.C_Facturacion.controlador_transaccion import registrar_transaccion

transaccion_bp = Blueprint('transaccion', __name__, url_prefix='/Rutas')

@transaccion_bp.route('/guardar_transaccion', methods=['POST'])
def guardar_transaccion():
    try:
        data = request.get_json(force=True)
        current_app.logger.info(f"[guardar_transaccion] payload: {data}")

        trans_id = registrar_transaccion(data)
        if trans_id:
            return jsonify({'success': True, 'transaccion_id': trans_id}), 200
        else:
            return jsonify({'success': False, 'error': 'Datos incompletos o error al insertar'}), 400
    except Exception as e:
        current_app.logger.exception("❌ Error en /guardar_transaccion")
        return jsonify({'success': False, 'error': str(e)}), 500