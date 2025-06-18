#!/usr/bin/env python3
"""
🌱 GREEN WORLD - Easy Deployment Script
Run this file to start your Green World social media platform!
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-socketio"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("💡 Try running: pip install flask flask-socketio")
        return False

def create_directories():
    """Create necessary directories"""
    try:
        os.makedirs("uploads", exist_ok=True)
        print("✅ Upload directory created/verified")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not create upload directory: {e}")
        return True  # Continue anyway

def run_app():
    """Run the Green World application"""
    print("\n🌱 Starting Green World Social Media Platform...")
    print("=" * 60)
    print("🌍 Your app will be available at: http://localhost:5001")
    print("🏠 Home Page: http://localhost:5001")
    print("🔑 Login: http://localhost:5001/login")
    print("🌐 Social Feed: http://localhost:5001/social-feed")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Import and run the app
        import app
        app.app.run(host='0.0.0.0', port=5001, debug=True)
    except ImportError:
        print("❌ Error: app.py not found in current directory")
        print("💡 Make sure app.py is in the same folder as this script")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

def main():
    """Main deployment function"""
    print("🌱 GREEN WORLD - Deployment Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️ Continuing without dependency installation...")
    
    # Create directories
    create_directories()
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main()
