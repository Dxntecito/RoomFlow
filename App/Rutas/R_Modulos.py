from flask import render_template, Blueprint, session, redirect, url_for, flash, request, jsonify
from functools import wraps
from decimal import Decimal
from datetime import date, timedelta

import App.Controladores.C_Usuarios.controlador_usuario as controller_usuario
import App.Controladores.C_Evento.controlador_evento as controlador_evento
import App.Controladores.C_Reserva.controlador_reserva as controller_reserva
import App.Controladores.C_Reserva.controlador_categoria as controller_categoria
import App.Controladores.C_Reserva.controlador_piso as controller_piso
import App.Controladores.C_Reserva.controlador_habitacion as controller_habitacion
import App.Controladores.C_Reserva.controlador_servicio as controller_service



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

    page = int(request.args.get('page', 1))
    per_page = 7
    offset = (page - 1) * per_page

    reservas = controller_reserva.get_reservas(limit=per_page, offset=offset)
    total_reservas = controller_reserva.count_reservas()
    total_pages = (total_reservas + per_page - 1) // per_page
    servicios = controller_service.get_services(limit=100)

    return render_template(
        "/MODULO_RESERVA/gestionar_reserva.html",
        perfil=perfil,
        tipos_documento=tipos_documento,
        reservas=reservas,
        servicios=servicios,
        mode="list",
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/modulos/Reserva-dashboard', methods=['GET'])
@login_required
def reserva_dashboard():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()

    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))

    resumen = {
        "categorias": controller_categoria.count_categories(),
        "habitaciones": controller_habitacion.count_rooms(),
        "reservas": controller_reserva.count_reservas(),
        "pisos": controller_piso.count_pisos()
    }

    return render_template(
        "/MODULO_RESERVA/resumen_reserva.html",
        perfil=perfil,
        tipos_documento=tipos_documento,
        resumen=resumen
    )


