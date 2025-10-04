"""
Launch script for POSH Video Generation FastAPI App
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if FastAPI and Uvicorn are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Installing FastAPI and Uvicorn...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]", "python-multipart"])
            print("✅ FastAPI dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install FastAPI dependencies")
            return False

def main():
    """Launch the FastAPI app"""
    print("🚀 POSH Video Generation System - FastAPI Interface")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Get the current directory
    current_dir = Path(__file__).parent
    app_path = current_dir / "fastapi_app.py"
    
    if not app_path.exists():
        print(f"❌ FastAPI app not found at: {app_path}")
        return
    
    print(f"📁 App location: {app_path}")
    print("🌐 Starting FastAPI server...")
    print("💡 The app will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Launch FastAPI with Uvicorn
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "fastapi_app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error launching FastAPI: {e}")

if __name__ == "__main__":
    main()

