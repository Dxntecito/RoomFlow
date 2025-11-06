from flask import render_template, Blueprint, session, redirect, url_for, flash, jsonify, make_response
from functools import wraps
import App.Controladores.C_Reportes.controlador_reporte as controller_reporte
import App.Controladores.C_Empleado.controlador_empleado as controller_empleado

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

@reportes_bp.route('/', methods=['GET'])
@reportes_bp.route('/reportes', methods=['GET'])
@admin_required
def reportes():
    """
    Página principal de reportes
    """
    return render_template("Reportes.html")

@reportes_bp.route('/api/estadisticas', methods=['GET'])
@admin_required
def api_estadisticas():
    """
    Obtener todas las estadísticas en formato JSON
    Optimizado para usar una sola conexión
    """
    try:
        estadisticas = controller_reporte.get_todas_estadisticas()
        
        return jsonify({
            'success': True,
            'estadisticas': estadisticas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500

@reportes_bp.route('/api/tablas', methods=['GET'])
@admin_required
def api_tablas():
    """
    Obtener la lista de todas las tablas en la base de datos
    """
    try:
        tablas = controller_reporte.get_lista_tablas()
        
        return jsonify({
            'success': True,
            'tablas': tablas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener lista de tablas: {str(e)}'
        }), 500

@reportes_bp.route('/api/tablas/<nombre_tabla>/atributos', methods=['GET'])
@admin_required
def api_atributos_tabla(nombre_tabla):
    """
    Obtener los atributos (columnas) de una tabla específica
    """
    try:
        from flask import request
        atributos = controller_reporte.get_atributos_tabla(nombre_tabla)
        
        return jsonify({
            'success': True,
            'tabla': nombre_tabla,
            'atributos': atributos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener atributos de la tabla: {str(e)}'
        }), 500

@reportes_bp.route('/api/conexiones', methods=['GET'])
@admin_required
def api_conexiones():
    """
    Obtener el detalle de todas las conexiones activas (SHOW PROCESSLIST)
    """
    try:
        conexiones = controller_reporte.get_detalle_conexiones()
        
        return jsonify({
            'success': True,
            'conexiones': conexiones
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener conexiones: {str(e)}'
        }), 500

@reportes_bp.route('/exportar/pdf', methods=['GET'])
@admin_required
def exportar_pdf():
    """
    Exportar reporte en formato PDF
    """
    try:
        from datetime import datetime
        
        # Obtener estadísticas
        estadisticas = controller_reporte.get_todas_estadisticas()
        
        # Obtener datos de empleados para procesar
        empleados = controller_empleado.get_empleados(limit=1000, offset=0, search_term='', rol_filter='')
        
        # Procesar empleados por rol
        empleados_por_rol = {}
        if empleados:
            for empleado in empleados:
                rol = empleado[10] if len(empleado) > 10 else 'Sin rol'  # nombre_tipo
                empleados_por_rol[rol] = empleados_por_rol.get(rol, 0) + 1
        
        empleados_data = {
            'empleadosPorRol': empleados_por_rol
        }
        
        # Obtener información del usuario
        usuario_id = session.get('usuario_id', 'usuario')
        # Intentar obtener el nombre completo del usuario o su nombre de usuario
        usuario_nombre = session.get('usuario', 'Usuario Desconocido')
        # Si hay nombres y apellidos en la sesión, usarlos
        nombres = session.get('nombres', '')
        ape_paterno = session.get('apellido_paterno', '')
        if nombres and ape_paterno:
            usuario_nombre = f"{nombres} {ape_paterno}"
        
        # Generar PDF
        pdf_content = controller_reporte.generar_reporte_pdf(estadisticas, empleados_data, usuario_nombre)
        
        # Crear nombre de archivo con fecha
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        nombre_archivo = f'Reporte_Roomflow_{fecha_actual}.pdf'
        
        # Crear respuesta
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error al generar PDF: {str(e)}', 'error')
        return redirect(url_for('reportes.reportes'))

@reportes_bp.route('/exportar/excel', methods=['GET'])
@admin_required
def exportar_excel():
    """
    Exportar reporte en formato Excel
    """
    try:
        from datetime import datetime
        
        # Obtener estadísticas
        estadisticas = controller_reporte.get_todas_estadisticas()
        
        # Obtener datos de empleados para procesar
        empleados = controller_empleado.get_empleados(limit=1000, offset=0, search_term='', rol_filter='')
        
        # Procesar empleados por rol
        empleados_por_rol = {}
        if empleados:
            for empleado in empleados:
                rol = empleado[10] if len(empleado) > 10 else 'Sin rol'  # nombre_tipo
                empleados_por_rol[rol] = empleados_por_rol.get(rol, 0) + 1
        
        empleados_data = {
            'empleadosPorRol': empleados_por_rol
        }
        
        # Obtener información del usuario
        usuario_id = session.get('usuario_id', 'usuario')
        usuario_nombre = session.get('usuario', 'Usuario Desconocido')
        nombres = session.get('nombres', '')
        ape_paterno = session.get('apellido_paterno', '')
        if nombres and ape_paterno:
            usuario_nombre = f"{nombres} {ape_paterno}"
        
        # Generar Excel
        excel_content = controller_reporte.generar_reporte_excel(estadisticas, empleados_data, usuario_nombre)
        
        # Crear nombre de archivo con fecha
        fecha_actual = datetime.now().strftime('%d-%m-%Y')
        nombre_archivo = f'Reporte_Roomflow_{fecha_actual}.xlsx'
        
        # Crear respuesta
        response = make_response(excel_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
        
        return response
    except ImportError as e:
        import traceback
        traceback.print_exc()
        flash(f'Error: openpyxl no está instalado. Por favor ejecuta: pip install openpyxl', 'error')
        return redirect(url_for('reportes.reportes'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error al generar Excel: {str(e)}', 'error')
        return redirect(url_for('reportes.reportes'))