@modulos_bp.route('/Categorias', methods=['GET'])
@login_required
def categorias():
    page = int(request.args.get('page', 1))
    per_page = 7
    offset = (page - 1) * per_page

    categorias = controller_categoria.get_categories(limit=per_page, offset=offset)
    total_categorias = controller_categoria.count_categories()
    total_pages = (total_categorias + per_page - 1) // per_page

    return render_template(
        '/MODULO_RESERVA/gestionar_categoria.html',
        categorias=categorias,
        mode='list',
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/FilterCategorias/<string:field>')
@login_required
def filter_categorias(field):
    page = int(request.args.get('page', 1))
    per_page = 7
    order = request.args.get('order', 'asc')

    categorias_all = controller_categoria.order_categories(field, order)
    total_categorias = len(categorias_all)
    total_pages = (total_categorias + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    categorias = categorias_all[start:end]

    return render_template(
        '/MODULO_RESERVA/gestionar_categoria.html',
        categorias=categorias,
        mode='list',
        filter=field,
        order=order,
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/NewCategoria')
@login_required
def new_categoria():
    return render_template('/MODULO_RESERVA/gestionar_categoria.html', categoria=None, mode='insert')


@modulos_bp.route('/SaveCategoria', methods=['POST'])
@login_required
def save_categoria():
    nombre = request.form.get('nombre_categoria')
    precio = request.form.get('precio_categoria', type=float)
    estado = request.form.get('estado', type=int)
    capacidad = request.form.get('capacidad', type=int)
    descripcion = request.form.get('descripcion')

    try:
        controller_categoria.insert_category(nombre, precio, estado, capacidad, descripcion)
        flash("Categoría creada correctamente", "success")
    except Exception as e:
        flash(f"Error al crear la categoría: {str(e)}", "error")

    return redirect(url_for('modulos.categorias'))


@modulos_bp.route('/ViewCategoria/<int:categoria_id>')
@login_required
def view_categoria(categoria_id):
    categoria = controller_categoria.get_category(categoria_id)
    if not categoria:
        flash("Categoría no encontrada", "error")
        return redirect(url_for('modulos.categorias'))
    return render_template('/MODULO_RESERVA/gestionar_categoria.html', categoria=categoria, mode='view')


@modulos_bp.route('/EditCategoria/<int:categoria_id>')
@login_required
def edit_categoria(categoria_id):
    categoria = controller_categoria.get_category(categoria_id)
    if not categoria:
        flash("Categoría no encontrada", "error")
        return redirect(url_for('modulos.categorias'))
    return render_template('/MODULO_RESERVA/gestionar_categoria.html', categoria=categoria, mode='edit')


@modulos_bp.route('/UpdateCategoria', methods=['POST'])
@login_required
def update_categoria():
    categoria_id = request.form.get('categoria_id', type=int)
    nombre = request.form.get('nombre_categoria')
    precio = request.form.get('precio_categoria', type=float)
    estado = request.form.get('estado', type=int)
    capacidad = request.form.get('capacidad', type=int)
    descripcion = request.form.get('descripcion')

    try:
        controller_categoria.update_category(categoria_id, nombre, precio, estado, capacidad, descripcion)
        flash("Categoría actualizada correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar la categoría: {str(e)}", "error")

    return redirect(url_for('modulos.categorias'))


@modulos_bp.route('/DeleteCategoria', methods=['POST'])
@login_required
def delete_categoria():
    categoria_id = request.form.get('categoria_id', type=int)
    try:
        controller_categoria.delete_category(categoria_id)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e))


@modulos_bp.route('/SearchCategorias')
@login_required
def search_categorias():
    query = request.args.get('query', '').strip()
    if not query:
        categorias = controller_categoria.get_categories(limit=50, offset=0)
    else:
        categorias = controller_categoria.search_categories(query)

    return jsonify(categorias)


@modulos_bp.route('/Habitaciones', methods=['GET'])
@login_required
def habitaciones():
    page = int(request.args.get('page', 1))
    per_page = 7
    offset = (page - 1) * per_page

    rooms = controller_habitacion.get_rooms(limit=per_page, offset=offset)
    total_rooms = controller_habitacion.count_rooms()
    total_pages = (total_rooms + per_page - 1) // per_page

    return render_template(
        '/MODULO_RESERVA/gestionar_habitacion.html',
        habitaciones=rooms,
        mode='list',
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/FilterHabitaciones/<string:field>')
@login_required
def filter_habitaciones(field):
    page = int(request.args.get('page', 1))
    per_page = 7
    order = request.args.get('order', 'asc')

    rooms_all = controller_habitacion.order_rooms(field, order)
    total_rooms = len(rooms_all)
    total_pages = (total_rooms + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    rooms = rooms_all[start:end]

    return render_template(
        '/MODULO_RESERVA/gestionar_habitacion.html',
        habitaciones=rooms,
        mode='list',
        filter=field,
        order=order,
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/NewHabitacion')
@login_required
def new_habitacion():
    categorias = controller_categoria.get_categories(limit=100, offset=0)
    pisos = controller_piso.get_pisos(limit=100, offset=0)
    return render_template(
        '/MODULO_RESERVA/gestionar_habitacion.html',
        habitacion=None,
        categorias=categorias,
        pisos=pisos,
        mode='insert'
    )


@modulos_bp.route('/SaveHabitacion', methods=['POST'])
@login_required
def save_habitacion():
    numero = request.form.get('numero')
    estado = request.form.get('estado', type=int)
    categoria_id = request.form.get('categoria_id', type=int)
    piso_id = request.form.get('piso_id', type=int)

    try:
        controller_habitacion.insert_room(numero, estado, categoria_id, piso_id)
        flash("Habitación creada correctamente", "success")
    except Exception as e:
        flash(f"Error al crear la habitación: {str(e)}", "error")

    return redirect(url_for('modulos.habitaciones'))


@modulos_bp.route('/ViewHabitacion/<int:habitacion_id>')
@login_required
def view_habitacion(habitacion_id):
    habitacion = controller_habitacion.get_room(habitacion_id)
    if not habitacion:
        flash("Habitación no encontrada", "error")
        return redirect(url_for('modulos.habitaciones'))
    return render_template('/MODULO_RESERVA/gestionar_habitacion.html', habitacion=habitacion, mode='view')


@modulos_bp.route('/EditHabitacion/<int:habitacion_id>')
@login_required
def edit_habitacion(habitacion_id):
    habitacion = controller_habitacion.get_room(habitacion_id)
    if not habitacion:
        flash("Habitación no encontrada", "error")
        return redirect(url_for('modulos.habitaciones'))
    categorias = controller_categoria.get_categories(limit=100, offset=0)
    pisos = controller_piso.get_pisos(limit=100, offset=0)
    return render_template(
        '/MODULO_RESERVA/gestionar_habitacion.html',
        habitacion=habitacion,
        categorias=categorias,
        pisos=pisos,
        mode='edit'
    )


@modulos_bp.route('/UpdateHabitacion', methods=['POST'])
@login_required
def update_habitacion():
    habitacion_id = request.form.get('habitacion_id', type=int)
    numero = request.form.get('numero')
    estado = request.form.get('estado', type=int)
    categoria_id = request.form.get('categoria_id', type=int)
    piso_id = request.form.get('piso_id', type=int)

    try:
        controller_habitacion.update_room(habitacion_id, numero, estado, categoria_id, piso_id)
        flash("Habitación actualizada correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar la habitación: {str(e)}", "error")

    return redirect(url_for('modulos.habitaciones'))


@modulos_bp.route('/DeleteHabitacion', methods=['POST'])
@login_required
def delete_habitacion():
    habitacion_id = request.form.get('habitacion_id', type=int)
    try:
        controller_habitacion.delete_room(habitacion_id)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e))


@modulos_bp.route('/SearchHabitaciones')
@login_required
def search_habitaciones():
    query = request.args.get('query', '').strip()
    if not query:
        rooms = controller_habitacion.get_rooms(limit=50, offset=0)
    else:
        rooms = controller_habitacion.search_rooms(query)
    return jsonify(rooms)


@modulos_bp.route('/FilterReservas/<string:field>')
@login_required
def filter_reservas(field):
    page = int(request.args.get('page', 1))
    per_page = 7
    order = request.args.get('order', 'desc')

    reservas_all = controller_reserva.order_reservas(field, order)
    total_reservas = len(reservas_all)
    total_pages = (total_reservas + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    reservas = reservas_all[start:end]

    servicios = controller_service.get_services(limit=100)

    return render_template(
        "/MODULO_RESERVA/gestionar_reserva.html",
        reservas=reservas,
        servicios=servicios,
        mode="list",
        filter=field,
        order=order,
        page=page,
        total_pages=total_pages
    )


@modulos_bp.route('/SearchReservas')
@login_required
def search_reservas():
    query = request.args.get('query', '').strip()
    if not query:
        reservas = controller_reserva.get_reservas(limit=50, offset=0)
    else:
        reservas = controller_reserva.search_reservas(query)
    return jsonify(reservas)


@modulos_bp.route('/ViewReserva/<int:reserva_id>')
@login_required
def view_reserva(reserva_id):
    reserva = controller_reserva.get_reserva_detalle(reserva_id)
    if not reserva:
        flash("Reserva no encontrada", "error")
        return redirect(url_for('modulos.reserva'))

    servicios = controller_service.get_services(limit=100)

    return render_template(
        "/MODULO_RESERVA/gestionar_reserva.html",
        reserva=reserva,
        servicios=servicios,
        mode='view'
    )


@modulos_bp.route('/EditReserva/<int:reserva_id>')
@login_required
def edit_reserva(reserva_id):
    reserva = controller_reserva.get_reserva_detalle(reserva_id)
    if not reserva:
        flash("Reserva no encontrada", "error")
        return redirect(url_for('modulos.reserva'))

    servicios = controller_service.get_services(limit=100)
    servicios_asignados = {serv['servicio_id'] for serv in reserva.get('servicios', [])}
    servicios_disponibles = [serv for serv in servicios if serv['id'] not in servicios_asignados]

    return render_template(
        "/MODULO_RESERVA/gestionar_reserva.html",
        reserva=reserva,
        servicios=servicios,
        servicios_disponibles=servicios_disponibles,
        mode='edit'
    )


@modulos_bp.route('/UpdateReserva', methods=['POST'])
@login_required
def update_reserva():
    reserva_id = request.form.get('reserva_id', type=int)
    fecha_ingreso = request.form.get('fecha_ingreso')
    hora_ingreso = request.form.get('hora_ingreso')
    fecha_salida = request.form.get('fecha_salida')
    hora_salida = request.form.get('hora_salida')
    estado = request.form.get('estado', type=int)
    monto_total = request.form.get('monto_total', type=float)
    motivo = request.form.get('motivo')

    servicios_ids = request.form.getlist('servicio_id[]')
    servicios_cantidades = request.form.getlist('servicio_cantidad[]')
    servicios_precios = request.form.getlist('servicio_precio[]')

    servicios = []
    for idx, servicio_id in enumerate(servicios_ids):
        if not servicio_id:
            continue
        cantidad = 1
        precio = 0.0
        if idx < len(servicios_cantidades):
            try:
                cantidad = int(servicios_cantidades[idx])
            except (ValueError, TypeError):
                cantidad = 1
        if idx < len(servicios_precios):
            try:
                precio = float(servicios_precios[idx])
            except (ValueError, TypeError):
                precio = 0.0
        servicios.append({
            "servicio_id": int(servicio_id),
            "cantidad": cantidad,
            "precio_unitario": precio
        })

    try:
        controller_reserva.update_reserva(
            reserva_id,
            fecha_ingreso,
            hora_ingreso,
            fecha_salida,
            hora_salida,
            estado,
            monto_total,
            motivo,
            servicios
        )
        flash("Reserva actualizada correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar la reserva: {str(e)}", "error")

    return redirect(url_for('modulos.reserva'))


@modulos_bp.route('/DeleteReserva', methods=['POST'])
@login_required
def delete_reserva_modulo():
    reserva_id = request.form.get('reserva_id', type=int)
    try:
        controller_reserva.eliminar_reserva_completa(reserva_id)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e))

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

@modulos_bp.route('/modulos/Facturacion', methods=['GET'])
@login_required
def facturacion():
    return redirect(url_for('facturacion.Facturacion'))

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

# ==========================================
# RUTAS PARA GESTIÓN DE CATÁLOGOS
# ==========================================

from App.Controladores.C_Usuarios import controlador_catalogos

# ===== PAÍSES =====
@modulos_bp.route('/modulos/gestionar-paises', methods=['GET'])
@login_required
def gestionar_paises():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if session.get('rol_id') != 1:
        flash('No tienes permisos para acceder a este módulo', 'danger')
        return redirect(url_for('modulos.modulos'))
    
    return render_template("/MODULO_USUARIO/gestionar_paises.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/api/paises', methods=['GET'])
@login_required
def api_get_paises():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.get_paises())

@modulos_bp.route('/api/paises', methods=['POST'])
@login_required
def api_create_pais():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.insert_pais(data['nombre'], data['estado']))

