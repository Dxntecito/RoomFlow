from flask import Flask, render_template,request,session,redirect,url_for,g
from bd import get_connection
from flask_socketio import SocketIO

from App.Blueprints.ModuleRoomsBooking.RoutesBooking import bookingroom_bp
from App.Blueprints.ModuleEmployees.RoutesEmpleados import empleados_bp
from App.Blueprints.ModuleEvents.RouteEvents import eventos_bp

app = Flask(__name__, template_folder="./App/Templates", static_folder="./App/Static")
app.secret_key = 'clave_super_secreta_123'

socketio = SocketIO(app)

app.register_blueprint(bookingroom_bp)
app.register_blueprint(empleados_bp)
app.register_blueprint(eventos_bp)
@app.route("/")
@app.route("/RoomFlow")
def Index():
    return render_template("Index.html")


# Iniciar el servidor
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)

