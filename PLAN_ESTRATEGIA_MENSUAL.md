# 🎯 Plan de Implementación - Sistema de Estrategia Mensual

## Problemas Críticos Actuales a Resolver PRIMERO

### 1. ❌ Tareas con mismo nombre se tachan todas
**Problema**: Al completar "Agendar demo" del día 1, se tachan también las del día 5 y 33
**Solución**: Agregar identificador único al título mostrado
```
Formato: [Título] - Día [X]
Ejemplo: "Agendar y realizar una demo con un prospecto - Día 1"
```

### 2. ❌ Logros no se actualizan
**Problema**: Al completar todas las tareas del día 1, no aparecen logros
**Solución**: Investigar por qué `check_achievements()` no funciona
- Verificar que se llame después de completar tarea
- Revisar criterios de logros
- Verificar inserción en tabla `logros_usuario`

### 3. ❌ No se puede desmarcar tarea completada
**Problema**: Si marco tarea por error, no puedo desmarcarlo
**Solución**: Implementar `uncomplete_task()` funcional
- Restar puntos
- Actualizar racha si es necesario
- Permitir checkbox bidireccional

---

## Nuevo Sistema de Estrategia Mensual

### Fase A: Análisis de Complejidad (IA)

**Input del usuario**:
- Meta actual
- Situación actual (ventas, seguidores, etc.)
- Presupuesto
- Tiempo disponible

**Output de la IA**:
```json
{
  "plazo_sugerido": 3,  // meses
  "justificacion": "Pasar de 100 USD a 1000 USD requiere construir audiencia, optimizar conversión y escalar gradualmente",
  "tareas_totales": 450,  // 150 por mes
  "tareas_por_dia": 5
}
```

### Fase B: Generación de Tareas Escaladas

**Cantidad de tareas**:
- 1 mes: 150 tareas (5/día x 30 días)
- 2 meses: 300 tareas (5/día x 60 días)
- 3 meses: 450 tareas (5/día x 90 días)

**Distribución**:
- Mes 1: Fundamentos y setup
- Mes 2: Optimización y escalamiento
- Mes 3: Consolidación y resultados

### Fase C: Vista Mensual con Calendario

**Tabs en Mi Progreso**:

1. **📋 Tareas de Hoy**
   - Muestra solo las 5 tareas sugeridas para hoy
   - Usuario puede completar más si quiere

2. **📅 Vista Mensual**
   - Calendario interactivo de 30 días
   - Navegación: ← Mes Anterior | Mes Actual | Mes Siguiente →
   - Cada día muestra sus tareas asignadas
   - Días con tareas completadas: ✅ verde
   - Día actual: destacado

3. **🏆 Logros y Estadísticas**
   - Barra de progreso general: "Día 15 de 90 (17%)"
   - Logros desbloqueados
   - Estadísticas por categoría

### Fase D: Progreso y Timeline

**Barra de Progreso General**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45%
Día 41 de 90 | 185 de 450 tareas completadas
Estrategia de 3 meses | A este ritmo terminarás en 2 meses
```

**Cálculo de Timeline Real**:
- Si usuario completa 10 tareas/día en vez de 5 → termina en la mitad del tiempo
- Sistema muestra proyección: "A este ritmo terminarás en X días"

---

## Orden de Implementación

### Sprint 1: Correcciones Críticas (URGENTE)
1. ✅ Agregar identificador de día a títulos de tareas
2. ✅ Implementar desmarcar tarea (uncomplete_task)
3. ✅ Investigar y corregir sistema de logros

### Sprint 2: Sistema de Análisis de Complejidad
4. ⏳ Prompt de IA para analizar complejidad del objetivo
5. ⏳ Determinar plazo (1, 2 o 3 meses)
6. ⏳ Ajustar cantidad de tareas según plazo

### Sprint 3: Generación de Tareas Escaladas
7. ⏳ Generar 150 tareas para 1 mes
8. ⏳ Generar 300 tareas para 2 meses
9. ⏳ Generar 450 tareas para 3 meses
10. ⏳ Distribuir tareas en calendario mensual

### Sprint 4: Vista Mensual con Calendario
11. ⏳ Crear componente de calendario mensual
12. ⏳ Navegación entre meses
13. ⏳ Mostrar tareas por día en calendario
14. ⏳ Indicadores visuales (completadas, pendientes)

### Sprint 5: Progreso y Timeline
15. ⏳ Barra de progreso general
16. ⏳ Cálculo de timeline real
17. ⏳ Proyección de finalización

---

## Cambios en Base de Datos

### Nueva columna en `users`:
```sql
ALTER TABLE users ADD COLUMN estrategia_plazo INTEGER DEFAULT 1;  -- meses
ALTER TABLE users ADD COLUMN estrategia_inicio TEXT;  -- fecha ISO
ALTER TABLE users ADD COLUMN estrategia_dias_totales INTEGER DEFAULT 30;
```

### Nueva columna en `tareas_diarias`:
```sql
ALTER TABLE tareas_diarias ADD COLUMN dia_numero INTEGER;  -- 1-90
```

---

## Ejemplo de Flujo Completo

1. Usuario: "Quiero vender 1000 USD/mes (actualmente vendo 100 USD)"
2. IA analiza → Determina: 3 meses necesarios
3. IA genera 450 tareas distribuidas en 90 días
4. Usuario ve:
   - Tab "Tareas de Hoy": 5 tareas del día 1
   - Tab "Vista Mensual": Calendario de 30 días (Mes 1)
   - Tab "Logros": Barra "Día 1 de 90 (1%)"
5. Usuario completa 10 tareas hoy (en vez de 5)
6. Sistema: "A este ritmo terminarás en 45 días en vez de 90"
7. Usuario termina en día 45
8. Sistema: "🎉 Objetivo completado! Genera nueva estrategia para seguir creciendo"

---

## Prioridad de Implementación

**AHORA (Sprint 1)**:
- Identificador de día en títulos
- Desmarcar tareas
- Corregir logros

**DESPUÉS (Sprints 2-5)**:
- Sistema mensual completo
- Análisis de complejidad
- Vista calendario

¿Empezamos con Sprint 1 (correcciones críticas)?