@modulos_bp.route('/api/paises/<int:pais_id>', methods=['PUT'])
@login_required
def api_update_pais(pais_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.update_pais(pais_id, data['nombre'], data['estado']))

@modulos_bp.route('/api/paises/<int:pais_id>', methods=['DELETE'])
@login_required
def api_delete_pais(pais_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.delete_pais(pais_id))

# ===== ROLES =====
@modulos_bp.route('/modulos/gestionar-roles', methods=['GET'])
@login_required
def gestionar_roles():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if session.get('rol_id') != 1:
        flash('No tienes permisos para acceder a este módulo', 'danger')
        return redirect(url_for('modulos.modulos'))
    
    return render_template("/MODULO_USUARIO/gestionar_roles.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/api/roles', methods=['GET'])
@login_required
def api_get_roles():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.get_roles())

@modulos_bp.route('/api/roles', methods=['POST'])
@login_required
def api_create_rol():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.insert_rol(data['nombre_rol'], data['descripcion'], data['estado']))

@modulos_bp.route('/api/roles/<int:rol_id>', methods=['PUT'])
@login_required
def api_update_rol(rol_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.update_rol(rol_id, data['nombre_rol'], data['descripcion'], data['estado']))

@modulos_bp.route('/api/roles/<int:rol_id>', methods=['DELETE'])
@login_required
def api_delete_rol(rol_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.delete_rol(rol_id))

