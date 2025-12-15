
import sqlite3
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def reset_points(username):
    print(f"🔧 Resetting points for {username}...\n")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check current points
        c.execute("SELECT puntos_totales FROM users WHERE username = ?", (username,))
        current = c.fetchone()[0]
        print(f"Current Points: {current}")
        
        # Reset to 0
        c.execute("UPDATE users SET puntos_totales = 0 WHERE username = ?", (username,))
        conn.commit()
        print("✅ Points reset to 0.")
        
        # Verify
        c.execute("SELECT puntos_totales FROM users WHERE username = ?", (username,))
        new_points = c.fetchone()[0]
        print(f"New Points: {new_points}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_points("rvargas91")
