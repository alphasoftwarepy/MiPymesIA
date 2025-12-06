"""
Migration Script: Multi-Strategy Support
Creates estrategias_v2 table and migrates existing data
"""

import sqlite3
import json
from datetime import datetime
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
os.makedirs(DB_PATH, exist_ok=True)
DB_NAME = os.path.join(DB_PATH, "users.db")

def migrate_to_multi_strategy():
    """
    Migrates database to support multiple strategies per user.
    
    Changes:
    1. Creates new table estrategias_v2 with multi-strategy support
    2. Migrates existing estrategias data to estrategias_v2
    3. Adds estrategia_id column to tareas_diarias
    4. Links existing tasks to migrated strategies
    """
    
    print("=" * 60)
    print("  MIGRATION: Multi-Strategy Support")
    print("=" * 60)
    print()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # ==================== STEP 1: Create estrategias_v2 table ====================
        print("📋 Step 1: Creating estrategias_v2 table...")
        c.execute("""
            CREATE TABLE IF NOT EXISTS estrategias_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                nombre_estrategia TEXT NOT NULL,
                producto_servicio TEXT NOT NULL,
                activa INTEGER DEFAULT 1,
                avatar TEXT,
                embudo TEXT,
                ads TEXT,
                objeciones TEXT,
                whatsapp TEXT,
                acciones_diarias TEXT,
                kpis TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(username),
                UNIQUE(user_id, nombre_estrategia)
            )
        """)
        print("   ✓ Table estrategias_v2 created")
        
        # ==================== STEP 2: Migrate existing data ====================
        print("\n📦 Step 2: Migrating existing estrategias to estrategias_v2...")
        
        # Check if old table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estrategias'")
        if c.fetchone():
            # Get all existing strategies
            c.execute("SELECT * FROM estrategias")
            old_estrategias = c.fetchall()
            
            # Get column names
            c.execute("PRAGMA table_info(estrategias)")
            columns = [col[1] for col in c.fetchall()]
            
            migrated_count = 0
            for estrategia in old_estrategias:
                # Create dict from row
                estrategia_dict = dict(zip(columns, estrategia))
                
                user_id = estrategia_dict.get('user_id')
                
                # Check if already migrated
                c.execute("SELECT id FROM estrategias_v2 WHERE user_id = ? AND nombre_estrategia = ?", 
                         (user_id, "Estrategia Principal"))
                if c.fetchone():
                    print(f"   - User {user_id}: Already migrated, skipping")
                    continue
                
                # Insert into new table with default name
                now = datetime.utcnow().isoformat()
                c.execute("""
                    INSERT INTO estrategias_v2 
                    (user_id, nombre_estrategia, producto_servicio, activa,
                     avatar, embudo, ads, objeciones, whatsapp, acciones_diarias, kpis,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    "Estrategia Principal",
                    "Producto/Servicio Principal",
                    1,  # activa
                    estrategia_dict.get('avatar'),
                    estrategia_dict.get('embudo'),
                    estrategia_dict.get('ads'),
                    estrategia_dict.get('objeciones'),
                    estrategia_dict.get('whatsapp'),
                    estrategia_dict.get('acciones_diarias'),
                    estrategia_dict.get('kpis'),
                    estrategia_dict.get('created_at', now),
                    estrategia_dict.get('updated_at', now)
                ))
                migrated_count += 1
                print(f"   ✓ Migrated strategy for user: {user_id}")
            
            print(f"\n   ✓ Migrated {migrated_count} strategies")
        else:
            print("   - No old estrategias table found, skipping migration")
        
        # ==================== STEP 3: Add estrategia_id to tareas_diarias ====================
        print("\n🔗 Step 3: Adding estrategia_id column to tareas_diarias...")
        
        # Check if column already exists
        c.execute("PRAGMA table_info(tareas_diarias)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'estrategia_id' not in columns:
            c.execute("ALTER TABLE tareas_diarias ADD COLUMN estrategia_id INTEGER")
            print("   ✓ Column estrategia_id added")
        else:
            print("   - Column estrategia_id already exists")
        
        # ==================== STEP 4: Link existing tasks to strategies ====================
        print("\n🔗 Step 4: Linking existing tasks to migrated strategies...")
        
        # Get all users with tasks
        c.execute("SELECT DISTINCT user_id FROM tareas_diarias WHERE estrategia_id IS NULL")
        users_with_tasks = [row[0] for row in c.fetchall()]
        
        linked_count = 0
        for user_id in users_with_tasks:
            # Get user's first strategy (should be the migrated one)
            c.execute("SELECT id FROM estrategias_v2 WHERE user_id = ? ORDER BY created_at LIMIT 1", (user_id,))
            result = c.fetchone()
            
            if result:
                estrategia_id = result[0]
                # Link all user's tasks to this strategy
                c.execute("""
                    UPDATE tareas_diarias
                    SET estrategia_id = ?
                    WHERE user_id = ? AND estrategia_id IS NULL
                """, (estrategia_id, user_id))
                
                tasks_linked = c.rowcount
                linked_count += tasks_linked
                print(f"   ✓ Linked {tasks_linked} tasks for user: {user_id}")
        
        print(f"\n   ✓ Total tasks linked: {linked_count}")
        
        # ==================== STEP 5: Create index for performance ====================
        print("\n⚡ Step 5: Creating performance indexes...")
        
        try:
            c.execute("CREATE INDEX IF NOT EXISTS idx_estrategias_v2_user ON estrategias_v2(user_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_tareas_estrategia ON tareas_diarias(user_id, estrategia_id)")
            print("   ✓ Indexes created")
        except Exception as e:
            print(f"   - Indexes may already exist: {e}")
        
        # ==================== STEP 6: Mark migration as complete ====================
        print("\n✅ Step 6: Marking migration as complete...")
        
        now = datetime.utcnow().isoformat()
        try:
            c.execute("""
                INSERT INTO schema_migrations (migration_name, executed_at)
                VALUES (?, ?)
            """, ("003_multi_strategy_support", now))
            print("   ✓ Migration marked as complete")
        except sqlite3.IntegrityError:
            print("   - Migration already marked as complete")
        
        # Commit all changes
        conn.commit()
        
        # ==================== VERIFICATION ====================
        print("\n" + "=" * 60)
        print("  VERIFICATION")
        print("=" * 60)
        
        # Count strategies
        c.execute("SELECT COUNT(*) FROM estrategias_v2")
        total_strategies = c.fetchone()[0]
        print(f"✓ Total strategies in estrategias_v2: {total_strategies}")
        
        # Count tasks with estrategia_id
        c.execute("SELECT COUNT(*) FROM tareas_diarias WHERE estrategia_id IS NOT NULL")
        linked_tasks = c.fetchone()[0]
        print(f"✓ Tasks linked to strategies: {linked_tasks}")
        
        # Count tasks without estrategia_id
        c.execute("SELECT COUNT(*) FROM tareas_diarias WHERE estrategia_id IS NULL")
        unlinked_tasks = c.fetchone()[0]
        if unlinked_tasks > 0:
            print(f"⚠️  Tasks not linked: {unlinked_tasks}")
        else:
            print(f"✓ All tasks are linked to strategies")
        
        print("\n" + "=" * 60)
        print("  ✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will modify your database schema")
    print("   Make sure you have a backup before proceeding\n")
    
    response = input("Continue with migration? (yes/no): ")
    
    if response.lower() == 'yes':
        migrate_to_multi_strategy()
    else:
        print("\n❌ Migration cancelled")
