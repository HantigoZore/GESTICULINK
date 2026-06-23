from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import serial
import time
import threading
from collections import deque
import logging

# Librerías de reconocimiento facial
from deepface import DeepFace
from fer import FER

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# INICIALIZACIÓN FLASK
# ============================================================================
app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURACIÓN OPTIMIZADA
# ============================================================================
class Config:
    PUERTO_ESP32 = 'COM6'
    BAUD_RATE = 115200
    EMOCIONES_PERMITIDAS = ["angry", "sad", "happy", "surprise"]
    CONFIANZA_MINIMA = 35
    BUFFER_SIZE = 3
    IMG_WIDTH = 320  # Reducido para más velocidad
    IMG_HEIGHT = 240
    USE_CLAHE = False  # Desactivado para velocidad
    USE_FACE_DETECTION = False  # Desactivado para velocidad

# Variables globales
locked = False
serial_lock = threading.Lock()
ser = None
emotion_buffer = deque(maxlen=Config.BUFFER_SIZE)
ultima_emocion = None
ultima_confianza = 0
frame_count = 0

# ============================================================================
# INICIALIZACIÓN RÁPIDA DE MODELOS
# ============================================================================
logger.info("🚀 Inicializando modelos...")

# Solo FER (más rápido que DeepFace)
fer_detector = FER(mtcnn=False)  # MTCNN=False para más velocidad

# Cache para DeepFace (se usa solo como backup)
deepface_cache = {"enabled": True, "last_result": None}

logger.info("✅ Modelos listos")

# ============================================================================
# INICIALIZACIÓN SERIAL
# ============================================================================
def inicializar_serial():
    global ser
    try:
        ser = serial.Serial(Config.PUERTO_ESP32, Config.BAUD_RATE, timeout=1)
        time.sleep(1)
        logger.info(f"✅ Puerto {Config.PUERTO_ESP32} abierto")
        return True
    except Exception as e:
        ser = None
        logger.warning(f"⚠️ Serial no disponible: {e}")
        return False

inicializar_serial()

# ============================================================================
# PREPROCESAMIENTO RÁPIDO
# ============================================================================
def preprocesar_imagen_rapido(frame):
    """Preprocesamiento mínimo y rápido"""
    if frame is None or frame.size == 0:
        return None
    
    try:
        # Solo redimensionar (sin CLAHE ni correcciones)
        frame_resized = cv2.resize(frame, (Config.IMG_WIDTH, Config.IMG_HEIGHT), 
                                   interpolation=cv2.INTER_LINEAR)
        return frame_resized
    except Exception as e:
        logger.error(f"❌ Error preprocesamiento: {e}")
        return None

# ============================================================================
# DETECCIÓN ULTRA RÁPIDA CON FER
# ============================================================================
def detectar_emocion_fer_rapido(frame):
    """Detección con FER optimizado"""
    try:
        result = fer_detector.detect_emotions(frame)
        
        if result and len(result) > 0:
            emociones = result[0]["emotions"]
            
            # Filtrar solo emociones permitidas
            filtered = {k: v for k, v in emociones.items() 
                       if k in Config.EMOCIONES_PERMITIDAS}
            
            if filtered:
                emotion = max(filtered, key=filtered.get)
                conf = filtered[emotion] * 100
                return emotion, conf, filtered
        
        return "neutral", 0, {}
    except Exception as e:
        logger.warning(f"⚠️ Error FER: {e}")
        return "neutral", 0, {}

# ============================================================================
# DETECCIÓN DEEPFACE SOLO SI ES NECESARIO
# ============================================================================
def detectar_emocion_deepface_cache(frame):
    """DeepFace con cache - solo se usa si FER falla"""
    try:
        res = DeepFace.analyze(
            frame,
            actions=['emotion'],
            detector_backend='opencv',  # El más rápido
            enforce_detection=False,
            silent=True
        )
        
        if isinstance(res, list):
            res = res[0]
        
        scores = res['emotion']
        filtered = {k: v for k, v in scores.items() 
                   if k in Config.EMOCIONES_PERMITIDAS}
        
        if filtered:
            emotion = max(filtered, key=filtered.get)
            conf = filtered[emotion]
            return emotion, conf, filtered
        
        return "neutral", 0, {}
    except Exception as e:
        logger.warning(f"⚠️ Error DeepFace: {e}")
        return "neutral", 0, {}

# ============================================================================
# FUSIÓN SIMPLE Y RÁPIDA
# ============================================================================
def fusionar_simple(e1, c1, e2, c2):
    """Fusión simple basada en confianza"""
    # Si ambos coinciden, aumentar confianza
    if e1 == e2 and e1 in Config.EMOCIONES_PERMITIDAS:
        return e1, (c1 + c2) / 2
    
    # Retornar el de mayor confianza
    if c1 >= c2:
        return e1, c1
    else:
        return e2, c2

