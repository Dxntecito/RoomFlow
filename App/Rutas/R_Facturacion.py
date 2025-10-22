from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, json, flash, send_file, current_app, make_response, current_app
import App.Controladores.C_Evento

facturaciones_bp = Blueprint('facturacion', __name__, template_folder='Templates', url_prefix='/WEB_CLIENTE/Facturacion')

@facturaciones_bp.route('/', methods=['GET'])
@facturaciones_bp.route('/Facturacion', methods=['GET'])
def Facturacion():
    return render_template("Facturacion.html")