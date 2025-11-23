<p align="center">
  <img src="PaginaWeb/assets/images/LogoSinFondo.png" alt="GESTICULINK Logo" width="200"/>
</p>

# GESTICULINK

**Cabeza Animatrónica GESTICULINK**  
Repositorio oficial del proyecto GESTICULINK, un sistema capaz de imitar gestos humanos en tiempo real mediante el uso de microcontroladores, reconocimiento facial y una interfaz web.

> 🚀 **[Ver Guía de Inicio Rápido](QUICKSTART.md)** para empezar en minutos

---

## 📂 Estructura del Repositorio

El repositorio está organizado en carpetas principales:

- **[Microcontrolador](/Microcontrolador)** → Códigos para el control del hardware y la animatrónica
- **[ReconocimientoFacial](/ReconocimientoFacial)** → Sistema de detección de gestos y expresiones faciales (DeepFace/FER)
- **[face_recognition_module](/face_recognition_module)** → **NUEVO:** Sistema avanzado de reconocimiento e identificación facial
- **[voice_assistant](/voice_assistant)** → **NUEVO:** Asistente de voz con integración de IA
- **[PaginaWeb](/PaginaWeb)** → Interfaz web para monitoreo y control
- **[scripts](/scripts)** → Scripts de utilidad para entrenamiento y pruebas

---

## 🚀 Características

### Características Principales
- ✅ **Reconocimiento Facial Avanzado**: Identifica personas por nombre usando encodings faciales
- ✅ **Detección de Emociones**: Detecta gestos y expresiones faciales en tiempo real
- ✅ **Asistente de Voz con IA**: Interacción por voz con integración de OpenAI
- ✅ **Saludo Automático**: Reconoce y saluda a personas conocidas
- ✅ **Preprocesamiento Robusto**: CLAHE, alineación facial, y normalización
- ✅ **Múltiples Detectores**: OpenCV DNN, Haar Cascades, MediaPipe
- ✅ **Integración de Hardware**: Comunicación con microcontrolador ESP32
- ✅ **Interfaz Web**: Visualización y control en tiempo real

### Tecnologías Utilizadas
- **Visión por Computadora**: OpenCV, face_recognition, MediaPipe, DeepFace, FER
- **Voz e IA**: SpeechRecognition, pyttsx3, gTTS, OpenAI GPT
- **Backend**: Flask, Python
- **Hardware**: ESP32, Servomotores

---

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- Cámara web (para reconocimiento facial)
- Micrófono (para interacción por voz)
- Sistema operativo: Windows, Linux, o macOS

### Instalación Paso a Paso

