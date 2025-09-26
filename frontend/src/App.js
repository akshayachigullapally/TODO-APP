import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import PomodoroTimer from './components/PomodoroTimer';
import './App.css';

const API_URL = 'http://127.0.0.1:5000';

function App() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('General');
  const [selectedPriority, setSelectedPriority] = useState('Medium');
  const [selectedRecurrence, setSelectedRecurrence] = useState('none');
  const [dueDate, setDueDate] = useState('');
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ 
    total: 0, 
    completed: 0, 
    pending: 0,
    priority_breakdown: { high: 0, medium: 0, low: 0 },
    overdue: 0
  });
  const [activeTab, setActiveTab] = useState('todos');
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [showPomodoro, setShowPomodoro] = useState(false);
  const [selectedTodoForFocus, setSelectedTodoForFocus] = useState(null);

  // Request notification permission on component mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  // Check for due tasks and show notifications
  useEffect(() => {
    const checkDueTasks = () => {
      if ('Notification' in window && Notification.permission === 'granted') {
        const now = new Date();
        const dueSoon = todos.filter(todo => {
          if (!todo.due_date || todo.completed) return false;
          const dueDate = new Date(todo.due_date);
          const timeDiff = dueDate - now;
          // Notify if due within next hour
          return timeDiff > 0 && timeDiff <= 60 * 60 * 1000;
        });

        dueSoon.forEach(todo => {
          new Notification('Task Due Soon!', {
            body: `"${todo.task}" is due soon`,
            icon: '/favicon.ico'
          });
        });
      }
    };

    const interval = setInterval(checkDueTasks, 60000); // Check every minute
    return () => clearInterval(interval);
  }, [todos]);

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return '#FF3B30';
      case 'Medium': return '#FF9500';
      case 'Low': return '#34C759';
      default: return '#FF9500';
    }
  };

  // Get category color
  const getCategoryColor = (category) => {
    const colors = {
      'Work': '#007AFF',
      'Personal': '#5856D6',
      'Shopping': '#FF9500',
      'Health': '#34C759',
      'General': '#8E8E93'
    };
    return colors[category] || colors['General'];
  };

  // Check if task is overdue
  const isOverdue = (dueDate, completed) => {
    if (!dueDate || completed) return false;
    return new Date(dueDate) < new Date();
  };

  // Check if task is due soon (within 24 hours)
  const isDueSoon = (dueDate, completed) => {
    if (!dueDate || completed) return false;
    const due = new Date(dueDate);
    const now = new Date();
    const timeDiff = due - now;
    return timeDiff > 0 && timeDiff <= 24 * 60 * 60 * 1000;
  };

  // Format date for display
  const formatDateTime = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format relative time
  const formatRelativeTime = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDateTime(dateString);
  };

  // Format due date display
  const formatDueDate = (dueDateString) => {
    if (!dueDateString) return null;
    const dueDate = new Date(dueDateString);
    const now = new Date();
    const diffMs = dueDate - now;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffMs < 0) return 'Overdue';
    if (diffDays === 0) {
      if (diffHours === 0) return 'Due now';
      return `Due in ${diffHours}h`;
    }
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays < 7) return `Due in ${diffDays} days`;
    return dueDate.toLocaleDateString();
  };

  // Fetch categories from backend
  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_URL}/categories`);
      setCategories(response.data);
    } catch (err) {
      console.error('Error fetching categories:', err);
      // Set default categories if fetch fails
      setCategories(['General', 'Work', 'Personal', 'Shopping', 'Health']);
    }
  };

  // Fetch todos from backend
  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/todos`);
      setTodos(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch todos. Make sure the backend is running.');
      console.error('Error fetching todos:', err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/todos/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  // Fetch history
  const fetchHistory = async () => {
    try {
      setHistoryLoading(true);
      const response = await axios.get(`${API_URL}/history?limit=7`);
      setHistory(response.data.history);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  // Add new todo
  const addTodo = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    try {
      const todoData = {
        task: inputValue.trim(),
        category: selectedCategory,
        priority: selectedPriority,
        recurrence: selectedRecurrence,
        due_date: dueDate || null
      };

      const response = await axios.post(`${API_URL}/todos`, todoData);
      setTodos([response.data, ...todos]);
      
      // Reset form
      setInputValue('');
      setSelectedCategory('General');
      setSelectedPriority('Medium');
      setSelectedRecurrence('none');
      setDueDate('');
      
      fetchStats();
    } catch (err) {
      setError('Failed to add todo');
      console.error('Error adding todo:', err);
    }
  };

  // Toggle todo completion
  const toggleTodo = async (id) => {
    try {
      const response = await axios.put(`${API_URL}/todos/${id}`);
      setTodos(todos.map(todo => 
        todo.id === id ? response.data : todo
      ));
      fetchStats();
    } catch (err) {
      setError('Failed to update todo');
      console.error('Error updating todo:', err);
    }
  };

  // Delete todo
  const deleteTodo = async (id) => {
    try {
      await axios.delete(`${API_URL}/todos/${id}`);
      setTodos(todos.filter(todo => todo.id !== id));
      fetchStats();
    } catch (err) {
      setError('Failed to delete todo');
      console.error('Error deleting todo:', err);
    }
  };

  // Start focus mode
  const startFocusMode = (todo) => {
    setSelectedTodoForFocus(todo);
    setShowPomodoro(true);
  };

  // Complete focus session
  const completeFocusSession = async () => {
    if (selectedTodoForFocus) {
      await toggleTodo(selectedTodoForFocus.id);
    }
  };

  // Close focus mode
  const closeFocusMode = () => {
    setShowPomodoro(false);
    setSelectedTodoForFocus(null);
  };

  useEffect(() => {
    fetchTodos();
    fetchStats();
    fetchCategories();
    if (activeTab === 'history') {
      fetchHistory();
    }
  }, [activeTab]);

  return (
    <div className="app">
      {/* Full Width Header */}
      <header className="header">
        <h1 className="title">
          <span className="title-icon">📋</span>
          All my tasks
        </h1>
        <p className="subtitle">Stay organized and focused</p>
      </header>

      <div className="container">
        {/* Sidebar */}
        <div className="sidebar">
          {/* Statistics */}
          <div className="stats">
            <div className="stat-card">
              <div className="stat-number">{stats.total}</div>
              <div className="stat-label">Total</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.completed}</div>
              <div className="stat-label">Completed</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{stats.pending}</div>
              <div className="stat-label">Pending</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'todos' ? 'active' : ''}`}
              onClick={() => setActiveTab('todos')}
            >
              <span>📝</span> Today
            </button>
            <button 
              className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <span>📊</span> Dashboard
            </button>
            <button 
              className={`tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <span>📅</span> History
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="main-content">
          {/* Error Message */}
          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {/* Add Todo Form - only show on todos tab */}
          {activeTab === 'todos' && (
            <form onSubmit={addTodo} className="todo-form">
              <div className="form-row">
                <div className="input-group">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Add a new task"
                    className="todo-input"
                  />
                  <button type="submit" className="add-button">
                    <span className="add-icon">+</span>
                  </button>
                </div>
              </div>
              
              <div className="form-options">
                <div className="option-group">
                  <label htmlFor="category">Category</label>
                  <select 
                    id="category"
                    value={selectedCategory} 
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="form-select"
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                
                <div className="option-group">
                  <label htmlFor="priority">Priority</label>
                  <select 
                    id="priority"
                    value={selectedPriority} 
                    onChange={(e) => setSelectedPriority(e.target.value)}
                    className="form-select"
                  >
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>
                </div>
                
                <div className="option-group">
                  <label htmlFor="recurrence">Repeat</label>
                  <select 
                    id="recurrence"
                    value={selectedRecurrence} 
                    onChange={(e) => setSelectedRecurrence(e.target.value)}
                    className="form-select"
                  >
                    <option value="none">None</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                
                <div className="option-group">
                  <label htmlFor="dueDate">Due Date</label>
                  <input 
                    type="datetime-local"
                    id="dueDate"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="form-input"
                  />
                </div>
              </div>
            </form>
          )}

          {/* Content Area */}
          <div className="content-area">
            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                Loading todos...
              </div>
            ) : activeTab === 'todos' ? (
              /* Todo List */
              <div className="todo-list">
                {todos.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">📝</div>
                    <h3>No tasks yet</h3>
                    <p>Add your first task above to get started!</p>
                  </div>
                ) : (
                  todos.map((todo) => (
                    <div key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''} ${
                      isOverdue(todo.due_date, todo.completed) ? 'overdue' : ''
                    } ${isDueSoon(todo.due_date, todo.completed) ? 'due-soon' : ''}`}>
                      <div 
                        className="todo-content"
                        onClick={() => toggleTodo(todo.id)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            toggleTodo(todo.id);
                          }
                        }}
                      >
                        <div className="todo-main">
                          <div className={`checkbox ${todo.completed ? 'checked' : ''}`}>
                            {todo.completed && <span className="checkmark">✓</span>}
                          </div>
                          <div className="todo-text-container">
                            <span className="todo-text">{todo.task}</span>
                            <div className="todo-meta">
                              <span 
                                className="category-badge"
                                style={{ backgroundColor: getCategoryColor(todo.category) }}
                              >
                                {todo.category}
                              </span>
                              <span 
                                className="priority-badge"
                                style={{ 
                                  backgroundColor: getPriorityColor(todo.priority),
                                  color: 'white'
                                }}
                              >
                                {todo.priority}
                              </span>
                              {todo.recurrence !== 'none' && (
                                <span className="recurrence-badge">
                                  🔄 {todo.recurrence}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="todo-timestamps">
                            <span className="created-at">
                              ➕ Created {formatRelativeTime(todo.created_at)}
                            </span>
                            {todo.completed_at && (
                              <span className="completed-at">
                                ✅ Completed {formatRelativeTime(todo.completed_at)}
                              </span>
                            )}
                            {todo.due_date && (
                              <span className={`due-date ${
                                isOverdue(todo.due_date, todo.completed) ? 'overdue' :
                                isDueSoon(todo.due_date, todo.completed) ? 'due-soon' : ''
                              }`}>
                                📅 {formatDueDate(todo.due_date)}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="todo-actions">
                        {!todo.completed && (
                          <button
                            onClick={() => startFocusMode(todo)}
                            className="focus-button"
                            aria-label="Start focus mode"
                            title="Start 25-minute focus session"
                          >
                            🍅
                          </button>
                        )}
                        <button
                          onClick={() => deleteTodo(todo.id)}
                          className="delete-button"
                          aria-label="Delete todo"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            ) : activeTab === 'dashboard' ? (
              /* Dashboard */
              <Dashboard />
            ) : (
              /* History View */
              <div className="history-view">
                {historyLoading ? (
                  <div className="loading">
                    <div className="spinner"></div>
                    Loading history...
                  </div>
                ) : history.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">📅</div>
                    <h3>No history yet</h3>
                    <p>Start creating and completing todos to see your history!</p>
                  </div>
                ) : (
                  history.map((day) => (
                    <div key={day.date} className="history-day">
                      <div className="history-date">
                        <h3>{new Date(day.date).toLocaleDateString('en-US', { 
                          weekday: 'long', 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}</h3>
                        <div className="day-stats">
                          <span className="stat">✨ {day.created_count} created</span>
                          <span className="stat">✅ {day.completed_count} completed</span>
                        </div>
                      </div>
                      <div className="history-todos">
                        {day.todos.map((todo) => (
                          <div key={`${day.date}-${todo.id}`} className="history-todo">
                            <div className={`activity-icon ${todo.activity_type}`}>
                              {todo.activity_type === 'created' ? '✨' : 
                               todo.activity_type === 'completed' ? '✅' : '🌟'}
                            </div>
                            <div className="history-todo-content">
                              <span className="history-todo-text">{todo.task}</span>
                              <span className="history-activity-type">
                                {todo.activity_type === 'created' ? 'Created' :
                                 todo.activity_type === 'completed' ? 'Completed' : 'Created & Completed'}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <footer className="footer">
            <p>Tap on a task to mark it as complete</p>
          </footer>
        </div>
      </div>

      {/* Pomodoro Timer Modal */}
      {showPomodoro && selectedTodoForFocus && (
        <PomodoroTimer
          todo={selectedTodoForFocus}
          onComplete={completeFocusSession}
          onClose={closeFocusMode}
        />
      )}
    </div>
  );
}

export default App;
