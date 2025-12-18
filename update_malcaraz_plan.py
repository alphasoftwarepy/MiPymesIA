"""
Script para actualizar el plan de 'malcaraz' de 'anual' a 'pro'
Ejecutar en la consola de EasyPanel
"""
import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL no está configurada")
    exit(1)

print("🔄 Conectando a PostgreSQL...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Verificar usuario actual
cursor.execute("SELECT username, plan_actual FROM users WHERE username = %s", ('malcaraz',))
user = cursor.fetchone()

if not user:
    print("❌ Usuario 'malcaraz' no encontrado")
    conn.close()
    exit(1)

print(f"📋 Usuario encontrado: {user[0]}")
print(f"   Plan actual: {user[1]}")

# Actualizar a 'pro'
cursor.execute("UPDATE users SET plan_actual = %s WHERE username = %s", ('pro', 'malcaraz'))
conn.commit()

# Verificar cambio
cursor.execute("SELECT plan_actual FROM users WHERE username = %s", ('malcaraz',))
new_plan = cursor.fetchone()[0]

print(f"✅ Plan actualizado a: {new_plan}")

conn.close()
print("🎉 ¡Listo!")
