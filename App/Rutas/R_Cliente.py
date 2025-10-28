# routes/ruta_cliente.py
from flask import Blueprint, request, jsonify, render_template
from App.Controladores.C_Cliente.controlador_cliente import guardar_cliente

cliente_bp = Blueprint('cliente_bp', __name__)

@cliente_bp.route('/form_cliente')
def form_cliente():
    # Renderiza el formulario de reserva con el JS y HTML
    return render_template('reserva.html')

@cliente_bp.route('/guardar_cliente', methods=['POST'])
def ruta_guardar_cliente():
    data = request.get_json()
    cliente_id = guardar_cliente(data)
    return jsonify({'cliente_id': cliente_id})
