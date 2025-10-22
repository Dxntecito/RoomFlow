from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app
import App.Controladores.C_Evento

eventos_bp = Blueprint('eventos', __name__, template_folder='Templates', url_prefix='/ModuleEvents')

@eventos_bp.route('/', methods=['GET'])
@eventos_bp.route('/Eventos', methods=['GET'])
def Eventos():
    return render_template("Eventos.html")