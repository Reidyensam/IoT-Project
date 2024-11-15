import asyncio
from threading import Thread
from websocket_server import start_websocket_server
from data_processor import process_queue
from app import socketio, app  # Importa tu aplicación Flask-SocketIO

# Función para iniciar el servidor Flask-SocketIO en segundo plano
def run_flask_socketio():
    # Quita `debug=True` para evitar el conflicto con las señales en hilos secundarios
    socketio.run(app, host="0.0.0.0", port=5000)

async def main():
    # Ejecuta la app Flask-SocketIO en un hilo separado
    #flask_thread = Thread(target=run_flask_socketio)
    #flask_thread.start()

    # Correr el servidor WebSocket y el procesamiento de cola en paralelo
    await asyncio.gather(
        start_websocket_server(),
        process_queue()
    )

if __name__ == "__main__":
    asyncio.run(main())
