from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import serial
import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging

# Librerías de reconocimiento facial
from deepface import DeepFace
import mediapipe as mp
from fer import FER

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# INICIALIZACIÓN FLASK
# ============================================================================
app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================
class Config:
    # Serial
    PUERTO_ESP32 = 'COM6'
    BAUD_RATE = 115200
    
    # Emociones
    EMOCIONES_PERMITIDAS = ["angry", "sad", "happy", "surprise"]
    CONFIANZA_MINIMA = 40  # Aumentado de 20 a 40
    BUFFER_SIZE = 5  # Aumentado de 3 a 5
    
    # Procesamiento de imagen
    IMG_WIDTH = 480  # Aumentado de 360
    IMG_HEIGHT = 360  # Aumentado de 240
    IMG_QUALITY = 0.85
    
    # Modelos
    DEEPFACE_MODEL = "Emotion"
    DEEPFACE_BACKEND = "retinaface"  # Mejor que opencv
    
    # Suavizado temporal
    ALPHA_SMOOTHING = 0.7

# Variables globales
locked = False
serial_lock = threading.Lock()
ser = None
executor = ThreadPoolExecutor(max_workers=3)

# Buffers y cache
emotion_buffer = deque(maxlen=Config.BUFFER_SIZE)
confidence_buffer = deque(maxlen=Config.BUFFER_SIZE)
ultima_emocion = None
ultima_confianza = 0
emotion_scores_history = {emo: deque(maxlen=5) for emo in Config.EMOCIONES_PERMITIDAS}

# ============================================================================
# INICIALIZACIÓN DE MODELOS
# ============================================================================
logger.info("🚀 Inicializando modelos de reconocimiento facial...")

# MediaPipe Face Detection (más rápido y preciso)
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
face_detection = mp_face_detection.FaceDetection(
    min_detection_confidence=0.7,
    model_selection=1
)

# FER con MTCNN
try:
    fer_detector = FER(mtcnn=True)
    logger.info("✅ FER inicializado con MTCNN")
except Exception as e:
    logger.warning(f"⚠️ Error inicializando FER con MTCNN: {e}")
    fer_detector = FER(mtcnn=False)

logger.info("✅ Modelos inicializados correctamente")

# ============================================================================
# INICIALIZACIÓN SERIAL
# ============================================================================
def inicializar_serial():
    """Inicializa la conexión serial con el ESP32"""
    global ser
    try:
        ser = serial.Serial(Config.PUERTO_ESP32, Config.BAUD_RATE, timeout=1)
        time.sleep(2)
        logger.info(f"✅ Puerto {Config.PUERTO_ESP32} abierto correctamente")
        return True
    except Exception as e:
        ser = None
        logger.error(f"⚠️ No se pudo abrir {Config.PUERTO_ESP32}: {e}")
        return False

inicializar_serial()

