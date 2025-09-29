@echo off
echo 🚀 Setting up Todo App...

REM Setup Backend
echo 📦 Setting up Flask backend...
cd flask-server

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating environment configuration file...
    copy .env.example .env
    echo ⚙️ Please edit .env file with your PostgreSQL credentials if you want to use PostgreSQL
    echo 💡 Otherwise, the app will use SQLite by default
)

echo ✅ Backend setup complete!

REM Setup Frontend
echo 📦 Setting up React frontend...
cd ..\frontend

REM Install Node dependencies
echo Installing Node dependencies...
npm install

echo ✅ Frontend setup complete!

echo.
echo 🎉 Setup complete! Run the following commands to start the app:
echo.
echo Backend (Flask):
echo   cd flask-server ^&^& python app.py
echo.
echo Frontend (React):
echo   cd frontend ^&^& npm start
echo.
echo The app will be available at:
echo   Backend: http://127.0.0.1:5000
echo   Frontend: http://localhost:3000

pause