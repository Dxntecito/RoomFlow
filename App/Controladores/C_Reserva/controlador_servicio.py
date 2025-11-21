from bd import get_connection
import unicodedata
from pathlib import Path


def _slugify(nombre: str) -> str:
    if not nombre:
        return ""
    normalized = unicodedata.normalize("NFKD", nombre)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower().replace(" ", "_")


BASE_IMG_DIR = Path(__file__).resolve().parents[2] / "Static" / "Img"


def get_services(limit=50, offset=0):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT servicio_id, nombre_servicio, descripcion, precio, estado
                FROM SERVICIO
                WHERE estado = 1
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cursor.fetchall()

            services = []
            for row in rows:
                slug = _slugify(row[1])
                image_map = {
                    "desayuno_buffet": "desayuno.jpg",
                    "spa": "spa.jpg",
                    "lavanderia": "lavanderia.jgp.jpg",
                    "gimnasio": "gimansio.jpg",
                    "wifi_premium": "wifi-premium.png",
                    "estacionamiento": "estacionamiento.jpg",
                }
                image_name = image_map.get(slug, f"{slug}.jpg" if slug else "")
                image_path = BASE_IMG_DIR / image_name if image_name else None
                if not image_path or not image_path.exists():
                    image_name = "fotohotel1.jpg"

                services.append(
                    {
                        "id": row[0],
                        "nombre": row[1],
                        "descripcion": row[2],
                        "precio": float(row[3]) if row[3] is not None else 0.0,
                        "estado": row[4],
                        "slug": slug,
                        "imagen": image_name,
                    }
                )
    finally:
        connection.close()
    return services


