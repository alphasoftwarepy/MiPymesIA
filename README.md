# MiPymesIA 🚀

Plataforma inteligente de generación de estrategias de marketing digital y gestión de tareas orientada a micro, pequeñas y medianas empresas (MiPyMEs).

## 📝 El Problema que Resuelve

Las MiPyMEs usualmente carecen de presupuesto para contratar agencias de marketing o especialistas a tiempo completo. Además, enfrentan la dificultad de ejecutar planes de marketing de forma consistente. 

**MiPymesIA** resuelve esto:
1. **Generando Estrategias Personalizadas:** Utiliza IA (OpenAI GPT-4o-mini) para formular embudos de contenido, copys para anuncios de tráfico frío/tibio/caliente, flujos de WhatsApp y manejo de objeciones específicas al negocio.
2. **Facilitando la Ejecución:** Transforma la estrategia en un plan de acción diario interactivo (Roadmap) con un sistema de gamificación (puntos, niveles y rachas) para mantener al usuario enfocado y motivado.

---

## 🏗️ Arquitectura Actual

El sistema está diseñado bajo una arquitectura monolítica modular construida en Python:
* **Frontend/UI:** Interfaz web interactiva impulsada por **Streamlit**.
* **Base de Datos:** Motor relacional **PostgreSQL** para persistencia de datos (usuarios, estrategias, tareas, logs).
* **Motor de IA:** Integración con **OpenAI API** y **LangChain** para orquestación de prompts y persistencia del contexto del negocio ("Cerebro de Negocio").
* **Programador de Tareas:** **APScheduler** para ejecutar rutinas automáticas (como el reinicio de límites diarios a las 2 AM).

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.11+
* **Framework Web:** Streamlit
* **ORACLE / ORM:** psycopg2 (Acceso nativo a PostgreSQL con wrappers compatibles)
* **Framework de IA:** LangChain y OpenAI SDK
* **Generación de Reportes:** FPDF (Generación automática de estrategias en PDF descargables)
* **Seguridad:** Bcrypt & Passlib (Hasheo robusto de contraseñas)
* **Programación:** APScheduler (Tareas en segundo plano)

---

## ⚙️ Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto basándote en `.env.template`:

```env
# URL de conexión a la base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/mipymes

# OpenAI API Key (o puedes usar el alias alternativo OPENIA_API_KEY)
OPENAI_API_KEY=sk-proj-tu-api-key-aqui

# Contraseña inicial por defecto para el administrador del sistema (Opcional)
ADMIN_DEFAULT_PASSWORD=alphaSoftware!
```

---

## 🐳 Ejecución con Docker

### Requisitos
* Docker y Docker Compose instalados.

### Levantamiento Rápido (Desarrollo local)
Para construir e iniciar la aplicación junto con una base de datos PostgreSQL:

```bash
docker-compose up --build
```

La aplicación estará disponible en `http://localhost:8501`.

---

## 🚀 Despliegue en EasyPanel (Producción)

1. Crea un nuevo servicio **App** en tu instancia de EasyPanel apuntando a tu repositorio Git.
2. Crea un servicio **PostgreSQL** en EasyPanel.
3. En la configuración de variables de entorno de tu App, vincula la base de datos y agrega las siguientes variables:
   * `DATABASE_URL` (Usa el valor provisto por EasyPanel para enlazar tu Postgres)
   * `OPENAI_API_KEY`
   * `ADMIN_DEFAULT_PASSWORD`
4. EasyPanel leerá automáticamente el `Dockerfile` del proyecto y levantará la aplicación web de manera persistente.

---

## 💻 Instalación y Desarrollo Local (Sin Docker)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/MiPymesIA.git
   cd MiPymesIA
   ```
2. **Crear e iniciar el entorno virtual:**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```
3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurar el archivo `.env`:**
   Asegúrate de tener un servidor PostgreSQL local corriendo y configura la URL en tu `.env`.
5. **Iniciar la aplicación:**
   ```bash
   streamlit run main.py
   ```

---

## 📁 Estructura Principal del Proyecto

```text
MiPymesIA/
├── .streamlit/          # Configuración visual de Streamlit
├── assets/              # Archivos multimedia y PDFs estáticos
├── components/          # Componentes visuales reutilizables (cabeceras, carrusel, pie de página)
├── content/             # Documentos estáticos de la plataforma (términos de servicio, precios)
├── dev-notes/           # Documentación interna de desarrollo (excluida de git)
├── views/               # Vistas de la aplicación (página de login, registro)
├── main.py              # Punto de entrada principal de la aplicación
├── auth.py              # Lógica de usuarios, contraseñas y roles
├── db_config.py         # Configuración del driver PostgreSQL
├── db_migrations.py     # Migraciones automáticas de la BD
├── ai_logic.py          # Lógica de integración de Inteligencia Artificial
└── tasks_manager.py     # Generación de tareas del roadmap gamificado
```

---

## 🔧 Solución de Problemas Frecuentes (Troubleshooting)

### Error: "No se detectó la API Key de OpenAI"
* **Causa:** La variable de entorno `OPENAI_API_KEY` o `OPENIA_API_KEY` no se cargó correctamente.
* **Solución:** Verifica que el archivo `.env` exista en la raíz del proyecto. Si estás en EasyPanel, asegúrate de haber guardado las variables de entorno del servicio y de haber reconstruido la aplicación (**Rebuild**).

### Error: "DATABASE_URL environment variable is required"
* **Causa:** La aplicación no encuentra las credenciales de conexión a la base de datos PostgreSQL.
* **Solución:** Asegúrate de proveer la variable `DATABASE_URL` al contenedor o entorno local.

---

## 📜 Licencia

Este proyecto está bajo la Licencia **Apache 2.0**. Ver el archivo [LICENSE](LICENSE) para más detalles.
