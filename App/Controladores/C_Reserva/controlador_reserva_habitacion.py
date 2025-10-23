# controllers/controlador_reserva_habitacion.py
from bd import get_connection

def guardar_reserva_habitacion(data):
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id) VALUES (%s, %s)"
    cursor.execute(query, (data.get('reserva_id'), data.get('habitacion_id')))
    conn.commit()

    reserva_habitacion_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return reserva_habitacion_id