1. **Clonar el repositorio**
```bash
git clone https://github.com/estherlysuarez-ui/GESTICULINK.git
cd GESTICULINK
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

**Nota sobre dlib**: Si la instalación de `dlib` falla:
- **Windows**: Descargar wheel precompilado desde [aquí](https://github.com/z-mahmud22/Dlib_Windows_Python3.x)
- **Linux**: `sudo apt-get install build-essential cmake`
- **Alternativa**: El sistema funciona con MediaPipe sin dlib

4. **Configurar variables de entorno** (opcional, para IA)

Crear archivo `.env` en la raíz del proyecto:
```bash
OPENAI_API_KEY=tu_clave_api_aqui
```

Para obtener una clave de OpenAI:
- Visita https://platform.openai.com/api-keys
- Crea una cuenta y genera una API key
- **Nota**: El sistema funciona sin OpenAI usando respuestas offline

5. **Descargar modelos DNN** (opcional, para mejor detección)

El sistema usa Haar Cascades por defecto. Para mejor precisión, descarga:
- [deploy.prototxt](https://github.com/opencv/opencv/blob/master/samples/dnn/face_detector/deploy.prototxt)
- [res10_300x300_ssd_iter_140000.caffemodel](https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel)

Guárdalos en `models/`

---

## 🎯 Guía de Uso

### Paso 1: Verificar Hardware

**Probar cámara:**
```bash
python scripts/test_camera.py
```

**Probar micrófono:**
```bash
python scripts/test_microphone.py
```

### Paso 2: Crear Dataset de Rostros

Captura imágenes de las personas que deseas reconocer:

```bash
python scripts/capture_faces.py --name "Juan Perez" --images 20
python scripts/capture_faces.py --name "Maria Garcia" --images 20
```

**Tips para mejores resultados:**
- ✅ Buena iluminación (luz natural preferible)
- ✅ Capturar desde diferentes ángulos (frontal, ligeramente girado)
- ✅ Diferentes expresiones (neutral, sonriente)
- ✅ Diferentes distancias
- ✅ Sin accesorios que oculten el rostro
- ✅ Fondo limpio y sin distracciones

Las imágenes se guardan en `dataset/nombre_persona/`

### Paso 3: Entrenar el Sistema

Genera los encodings faciales:

```bash
python scripts/train_encodings.py
```

Para mayor precisión (tarda más):
```bash
python scripts/train_encodings.py --jitters 5
```

Los encodings se guardan en `models/encodings.pickle`

### Paso 4: Ejecutar el Sistema Completo

**Con todas las funcionalidades:**
```bash
python scripts/example_run.py
```

**Sin OpenAI (modo offline):**
```bash
python scripts/example_run.py --no-openai
```

**Solo reconocimiento facial (sin voz):**
```bash
python scripts/example_run.py --no-voice
```

**Controles durante la ejecución:**
- `ESPACIO` - Activar interacción por voz
- `G` - Saludar a la persona reconocida
- `R` - Recargar encodings (si agregaste nuevas personas)
- `Q` o `ESC` - Salir

### Paso 5: Comandos de Voz

Una vez ejecutando el sistema, presiona `ESPACIO` y di:

- **"Hola"** - Saludo básico
- **"¿Quién soy?"** - Identificación facial
- **"¿Cómo estás?"** - Conversación
- **"Activar reconocimiento"** - Iniciar modo continuo
- **"Detener"** - Parar reconocimiento
- **"Adiós"** - Despedida

Con OpenAI habilitado, puedes hacer preguntas más complejas.

---

## 🔧 Calibración y Ajuste Fino

### Ajustar Sensibilidad del Reconocimiento

Edita los parámetros en tu script:

```python
recognizer = FaceRecognizer(
    tolerance=0.6  # Valor más bajo = más estricto (0.4-0.7 recomendado)
)
```

### Mejorar Precisión

1. **Capturar más imágenes**: 30-50 por persona
2. **Usar num_jitters más alto**: 5-10 para producción
3. **Variar condiciones**: Diferentes iluminaciones, ángulos, expresiones
4. **Recapturar rostros**: Si la precisión es baja, recaptura con mejor calidad

### Optimización de Rendimiento

Para sistemas más lentos:
- Reduce `recognition_interval` en example_run.py
- Usa `detection_method='haar'` en lugar de 'dnn'
- Desactiva la alineación facial

---

## 📊 Estructura de Archivos

```
GESTICULINK/
├── face_recognition_module/     # Módulo de reconocimiento facial
│   ├── detector.py             # Detección de rostros
│   ├── align.py                # Alineación facial
│   ├── encodings_manager.py    # Gestión de encodings
│   └── recognizer.py           # API principal
├── voice_assistant/             # Asistente de voz
│   └── voice_assistant.py      # STT, TTS, y conversación IA
├── scripts/                     # Scripts de utilidad
│   ├── capture_faces.py        # Captura de rostros
│   ├── train_encodings.py      # Entrenamiento
│   ├── example_run.py          # Demostración completa
│   ├── test_camera.py          # Test de cámara
│   └── test_microphone.py      # Test de micrófono
├── models/                      # Modelos y encodings (no en git)
│   └── encodings.pickle        # Encodings faciales
├── dataset/                     # Imágenes de entrenamiento (no en git)
│   ├── persona1/
│   └── persona2/
├── ReconocimientoFacial/        # Sistema de emociones (existente)
├── requirements.txt             # Dependencias Python
└── README.md                    # Esta documentación
```

---

## ⚙️ Soporte para GPU

Para mejor rendimiento (opcional):

**dlib con CUDA:**
```bash
# Requiere CUDA Toolkit instalado
pip install dlib --install-option="--yes" --install-option="USE_AVX_INSTRUCTIONS"
```

**OpenCV con CUDA:**
- Compilar OpenCV con soporte CUDA
- El detector DNN automáticamente usará GPU si está disponible

---

## 🐛 Solución de Problemas

### Error: "No se pudo abrir la cámara"
- Verifica que la cámara esté conectada
- Prueba diferentes IDs: `--camera 1`, `--camera 2`
- Cierra otras aplicaciones que usen la cámara

### Error: "No face encodings found"
- Ejecuta `train_encodings.py` primero
- Verifica que existan imágenes en `dataset/`
- Asegúrate de que las imágenes contengan rostros

### Reconocimiento incorrecto
- Captura más imágenes de la persona
- Mejora la iluminación durante captura y reconocimiento
- Aumenta `num_jitters` al entrenar
- Reduce `tolerance` para ser más estricto

### Error con micrófono
- Verifica permisos de micrófono en sistema operativo
- Prueba con `test_microphone.py`
- Instala PyAudio correctamente (puede requerir dependencias del sistema)

### OpenAI no funciona
- Verifica que `OPENAI_API_KEY` esté configurada
- Comprueba conexión a internet
- Usa `--no-openai` para modo offline

---

## 📌 Estado de la Rama

Esta rama incluye la **primera versión** con:

* Incorporación de la página web.
* Integración del sistema de reconocimiento facial.

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Puedes abrir un **issue** para reportar problemas o proponer mejoras, y enviar un **pull request** con tus cambios.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.
Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🌐 English

Si prefieres leer en inglés, revisa la versión en inglés: [README.en.md](README.en.md)
