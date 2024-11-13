# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
import mysql.connector
import pandas as pd
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'proyecto iot'
}

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Emite el último registro y el gráfico en tiempo real
def data_stream():
    fibomassi_values = []  # Lista para almacenar los valores de Fibomassi
    while True:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT * FROM Calidad"
        data = pd.read_sql(query, conn)
        conn.close()

        # Convertir el dataframe a una lista de diccionarios
        data_list = data.to_dict(orient='records')
        if data_list:
            last_record = data_list[-1]
            socketio.emit('updateTable', last_record)

            # Almacenar el último valor de Fibomassi
            fibomassi_values.append(last_record['Humedad'])  # Cambiar según la columna que deseas graficar
            # Emitir el gráfico
            socketio.emit('updateChart', fibomassi_values)

        # Espera 1 segundo antes de enviar el siguiente lote de datos
        time.sleep(1)

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(data_stream)
if __name__ == '__main__':
    socketio.run(app, debug=True)
