#!/usr/bin/env python3
"""
Download DNN Face Detection Models
Downloads required OpenCV DNN models for better face detection
"""
import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        logger.info(f"Downloading {os.path.basename(destination)}...")
        urllib.request.urlretrieve(url, destination)
        logger.info(f"✅ Downloaded to {destination}")
        return True
    except Exception as e:
        logger.error(f"❌ Error downloading: {e}")
        return False


def download_dnn_models():
    """Download DNN face detection models"""
    logger.info("=" * 60)
    logger.info("DNN Face Detection Models Downloader")
    logger.info("=" * 60)
    
    # Create models directory
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    # Model URLs
    prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
    caffemodel_url = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
    
    prototxt_path = os.path.join(models_dir, "deploy.prototxt")
    caffemodel_path = os.path.join(models_dir, "res10_300x300_ssd_iter_140000.caffemodel")
    
    # Check if already downloaded
    if os.path.exists(prototxt_path) and os.path.exists(caffemodel_path):
        logger.info("✅ Models already downloaded!")
        logger.info(f"  - {prototxt_path}")
        logger.info(f"  - {caffemodel_path}")
        return True
    
    # Download prototxt
    logger.info("")
    logger.info("Downloading deploy.prototxt...")
    success1 = download_file(prototxt_url, prototxt_path)
    
    # Download caffemodel (larger file, ~10MB)
    logger.info("")
    logger.info("Downloading res10_300x300_ssd_iter_140000.caffemodel (~10MB)...")
    logger.info("This may take a minute...")
    success2 = download_file(caffemodel_url, caffemodel_path)
    
    logger.info("")
    logger.info("=" * 60)
    
    if success1 and success2:
        logger.info("✅ All models downloaded successfully!")
        logger.info("")
        logger.info("Models saved to:")
        logger.info(f"  - {prototxt_path}")
        logger.info(f"  - {caffemodel_path}")
        logger.info("")
        logger.info("The face detector will now use DNN for better accuracy.")
        return True
    else:
        logger.error("❌ Failed to download some models")
        logger.info("")
        logger.info("The system will fall back to Haar Cascades.")
        logger.info("You can try downloading manually from:")
        logger.info(f"  - {prototxt_url}")
        logger.info(f"  - {caffemodel_url}")
        return False


def main():
    try:
        download_dnn_models()
    except KeyboardInterrupt:
        logger.info("\nDownload cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
