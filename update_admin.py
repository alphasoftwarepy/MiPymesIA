import sqlite3
import sys
sys.path.append('.')
from auth import get_password_hash

DB_NAME = "users.db"

def update_admin():
    """Update or create admin user with new credentials"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if rvargas91 exists
    c.execute("SELECT username, email FROM users WHERE username = ?", ("rvargas91",))
    user = c.fetchone()
    
    if user:
        print(f"Usuario encontrado: {user[0]}, Email: {user[1]}")
        # Update email if needed
        c.execute("UPDATE users SET email = ? WHERE username = ?", ("alphasoftpy@gmail.com", "rvargas91"))
        print("✅ Email actualizado a alphasoftpy@gmail.com")
    else:
        print("Usuario rvargas91 no existe. Creando...")
        # Create admin user
        hashed_password = get_password_hash("alphaSoftware!")
        c.execute("""INSERT INTO users 
                     (username, password, email, business_name, is_active, is_admin, start_date, expiration_date, 
                      requests_today, last_request_date, daily_request_limit, failed_login_attempts, lockout_until) 
                     VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, 0, NULL, ?, 0, NULL)""",
                  ("rvargas91", hashed_password, "alphasoftpy@gmail.com", "System Admin", True, True, 30))
        print("✅ Usuario admin creado")
    
    conn.commit()
    
    # Verify
    c.execute("SELECT username, email, is_admin, is_active, daily_request_limit FROM users WHERE username = ?", ("rvargas91",))
    admin = c.fetchone()
    print(f"\n📋 Verificación:")
    print(f"   Usuario: {admin[0]}")
    print(f"   Email: {admin[1]}")
    print(f"   Es Admin: {bool(admin[2])}")
    print(f"   Activo: {bool(admin[3])}")
    print(f"   Límite diario: {admin[4]}")
    
    conn.close()
    print("\n✅ Actualización completada!")
    print("\n🔐 Credenciales:")
    print("   Usuario: rvargas91")
    print("   Contraseña: alphaSoftware!")

if __name__ == "__main__":
    update_admin()