# ============================================================================
# PIPELINE DE DETECCIÓN OPTIMIZADO
# ============================================================================
def detectar_emocion(frame):
    """Pipeline optimizado para velocidad"""
    global ultima_emocion, ultima_confianza, frame_count
    
    frame_count += 1
    
    # 1. Preprocesamiento rápido
    frame_processed = preprocesar_imagen_rapido(frame)
    if frame_processed is None:
        return "neutral", 0, {}
    
    # 2. Detección con FER (principal y más rápido)
    e_fer, c_fer, scores_fer = detectar_emocion_fer_rapido(frame_processed)
    scores_finales = scores_fer
    
    # 3. Si FER tiene buena confianza, usar solo FER
    if c_fer >= Config.CONFIANZA_MINIMA:
        emotion_final = e_fer
        confianza_final = c_fer
    else:
        # 4. Solo si FER tiene baja confianza, usar DeepFace cada 2 frames
        if frame_count % 2 == 0:
            e_df, c_df, scores_df = detectar_emocion_deepface_cache(frame_processed)
            emotion_final, confianza_final = fusionar_simple(e_fer, c_fer, e_df, c_df)
            # Mezclar scores de ambos modelos
            if scores_df:
                scores_finales = {
                    k: (scores_fer.get(k, 0) + scores_df.get(k, 0)) / 2
                    for k in Config.EMOCIONES_PERMITIDAS
                }
        else:
            emotion_final = e_fer
            confianza_final = c_fer
    
    # 5. Verificar umbral
    if confianza_final < Config.CONFIANZA_MINIMA:
        emotion_final = "neutral"
    
    # 6. Buffer simple (sin suavizado complejo)
    emotion_buffer.append(emotion_final)
    
    if len(emotion_buffer) >= 2:
        # Votación simple por moda
        emotion_final = max(set(emotion_buffer), key=emotion_buffer.count)
    
    # 7. Evitar fluctuaciones innecesarias
    if ultima_emocion == emotion_final and abs(confianza_final - ultima_confianza) < 10:
        return ultima_emocion, ultima_confianza, scores_finales
    
    ultima_emocion = emotion_final
    ultima_confianza = confianza_final
    
    logger.info(f"🧠 Emoción: {emotion_final} ({confianza_final:.1f}%)")
    
    return emotion_final, confianza_final, scores_finales

# ============================================================================
# COMUNICACIÓN CON ESP32
# ============================================================================
def enviar_a_esp32(emocion):
    """Envía emoción al ESP32"""
    global ser
    
    if ser is None or not ser.is_open:
        inicializar_serial()
    
    if ser and ser.is_open:
        with serial_lock:
            try:
                ser.write(f"{emocion}\n".encode('utf-8'))
                logger.info(f"✅ → ESP32: {emocion}")
            except Exception as e:
                logger.error(f"⚠️ Error serial: {e}")
                ser = None

# ============================================================================
# ENDPOINTS FLASK
# ============================================================================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "serial": ser is not None and ser.is_open})

@app.route('/lock', methods=['POST'])
def acquire_lock():
    global locked
    if not locked:
        locked = True
        return jsonify({"status": "ok"})
    return jsonify({"status": "locked"}), 423

@app.route('/unlock', methods=['POST'])
def release_lock():
    global locked
    locked = False
    return jsonify({"status": "unlocked"})

@app.route('/emocion', methods=['POST'])
def emocion():
    """Endpoint principal optimizado"""
    start_time = time.time()
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image'}), 400
        
        img_data = data.get('image', '')
        
        if ',' in img_data:
            img_data = img_data.split(",")[1]
        
        # Decodificar
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Decode failed'}), 400
        
        # Detectar
        emocion_detectada, confianza_detectada, scores = detectar_emocion(frame)
        
        # Enviar a ESP32 en thread separado (no bloquear respuesta)
        threading.Thread(target=enviar_a_esp32, args=(emocion_detectada,), daemon=True).start()
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"⏱️ Tiempo: {elapsed:.0f}ms")
        
        # Normalizar scores a porcentaje (0-100)
        scores_pct = {k: round(float(v) * 100, 1) if v <= 1.0 else round(float(v), 1)
                      for k, v in scores.items()}
        
        return jsonify({
            'emocion': emocion_detectada,
            'confianza': float(confianza_detectada),
            'scores': scores_pct,
            'tiempo_ms': round(elapsed, 2)
        })
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Endpoint para ajustar configuración en tiempo real"""
    if request.method == 'POST':
        data = request.json
        if 'confianza_minima' in data:
            Config.CONFIANZA_MINIMA = int(data['confianza_minima'])
        if 'buffer_size' in data:
            Config.BUFFER_SIZE = int(data['buffer_size'])
        logger.info(f"⚙️ Config actualizada: {data}")
    
    return jsonify({
        'confianza_minima': Config.CONFIANZA_MINIMA,
        'buffer_size': Config.BUFFER_SIZE,
        'img_size': f"{Config.IMG_WIDTH}x{Config.IMG_HEIGHT}"
    })

# ============================================================================
# CLEANUP
# ============================================================================
def cleanup():
    global ser
    if ser and ser.is_open:
        ser.close()
    logger.info("👋 Sistema cerrado")

import atexit
atexit.register(cleanup)

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    logger.info("🚀 GESTICULINK v2.1 RÁPIDO")
    logger.info(f"🎯 Emociones: {Config.EMOCIONES_PERMITIDAS}")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True
    )