# ============================================================================
# PREPROCESAMIENTO DE IMAGEN
# ============================================================================
def preprocesar_imagen(frame):
    """
    Preprocesa la imagen con mejoras de calidad:
    - Redimensionamiento optimizado
    - Normalización de iluminación (CLAHE)
    - Corrección de color
    """
    if frame is None or frame.size == 0:
        return None
    
    try:
        # Convertir a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Redimensionar manteniendo aspect ratio
        height, width = frame_rgb.shape[:2]
        aspect_ratio = width / height
        
        if aspect_ratio > (Config.IMG_WIDTH / Config.IMG_HEIGHT):
            new_width = Config.IMG_WIDTH
            new_height = int(Config.IMG_WIDTH / aspect_ratio)
        else:
            new_height = Config.IMG_HEIGHT
            new_width = int(Config.IMG_HEIGHT * aspect_ratio)
        
        frame_resized = cv2.resize(frame_rgb, (new_width, new_height), 
                                   interpolation=cv2.INTER_LANCZOS4)
        
        # CLAHE para mejorar contraste (mejora detección en baja luz)
        lab = cv2.cvtColor(frame_resized, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        frame_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        return frame_enhanced
    
    except Exception as e:
        logger.error(f"❌ Error en preprocesamiento: {e}")
        return None

# ============================================================================
# DETECCIÓN DE ROSTRO CON MEDIAPIPE
# ============================================================================
def detectar_rostro_mediapipe(frame):
    """
    Detecta el rostro usando MediaPipe y retorna la región de interés (ROI)
    Esto mejora la precisión al enfocar solo en la cara
    """
    try:
        results = face_detection.process(frame)
        
        if not results.detections:
            return frame, False
        
        # Tomar la primera detección (rostro más prominente)
        detection = results.detections[0]
        bboxC = detection.location_data.relative_bounding_box
        
        h, w, _ = frame.shape
        x = int(bboxC.xmin * w)
        y = int(bboxC.ymin * h)
        width = int(bboxC.width * w)
        height = int(bboxC.height * h)
        
        # Expandir bounding box un 20% para contexto
        padding = 0.2
        x = max(0, int(x - width * padding / 2))
        y = max(0, int(y - height * padding / 2))
        width = int(width * (1 + padding))
        height = int(height * (1 + padding))
        
        # Extraer ROI
        roi = frame[y:y+height, x:x+width]
        
        return roi if roi.size > 0 else frame, True
    
    except Exception as e:
        logger.warning(f"⚠️ Error en detección MediaPipe: {e}")
        return frame, False

# ============================================================================
# DETECCIÓN CON DEEPFACE
# ============================================================================
def detectar_emocion_deepface(frame, resultado):
    """Detecta emociones usando DeepFace con backend mejorado"""
    try:
        res = DeepFace.analyze(
            frame,
            actions=['emotion'],
            detector_backend=Config.DEEPFACE_BACKEND,
            enforce_detection=False,
            silent=True
        )
        
        if isinstance(res, list):
            res = res[0]
        
        scores = res['emotion']
        
        # Filtrar solo emociones permitidas
        filtered_scores = {k: v for k, v in scores.items() 
                          if k.lower() in Config.EMOCIONES_PERMITIDAS}
        
        if not filtered_scores:
            resultado['deepface'] = ("neutral", 0, {})
            return
        
        emotion = max(filtered_scores, key=filtered_scores.get)
        conf = filtered_scores[emotion]
        
        resultado['deepface'] = (emotion.lower(), conf, filtered_scores)
        
    except Exception as e:
        logger.warning(f"⚠️ Error DeepFace: {e}")
        resultado['deepface'] = ("neutral", 0, {})

# ============================================================================
# DETECCIÓN CON FER
# ============================================================================
def detectar_emocion_fer(frame, resultado):
    """Detecta emociones usando FER"""
    try:
        # FER espera BGR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        result = fer_detector.detect_emotions(frame_bgr)
        
        if result and len(result) > 0:
            emociones = result[0]["emotions"]
            
            # Filtrar solo emociones permitidas
            filtered_emotions = {k: v for k, v in emociones.items() 
                                if k.lower() in Config.EMOCIONES_PERMITIDAS}
            
            if filtered_emotions:
                emotion = max(filtered_emotions, key=filtered_emotions.get)
                conf = filtered_emotions[emotion] * 100
                resultado['fer'] = (emotion.lower(), conf, filtered_emotions)
            else:
                resultado['fer'] = ("neutral", 0, {})
        else:
            resultado['fer'] = ("neutral", 0, {})
            
    except Exception as e:
        logger.warning(f"⚠️ Error FER: {e}")
        resultado['fer'] = ("neutral", 0, {})

# ============================================================================
# FUSIÓN AVANZADA DE EMOCIONES
# ============================================================================
def fusionar_emociones_avanzado(resultados):
    """
    Fusión inteligente de múltiples modelos con votación ponderada
    y suavizado temporal
    """
    # Extraer datos
    e1, c1, scores1 = resultados.get('deepface', ("neutral", 0, {}))
    e2, c2, scores2 = resultados.get('fer', ("neutral", 0, {}))
    
    # Si ambos detectan la misma emoción, aumentar confianza
    if e1 == e2 and e1 in Config.EMOCIONES_PERMITIDAS:
        confianza = (c1 + c2) / 2 * 1.2  # Bonus del 20%
        return e1, min(confianza, 100)
    
    # Votación ponderada por confianza
    emotion_votes = {}
    
    # Votos de DeepFace (peso 0.6)
    for emo, score in scores1.items():
        if emo.lower() in Config.EMOCIONES_PERMITIDAS:
            emotion_votes[emo.lower()] = emotion_votes.get(emo.lower(), 0) + score * 0.6
    
    # Votos de FER (peso 0.4)
    for emo, score in scores2.items():
        if emo.lower() in Config.EMOCIONES_PERMITIDAS:
            emotion_votes[emo.lower()] = emotion_votes.get(emo.lower(), 0) + (score * 100) * 0.4
    
    if not emotion_votes:
        return "neutral", 0
    
    # Obtener emoción con mayor votación
    emotion_final = max(emotion_votes, key=emotion_votes.get)
    confianza_final = emotion_votes[emotion_final] / 1.0  # Normalizar
    
    return emotion_final, confianza_final

# ============================================================================
# SUAVIZADO TEMPORAL
# ============================================================================
def aplicar_suavizado_temporal(emotion, confidence):
    """
    Aplica suavizado exponencial para evitar fluctuaciones
    """
    global ultima_emocion, ultima_confianza
    
    # Actualizar historial de scores
    if emotion in emotion_scores_history:
        emotion_scores_history[emotion].append(confidence)
    
    # Si es la misma emoción con confianza similar, mantener
    if ultima_emocion == emotion:
        if abs(confidence - ultima_confianza) < 15:
            return ultima_emocion, ultima_confianza
        
        # Suavizado exponencial
        confidence_suavizada = (Config.ALPHA_SMOOTHING * confidence + 
                               (1 - Config.ALPHA_SMOOTHING) * ultima_confianza)
        return emotion, confidence_suavizada
    
    return emotion, confidence

# ============================================================================
# DETECCIÓN FINAL CON PIPELINE COMPLETO
# ============================================================================
def detectar_emocion(frame):
    """
    Pipeline completo de detección con:
    1. Preprocesamiento mejorado
    2. Detección de rostro
    3. Análisis paralelo con múltiples modelos
    4. Fusión inteligente
    5. Suavizado temporal
    """
    global ultima_emocion, ultima_confianza
    
    # 1. Preprocesar imagen
    frame_processed = preprocesar_imagen(frame)
    if frame_processed is None:
        logger.error("❌ Error en preprocesamiento")
        return "neutral"
    
    # 2. Detectar rostro (opcional pero recomendado)
    frame_roi, face_detected = detectar_rostro_mediapipe(frame_processed)
    
    if not face_detected:
        logger.warning("⚠️ No se detectó rostro")
    
    # 3. Análisis paralelo con múltiples modelos
    resultado = {}
    
    futures = []
    futures.append(executor.submit(detectar_emocion_deepface, frame_roi, resultado))
    futures.append(executor.submit(detectar_emocion_fer, frame_roi, resultado))
    
    # Esperar a que terminen todos
    for future in futures:
        future.result()
    
    # 4. Fusión inteligente
    emotion_final, confianza_final = fusionar_emociones_avanzado(resultado)
    
    # 5. Verificar umbral mínimo
    if confianza_final < Config.CONFIANZA_MINIMA:
        emotion_final = "neutral"
        confianza_final = 0
    
    # 6. Aplicar suavizado temporal
    emotion_final, confianza_final = aplicar_suavizado_temporal(
        emotion_final, confianza_final
    )
    
    # 7. Buffer de votación (últimos N frames)
    emotion_buffer.append(emotion_final)
    confidence_buffer.append(confianza_final)
    
    if len(emotion_buffer) >= 3:
        # Votación por moda
        emotion_final = max(set(emotion_buffer), key=emotion_buffer.count)
        confianza_final = np.mean(list(confidence_buffer))
    
    # Actualizar estado
    ultima_emocion = emotion_final
    ultima_confianza = confianza_final
    
    # Log detallado
    e1, c1, _ = resultado.get('deepface', ("neutral", 0, {}))
    e2, c2, _ = resultado.get('fer', ("neutral", 0, {}))
    
    logger.info(
        f"🧠 DeepFace: {e1} ({c1:.1f}%) | "
        f"FER: {e2} ({c2:.1f}%) | "
        f"→ Final: {emotion_final} ({confianza_final:.1f}%)"
    )
    
    return emotion_final

# ============================================================================
# COMUNICACIÓN CON ESP32
# ============================================================================
def enviar_a_esp32(emocion):
    """Envía la emoción detectada al ESP32 vía serial"""
    global ser
    
    if ser is None or not ser.is_open:
        inicializar_serial()
    
    if ser and ser.is_open:
        with serial_lock:
            try:
                mensaje = f"{emocion}\n"
                ser.write(mensaje.encode('utf-8'))
                logger.info(f"✅ Enviado a ESP32: {emocion}")
            except Exception as e:
                logger.error(f"⚠️ Error enviando a ESP32: {e}")
                ser = None
    else:
        logger.warning("❌ Puerto serial no disponible")

# ============================================================================
# ENDPOINTS FLASK
# ============================================================================
@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servicio"""
    return jsonify({
        "status": "ok",
        "modelos": ["DeepFace", "FER", "MediaPipe"],
        "serial_conectado": ser is not None and ser.is_open
    })

@app.route('/lock', methods=['POST'])
def acquire_lock():
    """Adquiere el lock para uso exclusivo"""
    global locked
    if not locked:
        locked = True
        logger.info("🔒 Lock adquirido")
        return jsonify({"status": "ok"})
    else:
        logger.warning("⚠️ Intento de lock fallido - ya está en uso")
        return jsonify({"status": "locked"}), 423

@app.route('/unlock', methods=['POST'])
def release_lock():
    """Libera el lock"""
    global locked
    locked = False
    logger.info("🔓 Lock liberado")
    return jsonify({"status": "unlocked"})

@app.route('/emocion', methods=['POST'])
def emocion():
    """
    Endpoint principal para detección de emociones
    Recibe una imagen en base64 y retorna la emoción detectada
    """
    logger.info("📩 Petición de análisis recibida")
    
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        img_data = data.get('image', '')
        
        # Remover prefijo data:image si existe
        if ',' in img_data:
            img_data = img_data.split(",")[1]
        
        # Decodificar imagen
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'No se pudo decodificar la imagen'}), 400
        
        # Detectar emoción
        emocion_detectada = detectar_emocion(frame)
        
        # Enviar a ESP32
        enviar_a_esp32(emocion_detectada)
        
        return jsonify({
            'emocion': emocion_detectada,
            'confianza': float(ultima_confianza),
            'timestamp': time.time()
        })
    
    except Exception as e:
        logger.error(f"❌ Error procesando imagen: {e}", exc_info=True)
        return jsonify({'error': 'Error procesando la imagen'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Retorna estadísticas del sistema"""
    return jsonify({
        'ultima_emocion': ultima_emocion,
        'ultima_confianza': float(ultima_confianza) if ultima_confianza else 0,
        'buffer_size': len(emotion_buffer),
        'locked': locked
    })

# ============================================================================
# CLEANUP
# ============================================================================
def cleanup():
    """Limpieza de recursos al cerrar"""
    global ser
    if ser and ser.is_open:
        ser.close()
        logger.info("🔌 Puerto serial cerrado")
    
    executor.shutdown(wait=True)
    logger.info("👋 Sistema de reconocimiento cerrado")

import atexit
atexit.register(cleanup)

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    logger.info("🚀 Iniciando servidor de reconocimiento facial GESTICULINK v2.0")
    logger.info(f"📊 Configuración: {Config.EMOCIONES_PERMITIDAS}")
    logger.info(f"🎯 Confianza mínima: {Config.CONFIANZA_MINIMA}%")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True
    )