# controllers/controlador_cliente.py
from datetime import date
from bd import get_connection
import traceback

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

def buscar_cliente_por_documento(num_doc):
    """
    Devuelve cliente_id (int) si existe, o None.
    Usa get_connection() y with connection.cursor().
    """
    if not num_doc:
        return None

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT cliente_id FROM CLIENTE WHERE num_doc = %s", (num_doc,))
            row = cursor.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"❌ [ERROR en buscar_cliente_por_documento]: {e}")
        traceback.print_exc()
        return None
    finally:
        if connection:
            connection.close()

def buscar_cliente_natural(num_doc):
    """
    Devuelve una tupla con los datos del cliente natural si existe, o None.
    """
    if not num_doc:
        return None

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                cliente_id,
                num_doc,
                telefono,
                id_pais,
                tipo_doc_id,
                ape_paterno,
                ape_materno,
                nombres
            FROM CLIENTE
            WHERE num_doc = %s AND id_tipo_cliente = 'N'
        """
        cursor.execute(query, (num_doc,))
        row = cursor.fetchone()
        return row
    except Exception as e:
        print(f"❌ [ERROR en buscar_cliente_natural]: {e}")
        traceback.print_exc()
        return None
    finally:
        if conn:
            conn.close()

def buscar_cliente_juridico(num_doc):
    """
    Devuelve una tupla con los datos del cliente jurídico si existe, o None.
    """
    if not num_doc:
        return None

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    cliente_id,
                    num_doc,
                    telefono,
                    id_pais,
                    tipo_doc_id,
                    tipoemp_id,
                    razon_social,
                    direccion
                FROM CLIENTE
                WHERE num_doc = %s AND id_tipo_cliente = 'J'
            """
            cursor.execute(query, (num_doc,))
            row = cursor.fetchone()
            return row
    except Exception as e:
        print(f"❌ [ERROR en buscar_cliente_juridico]: {e}")
        traceback.print_exc()
        return None
    finally:
        if connection:
            connection.close()
