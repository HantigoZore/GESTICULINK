"""
Voice Assistant Module
Provides speech-to-text, text-to-speech, and AI conversation capabilities
"""
import os
import logging
import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class VoiceAssistant:
    """
    Voice assistant with AI integration
    """
    
    def __init__(self, use_openai=True, offline_mode=False):
        """
        Initialize voice assistant
        
        Args:
            use_openai: Whether to use OpenAI API for responses
            offline_mode: Use offline TTS and simple responses
        """
        self.use_openai = use_openai and not offline_mode
        self.offline_mode = offline_mode
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = None
        self._init_tts()
        
        # Initialize OpenAI if enabled
        self.openai_client = None
        if self.use_openai:
            self._init_openai()
        
        # Conversation history
        self.conversation_history = []
        
        logger.info("✅ Voice Assistant initialized")
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice properties
            self.tts_engine.setProperty('rate', 170)  # Speed
            self.tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            # Try to set a Spanish voice if available
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.languages:
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            logger.info("✅ TTS engine initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing TTS: {e}")
            self.tts_engine = None
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            logger.warning("⚠️ OPENAI_API_KEY not found. Using offline mode.")
            self.use_openai = False
            return
        
        try:
            self.openai_client = OpenAI(api_key=api_key)
            
            # Test the API with a simple request
            logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing OpenAI: {e}")
            self.use_openai = False
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """
        Listen for speech and convert to text
        
        Args:
            timeout: Seconds to wait for phrase to start
            phrase_time_limit: Maximum seconds for phrase
        
        Returns:
            Recognized text or None
        """
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                logger.info("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Recognize speech using Google Web Speech API
            logger.info("🧠 Processing speech...")
            text = self.recognizer.recognize_google(audio, language='es-ES')
            
            logger.info(f"📝 You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            logger.info("⏱️ No speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("⚠️ Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error during listening: {e}")
            return None
    
    def speak(self, text):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
        """
        logger.info(f"🔊 Speaking: {text}")
        
        if self.tts_engine is None:
            logger.warning("⚠️ TTS engine not available")
            return
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"❌ Error during speech: {e}")
    
    def get_ai_response(self, user_message, context=None):
        """
        Get AI response to user message
        
        Args:
            user_message: User's message
            context: Additional context (e.g., recognized person name)
        
        Returns:
            AI response text
        """
        if not self.use_openai or self.openai_client is None:
            # Use simple offline responses
            return self._get_offline_response(user_message, context)
        
        try:
            # Add user message to history
            if context:
                user_message = f"{context}\n{user_message}"
            
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente amigable y útil para un robot animatrónico llamado GESTICULINK. Responde de manera concisa y natural en español."
                    },
                    *self.conversation_history[-10:]  # Keep last 10 messages
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Error getting AI response: {e}")
            return self._get_offline_response(user_message, context)
    
    def _get_offline_response(self, user_message, context=None):
        """
        Get simple offline response
        
        Args:
            user_message: User's message
            context: Additional context
        
        Returns:
            Simple response text
        """
        user_message = user_message.lower()
        
        # Greeting with context
        if context and "reconocido" in context.lower():
            return context
        
        # Simple pattern matching
        if "hola" in user_message or "hey" in user_message:
            return "Hola, ¿cómo estás?"
        elif "como estas" in user_message or "cómo estás" in user_message:
            return "Estoy funcionando perfectamente, gracias por preguntar."
        elif "quien eres" in user_message or "quién eres" in user_message:
            return "Soy GESTICULINK, un robot animatrónico con reconocimiento facial."
        elif "quien soy" in user_message or "quién soy" in user_message:
            return "Por favor, mírame a la cámara para reconocerte."
        elif "gracias" in user_message:
            return "De nada, estoy aquí para ayudarte."
        elif "adios" in user_message or "adiós" in user_message or "chao" in user_message:
            return "Hasta luego, que tengas un buen día."
        elif "modo" in user_message:
            if "imitacion" in user_message or "imitación" in user_message:
                return "Activando modo de imitación de gestos."
            elif "voz" in user_message:
                return "Modo de voz activado."
        else:
            return "Entiendo. ¿Hay algo más en lo que pueda ayudarte?"
    
    def process_command(self, command, recognized_person=None):
        """
        Process a voice command
        
        Args:
            command: Voice command text
            recognized_person: Name of recognized person (if any)
        
        Returns:
            Response text and action dictionary
        """
        command = command.lower()
        
        # Create context
        context = None
        if recognized_person and recognized_person != "Unknown":
            context = f"La persona frente a la cámara es {recognized_person}."
        
        # Check for special commands
        action = {"type": "none"}
        
        if "quien soy" in command or "quién soy" in command:
            if recognized_person and recognized_person != "Unknown":
                response = f"Tú eres {recognized_person}."
            else:
                response = "No te reconozco. Por favor, asegúrate de estar registrado en el sistema."
            action = {"type": "identify"}
        
        elif "reconocimiento" in command or "reconocer" in command:
            response = "Activando reconocimiento facial continuo."
            action = {"type": "start_recognition"}
        
        elif "detener" in command or "parar" in command:
            response = "Deteniendo reconocimiento."
            action = {"type": "stop_recognition"}
        
        else:
            # Get AI or offline response
            response = self.get_ai_response(command, context)
            action = {"type": "conversation"}
        
        return response, action
    
    def greet_person(self, person_name):
        """
        Greet a recognized person
        
        Args:
            person_name: Name of the person
        
        Returns:
            Greeting text
        """
        if person_name == "Unknown":
            return "Hola, no te reconozco. ¿Quién eres?"
        else:
            return f"Hola {person_name}, es un gusto verte de nuevo."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
