from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app

import App.Models.controller_room as controller_room

bookingroom_bp = Blueprint('bookingroom', __name__, template_folder='Templates', url_prefix='/ModuleRoomsBooking')

@bookingroom_bp.route('/', methods=['GET'])
@bookingroom_bp.route('/BookingRoom', methods=['GET'])
def BookingRoom():
    rooms = controller_room.get_rooms()
    return render_template("Booking.html", rooms=rooms)