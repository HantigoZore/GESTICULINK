"""
Face Detector Module
Provides robust face detection using OpenCV DNN with fallback to Haar Cascades
"""
import cv2
import os
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Robust face detector with multiple backends
    """
    
    def __init__(self, method='auto'):
        """
        Initialize face detector
        
        Args:
            method (str): Detection method - 'dnn', 'haar', or 'auto'
        """
        self.method = method
        self.dnn_detector = None
        self.haar_cascade = None
        
        if method in ['dnn', 'auto']:
            self._load_dnn_detector()
        
        if method in ['haar', 'auto'] or self.dnn_detector is None:
            self._load_haar_cascade()
    
    def _load_dnn_detector(self):
        """Load OpenCV DNN face detector (res10_300x300_ssd)"""
        try:
            # Paths for the DNN model files
            model_file = "models/res10_300x300_ssd_iter_140000.caffemodel"
            config_file = "models/deploy.prototxt"
            
            # Check if model files exist
            if os.path.exists(model_file) and os.path.exists(config_file):
                self.dnn_detector = cv2.dnn.readNetFromCaffe(config_file, model_file)
                logger.info("✅ DNN face detector loaded successfully")
            else:
                logger.warning(f"⚠️ DNN model files not found at {model_file}")
                logger.info("Download from: https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector")
        except Exception as e:
            logger.error(f"❌ Error loading DNN detector: {e}")
            self.dnn_detector = None
    
    def _load_haar_cascade(self):
        """Load Haar Cascade face detector (fallback)"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.haar_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.haar_cascade.empty():
                raise Exception("Failed to load Haar Cascade")
            
            logger.info("✅ Haar Cascade detector loaded as fallback")
        except Exception as e:
            logger.error(f"❌ Error loading Haar Cascade: {e}")
            self.haar_cascade = None
    
    def detect_faces(self, image, confidence_threshold=0.5):
        """
        Detect faces in an image
        
        Args:
            image: BGR image from OpenCV
            confidence_threshold: Minimum confidence for DNN detection (0-1)
        
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
        """
        if image is None or image.size == 0:
            return []
        
        h, w = image.shape[:2]
        
        # Try DNN detector first
        if self.dnn_detector is not None:
            try:
                blob = cv2.dnn.blobFromImage(
                    cv2.resize(image, (300, 300)), 
                    1.0, 
                    (300, 300), 
                    (104.0, 177.0, 123.0)
                )
                self.dnn_detector.setInput(blob)
                detections = self.dnn_detector.forward()
                
                faces = []
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    
                    if confidence > confidence_threshold:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (x, y, x1, y1) = box.astype("int")
                        
                        # Ensure coordinates are within image bounds
                        x = max(0, x)
                        y = max(0, y)
                        x1 = min(w, x1)
                        y1 = min(h, y1)
                        
                        faces.append((x, y, x1 - x, y1 - y))
                
                return faces
            except Exception as e:
                logger.error(f"❌ DNN detection failed: {e}")
        
        # Fallback to Haar Cascade
        if self.haar_cascade is not None:
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.haar_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                return [tuple(face) for face in faces]
            except Exception as e:
                logger.error(f"❌ Haar Cascade detection failed: {e}")
        
        return []
    
    def get_largest_face(self, image, confidence_threshold=0.5):
        """
        Get the largest face in the image
        
        Args:
            image: BGR image from OpenCV
            confidence_threshold: Minimum confidence for detection
        
        Returns:
            Bounding box (x, y, w, h) or None if no face detected
        """
        faces = self.detect_faces(image, confidence_threshold)
        
        if not faces:
            return None
        
        # Return the largest face by area
        return max(faces, key=lambda f: f[2] * f[3])
