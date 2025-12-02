"""
Database migration script to add tasks and tracking tables.
Run this once to add the new tables to users.db
"""

import sqlite3
from datetime import datetime

DB_NAME = "users.db"

def migrate_tasks_system():
    """Add tables for actionable tasks and weekly tracking system."""
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("🔄 Starting tasks system migration...")
    
    # 1. Create tareas_diarias table
    print("Creating tareas_diarias table...")
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
    
    # 2. Create progreso_semanal table
    print("Creating progreso_semanal table...")
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
    
    # 3. Create logros_usuario table
    print("Creating logros_usuario table...")
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
    
    # 4. Add new columns to users table for gamification
    print("Adding gamification columns to users table...")
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN puntos_totales INTEGER DEFAULT 0")
        print("  ✓ Added puntos_totales")
    except sqlite3.OperationalError:
        print("  - puntos_totales already exists")
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN nivel INTEGER DEFAULT 1")
        print("  ✓ Added nivel")
    except sqlite3.OperationalError:
        print("  - nivel already exists")
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN racha_actual INTEGER DEFAULT 0")
        print("  ✓ Added racha_actual")
    except sqlite3.OperationalError:
        print("  - racha_actual already exists")
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN racha_maxima INTEGER DEFAULT 0")
        print("  ✓ Added racha_maxima")
    except sqlite3.OperationalError:
        print("  - racha_maxima already exists")
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN ultimo_dia_activo TEXT")
        print("  ✓ Added ultimo_dia_activo")
    except sqlite3.OperationalError:
        print("  - ultimo_dia_activo already exists")
    
    conn.commit()
    conn.close()
    
    print("✅ Migration completed successfully!")
    print("\nNew tables created:")
    print("  - tareas_diarias")
    print("  - progreso_semanal")
    print("  - logros_usuario")
    print("\nNew columns in users:")
    print("  - puntos_totales")
    print("  - nivel")
    print("  - racha_actual")
    print("  - racha_maxima")
    print("  - ultimo_dia_activo")

if __name__ == "__main__":
    migrate_tasks_system()
