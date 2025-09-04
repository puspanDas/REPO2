import subprocess
import sys
import time
import threading

def start_backend():
    subprocess.run([sys.executable, "backend.py"])

def start_frontend():
    time.sleep(3)  # Wait for backend to start
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend.py"])

if __name__ == "__main__":
    print("Starting Disease Prediction System...")
    
    # Start backend in separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Start frontend
    start_frontend()