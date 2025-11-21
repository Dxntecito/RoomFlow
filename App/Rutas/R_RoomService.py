from datetime import datetime
from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_RoomService.controlador_room_service as controlador_room_service
import App.Controladores.C_Evento.controlador_evento as controlador_evento

roomservice_bp = Blueprint('roomservice', __name__, url_prefix='/Roomservice')


@roomservice_bp.route('/buscar_reserva')
def buscar_reserva():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({'error': 'Debes iniciar sesión para continuar.'}), 401

    fecha_ingreso = request.args.get('fecha_ingreso')
    if not fecha_ingreso:
        return jsonify({'error': 'La fecha de ingreso es obligatoria.'}), 400

    try:
        datetime.strptime(fecha_ingreso, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Usa AAAA-MM-DD.'}), 400

    reserva = controlador_room_service.get_reserva_por_fecha_usuario(fecha_ingreso, usuario_id)

    if not reserva:
        return jsonify(None)

    fecha_reserva = reserva.get('fecha_ingreso')
    hora_reserva = reserva.get('hora_ingreso')
    if fecha_reserva and hora_reserva:
        try:
            inicio_reserva = datetime.strptime(f"{fecha_reserva} {hora_reserva}", "%Y-%m-%d %H:%M:%S")
            if inicio_reserva > datetime.now():
                return jsonify({
                    'status': 'pending',
                    'message': 'Aún no inicia tu reserva. Vuelve cuando haya comenzado.'
                })
        except ValueError:
            pass

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
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a RoomService.')
        return redirect(url_for('usuario.login'))

    metodos_pago = controlador_evento.get_metodos_pago()
    amenidades = controlador_room_service.get_amenidades()
    return render_template('Roomservice_Perfil.html', amenidades=amenidades, metodos_pago=metodos_pago)

@roomservice_bp.route('/procesar_pago_roomservice', methods=['POST'])
def procesar_pago():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({"success": False, "error": "Debes iniciar sesión para continuar."}), 401

    data = request.get_json() or {}
    data['usuario_id'] = usuario_id
    return controlador_room_service.procesar_pago_roomservice(data)