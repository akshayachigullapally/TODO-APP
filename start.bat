@echo off
echo 🚀 Starting Todo App...

REM Start Backend in a new window
echo 🐍 Starting Flask backend...
start "Flask Backend" cmd /k "cd flask-server && venv\Scripts\activate && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in a new window
echo ⚛️ Starting React frontend...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo ✅ Both servers are starting!
echo.
echo 📡 Backend: http://127.0.0.1:5000
echo 🌐 Frontend: http://localhost:3000
echo.
echo Press any key to continue...
pause >nul