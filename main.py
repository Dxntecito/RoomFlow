from flask import Flask, render_template,request,session,redirect,url_for,g
from bd import get_connection
from flask_socketio import SocketIO

from App.Rutas.R_Reserva import bookingroom_bp
from App.Rutas.R_Empleados import empleados_bp
from App.Rutas.R_Evento import eventos_bp
from App.Rutas.R_Cliente import cliente_bp
from App.Rutas.R_Reserva_Habitacion import reserva_habitacion_bp
from App.Rutas.R_Huesped  import huesped_bp
# from App.Rutas.RutasFacturacion import facturaciones_bp
# from App.Rutas.RutasIncidente import incidentes_bp
# from App.Rutas.RutasUsuario import usuarios_bp
# from App.Rutas.RutasRoomService import RoomService_bp

app = Flask(__name__, template_folder="./App/Rutas/TEMPLATES", static_folder="./App/Static")
app.secret_key = 'clave_super_secreta_123'

socketio = SocketIO(app)

app.register_blueprint(bookingroom_bp)
app.register_blueprint(empleados_bp)
app.register_blueprint(eventos_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(reserva_habitacion_bp)
app.register_blueprint(huesped_bp)


@app.route("/")
@app.route("/RoomFlow")
def Index():
    return render_template("Index.html")

from flask import request, render_template
from datetime import datetime

# Iniciar el servidor
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

