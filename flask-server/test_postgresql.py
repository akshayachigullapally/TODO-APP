#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_postgresql_connection():
    """Test PostgreSQL connection with current configuration"""
    print("🧪 Testing PostgreSQL Connection...")
    print("=" * 50)
    
    # Check environment variables
    postgres_host = os.getenv('POSTGRES_HOST')
    postgres_db = os.getenv('POSTGRES_DB')
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    database_url = os.getenv('DATABASE_URL')
    
    print("🔍 Environment Variables:")
    print(f"   POSTGRES_HOST: {postgres_host or 'Not set'}")
    print(f"   POSTGRES_DB: {postgres_db or 'Not set'}")
    print(f"   POSTGRES_USER: {postgres_user or 'Not set'}")
    print(f"   POSTGRES_PASSWORD: {'***' if postgres_password else 'Not set'}")
    print(f"   POSTGRES_PORT: {postgres_port}")
    print(f"   DATABASE_URL: {'***' if database_url else 'Not set'}")
    print()
    
    # Test psycopg2 import
    print("📦 Testing psycopg2 import...")
    try:
        import psycopg2
        print("   ✅ psycopg2 is installed!")
        print(f"   📋 Version: {psycopg2.__version__}")
    except ImportError as e:
        print("   ❌ psycopg2 not installed")
        print("   💡 Install with: pip install psycopg2-binary")
        print("   🔄 App will use SQLite as fallback")
        return False
    
    print()
    
    # Test connection
    if database_url:
        connection_string = database_url
        if connection_string.startswith('postgres://'):
            connection_string = connection_string.replace('postgres://', 'postgresql://', 1)
    elif all([postgres_host, postgres_db, postgres_user, postgres_password]):
        connection_string = f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}'
    else:
        print("❌ No PostgreSQL configuration found")
        print("💡 Set up environment variables or DATABASE_URL")
        return False
    
    print("🔌 Testing database connection...")
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"   ✅ Connection successful!")
        print(f"   🐘 PostgreSQL version: {version}")
        
        # Test database name
        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()[0]
        print(f"   📊 Connected to database: {db_name}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 Check your PostgreSQL server is running")
        print("   💡 Verify your connection credentials")
        return False
    
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def test_flask_app():
    """Test Flask app configuration"""
    print("\n🚀 Testing Flask App Configuration...")
    print("=" * 50)
    
    try:
        # Import after adding current directory to path
        sys.path.insert(0, os.path.dirname(__file__))
        from app import get_database_url, app
        
        db_url = get_database_url()
        print(f"🔗 Database URL: {db_url}")
        
        if db_url.startswith('postgresql://'):
            print("   ✅ Flask configured for PostgreSQL")
        else:
            print("   📁 Flask configured for SQLite (fallback)")
        
        print("   ✅ Flask app loaded successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Flask app error: {e}")
        return False

if __name__ == "__main__":
    print("🐘 PostgreSQL Integration Test")
    print("=" * 50)
    
    # Test PostgreSQL connection
    postgres_ok = test_postgresql_connection()
    
    # Test Flask configuration
    flask_ok = test_flask_app()
    
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"PostgreSQL Connection: {'✅ PASS' if postgres_ok else '❌ FAIL (will use SQLite)'}")
    print(f"Flask Configuration:   {'✅ PASS' if flask_ok else '❌ FAIL'}")
    
    if postgres_ok and flask_ok:
        print("\n🎉 All tests passed! Your PostgreSQL integration is working!")
    elif flask_ok:
        print("\n⚠️ PostgreSQL not available, but SQLite fallback is working")
        print("💡 Install PostgreSQL and psycopg2-binary for full functionality")
    else:
        print("\n❌ Setup issues detected. Check the errors above.")
    
    print("\n🔧 Quick Fixes:")
    print("- Install PostgreSQL driver: pip install psycopg2-binary")
    print("- Start PostgreSQL with Docker: start-postgres.bat")
    print("- Check .env file for correct credentials")