import sqlite3
import os
from datetime import datetime

def migrate_estrategias():
    """
    Creates the estrategias table for storing user strategies.
    This script is safe to run multiple times - it will only create the table if it doesn't exist.
    """
    # Use same DB path logic as auth.py
    DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
    os.makedirs(DB_PATH, exist_ok=True)
    DB_NAME = os.path.join(DB_PATH, "users.db")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Starting estrategias table migration...")
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estrategias'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        print("Creating 'estrategias' table...")
        cursor.execute('''
            CREATE TABLE estrategias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                avatar TEXT,
                embudo TEXT,
                ads TEXT,
                objeciones TEXT,
                whatsapp TEXT,
                acciones_diarias TEXT,
                kpis TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')
        
        # Create index for faster lookups by user_id
        cursor.execute('CREATE INDEX idx_estrategias_user_id ON estrategias(user_id)')
        
        print("✓ Created 'estrategias' table with index")
    else:
        print("✓ 'estrategias' table already exists")
    
    # Commit changes
    conn.commit()
    
    # Verify table structure
    cursor.execute("PRAGMA table_info(estrategias)")
    columns = cursor.fetchall()
    print(f"\nTable structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Show count
    cursor.execute("SELECT COUNT(*) FROM estrategias")
    count = cursor.fetchone()[0]
    print(f"\nCurrent strategies stored: {count}")
    
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate_estrategias()
