import asyncio
from threading import Thread
from websocket_server import start_websocket_server  # Asegúrate de implementar esta función
from data_processor import process_queue  # Asegúrate de implementar esta función
from app import socketio, app  # Importa tu aplicación Flask-SocketIO

# Función para iniciar el servidor Flask-SocketIO en segundo plano
def run_flask_socketio():
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)  # Quita `debug=True` para evitar conflictos en hilos

# Función principal asíncrona
async def main():
    # Inicia la app Flask-SocketIO en un hilo separado
    #flask_thread = Thread(target=run_flask_socketio, daemon=True)  # Daemon para que se cierre al terminar el proceso principal
    #flask_thread.start()

    # Ejecuta el servidor WebSocket y el procesamiento de la cola en paralelo
    await asyncio.gather(
        start_websocket_server(),
        process_queue()
    )

if __name__ == "__main__":
    asyncio.run(main())
