"""
Face Recognition Module
Complete face recognition system with detection, alignment, and recognition
"""
from .detector import FaceDetector
from .align import FaceAligner
from .encodings_manager import EncodingsManager
from .recognizer import FaceRecognizer

__all__ = [
    'FaceDetector',
    'FaceAligner',
    'EncodingsManager',
    'FaceRecognizer'
]
