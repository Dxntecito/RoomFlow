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


