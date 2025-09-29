#!/bin/bash

echo "🚀 Setting up Todo App..."

# Setup Backend
echo "📦 Setting up Flask backend..."
cd flask-server

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # For Mac/Linux
# For Windows, use: venv\Scripts\activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating environment configuration file..."
    cp .env.example .env
    echo "⚙️ Please edit .env file with your PostgreSQL credentials if you want to use PostgreSQL"
    echo "💡 Otherwise, the app will use SQLite by default"
fi

echo "✅ Backend setup complete!"

# Setup Frontend
echo "📦 Setting up React frontend..."
cd ../frontend

# Install Node dependencies (already installed, but ensuring)
echo "Installing Node dependencies..."
npm install

echo "✅ Frontend setup complete!"

echo ""
echo "🎉 Setup complete! Run the following commands to start the app:"
echo ""
echo "Backend (Flask):"
echo "  cd flask-server && python app.py"
echo ""
echo "Frontend (React):"
echo "  cd frontend && npm start"
echo ""
echo "The app will be available at:"
echo "  Backend: http://127.0.0.1:5000"
echo "  Frontend: http://localhost:3000"