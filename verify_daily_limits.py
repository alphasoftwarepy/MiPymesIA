
import sqlite3
import os
import auth
from datetime import datetime

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def test_daily_limits():
    """Test daily strategy limit logic."""
    print("🧪 Starting Daily Strategy Limit Verification...\n")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Create a test user
    username = "test_limit_user"
    print(f"Creating test user: {username}")
    
    # Delete if exists
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    c.execute("DELETE FROM estrategias_v2 WHERE user_id = ?", (username,))
    conn.commit()
    conn.close()
    
    auth.create_user(username, "password123", "test@test.com", "Test Biz")
    auth.set_user_plan(username, "gratuito") # Limit: 1/day
    
    print("User created with 'gratuito' plan (Limit: 1 strategy/day)\n")
    
    # 2. Check initial state
    print("Checking initial state...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_strategies_count, last_strategy_date FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    print(f"Initial DB State: count={row[0]}, date={row[1]}")
    conn.close()
    
    # 3. Create 1st Strategy (Should Succeed)
    print("\nAttempting to create 1st strategy...")
    success, msg, _ = auth.create_estrategia(
        username, 
        "Strat 1", 
        "Product 1", 
        {"avatar": "test"}, 
        roadmap={"steps": []}
    )
    print(f"Result: {success} - {msg}")
    
    if not success:
        print("❌ FAILED: 1st strategy creation should have succeeded.")
        return

    # 4. Check state after 1st
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT daily_strategies_count, last_strategy_date FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    print(f"DB State after 1st: count={row[0]}, date={row[1]}")
    conn.close()
    
    # 5. Create 2nd Strategy (Should Fail)
    print("\nAttempting to create 2nd strategy (Over limit)...")
    success, msg, _ = auth.create_estrategia(
        username, 
        "Strat 2", 
        "Product 2", 
        {"avatar": "test"}, 
        roadmap={"steps": []}
    )
    print(f"Result: {success} - {msg}")
    
    if success:
        print("❌ FAILED: 2nd strategy creation should have been blocked.")
        return
    else:
        print("✅ BLOCKED: Correctly blocked by daily limit.")

    # 6. Simulate Admin Reset
    print("\nSimulating Admin Reset...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET daily_strategies_count = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    print("✅ Limits reset.")
    
    # 7. Create 2nd Strategy Again (Should Succeed)
    print("\nAttempting to create 2nd strategy after reset...")
    success, msg, _ = auth.create_estrategia(
        username, 
        "Strat 2", 
        "Product 2", 
        {"avatar": "test"}, 
        roadmap={"steps": []}
    )
    print(f"Result: {success} - {msg}")
    
    if success:
         print("✅ SUCCESS: Strategy created after reset.")
    else:
         print("❌ FAILED: Should have succeeded after reset.")

    # Clean up
    print("\nCleaning up...")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    print("\n✅ VERIFICATION COMPLETE")

if __name__ == "__main__":
    test_daily_limits()
