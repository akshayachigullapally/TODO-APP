# 🚀 Modern Todo App

A beautiful, full-stack Todo application built with **Flask** (Python) backend and **React** frontend featuring a modern, professional UI design.

![Todo App Preview](https://img.shields.io/badge/Status-Ready-brightgreen)
![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)
![React](https://img.shields.io/badge/React-19.1.1-blue)
![Python](https://img.shields.io/badge/Python-3.8+-yellow)

## ✨ Features

### Backend (Flask)
- ✅ **REST API** with Flask, Flask-CORS, and Flask-SQLAlchemy
- 📊 **SQLite Database** for data persistence
- 🔄 **CRUD Operations** for todos (Create, Read, Update, Delete)
- 📈 **Statistics endpoint** for todo metrics
- 🛡️ **Error handling** with proper HTTP status codes
- 🐍 **Debug mode** enabled for development

### Frontend (React)
- 🎨 **Modern UI Design** with gradient backgrounds and smooth animations
- 📱 **Responsive Design** that works on mobile and desktop
- 📊 **Statistics Dashboard** showing total, completed, and pending todos
- ✨ **Interactive Elements** with hover effects and transitions
- 🎯 **Click to toggle** todo completion status
- 🗑️ **One-click delete** functionality
- ⚡ **Real-time updates** using Axios for API calls
- 🎨 **Professional CSS** with custom properties and modern styling

## 🏗️ Project Structure

```
TODO-APP/
├── flask-server/
│   ├── app.py              # Flask backend application
│   ├── requirements.txt    # Python dependencies
│   └── todos.db           # SQLite database (created automatically)
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Modern CSS styling
│   │   └── ...
│   ├── package.json       # Node.js dependencies
│   └── ...
├── setup.bat              # Windows setup script
├── start.bat              # Windows start script
└── README.md              # This file
```

## 🚀 Quick Start

### Method 1: Automated Setup (Windows)

1. **Clone or download** this repository
2. **Run setup script**:
   ```cmd
   setup.bat
   ```
3. **Start both servers**:
   ```cmd
   start.bat
   ```

### Method 2: Manual Setup

#### Backend Setup
```cmd
cd flask-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
```

#### Frontend Setup
```cmd
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:5000

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/todos` | Get all todos |
| `POST` | `/todos` | Create a new todo |
| `PUT` | `/todos/<id>` | Toggle todo completion status |
| `DELETE` | `/todos/<id>` | Delete a todo |
| `GET` | `/todos/stats` | Get todo statistics |

### Example API Usage

#### Create a new todo:
```bash
curl -X POST http://127.0.0.1:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"task": "Learn React"}'
```

#### Get all todos:
```bash
curl http://127.0.0.1:5000/todos
```

#### Toggle todo completion:
```bash
curl -X PUT http://127.0.0.1:5000/todos/1
```

## 🎨 Design Features

- **Modern Gradient Background**: Purple to blue gradient for visual appeal
- **Card-based Layout**: Clean, shadow-based cards for content organization
- **Smooth Animations**: CSS transitions and keyframe animations
- **Interactive Elements**: Hover effects, button animations, and loading states
- **Responsive Design**: Mobile-first approach with breakpoints
- **Accessibility**: Focus states, reduced motion support, and high contrast mode
- **Custom Scrollbar**: Styled scrollbar for todo list overflow

## 🛠️ Technologies Used

### Backend
- **Flask** 2.3.3 - Python web framework
- **Flask-SQLAlchemy** 3.0.5 - Database ORM
- **Flask-CORS** 4.0.0 - Cross-Origin Resource Sharing
- **SQLite** - Lightweight database

### Frontend
- **React** 19.1.1 - JavaScript library for UI
- **Axios** 1.12.2 - HTTP client for API calls
- **Modern CSS** - Custom properties, Grid, Flexbox
- **CSS Animations** - Smooth transitions and keyframes

## 🔧 Development

### Project Requirements
- **Python** 3.8 or higher
- **Node.js** 14 or higher
- **npm** or **yarn** package manager

### Environment Variables
The app uses default configurations, but you can customize:
- Backend runs on port **5000**
- Frontend runs on port **3000**
- Database file: `todos.db` (created automatically)

## 📝 Usage Guide

1. **Add a Todo**: Type in the input field and click "Add Task" or press Enter
2. **Mark Complete**: Click on any todo item to toggle its completion status
3. **Delete Todo**: Click the trash icon (🗑️) next to any todo
4. **View Stats**: Check the statistics cards at the top for progress overview

## 🐛 Troubleshooting

### Backend Issues
- **Port 5000 in use**: Change the port in `app.py` line: `app.run(debug=True, port=5001)`
- **Module not found**: Ensure virtual environment is activated and dependencies installed
- **Database errors**: Delete `todos.db` file to reset the database

### Frontend Issues
- **API connection failed**: Ensure Flask backend is running on port 5000
- **Build errors**: Clear node_modules and reinstall: `npm install`
- **Port 3000 in use**: React will prompt to use a different port

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🎯 Future Enhancements

- [ ] User authentication and authorization
- [ ] Todo categories and tags
- [ ] Due dates and reminders
- [ ] Drag and drop reordering
- [ ] Dark/light theme toggle
- [ ] Export todos to JSON/CSV
- [ ] Advanced filtering and search

---

**Made with ❤️ using Flask and React**

*Happy coding! 🚀*