"""
Export User Data from VPS Database
This script helps merge VPS user data with local database
"""

import sqlite3
import json
from datetime import datetime
import os

DB_NAME = "users.db"

def export_users_data(output_file="users_export.json"):
    """Export all user data to JSON for migration."""
    
    if not os.path.exists(DB_NAME):
        print(f"❌ Database file '{DB_NAME}' not found!")
        return
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "database": DB_NAME
    }
    
    # Export users
    try:
        c.execute("SELECT * FROM users")
        users = [dict(row) for row in c.fetchall()]
        data["users"] = users
        print(f"✅ Exported {len(users)} users")
    except Exception as e:
        print(f"⚠️  Error exporting users: {e}")
        data["users"] = []
    
    # Export estrategias
    try:
        c.execute("SELECT * FROM estrategias")
        estrategias = [dict(row) for row in c.fetchall()]
        data["estrategias"] = estrategias
        print(f"✅ Exported {len(estrategias)} estrategias")
    except Exception as e:
        print(f"⚠️  Error exporting estrategias: {e}")
        data["estrategias"] = []
    
    # Export tareas_diarias
    try:
        c.execute("SELECT * FROM tareas_diarias")
        tareas = [dict(row) for row in c.fetchall()]
        data["tareas_diarias"] = tareas
        print(f"✅ Exported {len(tareas)} tareas")
    except Exception as e:
        print(f"⚠️  Error exporting tareas: {e}")
        data["tareas_diarias"] = []
    
    # Export progreso_semanal
    try:
        c.execute("SELECT * FROM progreso_semanal")
        progreso = [dict(row) for row in c.fetchall()]
        data["progreso_semanal"] = progreso
        print(f"✅ Exported {len(progreso)} progreso records")
    except Exception as e:
        print(f"⚠️  Error exporting progreso: {e}")
        data["progreso_semanal"] = []
    
    # Export logros_usuario
    try:
        c.execute("SELECT * FROM logros_usuario")
        logros = [dict(row) for row in c.fetchall()]
        data["logros_usuario"] = logros
        print(f"✅ Exported {len(logros)} logros")
    except Exception as e:
        print(f"⚠️  Error exporting logros: {e}")
        data["logros_usuario"] = []
    
    # Export historial_secciones
    try:
        c.execute("SELECT * FROM historial_secciones")
        historial = [dict(row) for row in c.fetchall()]
        data["historial_secciones"] = historial
        print(f"✅ Exported {len(historial)} historial records")
    except Exception as e:
        print(f"⚠️  Error exporting historial: {e}")
        data["historial_secciones"] = []
    
    # Export conversaciones_archivadas
    try:
        c.execute("SELECT * FROM conversaciones_archivadas")
        conversaciones = [dict(row) for row in c.fetchall()]
        data["conversaciones_archivadas"] = conversaciones
        print(f"✅ Exported {len(conversaciones)} conversaciones")
    except Exception as e:
        print(f"⚠️  Error exporting conversaciones: {e}")
        data["conversaciones_archivadas"] = []
    
    conn.close()
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ All data exported to {output_file}")
    print(f"📦 File size: {os.path.getsize(output_file) / 1024:.2f} KB")


def import_users_data(input_file="users_export.json"):
    """Import user data from JSON file (use with caution!)."""
    
    if not os.path.exists(input_file):
        print(f"❌ Import file '{input_file}' not found!")
        return
    
    # Load data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📥 Importing data from {input_file}")
    print(f"   Exported at: {data.get('exported_at', 'Unknown')}")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Import users (update or insert)
    users = data.get("users", [])
    for user in users:
        try:
            # Check if user exists
            c.execute("SELECT username FROM users WHERE username = ?", (user['username'],))
            exists = c.fetchone()
            
            if exists:
                print(f"⚠️  User {user['username']} already exists, skipping...")
            else:
                # Insert new user
                columns = ', '.join(user.keys())
                placeholders = ', '.join(['?' for _ in user])
                sql = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
                c.execute(sql, list(user.values()))
                print(f"✅ Imported user: {user['username']}")
        except Exception as e:
            print(f"❌ Error importing user {user.get('username', 'unknown')}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Import complete!")


def compare_databases(local_db="users.db", vps_export="users_export_vps.json"):
    """Compare local database with VPS export to identify differences."""
    
    print("🔍 Comparing databases...\n")
    
    # Load VPS data
    if not os.path.exists(vps_export):
        print(f"❌ VPS export file '{vps_export}' not found!")
        return
    
    with open(vps_export, 'r', encoding='utf-8') as f:
        vps_data = json.load(f)
    
    # Get local data
    conn = sqlite3.connect(local_db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT username FROM users")
    local_users = {row['username'] for row in c.fetchall()}
    
    vps_users = {user['username'] for user in vps_data.get('users', [])}
    
    # Find differences
    only_in_vps = vps_users - local_users
    only_in_local = local_users - vps_users
    in_both = vps_users & local_users
    
    print("📊 Comparison Results:")
    print("=" * 50)
    print(f"  Users in VPS only: {len(only_in_vps)}")
    if only_in_vps:
        for user in sorted(only_in_vps):
            print(f"    - {user}")
    
    print(f"\n  Users in Local only: {len(only_in_local)}")
    if only_in_local:
        for user in sorted(only_in_local):
            print(f"    - {user}")
    
    print(f"\n  Users in both: {len(in_both)}")
    
    print("=" * 50)
    
    conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "export":
            output = sys.argv[2] if len(sys.argv) > 2 else "users_export.json"
            export_users_data(output)
        
        elif command == "import":
            input_file = sys.argv[2] if len(sys.argv) > 2 else "users_export.json"
            
            # Confirm before importing
            print("⚠️  WARNING: This will import data into the current database!")
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() == 'yes':
                import_users_data(input_file)
            else:
                print("❌ Import cancelled")
        
        elif command == "compare":
            vps_file = sys.argv[2] if len(sys.argv) > 2 else "users_export_vps.json"
            compare_databases(vps_export=vps_file)
        
        else:
            print("Unknown command. Use: export, import, or compare")
    
    else:
        # Default: export
        export_users_data()
