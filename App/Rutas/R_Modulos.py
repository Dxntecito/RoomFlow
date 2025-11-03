from flask import render_template, Blueprint, session, redirect, url_for, flash
from functools import wraps
import App.Controladores.C_Usuarios.controlador_usuario as controller_usuario

modulos_bp = Blueprint('modulos', __name__, url_prefix='/Cruds')

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.Login'))
        return f(*args, **kwargs)
    return decorated_function

@modulos_bp.route('/modulos', methods=['GET'])
@login_required
def modulos():
    """
    Página principal de modulos
    """
    return render_template("Modulos.html")

@modulos_bp.route('/modulos/Empleado', methods=['GET'])
@login_required
def empleado():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    return render_template("/MODULO_EMPLEADO/gestionar_empleados.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/modulos/Incidencia', methods=['GET'])
@login_required
def incidencia():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    return render_template("/MODULO_INCIDENCIA/gestionar_incidencias.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/modulos/Reserva', methods=['GET'])
@login_required
def reserva():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    return render_template("/MODULO_RESERVA/gestionar_reserva.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/modulos/Reserva-promociones', methods=['GET'])
@login_required
def promociones():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    return render_template("/MODULO_RESERVA/gestionar_promociones.html", perfil=perfil, tipos_documento=tipos_documento)


