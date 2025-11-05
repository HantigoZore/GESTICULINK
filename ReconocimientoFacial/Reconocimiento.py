from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import serial
import time
import threading
from collections import deque
from deepface import DeepFace
from fer import FER

# --- Inicialización Flask ---
app = Flask(__name__)
CORS(app)

# --- Variables globales ---
locked = False
serial_lock = threading.Lock()
PUERTO_ESP32 = 'COM6'
BAUD_RATE = 115200

# --- Inicialización de modelos ---
fer_detector = FER(mtcnn=True)
deepface_model = "Emotion"  # modelo ligero de emociones

# --- Configuración ---
emociones_permitidas = ["angry", "sad", "happy", "surprise"]
porcentaje_minimo = 20
emotion_buffer = deque(maxlen=3)
ultima_emocion = None
ultima_confianza = 0

# --- Inicializar puerto serial ---
def inicializar_serial():
    global ser
    try:
        ser = serial.Serial(PUERTO_ESP32, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"✅ Puerto {PUERTO_ESP32} abierto correctamente")
    except Exception as e:
        ser = None
        print(f"⚠️ No se pudo abrir {PUERTO_ESP32}: {e}")

inicializar_serial()

# --- Preprocesamiento rápido ---
def preprocesar_imagen(frame):
    if frame is None:
        return None
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (360, 240))  # más pequeño → más rápido
    return frame

# --- Detección DeepFace rápida ---
def detectar_emocion_deepface(frame, resultado):
    try:
        res = DeepFace.analyze(
            frame,
            actions=['emotion'],
            detector_backend='opencv',  # mucho más rápido
            enforce_detection=False,
            model_name=deepface_model
        )
        scores = res[0]['emotion']
        emotion = max(scores, key=scores.get)
        conf = scores[emotion]
        resultado['deepface'] = (emotion.lower(), conf)
    except Exception as e:
        print(f"⚠️ Error DeepFace: {e}")
        resultado['deepface'] = ("neutral", 0)

# --- Detección FER ---
def detectar_emocion_fer(frame, resultado):
    try:
        result = fer_detector.detect_emotions(frame)
        if result:
            emociones = result[0]["emotions"]
            emotion = max(emociones, key=emociones.get)
            conf = emociones[emotion] * 100
            resultado['fer'] = (emotion.lower(), conf)
        else:
            resultado['fer'] = ("neutral", 0)
    except Exception as e:
        print(f"⚠️ Error FER: {e}")
        resultado['fer'] = ("neutral", 0)

# --- Fusión ponderada ---
def fusionar_emociones(e1, c1, e2, c2):
    if e1 == e2:
        return e1
    if c1 > c2:
        return e1
    elif c2 > c1:
        return e2
    else:
        return "neutral"

# --- Detección final (paralela) ---
def detectar_emocion(frame):
    global ultima_emocion, ultima_confianza

    frame = preprocesar_imagen(frame)
    resultado = {}

    t1 = threading.Thread(target=detectar_emocion_deepface, args=(frame, resultado))
    t2 = threading.Thread(target=detectar_emocion_fer, args=(frame, resultado))

    t1.start(); t2.start()
    t1.join(); t2.join()

    e1, c1 = resultado.get('deepface', ("neutral", 0))
    e2, c2 = resultado.get('fer', ("neutral", 0))

    emotion_final = fusionar_emociones(e1, c1, e2, c2)
    confianza_final = max(c1, c2)

    if emotion_final not in emociones_permitidas or confianza_final < porcentaje_minimo:
        emotion_final = "neutral"

    # Evita fluctuaciones innecesarias
    if ultima_emocion == emotion_final and abs(confianza_final - ultima_confianza) < 10:
        return ultima_emocion

    emotion_buffer.append(emotion_final)
    if len(emotion_buffer) >= 2:
        emotion_final = max(set(emotion_buffer), key=emotion_buffer.count)

    ultima_emocion, ultima_confianza = emotion_final, confianza_final

    print(f"🧠 DeepFace: {e1} ({c1:.1f}%) | FER: {e2} ({c2:.1f}%) → Final: {emotion_final}")
    return emotion_final

# --- Comunicación con ESP32 ---
def enviar_a_esp32(emocion):
    global ser
    if ser is None or not ser.is_open:
        inicializar_serial()

    if ser and ser.is_open:
        with serial_lock:
            try:
                ser.write((emocion + "\n").encode('utf-8'))
                print(f"✅ Enviado a ESP32: {emocion}")
            except Exception as e:
                print(f"⚠️ Error enviando a ESP32: {e}")
    else:
        print("❌ Puerto serial no disponible")

# --- Endpoints Flask ---
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

@app.route('/emocion', methods=['POST'])
def emocion():
    print("📩 Petición recibida")
    data = request.json
    img_data = data.get('image', '')

    if ',' in img_data:
        img_data = img_data.split(",")[1]

    try:
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        emocion_detectada = detectar_emocion(frame)
        enviar_a_esp32(emocion_detectada)

        return jsonify({'emocion': emocion_detectada})
    except Exception as e:
        print(f"❌ Error procesando imagen: {e}")
        return jsonify({'error': 'no se pudo procesar la imagen'}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
