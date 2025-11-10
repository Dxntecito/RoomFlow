from flask import Flask, render_template,request,session,redirect,url_for,g
from bd import get_connection
from flask_socketio import SocketIO
from flask_mail import Mail
import os

from App.Rutas.R_Reserva import bookingroom_bp
from App.Rutas.R_Empleados import empleados_bp
from App.Rutas.R_Turno import turno_bp
from App.Rutas.R_Evento import eventos_bp
from App.Rutas.R_Cliente import cliente_bp
from App.Rutas.R_Reserva_Habitacion import reserva_habitacion_bp
from App.Rutas.R_Huesped  import huesped_bp
from App.Rutas.R_Usuario import usuarios_bp
from App.Rutas.R_Incidente import incidentes_bp
from App.Rutas.R_Reporte import reportes_bp
# from App.Rutas.RutasFacturacion import facturaciones_bp
from App.Rutas.R_RoomService import roomservice_bp
from App.Rutas.crear_comprobante import crear_comprobante_bp
from App.Rutas.R_transaccion import transaccion_bp
from App.Rutas.R_Promocion import promocion_bp
from App.Rutas.R_Modulos import modulos_bp
from App.Rutas.R_Facturacion import facturaciones_bp


app = Flask(__name__, template_folder="./App/Rutas/TEMPLATES", static_folder="./App/Static")
app.secret_key = 'clave_super_secreta_123'

# === Config de correo (Gmail SMTP) ===
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'valentinoandca@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'gcdl wgwf lego lmin')
app.config['MAIL_DEFAULT_SENDER'] = ('Hotel RoomFlow', 'valentinoandca@gmail.com')

mail = Mail(app)

socketio = SocketIO(app)

app.register_blueprint(bookingroom_bp)
app.register_blueprint(empleados_bp)
app.register_blueprint(turno_bp)
app.register_blueprint(eventos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(incidentes_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(roomservice_bp)
app.register_blueprint(crear_comprobante_bp)
app.register_blueprint(transaccion_bp)
app.register_blueprint(promocion_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(modulos_bp)
app.register_blueprint(facturaciones_bp)

@app.route("/")
@app.route("/RoomFlow")
def Index():
    return render_template("Index.html")

from flask import request, render_template
from datetime import datetime

# Hacer mail accesible para otros módulos
from App.Rutas import R_Usuario
R_Usuario.mail = mail

# Iniciar el servidor
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

