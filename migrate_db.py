import sqlite3
from datetime import datetime, timedelta

def migrate_database():
    """
    Migrates the users.db database to add subscription and usage tracking columns.
    This script is safe to run multiple times - it will only add columns if they don't exist.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Get current table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add start_date column if it doesn't exist
    if 'start_date' not in columns:
        print("Adding 'start_date' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN start_date TEXT")
        
        # Set start_date for existing users to now
        now = datetime.now().isoformat()
        cursor.execute("UPDATE users SET start_date = ? WHERE start_date IS NULL", (now,))
        print("✓ Added 'start_date' column and set default values")
    else:
        print("✓ 'start_date' column already exists")
    
    # Add expiration_date column if it doesn't exist
    if 'expiration_date' not in columns:
        print("Adding 'expiration_date' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN expiration_date TEXT")
        
        # Set expiration_date for existing users to 7 days from now (free trial)
        expiration = (datetime.now() + timedelta(days=7)).isoformat()
        cursor.execute("UPDATE users SET expiration_date = ? WHERE expiration_date IS NULL", (expiration,))
        print("✓ Added 'expiration_date' column and set 7-day trial for existing users")
    else:
        print("✓ 'expiration_date' column already exists")
    
    # Add requests_today column if it doesn't exist
    if 'requests_today' not in columns:
        print("Adding 'requests_today' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN requests_today INTEGER DEFAULT 0")
        cursor.execute("UPDATE users SET requests_today = 0 WHERE requests_today IS NULL")
        print("✓ Added 'requests_today' column and set default values")
    else:
        print("✓ 'requests_today' column already exists")
    
    # Add last_request_date column if it doesn't exist
    if 'last_request_date' not in columns:
        print("Adding 'last_request_date' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN last_request_date TEXT")
        print("✓ Added 'last_request_date' column")
    else:
        print("✓ 'last_request_date' column already exists")
    
    # Commit changes
    conn.commit()
    
    # Verify final structure
    cursor.execute("PRAGMA table_info(users)")
    final_columns = [column[1] for column in cursor.fetchall()]
    print(f"\nFinal columns: {final_columns}")
    
    # Show sample data
    cursor.execute("SELECT username, start_date, expiration_date, requests_today, last_request_date FROM users LIMIT 3")
    print("\nSample user data:")
    for row in cursor.fetchall():
        print(f"  User: {row[0]}, Start: {row[1]}, Expires: {row[2]}, Requests: {row[3]}, Last: {row[4]}")
    
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
