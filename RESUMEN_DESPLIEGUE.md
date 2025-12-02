# 📦 Resumen de Archivos Creados para Despliegue

## ✅ Archivos Creados

### 📘 Documentación

1. **DEPLOY.md** - Guía detallada paso a paso del proceso de despliegue
2. **DEPLOYMENT_GUIDE.md** - Guía rápida con comandos y herramientas
3. **.env.template** - Plantilla de variables de entorno

### 🔧 Scripts de Utilidad

4. **pre_deploy_check.py** - Verificación pre-despliegue (ejecutar antes de subir a GitHub)
5. **export_db_schema.py** - Exporta esquema de base de datos para documentación
6. **export_user_data.py** - Exporta/importa/compara datos de usuarios

### 🚀 Scripts de Despliegue

7. **deploy_to_github.bat** - Script automático para Windows (local → GitHub)
8. **deploy_on_vps.sh** - Script automático para Linux (GitHub → VPS)

### 🔒 Seguridad

9. **.gitignore** - Actualizado para proteger datos sensibles

---

## 🎯 Cómo Usar

### Opción 1: Despliegue Automático (RECOMENDADO)

#### En Windows (Local):
```powershell
.\deploy_to_github.bat
```

Este script:
- ✅ Ejecuta verificaciones pre-despliegue
- ✅ Exporta esquema de base de datos
- ✅ Muestra estado de Git
- ✅ Solicita confirmación
- ✅ Hace commit y push a GitHub

#### En VPS (Linux):
```bash
bash deploy_on_vps.sh
```

Este script:
- ✅ Crea backup automático
- ✅ Detiene la aplicación
- ✅ Descarga código de GitHub
- ✅ Actualiza dependencias
- ✅ Ejecuta migraciones
- ✅ Verifica base de datos
- ✅ Reinicia la aplicación

### Opción 2: Despliegue Manual

#### Paso 1: Verificar (Local)
```powershell
python pre_deploy_check.py
```

#### Paso 2: Subir a GitHub (Local)
```powershell
git add .
git commit -m "feat: Actualización completa del sistema"
git push origin main
```

#### Paso 3: Desplegar en VPS
```bash
ssh usuario@vps-ip
cd /ruta/proyecto
sudo systemctl stop mipymesia
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python db_migrations.py
sudo systemctl start mipymesia
```

---

## 📊 Estado Actual del Proyecto

Según el último check:

✅ **Git Repository**: Configurado correctamente  
✅ **Git Ignore**: Protegiendo archivos sensibles  
✅ **Database**: 152 KB, 6 tablas, 50 registros  
✅ **Dependencies**: 10 paquetes listados  
✅ **Migrations**: 2 migraciones ejecutadas  
✅ **Critical Files**: Todos presentes  

⚠️ **Environment File**: Faltan algunas variables (revisar .env)

---

## 🔍 Verificaciones Pre-Despliegue

El script `pre_deploy_check.py` verifica:

1. ✅ Estado de Git y repositorio remoto
2. ✅ Archivo .env y variables requeridas
3. ✅ Configuración de .gitignore
4. ✅ Base de datos y tablas
5. ✅ Dependencias (requirements.txt)
6. ✅ Sistema de migraciones
7. ✅ Archivos críticos del proyecto

---

## 🗄️ Gestión de Base de Datos

### Exportar Datos
```bash
# Exportar todo
python export_user_data.py export

# Exportar con nombre personalizado
python export_user_data.py export mi_backup.json
```

### Comparar Bases de Datos
```bash
# Comparar local con exportación del VPS
python export_user_data.py compare users_export_vps.json
```

### Exportar Esquema
```bash
# Genera database_schema.sql y database_structure.md
python export_db_schema.py
```

---

## 🔐 Seguridad

### Archivos Protegidos (NO se suben a GitHub)

- `.env` - Variables de entorno
- `*.db` - Bases de datos
- `users_export*.json` - Exportaciones de datos
- `*_backup*.py` - Archivos de respaldo
- `__pycache__/` - Cache de Python
- `temp_*` - Archivos temporales

### Variables de Entorno Requeridas

```env
OPENAI_API_KEY=sk-...
GOOGLE_SHEETS_ESTRATEGIAS_ID=...
GOOGLE_SHEETS_NEGOCIOS_ID=...
```

---

## 🚨 Importante

### Antes de Desplegar

1. ✅ Ejecuta `pre_deploy_check.py`
2. ✅ Verifica que `.env` tiene todas las variables
3. ✅ Haz backup de la base de datos del VPS
4. ✅ Revisa los cambios con `git status`

### Después de Desplegar

1. ✅ Verifica que la app inicia: `systemctl status mipymesia`
2. ✅ Revisa los logs: `journalctl -u mipymesia -f`
3. ✅ Prueba login de usuarios
4. ✅ Verifica nuevas funcionalidades

---

## 📚 Documentación

- **DEPLOYMENT_GUIDE.md** - Guía rápida de referencia
- **DEPLOY.md** - Guía detallada completa
- **.env.template** - Plantilla de configuración

---

## 🆘 Solución de Problemas

### Si algo falla en el VPS:

```bash
# Ver logs
sudo journalctl -u mipymesia -n 100

# Verificar base de datos
sqlite3 users.db ".tables"

# Verificar permisos
ls -la users.db

# Restaurar backup
cp ~/backups/mipymesia_YYYYMMDD_HHMMSS/users.db ./
```

### Si hay conflictos de Git:

```bash
git stash
git pull origin main
git stash pop
```

---

## ✨ Próximos Pasos

1. **Revisar** este resumen
2. **Ejecutar** `pre_deploy_check.py` para verificar estado
3. **Configurar** variables de entorno faltantes (si las hay)
4. **Ejecutar** `deploy_to_github.bat` para subir a GitHub
5. **Conectar** al VPS y ejecutar `deploy_on_vps.sh`
6. **Verificar** que todo funciona correctamente

---

**¡Todo listo para desplegar!** 🚀
