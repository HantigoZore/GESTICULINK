#!/usr/bin/env python3
"""
Train Face Encodings Script
Creates face encodings from captured images
"""
import sys
import os
import argparse
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from face_recognition_module import EncodingsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_encodings(dataset_path='dataset', output_path='models/encodings.pickle', num_jitters=1):
    """
    Train face encodings from dataset
    
    Args:
        dataset_path: Path to dataset directory
        output_path: Path to save encodings
        num_jitters: Number of times to resample face (higher = more accurate)
    """
    logger.info("=" * 60)
    logger.info("Face Recognition Training")
    logger.info("=" * 60)
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        logger.error(f"❌ Dataset path not found: {dataset_path}")
        logger.info("Please run 'python scripts/capture_faces.py' first to create dataset")
        return False
    
    # Check if dataset has person directories
    person_dirs = [d for d in os.listdir(dataset_path) 
                  if os.path.isdir(os.path.join(dataset_path, d))]
    
    if not person_dirs:
        logger.error(f"❌ No person directories found in {dataset_path}")
        logger.info("Dataset structure should be:")
        logger.info("  dataset/")
        logger.info("    person1/")
        logger.info("      image1.jpg")
        logger.info("      image2.jpg")
        logger.info("    person2/")
        logger.info("      image1.jpg")
        return False
    
    logger.info(f"Found {len(person_dirs)} people: {', '.join(person_dirs)}")
    
    # Create encodings
    manager = EncodingsManager(encodings_path=output_path)
    
    logger.info(f"Creating encodings with num_jitters={num_jitters}")
    logger.info("This may take a few minutes...")
    
    data = manager.create_encodings_from_directory(dataset_path, num_jitters=num_jitters)
    
    if not data['encodings']:
        logger.error("❌ No encodings were created!")
        logger.info("Please check:")
        logger.info("  - Images are in correct format (jpg, jpeg, png)")
        logger.info("  - Faces are clearly visible in images")
        logger.info("  - Images are not corrupted")
        return False
    
    # Save encodings
    success = manager.save_encodings(data)
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Training Complete!")
        logger.info("=" * 60)
        logger.info(f"Total encodings: {len(data['encodings'])}")
        logger.info(f"People trained: {len(set(data['names']))}")
        logger.info(f"Encodings saved to: {output_path}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Run 'python scripts/example_run.py' to test recognition")
        logger.info("  2. Run 'python scripts/test_camera.py' to test camera")
        return True
    else:
        logger.error("❌ Failed to save encodings")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Train face recognition from captured images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/train_encodings.py
  python scripts/train_encodings.py --dataset my_dataset --jitters 2
  
Notes:
  - Higher num_jitters improves accuracy but increases processing time
  - Use num_jitters=1 for quick testing, 5-10 for production
  - This script should be run after capturing faces with capture_faces.py
        """
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        default='dataset',
        help='Path to dataset directory (default: dataset)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='models/encodings.pickle',
        help='Output path for encodings file (default: models/encodings.pickle)'
    )
    
    parser.add_argument(
        '--jitters',
        type=int,
        default=1,
        help='Number of times to resample face (1-10, default: 1)'
    )
    
    args = parser.parse_args()
    
    success = train_encodings(
        dataset_path=args.dataset,
        output_path=args.output,
        num_jitters=args.jitters
    )
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
