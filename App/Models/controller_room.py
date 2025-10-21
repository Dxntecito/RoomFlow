from bd import get_connection
from datetime import datetime

def get_rooms(limit=20, offset=0):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
        
                       """)