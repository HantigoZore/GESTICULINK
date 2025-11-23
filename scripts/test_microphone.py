#!/usr/bin/env python3
"""
Microphone Test Script
Tests microphone and speech recognition functionality
"""
import logging
import speech_recognition as sr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_microphone():
    """Test microphone and speech recognition"""
    logger.info("=" * 60)
    logger.info("Microphone Test")
    logger.info("=" * 60)
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # List available microphones
    logger.info("Available microphones:")
    mic_list = sr.Microphone.list_microphone_names()
    for i, mic_name in enumerate(mic_list):
        logger.info(f"  [{i}] {mic_name}")
    
    logger.info("")
    
    # Test default microphone
    try:
        mic = sr.Microphone()
        logger.info("✅ Default microphone initialized")
    except Exception as e:
        logger.error(f"❌ Could not initialize microphone: {e}")
        logger.info("Troubleshooting:")
        logger.info("  - Check if microphone is connected")
        logger.info("  - Check system audio settings")
        logger.info("  - Try a different microphone")
        return False
    
    logger.info("")
    logger.info("Testing ambient noise adjustment...")
    
    try:
        with mic as source:
            logger.info("Adjusting for ambient noise... (please wait)")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            logger.info(f"✅ Ambient noise threshold: {recognizer.energy_threshold}")
    except Exception as e:
        logger.error(f"❌ Error adjusting for ambient noise: {e}")
        return False
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Speech Recognition Test")
    logger.info("=" * 60)
    logger.info("Say something in Spanish...")
    logger.info("(or press Ctrl+C to skip)")
    logger.info("")
    
    success_count = 0
    attempts = 0
    
    # Try 3 times
    for i in range(3):
        attempts += 1
        logger.info(f"Attempt {attempts}/3:")
        
        try:
            with mic as source:
                logger.info("🎤 Listening... (5 second timeout)")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            logger.info("🧠 Processing speech...")
            
            # Try Google Web Speech API
            try:
                text = recognizer.recognize_google(audio, language='es-ES')
                logger.info(f"✅ Recognized: '{text}'")
                success_count += 1
            except sr.UnknownValueError:
                logger.warning("⚠️ Could not understand audio")
            except sr.RequestError as e:
                logger.error(f"❌ API error: {e}")
                logger.info("Note: Internet connection required for Google Web Speech API")
        
        except sr.WaitTimeoutError:
            logger.info("⏱️ No speech detected (timeout)")
        except KeyboardInterrupt:
            logger.info("\nTest interrupted by user")
            break
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Microphones found: {len(mic_list)}")
    logger.info(f"Speech recognition attempts: {attempts}")
    logger.info(f"Successful recognitions: {success_count}")
    
    if success_count > 0:
        logger.info("✅ Microphone and speech recognition working!")
    elif attempts > 0:
        logger.info("⚠️ Microphone works but speech recognition had issues")
        logger.info("Troubleshooting:")
        logger.info("  - Speak clearly and closer to microphone")
        logger.info("  - Check internet connection (required for Google API)")
        logger.info("  - Reduce background noise")
        logger.info("  - Ensure language is set to Spanish")
    
    return success_count > 0


def main():
    try:
        test_microphone()
    except KeyboardInterrupt:
        logger.info("\nTest cancelled by user")


if __name__ == '__main__':
    main()
