"""
Launch script for POSH Video Generation Streamlit App
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        print("✅ Streamlit is installed")
        return True
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "pillow"])
            print("✅ Streamlit installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Streamlit")
            return False

def main():
    """Launch the Streamlit app"""
    print("🚀 POSH Video Generation System - Streamlit Interface")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Get the current directory
    current_dir = Path(__file__).parent
    app_path = current_dir / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"❌ Streamlit app not found at: {app_path}")
        return
    
    print(f"📁 App location: {app_path}")
    print("🌐 Starting Streamlit server...")
    print("💡 The app will open in your default web browser")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error launching Streamlit: {e}")

if __name__ == "__main__":
    main()
