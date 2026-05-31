# Changelog - MiPymesIA 📜

Todos los cambios notables en este proyecto serán documentados en este archivo. El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [1.2.0] - 2026-05-31

### Añadido
* Nueva estructura estándar de documentación del proyecto (`README.md`, `ROADMAP.md`, `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`).
* Carpeta interna de notas técnicas de desarrollo `dev-notes/` para soporte del equipo.

### Cambiado
* Migración del motor de base de datos a PostgreSQL (`db_config.py` y `db_migrations.py`).
* Refactorización de las tablas del sistema en `auth.py` para compatibilidad nativa con Postgres.

### Seguridad
* Adición de soporte para configurar la contraseña del administrador por defecto vía variable de entorno en lugar de usar un string hardcodeado en la base de código.
