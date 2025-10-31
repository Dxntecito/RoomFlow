# App/Controladores/C_Facturacion/controlador_transaccion.py
import traceback
from bd import get_connection

def registrar_transaccion(data):
    """
    Inserta una transacción en la tabla TRANSACCION.
    data: dict posible con claves variadas.
    Retorna transaccion_id (int) o None si falló.
    """
    connection = None
    try:
        # normalizar keys - aceptar distintos nombres
        metodo = data.get('metodo') or data.get('metodo_pago_id') or data.get('paymentMethodInputs') or data.get('paymentMethod');
        monto_raw = data.get('monto') or data.get('finalTotal') or data.get('final_total') or data.get('finaltotal');
        estado = data.get('estado', 1)
        reserva_id = data.get('reservaId') or data.get('reserva_id') or data.get('reserva')

        # si metodo viene como 'card'/'wallet', mapear a id (ajusta según tu tabla METODO_PAGO)
        if isinstance(metodo, str):
            m = metodo.lower()
            if m in ('card','tarjeta','card_payment'):
                metodo_pago_id = 1
            elif m in ('wallet','billetera','yape','wallet_payment'):
                metodo_pago_id = 2
            else:
                # si es numérico en string, intentar convertir
                try:
                    metodo_pago_id = int(metodo)
                except Exception:
                    metodo_pago_id = None
        else:
            try:
                metodo_pago_id = int(metodo) if metodo is not None else None
            except Exception:
                metodo_pago_id = None

        # monto -> float
        try:
            monto = float(monto_raw) if monto_raw not in (None, '') else None
        except Exception:
            monto = None

        try:
            reserva_id = int(reserva_id) if reserva_id not in (None, '') else None
        except Exception:
            reserva_id = None

        try:
            estado = int(estado)
        except Exception:
            estado = 1

        # VALIDACION
        if not all([metodo_pago_id, monto is not None, reserva_id]):
            print("⚠️ Faltan datos obligatorios para registrar la transacción:", {
                'metodo_pago_id': metodo_pago_id,
                'monto': monto,
                'reserva_id': reserva_id,
                'estado': estado
            })
            return None

        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TRANSACCION (metodo_pago_id, fecha_pago, monto, estado, reserva_id)
                VALUES (%s, CURDATE(), %s, %s, %s)
            """, (metodo_pago_id, monto, estado, reserva_id))
            transaccion_id = cursor.lastrowid
            connection.commit()
            print("✅ Transacción registrada, id:", transaccion_id)
            return transaccion_id

    except Exception as e:
        print("❌ [ERROR registrar_transaccion]:", e)
        traceback.print_exc()
        try:
            if connection:
                connection.rollback()
        except:
            pass
        return None
    finally:
        if connection:
            connection.close()
