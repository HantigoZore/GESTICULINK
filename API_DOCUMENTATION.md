# 🔧 API Documentation

Documentación técnica para desarrolladores que desean integrar o extender GESTICULINK.

## Face Recognition Module

### FaceDetector

Detecta rostros en imágenes usando OpenCV DNN o Haar Cascades.

```python
from face_recognition_module import FaceDetector

# Inicializar detector
detector = FaceDetector(method='auto')  # 'dnn', 'haar', or 'auto'

# Detectar rostros
import cv2
image = cv2.imread('image.jpg')
faces = detector.detect_faces(image, confidence_threshold=0.5)

# faces es una lista de tuplas (x, y, w, h)
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
```

### FaceAligner

Alinea rostros usando landmarks faciales para mejorar precisión.

```python
from face_recognition_module import FaceAligner

aligner = FaceAligner()

# Alinear rostro
face_box = (x, y, w, h)  # De FaceDetector
aligned_face = aligner.align_face(image, face_box)

# Preprocesar (CLAHE + normalización)
preprocessed = aligner.preprocess_face(aligned_face)
```

### EncodingsManager

Gestiona la creación y almacenamiento de encodings faciales.

```python
from face_recognition_module import EncodingsManager

manager = EncodingsManager(encodings_path='models/encodings.pickle')

# Crear encodings desde directorio
data = manager.create_encodings_from_directory('dataset/', num_jitters=1)

# Guardar encodings
manager.save_encodings(data)

# Cargar encodings
manager.load_encodings()

# Obtener encodings
encodings, names = manager.get_encodings()
```

### FaceRecognizer

API completa para reconocimiento facial en tiempo real.

```python
from face_recognition_module import FaceRecognizer

# Inicializar reconocedor
recognizer = FaceRecognizer(
    encodings_path='models/encodings.pickle',
    tolerance=0.6,  # Menor = más estricto
    detection_method='auto'
)

# Reconocer rostros en imagen
results = recognizer.recognize_faces(image)

# results es una lista de diccionarios:
# [
#     {
#         'box': (x, y, w, h),
#         'name': 'Person Name',
#         'confidence': 0.95
#     },
#     ...
# ]

# Reconocer solo el rostro más grande
result = recognizer.recognize_largest_face(image)

# Dibujar resultados en imagen
output = recognizer.draw_results(image, results, show_confidence=True)

# Recargar encodings (si se agregaron nuevas personas)
recognizer.reload_encodings()
```

## Voice Assistant Module

### VoiceAssistant

Asistente de voz con STT, TTS, e integración de IA.

```python
from voice_assistant import VoiceAssistant

# Inicializar asistente
assistant = VoiceAssistant(
    use_openai=True,      # Usar OpenAI API
    offline_mode=False    # Modo offline
)

# Escuchar comando de voz
command = assistant.listen(timeout=5, phrase_time_limit=10)

# Hablar texto
assistant.speak("Hola, ¿cómo estás?")

# Obtener respuesta de IA
response = assistant.get_ai_response(
    user_message="¿Qué hora es?",
    context="Usuario reconocido: Juan"
)

# Procesar comando con acciones
response, action = assistant.process_command(
    command="¿Quién soy?",
    recognized_person="Juan Perez"
)
# action es un dict: {'type': 'identify'} o {'type': 'conversation'}

# Saludar persona
greeting = assistant.greet_person("Juan Perez")
assistant.speak(greeting)

# Limpiar historial de conversación
assistant.clear_history()
```

## Ejemplo de Integración Completa

```python
import cv2
from face_recognition_module import FaceRecognizer
from voice_assistant import VoiceAssistant

# Inicializar componentes
recognizer = FaceRecognizer()
assistant = VoiceAssistant(use_openai=True)

# Abrir cámara
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Reconocer rostros
    results = recognizer.recognize_faces(frame)
    
    # Si se reconoce alguien, saludar
    if results and results[0]['name'] != "Unknown":
        person_name = results[0]['name']
        greeting = assistant.greet_person(person_name)
        assistant.speak(greeting)
    
    # Dibujar resultados
    frame = recognizer.draw_results(frame, results)
    cv2.imshow('Frame', frame)
    
    # Interacción por voz al presionar ESPACIO
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        command = assistant.listen()
        if command:
            response, action = assistant.process_command(
                command, 
                results[0]['name'] if results else None
            )
            assistant.speak(response)
    
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Configuración Avanzada

### Ajustar Tolerancia de Reconocimiento

```python
# Más estricto (menos falsos positivos)
recognizer = FaceRecognizer(tolerance=0.4)

