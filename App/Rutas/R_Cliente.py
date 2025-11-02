# routes/ruta_cliente.py
from flask import Blueprint, request, jsonify, render_template
from App.Controladores.C_Cliente.controlador_cliente import (guardar_cliente, buscar_cliente_natural, buscar_cliente_juridico, registrar_cliente_natural,registrar_cliente_juridico)

cliente_bp = Blueprint('cliente_bp',__name__,template_folder='TEMPLATES',url_prefix='/Rutas')

@cliente_bp.route('/form_cliente')
def form_cliente():
    # Renderiza el formulario de reserva con el JS y HTML
    return render_template('reserva.html')

@cliente_bp.route('/guardar_cliente', methods=['POST'])
def ruta_guardar_cliente():
    data = request.get_json()
    cliente_id = guardar_cliente(data)
    return jsonify({'cliente_id': cliente_id})

@cliente_bp.route("/buscar_cliente_natural", methods=["GET"])
def route_buscar_cliente_natural():
    num_doc = request.args.get("num_doc")
    if not num_doc:
        return jsonify({"error": "Falta el parámetro num_doc"}), 400

    row = buscar_cliente_natural(num_doc)
    if not row:
        return jsonify({"mensaje": "Cliente natural no encontrado"}), 404

    # convertir tupla en dict (según el orden del SELECT)
    keys = [
        "cliente_id", "num_doc", "telefono", "id_pais",
        "tipo_doc_id", "ape_paterno", "ape_materno", "nombres"
    ]
    cliente = dict(zip(keys, row))
    return jsonify(cliente), 200


@cliente_bp.route("/buscar_cliente_juridico", methods=["GET"])
def route_buscar_cliente_juridico():
    num_doc = request.args.get("num_doc")
    if not num_doc:
        return jsonify({"error": "Falta el parámetro num_doc"}), 400

    row = buscar_cliente_juridico(num_doc)
    if not row:
        return jsonify({"mensaje": "Cliente jurídico no encontrado"}), 404

    # convertir tupla en dict (según el orden del SELECT)
    keys = [
        "cliente_id", "num_doc", "telefono", "id_pais",
        "tipo_doc_id", "tipoemp_id", "razon_social", "direccion"
    ]
    cliente = dict(zip(keys, row))
    return jsonify(cliente), 200