# ===== TIPOS DE DOCUMENTO =====
@modulos_bp.route('/modulos/gestionar-tipo-documento', methods=['GET'])
@login_required
def gestionar_tipo_documento():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if session.get('rol_id') != 1:
        flash('No tienes permisos para acceder a este módulo', 'danger')
        return redirect(url_for('modulos.modulos'))
    
    return render_template("/MODULO_USUARIO/gestionar_tipo_documento.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/api/tipos-documento', methods=['GET'])
@login_required
def api_get_tipos_documento():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.get_tipos_documento())

@modulos_bp.route('/api/tipos-documento', methods=['POST'])
@login_required
def api_create_tipo_documento():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.insert_tipo_documento(data['nombre_tipo_doc'], data['estado']))

@modulos_bp.route('/api/tipos-documento/<int:tipo_doc_id>', methods=['PUT'])
@login_required
def api_update_tipo_documento(tipo_doc_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.update_tipo_documento(tipo_doc_id, data['nombre_tipo_doc'], data['estado']))

@modulos_bp.route('/api/tipos-documento/<int:tipo_doc_id>', methods=['DELETE'])
@login_required
def api_delete_tipo_documento(tipo_doc_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.delete_tipo_documento(tipo_doc_id))

# ===== TIPOS DE CLIENTE =====
@modulos_bp.route('/modulos/gestionar-tipo-cliente', methods=['GET'])
@login_required
def gestionar_tipo_cliente():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if session.get('rol_id') != 1:
        flash('No tienes permisos para acceder a este módulo', 'danger')
        return redirect(url_for('modulos.modulos'))
    
    return render_template("/MODULO_USUARIO/gestionar_tipo_cliente.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/api/tipos-cliente', methods=['GET'])
@login_required
def api_get_tipos_cliente():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.get_tipos_cliente())

