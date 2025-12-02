"""
Database Migration Manager - Handles automatic migrations on app startup
"""

import sqlite3
import os
from datetime import datetime

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")

# Ensure the directory exists
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



def migration_003_missing_auth_columns():
    """Add missing auth columns (email, limits, lockout) if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    columns_to_add = [
        ("email", "TEXT DEFAULT ''"),
        ("daily_request_limit", "INTEGER DEFAULT 20"),
        ("failed_login_attempts", "INTEGER DEFAULT 0"),
        ("lockout_until", "TEXT")
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




def migration_004_estrategias_table():
    """Create estrategias table for storing user strategies."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estrategias'")
    if c.fetchone():
        print("    - Table 'estrategias' already exists")
        conn.close()
        return
    
    print("    ✓ Creating 'estrategias' table...")
    c.execute('''
        CREATE TABLE estrategias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            avatar TEXT,
            embudo TEXT,
            ads TEXT,
            objeciones TEXT,
            whatsapp TEXT,
            acciones_diarias TEXT,
            kpis TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')
    
    # Create index for faster lookups
    c.execute('CREATE INDEX idx_estrategias_user_id ON estrategias(user_id)')
    
    conn.commit()
    conn.close()


def migration_005_historial_secciones_table():
    """Create historial_secciones table for storing section interaction history."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historial_secciones'")
    if c.fetchone():
        print("    - Table 'historial_secciones' already exists")
        conn.close()
        return
    
    print("    ✓ Creating 'historial_secciones' table...")
    c.execute('''
        CREATE TABLE historial_secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            seccion TEXT NOT NULL,
            tipo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for faster lookups
    c.execute('CREATE INDEX idx_historial_user_id ON historial_secciones(user_id)')
    c.execute('CREATE INDEX idx_historial_seccion ON historial_secciones(user_id, seccion)')
    c.execute('CREATE INDEX idx_historial_timestamp ON historial_secciones(timestamp)')
    
    conn.commit()
    conn.close()


def migration_006_conversaciones_archivadas_table():
    """Create conversaciones_archivadas table for storing compacted conversation summaries."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversaciones_archivadas'")
    if c.fetchone():
        print("    - Table 'conversaciones_archivadas' already exists")
        conn.close()
        return
    
    print("    ✓ Creating 'conversaciones_archivadas' table...")
    c.execute("""
        CREATE TABLE conversaciones_archivadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            seccion TEXT NOT NULL,
            resumen TEXT,
            mensajes_count INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            expandible BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    
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
        ("003_missing_auth_columns", migration_003_missing_auth_columns),
        ("004_estrategias_table", migration_004_estrategias_table),
        ("005_historial_secciones_table", migration_005_historial_secciones_table),
        ("006_conversaciones_archivadas_table", migration_006_conversaciones_archivadas_table),
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
