# Guía de Despliegue en EasyPanel

Este proyecto está configurado para desplegarse fácilmente en EasyPanel.

## Base de Datos (`users.db`)

La base de datos SQLite `users.db` **NO se sube al repositorio** por razones de seguridad y para evitar conflictos. Está en el `.gitignore`.

### 1. Primera Instalación (Base de Datos Nueva)
Si es la primera vez que despliegas y no tienes datos previos:
- No necesitas hacer nada. La aplicación creará automáticamente una base de datos vacía al iniciar.
- Se creará un usuario administrador por defecto si no existe ninguno.

### 2. Migrar Datos Existentes (Subir tu DB Local)
Si tienes una base de datos local con usuarios y quieres conservarla en producción:

1.  Despliega la aplicación en EasyPanel.
2.  Ve a la pestaña **"Console"** o **"File Manager"** de tu servicio en EasyPanel.
3.  Navega a la carpeta `/app/data` (o donde esté montado el volumen persistente).
    *   *Nota: Si no has configurado un volumen, los datos se perderán en cada despliegue. Asegúrate de montar un volumen en `/app/data`.*
4.  Sube tu archivo `users.db` local a esa carpeta, reemplazando el existente si es necesario.
5.  Reinicia el servicio.

## Migraciones Automáticas

El sistema cuenta con un gestor de migraciones automático (`db_migrations.py`).
Cada vez que la aplicación se inicia, verifica si la base de datos necesita actualizaciones (nuevas columnas, tablas, etc.) y las aplica automáticamente.

Esto significa que puedes subir una base de datos antigua, y el sistema la actualizará a la última versión sin que pierdas datos.
