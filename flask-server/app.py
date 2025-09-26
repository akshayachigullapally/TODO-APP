from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os

# Initialize Flask app
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "todos.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    category = db.Column(db.String(50), nullable=True, default='General')
    priority = db.Column(db.String(10), nullable=False, default='Medium')
    due_date = db.Column(db.DateTime, nullable=True)
    recurrence = db.Column(db.String(20), nullable=False, default='none')
    parent_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=True)  # For recurring tasks
    
    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'category': self.category,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'recurrence': self.recurrence,
            'parent_id': self.parent_id
        }

# Routes
@app.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos sorted by priority and creation date"""
    try:
        # Define priority order for sorting
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        
        # Get all todos
        todos = Todo.query.all()
        
        # Sort by priority first, then by creation date (newest first)
        sorted_todos = sorted(todos, key=lambda x: (
            priority_order.get(x.priority, 2),  # Default to Medium if priority not found
            -int(x.created_at.timestamp())  # Negative for descending order
        ))
        
        return jsonify([todo.to_dict() for todo in sorted_todos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo with category, priority, due date, and recurrence support"""
    try:
        data = request.get_json()
        
        if not data or 'task' not in data or not data['task'].strip():
            return jsonify({'error': 'Task is required'}), 400
        
        # Validate priority if provided
        valid_priorities = ['High', 'Medium', 'Low']
        priority = data.get('priority', 'Medium')
        if priority not in valid_priorities:
            return jsonify({'error': 'Priority must be one of: High, Medium, Low'}), 400
        
        # Validate recurrence if provided
        valid_recurrences = ['none', 'daily', 'weekly', 'monthly']
        recurrence = data.get('recurrence', 'none')
        if recurrence not in valid_recurrences:
            return jsonify({'error': 'Recurrence must be one of: none, daily, weekly, monthly'}), 400
        
        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO 8601 format'}), 400
        
        # Create new todo
        new_todo = Todo(
            task=data['task'].strip(),
            category=data.get('category', 'General'),
            priority=priority,
            due_date=due_date,
            recurrence=recurrence,
            parent_id=data.get('parent_id')
        )
        
        db.session.add(new_todo)
        db.session.commit()
        
        return jsonify(new_todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def calculate_next_due_date(current_due_date, recurrence):
    """Calculate the next due date based on recurrence pattern"""
    if not current_due_date or recurrence == 'none':
        return None
    
    if recurrence == 'daily':
        return current_due_date + timedelta(days=1)
    elif recurrence == 'weekly':
        return current_due_date + timedelta(weeks=1)
    elif recurrence == 'monthly':
        # Add one month
        next_month = current_due_date.month + 1
        next_year = current_due_date.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        # Handle day overflow (e.g., Jan 31 -> Feb 28/29)
        try:
            return current_due_date.replace(year=next_year, month=next_month)
        except ValueError:
            # If the day doesn't exist in the next month, use the last day of that month
            import calendar
            last_day = calendar.monthrange(next_year, next_month)[1]
            return current_due_date.replace(year=next_year, month=next_month, day=last_day)
    
    return None

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo (toggle completion or update fields) with recurring task support"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        data = request.get_json()
        
        # If no data provided, just toggle completion status (legacy behavior)
        if not data:
            was_completed_before = todo.completed
            todo.completed = not todo.completed
            if todo.completed:
                todo.completed_at = datetime.utcnow()
                
                # Handle recurring tasks
                if not was_completed_before and todo.recurrence != 'none':
                    next_due_date = calculate_next_due_date(todo.due_date, todo.recurrence)
                    
                    # Create next occurrence
                    next_todo = Todo(
                        task=todo.task,
                        category=todo.category,
                        priority=todo.priority,
                        due_date=next_due_date,
                        recurrence=todo.recurrence,
                        parent_id=todo.id
                    )
                    db.session.add(next_todo)
            else:
                todo.completed_at = None
        else:
            # Update specific fields if provided
            if 'completed' in data:
                was_completed_before = todo.completed
                todo.completed = data['completed']
                if todo.completed:
                    todo.completed_at = datetime.utcnow()
                    
                    # Handle recurring tasks
                    if not was_completed_before and todo.recurrence != 'none':
                        next_due_date = calculate_next_due_date(todo.due_date, todo.recurrence)
                        
                        # Create next occurrence
                        next_todo = Todo(
                            task=todo.task,
                            category=todo.category,
                            priority=todo.priority,
                            due_date=next_due_date,
                            recurrence=todo.recurrence,
                            parent_id=todo.id
                        )
                        db.session.add(next_todo)
                else:
                    todo.completed_at = None
            
            if 'task' in data and data['task'].strip():
                todo.task = data['task'].strip()
            
            if 'category' in data:
                todo.category = data['category']
            
            if 'priority' in data:
                valid_priorities = ['High', 'Medium', 'Low']
                if data['priority'] in valid_priorities:
                    todo.priority = data['priority']
                else:
                    return jsonify({'error': 'Priority must be one of: High, Medium, Low'}), 400
            
            if 'recurrence' in data:
                valid_recurrences = ['none', 'daily', 'weekly', 'monthly']
                if data['recurrence'] in valid_recurrences:
                    todo.recurrence = data['recurrence']
                else:
                    return jsonify({'error': 'Recurrence must be one of: none, daily, weekly, monthly'}), 400
            
            if 'due_date' in data:
                if data['due_date']:
                    try:
                        todo.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                    except ValueError:
                        return jsonify({'error': 'Invalid due_date format. Use ISO 8601 format'}), 400
                else:
                    todo.due_date = None
        
        db.session.commit()
        
        return jsonify(todo.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo by ID"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify({'message': 'Todo deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/todos/stats', methods=['GET'])
def get_stats():
    """Get todo statistics including priority and category breakdown"""
    try:
        total = Todo.query.count()
        completed = Todo.query.filter_by(completed=True).count()
        pending = total - completed
        
        # Priority breakdown
        high_priority = Todo.query.filter_by(priority='High', completed=False).count()
        medium_priority = Todo.query.filter_by(priority='Medium', completed=False).count()
        low_priority = Todo.query.filter_by(priority='Low', completed=False).count()
        
        # Category breakdown
        categories = db.session.query(
            Todo.category, db.func.count(Todo.id).label('count')
        ).filter_by(completed=False).group_by(Todo.category).all()
        
        category_stats = {category: count for category, count in categories}
        
        # Overdue tasks
        now = datetime.utcnow()
        overdue = Todo.query.filter(
            Todo.due_date < now,
            Todo.completed == False
        ).count()
        
        return jsonify({
            'total': total,
            'completed': completed,
            'pending': pending,
            'priority_breakdown': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            },
            'category_stats': category_stats,
            'overdue': overdue
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive analytics data for dashboard"""
    try:
        # Basic stats
        total = Todo.query.count()
        completed = Todo.query.filter_by(completed=True).count()
        pending = total - completed
        
        # Priority breakdown (pending tasks only)
        high_priority = Todo.query.filter_by(priority='High', completed=False).count()
        medium_priority = Todo.query.filter_by(priority='Medium', completed=False).count()
        low_priority = Todo.query.filter_by(priority='Low', completed=False).count()
        
        # Category breakdown (all tasks)
        categories = db.session.query(
            Todo.category, 
            db.func.count(Todo.id).label('count'),
            db.func.sum(db.case([(Todo.completed == True, 1)], else_=0)).label('completed_count')
        ).group_by(Todo.category).all()
        
        category_stats = []
        for category, total_count, completed_count in categories:
            category_stats.append({
                'category': category,
                'total': total_count,
                'completed': completed_count or 0,
                'pending': total_count - (completed_count or 0)
            })
        
        # Overdue tasks
        now = datetime.utcnow()
        overdue = Todo.query.filter(
            Todo.due_date < now,
            Todo.completed == False
        ).count()
        
        # Average completion time (only for completed tasks with completion time)
        completed_todos_with_time = Todo.query.filter(
            Todo.completed == True,
            Todo.completed_at.isnot(None)
        ).all()
        
        completion_times = []
        for todo in completed_todos_with_time:
            time_diff = todo.completed_at - todo.created_at
            completion_times.append(time_diff.total_seconds() / 3600)  # Convert to hours
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Tasks completed per day (last 7 days)
        seven_days_ago = now - timedelta(days=7)
        daily_completions = []
        
        for i in range(7):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            completed_count = Todo.query.filter(
                Todo.completed_at >= day_start,
                Todo.completed_at < day_end
            ).count()
            
            created_count = Todo.query.filter(
                Todo.created_at >= day_start,
                Todo.created_at < day_end
            ).count()
            
            daily_completions.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'day': day_start.strftime('%A'),
                'completed': completed_count,
                'created': created_count
            })
        
        # Reverse to show oldest to newest
        daily_completions.reverse()
        
        # Recurring tasks stats
        recurring_active = Todo.query.filter(
            Todo.recurrence != 'none',
            Todo.completed == False
        ).count()
        
        # Productivity metrics
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_completed = Todo.query.filter(
            Todo.completed_at >= today_start,
            Todo.completed == True
        ).count()
        
        today_created = Todo.query.filter(
            Todo.created_at >= today_start
        ).count()
        
        return jsonify({
            'overview': {
                'total': total,
                'completed': completed,
                'pending': pending,
                'overdue': overdue,
                'completion_rate': round((completed / total * 100) if total > 0 else 0, 1)
            },
            'priority_breakdown': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            },
            'category_stats': category_stats,
            'time_metrics': {
                'average_completion_time_hours': round(avg_completion_time, 2),
                'average_completion_time_days': round(avg_completion_time / 24, 2)
            },
            'daily_activity': daily_completions,
            'productivity': {
                'today_completed': today_completed,
                'today_created': today_created,
                'today_completion_rate': round((today_completed / today_created * 100) if today_created > 0 else 0, 1)
            },
            'recurring_tasks': {
                'active_recurring': recurring_active
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique categories"""
    try:
        categories = db.session.query(Todo.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        # Add default categories if no todos exist
        if not category_list:
            category_list = ['General', 'Work', 'Personal', 'Shopping', 'Health']
        
        return jsonify(category_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/<date_str>', methods=['GET'])
def get_history(date_str):
    """Get todos created or completed on a specific date (YYYY-MM-DD)"""
    try:
        # Parse the date string
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Find todos created on this date
        created_todos = Todo.query.filter(
            db.func.date(Todo.created_at) == target_date
        ).all()
        
        # Find todos completed on this date
        completed_todos = Todo.query.filter(
            Todo.completed_at.isnot(None),
            db.func.date(Todo.completed_at) == target_date
        ).all()
        
        # Combine and deduplicate (a todo might be created and completed on the same day)
        all_todos = {}
        
        for todo in created_todos:
            all_todos[todo.id] = {
                **todo.to_dict(),
                'activity_type': 'created'
            }
        
        for todo in completed_todos:
            if todo.id in all_todos:
                # Todo was both created and completed on this date
                all_todos[todo.id]['activity_type'] = 'created_and_completed'
            else:
                all_todos[todo.id] = {
                    **todo.to_dict(),
                    'activity_type': 'completed'
                }
        
        # Convert to list and sort by creation time
        result = list(all_todos.values())
        result.sort(key=lambda x: x['created_at'])
        
        return jsonify({
            'date': date_str,
            'todos': result,
            'summary': {
                'total_activities': len(result),
                'created': len(created_todos),
                'completed': len(completed_todos)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_all_history():
    """Get all todos with their history, grouped by date"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 30, type=int)  # Default to last 30 days
        
        # Get all todos ordered by creation date (most recent first)
        todos = Todo.query.order_by(Todo.created_at.desc()).limit(limit * 2).all()
        
        # Group by date
        history_by_date = {}
        
        for todo in todos:
            # Add to created date
            created_date = todo.created_at.date().isoformat()
            if created_date not in history_by_date:
                history_by_date[created_date] = {
                    'date': created_date,
                    'todos': [],
                    'created_count': 0,
                    'completed_count': 0
                }
            
            activity_type = 'created'
            history_by_date[created_date]['created_count'] += 1
            
            # Check if also completed on the same date
            if todo.completed_at and todo.completed_at.date().isoformat() == created_date:
                activity_type = 'created_and_completed'
                history_by_date[created_date]['completed_count'] += 1
            
            # Add to completed date if different from created date
            elif todo.completed_at:
                completed_date = todo.completed_at.date().isoformat()
                if completed_date not in history_by_date:
                    history_by_date[completed_date] = {
                        'date': completed_date,
                        'todos': [],
                        'created_count': 0,
                        'completed_count': 0
                    }
                history_by_date[completed_date]['completed_count'] += 1
                history_by_date[completed_date]['todos'].append({
                    **todo.to_dict(),
                    'activity_type': 'completed'
                })
            
            history_by_date[created_date]['todos'].append({
                **todo.to_dict(),
                'activity_type': activity_type
            })
        
        # Convert to sorted list (most recent first)
        result = sorted(history_by_date.values(), key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'history': result[:limit],
            'total_days': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
def migrate_database():
    """Handle database migrations for new columns"""
    try:
        # Check existing columns
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(todo)"))
            columns = [row[1] for row in result.fetchall()]
            
            # Add missing columns
            migrations = []
            
            if 'completed_at' not in columns:
                migrations.append("ALTER TABLE todo ADD COLUMN completed_at DATETIME")
                
            if 'category' not in columns:
                migrations.append("ALTER TABLE todo ADD COLUMN category VARCHAR(50) DEFAULT 'General'")
                
            if 'priority' not in columns:
                migrations.append("ALTER TABLE todo ADD COLUMN priority VARCHAR(10) DEFAULT 'Medium'")
                
            if 'due_date' not in columns:
                migrations.append("ALTER TABLE todo ADD COLUMN due_date DATETIME")
                
            if 'recurrence' not in columns:
                migrations.append("ALTER TABLE todo ADD COLUMN recurrence VARCHAR(20) DEFAULT 'none'")
                
            if 'parent_id' not in columns:
                migrations.append("ALTER TABLE todo ADD COLUMN parent_id INTEGER REFERENCES todo(id)")
            
            # Execute migrations
            for migration in migrations:
                print(f"Running migration: {migration}")
                conn.execute(db.text(migration))
                conn.commit()
                
            if migrations:
                print(f"Completed {len(migrations)} migrations successfully!")
            else:
                print("Database is up to date.")
                
    except Exception as e:
        print(f"Migration error: {e}")

with app.app_context():
    db.create_all()
    migrate_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)