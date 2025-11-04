from flask import render_template, Blueprint, session, redirect, url_for, flash,request,jsonify
from functools import wraps
import App.Controladores.C_Usuarios.controlador_usuario as controller_usuario
import App.Controladores.C_Reserva.controlador_piso as controller_piso
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

###########    INCIO MODULO RESERVA    ###########

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


#-------------- INICIO SECCION PISO--------------#

# LISTADO CON FILTRO Y PAGINACION
@modulos_bp.route('/Pisos')
def pisos():
    page = int(request.args.get('page', 1))
    per_page = 7
    offset = (page - 1) * per_page

    pisos = controller_piso.get_pisos(limit=per_page, offset=offset)

    total_pisos = controller_piso.count_pisos()
    total_pages = (total_pisos + per_page - 1) // per_page

    return render_template(
        '/MODULO_RESERVA/gestionar_piso.html',
        pisos=pisos,
        mode="list",
        filter='piso_id',
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/FilterPisos/<string:filter>')
def FilterPisos(filter):
    page = int(request.args.get('page', 1))
    per_page = 7
    order = request.args.get('order', 'asc')

    pisos_all_tuples = controller_piso.order_piso(filter, order)
    pisos_all = [dict(piso_id=p[0], numero=p[1], estado=p[2], precio=p[3]) for p in pisos_all_tuples]

    total_pisos = len(pisos_all)
    total_pages = (total_pisos + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    pisos = pisos_all[start:end]

    return render_template(
        '/MODULO_RESERVA/gestionar_piso.html',
        pisos=pisos,
        mode='list',
        filter=filter,
        order=order,
        page=page,
        total_pages=total_pages
    )


# VER DETALLE
@modulos_bp.route('/ViewPiso/<int:piso_id>')
def ViewPiso(piso_id):
    piso = controller_piso.get_one_piso(piso_id)  # ya es dict
    return render_template('/MODULO_RESERVA/gestionar_piso.html', piso=piso, mode='view')   


# EDITAR
@modulos_bp.route('/EditPiso/<int:piso_id>')
def EditPiso(piso_id):
    piso = controller_piso.get_one_piso(piso_id)  # ya es dict
    return render_template('/MODULO_RESERVA/gestionar_piso.html', piso=piso, mode='edit')


# ACTUALIZAR
@modulos_bp.route('/UpdatePiso', methods=['POST'])
def UpdatePiso():
    try:
        piso_id = request.form['piso_id']
        numero = request.form['numero']
        estado = request.form['estado']
        precio = request.form['precio']

        controller_piso.update_piso(numero, estado, precio, piso_id)
        flash("Piso actualizado correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar el piso: {str(e)}", "error")

    return redirect(url_for('modulos.FilterPisos', filter='piso_id'))


# CREAR NUEVO
@modulos_bp.route('/NewPiso')
def NewPiso():
    return render_template('/MODULO_RESERVA/gestionar_piso.html', piso=None, mode='insert')


# GUARDAR NUEVO
@modulos_bp.route('/SavePiso', methods=['POST'])
def SavePiso():
    try:
        numero = request.form['numero']
        estado = request.form['estado']
        precio = request.form['precio']

        controller_piso.insert_piso(numero, estado, precio)
        flash("Piso creado correctamente", "success")
    except Exception as e:
        flash(f"Error al crear el piso: {str(e)}", "error")

    return redirect(url_for('modulos.FilterPisos', filter='piso_id'))


# ELIMINAR
@modulos_bp.route('/DeletePiso', methods=['POST'])
def DeletePiso():
    piso_id = request.form.get('piso_id')
    try:
        controller_piso.delete_piso(piso_id)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e))



# BUSQUEDA AJAX
@modulos_bp.route('/SearchPisos')
def SearchPisos():
    query = request.args.get('query', '').strip()
    if query:
        resultados = controller_piso.search_piso(query)
    else:
        resultados = controller_piso.get_pisos()

    # Convierte a JSON
    pisos_json = [
        {"piso_id": p[0], "numero": p[1], "estado": p[2], "precio": p[3]}
        for p in resultados
    ]
    return jsonify(pisos_json)


#-------------- FIN SECCION PISO--------------#


###########    FIN MODULO RESERVA    ###########


###########    INCIO MODULO FACTURACION    ###########

###########    FIN MODULO FACTURACION    ###########


