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

def registrar_cliente_natural(cursor, cliente):
    """
    Registra un cliente persona natural (acepta dict, tupla o Row-like).
    Retorna lastrowid si se inserta correctamente, o None.
    """
    try:
        if not cliente:
            print("⚠️ [registrar_cliente_natural] cliente vacío")
            return None

        # Normalizar a dict (si viene tupla/row)
        if isinstance(cliente, dict):
            data = cliente
        else:
            # intentar convertir Row/tupla a dict con keys comunes
            try:
                if hasattr(cliente, "_mapping"):
                    data = dict(cliente._mapping)
                else:
                    # si es tupla/lista asumimos orden (ajusta si tu orden es distinto)
                    keys = ['num_doc', 'nombres', 'ape_paterno', 'ape_materno', 'telefono', 'pais_id', 'correo', 'tipo' ,'tipo_doc_id']
                    data = {k: (cliente[i] if i < len(cliente) else None) for i, k in enumerate(keys)}
            except Exception as e:
                print(f"⚠️ [registrar_cliente_natural] no pude normalizar entrada: {e}")
                return None

        # Extraer campos (aceptar alias para compatibilidad)
        num_doc = data.get('num_doc') or data.get('dni') or None
        nombres = data.get('nombres') or data.get('nombre') or None
        ape_paterno = data.get('ape_paterno') or data.get('apellido') or None
        ape_materno = data.get('ape_materno') or data.get('apeMaterno') or None
        telefono = data.get('telefono') or data.get('movil') or None
        correo = data.get('correo') or data.get('email') or None
        tipo_doc_id = data.get('tipo_doc_id') or None

        # Normalizar pais_id (acepta 'pais_id' o 'id_pais' o 'pais')
        pais_id_raw = data.get('pais_id') or data.get('id_pais') or data.get('pais') or None
        try:
            pais_id = int(pais_id_raw) if pais_id_raw not in (None, '', []) else None
        except Exception:
            pais_id = None

        # Normalizar tipo cliente (guardar 'N' o 'J')
        tipo_cliente = data.get('tipo') or data.get('id_tipo_cliente') or 'N'
        if isinstance(tipo_cliente, str):
            if tipo_cliente.lower().startswith('n'):
                tipo_cliente = 'N'
            elif tipo_cliente.lower().startswith('j'):
                tipo_cliente = 'J'
            else:
                tipo_cliente = 'N'
        else:
            tipo_cliente = 'N'

        # Validaciones mínimas
        if not num_doc or not nombres:
            print("⚠️ [registrar_cliente_natural] faltan datos obligatorios (num_doc o nombres).")
            print("DEBUG data:", data)
            return None

        if pais_id is None:
            print("⚠️ [registrar_cliente_natural] pais_id es None. data:", data)
            # Si quieres asignar por defecto: pais_id = 1
            return None

        # Preparar tuple de insert — ajustado a tu esquema CLIENTE
        # Tabla CLIENTE (según tu DDL): direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, id_tipoemp, ape_paterno, ape_materno, nombres, razon_social
        # Vamos a insertar sólo los campos esenciales (otros NULL)
        params = (num_doc, nombres, ape_paterno, ape_materno, telefono, pais_id, tipo_cliente,tipo_doc_id)
        print("DEBUG [registrar_cliente_natural] params a insertar (num_doc,nombres,ape_p,ape_m,pais_id,tipo):", params)

        # Inserción: usar columnas explícitas para evitar desorden
        cursor.execute("""
            INSERT INTO CLIENTE (num_doc, nombres, ape_paterno, ape_materno, telefono, id_pais, id_tipo_cliente, tipo_doc_id,f_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s ,CURDATE())
        """, params)

        last_id = cursor.lastrowid
        print(f"✅ Cliente persona natural registrado correctamente. id={last_id}")
        return last_id

    except Exception as e:
        print(f"❌ [ERROR en registrar_cliente_natural]: {e}")
        traceback.print_exc()
        return None

def registrar_cliente_juridico(cursor, cliente):
    """
    Registra un cliente persona jurídica (acepta dict/tupla/row).
    Retorna lastrowid o None.
    """
    try:
        if not cliente:
            return None

        if isinstance(cliente, dict):
            data = cliente
        else:
            try:
                if hasattr(cliente, "_mapping"):
                    data = dict(cliente._mapping)
                else:
                    keys = ['ruc', 'razon_social', 'direecion','telefono', 'pais_id','tipo','tipoemp_id', 'tipo_doc_id,']
                    data = {k: (cliente[i] if i < len(cliente) else None) for i, k in enumerate(keys)}
            except Exception as e:
                print(f"⚠️ [registrar_cliente_juridico] no pude normalizar entrada: {e}")
                return None

        ruc = data.get('ruc') or data.get('num_doc') or None
        razon_social = data.get('razon_social') or data.get('razon') or data.get('nombre') or None
        telefono = data.get('telefono') or None
        pais_id_raw = data.get('pais_id') or data.get('id_pais') or None
        direccion = data.get('direccion') or None
        tipoemp_id = data.get('tipoemp_id') or None
        tipo_doc_id = data.get('tipo_doc_id') or None
        try:
            pais_id = int(pais_id_raw) if pais_id_raw not in (None, '', []) else None
        except Exception:
            pais_id = None

        tipo_cliente = data.get('tipo') or data.get('id_tipo_cliente') or 'J'
        if isinstance(tipo_cliente, str):
            if tipo_cliente.lower().startswith('n'):
                tipo_cliente = 'N'
            elif tipo_cliente.lower().startswith('j'):
                tipo_cliente = 'J'
            else:
                tipo_cliente = 'J'
        else:
            tipo_cliente = 'J'

        if not ruc or not razon_social:
            print("⚠️ [registrar_cliente_juridico] faltan ruc o razon_social. data:", data)
            return None

        if pais_id is None:
            print("⚠️ [registrar_cliente_juridico] pais_id es None. data:", data)
            return None

        params = (ruc, razon_social,direccion, telefono, pais_id, tipo_cliente,tipoemp_id,tipo_doc_id)
        print("DEBUG [registrar_cliente_juridico] params a insertar (ruc, razon_social,direccion, telefono, pais_id, tipo_cliente,tipoemp_id,tipo_doc_id):", params)

        # Insertar: guardamos razon_social en campo 'nombres' para unificar tabla CLIENTE
        cursor.execute("""
            INSERT INTO CLIENTE (num_doc, razon_social, direccion, telefono, id_pais, id_tipo_cliente, tipoemp_id, tipo_doc_id, f_registro)
            VALUES (%s, %s, %s, %s, %s, %s , %s, %s ,CURDATE())
        """, (ruc, razon_social, direccion, telefono, pais_id, tipo_cliente,tipoemp_id,tipo_doc_id,))

        last_id = cursor.lastrowid
        print(f"✅ Cliente persona jurídica registrado correctamente. id={last_id}")
        return last_id

    except Exception as e:
        print(f"❌ [ERROR en registrar_cliente_juridico]: {e}")
        traceback.print_exc()
        return None