@modulos_bp.route('/api/tipos-cliente', methods=['POST'])
@login_required
def api_create_tipo_cliente():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.insert_tipo_cliente(data['tipo_cliente_id'], data['descripcion'], data['estado']))

@modulos_bp.route('/api/tipos-cliente/<string:tipo_cliente_id>', methods=['PUT'])
@login_required
def api_update_tipo_cliente(tipo_cliente_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.update_tipo_cliente(tipo_cliente_id, data['tipo_cliente_id'], data['descripcion'], data['estado']))

@modulos_bp.route('/api/tipos-cliente/<string:tipo_cliente_id>', methods=['DELETE'])
@login_required
def api_delete_tipo_cliente(tipo_cliente_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.delete_tipo_cliente(tipo_cliente_id))

# ===== TIPOS DE EMPRESA =====
@modulos_bp.route('/modulos/gestionar-tipo-empresa', methods=['GET'])
@login_required
def gestionar_tipo_empresa():
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()
    
    if session.get('rol_id') != 1:
        flash('No tienes permisos para acceder a este módulo', 'danger')
        return redirect(url_for('modulos.modulos'))
    
    return render_template("/MODULO_USUARIO/gestionar_tipo_empresa.html", perfil=perfil, tipos_documento=tipos_documento)

@modulos_bp.route('/api/tipos-empresa', methods=['GET'])
@login_required
def api_get_tipos_empresa():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.get_tipos_empresa())

@modulos_bp.route('/api/tipos-empresa', methods=['POST'])
@login_required
def api_create_tipo_empresa():
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.insert_tipo_empresa(data['nombre_tipo'], data['estado']))

