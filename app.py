from flask import Flask, render_template, request, redirect, url_for, jsonify
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grafico')
def grafico():
    return render_template('tabla.html')

@app.route('/altas', methods=['GET', 'POST'])
def altas():
    if request.method == 'POST':
        # Obtener los valores del formulario
        tiempo = request.form['tiempo']
        aire = request.form['aire']
        ultrasonico = request.form['ultrasonico']
        temperatura = request.form['temperatura']
        humedad = request.form['humedad']

        if not tiempo or not aire or not ultrasonico or not temperatura or not humedad:
            return "Todos los campos son obligatorios", 400

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = """
                INSERT INTO Calidad (Tiempo, aire, Ultrasonico, Temperatura, Humedad) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (tiempo, aire, ultrasonico, temperatura, humedad))
            conn.commit()
            conn.close()

            return redirect(url_for('altas'))
        except mysql.connector.Error as err:
            return f"Error al insertar en la base de datos: {err}", 500

    return render_template('altas.html')

@app.route('/bajas', methods=['GET', 'POST'])
def bajas():
    if request.method == 'POST':
        record_id = request.form['record_id']

        if not record_id:
            return "El ID del registro es obligatorio", 400

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            query = "DELETE FROM Calidad WHERE ID = %s"
            cursor.execute(query, (record_id,))
            conn.commit()
            conn.close()

            return redirect(url_for('bajas'))
        except mysql.connector.Error as err:
            return f"Error al eliminar el registro: {err}", 500

    return render_template('bajas.html')

# Nueva función para buscar por ID
@app.route('/buscar', methods=['GET'])
def buscar():
    record_id = request.args.get('id')
    
    if not record_id:
        return "El ID del registro es obligatorio", 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Consultar el registro por ID
        query = "SELECT * FROM Calidad WHERE ID = %s"
        cursor.execute(query, (record_id,))
        result = cursor.fetchone()  # Obtener un solo registro

        conn.close()
        
        if result:
            return jsonify(result)  # Devolver el resultado en formato JSON
        else:
            return "Registro no encontrado", 404

    except mysql.connector.Error as err:
        return f"Error al buscar el registro: {err}", 500

# Emite el último registro y el gráfico en tiempo real
def data_stream():
    fibomassi_values = []
    while True:
        conn = mysql.connector.connect(**db_config)
        query = "SELECT * FROM Calidad"
        data = pd.read_sql(query, conn)
        conn.close()

        data_list = data.to_dict(orient='records')
        if data_list:
            last_record = data_list[-1]
            socketio.emit('updateTable', last_record)

            fibomassi_values.append(last_record['Humedad'])
            socketio.emit('updateChart', fibomassi_values)

        time.sleep(1)

@socketio.on('connect')
def handle_connect():
    socketio.start_background_task(data_stream)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
