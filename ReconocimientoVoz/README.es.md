# Sistema de Conversación por Voz con IA

## 📌 Descripción

Este proyecto implementa un servidor en Python utilizando **Flask** que permite la comunicación entre una interfaz web y un modelo de inteligencia artificial (**Gemini 2.5 Flash**).

El sistema está diseñado para integrarse con un robot animatrónico (*HerlIA*), capaz de mantener conversaciones naturales por voz, adaptando sus respuestas según la emoción del usuario.

---

## ⚙️ Requisitos

* Python 3.8 o superior
* API Key de Gemini
* Conexión a internet

---

## 📦 Instalación

1. Clona el repositorio o copia los archivos
2. Instala las dependencias:

```bash
pip install flask flask-cors google-generativeai
```

3. Configura tu API Key:

**Opción A: Variable de entorno**

```bash
export GEMINI_API_KEY="tu_api_key"
```

**Opción B: archivo `.env`**

```env
GEMINI_API_KEY=tu_api_key
```

---

## 🚀 Ejecución

Ejecuta el servidor con:

```bash
python nombre_del_archivo.py
```

Servidor disponible en:
👉 [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 🔌 Endpoints

### 🧠 POST `/chat`

Envía un mensaje y recibe respuesta de la IA.

**Body:**

```json
{
  "user_id": "user1",
  "message": "Hola",
  "emocion": "happy"
}
```

---

### 🔄 POST `/reset`

Reinicia la conversación de un usuario.

---

### ❤️ GET `/health`

Estado del servidor.

---

### 📊 GET `/stats`

Estadísticas del sistema.

---

## 🧠 Funcionamiento

* Se mantiene una conversación por cada `user_id`
* Se usa un *system prompt* para definir la personalidad del robot
* Se considera la emoción del usuario para contextualizar
* Se detecta la emoción en la respuesta del modelo

---

## 🎭 Emociones soportadas

* happy
* sad
* angry
* surprise
* neutral

---

## ⚠️ Notas

* El servidor debe estar corriendo antes de abrir la web
* El frontend y backend deben estar en la misma red
* Las respuestas están optimizadas para voz (1–3 oraciones)

---

## 🧪 Logs

El sistema registra:

* Mensajes del usuario
* Respuestas del modelo
* Tokens utilizados
* Errores

---


