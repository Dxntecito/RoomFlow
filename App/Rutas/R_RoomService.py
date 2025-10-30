from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for, flash
import App.Controladores.C_Usuarios.controlador_usuario as controller_usuario


roomservice_bp = Blueprint('roomservice', __name__, url_prefix='/Roomservice')

@roomservice_bp.route('/roomservice_perfil')
def roomservice_perfil():
    return render_template('Roomservice_Perfil.html')