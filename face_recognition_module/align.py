"""
Facial Alignment Module
Uses MediaPipe for facial landmark detection and alignment
"""
import cv2
import numpy as np
import logging
import mediapipe as mp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceAligner:
    """
    Aligns faces using facial landmarks for better recognition accuracy
    """
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh"""
        try:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            logger.info("✅ MediaPipe Face Mesh initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing MediaPipe: {e}")
            self.face_mesh = None
    
    def align_face(self, image, face_box=None):
        """
        Align a face in the image
        
        Args:
            image: BGR image from OpenCV
            face_box: Optional (x, y, w, h) to crop before alignment
        
        Returns:
            Aligned face image or original if alignment fails
        """
        if self.face_mesh is None:
            return image
        
        try:
            # Crop to face region if box provided
            if face_box is not None:
                x, y, w, h = face_box
                # Add some padding
                padding = int(0.2 * max(w, h))
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(image.shape[1], x + w + padding)
                y2 = min(image.shape[0], y + h + padding)
                face_img = image[y1:y2, x1:x2]
            else:
                face_img = image
            
            if face_img.size == 0:
                return image
            
            # Convert to RGB for MediaPipe
            rgb_image = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            
            # Detect landmarks
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return face_img
            
            # Get landmarks
            landmarks = results.multi_face_landmarks[0]
            h, w = face_img.shape[:2]
            
            # Get key points for alignment (left eye, right eye, nose)
            # MediaPipe landmark indices:
            # 33: left eye center, 263: right eye center, 1: nose tip
            left_eye = landmarks.landmark[33]
            right_eye = landmarks.landmark[263]
            
            # Convert normalized coordinates to pixel coordinates
            left_eye_pts = np.array([left_eye.x * w, left_eye.y * h])
            right_eye_pts = np.array([right_eye.x * w, right_eye.y * h])
            
            # Calculate angle between eyes
            dY = right_eye_pts[1] - left_eye_pts[1]
            dX = right_eye_pts[0] - left_eye_pts[0]
            angle = np.degrees(np.arctan2(dY, dX))
            
            # Calculate center point between eyes
            eyes_center = ((left_eye_pts[0] + right_eye_pts[0]) // 2,
                          (left_eye_pts[1] + right_eye_pts[1]) // 2)
            
            # Get rotation matrix
            M = cv2.getRotationMatrix2D(eyes_center, angle, 1.0)
            
            # Apply rotation
            aligned = cv2.warpAffine(
                face_img, 
                M, 
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            return aligned
            
        except Exception as e:
            logger.error(f"❌ Error during face alignment: {e}")
            return face_img if face_box else image
    
    def preprocess_face(self, face_image):
        """
        Preprocess face for better recognition
        Applies CLAHE and normalization
        
        Args:
            face_image: Face image (BGR)
        
        Returns:
            Preprocessed face image
        """
        try:
            # Convert to grayscale for CLAHE
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Convert back to BGR
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
            # Resize to standard size
            standard_size = (160, 160)
            resized = cv2.resize(enhanced_bgr, standard_size, interpolation=cv2.INTER_CUBIC)
            
            return resized
            
        except Exception as e:
            logger.error(f"❌ Error during preprocessing: {e}")
            # Return resized original if preprocessing fails
            return cv2.resize(face_image, (160, 160), interpolation=cv2.INTER_CUBIC)
    
    def __del__(self):
        """Cleanup"""
        if self.face_mesh is not None:
            self.face_mesh.close()
