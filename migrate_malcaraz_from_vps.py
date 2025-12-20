"""
Script para migrar usuario 'malcaraz' del VPS a la base de datos local
antes de subir todo a PostgreSQL.
"""
import sqlite3
import psycopg2
import os

# Configuración
LOCAL_DB = "users.db"
VPS_DATABASE_URL = os.getenv("DATABASE_URL")  # La del VPS actual

def migrate_malcaraz_to_local():
    """Migra el usuario malcaraz desde PostgreSQL del VPS a SQLite local."""
    
    if not VPS_DATABASE_URL:
        print("❌ DATABASE_URL no está configurada")
        return
    
    print("🔄 Conectando a PostgreSQL del VPS...")
    pg_conn = psycopg2.connect(VPS_DATABASE_URL)
    pg_cursor = pg_conn.cursor()
    
    print("🔄 Conectando a SQLite local...")
    sqlite_conn = sqlite3.connect(LOCAL_DB)
    sqlite_cursor = sqlite_conn.cursor()
    
    # 1. Migrar usuario malcaraz
    print("📦 Buscando usuario 'malcaraz' en VPS...")
    pg_cursor.execute("SELECT * FROM users WHERE username = %s", ('malcaraz',))
    user_data = pg_cursor.fetchone()
    
    if not user_data:
        print("⚠️ Usuario 'malcaraz' no encontrado en VPS")
        pg_conn.close()
        sqlite_conn.close()
        return
    
    # Obtener nombres de columnas
    pg_cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position")
    columns = [row[0] for row in pg_cursor.fetchall()]
    
    print(f"✅ Usuario encontrado: {user_data[0]}")
    
    # Verificar si ya existe en local
    sqlite_cursor.execute("SELECT username FROM users WHERE username = ?", ('malcaraz',))
    if sqlite_cursor.fetchone():
        print("⚠️ Usuario 'malcaraz' ya existe en local, actualizando...")
        # Actualizar
        placeholders = ", ".join([f"{col} = ?" for col in columns if col != 'username'])
        values = [val for i, val in enumerate(user_data) if columns[i] != 'username']
        values.append('malcaraz')
        sqlite_cursor.execute(f"UPDATE users SET {placeholders} WHERE username = ?", values)
    else:
        print("➕ Insertando usuario 'malcaraz' en local...")
        # Insertar
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])
        sqlite_cursor.execute(f"INSERT INTO users ({cols_str}) VALUES ({placeholders})", user_data)
    
    # 2. Migrar estrategias del usuario
    print("📦 Migrando estrategias de 'malcaraz'...")
    pg_cursor.execute("SELECT * FROM estrategias_v2 WHERE username = %s", ('malcaraz',))
    estrategias = pg_cursor.fetchall()
    
    if estrategias:
        pg_cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='estrategias_v2' ORDER BY ordinal_position")
        est_columns = [row[0] for row in pg_cursor.fetchall()]
        
        for est in estrategias:
            est_id = est[0]
            # Verificar si existe
            sqlite_cursor.execute("SELECT id FROM estrategias_v2 WHERE id = ?", (est_id,))
            if sqlite_cursor.fetchone():
                print(f"  ⚠️ Estrategia {est_id} ya existe, omitiendo...")
                continue
            
            cols_str = ", ".join(est_columns)
            placeholders = ", ".join(["?" for _ in est_columns])
            sqlite_cursor.execute(f"INSERT INTO estrategias_v2 ({cols_str}) VALUES ({placeholders})", est)
            print(f"  ✅ Estrategia {est_id} migrada")
    
    # 3. Migrar tareas
    print("📦 Migrando tareas de 'malcaraz'...")
    pg_cursor.execute("SELECT * FROM tareas_diarias WHERE username = %s", ('malcaraz',))
    tareas = pg_cursor.fetchall()
    
    if tareas:
        pg_cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='tareas_diarias' ORDER BY ordinal_position")
        task_columns = [row[0] for row in pg_cursor.fetchall()]
        
        for tarea in tareas:
            tarea_id = tarea[0]
            sqlite_cursor.execute("SELECT id FROM tareas_diarias WHERE id = ?", (tarea_id,))
            if sqlite_cursor.fetchone():
                continue
            
            cols_str = ", ".join(task_columns)
            placeholders = ", ".join(["?" for _ in task_columns])
            sqlite_cursor.execute(f"INSERT INTO tareas_diarias ({cols_str}) VALUES ({placeholders})", tarea)
        
        print(f"  ✅ {len(tareas)} tareas migradas")
    
    sqlite_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    
    print("\n🎉 Migración de 'malcaraz' completada!")
    print("Ahora puedes subir users.db actualizado a GitHub")

if __name__ == "__main__":
    migrate_malcaraz_to_local()
