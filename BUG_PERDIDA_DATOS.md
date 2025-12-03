# 🔍 Análisis: Pérdida de Tareas en EasyPanel

## Problema
**Síntoma**: Al redesplegar en EasyPanel, todos los datos persisten EXCEPTO las tareas de "Mi Progreso"

## Investigación Realizada

### ✅ Verificado - NO es la causa:
1. **DELETE statements**: Solo en lugares correctos (botón generar estrategia)
2. **DROP TABLE**: No existe en ningún archivo
3. **init_db.py**: Usa `CREATE TABLE IF NOT EXISTS` (no borra datos)
4. **auto_init_db.py**: Solo inicializa si falta la BD

### 🤔 Hipótesis Más Probable

**El problema NO está en el código, sino en el volumen de EasyPanel**

#### Escenario Posible:
1. Usuario genera estrategia → Se crean tareas en `tareas_diarias`
2. Usuario redesplega en EasyPanel
3. EasyPanel reinicia contenedor
4. `auto_init_db.py` se ejecuta
5. Verifica que tabla `users` existe → No reinicializa
6. Pero `users.db` está en un volumen que NO persiste correctamente
7. O el volumen está montado en ruta incorrecta

## Solución Propuesta

### Opción 1: Verificar Configuración de Volumen en EasyPanel

**Verificar**:
- ¿El volumen persistente está montado en `/app`?
- ¿La ruta de `users.db` coincide con el volumen?
- ¿El volumen tiene permisos de escritura?

**Comando para verificar** (en terminal de EasyPanel):
```bash
ls -la /app/users.db
sqlite3 /app/users.db "SELECT COUNT(*) FROM tareas_diarias;"
```

### Opción 2: Agregar Logging para Debug

Agregar prints en `auto_init_db.py` para ver qué está pasando:

```python
def auto_initialize():
    print(f"📍 Checking database at: {os.path.abspath(DB_NAME)}")
    print(f"📍 Database exists: {os.path.exists(DB_NAME)}")
    
    if needs_initialization():
        print("🔄 Database needs initialization")
        # ... resto del código
```

### Opción 3: Forzar Verificación de Todas las Tablas

Modificar `needs_initialization()` para verificar TODAS las tablas críticas:

```python
def needs_initialization():
    # ... código existente ...
    
    # Verificar que tareas_diarias existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tareas_diarias'")
    if not c.fetchone():
        print("⚠️ Table tareas_diarias missing!")
        conn.close()
        return True
    
    # Verificar que tiene datos (opcional)
    c.execute("SELECT COUNT(*) FROM tareas_diarias")
    count = c.fetchone()[0]
    print(f"📊 tareas_diarias has {count} records")
```

## Próximos Pasos

1. **Verificar logs de EasyPanel** al redesplegar
2. **Confirmar ruta de volumen** en configuración
3. **Agregar logging** para debug
4. **Probar solución** según hallazgos

---

**Estado**: Investigación completa - Necesita verificación en EasyPanel
