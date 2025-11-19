from bd import get_connection
import unicodedata


def _slugify(nombre: str) -> str:
    """
    Convierte el nombre de la categoría en un identificador apto para usar como nombre
    de archivo (p. ej. 'Económica' -> 'economica').
    """
    if not nombre:
        return ""
    normalized = unicodedata.normalize("NFKD", nombre)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower().replace(" ", "_")


def get_categories(limit=20, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    c.categoria_id,
                    c.nombre_categoria,
                    c.precio_categoria,
                    c.estado,
                    c.capacidad,
                    c.descripcion
                FROM CATEGORIA c
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cursor.fetchall()

            categories = []
            for row in rows:
                categories.append({
                    "id": row[0],
                    "nombre": row[1],
                    "precio": float(row[2]) if row[2] is not None else 0.0,
                    "estado": row[3],
                    "capacidad": row[4],
                    "descripcion": row[5],
                    "slug": _slugify(row[1])
                })
    finally:
        connection.close()
    return categories


def count_categories():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM CATEGORIA")
            row = cursor.fetchone()
            return row[0] if row else 0
    finally:
        connection.close()


def order_categories(field="categoria_id", order="asc"):
    valid_fields = {
        "categoria_id": "categoria_id",
        "nombre": "nombre_categoria",
        "precio": "precio_categoria",
        "estado": "estado",
        "capacidad": "capacidad"
    }
    field_db = valid_fields.get(field, "categoria_id")
    order_db = "DESC" if str(order).lower() == "desc" else "ASC"

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    categoria_id,
                    nombre_categoria,
                    precio_categoria,
                    estado,
                    capacidad,
                    descripcion
                FROM CATEGORIA
                ORDER BY {field_db} {order_db}
            """)
            rows = cursor.fetchall()
            categories = []
            for row in rows:
                categories.append({
                    "id": row[0],
                    "nombre": row[1],
                    "precio": float(row[2]) if row[2] is not None else 0.0,
                    "estado": row[3],
                    "capacidad": row[4],
                    "descripcion": row[5],
                    "slug": _slugify(row[1])
                })
            return categories
    finally:
        connection.close()


def get_category(categoria_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    categoria_id,
                    nombre_categoria,
                    precio_categoria,
                    estado,
                    capacidad,
                    descripcion
                FROM CATEGORIA
                WHERE categoria_id = %s
            """, (categoria_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "nombre": row[1],
                "precio": float(row[2]) if row[2] is not None else 0.0,
                "estado": row[3],
                "capacidad": row[4],
                "descripcion": row[5],
                "slug": _slugify(row[1])
            }
    finally:
        connection.close()


def insert_category(nombre, precio, estado, capacidad, descripcion):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO CATEGORIA (nombre_categoria, precio_categoria, estado, capacidad, descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, precio, estado, capacidad, descripcion))
        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        connection.close()


def update_category(categoria_id, nombre, precio, estado, capacidad, descripcion):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE CATEGORIA
                SET nombre_categoria = %s,
                    precio_categoria = %s,
                    estado = %s,
                    capacidad = %s,
                    descripcion = %s
                WHERE categoria_id = %s
            """, (nombre, precio, estado, capacidad, descripcion, categoria_id))
        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        connection.close()


def delete_category(categoria_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM CATEGORIA WHERE categoria_id = %s", (categoria_id,))
        connection.commit()
        return True
    except Exception:
        if connection:
            connection.rollback()
        raise
    finally:
        connection.close()


def search_categories(query):
    connection = get_connection()
    try:
        wildcard = f"%{query}%"
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    categoria_id,
                    nombre_categoria,
                    precio_categoria,
                    estado,
                    capacidad,
                    descripcion
                FROM CATEGORIA
                WHERE nombre_categoria LIKE %s
                   OR descripcion LIKE %s
            """, (wildcard, wildcard))
            rows = cursor.fetchall()
            categories = []
            for row in rows:
                categories.append({
                    "id": row[0],
                    "nombre": row[1],
                    "precio": float(row[2]) if row[2] is not None else 0.0,
                    "estado": row[3],
                    "capacidad": row[4],
                    "descripcion": row[5],
                    "slug": _slugify(row[1])
                })
            return categories
    finally:
        connection.close()


