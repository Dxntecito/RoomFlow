import pymysql

def get_connection():
    conexion = pymysql.connect(
        host='localhost',
        user='root',
        port=3306,
        password='',
        db='roomflowdb',
        charset='utf8mb4'
    )
    with conexion.cursor() as cursor:
        cursor.execute("SET time_zone = '-05:00';")


    return conexion