"""
Auto Database Initialization
This module checks if the database needs initialization and runs it automatically
"""

import sqlite3
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
os.makedirs(DB_PATH, exist_ok=True)
DB_NAME = os.path.join(DB_PATH, "users.db")

def needs_initialization():
    """Check if database needs initialization."""
    # If database doesn't exist, needs init
    if not os.path.exists(DB_NAME):
        return True
    
    # If database exists but is empty or missing tables, needs init
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check if users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            conn.close()
            return True
        
        # Check if users table has required columns
        c.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in c.fetchall()}
        
        required_columns = {
            'username', 'password', 'puntos_totales', 'nivel', 
            'racha_actual', 'ai_requests_today', 'plan_actual'
        }
        
        if not required_columns.issubset(columns):
            conn.close()
            return True
        
        conn.close()
        return False
        
    except Exception as e:
        print(f"Error checking database: {e}")
        return True

def auto_initialize():
    """Automatically initialize database if needed."""
    if needs_initialization():
        print("🔄 Database needs initialization, running init_db...")
        try:
            import init_db
            init_db.init_complete_database()
            print("✅ Database initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return False
    else:
        print("✅ Database already initialized")
        return True

if __name__ == "__main__":
    auto_initialize()
