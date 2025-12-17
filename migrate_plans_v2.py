import sqlite3
import os
from datetime import datetime

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def migrate_user_plans():
    """
    Migrates users with legacy plan names to new names:
    mensual -> starter
    trimestral -> growth
    semestral -> growth (mapping to middle tier)
    anual -> pro
    """
    print(f"Checking database at: {DB_NAME}")
    
    if not os.path.exists(DB_NAME):
        print("❌ Database not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Define mappings
    plan_mapping = {
        'mensual': 'starter',
        'trimestral': 'growth',
        'semestral': 'growth',
        'anual': 'pro'
    }

    total_migrated = 0

    for old_plan, new_plan in plan_mapping.items():
        print(f"Migrating '{old_plan}' to '{new_plan}'...")
        
        # Check count first
        c.execute("SELECT COUNT(*) FROM users WHERE plan_actual = ?", (old_plan,))
        count = c.fetchone()[0]
        
        if count > 0:
            c.execute("UPDATE users SET plan_actual = ? WHERE plan_actual = ?", (new_plan, old_plan))
            print(f"✅ Updated {count} users from {old_plan} to {new_plan}")
            total_migrated += count
        else:
            print(f"No users found with plan {old_plan}")

    conn.commit()
    conn.close()
    
    print(f"\n🎉 Migration complete! Total users migrated: {total_migrated}")

if __name__ == "__main__":
    migrate_user_plans()
