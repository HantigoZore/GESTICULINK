from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from deepface import DeepFace
import numpy as np
import base64
import serial
import time
import threading

app = Flask(__name__)
CORS(app)

# --- Lock global para acceso exclusivo ---
locked = False
serial_lock = threading.Lock()  # Lock para acceso al puerto serial

# --- Configuración del puerto ---
PUERTO_ESP32 = 'COM6'  # Cambia según tu sistema
BAUD_RATE = 115200

# --- Abrir el puerto globalmente al iniciar ---
try:
    ser = serial.Serial(PUERTO_ESP32, BAUD_RATE, timeout=1)
    time.sleep(2)  # Espera a que la ESP32 inicialice el puerto
    print(f"✅ Puerto {PUERTO_ESP32} abierto para toda la sesión")
except Exception as e:
    ser = None
    print(f"⚠️ No se pudo abrir {PUERTO_ESP32}: {e}")

emociones_permitidas = ["angry", "sad", "happy", "surprise"]
porcentaje_minimo = 10

@app.route('/lock', methods=['POST'])
def acquire_lock():
    global locked
    if not locked:
        locked = True
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "locked"})

@app.route('/unlock', methods=['POST'])
def release_lock():
    global locked
    locked = False
    return jsonify({"status": "unlocked"})

def detectar_emocion(frame):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion_scores = result[0]['emotion']
        emociones_filtradas = {k: v for k, v in emotion_scores.items() if k in emociones_permitidas}
        if emociones_filtradas:
            emotion = max(emociones_filtradas, key=lambda k: emociones_filtradas[k])
            if emociones_filtradas[emotion] < porcentaje_minimo:
                emotion = "neutral"
        else:
            emotion = "neutral"
        return emotion
    except Exception as e:
        print(f"Error detectando emoción: {e}")
        return "error"

def enviar_a_esp32(emocion):
    global ser
    if ser is not None:
        with serial_lock:
            try:
                ser.write((emocion + "\n").encode('utf-8'))
                print(f"✅ Enviado a ESP32: {emocion}")
            except Exception as e:
                print(f"⚠️ Error enviando a la ESP32: {e}")
    else:
        print("❌ Puerto no disponible")

@app.route('/emocion', methods=['POST'])
def emocion():
    print("Petición recibida")
    data = request.json
    img_data = data['image']

    if ',' in img_data:
        img_data = img_data.split(",")[1]

    try:
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        emocion_detectada = detectar_emocion(frame)
        print(f"Emoción detectada: {emocion_detectada}")

        if emocion_detectada in emociones_permitidas:
            enviar_a_esp32(emocion_detectada)
        else:
            enviar_a_esp32("neutral")

        return jsonify({'emocion': emocion_detectada})
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return jsonify({'error': 'no se pudo procesar la imagen'}), 400

if __name__ == '__main__':
    # debug=False evita reinicios automáticos que abren el puerto varias veces
    app.run(host='127.0.0.1', port=5000, debug=False)
