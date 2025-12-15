import sqlite3
import json

DB_PATH = 'users.db'

def check_latest_strategy():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT id, nombre_estrategia, roadmap, duracion_dias FROM estrategias_v2 ORDER BY id DESC LIMIT 1")
        row = c.fetchone()
        if row:
            print(f"ID: {row[0]}")
            print(f"Nombre: {row[1]}")
            print(f"Duracion: {row[3]}")
            print(f"Roadmap (Raw): {row[2]}")
            try:
                parsed = json.loads(row[2])
                print(f"Roadmap (Parsed): with {len(parsed)} items")
            except:
                print("Roadmap is NOT valid JSON")
        else:
            print("No strategies found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_latest_strategy()
