import cv2
from deepface import DeepFace
from flask import Flask, request, jsonify
import numpy as np
import base64
import serial

app = Flask(__name__)

emociones_permitidas = ["angry", "sad", "happy", "surprise"]
porcentaje_minimo = 10

# Configura el puerto COM correspondiente a tu ESP32
SERIAL_PORT = 'COM3'  # Cambia 'COM3' por el puerto que corresponda en tu PC
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except Exception as e:
    ser = None
    print(f"No se pudo abrir el puerto serial: {e}")

def enviar_emocion_bluetooth(emocion):
    if ser and ser.is_open:
        try:
            ser.write((emocion + '\n').encode())
        except Exception as e:
            print(f"Error enviando por Bluetooth: {e}")

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
        return "error"

@app.route('/emocion', methods=['POST'])
def emocion():
    data = request.json
    img_data = base64.b64decode(data['image'])
    np_arr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    emocion_detectada = detectar_emocion(frame)
    enviar_emocion_bluetooth(emocion_detectada)
    return jsonify({'emocion': emocion_detectada})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