###########    INICIO MODULO INCIDENCIA    ###########
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

###########    FIN MODULO INCIDENCIA    ###########



###########    INICIO MODULO EMPLEADO    ###########
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

###########    FIN MODULO EMPLEADO    ###########


###########    INICIO MODULO USUARIO    ###########
@modulos_bp.route('/modulos/Usuario', methods=['GET'])
@login_required
def usuario():
    print("=" * 60)
    print("ACCEDIENDO A MÓDULO DE USUARIO")
    print("=" * 60)
    
    usuario_id = session.get('usuario_id')
    print(f"Usuario ID: {usuario_id}")
    print(f"Rol ID: {session.get('rol_id')}")
    
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if not perfil:
        print("ERROR: Perfil no encontrado")
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    # Solo administradores pueden acceder
    if session.get('rol_id') != 1:
        print("ERROR: Usuario no es administrador")
        flash('No tienes permisos para acceder a este módulo', 'danger')
        return redirect(url_for('modulos.modulos'))
    
    print("Renderizando template: /MODULO_USUARIO/gestionar_usuarios.html")
    print("=" * 60)
    
    try:
        return render_template("/MODULO_USUARIO/gestionar_usuarios.html", perfil=perfil, tipos_documento=tipos_documento)
    except Exception as e:
        print(f"ERROR AL RENDERIZAR TEMPLATE: {e}")
        import traceback
        traceback.print_exc()
        raise

# API para obtener usuarios
@modulos_bp.route('/modulos/usuarios/api', methods=['GET'])
@login_required
def api_usuarios():
    # Solo administradores
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        search_term = request.args.get('search', '')
        rol_filter = request.args.get('rol', '')
        estado_filter = request.args.get('estado', '')
        
        usuarios = controller_usuario.get_usuarios_admin(
            limit=100, 
            offset=0, 
            search_term=search_term,
            rol_filter=rol_filter,
            estado_filter=estado_filter
        )
        
        return jsonify({
            'success': True,
            'usuarios': usuarios
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# Crear usuario
@modulos_bp.route('/modulos/usuarios/crear', methods=['POST'])
@login_required
def crear_usuario():
    # Solo administradores
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        usuario = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        email = request.form.get('email')
        rol = request.form.get('rol')
        estado = request.form.get('estado', '1')
        
        if not all([usuario, contrasena, email, rol]):
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
        
        resultado = controller_usuario.insert_usuario_admin(
            usuario=usuario,
            contrasena=contrasena,
            email=email,
            id_rol=int(rol),
            estado=int(estado)
        )
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Actualizar usuario
@modulos_bp.route('/modulos/usuarios/actualizar/<int:usuario_id>', methods=['POST'])
@login_required
def actualizar_usuario(usuario_id):
    # Solo administradores
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        usuario = request.form.get('usuario')
        email = request.form.get('email')
        rol = request.form.get('rol')
        estado = request.form.get('estado')
        
        if not all([usuario, email, rol, estado]):
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
        
        resultado = controller_usuario.update_usuario_admin(
            usuario_id=usuario_id,
            usuario=usuario,
            email=email,
            id_rol=int(rol),
            estado=int(estado)
        )
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Resetear contraseña
@modulos_bp.route('/modulos/usuarios/resetear/<int:usuario_id>', methods=['POST'])
@login_required
def resetear_contrasena_usuario(usuario_id):
    # Solo administradores
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    try:
        nueva_contrasena = request.form.get('nueva_contrasena')
        
        if not nueva_contrasena:
            return jsonify({'success': False, 'message': 'La contraseña es obligatoria'})
        
        if len(nueva_contrasena) < 6:
            return jsonify({'success': False, 'message': 'La contraseña debe tener al menos 6 caracteres'})
        
        resultado = controller_usuario.resetear_contrasena_admin(
            usuario_id=usuario_id,
            nueva_contrasena=nueva_contrasena
        )
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Eliminar usuario
@modulos_bp.route('/modulos/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    # Solo administradores
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    # No permitir auto-eliminación
    if usuario_id == session.get('usuario_id'):
        return jsonify({'success': False, 'message': 'No puedes eliminar tu propia cuenta desde aquí'})
    
    try:
        resultado = controller_usuario.eliminar_usuario_admin(usuario_id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

###########    FIN MODULO USUARIO    ###########