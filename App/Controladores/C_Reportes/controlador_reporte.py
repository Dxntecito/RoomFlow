from bd import get_connection

def get_todas_estadisticas():
    """
    Obtener todas las estadísticas en una sola conexión para mejorar el rendimiento
    Retorna un diccionario con todas las estadísticas
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Obtener totales básicos
            cursor.execute("SELECT COUNT(*) FROM CLIENTE")
            total_clientes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM HABITACION WHERE estado = 1")
            total_habitaciones = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM RESERVA")
            total_reservas = cursor.fetchone()[0]
            
            # Reservas por estado
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN estado = 1 THEN 'Activa'
                        WHEN estado = 0 THEN 'Cancelada'
                        ELSE 'Desconocida'
                    END as estado_reserva,
                    COUNT(*) as cantidad
                FROM RESERVA
                GROUP BY estado
            """)
            resultados_reservas = cursor.fetchall()
            reservas_por_estado = {}
            for row in resultados_reservas:
                reservas_por_estado[row[0]] = row[1]
            
            # Clientes por tipo
            cursor.execute("""
                SELECT 
                    tc.descripcion as tipo_cliente,
                    COUNT(*) as cantidad
                FROM CLIENTE c
                INNER JOIN TIPO_CLIENTE tc ON c.id_tipo_cliente = tc.tipo_cliente_id
                GROUP BY tc.descripcion
            """)
            resultados_clientes = cursor.fetchall()
            clientes_por_tipo = {}
            for row in resultados_clientes:
                clientes_por_tipo[row[0]] = row[1]
            
            # Empleados por turno
            cursor.execute("""
                SELECT 
                    t.nombre_turno,
                    COUNT(DISTINCT dt.empleado_id) as cantidad
                FROM TURNO t
                LEFT JOIN DETALLE_TURNO dt ON t.turno_id = dt.turno_id
                GROUP BY t.turno_id, t.nombre_turno
            """)
            resultados_turnos = cursor.fetchall()
            empleados_por_turno = {}
            for row in resultados_turnos:
                empleados_por_turno[row[0]] = row[1]
            
            # Total tablas
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """)
            total_tablas = cursor.fetchone()[0]
            
            # Total registros
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM CLIENTE) +
                    (SELECT COUNT(*) FROM EMPLEADO) +
                    (SELECT COUNT(*) FROM RESERVA) +
                    (SELECT COUNT(*) FROM HABITACION) +
                    (SELECT COUNT(*) FROM USUARIO) +
                    (SELECT COUNT(*) FROM TURNO) +
                    (SELECT COUNT(*) FROM DETALLE_TURNO) as total
            """)
            total_registros = cursor.fetchone()[0]
            
            # Habitaciones por categoría
            cursor.execute("""
                SELECT 
                    c.nombre_categoria,
                    COUNT(*) as cantidad
                FROM HABITACION h
                INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                GROUP BY c.categoria_id, c.nombre_categoria
            """)
            resultados_habitaciones = cursor.fetchall()
            habitaciones_por_categoria = {}
            for row in resultados_habitaciones:
                habitaciones_por_categoria[row[0]] = row[1]
            
            # Reservas por mes
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                    COUNT(*) as cantidad
                FROM RESERVA
                WHERE fecha_registro >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
                ORDER BY mes
            """)
            resultados_meses = cursor.fetchall()
            reservas_por_mes = {}
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            for row in resultados_meses:
                fecha_str = row[0]
                año, mes = fecha_str.split('-')
                mes_nombre = f"{meses[int(mes)-1]} {año}"
                reservas_por_mes[mes_nombre] = row[1]
            
            return {
                'total_clientes': total_clientes,
                'total_habitaciones': total_habitaciones,
                'total_reservas': total_reservas,
                'reservas_por_estado': reservas_por_estado,
                'clientes_por_tipo': clientes_por_tipo,
                'empleados_por_turno': empleados_por_turno,
                'total_tablas': total_tablas,
                'total_registros': total_registros,
                'habitaciones_por_categoria': habitaciones_por_categoria,
                'reservas_por_mes': reservas_por_mes
            }
    finally:
        connection.close()

def get_total_clientes():
    """
    Obtener el total de clientes
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM CLIENTE")
            total = cursor.fetchone()[0]
            return total
    finally:
        connection.close()

def get_total_habitaciones_disponibles():
    """
    Obtener el total de habitaciones disponibles (estado = 1)
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM HABITACION WHERE estado = 1")
            total = cursor.fetchone()[0]
            return total
    finally:
        connection.close()

def get_total_reservas():
    """
    Obtener el total de reservas
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM RESERVA")
            total = cursor.fetchone()[0]
            return total
    finally:
        connection.close()

