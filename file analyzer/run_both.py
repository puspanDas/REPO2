import subprocess
import time
import sys
import os

def run_backend():
    """Start Flask backend"""
    return subprocess.Popen([sys.executable, 'backend.py'])

def run_frontend():
    """Start Streamlit frontend"""
    return subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'app_with_backend.py'])

if __name__ == "__main__":
    print("🚀 Starting AI Dashboard with Backend...")
    
    # Start backend
    print("📡 Starting Flask backend...")
    backend_process = run_backend()
    time.sleep(3)  # Wait for backend to start
    
    # Start frontend
    print("🎨 Starting Streamlit frontend...")
    frontend_process = run_frontend()
    
    try:
        print("✅ Both services running!")
        print("🌐 Backend: http://localhost:5000")
        print("🎯 Frontend: http://localhost:8501")
        print("Press Ctrl+C to stop both services")
        
        # Wait for processes
        backend_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Services stopped")