# routes/ruta_reserva_habitacion.py
from flask import Blueprint, request, jsonify
from App.Controladores.C_Reserva.controlador_reserva_habitacion import guardar_reserva_habitacion

reserva_habitacion_bp = Blueprint('reserva_habitacion_bp', __name__)

@reserva_habitacion_bp.route('/guardar_reserva_habitacion', methods=['POST'])
def ruta_guardar_reserva_habitacion():
    data = request.get_json()
    reserva_habitacion_id = guardar_reserva_habitacion(data)
    return jsonify({'reserva_habitacion_id': reserva_habitacion_id})
