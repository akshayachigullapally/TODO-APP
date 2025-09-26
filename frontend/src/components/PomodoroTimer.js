import React, { useState, useEffect, useRef } from 'react';
import './PomodoroTimer.css';

const PomodoroTimer = ({ todo, onComplete, onClose }) => {
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isRunning && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setIsRunning(false);
            setIsCompleted(true);
            
            // Show notification
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification('Pomodoro Complete!', {
                body: `Focus session completed for "${todo.task}"`,
                icon: '/favicon.ico'
              });
            }
            
            // Play sound (optional)
            try {
              const audio = new Audio('/notification.mp3');
              audio.play().catch(() => {
                // Ignore audio errors
              });
            } catch (error) {
              // Ignore audio errors
            }
            
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      clearInterval(intervalRef.current);
    }

    return () => clearInterval(intervalRef.current);
  }, [isRunning, timeLeft, todo.task]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStart = () => {
    setIsRunning(true);
  };

  const handlePause = () => {
    setIsRunning(false);
  };

  const handleReset = () => {
    setIsRunning(false);
    setTimeLeft(25 * 60);
    setIsCompleted(false);
  };

  const handleComplete = () => {
    onComplete();
    onClose();
  };

  const progressPercentage = ((25 * 60 - timeLeft) / (25 * 60)) * 100;

  return (
    <div className="pomodoro-overlay">
      <div className="pomodoro-modal">
        <div className="pomodoro-header">
          <h3>🍅 Focus Mode</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="pomodoro-content">
          <div className="task-info">
            <h4>{todo.task}</h4>
            <p>Stay focused for 25 minutes</p>
          </div>
          
          <div className="timer-display">
            <div className="circular-progress">
              <svg className="progress-circle" width="200" height="200">
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="var(--border-secondary)"
                  strokeWidth="8"
                />
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="var(--primary-blue)"
                  strokeWidth="8"
                  strokeDasharray="565.48"
                  strokeDashoffset={565.48 - (565.48 * progressPercentage) / 100}
                  className="progress-bar"
                />
              </svg>
              <div className="timer-text">
                <span className="time">{formatTime(timeLeft)}</span>
                <span className="label">
                  {isCompleted ? 'Complete!' : isRunning ? 'Focus Time' : 'Ready?'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="timer-controls">
            {!isCompleted ? (
              <>
                {!isRunning ? (
                  <button 
                    className="control-button start" 
                    onClick={handleStart}
                    disabled={timeLeft === 0}
                  >
                    ▶️ Start
                  </button>
                ) : (
                  <button className="control-button pause" onClick={handlePause}>
                    ⏸️ Pause
                  </button>
                )}
                <button className="control-button reset" onClick={handleReset}>
                  🔄 Reset
                </button>
              </>
            ) : (
              <div className="completion-actions">
                <p className="completion-message">🎉 Great job! You stayed focused for 25 minutes!</p>
                <div className="completion-buttons">
                  <button className="control-button complete" onClick={handleComplete}>
                    ✅ Mark Task Complete
                  </button>
                  <button className="control-button secondary" onClick={handleReset}>
                    🔄 Start Another Session
                  </button>
                </div>
              </div>
            )}
          </div>
          
          <div className="timer-info">
            <div className="info-item">
              <span className="info-label">Session:</span>
              <span className="info-value">25 minutes</span>
            </div>
            <div className="info-item">
              <span className="info-label">Technique:</span>
              <span className="info-value">Pomodoro</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PomodoroTimer;