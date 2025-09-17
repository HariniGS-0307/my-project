#!/usr/bin/env python3
"""
Startup script for AI Elderly Medicare System
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_database():
    """Initialize the database"""
    print("🗄️ Setting up database...")
    try:
        # Add the backend directory to Python path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Load environment variables from backend/.env
        load_dotenv(dotenv_path=backend_path / ".env")
        
        from app.database import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("ℹ️ Database will be created automatically when the server starts")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting AI Elderly Medicare System...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

def open_browser():
    """Open the application in browser"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if frontend_path.exists():
        webbrowser.open(f"file://{frontend_path.absolute()}")
        print("🌐 Opening application in browser...")

def main():
    """Main startup function"""
    print("=" * 50)
    print("🏥 AI Elderly Medicare System")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Install dependencies and start server")
    print("2. Start server only")
    print("3. Open frontend in browser")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        install_dependencies()
        setup_database()
        print("\n" + "=" * 50)
        print("🎉 Setup complete! Starting server...")
        print("📍 Backend API: http://localhost:8000")
        print("📍 API Docs: http://localhost:8000/docs")
        print("📍 Frontend: Open frontend/index.html in browser")
        print("=" * 50)
        start_server()
        
    elif choice == "2":
        setup_database()
        start_server()
        
    elif choice == "3":
        open_browser()
        
    elif choice == "4":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()