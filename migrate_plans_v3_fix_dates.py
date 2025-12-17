import sqlite3
import os
from datetime import datetime, timedelta

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def fix_plan_expirations():
    """
    1. Migrates any remaining legacy plans to new names.
    2. Updates expiration date to 30 days from now for ALL paid plans (starter, growth, pro).
    """
    print(f"Checking database at: {DB_NAME}")
    
    if not os.path.exists(DB_NAME):
        print("❌ Database not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. Complete any pending renaming
    plan_mapping = {
        'mensual': 'starter',
        'trimestral': 'growth',
        'semestral': 'growth',
        'anual': 'pro'
    }

    for old_plan, new_plan in plan_mapping.items():
        c.execute("UPDATE users SET plan_actual = ? WHERE plan_actual = ?", (new_plan, old_plan))
        if c.rowcount > 0:
            print(f"✅ Renamed {c.rowcount} remaining users from {old_plan} to {new_plan}")

    # 2. Update expiration dates for ALL paid plans to 30 days from now
    paid_plans = ['starter', 'growth', 'pro']
    
    # Calculate new expiration date (Now + 30 days)
    new_expiration = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"Setting expiration date to: {new_expiration} (30 days from now) for paid plans")

    placeholders = ', '.join(['?'] * len(paid_plans))
    query = f"UPDATE users SET fecha_vencimiento = ? WHERE plan_actual IN ({placeholders})"
    
    c.execute(query, [new_expiration] + paid_plans)
    updated_count = c.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"🎉 Updated expiration dates for {updated_count} users in plans: {', '.join(paid_plans)}")

if __name__ == "__main__":
    fix_plan_expirations()
