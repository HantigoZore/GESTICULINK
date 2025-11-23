"""
Face Encodings Manager
Handles creation, storage, and loading of face encodings
"""
import os
import pickle
import cv2
import numpy as np
import logging
import face_recognition

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EncodingsManager:
    """
    Manages face encodings for recognition
    """
    
    def __init__(self, encodings_path='models/encodings.pickle'):
        """
        Initialize encodings manager
        
        Args:
            encodings_path: Path to save/load encodings file
        """
        self.encodings_path = encodings_path
        self.known_encodings = []
        self.known_names = []
        
        # Ensure models directory exists
        os.makedirs(os.path.dirname(encodings_path), exist_ok=True)
    
    def create_encodings_from_directory(self, dataset_path, num_jitters=1):
        """
        Create face encodings from a directory of images
        
        Directory structure should be:
        dataset_path/
            person1/
                image1.jpg
                image2.jpg
            person2/
                image1.jpg
        
        Args:
            dataset_path: Path to dataset directory
            num_jitters: Number of times to re-sample face for encoding (higher = more accurate but slower)
        
        Returns:
            Dictionary with 'encodings' and 'names' lists
        """
        logger.info(f"Creating encodings from {dataset_path}")
        
        encodings = []
        names = []
        
        if not os.path.exists(dataset_path):
            logger.error(f"❌ Dataset path does not exist: {dataset_path}")
            return {'encodings': [], 'names': []}
        
        # Iterate through each person's directory
        person_dirs = [d for d in os.listdir(dataset_path) 
                      if os.path.isdir(os.path.join(dataset_path, d))]
        
        if not person_dirs:
            logger.warning(f"⚠️ No person directories found in {dataset_path}")
            return {'encodings': [], 'names': []}
        
        for person_name in person_dirs:
            person_path = os.path.join(dataset_path, person_name)
            logger.info(f"Processing images for: {person_name}")
            
            # Get all image files
            image_files = [f for f in os.listdir(person_path)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            for image_file in image_files:
                image_path = os.path.join(person_path, image_file)
                
                try:
                    # Load image
                    image = cv2.imread(image_path)
                    if image is None:
                        logger.warning(f"⚠️ Could not load image: {image_path}")
                        continue
                    
                    # Convert BGR to RGB (face_recognition uses RGB)
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces
                    face_locations = face_recognition.face_locations(
                        rgb_image,
                        model='hog'  # Use 'cnn' for better accuracy but slower
                    )
                    
                    if not face_locations:
                        logger.warning(f"⚠️ No face found in {image_path}")
                        continue
                    
                    # Get face encodings
                    face_encodings = face_recognition.face_encodings(
                        rgb_image,
                        face_locations,
                        num_jitters=num_jitters
                    )
                    
                    if face_encodings:
                        encodings.append(face_encodings[0])
                        names.append(person_name)
                        logger.info(f"✅ Encoded: {image_file}")
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {image_path}: {e}")
                    continue
        
        logger.info(f"✅ Created {len(encodings)} encodings for {len(set(names))} people")
        
        return {'encodings': encodings, 'names': names}
    
    def save_encodings(self, data):
        """
        Save encodings to pickle file
        
        Args:
            data: Dictionary with 'encodings' and 'names' lists
        """
        try:
            with open(self.encodings_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"✅ Encodings saved to {self.encodings_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving encodings: {e}")
            return False
    
    def load_encodings(self):
        """
        Load encodings from pickle file
        
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.encodings_path):
            logger.warning(f"⚠️ Encodings file not found: {self.encodings_path}")
            return False
        
        try:
            with open(self.encodings_path, 'rb') as f:
                data = pickle.load(f)
            
            self.known_encodings = data.get('encodings', [])
            self.known_names = data.get('names', [])
            
            logger.info(f"✅ Loaded {len(self.known_encodings)} encodings")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading encodings: {e}")
            return False
    
    def add_encoding(self, encoding, name):
        """
        Add a single encoding to the current set
        
        Args:
            encoding: Face encoding array
            name: Person's name
        """
        self.known_encodings.append(encoding)
        self.known_names.append(name)
    
    def get_encodings(self):
        """
        Get current encodings and names
        
        Returns:
            Tuple of (encodings, names)
        """
        return self.known_encodings, self.known_names
    
    def clear_encodings(self):
        """Clear all loaded encodings"""
        self.known_encodings = []
        self.known_names = []
        logger.info("Encodings cleared")
