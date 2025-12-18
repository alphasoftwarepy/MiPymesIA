import os
import sqlite3
import psycopg2
import db_config
import auth
from psycopg2.extras import execute_values

# Source SQLite
SQLITE_DB = "users.db" # Or get from db_config.get_sqlite_path() if locally different

# Target Postgres
DATABASE_URL = os.getenv("DATABASE_URL")

def reset_sequences(pg_cursor):
    """Resets sequences for tables with SERIAL columns."""
    tables = [
        "estrategias_v2", 
        "historial_secciones", 
        "conversaciones_archivadas", 
        "tareas_diarias", 
        "logros_usuario"
    ]
    
    print("🔄 Resetting sequences...")
    for table in tables:
        try:
            # Postgres specific: generic way to auto-reset sequence to max id
            query = f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 0) + 1, false) FROM {table};"
            pg_cursor.execute(query)
            print(f"  ✅ Sequence reset for {table}")
        except Exception as e:
            print(f"  ⚠️ Could not reset sequence for {table}: {e}")

def migrate():
    if not DATABASE_URL:
        print("❌ DATABASE_URL is not set. Cannot migrate to Postgres.")
        return

    sqlite_db_path = SQLITE_DB
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database {sqlite_db_path} not found.")
        # Try production path just in case
        if os.path.exists("/app/data/users.db"):
             sqlite_db_path = "/app/data/users.db"
             print(f"📍 Found database at fallback path: {sqlite_db_path}")
        else:
             return

    print(f"🚀 Starting migration from {sqlite_db_path} to Postgres...")
    
    # 0. Clean Postgres (Optional but recommended for full migration)
    print("🧹 Cleaning target database...")
    clean_conn = psycopg2.connect(DATABASE_URL)
    clean_cursor = clean_conn.cursor()
    tables_to_drop = ["tareas_diarias", "conversaciones_archivadas", "historial_secciones", "estrategias_v2", "logros_usuario", "users"]
    for t in tables_to_drop:
        clean_cursor.execute(f"DROP TABLE IF EXISTS {t} CASCADE;")
    clean_conn.commit()
    clean_conn.close()

    # 1. Initialize Postgres Schema
    print("🛠️ Initializing Postgres Schema...")
    try:
        auth.init_db()
        print("✅ Schema initialized successfully.")
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        return
    
    # 2. Connect to both
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row
    sq_cursor = sqlite_conn.cursor()

    pg_conn = psycopg2.connect(DATABASE_URL)
    pg_cursor = pg_conn.cursor()

    # 3. Migrate data table by table
    # Order matters due to Foreign Keys: users -> estrategias -> tables referencing them
    tables = [
        "users",
        "estrategias_v2",
        "historial_secciones",
        "conversaciones_archivadas",
        "tareas_diarias",
        "logros_usuario"
    ]

    for table in tables:
        print(f"📦 Migrating table: {table}")
        
        # Get data from SQLite
        try:
            sq_cursor.execute(f"SELECT * FROM {table}")
            rows = sq_cursor.fetchall()
            
            if not rows:
                print(f"  ℹ️  Table {table} is empty. Skipping.")
                continue

            # Get column names
            col_names = [description[0] for description in sq_cursor.description]
            columns_str = ", ".join(col_names)
            placeholders = ", ".join(["%s"] * len(col_names))
            
            # Prepare data
            
            # Map of table -> set of boolean columns
            bool_columns = {
                "users": {"is_active", "is_admin"},
                "estrategias_v2": {"activa"},
                "conversaciones_archivadas": {"expandible"},
                "tareas_diarias": {"completada"}
            }
            
            table_bools = bool_columns.get(table, set())
            
            # Find indices of boolean columns
            bool_indices = [i for i, name in enumerate(col_names) if name in table_bools]
            
            final_data = []
            for row in rows:
                row_list = list(row)
                for idx in bool_indices:
                    # Convert 0/1 to bool
                    if row_list[idx] is not None:
                        row_list[idx] = bool(row_list[idx])
                final_data.append(tuple(row_list))
            
            # Clean target table first? (Optional, but safe for initial migration)
            # pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE;") # Careful with FKs
            # Better to use INSERT ON CONFLICT DO NOTHING or just try insert
            
            query = f"INSERT INTO {table} ({columns_str}) VALUES %s ON CONFLICT DO NOTHING"
            
            execute_values(pg_cursor, query, final_data)
            pg_conn.commit()  # Commit after each table
            print(f"  ✅ Migrated {len(final_data)} rows.")

        except Exception as e:
            print(f"  ❌ Error migrating {table}: {e}")
            pg_conn.rollback()
            # Depending on strictness, we might return or continue
            continue
    
    # 4. Reset sequences
    reset_sequences(pg_cursor)

    pg_conn.commit()
    sqlite_conn.close()
    pg_conn.close()
    print("🎉 Migration completed successfully!")

if __name__ == "__main__":
    migrate()
