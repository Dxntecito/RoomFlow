from bd import get_connection

# OBTENER TODOS LOS PISOS CON LIMIT Y OFFSET
def get_pisos(limit=20, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT piso_id, numero, estado, precio FROM PISO
            LIMIT %s OFFSET %s
        """, (limit, offset))
        rows = cursor.fetchall()
        pisos = []
        for r in rows:
            pisos.append({
                'piso_id': r[0],
                'numero': r[1],
                'estado': r[2],
                'precio': r[3]
            })
    connection.close()
    return pisos

# CONTAR TOTAL DE PISOS
def count_pisos():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM PISO")
        total = cursor.fetchone()[0]
    connection.close()
    return total

# OBTENER UN PISO POR ID
def get_one_piso(piso_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT piso_id, numero, estado, precio 
            FROM PISO WHERE piso_id = %s
        """, (piso_id,))
        row = cursor.fetchone()
        if row:
            return {"piso_id": row[0], "numero": row[1], "estado": row[2], "precio": row[3]}
        return None
    connection.close()
    return None

# INSERTAR NUEVO PISO
def insert_piso(numero, estado, precio):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO PISO (numero, estado, precio)
            VALUES (%s, %s, %s)
        """, (numero, estado, precio))
    connection.commit()
    connection.close()

# ACTUALIZAR PISO EXISTENTE
def update_piso(numero, estado, precio, piso_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE PISO
            SET numero = %s, estado = %s, precio = %s
            WHERE piso_id = %s
        """, (numero, estado, precio, piso_id))
    connection.commit()
    connection.close()

# ELIMINAR PISO
def delete_piso(piso_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM PISO WHERE piso_id = %s", (piso_id,))
    connection.commit()
    connection.close()

# ORDENAR PISOS
def order_piso(filter_field, order):
    allowed_fields = ['piso_id', 'numero', 'estado', 'precio']
    if filter_field not in allowed_fields:
        filter_field = 'piso_id'
    if order.lower() not in ['asc', 'desc']:
        order = 'asc'

    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT piso_id, numero, estado, precio FROM PISO
            ORDER BY {filter_field} {order.upper()}
        """)
        pisos = cursor.fetchall()
    connection.close()
    return pisos

# BUSQUEDA POR NUMERO DE PISO
def search_piso(query):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT piso_id, numero, estado, precio FROM PISO
            WHERE LOWER(numero) LIKE %s
        """, ('%' + query.lower() + '%',))
        pisos = cursor.fetchall()
    connection.close()
    return pisos