def get_reservas_por_estado():
    """
    Obtener el conteo de reservas por estado
    Retorna un diccionario con {estado: cantidad}
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN estado = 1 THEN 'Activa'
                        WHEN estado = 0 THEN 'Cancelada'
                        ELSE 'Desconocida'
                    END as estado_reserva,
                    COUNT(*) as cantidad
                FROM RESERVA
                GROUP BY estado
            """)
            resultados = cursor.fetchall()
            
            # Convertir a diccionario
            reservas_por_estado = {}
            for row in resultados:
                reservas_por_estado[row[0]] = row[1]
            
            return reservas_por_estado
    finally:
        connection.close()

def get_clientes_por_tipo():
    """
    Obtener el conteo de clientes por tipo
    Retorna un diccionario con {tipo: cantidad}
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    tc.descripcion as tipo_cliente,
                    COUNT(*) as cantidad
                FROM CLIENTE c
                INNER JOIN TIPO_CLIENTE tc ON c.id_tipo_cliente = tc.tipo_cliente_id
                GROUP BY tc.descripcion
            """)
            resultados = cursor.fetchall()
            
            # Convertir a diccionario
            clientes_por_tipo = {}
            for row in resultados:
                clientes_por_tipo[row[0]] = row[1]
            
            return clientes_por_tipo
    finally:
        connection.close()

def get_empleados_por_turno():
    """
    Obtener el conteo de empleados asignados por turno
    Retorna un diccionario con {turno: cantidad}
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.nombre_turno,
                    COUNT(DISTINCT dt.empleado_id) as cantidad
                FROM TURNO t
                LEFT JOIN DETALLE_TURNO dt ON t.turno_id = dt.turno_id
                GROUP BY t.turno_id, t.nombre_turno
            """)
            resultados = cursor.fetchall()
            
            # Convertir a diccionario
            empleados_por_turno = {}
            for row in resultados:
                empleados_por_turno[row[0]] = row[1]
            
            return empleados_por_turno
    finally:
        connection.close()

def get_total_tablas():
    """
    Obtener el total de tablas en la base de datos
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """)
            total = cursor.fetchone()[0]
            return total
    finally:
        connection.close()

def get_total_registros():
    """
    Obtener el total de registros en todas las tablas principales
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Sumar registros de las tablas principales
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM CLIENTE) +
                    (SELECT COUNT(*) FROM EMPLEADO) +
                    (SELECT COUNT(*) FROM RESERVA) +
                    (SELECT COUNT(*) FROM HABITACION) +
                    (SELECT COUNT(*) FROM USUARIO) +
                    (SELECT COUNT(*) FROM TURNO) +
                    (SELECT COUNT(*) FROM DETALLE_TURNO) as total
            """)
            total = cursor.fetchone()[0]
            return total
    finally:
        connection.close()

def get_habitaciones_por_categoria():
    """
    Obtener el conteo de habitaciones por categoría
    Retorna un diccionario con {categoria: cantidad}
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.nombre_categoria,
                    COUNT(*) as cantidad
                FROM HABITACION h
                INNER JOIN CATEGORIA c ON h.id_categoria = c.categoria_id
                GROUP BY c.categoria_id, c.nombre_categoria
            """)
            resultados = cursor.fetchall()
            
            # Convertir a diccionario
            habitaciones_por_categoria = {}
            for row in resultados:
                habitaciones_por_categoria[row[0]] = row[1]
            
            return habitaciones_por_categoria
    finally:
        connection.close()

def get_reservas_por_mes():
    """
    Obtener el conteo de reservas por mes (últimos 12 meses)
    Retorna un diccionario con {mes: cantidad}
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(fecha_registro, '%Y-%m') as mes,
                    COUNT(*) as cantidad
                FROM RESERVA
                WHERE fecha_registro >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(fecha_registro, '%Y-%m')
                ORDER BY mes
            """)
            resultados = cursor.fetchall()
            
            # Convertir a diccionario con formato de mes legible
            reservas_por_mes = {}
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            
            for row in resultados:
                # Formato: YYYY-MM
                fecha_str = row[0]
                año, mes = fecha_str.split('-')
                mes_nombre = f"{meses[int(mes)-1]} {año}"
                reservas_por_mes[mes_nombre] = row[1]
            
            return reservas_por_mes
    finally:
        connection.close()

