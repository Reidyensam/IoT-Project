import mysql.connector
import asyncio
from concurrent.futures import ThreadPoolExecutor
from websocket_server import sensor_queue  # Importa la cola compartida

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'proyecto iot'
}

def insert_data_sync(data):
    """
    Inserta datos en la base de datos de forma sincrónica (usado en un hilo separado).
    """
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
        print("Datos insertados:", data)
    except mysql.connector.Error as err:
        print(f"Error en la conexión a la base de datos: {err}")
    finally:
        cursor.close()
        conn.close()

async def process_queue():
    """
    Procesa la cola de sensores de forma asíncrona.
    """
    executor = ThreadPoolExecutor()
    while True:
        data = await sensor_queue.get()
        print(f"Procesando datos: {data}")
        # Enviar a un hilo separado para evitar bloqueos
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, insert_data_sync, data)
        sensor_queue.task_done()
        await asyncio.sleep(0.1)
