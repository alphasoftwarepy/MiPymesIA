# SG MiPymes IA

Sistema generador de estrategias de marketing digital para pequeñas empresas.

## Instalación

1.  Crear entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configurar variables de entorno:
    - Renombrar `.env` (si es necesario) y agregar tu `OPENAI_API_KEY`.

## Ejecución

1.  Inicializar la base de datos (solo la primera vez):
    ```bash
    python auth.py
    ```
    Esto creará el usuario admin por defecto: `admin` / `admin123`.

2.  Correr la aplicación:
    ```bash
    streamlit run main.py
    ```

## Uso

1.  **Login**: Ingresa con `admin` / `admin123`.
2.  **Admin Panel**: Crea nuevos usuarios y actívalos.
3.  **Generador**:
    - Completa el formulario de diagnóstico.
    - Espera a que la IA genere la estrategia.
    - Descarga el PDF o chatea con el asistente para refinar la estrategia.

## Estructura

- `main.py`: Aplicación principal (Streamlit).
- `auth.py`: Gestión de usuarios y base de datos.
- `ai_logic.py`: Lógica de IA (LangChain + OpenAI).
- `pdf_gen.py`: Generación de reportes PDF.
