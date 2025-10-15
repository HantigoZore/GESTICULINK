from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
from deepface import DeepFace
import numpy as np
import base64
import serial
import time

# --- Configuración del servidor Flask ---
app = Flask(__name__)
CORS(app)
ser = serial.Serial('COM3', 115200, timeout=1)
time.sleep(2)  

# --- Lock global para acceso exclusivo ---
locked = False

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

emociones_permitidas = ["angry", "sad", "happy", "surprise"]
porcentaje_minimo = 10

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

@app.route('/emocion', methods=['POST'])
def emocion():
    print("Petición recibida")
    data = request.json
    img_data = data['image']

    # Decodifica la imagen base64
    if ',' in img_data:
        img_data = img_data.split(",")[1]

    try:
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        emocion_detectada = detectar_emocion(frame)

        print(f"Emoción detectada: {emocion_detectada}")

        # --- Enviar emoción a la ESP32 por serial ---
        try:
            if ser.is_open:
                ser.write((emocion_detectada + '\n').encode('utf-8'))
                print(f"Enviando a ESP32: {emocion_detectada}")
            else:
                print("Error: Puerto serial no está abierto.")
        except Exception as e:
            print(f"Error enviando por serial: {e}")

        return jsonify({'emocion': emocion_detectada})
    except Exception as e:
        print(f"Error procesando imagen: {e}")
        return jsonify({'error': 'no se pudo procesar la imagen'}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
