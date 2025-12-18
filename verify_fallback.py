import db_config
import auth
import sqlite3

def verify_fallback():
    print("🧪 Verifying SQLite Fallback...")
    
    # 1. Check connection type
    conn = db_config.get_connection()
    print(f"Connection type: {type(conn)}")
    
    if isinstance(conn, sqlite3.Connection):
        print("✅ Correctly using SQLite connection (Fallback works)")
    else:
        print(f"❌ Unexpected connection type: {type(conn)}")
    
    # 2. Check data access (auth module)
    try:
        # Try to get a user
        c = conn.cursor()
        c.execute("SELECT count(*) FROM users")
        count = c.fetchone()[0]
        print(f"✅ Can read from DB. Total users: {count}")
    except Exception as e:
        print(f"❌ Failed to read from DB: {e}")

    # 3. Check schema initialization (idempotency)
    try:
        auth.init_db()
        print("✅ auth.init_db() ran successfully (Schema check)")
    except Exception as e:
        print(f"❌ auth.init_db() failed: {e}")

    conn.close()

if __name__ == "__main__":
    verify_fallback()
