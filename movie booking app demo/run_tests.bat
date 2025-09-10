@echo off
echo Running CineBook Test Suite...
echo.

echo Starting Flask server for testing...
start "Flask Test Server" cmd /k "python app_flask.py"

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo Running tests...
python test_cases.py

echo.
echo Test execution completed.
pause