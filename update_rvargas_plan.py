import sqlite3
import sys
sys.path.append('.')
import auth

# Update rvargas91 to anual plan
print("Actualizando plan de rvargas91 a 'anual'...")
result = auth.set_user_plan('rvargas91', 'anual')

if result:
    print("✅ Plan actualizado exitosamente")
    
    # Verify
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT plan_actual, daily_request_limit, ai_request_limit, fecha_vencimiento 
        FROM users 
        WHERE username = 'rvargas91'
    """)
    
    updated = c.fetchone()
    print(f"\nPlan: {updated[0]}")
    print(f"Límite estrategias/día: {updated[1]}")
    print(f"Límite consultas IA/día: {updated[2]}")
    print(f"Vencimiento: {updated[3]}")
    conn.close()
else:
    print("❌ Error al actualizar plan")
