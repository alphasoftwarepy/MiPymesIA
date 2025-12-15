
import sqlite3
import os
import auth
from auth_subscription import track_tokens
import time

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def verify_tracking():
    print("🧪 Verifying Token Tracking & Admin Panel Logic...\n")
    
    username = "test_token_user"
    
    # 1. Setup User
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    auth.create_user(username, "pass123", "token@test.com", "Token Biz")
    auth.set_user_plan(username, "prueba") # Limits: 3 strat, 10 AI
    
    # 2. Simulate Token Usage via track_tokens
    print(f"Simulating usage of 1500 tokens for {username}...")
    track_tokens(username, 1500)
    
    # 3. Check Database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT tokens_total, tokens_mes_actual, tokens_dia_actual 
        FROM users WHERE username = ?
    """, (username,))
    row = c.fetchone()
    conn.close()
    
    print(f"DB State: Total={row[0]}, Month={row[1]}, Day={row[2]}")
    
    if row[0] == 1500 and row[1] == 1500 and row[2] == 1500:
        print("✅ Token tracking confirmed in DB.")
    else:
        print("❌ Token tracking FAILED.")
        
    # 4. Verify Strategy Limit Logic (Admin Panel View)
    from auth_subscription import get_plan_limits
    user_plan = "prueba"
    limits = get_plan_limits(user_plan)
    strat_limit = limits.get('estrategias_dia', 1)
    
    print(f"\nAdmin Panel Plan Logic Check:")
    print(f"Plan: {user_plan}")
    print(f"Expected Strat Limit: {strat_limit}")
    
    if strat_limit == 3:
        print("✅ Plan limits correctly retrieved.")
    else:
        print(f"❌ Incorrect limit retrieved: {strat_limit}")
        
    # Cleanup
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    print("\n✅ Verification cleanup done.")

if __name__ == "__main__":
    verify_tracking()
