from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app

import App.Controladores.C_Reserva.controlador_habitacion as controller_room
import App.Controladores.C_Reserva.controlador_categoria as controller_category
import App.Controladores.C_Reserva.controlador_piso as controller_floor

bookingroom_bp = Blueprint('bookingroom',__name__,template_folder='TEMPLATES',url_prefix='/Rutas/TEMPLATES')

@bookingroom_bp.route('/', methods=['GET'])
@bookingroom_bp.route('/ReservaHabitacion/', methods=['GET'])
def BookingRoom():
    rooms = controller_room.get_available_rooms()
    categories = controller_category.get_categories()
    floors = controller_floor.get_floors()
    return render_template("Booking.html", rooms=rooms , categories=categories,floors=floors )
