import pymysql

def get_connection():
    conexion = pymysql.connect(
        host='switchyard.proxy.rlwy.net',
        user='root',
        port=21592,
        password='mnNJDFhyYUysKijkrSpMRTpjjelkoptN',
        db='roomflow',
        charset='utf8mb4'
    )
    with conexion.cursor() as cursor:
        cursor.execute("SET time_zone = '-05:00';")


    return conexion