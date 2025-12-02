# Guía de Despliegue - MiPymesIA

## Situación Actual
- **Versión Local**: Más actualizada y completa
- **Versión VPS**: Desactualizada
- **Base de Datos Local**: Más completa que la del VPS
- **Objetivo**: Subir versión local a GitHub y desplegar en VPS

---

## 📋 Plan de Despliegue

### Fase 1: Preparación y Backup

#### 1.1 Backup del VPS (CRÍTICO)
Antes de hacer cualquier cambio, respalda todo en el VPS:

```bash
# Conectarse al VPS
ssh usuario@tu-vps-ip

# Crear directorio de backup
mkdir -p ~/backups/mipymesia_$(date +%Y%m%d_%H%M%S)

# Backup de la base de datos
cp /ruta/a/tu/proyecto/users.db ~/backups/mipymesia_$(date +%Y%m%d_%H%M%S)/

# Backup del código completo
cp -r /ruta/a/tu/proyecto ~/backups/mipymesia_$(date +%Y%m%d_%H%M%S)/codigo
```

#### 1.2 Backup Local
```powershell
# Crear backup de la base de datos local
Copy-Item "c:\MiPymesIA\users.db" "c:\MiPymesIA\users_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
```

---

### Fase 2: Preparar Repositorio Local

#### 2.1 Verificar Estado de Git
```powershell
cd c:\MiPymesIA
git status
git log --oneline -10
```

#### 2.2 Crear .gitignore Apropiado
Asegúrate de que estos archivos NO se suban a GitHub:

```gitignore
# Archivos sensibles
.env
users.db
*.db

# Entornos virtuales
.venv/
venv/
env/

# Cache de Python
__pycache__/
*.pyc
*.pyo

# Archivos temporales
*.log
temp_*.txt
```

#### 2.3 Exportar Esquema de Base de Datos
Necesitamos exportar el esquema y datos importantes (sin datos sensibles):

```powershell
# Ejecutar script de exportación (crear este archivo)
python export_db_schema.py
```

---

### Fase 3: Commit y Push a GitHub

#### 3.1 Agregar Cambios
```powershell
# Ver qué archivos han cambiado
git status

# Agregar todos los archivos (excepto los del .gitignore)
git add .

# Verificar qué se va a commitear
git status
```

#### 3.2 Crear Commit
```powershell
git commit -m "feat: Actualización completa del sistema

- Sistema de suscripciones mejorado
- Sistema de tareas y gamificación
- Mejoras en generación de estrategias
- Migraciones de base de datos automatizadas
- Panel de administración mejorado
- Múltiples correcciones de bugs"
```

#### 3.3 Push a GitHub
```powershell
# Si es la primera vez o hay conflictos
git pull origin main --rebase

# Subir cambios
git push origin main
```

---

### Fase 4: Migración de Base de Datos

#### 4.1 Estrategia de Migración
Tienes dos opciones:

**Opción A: Migración Completa (Recomendada si hay pocos usuarios)**
- Exportar datos de usuarios del VPS
- Importarlos a tu base de datos local
- Subir la base de datos completa al VPS

**Opción B: Migración Incremental (Recomendada si hay muchos usuarios)**
- Usar el sistema de migraciones automáticas (`db_migrations.py`)
- Aplicar cambios de esquema sin perder datos del VPS

#### 4.2 Script de Exportación de Datos (Opción A)

Crear `export_user_data.py`:
```python
import sqlite3
import json
from datetime import datetime

def export_users_data(db_path="users.db", output_file="users_export.json"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Exportar usuarios
    c.execute("SELECT * FROM users")
    users = [dict(row) for row in c.fetchall()]
    
    # Exportar estrategias
    c.execute("SELECT * FROM estrategias")
    estrategias = [dict(row) for row in c.fetchall()]
    
    # Exportar tareas
    c.execute("SELECT * FROM tareas_diarias")
    tareas = [dict(row) for row in c.fetchall()]
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "users": users,
        "estrategias": estrategias,
        "tareas": tareas
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    conn.close()
    print(f"✅ Datos exportados a {output_file}")

if __name__ == "__main__":
    export_users_data()
```

---

### Fase 5: Despliegue en VPS

#### 5.1 Conectar al VPS
```bash
ssh usuario@tu-vps-ip
```

#### 5.2 Actualizar Código desde GitHub
```bash
cd /ruta/a/tu/proyecto

# Detener la aplicación
sudo systemctl stop mipymesia  # o el comando que uses

# Actualizar código
git pull origin main

# Activar entorno virtual
source .venv/bin/activate  # o el path de tu venv

# Actualizar dependencias
pip install -r requirements.txt
```

#### 5.3 Aplicar Migraciones de Base de Datos
```bash
# Opción B (Incremental - Recomendada)
python db_migrations.py

# Esto aplicará automáticamente todas las migraciones pendientes
# sin perder datos existentes
```

#### 5.4 Reiniciar Aplicación
```bash
# Reiniciar servicio
sudo systemctl start mipymesia
sudo systemctl status mipymesia

# Ver logs para verificar
sudo journalctl -u mipymesia -f
```

---

### Fase 6: Verificación Post-Despliegue

#### 6.1 Checklist de Verificación
- [ ] La aplicación inicia sin errores
- [ ] Los usuarios existentes pueden iniciar sesión
- [ ] Las nuevas funcionalidades están disponibles
- [ ] La base de datos tiene todas las tablas necesarias
- [ ] No hay errores en los logs

#### 6.2 Verificar Base de Datos
```bash
sqlite3 users.db

# Verificar tablas
.tables

# Verificar estructura de users
.schema users

# Verificar que existen las nuevas tablas
SELECT name FROM sqlite_master WHERE type='table';

# Salir
.exit
```

#### 6.3 Pruebas Funcionales
1. Iniciar sesión con usuario existente
2. Generar una estrategia
3. Verificar sistema de tareas
4. Verificar panel de administración
5. Verificar límites de suscripción

---

## 🚨 Solución de Problemas

### Error: "Database is locked"
```bash
# Detener la aplicación
sudo systemctl stop mipymesia

# Verificar procesos
ps aux | grep python

# Matar procesos si es necesario
kill -9 <PID>
```

### Error: Columnas faltantes
```bash
# Ejecutar migraciones manualmente
python db_migrations.py
```

### Error: Conflictos de Git
```bash
# Ver diferencias
git diff

# Guardar cambios locales
git stash

# Actualizar
git pull origin main

# Aplicar cambios guardados
git stash pop
```

---

## 📝 Notas Importantes

1. **Variables de Entorno**: Asegúrate de que el archivo `.env` en el VPS tenga todas las variables necesarias
2. **Permisos**: Verifica que el usuario que ejecuta la app tenga permisos sobre `users.db`
3. **Backup Regular**: Configura backups automáticos de la base de datos
4. **Monitoreo**: Revisa los logs regularmente después del despliegue

---

## 🔄 Proceso Rápido (Resumen)

```powershell
# LOCAL
cd c:\MiPymesIA
git add .
git commit -m "Actualización completa del sistema"
git push origin main
```

```bash
# VPS
cd /ruta/proyecto
sudo systemctl stop mipymesia
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python db_migrations.py
sudo systemctl start mipymesia
sudo systemctl status mipymesia
```

---

## 📞 Contacto y Soporte

Si encuentras problemas durante el despliegue, documenta:
1. El paso exacto donde ocurrió el error
2. El mensaje de error completo
3. Los últimos 50 líneas de logs: `sudo journalctl -u mipymesia -n 50`
