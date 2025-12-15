
import sqlite3
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def inspect_points():
    print("🔍 Inspecting User Points...\n")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        c.execute("SELECT username, puntos_totales FROM users")
        users = c.fetchall()
        
        print(f"{'Username':<20} | {'Puntos Totales'}")
        print("-" * 35)
        
        found_50 = False
        for u in users:
            points = u[1]
            print(f"{u[0]:<20} | {points}")
            if points == 50:
                found_50 = True
                
        if found_50:
            print("\n✅ Found user(s) with 50 points.")
        else:
            print("\n❌ No user found with exactly 50 points.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_points()
