import os
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import pyttsx3

# -------------------------
# Inicializar TTS (voz)
# -------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

def speak(text):
    print(f"[Robot]: {text}")
    engine.say(text)
    engine.runAndWait()

# -------------------------
# RUTA RELATIVA DEL MODELO
# -------------------------
# Carpeta donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Modelo en carpeta 'model/vosk-model-small-es-0.42' relativa al script
MODEL_DIR_NAME = "vosk-model-small-es-0.42"
MODEL_PATH = os.path.join(BASE_DIR, "model", MODEL_DIR_NAME)

# Evitar problemas con caracteres especiales en Windows
MODEL_PATH = os.path.normpath(MODEL_PATH)

# Verificar existencia del modelo
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en: {MODEL_PATH}")

print("Cargando modelo... (puede tardar unos segundos)")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

# -------------------------
# Inicializar micrófono
# -------------------------
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192)
stream.start_stream()

print("\nSistema listo. Habla...")

# -------------------------
# Bucle principal
# -------------------------
while True:
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()

        if text.strip() != "":
            print(f"▶ Dijiste: {text}")

            # -------------------------
            # Respuestas programadas
            # -------------------------
            if "hola" in text:
                speak("Hola, ¿cómo estás?")
            
            elif "como estas" in text:
                speak("Me encuentro muy bien, gracias por preguntar.")
            
            elif "modo imitacion" in text:
                speak("Activando modo imitación.")

            elif "modo voz" in text:
                speak("Activando modo voz.")
            
            elif "adios" in text or "chao" in text:
                speak("Hasta luego.")

            elif "gracias" in text:
                speak("Con gusto.")

            elif "prueba" in text:
                speak("Prueba de sistemas completada.")

            # Agrega más comandos si quieres:
            # elif "tu comando" in text:
            #     speak("tu respuesta")
