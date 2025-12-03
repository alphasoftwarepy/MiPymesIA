# 🚀 Despliegue en EasyPanel

## 📋 Situación Actual

✅ **Código subido a GitHub**: `github.com/cursosdigitaleshd-del/MiPymesIA`  
🎯 **Objetivo**: Actualizar la aplicación en EasyPanel

---

## ⚡ Despliegue Automático en EasyPanel

EasyPanel se conecta directamente a GitHub y despliega automáticamente. Aquí está el proceso:

### Opción 1: Redespliegue Automático (Recomendado)

1. **Accede a EasyPanel**
   - Ve a tu panel de EasyPanel
   - URL típica: `https://tu-dominio.easypanel.io`

2. **Localiza tu Proyecto**
   - Busca el proyecto `MiPymesIA` en tu lista de aplicaciones

3. **Redesplegar**
   - Click en el proyecto
   - Busca el botón **"Deploy"** o **"Redeploy"**
   - EasyPanel descargará automáticamente la última versión de GitHub
   - Esperará a que termine el despliegue

4. **Verificar**
   - Revisa los logs en EasyPanel
   - Verifica que la aplicación esté corriendo

---

## 🔧 Opción 2: Acceso por Terminal (Si necesitas ejecutar comandos)

Si necesitas acceder a la terminal de tu contenedor en EasyPanel:

### Paso 1: Abrir Terminal en EasyPanel

1. Ve a tu proyecto en EasyPanel
2. Busca la opción **"Terminal"** o **"Console"**
3. Se abrirá una terminal dentro del contenedor

### Paso 2: Ejecutar Migraciones (Si es necesario)

Una vez en la terminal del contenedor:

```bash
# Verificar que estás en el directorio correcto
pwd
ls -la

# Ejecutar migraciones de base de datos
python db_migrations.py

# Verificar base de datos
python -c "import sqlite3; conn = sqlite3.connect('users.db'); c = conn.cursor(); c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print([row[0] for row in c.fetchall()])"
```

---

## 🔄 Configuración de Auto-Deploy (Recomendado)

Para que EasyPanel actualice automáticamente cuando hagas push a GitHub:

### Configurar Webhook de GitHub

1. **En EasyPanel:**
   - Ve a tu proyecto
   - Busca la sección **"GitHub Integration"** o **"Webhooks"**
   - Copia la URL del webhook

2. **En GitHub:**
   - Ve a `https://github.com/cursosdigitaleshd-del/MiPymesIA/settings/hooks`
   - Click en **"Add webhook"**
   - Pega la URL del webhook de EasyPanel
   - Selecciona eventos: `push` events
   - Click en **"Add webhook"**

3. **Resultado:**
   - Cada vez que hagas `git push`, EasyPanel actualizará automáticamente
   - No necesitarás hacer nada manual

---

## 📊 Variables de Entorno en EasyPanel

**IMPORTANTE**: Asegúrate de que las variables de entorno estén configuradas en EasyPanel:

### Cómo Configurar Variables de Entorno

1. **Accede a tu proyecto en EasyPanel**

2. **Busca la sección "Environment Variables" o "Env Vars"**

3. **Agrega las siguientes variables:**

```env
OPENAI_API_KEY=tu_api_key_aqui
GOOGLE_SHEETS_ESTRATEGIAS_ID=tu_sheet_id_aqui
GOOGLE_SHEETS_NEGOCIOS_ID=tu_sheet_id_aqui
```

4. **Guarda y Redesplega**
   - Después de agregar las variables, redesplega la aplicación

---

## 🗄️ Base de Datos en EasyPanel

### Opción A: Base de Datos Persistente (Recomendado)

Si tu base de datos está en un volumen persistente:

1. **Verifica el Volumen**
   - En EasyPanel, ve a la sección **"Volumes"** o **"Storage"**
   - Asegúrate de que `users.db` esté en un volumen montado
   - Ruta típica: `/app/users.db` o `/data/users.db`

2. **Las Migraciones se Ejecutarán Automáticamente**
   - El archivo `main.py` ejecuta `db_migrations.py` al iniciar
   - Esto actualizará el esquema sin perder datos

### Opción B: Migrar Base de Datos Manualmente

