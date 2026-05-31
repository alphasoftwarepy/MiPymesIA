# Roadmap del Proyecto - MiPymesIA 📌

Este documento detalla el estado actual del desarrollo de la plataforma, las mejoras inmediatas y el backlog a largo plazo basadas en la arquitectura actual basada en PostgreSQL y Streamlit.

---

## 🛠️ Fase Actual: Estabilización y Migración a PostgreSQL

El sistema cuenta actualmente con las siguientes características completamente operativas:
* **Persistencia en PostgreSQL:** Todo el esquema se inicializa e integra de manera idempotente usando `psycopg2` y el módulo `db_config.py`.
* **Soporte Multi-Estrategia (Estrategias V2):** Los usuarios pueden tener múltiples estrategias activas por producto/servicio en paralelo.
* **Gamificación Básica:** Registro de tareas completadas, asignación de puntos, niveles y rachas de días activos.
* **Descarga de PDF:** Exportación en PDF formateado de la estrategia de marketing y plan de anuncios.
* **Generación de Tareas con OpenAI:** Creación de listas de tareas semanales estructuradas para el Roadmap diario.

---

## 📈 Próximas Mejoras (Corto y Mediano Plazo)

### Estabilidad y Robustez
* [ ] **Limpieza de Scripts de la Raíz:** Mover los más de 40 scripts auxiliares antiguos a un directorio `legacy_scripts/` para limpiar la estructura.
* [ ] **Refactorización de `deploy_on_vps.sh`:** Eliminar dependencias de `users.db` (SQLite) del script de despliegue y adaptarlo al entorno de base de datos PostgreSQL en red.
* [ ] **Reconstrucción del Entorno Virtual Local:** Eliminar `.venv` obsoletos y documentar la instalación limpia bajo Python 3.11+.

### Seguridad y Observabilidad
* [ ] **Contraseñas Dinámicas en Inicialización:** Retirar la contraseña por defecto del administrador hardcodeada en `auth.py` y parametrizarla mediante `ADMIN_DEFAULT_PASSWORD`.
* [ ] **Auditoría de Consultas SQL:** Cambiar todos los inserts crudos que aún queden por llamadas parametrizadas seguras.
* [ ] **Logger Centralizado:** Implementar el módulo `logging` estándar de Python en lugar de llamadas directas a `print()`, facilitando el monitoreo en contenedores Docker.

### UX & IA
* [ ] **Mejora en Detección de API Key:** Integrar el fallback robusto para detectar `OPENIA_API_KEY` (typo común de usuario) y propagar errores detallados de cuota excedida de OpenAI directamente en la interfaz.

---

## 📥 Backlog (Ideas Futuras)

* [ ] **Integración Real con Meta/Google API:** Permitir publicar anuncios o programar posts directamente desde el panel de tareas del Roadmap.
* [ ] **Panel de Analíticas Visuales:** Gráficos e indicadores visuales de conversión basados en las métricas sugeridas (Costo por Lead, CTR, Tasa de Cierre).
* [ ] **Soporte para Modelos Locales:** Opción de fallback hacia modelos open-source utilizando Ollama o integradores como OpenRouter.

---

## ⚠️ Deuda Técnica Detectada

1. **Scripts Auxiliares SQLite Activos:** Herramientas de exportación (`export_db_schema.py`) y verificación que asumen que la base de datos sigue siendo SQLite local.
2. **Duplicidad de Código AI:** Existe `ai_logic.py` y `ai_logic_new.py` con lógicas similares pero ligeramente divergentes de inicialización y prompts. Se debe unificar en un solo módulo de IA de alto rendimiento.
3. **Manejo Manual de Conexiones PostgreSQL:** `db_config.py` abre conexiones directas usando `psycopg2` para evitar fallas del pool, pero requiere un manejo cuidadoso de cierres para evitar fugas de conexiones en el servidor PostgreSQL.
