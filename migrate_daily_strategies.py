import sqlite3
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
os.makedirs(DB_PATH, exist_ok=True)
DB_NAME = os.path.join(DB_PATH, "users.db")

def migrate():
    """Add daily_strategies_count and last_strategy_date columns to users table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("🔄 Running migration: Add daily strategy limits...")
    
    # Check if columns exist
    c.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in c.fetchall()]
    
    if 'daily_strategies_count' not in columns:
        print("  ➕ Adding daily_strategies_count column...")
        c.execute("ALTER TABLE users ADD COLUMN daily_strategies_count INTEGER DEFAULT 0")
    else:
        print("  ✓ daily_strategies_count already exists")
        
    if 'last_strategy_date' not in columns:
        print("  ➕ Adding last_strategy_date column...")
        c.execute("ALTER TABLE users ADD COLUMN last_strategy_date TEXT")
    else:
        print("  ✓ last_strategy_date already exists")
    
    conn.commit()
    conn.close()
    print("✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
