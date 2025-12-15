
import os
os.environ["OPENAI_API_KEY"] = "sk-dummy-key" # Avoid import error

import sqlite3
import auth
import tasks_manager
import time

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def verify_reset():
    print("🧪 Verifying Reset Progress Feature...\n")
    
    username = "test_reset_user"
    
    # 1. Setup User
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    # Create user with limits
    auth.create_user(username, "pass123", "reset@test.com", "Reset Biz")
    
    # Update user to have points and custom limits to verify they persist
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET puntos_totales = 100, 
            nivel = 5,
            daily_request_limit = 99,
            daily_strategies_count = 5
        WHERE username = ?
    """, (username,))
    conn.commit()
    conn.close()
    
    # Create a task
    tasks_manager.create_task(username, "Task to delete")
    
    # Verify initial state
    stats = tasks_manager.get_user_stats(username)
    print(f"Initial State: Points={stats['puntos']}, Level={stats['nivel']}")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_request_limit, daily_strategies_count FROM users WHERE username = ?", (username,))
    limits = c.fetchone()
    conn.close()
    print(f"Initial Limits: RequestLimit={limits[0]}, StrategyCount={limits[1]}")
    
    if stats['puntos'] != 100:
        print("❌ Setup failed (points incorrect).")
        return

    # 2. RUN RESET
    print("\n🔄 Running Reset Progress...")
    success = tasks_manager.reset_user_progress(username)
    
    if not success:
        print("❌ Reset function return False.")
        return
        
    # 3. Verify Post-Reset
    print("\n🔍 Verifying Post-Reset State...")
    
    # Check stats
    new_stats = tasks_manager.get_user_stats(username)
    print(f"New Stats: Points={new_stats['puntos']}, Level={new_stats['nivel']}")
    
    if new_stats['puntos'] != 0 or new_stats['nivel'] != 1:
        print("❌ Stats not reset correctly.")
    else:
        print("✅ Stats reset correctly.")
        
    # Check tasks
    tasks = tasks_manager.get_tasks_for_week(username)
    if len(tasks) > 0:
        print(f"❌ Tasks not deleted. Found {len(tasks)} tasks.")
    else:
        print("✅ All tasks deleted.")
        
    # Check limits (should be UNCHANGED)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_request_limit, daily_strategies_count FROM users WHERE username = ?", (username,))
    new_limits = c.fetchone()
    conn.close()
    print(f"New Limits: RequestLimit={new_limits[0]}, StrategyCount={new_limits[1]}")
    
    if new_limits[0] == 99 and new_limits[1] == 5:
        print("✅ Limits preserved correctly.")
    else:
        print("❌ Limits were modified! (Error)")

    # Cleanup
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    print("\n✅ Verification Complete.")

if __name__ == "__main__":
    verify_reset()
