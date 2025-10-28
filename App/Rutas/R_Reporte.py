from flask import render_template, Blueprint, session, redirect, url_for, flash
from functools import wraps

reportes_bp = Blueprint('reportes', __name__, url_prefix='/Cruds/Reportes')

def login_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.Login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para proteger rutas que requieren rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('usuarios.Login'))
        if session.get('rol_id') != 1:  # Asumiendo que rol_id=1 es administrador
            flash('No tienes permisos para acceder a esta página. Solo administradores pueden ver reportes.', 'danger')
            return redirect(url_for('Index'))
        return f(*args, **kwargs)
    return decorated_function

@reportes_bp.route('/reportes', methods=['GET'])
@admin_required
def reportes():
    """
    Página principal de reportes
    """
    return render_template("Reportes.html")
