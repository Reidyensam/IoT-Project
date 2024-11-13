# websocket_server.py
import asyncio
import websockets
import json

# Cola de mensajes
message_queue = []

async def handle_client(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        message_queue.append(data)
        print(f"Datos recibidos y encolados: {data}")

async def start_websocket_server():
    print("Servidor WebSocket activo en ws://localhost:8080")
    async with websockets.serve(handle_client, "0.0.0.0", 8080):
        await asyncio.Future()  # Mantener el servidor activo
