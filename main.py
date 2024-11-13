# main.py
import asyncio
from websocket_server import start_websocket_server
from data_processor import process_queue
from app import run_app  # Importa la función desde app.py
async def main():
    # Correr ambos procesos en paralelo
    await asyncio.gather(
        start_websocket_server(),
        run_app(),
        process_queue()
    )

if __name__ == "__main__":
    asyncio.run(main())
