from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app
from datetime import datetime
import App.Controladores.C_Reserva.controlador_habitacion as controller_room
import App.Controladores.C_Reserva.controlador_categoria as controller_category
import App.Controladores.C_Reserva.controlador_piso as controller_floor
import App.Controladores.C_Reserva.controlador_reserva as controller_reserva
import App.Controladores.C_Reserva.controlador_pais as controller_pais

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
    countries = controller_pais.get_countries()
    print("start:", start)
    print("end:", end)
    print("start_dt:", start_dt)
    print("end_dt:", end_dt)

    return render_template("Booking.html", rooms=rooms, categories=categories, floors=floors ,start_dt =start_dt, end_dt=end_dt , countries=countries)


@bookingroom_bp.route('/guardar_reserva', methods=['POST'])
def ruta_guardar_reserva():
    current_app.logger.info("📩 [DEBUG] Petición recibida en /guardar_reserva")
    try:
        data = request.get_json()
        current_app.logger.info(f"📦 [DEBUG] Datos recibidos del front: {data}")
        reserva_id = controller_reserva.guardar_reserva(data)
        current_app.logger.info(f"✅ [DEBUG] Reserva guardada con ID: {reserva_id}")
        return jsonify({'success': True, 'reserva_id': reserva_id}), 200
    except Exception as e:
        current_app.logger.exception("❌ Error al guardar reserva")
        return jsonify({'success': False, 'error': str(e)}), 500

