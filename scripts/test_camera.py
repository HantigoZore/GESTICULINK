#!/usr/bin/env python3
"""
Camera Test Script
Tests camera functionality and face detection
"""
import cv2
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_camera(camera_id=0):
    """
    Test camera and face detection
    
    Args:
        camera_id: Camera device ID
    """
    logger.info("=" * 60)
    logger.info("Camera Test")
    logger.info("=" * 60)
    
    # Try to open camera
    logger.info(f"Opening camera {camera_id}...")
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        logger.error(f"❌ Could not open camera {camera_id}")
        logger.info("Troubleshooting:")
        logger.info("  - Check if camera is connected")
        logger.info("  - Try different camera ID (--camera 1, 2, etc.)")
        logger.info("  - Check if another application is using the camera")
        return False
    
    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    logger.info(f"✅ Camera opened successfully")
    logger.info(f"Resolution: {width}x{height}")
    logger.info(f"FPS: {fps}")
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    if face_cascade.empty():
        logger.warning("⚠️ Could not load face detector")
        test_detection = False
    else:
        logger.info("✅ Face detector loaded")
        test_detection = True
    
    logger.info("")
    logger.info("Press 'Q' or ESC to quit")
    logger.info("")
    
    frame_count = 0
    faces_detected = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                logger.error("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Test face detection
            if test_detection and frame_count % 5 == 0:  # Every 5 frames
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Draw rectangles
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        "Face Detected",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )
                
                if len(faces) > 0:
                    faces_detected += 1
            
            # Add info overlay
            cv2.putText(
                frame,
                f"Frame: {frame_count} | Faces: {faces_detected}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
            
            cv2.putText(
                frame,
                "Press Q or ESC to quit",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            
            # Display frame
            cv2.imshow('Camera Test', frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Total frames: {frame_count}")
    if test_detection:
        logger.info(f"Frames with faces detected: {faces_detected}")
        if faces_detected > 0:
            logger.info("✅ Face detection working!")
        else:
            logger.info("⚠️ No faces detected. Try positioning yourself in front of camera.")
    
    logger.info("✅ Camera test complete")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Test camera functionality',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device ID to test (default: 0)'
    )
    
    args = parser.parse_args()
    
    test_camera(args.camera)


if __name__ == '__main__':
    main()
