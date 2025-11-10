from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app
from datetime import datetime
import App.Controladores.C_Reserva.controlador_habitacion as controller_room
import App.Controladores.C_Reserva.controlador_categoria as controller_category
import App.Controladores.C_Reserva.controlador_piso as controller_floor
import App.Controladores.C_Reserva.controlador_reserva as controller_reserva
import App.Controladores.C_Reserva.controlador_pais as controller_pais
import App.Controladores.C_Cliente.controlador_tipo_doc as controller_type_doc
import App.Controladores.C_Cliente.controlador_tipo_emp as controller_type_emp
import App.Controladores.C_Reserva.controlador_servicio as controller_service
bookingroom_bp = Blueprint('bookingroom',__name__,template_folder='TEMPLATES',url_prefix='/Rutas/TEMPLATES')

@bookingroom_bp.route('/', methods=['GET'])
@bookingroom_bp.route('/ReservaHabitacion/', methods=['GET'])
def BookingRoom():
    start = request.args.get('start')
    end = request.args.get('end')

    print("start raw:", start)
    print("end raw:", end)

    # Convertimos a datetime si vienen las fechas
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None

    print("start_dt:", start_dt)
    print("end_dt:", end_dt)

    # Pasamos las fechas al controlador
    rooms = controller_room.get_available_rooms(start_dt, end_dt)
    
    categories = controller_category.get_categories()
    floors = controller_floor.get_floors()
    categories_map = {category["id"]: category for category in categories}
    floors_map = {floor[0]: floor[1] for floor in floors}
    services = controller_service.get_services()
    countries = controller_pais.get_countries()
    types_doc = controller_type_doc.get_types_doc()
    types_emp = controller_type_emp.get_types_emp()
    print("start:", start)
    print("end:", end)
    print("start_dt:", start_dt)
    print("end_dt:", end_dt)

    return render_template(
        "Booking.html",
        rooms=rooms,
        categories=categories,
        categories_map=categories_map,
        floors=floors,
        floors_map=floors_map,
        services=services,
        start_dt=start_dt,
        end_dt=end_dt,
        countries=countries,
        types_doc=types_doc,
        types_emp=types_emp
    )


@bookingroom_bp.route('/reserva/<int:reserva_id>/estado', methods=['GET'])
def obtener_estado_reserva(reserva_id):
    estado = controller_reserva.obtener_estado_validado(reserva_id)
    if estado is None:
        return jsonify({"success": False, "message": "Reserva no encontrada"}), 404
    return jsonify({"success": True, "validado": estado})


@bookingroom_bp.route('/reserva/<int:reserva_id>', methods=['DELETE'])
def eliminar_reserva(reserva_id):
    ok = controller_reserva.eliminar_reserva_completa(reserva_id)
    if ok:
        return jsonify({"success": True})
    return jsonify({"success": False}), 400


@bookingroom_bp.route('/guardar_reserva', methods=['POST'])
def ruta_guardar_reserva():
    try:
        data = request.get_json()
        bandera = data.get("bandera",None)
        if bandera == "TRUE":
            reserva_id = controller_reserva.guardar_reserva_c_usuario(data)
        elif bandera == "FALSE":
            reserva_id = controller_reserva.guardar_reserva_s_usuario(data)
        else:
            return jsonify({'success': False, 'error': f'Bandera desconocida: {bandera}'}), 400
        if reserva_id:
            return jsonify({'success': True, 'reserva_id': reserva_id}), 200
        else:
            return jsonify({'success': False, 'error': 'No se pudo guardar la reserva'}), 400
    except Exception as e:
        current_app.logger.exception("❌ Error al guardar reserva")
        return jsonify({'success': False, 'error': str(e)}), 500


