import asyncio
import websockets
import json
import base64
from pynput import keyboard
from concurrent.futures import ThreadPoolExecutor

# Configuración global
sensor_queue = asyncio.Queue()
key_pressed = None
connected_clients = set()
executor = ThreadPoolExecutor()

def on_press(key):
    global key_pressed
    try:
        if key.char in ['w', 'x', 'a', 'd', 'q', 'e', 'z', 'c', 'g', 'f', 's']:
            key_pressed = key.char
    except AttributeError:
        pass

async def send_response_on_keypress(websocket):
    global key_pressed
    last_command = None
    last_key = None  # Variable para controlar la tecla presionada

    while True:
        command = None

        # Solo se envía el comando si una nueva tecla es presionada
        if key_pressed and key_pressed != last_key:
            last_key = key_pressed  # Guardar la tecla presionada

            if key_pressed == 'w':
                command = "adelante"
            elif key_pressed == 'x':
                command = "atras"
            elif key_pressed == 'a':
                command = "izquier"
            elif key_pressed == 'd':
                command = "derecha"
            elif key_pressed == 'q':
                command = "ader"
            elif key_pressed == 'e':
                command = "aizq"
            elif key_pressed == 'z':
                command = "bizq"
            elif key_pressed == 'c':
                command = "bder"
            elif key_pressed == 'g':
                command = "dder"
            elif key_pressed == 'f':
                command = "iizq"
            elif key_pressed == 's':
                command = "quieto"

            # Enviar el comando solo si ha cambiado
            if command != last_command:
                response = {"command": command}
                try:
                    await websocket.send(json.dumps(response))
                    print(f"Comando enviado: '{command}'")
                    last_command = command
                except websockets.exceptions.ConnectionClosed:
                    print("No se pudo enviar comando: cliente desconectado")
                    break

        # Esperar un pequeño tiempo para procesar los cambios de tecla
        await asyncio.sleep(0.05)


async def process_sensor_data():
    while True:
        data = await sensor_queue.get()
        try:
            print(f"Procesando datos del sensor: {data}")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(executor, insert_data_sync, data)
        finally:
            sensor_queue.task_done()

def insert_data_sync(data):
    import time
    time.sleep(0.1)
    print(f"Datos insertados en la base de datos: {data}")

async def retransmit_frame(frame_data, websocket):
    frame_message = json.dumps({
        "role": "stream",
        "frame": frame_data
    })

    disconnected_clients = []
    for client in list(connected_clients):
        if client != websocket:
            try:
                await client.send(frame_message)
                await asyncio.sleep(0.01)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)

    for client in disconnected_clients:
        connected_clients.remove(client)

async def process_message(message, websocket):
    try:
        data = json.loads(message)
        role = data.get("role")
        if role == "sensor":
            await sensor_queue.put(data)
        elif role == "video" and 'frame' in data:
            await retransmit_frame(data['frame'], websocket)
    except json.JSONDecodeError:
        error_response = {"error": "Mensaje no válido. Debe ser JSON."}
        await websocket.send(json.dumps(error_response))

async def handle_client(websocket, path):
    global connected_clients
    connected_clients.add(websocket)
    print(f"Cliente conectado desde {path}")

    try:
        asyncio.create_task(send_response_on_keypress(websocket))

        async for message in websocket:
            asyncio.create_task(process_message(message, websocket))

    except websockets.exceptions.ConnectionClosedError:
        print(f"El cliente cerró la conexión: {path}")
    finally:
        connected_clients.remove(websocket)

async def start_websocket_server():
    print("Servidor WebSocket activo en ws://localhost:8080")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    server = await websockets.serve(handle_client, "0.0.0.0", 8080)
    await asyncio.gather(server.wait_closed(), process_sensor_data())

if __name__ == "__main__":
    asyncio.run(start_websocket_server())
