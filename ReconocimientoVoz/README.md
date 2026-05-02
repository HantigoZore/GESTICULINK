# AI Voice Conversation System

## 📌 Description

This project implements a Python server using **Flask** that enables communication between a web interface and an artificial intelligence model (**Gemini 2.5 Flash**).

The system is designed to integrate with an animatronic robot (*HerlIA*), capable of maintaining natural voice conversations and adapting responses based on user emotions.

---

## ⚙️ Requirements

* Python 3.8 or higher
* Gemini API Key
* Internet connection

---

## 📦 Installation

1. Clone the repository or copy the files
2. Install dependencies:

```bash
pip install flask flask-cors google-generativeai
```

3. Configure your API Key:

**Option A: Environment variable**

```bash
export GEMINI_API_KEY="your_api_key"
```

**Option B: `.env` file**

```env
GEMINI_API_KEY=your_api_key
```

---

## 🚀 Running

Run the server:

```bash
python your_file_name.py
```

Server available at:
👉 [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 🔌 Endpoints

### 🧠 POST `/chat`

Send a message and receive an AI response.

**Body:**

```json
{
  "user_id": "user1",
  "message": "Hello",
  "emocion": "happy"
}
```

---

### 🔄 POST `/reset`

Reset a user conversation.

---

### ❤️ GET `/health`

Server health status.

---

### 📊 GET `/stats`

System statistics.

---

## 🧠 How it works

* A conversation is maintained per `user_id`
* A system prompt defines the robot personality
* User emotion is used to contextualize responses
* The model response is analyzed to detect emotion

---

## 🎭 Supported emotions

* happy
* sad
* angry
* surprise
* neutral

---

## ⚠️ Notes

* The server must be running before using the web app
* Frontend and backend must be on the same network
* Responses are optimized for voice (1–3 sentences)

---

## 🧪 Logs

The system logs:

* User messages
* Model responses
* Token usage
* Errors

---

