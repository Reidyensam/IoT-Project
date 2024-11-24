# data_processor.py
import mysql.connector
import asyncio
from websocket_server import sensor_queue

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'proyecto iot'
}

async def insert_data(data):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = """
            INSERT INTO Calidad (Tiempo, aire, Ultrasonico, Temperatura, Humedad)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            data['Tiempo'],
            data['aire'],
            data['Ultrasonico'],
            data['Temperatura'],
            data['Humedad']
        )
        cursor.execute(sql, values)
        conn.commit()
        print("Datos insertados en la base de datos:", data)

    except mysql.connector.Error as err:
        print(f"Error en la conexión a la base de datos: {err}")
    finally:
        cursor.close()
        conn.close()

async def process_queue():
    while True:
        if sensor_queue:
            # Aquí puedes añadir un mecanismo de sincronización si es necesario
            data = sensor_queue.pop(0)
            await insert_data(data)
        await asyncio.sleep(0.5)
