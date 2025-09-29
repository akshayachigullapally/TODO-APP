#!/usr/bin/env python3
"""
PostgreSQL-Only Application Test Script
Tests the PostgreSQL-only TODO app configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_postgresql_requirements():
    """Test PostgreSQL-only application requirements"""
    print("🐘 PostgreSQL-Only Application Test")
    print("=" * 50)
    print("🧪 Testing Required PostgreSQL Configuration...")
    print("=" * 50)
    
    # Test 1: Environment Variables
    print("🔍 Environment Variables:")
    postgres_host = os.getenv('POSTGRES_HOST')
    postgres_db = os.getenv('POSTGRES_DB') 
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        print(f"   DATABASE_URL: {'✅ SET' if database_url else '❌ NOT SET'}")
        config_method = "DATABASE_URL"
    elif all([postgres_host, postgres_db, postgres_user, postgres_password]):
        print(f"   POSTGRES_HOST: {postgres_host}")
        print(f"   POSTGRES_DB: {postgres_db}")
        print(f"   POSTGRES_USER: {postgres_user}")
        print(f"   POSTGRES_PASSWORD: {'***' if postgres_password else 'NOT SET'}")
        print(f"   POSTGRES_PORT: {postgres_port}")
        config_method = "Individual Variables"
    else:
        print("   ❌ No PostgreSQL configuration found!")
        print("   🚫 APPLICATION WILL NOT START")
        return False
    
    print(f"   ✅ Configuration Method: {config_method}")
    print()
    
    # Test 2: psycopg2 Installation
    print("📦 Testing PostgreSQL Driver...")
    try:
        import psycopg2
        print("   ✅ psycopg2 installed successfully")
        print(f"   📄 Version: {psycopg2.__version__}")
    except ImportError:
        print("   ❌ psycopg2 NOT installed")
        print("   🚫 APPLICATION WILL NOT START")
        print("   💡 Install with: pip install psycopg2-binary")
        return False
    print()
    
    # Test 3: PostgreSQL Connection
    print("🔗 Testing PostgreSQL Connection...")
    try:
        if database_url:
            conn_string = database_url
        else:
            conn_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        
        import psycopg2
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Test database info
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"   ✅ Connected to PostgreSQL successfully")
        print(f"   🗄️  Database: {current_db}")
        print(f"   📋 Server Version: {version.split()[1]}")
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print("   🚫 APPLICATION WILL NOT START")
        return False
    print()
    
    # Test 4: Flask App Configuration
    print("🚀 Testing Flask App Configuration...")
    try:
        from app import app, db
        
        with app.app_context():
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   🔗 Database URL configured: {db_url.split('@')[0]}@***")
            print("   ✅ Flask app loaded successfully")
            print("   ✅ SQLAlchemy configured for PostgreSQL")
            
    except Exception as e:
        print(f"   ❌ Flask configuration failed: {str(e)}")
        return False
    print()
    
    return True

def test_database_operations():
    """Test basic database operations"""
    print("📊 Testing Database Operations...")
    print("=" * 50)
    
    try:
        from app import app, db, Todo
        
        with app.app_context():
            # Test table creation
            print("🏗️  Testing table creation...")
            db.create_all()
            print("   ✅ Tables created/verified")
            
            # Test insert
            print("📝 Testing data insertion...")
            test_todo = Todo(
                task="PostgreSQL Test Task",
                category="Test",
                priority="High"
            )
            db.session.add(test_todo)
            db.session.commit()
            print(f"   ✅ Test todo created with ID: {test_todo.id}")
            
            # Test query
            print("🔍 Testing data retrieval...")
            todos = Todo.query.all()
            print(f"   ✅ Found {len(todos)} todos in database")
            
            # Test update
            print("✏️  Testing data update...")
            test_todo.completed = True
            db.session.commit()
            print("   ✅ Todo updated successfully")
            
            # Test delete
            print("🗑️  Testing data deletion...")
            db.session.delete(test_todo)
            db.session.commit()
            print("   ✅ Test todo deleted successfully")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Database operation failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print()
    
    # Test PostgreSQL requirements
    config_test = test_postgresql_requirements()
    
    if config_test:
        # Test database operations
        db_test = test_database_operations()
        
        # Final results
        print("📊 Test Results:")
        print("=" * 50)
        print(f"PostgreSQL Configuration: {'✅ PASS' if config_test else '❌ FAIL'}")
        print(f"Database Operations:     {'✅ PASS' if db_test else '❌ FAIL'}")
        print()
        
        if config_test and db_test:
            print("🎉 All tests passed! Your PostgreSQL-only TODO app is ready!")
            print()
            print("🚀 Start your app with:")
            print("   python app.py")
            print()
            print("🌐 Access your app:")
            print("   Frontend: http://localhost:3000")
            print("   Backend:  http://127.0.0.1:5000")
        else:
            print("❌ Some tests failed. Please fix the issues above.")
            sys.exit(1)
    else:
        print("❌ PostgreSQL configuration test failed.")
        print()
        print("🔧 Quick fixes:")
        print("- Run: start-postgres.bat (to start PostgreSQL with Docker)")
        print("- Copy: .env.example to .env and configure")
        print("- Install: pip install psycopg2-binary")
        sys.exit(1)

if __name__ == "__main__":
    main()