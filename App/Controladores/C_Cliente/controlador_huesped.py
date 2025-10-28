# controllers/controlador_huesped.py
from bd import get_connection

def guardar_huesped(data):
    conn = get_connection()
    cursor = conn.cursor()

    query = """INSERT INTO HUESPED (num_doc, nombre, ape_paterno, ape_materno, id_cliente, reserva_habitacion_id)
               VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (
        data.get('num_doc'),
        data.get('nombre'),
        data.get('ape_paterno'),
        data.get('ape_materno'),
        data.get('id_cliente'),
        data.get('reserva_habitacion_id')
    ))
    conn.commit()

    huesped_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return huesped_id