@modulos_bp.route('/api/tipos-empresa/<int:tipo_id>', methods=['PUT'])
@login_required
def api_update_tipo_empresa(tipo_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    data = request.get_json()
    return jsonify(controlador_catalogos.update_tipo_empresa(tipo_id, data['nombre_tipo'], data['estado']))

@modulos_bp.route('/api/tipos-empresa/<int:tipo_id>', methods=['DELETE'])
@login_required
def api_delete_tipo_empresa(tipo_id):
    if session.get('rol_id') != 1:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    return jsonify(controlador_catalogos.delete_tipo_empresa(tipo_id))

###########    FIN MODULO USUARIO    ###########


###########    INCIO MODULO EVENTO    ###########
@modulos_bp.route('/modulos/Evento', methods=['GET'])
@login_required
def evento():
    controlador_evento.inactivar_eventos_vencidos()
    usuario_id = session.get('usuario_id')
    perfil = controller_usuario.get_perfil_completo(usuario_id)
    tipos_documento = controller_usuario.get_tipos_documento()

    page = int(request.args.get('page', 1))
    per_page = 7
    offset = (page - 1) * per_page

    eventos = controlador_evento.get_eventos(limit=per_page, offset=offset)
    total_eventos = controlador_evento.count_eventos()
    total_pages = (total_eventos + per_page - 1) // per_page
    controlador_evento.marcar_eventos_con_nota_credito_por_id(eventos)
    
    if not perfil:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('Index'))
    
    return render_template("/MODULO_EVENTO/gestionar_evento.html", perfil=perfil, tipos_documento=tipos_documento,eventos=eventos,
        mode="list",
        filter='id_evento',
        page=page,
        total_pages=total_pages)

# LISTADO CON FILTRO Y PAGINACIÓN
@modulos_bp.route('/TiposEventos')
def tipos_eventos():
    page = int(request.args.get('page', 1))
    per_page = 7
    offset = (page - 1) * per_page

    tipos = controlador_evento.get_tipos_eventos(limit=per_page, offset=offset)
    total_tipos = controlador_evento.count_tipos_eventos()
    total_pages = (total_tipos + per_page - 1) // per_page

    return render_template(
        '/MODULO_EVENTO/gestionar_tipo_evento.html',
        tipos=tipos,
        mode="list",
        filter='tipo_evento_id',
        page=page,
        total_pages=total_pages
    )


