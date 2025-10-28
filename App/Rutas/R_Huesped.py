# routes/ruta_huesped.py
from flask import Blueprint, request, jsonify
from App.Controladores.C_Cliente.controlador_huesped import guardar_huesped

huesped_bp = Blueprint('huesped_bp', __name__)

@huesped_bp.route('/guardar_huesped', methods=['POST'])
def ruta_guardar_huesped():
    data = request.get_json()
    huesped_id = guardar_huesped(data)
    return jsonify({'huesped_id': huesped_id})
