# 🚀 Guía Rápida de Actualización en EasyPanel

## ✅ Cambios Desplegados

Se han corregido los siguientes errores:

1. ✅ **TypeError en Mi Progreso** - Agregadas validaciones null-safe
2. ✅ **Error en Admin Panel** - Eliminadas columnas inexistentes
3. ✅ **Script de inicialización mejorado** - Incluye TODAS las columnas necesarias
4. ✅ **Mejor manejo de usuarios sin datos** - Valores por defecto apropiados

---

## 📋 Pasos para Actualizar en EasyPanel

### 1. Redesplegar la Aplicación

1. Accede a tu panel de EasyPanel
2. Ve a tu proyecto **MiPymesIA**
3. Click en **"Deploy"** o **"Redeploy"**
4. Espera 2-3 minutos

### 2. Inicializar/Actualizar Base de Datos

Una vez que la aplicación esté desplegada, abre la terminal en EasyPanel y ejecuta:

```bash
# Opción A: Inicialización automática (RECOMENDADO)
python init_db.py
# Cuando pregunte, escribe: yes
```

Este script:
- ✅ Crea todas las tablas necesarias
- ✅ Agrega todas las columnas requeridas
- ✅ Marca las migraciones como ejecutadas
- ✅ NO borra datos existentes
- ✅ Es seguro ejecutar múltiples veces

### 3. Verificar

```bash
# Verificar que las tablas existen
sqlite3 users.db ".tables"

# Verificar estructura de users
sqlite3 users.db ".schema users"

# Salir
.exit
```

Deberías ver estas tablas:
- `users`
- `estrategias`
- `historial_secciones`
- `conversaciones_archivadas`
- `tareas_diarias`
- `progreso_semanal`
- `logros_usuario`
- `schema_migrations`

### 4. Reiniciar Aplicación

En EasyPanel:
- Click en **"Restart"** o simplemente cierra la terminal
- La aplicación se reiniciará automáticamente

---

## 🎯 Verificación Post-Actualización

Prueba estas funcionalidades:

- [ ] **Login** - Puedes iniciar sesión
- [ ] **Generar Estrategia** - Funciona sin errores
- [ ] **Mi Progreso** - Se muestra sin TypeError
- [ ] **Admin Panel** - Usuarios, Estadísticas y Configuración funcionan
- [ ] **Tareas** - Se pueden crear y completar tareas

---

## 🐛 Si Aún Hay Errores

### Error: "no such table: users"

```bash
# La base de datos está vacía, ejecuta:
python init_db.py
```

### Error: "no such column: X"

```bash
# Falta una columna, ejecuta:
python db_migrations.py
```

### Error Persistente

```bash
# Opción nuclear: Recrear base de datos (PERDERÁS DATOS)
rm users.db
python init_db.py
```

---

## 📝 Notas Importantes

1. **Base de Datos Persistente**: Si tu base de datos está en `/app/data/`, asegúrate de que el enlace simbólico esté correcto:
   ```bash
   ls -la users.db
   # Debería mostrar: users.db -> data/users.db
   ```

2. **Migraciones Automáticas**: El archivo `main.py` ejecuta `db_migrations.py` automáticamente al iniciar, pero solo si las tablas ya existen.

3. **Primera Vez**: Si es la primera vez que despliegas, DEBES ejecutar `init_db.py` manualmente.

---

## 🔄 Proceso Completo (Desde Cero)

Si estás empezando desde cero en un nuevo VPS/contenedor:

```bash
# 1. Verificar archivos
ls -la

# 2. Inicializar base de datos
python init_db.py
# Escribir: yes

# 3. Verificar
sqlite3 users.db ".tables"

# 4. Salir y dejar que la app inicie
exit
```

---

## ✅ Checklist Final

- [ ] Código actualizado desde GitHub (Deploy en EasyPanel)
- [ ] Base de datos inicializada (`python init_db.py`)
- [ ] Tablas verificadas (`sqlite3 users.db ".tables"`)
- [ ] Aplicación reiniciada
- [ ] Login funciona
- [ ] Mi Progreso funciona
- [ ] Admin Panel funciona

---

**¡Listo!** Tu aplicación debería estar funcionando correctamente ahora. 🎉
