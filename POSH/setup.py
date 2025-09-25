"""
Setup script for POSH Video Generation System
"""
import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_conda_environment():
    """Check if running in POSH conda environment"""
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env != 'POSH':
        print("⚠️ Warning: Not running in POSH conda environment")
        print(f"Current environment: {conda_env}")
        print("Please run: conda activate POSH")
        return False
    print(f"✅ Conda environment: {conda_env}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_api_key():
    """Check if API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    if len(api_key) < 30:  # Basic validation
        print("⚠️ GEMINI_API_KEY seems invalid (too short)")
        return False
    
    print("✅ GEMINI_API_KEY configured")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["generated_videos", "temp_scenes"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def run_test():
    """Run a basic test to ensure everything works"""
    print("\n🧪 Running basic test...")
    
    try:
        from config import Config
        Config.validate()
        print("✅ Configuration test passed")
        
        from scenario_processor import ScenarioProcessor
        processor = ScenarioProcessor()
        print("✅ Scenario processor initialized")
        
        from video_generator import VideoGenerator
        generator = VideoGenerator()
        print("✅ Video generator initialized")
        
        from video_combiner import VideoCombiner
        combiner = VideoCombiner()
        print("✅ Video combiner initialized")
        
        from workflow import POSHVideoWorkflow
        workflow = POSHVideoWorkflow()
        print("✅ Workflow initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 POSH Video Generation System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check conda environment
    check_conda_environment()  # Warning only
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check API key
    if not check_api_key():
        print("\n⚠️ Please ensure your GEMINI_API_KEY is set in the .env file")
        print("You can get an API key from: https://ai.google.dev/")
        return False
    
    # Create directories
    create_directories()
    
    # Run test
    if not run_test():
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("To run the application:")
    print("  python main.py")
    print("\nFor help:")
    print("  python main.py --help")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
