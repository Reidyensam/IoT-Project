import asyncio
from threading import Thread
from websocket_server import start_websocket_server  # Asegúrate de implementar esta función
from data_processor import process_queue  # Asegúrate de implementar esta función
from app import socketio, app  # Importa tu aplicación Flask-SocketIO

async def main():
    await asyncio.gather(
        start_websocket_server(),
        process_queue()
    )
if __name__ == "__main__":
    asyncio.run(main())
