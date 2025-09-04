import subprocess
import time
import sys
import os

def run_app():
    print("Starting Movie Booking App...")
    print()
    
    try:
        # Start Flask API
        print("Starting Flask API server...")
        flask_process = subprocess.Popen([sys.executable, "app_flask.py"], 
                                       cwd=os.getcwd())
        
        # Wait for Flask to start
        print("Waiting for Flask server to start...")
        time.sleep(3)
        
        # Start Streamlit
        print("Starting Streamlit frontend...")
        streamlit_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"], 
                                           cwd=os.getcwd())
        
        print()
        print("Both servers are running:")
        print("Flask API: http://localhost:5000")
        print("Streamlit App: http://localhost:8501")
        print()
        print("Press Ctrl+C to stop both servers...")
        
        # Wait for user interrupt
        try:
            flask_process.wait()
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\nStopping servers...")
            flask_process.terminate()
            streamlit_process.terminate()
            print("Done.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_app()