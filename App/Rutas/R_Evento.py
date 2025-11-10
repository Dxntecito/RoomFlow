from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app
import App.Controladores.C_Evento.controlador_evento as controlador_evento
import App.Controladores.C_Reserva.controlador_pais as controlador_pais
import App.Controladores.C_Evento.controlador_servicios_evento as controlador_servicios_evento
from datetime import date, timedelta,datetime
eventos_bp = Blueprint('eventos', __name__, template_folder='TEMPLATES', url_prefix='/Eventos')

@eventos_bp.route('/', methods=['GET'])
@eventos_bp.route('/Eventos', methods=['GET'])
def Eventos():
    tipos_evento = controlador_evento.get_tipos_eventos2()
    tipos_evento1 = controlador_evento.get_tipos_eventos1()
    tipos_evento1_raw = {t[0]: t[2] or 0 for t in tipos_evento1}
    
    metodos_pago = controlador_evento.get_metodos_pago()
    countries=controlador_pais.get_countries()
    tipo_doc=controlador_evento.get_tipo_documento()
    return render_template("Eventos.html",tipos_evento=tipos_evento, metodos_pago=metodos_pago,countries=countries, tipos_evento1= tipos_evento1
                           ,tipo_doc=tipo_doc,current_date= date.today() + timedelta(days=1),tipos_evento1_raw=tipos_evento1_raw)
@eventos_bp.route("/procesar_pago", methods=['GET', 'POST'])
def procesar_pago_route():
    resultado = controlador_evento.procesar_pago()  # ✅ Captura el retorno
    
    # Si fue exitoso, agrega la URL de redirección
    if resultado.get_json().get("success"):
        data = resultado.get_json()
        data["redirect_url"] = url_for("Index")
        return jsonify(data)
    
    # Si falló, retorna el error tal cual
    return resultado

@eventos_bp.route("/reservas_fecha", methods=["GET"])
def reservas_por_fecha():
    fecha = request.args.get("fecha")
    if not fecha:
        return jsonify({"success": False, "message": "Fecha requerida"}), 400

    reservas = controlador_evento.obtener_evento(fecha)

    reservas_lista = []
    for r in reservas:
        # Convertimos TIME (timedelta) a strings "HH:MM"
        hora_inicio = (datetime.min + r[0]).time().strftime("%H:%M")
        hora_fin = (datetime.min + r[1]).time().strftime("%H:%M")
        reservas_lista.append({
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin
        })

    return jsonify({"success": True, "reservas": reservas_lista})

#  Obtener todos los tipos de servicio (Comida, Música, etc.)

@eventos_bp.route('/tipos_servicio', methods=['GET'])
def tipos_servicio_evento():
    try:
        tipos = controlador_servicios_evento.get_tipos_servicio_evento()
        return jsonify({"success": True, "data": tipos})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

# Obtener todos los servicios agrupados por tipo
@eventos_bp.route('/servicios', methods=['GET'])
def servicios_evento():
    try:
        servicios = controlador_servicios_evento.get_todos_servicios_por_tipo_servicio()
        return jsonify({"success": True, "data": servicios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
# Obtener servicios filtrados por tipo (opcional)
# Ejemplo: /servicios/1 para todos los de tipo "Comida"
@eventos_bp.route('/servicios/<int:tipo_id>', methods=['GET'])
def servicios_por_tipo(tipo_id):
    try:
        servicios = controlador_servicios_evento.get_servicios_por_tipo(tipo_id)
        return jsonify({"success": True, "data": servicios})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
