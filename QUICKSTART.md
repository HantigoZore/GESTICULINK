# 🚀 GESTICULINK - Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el sistema de reconocimiento facial y asistente de voz en minutos.

## ⚡ Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/estherlysuarez-ui/GESTICULINK.git
cd GESTICULINK

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Configurar OpenAI
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

## 🎯 Uso en 4 Pasos

### Paso 1: Verificar Hardware
```bash
# Probar cámara
python scripts/test_camera.py

# Probar micrófono
python scripts/test_microphone.py
```

### Paso 2: Capturar Rostros
```bash
# Capturar imágenes de personas a reconocer
python scripts/capture_faces.py --name "Tu Nombre" --images 20

# Repetir para cada persona
python scripts/capture_faces.py --name "Otra Persona" --images 20
```

**Consejos:**
- Usa buena iluminación
- Captura desde diferentes ángulos
- Varía las expresiones (neutral, sonriente)

### Paso 3: Entrenar el Sistema
```bash
# Generar encodings faciales
python scripts/train_encodings.py
```

### Paso 4: ¡Ejecutar!
```bash
# Sistema completo con voz e IA
python scripts/example_run.py

# O sin OpenAI (modo offline)
python scripts/example_run.py --no-openai
```

## 🎮 Controles

Durante la ejecución:
- **ESPACIO** - Activar interacción por voz
- **G** - Saludar a persona reconocida
- **R** - Recargar encodings
- **Q / ESC** - Salir

## 🗣️ Comandos de Voz

Presiona ESPACIO y di:
- "Hola" - Saludo
- "¿Quién soy?" - Identificación
- "¿Cómo estás?" - Conversación
- "Activar reconocimiento" - Modo continuo
- "Adiós" - Salir

## 🔧 Solución Rápida de Problemas

### No se abre la cámara
```bash
# Probar diferentes IDs
python scripts/test_camera.py --camera 1
```

### No reconoce rostros
```bash
# Verificar que entrenaste el sistema
python scripts/train_encodings.py

# Capturar más imágenes
python scripts/capture_faces.py --name "Nombre" --images 30
```

### Micrófono no funciona
```bash
# Verificar permisos del sistema
python scripts/test_microphone.py

# Instalar PyAudio (si falla)
# Windows: pip install pipwin && pipwin install pyaudio
# Linux: sudo apt-get install python3-pyaudio
```

### OpenAI no responde
```bash
# Usar modo offline
python scripts/example_run.py --no-openai

# Verificar clave API en .env
cat .env
```

## 📚 Documentación Completa

Para más información, consulta el [README.md](README.md) principal.

## 💡 Ejemplos de Uso

### Solo Reconocimiento Facial (sin voz)
```bash
python scripts/example_run.py --no-voice
```

### Modo Offline Completo
```bash
python scripts/example_run.py --no-openai
```

### Usando Cámara Externa
```bash
python scripts/example_run.py --camera 1
```

## 🆘 Soporte

Si tienes problemas:
1. Lee la [Solución de Problemas](README.md#-solución-de-problemas) en README.md
2. Abre un [Issue](https://github.com/estherlysuarez-ui/GESTICULINK/issues) en GitHub
3. Revisa los logs para más detalles

## 🎉 ¡Listo!

Ahora tienes GESTICULINK funcionando. Disfruta del reconocimiento facial y la interacción por voz con IA.

---

**Próximos Pasos:**
- Agregar más personas al sistema
- Experimentar con comandos de voz personalizados
- Integrar con el hardware ESP32
- Personalizar respuestas del asistente
