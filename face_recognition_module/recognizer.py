"""
Face Recognizer Module
Main API for real-time face recognition
"""
import cv2
import numpy as np
import logging
import face_recognition
from .detector import FaceDetector
from .align import FaceAligner
from .encodings_manager import EncodingsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceRecognizer:
    """
    Complete face recognition system
    """
    
    def __init__(self, encodings_path='models/encodings.pickle', 
                 tolerance=0.6, detection_method='auto'):
        """
        Initialize face recognizer
        
        Args:
            encodings_path: Path to encodings file
            tolerance: Face matching tolerance (lower = more strict)
            detection_method: Face detection method ('dnn', 'haar', 'auto')
        """
        self.tolerance = tolerance
        self.detector = FaceDetector(method=detection_method)
        self.aligner = FaceAligner()
        self.encodings_manager = EncodingsManager(encodings_path)
        
        # Load existing encodings
        self.encodings_manager.load_encodings()
        
        logger.info("✅ Face Recognizer initialized")
    
    def recognize_faces(self, image, return_encodings=False):
        """
        Recognize faces in an image
        
        Args:
            image: BGR image from OpenCV
            return_encodings: Whether to return face encodings
        
        Returns:
            List of dictionaries with recognition results:
            [
                {
                    'box': (x, y, w, h),
                    'name': 'person_name',
                    'confidence': 0.95,
                    'encoding': [...] (optional)
                },
                ...
            ]
        """
        if image is None or image.size == 0:
            return []
        
        results = []
        
        try:
            # Detect faces
            faces = self.detector.detect_faces(image)
            
            if not faces:
                return []
            
            # Get known encodings
            known_encodings, known_names = self.encodings_manager.get_encodings()
            
            if not known_encodings:
                logger.warning("⚠️ No known face encodings loaded")
                # Return detected faces as "Unknown"
                for face in faces:
                    results.append({
                        'box': face,
                        'name': 'Unknown',
                        'confidence': 0.0
                    })
                return results
            
            # Convert to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process each detected face
            for face_box in faces:
                x, y, w, h = face_box
                
                # Align and preprocess face
                face_img = image[y:y+h, x:x+w]
                
                if face_img.size == 0:
                    continue
                
                # Get face encoding
                # Convert box format for face_recognition (top, right, bottom, left)
                face_location = (y, x + w, y + h, x)
                
                try:
                    face_encodings = face_recognition.face_encodings(
                        rgb_image,
                        [face_location]
                    )
                    
                    if not face_encodings:
                        results.append({
                            'box': face_box,
                            'name': 'Unknown',
                            'confidence': 0.0
                        })
                        continue
                    
                    face_encoding = face_encodings[0]
                    
                    # Compare with known faces
                    matches = face_recognition.compare_faces(
                        known_encodings,
                        face_encoding,
                        tolerance=self.tolerance
                    )
                    
                    # Calculate face distances (lower = more similar)
                    face_distances = face_recognition.face_distance(
                        known_encodings,
                        face_encoding
                    )
                    
                    name = "Unknown"
                    confidence = 0.0
                    
                    if True in matches:
                        # Get best match
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_names[best_match_index]
                            # Convert distance to confidence score (0-1)
                            confidence = 1.0 - face_distances[best_match_index]
                    
                    result = {
                        'box': face_box,
                        'name': name,
                        'confidence': float(confidence)
                    }
                    
                    if return_encodings:
                        result['encoding'] = face_encoding
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"❌ Error encoding face: {e}")
                    results.append({
                        'box': face_box,
                        'name': 'Unknown',
                        'confidence': 0.0
                    })
        
        except Exception as e:
            logger.error(f"❌ Error during face recognition: {e}")
        
        return results
    
    def recognize_largest_face(self, image):
        """
        Recognize only the largest face in the image
        
        Args:
            image: BGR image from OpenCV
        
        Returns:
            Dictionary with recognition result or None
        """
        results = self.recognize_faces(image)
        
        if not results:
            return None
        
        # Return the face with largest bounding box
        return max(results, key=lambda r: r['box'][2] * r['box'][3])
    
    def draw_results(self, image, results, show_confidence=True):
        """
        Draw recognition results on image
        
        Args:
            image: BGR image from OpenCV
            results: Recognition results from recognize_faces()
            show_confidence: Whether to show confidence score
        
        Returns:
            Image with drawn results
        """
        output = image.copy()
        
        for result in results:
            x, y, w, h = result['box']
            name = result['name']
            confidence = result['confidence']
            
            # Choose color based on recognition
            if name == "Unknown":
                color = (0, 0, 255)  # Red
            else:
                color = (0, 255, 0)  # Green
            
            # Draw rectangle
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = name
            if show_confidence and confidence > 0:
                label += f" ({confidence:.2f})"
            
            # Draw background for text
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(
                output,
                (x, y - 25),
                (x + label_size[0], y),
                color,
                -1
            )
            
            # Draw text
            cv2.putText(
                output,
                label,
                (x, y - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        return output
    
    def reload_encodings(self):
        """Reload encodings from file"""
        return self.encodings_manager.load_encodings()
