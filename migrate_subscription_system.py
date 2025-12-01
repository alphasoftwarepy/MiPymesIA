import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'users.db'

def migrate():
    """
    Adds new columns to users table for subscription management and usage tracking.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Get existing columns
        c.execute("PRAGMA table_info(users)")
        existing_columns = [column[1] for column in c.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Define new columns to add
        new_columns = [
            ("fecha_registro", "DATETIME"),
            ("fecha_ultimo_pago", "DATETIME"),
            ("fecha_vencimiento", "DATETIME"),
            ("plan_actual", "TEXT DEFAULT 'prueba'"),
            ("ai_requests_today", "INTEGER DEFAULT 0"),
            ("ai_request_limit", "INTEGER DEFAULT 10"),
            ("tokens_total", "INTEGER DEFAULT 0"),
            ("tokens_mes_actual", "INTEGER DEFAULT 0"),
            ("tokens_dia_actual", "INTEGER DEFAULT 0"),
            ("tokens_last_reset", "DATETIME"),
        ]
        
        # Add each column if it doesn't exist
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                print(f"Adding column: {column_name}")
                c.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name}")
            else:
                print(f"⏭️  Column {column_name} already exists, skipping")
        
        # Update existing users with default values
        now = datetime.utcnow().isoformat()
        seven_days_later = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        # Set fecha_registro for users without it
        c.execute("UPDATE users SET fecha_registro = ? WHERE fecha_registro IS NULL", (now,))
        
        # Set fecha_vencimiento for users without it (7 days from now for trial)
        c.execute("UPDATE users SET fecha_vencimiento = ? WHERE fecha_vencimiento IS NULL", (seven_days_later,))
        
        # Set plan_actual for users without it
        c.execute("UPDATE users SET plan_actual = 'prueba' WHERE plan_actual IS NULL OR plan_actual = ''")
        
        # Set tokens_last_reset for users without it
        c.execute("UPDATE users SET tokens_last_reset = ? WHERE tokens_last_reset IS NULL", (now,))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print(f"✅ Updated {c.rowcount} existing users with default values")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting migration: Add subscription and usage tracking columns...")
    migrate()
    print("✅ Migration script finished.")