Si necesitas actualizar la base de datos manualmente:

#### 1. Exportar Datos del VPS (Desde la terminal de EasyPanel)

```bash
# En la terminal de EasyPanel
python export_user_data.py export users_backup.json

# Descargar el archivo (usa la interfaz de EasyPanel o SCP)
```

#### 2. Importar a Nueva Base de Datos

```bash
# Si necesitas importar datos
python export_user_data.py import users_backup.json
```

---

## 🔍 Verificación Post-Despliegue

### En la Interfaz de EasyPanel

1. **Estado de la Aplicación**
   - Verifica que el estado sea **"Running"** (verde)
   - Si está en rojo o amarillo, revisa los logs

2. **Logs de la Aplicación**
   - Click en **"Logs"** o **"View Logs"**
   - Busca mensajes como:
     ```
     🔄 Checking for pending database migrations...
     ✅ Database is up to date
     ```

3. **Acceder a la Aplicación**
   - Click en el URL de tu aplicación
   - Intenta iniciar sesión
   - Verifica que las nuevas funcionalidades estén disponibles

---

## 🚨 Solución de Problemas en EasyPanel

### Error: "Application Failed to Start"

1. **Revisa los logs en EasyPanel**
   - Busca errores de Python o dependencias

2. **Verifica las variables de entorno**
   - Asegúrate de que todas estén configuradas

3. **Verifica el Dockerfile**
   - EasyPanel usa el `Dockerfile` del repositorio
   - Asegúrate de que esté actualizado

### Error: "Database Locked"

```bash
# En la terminal de EasyPanel
# Detener procesos que usen la DB
pkill -f streamlit

# Reiniciar la aplicación desde EasyPanel
```

### Error: "Missing Dependencies"

```bash
# En la terminal de EasyPanel
pip install -r requirements.txt
```

---

## 📝 Proceso Completo Paso a Paso

### Para Actualizar tu Aplicación en EasyPanel:

1. ✅ **Ya hiciste**: Push a GitHub
   ```powershell
   git push origin main  # ✅ COMPLETADO
   ```

2. **Ahora en EasyPanel**:
   
   **Opción A - Auto Deploy (Si está configurado):**
   - Espera 1-2 minutos
   - EasyPanel detectará el cambio automáticamente
   - Verifica los logs

   **Opción B - Manual:**
   - Accede a EasyPanel
   - Ve a tu proyecto `MiPymesIA`
   - Click en **"Deploy"** o **"Redeploy"**
   - Espera a que termine (1-3 minutos)

3. **Verificar**:
   - Revisa los logs en EasyPanel
   - Accede a la URL de tu aplicación
   - Prueba iniciar sesión
   - Verifica nuevas funcionalidades

---

## 🎯 Resumen Rápido

```
1. ✅ Código en GitHub (Ya hecho)
2. 🔄 EasyPanel → Click en "Deploy/Redeploy"
3. ⏱️  Esperar 1-3 minutos
4. ✅ Verificar logs y aplicación
```

---

## 📞 Checklist Final

Después del despliegue en EasyPanel, verifica:

- [ ] La aplicación está en estado "Running" (verde)
- [ ] No hay errores en los logs
- [ ] Puedes acceder a la URL de la aplicación
- [ ] Los usuarios pueden iniciar sesión
- [ ] Las nuevas funcionalidades están disponibles
- [ ] El sistema de tareas funciona
- [ ] La generación de estrategias funciona

---

## 💡 Consejos para EasyPanel

1. **Usa Volúmenes Persistentes** para la base de datos
2. **Configura Auto-Deploy** para actualizaciones automáticas
3. **Revisa los logs regularmente** después de cada despliegue
4. **Haz backup** de la base de datos antes de cambios importantes
5. **Usa variables de entorno** para configuración sensible

---

## 🔗 Enlaces Útiles

- **Tu Repositorio**: https://github.com/cursosdigitaleshd-del/MiPymesIA
- **EasyPanel Docs**: https://easypanel.io/docs
- **Guía Detallada**: Ver `DEPLOY.md` en el repositorio

---

**¿Necesitas ayuda para acceder a EasyPanel o configurar el despliegue?**
