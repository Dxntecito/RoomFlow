from flask import render_template, Blueprint, jsonify, request
import App.Controladores.C_Reserva.controlador_reserva as controller_reserva

facturaciones_bp = Blueprint('facturacion', __name__, template_folder='Templates', url_prefix='/WEB_CLIENTE/Facturacion')

@facturaciones_bp.route('/', methods=['GET'])
@facturaciones_bp.route('/Facturacion', methods=['GET'])
def Facturacion():
    return render_template("Facturacion.html")


@facturaciones_bp.route('/pendientes', methods=['GET'])
def obtener_pendientes():
    data = controller_reserva.listar_reservas_pendientes_validacion()
    return jsonify({"data": data})


@facturaciones_bp.route('/validar/<int:reserva_id>', methods=['POST'])
def validar_reserva(reserva_id):
    ok = controller_reserva.actualizar_validado_reserva(reserva_id, "1")
    if ok:
        return jsonify({"success": True})
    return jsonify({"success": False}), 400