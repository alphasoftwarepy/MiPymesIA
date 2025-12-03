"""
Complete Database Initialization Script
Creates all tables with all required columns for MiPymesIA
Run this ONCE when deploying to a new environment
"""

import sqlite3
from datetime import datetime, timedelta

DB_NAME = "users.db"

def init_complete_database():
    """Initialize database with ALL required tables and columns."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("🔄 Initializing complete database schema...")
    
    # ==================== USERS TABLE ====================
    print("  📋 Creating users table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT,
            full_name TEXT,
            business_name TEXT,
            business_type TEXT,
            target_audience TEXT,
            business_description TEXT,
            business_profile TEXT,
            plan_actual TEXT DEFAULT 'prueba',
            fecha_registro TEXT,
            fecha_ultimo_pago TEXT,
            fecha_vencimiento TEXT,
            ai_requests_today INTEGER DEFAULT 0,
            ai_request_limit INTEGER DEFAULT 10,
            tokens_total INTEGER DEFAULT 0,
            tokens_mes_actual INTEGER DEFAULT 0,
            tokens_dia_actual INTEGER DEFAULT 0,
            tokens_last_reset TEXT,
            puntos_totales INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            racha_actual INTEGER DEFAULT 0,
            racha_maxima INTEGER DEFAULT 0,
            ultimo_dia_activo TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    
    # ==================== ESTRATEGIAS TABLE ====================
    print("  📋 Creating estrategias table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS estrategias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            contenido TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    
    # ==================== HISTORIAL_SECCIONES TABLE ====================
    print("  📋 Creating historial_secciones table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS historial_secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            seccion TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    
    # ==================== CONVERSACIONES_ARCHIVADAS TABLE ====================
    print("  📋 Creating conversaciones_archivadas table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversaciones_archivadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tarea_id INTEGER NOT NULL,
            mensaje TEXT NOT NULL,
            rol TEXT NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
    """)
    
    # ==================== TAREAS_DIARIAS TABLE ====================
    print("  📋 Creating tareas_diarias table...")
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
    
    # ==================== PROGRESO_SEMANAL TABLE ====================
    print("  📋 Creating progreso_semanal table...")
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
    
    # ==================== LOGROS_USUARIO TABLE ====================
    print("  📋 Creating logros_usuario table...")
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
    
    # ==================== SCHEMA_MIGRATIONS TABLE ====================
    print("  📋 Creating schema_migrations table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_name TEXT UNIQUE NOT NULL,
            executed_at TEXT NOT NULL
        )
    """)
    
    # Mark migrations as executed
    now = datetime.utcnow().isoformat()
    try:
        c.execute("INSERT INTO schema_migrations (migration_name, executed_at) VALUES (?, ?)", 
                  ("001_subscription_system", now))
        print("  ✓ Marked migration: 001_subscription_system")
    except sqlite3.IntegrityError:
        print("  - Migration 001_subscription_system already marked")
    
    try:
        c.execute("INSERT INTO schema_migrations (migration_name, executed_at) VALUES (?, ?)", 
                  ("002_tasks_system", now))
        print("  ✓ Marked migration: 002_tasks_system")
    except sqlite3.IntegrityError:
        print("  - Migration 002_tasks_system already marked")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database initialized successfully!")
    print("\n📊 Verifying tables...")
    
    # Verify tables
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = c.fetchall()
    
    print("\nTables created:")
    for table in tables:
        c.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = c.fetchone()[0]
        print(f"  ✓ {table[0]}: {count} records")
    
    # Get database size
    import os
    if os.path.exists(DB_NAME):
        db_size = os.path.getsize(DB_NAME) / 1024  # KB
        print(f"\n💾 Database size: {db_size:.2f} KB")
    
    conn.close()
    
    print("\n" + "="*50)
    print("✅ INITIALIZATION COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("  1. Restart your application")
    print("  2. Create your first user account")
    print("  3. Verify everything works correctly")
    print("\n")

if __name__ == "__main__":
    print("="*50)
    print("  MiPymesIA - Complete Database Initialization")
    print("="*50)
    print("\n⚠️  WARNING: This will create/update the database schema")
    print("   Existing data will NOT be lost\n")
    
    response = input("Continue? (yes/no): ")
    
    if response.lower() == 'yes':
        init_complete_database()
    else:
        print("\n❌ Initialization cancelled")
