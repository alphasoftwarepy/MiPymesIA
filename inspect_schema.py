import sqlite3
import os

DB_PATH = "users.db"
# check fallback
if not os.path.exists(DB_PATH) and os.path.exists("/app/data/users.db"):
    DB_PATH = "/app/data/users.db"

def inspect_schema():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    tables = ["users", "estrategias_v2", "historial_secciones", "conversaciones_archivadas", "tareas_diarias", "logros_usuario"]
    
    for table in tables:
        print(f"--- TABLE: {table} ---")
        try:
            c.execute(f"PRAGMA table_info({table})")
            columns = c.fetchall()
            for col in columns:
                # cid, name, type, notnull, dflt_value, pk
                print(f"{col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_schema()
