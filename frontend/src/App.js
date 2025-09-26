import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://127.0.0.1:5000';

function App() {
  const [todos, setTodos] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0 });
  const [activeTab, setActiveTab] = useState('todos'); // 'todos' or 'history'
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

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
      const response = await axios.post(`${API_URL}/todos`, {
        task: inputValue.trim()
      });
      setTodos([response.data, ...todos]);
      setInputValue('');
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

  useEffect(() => {
    fetchTodos();
    fetchStats();
    if (activeTab === 'history') {
      fetchHistory();
    }
  }, [activeTab]);

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">
            <span className="title-icon">📋</span>
            All my tasks
          </h1>
          <p className="subtitle">Stay organized and focused</p>
        </header>

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
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <span>📅</span> History
          </button>
        </div>

        {/* Add Todo Form - only show on todos tab */}
        {activeTab === 'todos' && (
          <form onSubmit={addTodo} className="todo-form">
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
          </form>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Main Content */}
        <div className="main-content">
          {activeTab === 'todos' ? (
            /* Todo List */
            <div className="todo-list">
              {loading ? (
                <div className="loading">
                  <div className="spinner"></div>
                  Loading todos...
                </div>
              ) : todos.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">🎯</div>
                  <h3>Add your first task</h3>
                  <p>Time to add your first tasks</p>
                </div>
              ) : (
                todos.map((todo) => (
                  <div
                    key={todo.id}
                    className={`todo-item ${todo.completed ? 'completed' : ''}`}
                  >
                    <div className="todo-content" onClick={() => toggleTodo(todo.id)}>
                      <div className="checkbox">
                        {todo.completed && <span className="checkmark">✓</span>}
                      </div>
                      <div className="todo-details">
                        <span className="todo-text">{todo.task}</span>
                        <div className="todo-timestamps">
                          <span className="created-at">
                            ➕ Created {formatRelativeTime(todo.created_at)}
                          </span>
                          {todo.completed_at && (
                            <span className="completed-at">
                              ✅ Completed {formatRelativeTime(todo.completed_at)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => deleteTodo(todo.id)}
                      className="delete-button"
                      aria-label="Delete todo"
                    >
                      ×
                    </button>
                  </div>
                ))
              )}
            </div>
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
  );
}

export default App;
