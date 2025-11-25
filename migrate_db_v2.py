import sqlite3
from datetime import datetime

DB_NAME = "users.db"

def migrate_database():
    """
    Migrates the users database to add new columns:
    - email (TEXT)
    - daily_request_limit (INTEGER, default 20)
    - failed_login_attempts (INTEGER, default 0)
    - lockout_until (TEXT, nullable)
    """
    print("Starting database migration...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get current table info
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    print(f"Current columns: {columns}")
    
    # Add email column if not exists
    if 'email' not in columns:
        print("Adding 'email' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT ''")
        conn.commit()
        print("✓ 'email' column added")
    else:
        print("✓ 'email' column already exists")
    
    # Add daily_request_limit column if not exists
    if 'daily_request_limit' not in columns:
        print("Adding 'daily_request_limit' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN daily_request_limit INTEGER DEFAULT 20")
        conn.commit()
        print("✓ 'daily_request_limit' column added")
    else:
        print("✓ 'daily_request_limit' column already exists")
    
    # Add failed_login_attempts column if not exists
    if 'failed_login_attempts' not in columns:
        print("Adding 'failed_login_attempts' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0")
        conn.commit()
        print("✓ 'failed_login_attempts' column added")
    else:
        print("✓ 'failed_login_attempts' column already exists")
    
    # Add lockout_until column if not exists
    if 'lockout_until' not in columns:
        print("Adding 'lockout_until' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN lockout_until TEXT")
        conn.commit()
        print("✓ 'lockout_until' column added")
    else:
        print("✓ 'lockout_until' column already exists")
    
    # Verify migration
    cursor.execute("PRAGMA table_info(users)")
    new_columns = [row[1] for row in cursor.fetchall()]
    print(f"\nFinal columns: {new_columns}")
    
    # Show user count
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\nTotal users in database: {user_count}")
    
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
