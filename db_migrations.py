"""
Database Migration Manager - Handles automatic migrations for PostgreSQL
"""
import os
from datetime import datetime
import db_config

MIGRATIONS_TABLE = "schema_migrations"

def get_db_cursor():
    """Get a database cursor from the pool."""
    conn = db_config.get_connection()
    return conn, conn.cursor()

def init_migrations_table():
    """Create migrations tracking table if it doesn't exist."""
    conn, c = get_db_cursor()
    try:
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
                migration_id TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def is_migration_applied(migration_id):
    """Check if a specific migration has already been applied."""
    conn, c = get_db_cursor()
    try:
        c.execute(f"SELECT 1 FROM {MIGRATIONS_TABLE} WHERE migration_id = %s", (migration_id,))
        return c.fetchone() is not None
    finally:
        conn.close()

def mark_migration_applied(migration_id):
    """Mark a migration as applied in the tracking table."""
    conn, c = get_db_cursor()
    try:
        c.execute(f"INSERT INTO {MIGRATIONS_TABLE} (migration_id) VALUES (%s)", (migration_id,))
        conn.commit()
    finally:
        conn.close()

def add_column_if_not_exists(table_name, column_name, column_def):
    """
    Helper to add a column only if it doesn't already exist.
    """
    migration_id = f"add_{column_name}_to_{table_name}_v2"
    
    if is_migration_applied(migration_id):
        return

    print(f"  - Ensuring column exists: {table_name}.{column_name}")
    conn, c = get_db_cursor()
    try:
        # PostgreSQL syntax for checking column existence
        c.execute(f"""
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='{table_name}' AND column_name='{column_name}'
        """)
        
        if not c.fetchone():
            print(f"    - Adding column {column_name} to {table_name}...")
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            conn.commit()
            print(f"    ✅ Column {column_name} added successfully.")
        
        mark_migration_applied(migration_id)
    except Exception as e:
        print(f"    ❌ Error adding column {column_name}: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# ==================== MIGRATIONS LIST ====================

def migrate_users_table():
    print("  - Checking 'users' table columns...")
    # These were previously SQLite specific migrations, now normalized for Postgres if needed
    add_column_if_not_exists("users", "last_form_data", "TEXT DEFAULT ''")
    add_column_if_not_exists("users", "business_profile", "TEXT DEFAULT ''")
    
    # Check if level/puntos columns exist (added in newer versions)
    add_column_if_not_exists("users", "puntos_totales", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "nivel", "INTEGER DEFAULT 1")
    add_column_if_not_exists("users", "racha_actual", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "total_tokens_used", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "daily_strategies_count", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "last_strategy_date", "TEXT")

def migrate_estrategia_v2_table():
    print("  - Checking 'estrategias_v2' table columns...")
    add_column_if_not_exists("estrategias_v2", "duracion_dias", "INTEGER DEFAULT 30")
    add_column_if_not_exists("estrategias_v2", "semana_actual", "INTEGER DEFAULT 1")
    add_column_if_not_exists("estrategias_v2", "roadmap", "JSONB") # Use JSONB for Postgres
    add_column_if_not_exists("estrategias_v2", "feedback_historico", "JSONB")

def migrate_tareas_diarias_table():
    print("  - Checking 'tareas_diarias' table columns...")
    add_column_if_not_exists("tareas_diarias", "estrategia_id", "INTEGER")
    add_column_if_not_exists("tareas_diarias", "seccion_origen", "TEXT")

# ==================== MAIN MIGRATION RUNNER ====================

def run_migrations():
    """Run all pending migrations."""
    print("\n🔄 Checking for database migrations (PostgreSQL Only)...")
    
    init_migrations_table()
    
    try:
        migrate_users_table()
        migrate_estrategia_v2_table()
        migrate_tareas_diarias_table()
        print("✅ Database migrations check complete.\n")
    except Exception as e:
        print(f"⚠️ Error during migrations: {e}")
        raise

if __name__ == "__main__":
    run_migrations()
