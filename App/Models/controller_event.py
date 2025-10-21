from bd import get_connection
from Models import controller_detalle

def insert_evento(nombre_evento, fecha, hora_inicio, hora_fin, estado, tipo_evento_id, tipo_reserva_id, detalle_comprobante_id, num_horas, precio_final):
    """
    Inserta un nuevo evento (reserva) en la base de datos.
    """

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO EVENTO (
                    nombre_evento, fecha, hora_inicio, hora_fin, estado, 
                    tipo_evento_id, tipo_reserva_id, detalle_comprobante_id, 
                    num_horas, precio_final
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nombre_evento,
                fecha,
                hora_inicio,
                hora_fin,
                estado,
                tipo_evento_id,
                tipo_reserva_id,
                detalle_comprobante_id,
                num_horas,
                precio_final
            ))
        connection.commit()
        print("✅ Evento insertado correctamente")
        return True
    except Exception as ex:
        print("❌ Error al insertar evento:", ex)
        return False
    finally:
        connection.close()
def registrar_evento_con_comprobante(nombre_evento, fecha, hora_inicio, hora_fin, estado, tipo_evento_id,
                                     tipo_reserva_id, metodo_pago, nro_tarjeta, precio_por_hora):
    from datetime import datetime

    # Calcular número de horas y precio total
    formato = "%H:%M"
    h1 = datetime.strptime(hora_inicio, formato)
    h2 = datetime.strptime(hora_fin, formato)

    num_horas = int((h2 - h1).seconds / 3600)
    precio_final = num_horas * precio_por_hora

    # 1️⃣ Insertar el detalle de comprobante
    detalle_id = controller_detalle.insert_detalle_comprobante(metodo_pago, nro_tarjeta, precio_final)

    # 2️⃣ Insertar el evento si se creó el comprobante
    if detalle_id:
        insert_evento(
            nombre_evento,
            fecha,
            hora_inicio,
            hora_fin,
            estado,
            tipo_evento_id,
            tipo_reserva_id,
            detalle_id,
            num_horas,
            precio_final
        )
        print("✅ Evento y comprobante registrados correctamente.")
    else:
        print("❌ No se pudo crear el comprobante.")

