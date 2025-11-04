from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app
import App.Controladores.C_Evento.controlador_evento as controlador_evento
import App.Controladores.C_Reserva.controlador_pais as controlador_pais

eventos_bp = Blueprint('eventos', __name__, template_folder='TEMPLATES', url_prefix='/Eventos')

@eventos_bp.route('/', methods=['GET'])
@eventos_bp.route('/Eventos', methods=['GET'])
def Eventos():
    tipos_evento = controlador_evento.get_tipos_eventos()
    metodos_pago = controlador_evento.get_metodos_pago()
    countries=controlador_pais.get_countries()
    tipo_doc=controlador_evento.get_tipo_documento()
    return render_template("Eventos.html",tipos_evento=tipos_evento, metodos_pago=metodos_pago,countries=countries
                           ,tipo_doc=tipo_doc)

@eventos_bp.route("/procesar_pago", methods=["POST"])
def procesar_pago_route():
    controlador_evento.procesar_pago()
    return jsonify({"success": True, "redirect_url": url_for("Index")})


