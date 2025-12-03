"""
Database Migration Manager - Handles automatic migrations on app startup
"""

import sqlite3
import os
from datetime import datetime

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
os.makedirs(DB_PATH, exist_ok=True)
DB_NAME = os.path.join(DB_PATH, "users.db")

MIGRATIONS_TABLE = "schema_migrations"

def init_migrations_table():
    """Create migrations tracking table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {MIGRATIONS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_name TEXT UNIQUE NOT NULL,
            executed_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def has_migration_run(migration_name):
    """Check if a migration has already been executed."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute(f"SELECT COUNT(*) FROM {MIGRATIONS_TABLE} WHERE migration_name = ?", (migration_name,))
    count = c.fetchone()[0]
    
    conn.close()
    return count > 0


def mark_migration_as_run(migration_name):
    """Mark a migration as executed."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    c.execute(f"INSERT INTO {MIGRATIONS_TABLE} (migration_name, executed_at) VALUES (?, ?)", 
              (migration_name, now))
    
    conn.commit()
    conn.close()


def run_migration(migration_name, migration_func):
    """Run a migration if it hasn't been executed yet."""
    if has_migration_run(migration_name):
        print(f"  ⏭️  Migration '{migration_name}' already executed, skipping...")
        return False
    
    print(f"  🔄 Running migration: {migration_name}")
    try:
        migration_func()
        mark_migration_as_run(migration_name)
        print(f"  ✅ Migration '{migration_name}' completed successfully")
        return True
    except Exception as e:
        print(f"  ❌ Migration '{migration_name}' failed: {e}")
        raise


# ==================== MIGRATION FUNCTIONS ====================

def migration_001_subscription_system():
    """Add subscription and usage limit columns to users table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    columns_to_add = [
        ("plan_actual", "TEXT DEFAULT 'prueba'"),
        ("fecha_registro", "TEXT"),
        ("fecha_ultimo_pago", "TEXT"),
        ("fecha_vencimiento", "TEXT"),
        ("ai_requests_today", "INTEGER DEFAULT 0"),
        ("ai_request_limit", "INTEGER DEFAULT 10"),
        ("tokens_total", "INTEGER DEFAULT 0"),
        ("tokens_mes_actual", "INTEGER DEFAULT 0"),
        ("tokens_dia_actual", "INTEGER DEFAULT 0"),
        ("tokens_last_reset", "TEXT")
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
            print(f"    ✓ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"    - Column {column_name} already exists")
            else:
                raise
    
    conn.commit()
    conn.close()


def migration_002_tasks_system():
    """Add tasks, progress, and achievements tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create tareas_diarias table
    c.execute("""
        CREATE TABLE IF NOT EXISTS tareas_diarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            categoria TEXT,
            prioridad TEXT DEFAULT 'media',
            frecuencia TEXT DEFAULT 'unica',
            dia_semana INTEGER,
            completada INTEGER DEFAULT 0,
            fecha_completada TEXT,
            fecha_creacion TEXT NOT NULL,
            seccion_origen TEXT,
            puntos INTEGER DEFAULT 5,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    print("    ✓ Created table: tareas_diarias")
    
    # Create progreso_semanal table
    c.execute("""
        CREATE TABLE IF NOT EXISTS progreso_semanal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            semana_inicio TEXT NOT NULL,
            tareas_completadas INTEGER DEFAULT 0,
            tareas_totales INTEGER DEFAULT 0,
            racha_dias INTEGER DEFAULT 0,
            puntos_ganados INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(username),
            UNIQUE(user_id, semana_inicio)
        )
    """)
    print("    ✓ Created table: progreso_semanal")
    
    # Create logros_usuario table
    c.execute("""
        CREATE TABLE IF NOT EXISTS logros_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            logro_id TEXT NOT NULL,
            logro_nombre TEXT NOT NULL,
            fecha_obtenido TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username),
            UNIQUE(user_id, logro_id)
        )
    """)
    print("    ✓ Created table: logros_usuario")
    
    # Add gamification columns to users
    gamification_columns = [
        ("puntos_totales", "INTEGER DEFAULT 0"),
        ("nivel", "INTEGER DEFAULT 1"),
        ("racha_actual", "INTEGER DEFAULT 0"),
        ("racha_maxima", "INTEGER DEFAULT 0"),
        ("ultimo_dia_activo", "TEXT")
    ]
    
    for column_name, column_def in gamification_columns:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
            print(f"    ✓ Added column to users: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"    - Column {column_name} already exists")
            else:
                raise
    
    conn.commit()
    conn.close()


# ==================== MAIN MIGRATION RUNNER ====================

def run_all_migrations():
    """Run all pending migrations in order."""
    print("\n🔄 Checking for pending database migrations...")
    
    # Initialize migrations tracking
    init_migrations_table()
    
    # Define all migrations in order
    migrations = [
        ("001_subscription_system", migration_001_subscription_system),
        ("002_tasks_system", migration_002_tasks_system),
    ]
    
    # Run each migration
    executed_count = 0
    for migration_name, migration_func in migrations:
        if run_migration(migration_name, migration_func):
            executed_count += 1
    
    if executed_count > 0:
        print(f"\n✅ {executed_count} migration(s) executed successfully\n")
    else:
        print("\n✅ Database is up to date (no migrations needed)\n")


if __name__ == "__main__":
    run_all_migrations()
