#!/usr/bin/env python3
"""
Face Capture Script
Captures face images for training the recognition system
"""
import cv2
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def capture_faces(person_name, output_dir='dataset', num_images=20, camera_id=0):
    """
    Capture face images for a person
    
    Args:
        person_name: Name of the person
        output_dir: Base directory to save images
        num_images: Number of images to capture
        camera_id: Camera device ID
    """
    # Create person directory
    person_dir = os.path.join(output_dir, person_name)
    os.makedirs(person_dir, exist_ok=True)
    
    # Initialize camera
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        logger.error(f"❌ Could not open camera {camera_id}")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    count = 0
    captured = 0
    
    logger.info(f"📷 Starting face capture for: {person_name}")
    logger.info(f"Target: {num_images} images")
    logger.info("Press SPACE to capture, ESC to quit")
    
    while captured < num_images:
        ret, frame = cap.read()
        
        if not ret:
            logger.error("❌ Failed to read from camera")
            break
        
        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        # Draw rectangles around faces
        display_frame = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                display_frame,
                f"Face Detected",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        # Display capture status
        status_text = f"Captured: {captured}/{num_images} | Press SPACE to capture"
        cv2.putText(
            display_frame,
            status_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        cv2.imshow('Face Capture', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Capture on SPACE
        if key == ord(' '):
            if len(faces) == 0:
                logger.warning("⚠️ No face detected! Please position your face in the frame.")
            elif len(faces) > 1:
                logger.warning("⚠️ Multiple faces detected! Please ensure only one person is in frame.")
            else:
                # Save the captured frame
                filename = f"{person_name}_{captured:03d}.jpg"
                filepath = os.path.join(person_dir, filename)
                cv2.imwrite(filepath, frame)
                captured += 1
                logger.info(f"✅ Captured {captured}/{num_images}: {filename}")
        
        # Quit on ESC
        elif key == 27:
            logger.info("Capture cancelled by user")
            break
        
        count += 1
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    logger.info(f"✅ Capture complete! Saved {captured} images to {person_dir}")
    logger.info(f"Next step: Run 'python scripts/train_encodings.py' to create encodings")


def main():
    parser = argparse.ArgumentParser(
        description='Capture face images for training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/capture_faces.py --name "John Doe" --images 30
  python scripts/capture_faces.py --name "Jane Smith" --camera 1

Tips for best results:
  - Use good lighting (natural light is best)
  - Capture from different angles (front, slight left, slight right)
  - Use different expressions (neutral, smiling)
  - Ensure face is clearly visible
  - Capture at different distances
        """
    )
    
    parser.add_argument(
        '--name',
        type=str,
        required=True,
        help='Name of the person'
    )
    
    parser.add_argument(
        '--images',
        type=int,
        default=20,
        help='Number of images to capture (default: 20)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='dataset',
        help='Output directory (default: dataset)'
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device ID (default: 0)'
    )
    
    args = parser.parse_args()
    
    capture_faces(
        person_name=args.name,
        output_dir=args.output,
        num_images=args.images,
        camera_id=args.camera
    )


if __name__ == '__main__':
    main()
