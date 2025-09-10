@echo off
echo Starting Movie Booking App...
echo.

echo Starting Flask API server...
start "Flask API" cmd /k "python app_flask.py"

echo Waiting for Flask server to start...
timeout /t 3 /nobreak >nul

echo Starting Streamlit frontend...
start "Streamlit App" cmd /k "streamlit run app.py"

echo.
echo Both servers are starting...
echo Flask API: http://localhost:5000
echo Streamlit App: http://localhost:8501
echo.
echo Press any key to stop both servers...
pause >nul

echo Stopping servers...
taskkill /f /im python.exe 2>nul
echo Done.