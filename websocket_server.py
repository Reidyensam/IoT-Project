# websocket_server.py
import asyncio
import websockets
import json
from pynput import keyboard
# Cola de mensajes
sensor_queue = []
key_pressed = None
# Función que se ejecuta al presionar una tecla
def on_press(key):
    global key_pressed
    try:
        if key.char in ['w', 's', 'a', 'd']:  # Solo registrar teclas relevantes
            key_pressed = key.char
    except AttributeError:
        pass

async def send_response_on_keypress(websocket):
    """
    Envía un mensaje al cliente cuando se detecta un cambio en las teclas presionadas.
    """
    global key_pressed
    last_command = None  # Almacena el último comando enviado

    while True:
        command = None

        if key_pressed == 'w':
            command = "adelante"
        elif key_pressed == 's':
            command = "atras"
        elif key_pressed == 'a':
            command = "izquier"
        elif key_pressed == 'd':
            command = "derecha"
        elif key_pressed is None:
            command = "quieto"

        # Solo enviar si el comando es diferente al último enviado
        if command != last_command:
            response = {"command": command}
            await websocket.send(json.dumps(response))
            print(f"Comando enviado: '{command}'")
            last_command = command  # Actualizar el último comando enviado

        key_pressed = None  # Reinicia la detección de teclas
        await asyncio.sleep(0.4)  # Pausa pequeña para evitar uso excesivo de CPU


async def handle_client(websocket, path):
    print(f"Cliente conectado desde {path}")
    try:
        keypress_task = asyncio.create_task(send_response_on_keypress(websocket))
        async for message in websocket:
            try:
                # Intentar cargar el mensaje como JSON
                #response = {"command": "adelante"}
                #await websocket.send(json.dumps(response))
                data = json.loads(message)
                role = data.get("role")
                print(role)
                if role == "sensor":
                    sensor_queue.append(data)
                    print(f"Datos recibidos y encolados: {data}")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
                # Responder con un mensaje de error
                error_response = {"error": "Mensaje no válido. Debe ser JSON."}
                await websocket.send(json.dumps(error_response))
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"El cliente cerró la conexión: {e}")
    except websockets.exceptions.ProtocolError as e:
        print(f"Error de protocolo: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        print(f"Cliente desconectado desde {path}")

async def start_websocket_server():
    print("Servidor WebSocket activo en ws://localhost:8080")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    async with websockets.serve(handle_client, "0.0.0.0", 8080):
        await asyncio.Future()  # Mantener el servidor activo