# ORDENAR / FILTRAR
@modulos_bp.route('/FilterTiposEventos/<string:filter>')
def FilterTiposEventos(filter):
    page = int(request.args.get('page', 1))
    per_page = 7
    order = request.args.get('order', 'asc')

    tipos_all_tuples = controlador_evento.order_tipo_evento(filter, order)
    tipos_all = [
        dict(tipo_evento_id=t[0], nombre_tipo_evento=t[1], estado=t[2])
        for t in tipos_all_tuples
    ]

    total_tipos = len(tipos_all)
    total_pages = (total_tipos + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    tipos = tipos_all[start:end]

    return render_template(
        '/MODULO_EVENTO/gestionar_tipo_evento.html',
        tipos=tipos,
        mode='list',
        filter=filter,
        order=order,
        page=page,
        total_pages=total_pages
    )


# VER DETALLE
@modulos_bp.route('/ViewTipoEvento/<int:tipo_evento_id>')
def ViewTipoEvento(tipo_evento_id):
    tipo = controlador_evento.get_one_tipo_evento(tipo_evento_id)
    return render_template('/MODULO_EVENTO/gestionar_tipo_evento.html', tipo_evento=tipo, mode='view')


# EDITAR
@modulos_bp.route('/EditTipoEvento/<int:tipo_evento_id>')
def EditTipoEvento(tipo_evento_id):
    tipo = controlador_evento.get_one_tipo_evento(tipo_evento_id)
    return render_template('/MODULO_EVENTO/gestionar_tipo_evento.html', tipo_evento=tipo, mode='edit')


# ACTUALIZAR
@modulos_bp.route('/UpdateTipoEvento', methods=['POST'])
def UpdateTipoEvento():
    try:
        tipo_evento_id = request.form['tipo_evento_id']
        nombre_tipo_evento = request.form['nombre_tipo_evento']
        estado = request.form['estado']
        precio_por_hora = request.form['precio_por_hora']

        controlador_evento.update_tipo_evento(nombre_tipo_evento, estado,precio_por_hora, tipo_evento_id)
        flash("Tipo de evento actualizado correctamente", "success")
    except Exception as e:
        flash(f"Error al actualizar el tipo de evento: {str(e)}", "error")

    return redirect(url_for('modulos.FilterTiposEventos', filter='tipo_evento_id'))

@modulos_bp.route('/NewTipoEvento')
def NewTipoEvento():
    return render_template(
        '/MODULO_EVENTO/gestionar_tipo_evento.html',
        tipo_evento=None,  # ✅ debe llamarse igual
        mode='insert'
    )

		
# GUARDAR NUEVO
@modulos_bp.route('/SaveTipoEvento', methods=['POST'])
def SaveTipoEvento():
    try:
        nombre_tipo_evento = request.form['nombre_tipo_evento']
        estado = request.form['estado']
        precio_por_hora = request.form['precio_por_hora']
        controlador_evento.insert_tipo_evento(nombre_tipo_evento, estado, precio_por_hora)
        flash("Tipo de evento creado correctamente", "success")
    except Exception as e:
        flash(f"Error al crear el tipo de evento: {str(e)}", "error")

    return redirect(url_for('modulos.FilterTiposEventos', filter='tipo_evento_id'))


# ELIMINAR
@modulos_bp.route('/DeleteTipoEvento', methods=['POST'])
def DeleteTipoEvento():
    tipo_evento_id = request.form.get('tipo_evento_id')
    try:
        controlador_evento.delete_tipo_evento(tipo_evento_id)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e))


# BUSQUEDA AJAX


# BUSQUEDA AJAX
@modulos_bp.route('/SearchTiposEventos')
def SearchTiposEventos():
    query = request.args.get('query', '').strip()

    if query:
        resultados = controlador_evento.search_tipo_evento(query)
    else:
        resultados = controlador_evento.get_tipos_eventos()

    # ✅ resultados ya son diccionarios, así que devolvemos directo
    return jsonify(resultados)



###########    INCIO MODULO EVENTO    ###########
# @modulos_bp.route('/Eventos')
# def eventos():
#     page = int(request.args.get('page', 1))
#     per_page = 7
#     offset = (page - 1) * per_page

#     eventos = controlador_evento.get_eventos(limit=per_page, offset=offset)

#     # Llamamos a la función que marca si ya tienen nota de crédito
#     controlador_evento.marcar_eventos_con_nota_credito_por_id(eventos)

#     total_eventos = controlador_evento.count_eventos()
#     total_pages = (total_eventos + per_page - 1) // per_page

#     return render_template(
#         '/MODULO_EVENTO/gestionar_evento.html',
#         eventos=eventos,
#         mode="list",
#         filter='id_evento',
#         page=page,
#         total_pages=total_pages
#     )



