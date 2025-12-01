import sqlite3
import os
from datetime import datetime

def migrate_historial_secciones():
    """
    Creates the historial_secciones table for storing section interaction history.
    This script is safe to run multiple times - it will only create the table if it doesn't exist.
    """
    # Use same DB path logic as auth.py
    DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
    os.makedirs(DB_PATH, exist_ok=True)
    DB_NAME = os.path.join(DB_PATH, "users.db")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print("Starting historial_secciones table migration...")
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historial_secciones'")
    table_exists = cursor.fetchone() is not None
    
    if not table_exists:
        print("Creating 'historial_secciones' table...")
        cursor.execute('''
            CREATE TABLE historial_secciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                seccion TEXT NOT NULL,
                tipo TEXT NOT NULL,
                contenido TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for faster lookups
        cursor.execute('CREATE INDEX idx_historial_user_id ON historial_secciones(user_id)')
        cursor.execute('CREATE INDEX idx_historial_seccion ON historial_secciones(user_id, seccion)')
        cursor.execute('CREATE INDEX idx_historial_timestamp ON historial_secciones(timestamp)')
        
        print("✓ Created 'historial_secciones' table with indexes")
    else:
        print("✓ 'historial_secciones' table already exists")
    
    # Commit changes
    conn.commit()
    
    # Verify table structure
    cursor.execute("PRAGMA table_info(historial_secciones)")
    columns = cursor.fetchall()
    print(f"\nTable structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Show count
    cursor.execute("SELECT COUNT(*) FROM historial_secciones")
    count = cursor.fetchone()[0]
    print(f"\nCurrent history entries: {count}")
    
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate_historial_secciones()
