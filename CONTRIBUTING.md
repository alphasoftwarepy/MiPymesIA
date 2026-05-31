# Guía de Contribución a MiPymesIA 🤝

¡Gracias por tu interés en contribuir a MiPymesIA! Tu ayuda es fundamental para mejorar esta herramienta para miles de emprendedores.

---

## 💻 Configuración del Entorno de Desarrollo Local

1. **Bifurcar (Fork) el repositorio** en tu cuenta de GitHub.
2. **Clonar tu bifurcación localmente:**
   ```bash
   git clone https://github.com/tu-usuario/MiPymesIA.git
   cd MiPymesIA
   ```
3. **Crear una rama para tu feature o corrección:**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   # o para correcciones de bugs:
   git checkout -b bugfix/corregir-error
   ```
4. **Instalar dependencias y levantar el servidor local** como se indica en el [README.md](README.md).

---

## 🛠️ Convenciones del Proyecto

### Formato de Commits Recomendado
Seguimos la convención de **Conventional Commits**:
* `feat:` Para nuevas funcionalidades (ej. `feat: agregar fallback para API key OPENIA_API_KEY`)
* `fix:` Para corrección de errores (ej. `fix: corregir tamaño de pdf generado en móvil`)
* `docs:` Cambios solo en documentación (ej. `docs: añadir notas de arquitectura en dev-notes`)
* `refactor:` Cambios en código que no corrigen bugs ni agregan features (ej. `refactor: modularizar funciones de db_config`)

### Convenciones de Ramas
* La rama principal es `main`.
* No realices contribuciones directamente sobre `main`. Utiliza ramas descriptivas e inicia un Pull Request (PR) hacia `main`.

---

## 📬 Envío de Pull Requests

1. Asegúrate de que los pre-deployment checks pasen localmente ejecutando:
   ```bash
   python pre_deploy_check.py
   ```
2. Realiza el push de tu rama hacia tu repositorio bifurcado:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```
3. Ve a la página del repositorio original en GitHub y abre un Pull Request explicando detalladamente tus cambios, por qué son necesarios y cómo pueden probarse.