# Menos estricto (más flexible)
recognizer = FaceRecognizer(tolerance=0.7)

# Por defecto: 0.6 (balanceado)
```

### Cambiar Método de Detección

```python
# Usar solo DNN (más preciso, más lento)
recognizer = FaceRecognizer(detection_method='dnn')

# Usar solo Haar Cascade (más rápido, menos preciso)
recognizer = FaceRecognizer(detection_method='haar')

# Automático (intenta DNN, fallback a Haar)
recognizer = FaceRecognizer(detection_method='auto')
```

### Mejorar Encodings

```python
# Usar más jitters para mayor precisión (más lento)
data = manager.create_encodings_from_directory(
    'dataset/',
    num_jitters=10  # 1-10, default: 1
)
```

### Configurar Voz en Español

```python
# El asistente ya usa español por defecto
# Para cambiar idioma de reconocimiento:
text = recognizer.recognize_google(audio, language='es-ES')

# Configurar velocidad y volumen TTS
assistant.tts_engine.setProperty('rate', 170)  # Velocidad
assistant.tts_engine.setProperty('volume', 1.0)  # Volumen
```

## Manejo de Errores

```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

try:
    # Tu código aquí
    recognizer = FaceRecognizer()
    results = recognizer.recognize_faces(image)
except Exception as e:
    logging.error(f"Error: {e}")
```

## Variables de Entorno

```bash
# .env file
OPENAI_API_KEY=your_key_here
FACE_RECOGNITION_TOLERANCE=0.6
DETECTION_METHOD=auto
USE_OPENAI=true
TTS_RATE=170
TTS_VOLUME=1.0
```

Cargar en código:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
tolerance = float(os.getenv('FACE_RECOGNITION_TOLERANCE', 0.6))
```

## Performance Tips

### Optimizar para Video en Tiempo Real

```python
# Procesar cada N frames
frame_count = 0
recognition_interval = 5  # Procesar cada 5 frames

while True:
    ret, frame = cap.read()
    
    if frame_count % recognition_interval == 0:
        results = recognizer.recognize_faces(frame)
    
    # Dibujar resultados previos
    frame = recognizer.draw_results(frame, results)
    
    frame_count += 1
```

### Reducir Resolución

```python
# Reducir tamaño de frame para procesamiento más rápido
small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
results = recognizer.recognize_faces(small_frame)

# Ajustar coordenadas de vuelta
for result in results:
    x, y, w, h = result['box']
    result['box'] = (x*2, y*2, w*2, h*2)
```

## Extensión y Personalización

### Agregar Detector Personalizado

```python
# En detector.py, agregar nuevo método
class FaceDetector:
    def _load_custom_detector(self):
        # Tu implementación aquí
        pass
```

### Agregar Comandos de Voz Personalizados

```python
# En voice_assistant.py, extender process_command
def process_command(self, command, recognized_person=None):
    if "mi comando" in command:
        response = "Respuesta personalizada"
        action = {"type": "custom_action"}
        return response, action
    # ... resto del código
```

### Integrar con Otros Sistemas

```python
# Ejemplo: Enviar datos a servidor
import requests

results = recognizer.recognize_faces(frame)
if results:
    data = {
        'name': results[0]['name'],
        'confidence': results[0]['confidence']
    }
    requests.post('http://your-server.com/api/recognition', json=data)
```

## Testing

```python
# Test básico de reconocimiento
def test_recognition():
    recognizer = FaceRecognizer()
    image = cv2.imread('test_image.jpg')
    results = recognizer.recognize_faces(image)
    assert len(results) > 0
    assert 'name' in results[0]
    assert 'confidence' in results[0]

# Test de asistente de voz (mock)
def test_voice_assistant():
    assistant = VoiceAssistant(use_openai=False)
    response = assistant._get_offline_response("hola", None)
    assert response is not None
    assert isinstance(response, str)
```

## Recursos Adicionales

- [OpenCV Documentation](https://docs.opencv.org/)
- [face_recognition Library](https://github.com/ageitgey/face_recognition)
- [MediaPipe Docs](https://google.github.io/mediapipe/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [SpeechRecognition Docs](https://github.com/Uberi/speech_recognition)

## Soporte

Para problemas o preguntas:
1. Revisa la [documentación principal](README.md)
2. Consulta los [ejemplos](scripts/example_run.py)
3. Abre un [Issue en GitHub](https://github.com/estherlysuarez-ui/GESTICULINK/issues)
