#!/usr/bin/env python3
"""
GESTICULINK Setup Script
Interactive setup wizard for first-time configuration
"""
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("     GESTICULINK - Setup Wizard")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible"""
    logger.info("Checking Python version...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False


def check_pip():
    """Check if pip is available"""
    logger.info("Checking pip...")
    try:
        subprocess.run(['pip', '--version'], capture_output=True, check=True)
        logger.info("✅ pip is available")
        return True
    except:
        logger.error("❌ pip not found")
        return False


def install_dependencies():
    """Install Python dependencies"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Installing dependencies...")
    logger.info("This may take several minutes...")
    logger.info("=" * 60)
    
    response = input("Install dependencies from requirements.txt? (y/n): ")
    if response.lower() != 'y':
        logger.info("Skipping dependency installation")
        return True
    
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to install dependencies")
        logger.info("Try manually: pip install -r requirements.txt")
        return False


def setup_environment():
    """Setup environment variables"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Environment Configuration")
    logger.info("=" * 60)
    
    if os.path.exists('.env'):
        logger.info("✅ .env file already exists")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            return True
    
    # Copy template
    if os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        logger.info("✅ Created .env from template")
    else:
        # Create basic .env
        with open('.env', 'w') as f:
            f.write("# GESTICULINK Environment Variables\n")
            f.write("OPENAI_API_KEY=\n")
        logger.info("✅ Created .env file")
    
    logger.info("")
    logger.info("Optional: Add OpenAI API key for AI conversations")
    response = input("Do you want to add OpenAI API key now? (y/n): ")
    
    if response.lower() == 'y':
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            with open('.env', 'r') as f:
                content = f.read()
            content = content.replace('OPENAI_API_KEY=', f'OPENAI_API_KEY={api_key}')
            with open('.env', 'w') as f:
                f.write(content)
            logger.info("✅ OpenAI API key saved")
        else:
            logger.info("No key entered, you can add it later in .env")
    
    return True


def download_models():
    """Download DNN models"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("DNN Models (optional)")
    logger.info("=" * 60)
    logger.info("Download models for better face detection?")
    logger.info("System works without them using Haar Cascades.")
    
    response = input("Download DNN models? (y/n): ")
    if response.lower() != 'y':
        logger.info("Skipping model download")
        return True
    
    try:
        subprocess.run(['python', 'scripts/download_models.py'], check=True)
        return True
    except subprocess.CalledProcessError:
        logger.warning("⚠️ Model download failed, but system will work with Haar Cascades")
        return True


def test_hardware():
    """Test camera and microphone"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Hardware Test")
    logger.info("=" * 60)
    
    response = input("Test camera? (y/n): ")
    if response.lower() == 'y':
        logger.info("Starting camera test...")
        try:
            subprocess.run(['python', 'scripts/test_camera.py'])
        except:
            logger.warning("⚠️ Camera test failed")
    
    logger.info("")
    response = input("Test microphone? (y/n): ")
    if response.lower() == 'y':
        logger.info("Starting microphone test...")
        try:
            subprocess.run(['python', 'scripts/test_microphone.py'])
        except:
            logger.warning("⚠️ Microphone test failed")
    
    return True


def show_next_steps():
    """Show next steps to user"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Setup Complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("")
    logger.info("1. Capture face images:")
    logger.info("   python scripts/capture_faces.py --name \"Your Name\" --images 20")
    logger.info("")
    logger.info("2. Train the system:")
    logger.info("   python scripts/train_encodings.py")
    logger.info("")
    logger.info("3. Run the system:")
    logger.info("   python scripts/example_run.py")
    logger.info("")
    logger.info("For detailed guide, see:")
    logger.info("  - QUICKSTART.md for quick start")
    logger.info("  - README.md for full documentation")
    logger.info("")


def main():
    """Run setup wizard"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Installation steps
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Download Models", download_models),
        ("Test Hardware", test_hardware)
    ]
    
    logger.info("")
    logger.info("Setup steps:")
    for i, (name, _) in enumerate(steps, 1):
        logger.info(f"  {i}. {name}")
    logger.info("")
    
    response = input("Continue with setup? (y/n): ")
    if response.lower() != 'y':
        logger.info("Setup cancelled")
        return False
    
    # Run steps
    for name, step_func in steps:
        if not step_func():
            logger.error(f"Setup failed at: {name}")
            return False
    
    # Show next steps
    show_next_steps()
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)
