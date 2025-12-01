import sqlite3
from datetime import datetime

DB_NAME = 'users.db'

def migrate():
    """
    Adds conversaciones_archivadas table for storing compacted conversation summaries.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if table already exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversaciones_archivadas'")
        if c.fetchone():
            print("✅ Table 'conversaciones_archivadas' already exists. Skipping migration.")
            conn.close()
            return
        
        # Create conversaciones_archivadas table
        c.execute("""
            CREATE TABLE conversaciones_archivadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                seccion TEXT NOT NULL,
                resumen TEXT,
                mensajes_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                expandible BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(username)
            )
        """)
        
        print("✅ Created table: conversaciones_archivadas")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting migration: Add conversaciones_archivadas table...")
    migrate()
    print("✅ Migration script finished.")
