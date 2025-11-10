from bd import get_connection
from datetime import datetime
from decimal import Decimal
from flask import request, jsonify
from datetime import date
from pymysql.cursors import DictCursor

def get_tipos_servicio_evento(): 
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_tipo_servicio_evento, 
                nombre_tipo, 
                estado
            FROM TIPO_SERVICIO_EVENTO
            WHERE estado = 1
            ORDER BY nombre_tipo ASC
        """)
        tipos_servicio = cursor.fetchall()
    connection.close()
    return tipos_servicio



def get_todos_servicios_por_tipo_servicio():
    connection = get_connection()
    with connection.cursor(DictCursor) as cursor:
        cursor.execute("""
            SELECT 
                s.id_servicio_evento,
                s.nombre_servicio,
                s.descripcion,
                s.precio,
                s.estado,
                t.id_tipo_servicio_evento,
                t.nombre_tipo AS nombre_tipo
            FROM SERVICIO_EVENTO s
            INNER JOIN TIPO_SERVICIO_EVENTO t 
                ON s.tipo_servicio_evento_id = t.id_tipo_servicio_evento
            WHERE s.estado = 1
        """)
        servicios = cursor.fetchall()
    connection.close()
    return servicios


def get_servicios_por_tipo(tipo_id):
    connection = get_connection()
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT 
                id_servicio_evento,
                nombre_servicio,
                descripcion,
                precio,
                estado
            FROM SERVICIO_EVENTO
            WHERE tipo_servicio_evento_id = %s
              AND estado = 1
            ORDER BY nombre_servicio
        """, (tipo_id,))
        servicios = cursor.fetchall()
    connection.close()
    return servicios
