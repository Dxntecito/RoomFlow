from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_RoomService.controlador_room_service as controlador_room_service
import App.Controladores.C_Evento.controlador_evento as controlador_evento
import App.Controladores.C_Reserva.controlador_pais as controlador_pais

roomservice_bp = Blueprint('roomservice', __name__, url_prefix='/Roomservice')


@roomservice_bp.route('/buscar_reserva/<string:numero_comprobante>')
def buscar_reserva(numero_comprobante):
    reserva = controlador_room_service.get_reserva_por_comprobante(numero_comprobante)

    # Si no hay datos
    if not reserva:
        return jsonify(None)

    # Armar el JSON final directamente
    resultado = {
        'fecha_ingreso': reserva.get('fecha_ingreso', ''),
        'fecha_salida': reserva.get('fecha_salida', ''),
        'hora_ingreso': reserva.get('hora_ingreso', ''),
        'hora_salida': reserva.get('hora_salida', ''),
        'habitaciones': reserva.get('habitaciones', [])
    }

    return jsonify(resultado)


@roomservice_bp.route('/roomservice_perfil')
def roomservice_perfil():
    metodos_pago = controlador_evento.get_metodos_pago()
    countries=controlador_pais.get_countries()
    tipo_doc=controlador_evento.get_tipo_documento()
    amenidades = controlador_room_service.get_amenidades()
    return render_template('Roomservice_Perfil.html',amenidades=amenidades, metodos_pago=metodos_pago,countries=countries
                           ,tipo_doc=tipo_doc)

@roomservice_bp.route('/procesar_pago_roomservice', methods=['POST'])
def procesar_pago():
    data = request.get_json()
    return controlador_room_service.procesar_pago_roomservice(data)