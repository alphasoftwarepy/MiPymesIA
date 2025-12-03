# 📝 Plan de Implementación Detallado

## Problemas Identificados

1. ❌ **12 tareas en primer día** - No respeta límite de 5
2. ❌ **"Tareas" muestra tareas de otros días** - Debería mostrar solo hoy
3. ❌ **No se otorgan logros** - Sistema de logros no funciona
4. ❌ **Chats de IA persisten** - No se borran al generar nueva estrategia
5. ❌ **Cerebro se borra** - Se pierde conocimiento al generar nueva estrategia

---

## Fase 1: Correcciones Críticas ⚡

### 1.1 Límite de 5 Tareas por Día
**Archivo**: `tasks_manager.py`
**Problema**: La IA genera 12 tareas para el primer día
**Solución**: Post-procesamiento para redistribuir tareas si exceden el límite

### 1.2 Filtrar Tareas de Hoy
**Archivo**: `tracking_panel.py`
**Problema**: Tab "Tareas" muestra tareas de otros días
**Solución**: Cambiar query para mostrar SOLO tareas de hoy

### 1.3 Limpieza de Chats
**Archivo**: `main.py`
**Problema**: Chats de secciones no se borran
**Solución**: Verificar que se borren `historial_secciones` Y `conversaciones_archivadas`

### 1.4 Preservar Cerebro
**Archivo**: `main.py`
**Problema**: Se borra `business_profile` al generar nueva estrategia
**Solución**: NO borrar `business_profile`, solo limpiar chats y tareas

---

## Fase 2: Mejoras UX 🎨

### 2.1 Sistema de Logros
**Archivo**: `tasks_manager.py`
**Problema**: No se otorgan logros al completar tareas
**Solución**: Verificar función `check_achievements()`

### 2.2 Descripciones Motivacionales
**Archivo**: `tracking_panel.py`
**Problema**: Tabs sin descripciones
**Solución**: Agregar `st.info()` con mensajes motivacionales

---

## Fase 3: Optimizaciones ✨

### 3.1 Mensajes de Carga
**Archivo**: `main.py`, `ai_logic.py`
**Solución**: Implementar frases únicas y sub-pasos

### 3.2 Enriquecer Cerebro
**Archivo**: `main.py`
**Solución**: Agregar insights de nueva estrategia al cerebro

---

## Orden de Ejecución

1. ✅ Preservar Cerebro (crítico - evita pérdida de datos)
2. ✅ Limpieza de Chats (crítico - UX)
3. ✅ Filtrar Tareas de Hoy (crítico - UX)
4. ✅ Límite de 5 Tareas (crítico - funcionalidad)
5. ⏳ Sistema de Logros (importante)
6. ⏳ Descripciones Motivacionales (mejora)
7. ⏳ Mensajes de Carga (mejora)
8. ⏳ Enriquecer Cerebro (optimización)
