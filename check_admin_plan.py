import sqlite3

# Connect to database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Check admin user
c.execute("""
    SELECT username, plan_actual, daily_request_limit, ai_request_limit, fecha_vencimiento 
    FROM users 
    WHERE is_admin = 1
""")

admin = c.fetchone()

if admin:
    print(f"Usuario admin: {admin[0]}")
    print(f"Plan actual: {admin[1]}")
    print(f"Límite estrategias/día: {admin[2]}")
    print(f"Límite consultas IA/día: {admin[3]}")
    print(f"Fecha vencimiento: {admin[4]}")
    print()
    
    # If plan is not 'anual', update it
    if admin[1] != 'anual':
        print("⚠️ El plan no es 'anual', actualizando...")
        
        # Import set_user_plan from auth_subscription
        import sys
        sys.path.append('.')
        from auth_subscription import set_user_plan
        
        # Set to anual plan
        set_user_plan(admin[0], 'anual')
        print("✅ Plan actualizado a 'anual'")
        
        # Verify
        c.execute("""
            SELECT plan_actual, daily_request_limit, ai_request_limit 
            FROM users 
            WHERE username = ?
        """, (admin[0],))
        
        updated = c.fetchone()
        print(f"\nNuevo plan: {updated[0]}")
        print(f"Nuevo límite estrategias: {updated[1]}")
        print(f"Nuevo límite IA: {updated[2]}")
    else:
        print("✅ El plan ya es 'anual'")

conn.close()
