"""
GESTICULINK - Sistema de Conversación por Voz con IA
Usando Gemini 2.5 Flash (Verificado funcionando)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURACIÓN DE GEMINI
# ============================================================================
def load_gemini_api_key():
    """Carga la API key desde env vars o un archivo .env local."""
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key.strip()

    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                if not line or line.strip().startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                if name.strip() == "GEMINI_API_KEY":
                    return value.strip().strip('"').strip("'")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo leer .env: {e}")

    return "TU_API_KEY_AQUI"


GEMINI_API_KEY = load_gemini_api_key()

if GEMINI_API_KEY and GEMINI_API_KEY != "TU_API_KEY_AQUI":
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("🔑 API Key cargada correctamente (env/.env)")
else:
    logger.warning("⚠️ GEMINI_API_KEY no configurada. Define la variable de entorno o el archivo .env")

# ✅ Modelo verificado funcionando
MODEL = "gemini-2.5-flash"

try:
    model = genai.GenerativeModel(
        MODEL,
        generation_config={
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 500,
        },
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    )
    logger.info(f"✅ Modelo inicializado: {MODEL}")
except Exception as e:
    logger.error(f"❌ Error inicializando modelo: {e}")
    model = None

# Sistema de personalidad para tu robot
SYSTEM_PROMPT = """Eres HerlIA, un robot animatrónico amigable del proyecto GESTICULINK. 
Tu función es conversar de manera natural, empática y breve. 
Mantén respuestas cortas (1-3 oraciones máximo) para conversaciones fluidas por voz.
Puedes expresar emociones: feliz (happy), triste (sad), enojado (angry) o sorprendido (surprise).
Sé cercano, divertido, útil y adapta tu tono a la emoción del usuario.
Responde SIEMPRE en español."""

# Almacenar conversaciones por usuario
conversations = {}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal para conversación"""
    if model is None:
        return jsonify({'error': 'Modelo no inicializado'}), 500
    
    try:
        data = request.json
        user_id = data.get('user_id', 'default')
        message = data.get('message', '')
        emocion_actual = data.get('emocion', 'neutral')
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Inicializar conversación si no existe
        if user_id not in conversations:
            conversations[user_id] = model.start_chat(history=[])
            # Mensaje del sistema
            try:
                conversations[user_id].send_message(SYSTEM_PROMPT)
                logger.info(f"🤖 Conversación iniciada para {user_id}")
            except Exception as e:
                logger.warning(f"⚠️ Sistema prompt error: {e}")
        
        chat_session = conversations[user_id]
        
        # Agregar contexto emocional
        emociones_descripcion = {
            'happy': 'feliz y animado',
            'sad': 'triste o desanimado',
            'angry': 'molesto o frustrado',
            'surprise': 'sorprendido',
            'neutral': 'neutral'
        }
        
        if emocion_actual in emociones_descripcion and emocion_actual != 'neutral':
            contexto = f"[El usuario se ve {emociones_descripcion[emocion_actual]}]\n{message}"
        else:
            contexto = message
        
        # Enviar mensaje y obtener respuesta
        logger.info(f"👤 {user_id}: {message} [emoción: {emocion_actual}]")
        
        response = chat_session.send_message(contexto)
        respuesta_texto = response.text
        
        # Analizar emoción sugerida para el robot
        emocion_robot = detectar_emocion_respuesta(respuesta_texto)
        
        # Logging con metadata de uso
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            u = response.usage_metadata
            logger.info(
                f"🤖 HerlIA: {respuesta_texto[:50]}... "
                f"[emoción: {emocion_robot}] "
                f"[tokens: {u.total_token_count}]"
            )
        else:
            logger.info(f"🤖 HerlIA: {respuesta_texto} [emoción: {emocion_robot}]")
        
        return jsonify({
            'respuesta': respuesta_texto,
            'emocion_robot': emocion_robot,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'modelo': MODEL
        })
    
    except Exception as e:
        logger.error(f"❌ Error en chat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reinicia la conversación de un usuario"""
    data = request.json
    user_id = data.get('user_id', 'default')
    
    if user_id in conversations:
        del conversations[user_id]
        logger.info(f"🔄 Conversación reiniciada para {user_id}")
        return jsonify({'status': 'reset', 'user_id': user_id})
    else:
        return jsonify({'status': 'no_conversation', 'user_id': user_id})

@app.route('/health', methods=['GET'])
def health():
    """Check de salud del servicio"""
    return jsonify({
        'status': 'ok' if model else 'error',
        'model': MODEL,
        'active_conversations': len(conversations),
        'api_configured': GEMINI_API_KEY != "TU_API_KEY_AQUI"
    })

@app.route('/stats', methods=['GET'])
def stats():
    """Estadísticas del sistema"""
    return jsonify({
        'modelo': MODEL,
        'conversaciones_activas': len(conversations),
        'usuarios': list(conversations.keys())
    })

# ============================================================================
# UTILIDADES
# ============================================================================

def detectar_emocion_respuesta(texto):
    """Analiza el texto de respuesta para sugerir una emoción al robot"""
    texto_lower = texto.lower()
    
    # Patrones específicos para cada emoción
    emociones = {
        'happy': [
            'feliz', 'alegr', 'genial', 'excelente', 'maravilloso', 
            'jaja', 'jeje', 'super', 'increíble', 'fantástico', 
            'estupendo', 'perfecto', 'encant', 'divertido',
            'me alegr', 'qué bien', 'qué bueno', 'me gusta',
            '😊', '😄', '🎉', '✨'
        ],
        'sad': [
            'triste', 'lament', 'pena', 'sentir mal', 'desafortunado', 
            'difícil', 'complicado', 'duro', 'siento mucho',
            'lo siento', 'qué mal', 'qué pena', 'desgracia',
            'perdón', 'disculpa',
            '😢', '😞', '😔'
        ],
        'surprise': [
            'sorprend', 'wow', 'increíble', 'asombr', 'impresionante',
            'vaya', 'guau', 'caramba', 'inesperado', 'en serio',
            'no sabía', 'no me esperaba', 'qué sorpresa',
            '😮', '😲', '🤯'
        ],
        'angry': [
            'enoj', 'molest', 'frustrant', 'terrible', 'horrible',
            'irritante', 'fastidioso', 'odio', 'rabia',
            'no puedo creer', 'maldito', 'mal hecho',
            '😠', '😡', '🤬'
        ]
    }
    
    scores = {emo: 0 for emo in emociones}
    
    # Contar coincidencias con peso por posición
    for emocion, keywords in emociones.items():
        for keyword in keywords:
            if keyword in texto_lower:
                # Más peso si aparece al inicio
                pos = texto_lower.find(keyword)
                if pos < 30:
                    scores[emocion] += 2
                else:
                    scores[emocion] += 1
    
    # Retornar emoción con mayor score
    max_emocion = max(scores, key=scores.get)
    
    # Solo retornar si hay suficiente confianza
    if scores[max_emocion] >= 1:
        return max_emocion
    
    return 'neutral'

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🤖 GESTICULINK - Sistema de Conversación IA")
    print("=" * 70)
    
    if model:
        print(f"✅ Modelo: {MODEL}")
        print(f"🔑 API Key configurada: ...{GEMINI_API_KEY[-20:]}")
    else:
        print("❌ Error: Modelo no inicializado")
    
    print(f"🌐 Servidor: http://127.0.0.1:5001")
    print(f"🎤 Endpoints disponibles:")
    print(f"   - POST /chat      → Conversación")
    print(f"   - POST /reset     → Reiniciar chat")
    print(f"   - GET  /health    → Estado del servicio")
    print(f"   - GET  /stats     → Estadísticas")
    print("=" * 70)
    
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)