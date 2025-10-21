from bd import get_connection
from datetime import datetime

def insert_detalle_comprobante(metodo_pago, nro_tarjeta, monto_total, estado=1):
    """
    Inserta un nuevo detalle de comprobante y retorna su ID generado.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO DETALLE_COMPROBANTE (metodo_pago, nro_tarjeta, monto_total, fecha_pago, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (metodo_pago, nro_tarjeta, monto_total, datetime.now(), estado))
            connection.commit()
            return cursor.lastrowid  # ✅ retorna el ID del comprobante creado
    except Exception as ex:
        print("❌ Error al insertar detalle_comprobante:", ex)
        return None
    finally:
        connection.close()
