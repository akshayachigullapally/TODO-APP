import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import './Dashboard.css';

const API_URL = 'http://127.0.0.1:5000';

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/analytics`);
      setAnalytics(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>{error}</p>
        <button onClick={fetchAnalytics} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) return null;

  // Data for pie chart
  const pieData = [
    { name: 'Completed', value: analytics.overview.completed, color: '#34C759' },
    { name: 'Pending', value: analytics.overview.pending, color: '#FF9500' },
    { name: 'Overdue', value: analytics.overview.overdue, color: '#FF3B30' }
  ];

  // Data for priority chart
  const priorityData = [
    { name: 'High', value: analytics.priority_breakdown.high, color: '#FF3B30' },
    { name: 'Medium', value: analytics.priority_breakdown.medium, color: '#FF9500' },
    { name: 'Low', value: analytics.priority_breakdown.low, color: '#34C759' }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>📊 Analytics Dashboard</h2>
        <button onClick={fetchAnalytics} className="refresh-button">
          🔄 Refresh
        </button>
      </div>

      {/* Overview Stats */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <div className="stat-number">{analytics.overview.total}</div>
            <div className="stat-label">Total Tasks</div>
          </div>
        </div>
        
        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-number">{analytics.overview.completed}</div>
            <div className="stat-label">Completed</div>
          </div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <div className="stat-number">{analytics.overview.pending}</div>
            <div className="stat-label">Pending</div>
          </div>
        </div>
        
        <div className="stat-card danger">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-number">{analytics.overview.overdue}</div>
            <div className="stat-label">Overdue</div>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-number">
              {analytics.time_metrics.average_completion_time_days}d
            </div>
            <div className="stat-label">Avg Completion Time</div>
          </div>
        </div>

        <div className="stat-card accent">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-number">{analytics.overview.completion_rate}%</div>
            <div className="stat-label">Completion Rate</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Task Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Priority Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={priorityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#007AFF" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Activity Chart */}
      <div className="chart-container full-width">
        <h3>Daily Activity (Last 7 Days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={analytics.daily_activity}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="created" fill="#007AFF" name="Created" />
            <Bar dataKey="completed" fill="#34C759" name="Completed" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Category Breakdown */}
      {analytics.category_stats.length > 0 && (
        <div className="category-section">
          <h3>Category Breakdown</h3>
          <div className="category-grid">
            {analytics.category_stats.map((cat, index) => (
              <div key={index} className="category-card">
                <h4>{cat.category}</h4>
                <div className="category-stats">
                  <span className="category-total">Total: {cat.total}</span>
                  <span className="category-completed">Completed: {cat.completed}</span>
                  <span className="category-pending">Pending: {cat.pending}</span>
                </div>
                <div className="category-progress">
                  <div 
                    className="category-progress-bar"
                    style={{ 
                      width: `${cat.total > 0 ? (cat.completed / cat.total) * 100 : 0}%` 
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;