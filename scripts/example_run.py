#!/usr/bin/env python3
"""
Example Run - Complete System Integration
Demonstrates facial recognition with voice interaction
"""
import sys
import os
import cv2
import argparse
import logging
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from face_recognition_module import FaceRecognizer
from voice_assistant import VoiceAssistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_integrated_system(camera_id=0, show_video=True, use_voice=True, use_openai=True):
    """
    Run the complete integrated system
    
    Args:
        camera_id: Camera device ID
        show_video: Whether to show video window
        use_voice: Whether to enable voice interaction
        use_openai: Whether to use OpenAI for conversations
    """
    logger.info("=" * 60)
    logger.info("GESTICULINK - Integrated Face Recognition & Voice System")
    logger.info("=" * 60)
    
    # Initialize face recognizer
    logger.info("Initializing face recognizer...")
    recognizer = FaceRecognizer()
    
    # Initialize voice assistant if enabled
    assistant = None
    if use_voice:
        logger.info("Initializing voice assistant...")
        assistant = VoiceAssistant(use_openai=use_openai)
    
    # Initialize camera
    logger.info(f"Opening camera {camera_id}...")
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        logger.error(f"❌ Could not open camera {camera_id}")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    logger.info("✅ System ready!")
    logger.info("")
    logger.info("Controls:")
    logger.info("  SPACE - Trigger voice interaction")
    logger.info("  G - Greet recognized person")
    logger.info("  R - Reload face encodings")
    logger.info("  Q/ESC - Quit")
    logger.info("")
    
    last_recognized_person = None
    last_greeting_time = 0
    greeting_cooldown = 10  # Seconds between automatic greetings
    
    frame_count = 0
    recognition_interval = 5  # Process every N frames for performance
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                logger.error("❌ Failed to read from camera")
                break
            
            # Process face recognition periodically
            results = []
            if frame_count % recognition_interval == 0:
                results = recognizer.recognize_faces(frame)
                
                # Check for new person recognition
                if results:
                    current_person = results[0]['name']
                    confidence = results[0]['confidence']
                    
                    # Auto-greet if it's a new person and cooldown expired
                    if (current_person != "Unknown" and 
                        current_person != last_recognized_person and
                        time.time() - last_greeting_time > greeting_cooldown and
                        assistant is not None):
                        
                        greeting = assistant.greet_person(current_person)
                        assistant.speak(greeting)
                        last_recognized_person = current_person
                        last_greeting_time = time.time()
                        logger.info(f"👋 Greeted: {current_person}")
            
            # Draw results if we have them
            if results and show_video:
                frame = recognizer.draw_results(frame, results)
            
            # Display video
            if show_video:
                # Add status text
                status = f"Frame: {frame_count} | People: {len(results)}"
                if results and results[0]['name'] != "Unknown":
                    status += f" | Recognized: {results[0]['name']}"
                
                cv2.putText(
                    frame,
                    status,
                    (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )
                
                cv2.imshow('GESTICULINK', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                logger.info("Quitting...")
                break
            
            elif key == ord(' '):  # SPACE - Voice interaction
                if assistant is None:
                    logger.warning("⚠️ Voice assistant not enabled")
                else:
                    logger.info("🎤 Listening for command...")
                    command = assistant.listen()
                    
                    if command:
                        # Get current recognized person
                        current_person = None
                        if results and results[0]['name'] != "Unknown":
                            current_person = results[0]['name']
                        
                        # Process command
                        response, action = assistant.process_command(command, current_person)
                        assistant.speak(response)
                        
                        # Handle actions
                        if action['type'] == 'stop_recognition':
                            break
            
            elif key == ord('g'):  # G - Greet
                if assistant is None:
                    logger.warning("⚠️ Voice assistant not enabled")
                elif not results:
                    logger.warning("⚠️ No person detected")
                else:
                    person_name = results[0]['name']
                    greeting = assistant.greet_person(person_name)
                    assistant.speak(greeting)
                    logger.info(f"👋 Greeted: {person_name}")
            
            elif key == ord('r'):  # R - Reload encodings
                logger.info("🔄 Reloading face encodings...")
                if recognizer.reload_encodings():
                    logger.info("✅ Encodings reloaded")
                else:
                    logger.warning("⚠️ Failed to reload encodings")
            
            frame_count += 1
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        logger.info("✅ System shutdown complete")


def main():
    parser = argparse.ArgumentParser(
        description='Run integrated face recognition and voice system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/example_run.py
  python scripts/example_run.py --no-voice
  python scripts/example_run.py --no-openai
  python scripts/example_run.py --camera 1

Controls:
  SPACE - Activate voice interaction
  G - Greet recognized person
  R - Reload face encodings
  Q/ESC - Quit

Requirements:
  1. Face encodings must be created first (run train_encodings.py)
  2. For OpenAI integration, set OPENAI_API_KEY environment variable
  3. Ensure camera is connected and accessible
        """
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device ID (default: 0)'
    )
    
    parser.add_argument(
        '--no-video',
        action='store_true',
        help='Disable video display (useful for headless systems)'
    )
    
    parser.add_argument(
        '--no-voice',
        action='store_true',
        help='Disable voice assistant'
    )
    
    parser.add_argument(
        '--no-openai',
        action='store_true',
        help='Disable OpenAI integration (use offline responses)'
    )
    
    args = parser.parse_args()
    
    run_integrated_system(
        camera_id=args.camera,
        show_video=not args.no_video,
        use_voice=not args.no_voice,
        use_openai=not args.no_openai
    )


if __name__ == '__main__':
    main()
