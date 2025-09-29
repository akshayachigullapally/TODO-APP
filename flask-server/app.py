from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

def get_database_url():
    """Get PostgreSQL database URL - POSTGRESQL ONLY APPLICATION"""
    # PostgreSQL configuration from environment
    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_db = os.getenv('POSTGRES_DB', 'todo_db')
    postgres_user = os.getenv('POSTGRES_USER', 'postgres')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'admin')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    
    # Build PostgreSQL connection string
    postgres_url = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
    
    # Verify psycopg is available
    try:
        import psycopg
        print(f"🐘 PostgreSQL Driver: psycopg {psycopg.__version__}")
    except ImportError:
        print("❌ FATAL ERROR: psycopg not installed!")
        print("📦 Install with: pip install psycopg[binary]")
        raise ImportError("PostgreSQL driver (psycopg) is required for this application")
    
    return postgres_url

# PostgreSQL-Only Configuration
print("🐘 Starting PostgreSQL-Only TODO Application")
print("=" * 50)

try:
    # Get PostgreSQL connection string
    postgres_url = get_database_url()
    
    # Configure Flask for PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = postgres_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # Extract database info for display
    db_parts = postgres_url.replace('postgresql://', '').split('@')
    host_db = db_parts[1] if len(db_parts) > 1 else 'localhost:5432/todo_db'
    host, db_name = host_db.split('/', 1) if '/' in host_db else (host_db, 'todo_db')
    
    print(f"🐘 PostgreSQL Database: {db_name}")
    print(f"🌐 PostgreSQL Host: {host}")
    print(f"✅ PostgreSQL connection configured")
        
except Exception as e:
    print(f"❌ FATAL ERROR: {str(e)}")
    print("🚫 Cannot start without PostgreSQL connection")
    print("📋 Check your PostgreSQL server and credentials")
    exit(1)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# PostgreSQL-Optimized Todo Model
class Todo(db.Model):
    __tablename__ = 'todo'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    category = db.Column(db.String(50), nullable=True, default='General', index=True)
    priority = db.Column(db.String(10), nullable=False, default='Medium', index=True)
    due_date = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    recurrence = db.Column(db.String(20), nullable=False, default='none')
    parent_id = db.Column(db.Integer, db.ForeignKey('todo.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # PostgreSQL-specific constraints and indexes
    __table_args__ = (
        db.CheckConstraint("priority IN ('High', 'Medium', 'Low')", name='valid_priority'),
        db.CheckConstraint("recurrence IN ('none', 'daily', 'weekly', 'monthly')", name='valid_recurrence'),
        db.CheckConstraint("LENGTH(task) >= 1", name='task_not_empty'),
        db.Index('idx_todo_status_priority', 'completed', 'priority'),
        db.Index('idx_todo_category_created', 'category', 'created_at'),
    )
    
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
            priority_order.get(x.priority, 2),
            -int(x.created_at.timestamp())
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
            'category_stats': category_stats
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

# PostgreSQL-Only Database Operations
def initialize_postgresql():
    """Initialize PostgreSQL database with tables and indexes"""
    try:
        print("🔄 Initializing PostgreSQL database...")
        
        # Test connection first
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"📊 PostgreSQL Version: {version.split()[1]}")
        
        # Create all tables
        db.create_all()
        print("✅ PostgreSQL tables created/verified")
        
        # Create performance indexes
        create_postgresql_indexes()
        
        print("🐘 PostgreSQL database initialization complete!")
        
    except Exception as e:
        print(f"❌ PostgreSQL initialization failed: {e}")
        raise

def create_postgresql_indexes():
    """Create PostgreSQL performance indexes"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_todo_completed ON todo(completed)",
        "CREATE INDEX IF NOT EXISTS idx_todo_priority ON todo(priority)", 
        "CREATE INDEX IF NOT EXISTS idx_todo_category ON todo(category)",
        "CREATE INDEX IF NOT EXISTS idx_todo_due_date ON todo(due_date)",
        "CREATE INDEX IF NOT EXISTS idx_todo_created_at ON todo(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_todo_parent_id ON todo(parent_id)",
        "CREATE INDEX IF NOT EXISTS idx_todo_status_priority ON todo(completed, priority)",
        "CREATE INDEX IF NOT EXISTS idx_todo_category_created ON todo(category, created_at)"
    ]
    
    with db.engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(db.text(index_sql))
                conn.commit()
            except Exception:
                pass  # Index might already exist
    
    print("📈 PostgreSQL performance indexes created")

# Initialize PostgreSQL database
with app.app_context():
    initialize_postgresql()

if __name__ == '__main__':
    print("🚀 Starting PostgreSQL-Only TODO App Server...")
    print("🌐 Frontend: http://localhost:3000")
    print("🔗 Backend: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)