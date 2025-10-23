# controllers/controlador_cliente.py
from datetime import date
from bd import get_connection

def guardar_cliente(data):
    num_doc = data.get('num_doc')
    tipo_cliente = data.get('id_tipo_cliente')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar si ya existe
    cursor.execute("SELECT cliente_id FROM CLIENTE WHERE num_doc = %s", (num_doc,))
    existente = cursor.fetchone()

    if existente:
        cliente_id = existente['cliente_id']
    else:
        query = """INSERT INTO CLIENTE 
                   (direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, id_tipoemp, 
                    ape_paterno, ape_materno, nombres, razon_social)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (
            data.get('direccion'),
            data.get('telefono'),
            date.today(),
            num_doc,
            tipo_cliente,
            data.get('id_pais'),
            data.get('id_tipoemp'),
            data.get('ape_paterno'),
            data.get('ape_materno'),
            data.get('nombres'),
            data.get('razon_social')
        )
        cursor.execute(query, valores)
        conn.commit()
        cliente_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return cliente_id