@modulos_bp.route('/FilterEventos/<string:filter>')
def FilterEventos(filter):
    page = int(request.args.get('page', 1))
    per_page = 7
    order = request.args.get('order', 'asc')

    eventos_all = controlador_evento.order_evento(filter, order)
    eventos_all = [
        dict(
            id_evento=e[0],
            nombre_evento=e[1],
            fecha=e[2],
            hora_inicio=e[3],
            hora_fin=e[4],
            estado=e[5]
        ) for e in eventos_all
    ]

    total_eventos = len(eventos_all)
    total_pages = (total_eventos + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    eventos = eventos_all[start:end]

    return render_template(
        '/MODULO_EVENTO/gestionar_evento.html',
        eventos=eventos,
        mode='list',
        filter=filter,
        order=order,
        page=page,
        total_pages=total_pages
        
    )

@modulos_bp.route('/ViewEvento/<int:id_evento>')
def ViewEvento(id_evento):
    evento = controlador_evento.get_evento_by_id(id_evento)
    tipos_eventos = controlador_evento.get_tipos_eventos2()
    return render_template(
        '/MODULO_EVENTO/gestionar_evento.html',
        evento=evento,
        tipos_eventos=tipos_eventos,
        mode='view'
    )

@modulos_bp.route('/EditEvento/<int:id_evento>')
def EditEvento(id_evento):
    evento = controlador_evento.get_evento_by_id(id_evento)   # ✅ función correcta
    tipos_eventos = controlador_evento.get_tipos_eventos2()
    return render_template(
        '/MODULO_EVENTO/gestionar_evento.html',
        evento=evento,
        mode='edit',
        tipos_eventos=tipos_eventos, current_date=date.today() + timedelta(days=1)
    )


@modulos_bp.route('/UpdateEvento', methods=['POST'])
def UpdateEvento():
    try:
        id_evento = int(request.form['id_evento'])
        nombre_evento = request.form['nombre_evento']
        fecha = request.form['fecha']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        # estado = int(request.form.get('estado', 1))

        numero_horas = Decimal(str(request.form['numero_horas']))
        tipo_evento_id = int(request.form['tipo_evento_id'])

        motivo = "Cambio de monto"  # puedes cambiarlo

        print("\n✅ DATOS RECIBIDOS DEL FORMULARIO:")
        print("ID:", id_evento)
        print("Nombre:", nombre_evento)
        print("Fecha:", fecha)
        print("Hora inicio:", hora_inicio)
        print("Hora fin:", hora_fin)
        # print("Estado:", estado)
        print("Horas:", numero_horas)
        print("Tipo evento:", tipo_evento_id)

        # Obtener precio base
        tipo = controlador_evento.get_tipo_evento_by_id(tipo_evento_id)
        precio_base = Decimal(str(tipo[2]))
        precio_final = precio_base * numero_horas

        print("Precio base:", precio_base)
        print("Precio final calculado:", precio_final)

        controlador_evento.update_evento(
            nombre_evento, fecha, hora_inicio, hora_fin, 
            numero_horas, precio_final, tipo_evento_id, id_evento, motivo
        )

        flash("Evento actualizado correctamente", "success")

    except Exception as e:
        print(" ERROR EN UpdateEvento:", e)
        flash(f"Error al actualizar el evento: {str(e)}", "error")

    return redirect(url_for('modulos.evento'))




@modulos_bp.route('/NewEvento')
def NewEvento():
    return render_template('/MODULO_EVENTO/gestionar_evento.html', evento=None, mode='insert')
@modulos_bp.route('/SaveEvento', methods=['POST'])
def SaveEvento():
    try:
        nombre_evento = request.form['nombre_evento']
        fecha = request.form['fecha']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        estado = request.form['estado']

        controlador_evento.insert_evento(nombre_evento, fecha, hora_inicio, hora_fin, estado)
        flash("Evento creado correctamente", "success")
    except Exception as e:
        flash(f"Error al crear el evento: {str(e)}", "error")

    return redirect(url_for('modulos.FilterEventos', filter='id_evento'))
@modulos_bp.route('/SearchEventos')
def SearchEventos():
    query = request.args.get('query', '').strip()

    if query:
        resultados = controlador_evento.search_evento(query)
    else:
        resultados = controlador_evento.get_eventos()

    return jsonify(resultados)


@modulos_bp.route('/BajaEvento', methods=['POST'])
def baja_evento_route():
    try:
        evento_id = int(request.form['evento_id'])
        motivo = request.form['motivo']  # Obligatorio

        # Llamar a la función corregida
        controlador_evento.baja_evento(evento_id, motivo)

        return jsonify({"success": True, "message": "Evento dado de baja correctamente"})
    except Exception as e:
        print("❌ Error en baja_evento_route:", e)
        return jsonify({"success": False, "message": str(e)})



###########    FIN MODULO EVENTO    ###########