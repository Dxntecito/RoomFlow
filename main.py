from flask import Flask, render_template,request,session,redirect,url_for,g
from bd import get_connection
from flask_socketio import SocketIO

from App.Rutas.R_Reserva import bookingroom_bp
from App.Rutas.R_Empleados import empleados_bp
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



app = Flask(__name__, template_folder="./App/Rutas/TEMPLATES", static_folder="./App/Static")
app.secret_key = 'clave_super_secreta_123'

socketio = SocketIO(app)

app.register_blueprint(bookingroom_bp)
app.register_blueprint(empleados_bp)
app.register_blueprint(eventos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(incidentes_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(roomservice_bp)
app.register_blueprint(crear_comprobante_bp)
app.register_blueprint(transaccion_bp)
app.register_blueprint(promocion_bp)

@app.route("/")
@app.route("/RoomFlow")
def Index():
    return render_template("Index.html")

from flask import request, render_template
from datetime import datetime

# Iniciar el servidor
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

