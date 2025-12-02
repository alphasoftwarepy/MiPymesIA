import sqlite3

# Connect to database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Check rvargas91 user
c.execute("""
    SELECT username, plan_actual, daily_request_limit, ai_request_limit, fecha_vencimiento, is_admin 
    FROM users 
    WHERE username = 'rvargas91'
""")

user = c.fetchone()

if user:
    print(f"Usuario: {user[0]}")
    print(f"Plan actual: {user[1]}")
    print(f"Límite estrategias/día: {user[2]}")
    print(f"Límite consultas IA/día: {user[3]}")
    print(f"Fecha vencimiento: {user[4]}")
    print(f"Es admin: {bool(user[5])}")
    print()
    
    # If plan is not 'anual', update it
    if user[1] != 'anual':
        print("⚠️ El plan no es 'anual', actualizando...")
        
        # Import set_user_plan from auth_subscription
        import sys
        sys.path.append('.')
        from auth_subscription import set_user_plan
        
        # Set to anual plan
        set_user_plan(user[0], 'anual')
        print("✅ Plan actualizado a 'anual'")
        
        # Verify
        c.execute("""
            SELECT plan_actual, daily_request_limit, ai_request_limit 
            FROM users 
            WHERE username = ?
        """, (user[0],))
        
        updated = c.fetchone()
        print(f"\nNuevo plan: {updated[0]}")
        print(f"Nuevo límite estrategias: {updated[1]}")
        print(f"Nuevo límite IA: {updated[2]}")
    else:
        print("✅ El plan ya es 'anual'")
else:
    print("❌ Usuario 'rvargas91' no encontrado")

conn.close()
