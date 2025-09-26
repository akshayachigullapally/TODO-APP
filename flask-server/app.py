from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

# Routes
@app.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    try:
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        return jsonify([todo.to_dict() for todo in todos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    try:
        data = request.get_json()
        
        if not data or 'task' not in data or not data['task'].strip():
            return jsonify({'error': 'Task is required'}), 400
        
        new_todo = Todo(task=data['task'].strip())
        db.session.add(new_todo)
        db.session.commit()
        
        return jsonify(new_todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Toggle completed status for a todo"""
    try:
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({'error': 'Todo not found'}), 404
        
        # Toggle completion status
        todo.completed = not todo.completed
        
        # Set or clear completed_at timestamp
        if todo.completed:
            todo.completed_at = datetime.utcnow()
        else:
            todo.completed_at = None
        
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
    """Get todo statistics"""
    try:
        total = Todo.query.count()
        completed = Todo.query.filter_by(completed=True).count()
        pending = total - completed
        
        return jsonify({
            'total': total,
            'completed': completed,
            'pending': pending
        }), 200
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
        # Check if completed_at column exists
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(todo)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'completed_at' not in columns:
                print("Adding completed_at column...")
                conn.execute(db.text("ALTER TABLE todo ADD COLUMN completed_at DATETIME"))
                conn.commit()
                print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration error: {e}")

with app.app_context():
    db.create_all()
    migrate_database()

if __name__ == '__main__':
    app.run(debug=True, port=5000)