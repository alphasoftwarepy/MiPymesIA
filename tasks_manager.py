"""
Tasks Manager - Handles task generation, CRUD operations, and progress tracking
"""

import json
from datetime import datetime, timedelta
from openai import OpenAI
import os
import db_config
import streamlit as st

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==================== TASK GENERATION ====================

def generate_tasks_from_strategy(username, estrategia_dict, business_info, estrategia_id=None):
    # This is effectively Week 1 initialization now
    return generate_week1_tasks(username, estrategia_dict, business_info, estrategia_id)
    
def generate_week1_tasks(username, estrategia_dict, business_info, estrategia_id=None):
    """
    Uses AI to analyze strategy and generate actionable daily/weekly tasks.
    
    Args:
        username: user's username
        estrategia_dict: dict with strategy sections (avatar, embudo, ads, etc.)
        business_info: dict with business context
    
    Returns:
        List of generated tasks
    """
    
    # Build context for AI
    context = f"""
Negocio: {business_info.get('nombre', 'N/A')}
Rubro: {business_info.get('rubro', 'N/A')}
Producto: {business_info.get('producto', 'N/A')}
Plataformas: {business_info.get('plataforma', 'N/A')}
Presupuesto: ${business_info.get('presupuesto', 0)}/mes

ESTRATEGIA GENERADA:

AVATAR DE CLIENTE:
{estrategia_dict.get('avatar', 'No disponible')}

EMBUDO DE CONTENIDO:
{estrategia_dict.get('embudo', 'No disponible')}

ESTRATEGIA DE ADS:
{estrategia_dict.get('ads', 'No disponible')}

FLUJO WHATSAPP:
{estrategia_dict.get('whatsapp', 'No disponible')[:500]}...

OBJECIONES:
{estrategia_dict.get('objeciones', 'No disponible')[:300]}...

ACCIONES DIARIAS:
{estrategia_dict.get('acciones_diarias', 'No disponible')}
"""
    
    prompt = f"""Eres un asistente experto en marketing digital. Analiza esta estrategia y genera tareas CONCRETAS y EJECUTABLES que ayuden a implementarla paso a paso.

{context}

INSTRUCCIONES CRÍTICAS:
1. Genera tareas que formen SECUENCIAS COMPLETAS (ej: "Crear copy para post TOFU" → "Diseñar flyer para post TOFU" → "Publicar post TOFU en Instagram")
2. Cada tarea debe ser MUY ESPECÍFICA y ACCIONABLE (no genéricas como "crear contenido")
3. Incluye tareas de SETUP inicial (configuraciones únicas) - prioridad ALTA
4. **DISTRIBUCIÓN SEMANAL BALANCEADA**:
   - **MÁXIMO 5 TAREAS POR DÍA** (esto es CRÍTICO)
   - Distribuye uniformemente: 3-5 tareas por día
   - NO concentres todas las tareas en un solo día
   - Usa los 7 días de la semana (Lunes=0, Domingo=6)
5. Asigna prioridades de forma BALANCEADA:
   - alta (rojo): Setup crítico, lanzamientos, campañas importantes
   - media (amarillo): Contenido regular, seguimiento, optimización
   - baja (verde): Revisiones, análisis, tareas de mantenimiento

DISTRIBUCIÓN DE PRIORIDADES:
- Máximo 30% tareas alta (rojo)
- Aproximadamente 50% tareas media (amarillo)
- Aproximadamente 20% tareas baja (verde)

DISTRIBUCIÓN POR DÍA (EJEMPLO):
- Lunes (dia_semana: 0): 4 tareas
- Martes (dia_semana: 1): 5 tareas
- Miércoles (dia_semana: 2): 4 tareas
- Jueves (dia_semana: 3): 5 tareas
- Viernes (dia_semana: 4): 4 tareas
- Sábado (dia_semana: 5): 3 tareas
- Domingo (dia_semana: 6): 3 tareas

CATEGORÍAS:
- contenido: Creación de posts, copy, diseño
- ads: Configuración y gestión de campañas
- whatsapp: Mensajes, seguimiento, cierre de ventas
- metricas: Análisis, reportes, optimización
- setup: Configuraciones iniciales (pixel, perfiles, etc.)

FORMATO DE RESPUESTA (JSON):
[
  {{
    "titulo": "Configurar Pixel de Facebook en sitio web",
    "descripcion": "Instalar el código del pixel de Facebook en el header de todas las páginas del sitio para rastrear conversiones",
    "categoria": "setup",
    "prioridad": "alta",
    "frecuencia": "unica",
    "dia_semana": null,
    "seccion_origen": "ads"
  }},
  {{
    "titulo": "Crear copy para post TOFU educativo sobre [tema]",
    "descripcion": "Escribir texto educativo de 150-200 palabras con gancho, valor y CTA suave",
    "categoria": "contenido",
    "prioridad": "media",
    "frecuencia": "semanal",
    "dia_semana": 0,
    "seccion_origen": "embudo"
  }},
  {{
    "titulo": "Diseñar flyer para post TOFU sobre [tema]",
    "descripcion": "Crear diseño visual atractivo en Canva con colores de marca y mensaje claro",
    "categoria": "contenido",
    "prioridad": "media",
    "frecuencia": "semanal",
    "dia_semana": 1,
    "seccion_origen": "embudo"
  }},
  {{
    "titulo": "Publicar post TOFU en Instagram y Facebook",
    "descripcion": "Publicar el contenido creado en ambas plataformas con hashtags relevantes",
    "categoria": "contenido",
    "prioridad": "media",
    "frecuencia": "semanal",
    "dia_semana": 2,
    "seccion_origen": "embudo"
  }}
]

Genera entre 25-35 tareas que cubran toda la estrategia, formando secuencias lógicas y DISTRIBUYENDO MÁXIMO 5 TAREAS POR DÍA. RESPONDE SOLO CON EL JSON, SIN TEXTO ADICIONAL."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en marketing digital que convierte estrategias en tareas accionables."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        tasks_json = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if tasks_json.startswith("```"):
            tasks_json = tasks_json.split("```")[1]
            if tasks_json.startswith("json"):
                tasks_json = tasks_json[4:]
            tasks_json = tasks_json.strip()
        
        tasks = json.loads(tasks_json)
        
        # Calculate offset based on week number (default week 1)
        week_num = 1
        day_offset = (week_num - 1) * 7
        
        return save_distributed_tasks(username, estrategia_id, tasks, day_offset)
        
    except Exception as e:
        print(f"Error generating tasks: {e}")
        return 0, []

def generate_weekly_tasks(username, estrategia_id, week_num, prev_feedback, roadmap_context):
    """Generates tasks for a specific week based on roadmap and feedback."""
    print(f"DEBUG: Generando tareas semana {week_num} para {username}")
    print(f"DEBUG: Roadmap Context: {json.dumps(roadmap_context)[:200]}...") # Log start of roadmap
    
    prompt = f"""Eres un Project Manager de Marketing.
EXPERTO EN GESTIÓN DE TIEMPO Y PRODUCTIVIDAD.

CONTEXTO ESTRATEGIA (Roadmap):
{json.dumps(roadmap_context, indent=2)}

OBJETIVO: Generar el PLAN DE TAREAS para la SEMANA {week_num}.
FOCUS DE LA SEMANA: {next((item['foco'] for item in roadmap_context if item['semana'] == week_num), 'General')}

FEEDBACK SEMANA ANTERIOR:
{prev_feedback}

INSTRUCCIONES:
1. Genera entre 15-20 tareas específicas para lograr el foco de la semana.
2. Si el feedback fue negativo, ajusta la dificultad o estrategia.
3. Distribuye las tareas en 7 días (0=Lunes, 6=Domingo).
4. SÉ MUY ESPECÍFICO (Ej: "Grabar Reel sobre X" en lugar de "Crear contenido").

FORMATO JSON:
[
  {{
    "titulo": "Acción específica",
    "descripcion": "Detalle paso a paso",
    "categoria": "contenido|ads|whatsapp|metricas|setup (SOLO estas opciones, NO email, blog, ni otras)",
    "prioridad": "alta|media|baja",
    "frecuencia": "unica",
    "dia_semana": 0-6
  }}
]
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en productividad."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        tasks_json = response.choices[0].message.content.strip()
        print(f"DEBUG: AI Tasks Response: {tasks_json[:100]}...")
        
        import re
        # Regex to find JSON block (supports json, js, or no tag)
        json_match = re.search(r"```(%s:json|js)%s\s*(\[[\s\S]*%s\])\s*```", tasks_json)
        
        if json_match:
            tasks_json = json_match.group(1)
        elif "[" in tasks_json and "]" in tasks_json:
            # Fallback: try to find the array/list directly if no code blocks
            start = tasks_json.find("[")
            end = tasks_json.rfind("]") + 1
            tasks_json = tasks_json[start:end]
            
        tasks_json = tasks_json.strip()
            
        tasks = json.loads(tasks_json)
        print(f"DEBUG: Parsed {len(tasks)} tasks.")
        
        # Calculate day offset for this week (e.g. Week 2 starts at day 7)
        day_offset = (week_num - 1) * 7
        
        return save_distributed_tasks(username, estrategia_id, tasks, day_offset)

    except Exception as e:
        print(f"Error generating weekly tasks: {e}")
        return 0, []

def save_distributed_tasks(username, estrategia_id, tasks, day_offset=0):
    """Helper to distribute and save tasks with day offset."""
    print(f"DEBUG: Saving {len(tasks)} tasks for user {username}, starting day {day_offset}")
    # ... Same distribution logic as before but adding day_offset ...
    
    # Initialize day buckets (0-6 relative to week)
    days_tasks = {i: [] for i in range(7)}
    
    # Distribute tasks into 0-6 buckets first
    weekly_tasks = [t for t in tasks if t.get('frecuencia') == 'semanal' or t.get('dia_semana') is not None]
    unique_tasks = [t for t in tasks if t not in weekly_tasks and t.get('frecuencia') != 'diaria']
    
    for task in weekly_tasks:
        day = task.get('dia_semana', 0)
        if day is None: day = 0
        days_tasks[day % 7].append(task)
        
    # Distribute unique tasks
    for task in unique_tasks:
        min_day = min(days_tasks.keys(), key=lambda d: len(days_tasks[d]))
        task['dia_semana'] = min_day
        days_tasks[min_day].append(task)
        
    # Redistribute if > 5 per day
    for day in range(7):
        while len(days_tasks[day]) > 5:
            other_days = [d for d in range(7) if d != day and len(days_tasks[d]) < 5]
            if not other_days: break
            min_day = min(other_days, key=lambda d: len(days_tasks[d]))
            task = days_tasks[day].pop()
            task['dia_semana'] = min_day
            days_tasks[min_day].append(task)

    # Save validation
    saved_count = 0
    final_tasks = []
    
    # 1. Add specific day tasks
    for day, day_tasks in days_tasks.items():
        for task in day_tasks:
            task['dia_semana'] = day # Ensure 0-6
            final_tasks.append(task)
            
    # 2. Add daily tasks (create copies for each day 0-6)
    for task in tasks:
        if task.get('frecuencia') == 'diaria':
            for d in range(7):
                t_copy = task.copy()
                t_copy['dia_semana'] = d
                final_tasks.append(t_copy)

    # Save to DB applying Offset
    conn = db_config.get_connection()
    c = conn.cursor()
    
    # Get max current task number for ID consistency
    c.execute("SELECT COUNT(*) FROM tareas_diarias WHERE user_id = %s AND estrategia_id = %s", (username, estrategia_id))
    start_num = c.fetchone()[0]
    
    created_tasks = []
    
    for i, task in enumerate(final_tasks):
        # Apply offset (Week 2 Monday = 0 + 7 = 7)
        relative_day = task['dia_semana']
        absolute_day = relative_day + day_offset
        
        titulo = task['titulo']
        titulo_con_prefijo = f"E{estrategia_id}-{start_num + i + 1} ; {titulo}"
        
        puntos = {"alta": 10, "media": 5, "baja": 3}.get(task.get('prioridad'), 5)
        now = datetime.utcnow().isoformat()
        
        try:
            c.execute("""
                INSERT INTO tareas_diarias 
                (user_id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, 
                 fecha_creacion, seccion_origen, puntos, estrategia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, titulo_con_prefijo, task.get('descripcion', ''), 
                  task.get('categoria', 'general'), task.get('prioridad', 'media'), 
                  task.get('frecuencia', 'unica'), absolute_day,
                  now, task.get('seccion_origen', ''), puntos, estrategia_id))
            saved_count += 1
            created_tasks.append(task)
        except Exception as e:
            print(f"Error saving task: {e}")
            
    conn.commit()
    conn.close()
    
    print(f"DEBUG: Successfully committed {saved_count} tasks to DB.")
    return saved_count, created_tasks

def delete_week_tasks(username, estrategia_id, week_num):
    """Deletes all tasks for a specific week."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    start_day = (week_num - 1) * 7
    end_day = start_day + 6
    
    c.execute("""
        DELETE FROM tareas_diarias 
        WHERE user_id = %s AND estrategia_id = %s AND dia_semana BETWEEN %s AND %s
    """, (username, estrategia_id, start_day, end_day))
    
    conn.commit()
    conn.close()
    return True


# ==================== TASK CRUD ====================

def create_task(username, titulo, descripcion="", categoria="general", prioridad="media", 
                frecuencia="unica", dia_semana=None, seccion_origen="", estrategia_id=None):
    """Create a new task."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    # Calculate points based on priority
    puntos = {"alta": 10, "media": 5, "baja": 3}.get(prioridad, 5)
    
    # ========== AGREGAR PREFIJO DEBUG PARA ESTRATEGIAS ==========
    # Formato: E{id}-{num} ; titulo original
    if estrategia_id:
        # Contar tareas existentes para esta estrategia
        c.execute("""
            SELECT COUNT(*) FROM tareas_diarias 
            WHERE user_id = %s AND estrategia_id = %s
        """, (username, estrategia_id))
        task_count = c.fetchone()[0]
        task_num = task_count + 1
        
        # Agregar prefijo
        titulo_con_prefijo = f"E{estrategia_id}-{task_num} ; {titulo}"
    else:
        titulo_con_prefijo = titulo
    # ============================================================
    
    
    # Calculate actual date for weekly tasks to append to title
    if frecuencia == 'semanal' and dia_semana is not None:
        # Get current date
        today = datetime.now().date()
        current_weekday = today.weekday()
        
        # Calculate days until target weekday
        days_ahead = dia_semana - current_weekday
        if days_ahead < 0:
            days_ahead += 7
        
        # Calculate target date
        target_date = today + timedelta(days=days_ahead)
        
        # Count how many weeks ahead this task is (for recurring tasks)
        c.execute("""
            SELECT COUNT(*) FROM tareas_diarias 
            WHERE user_id = %s AND titulo LIKE %s AND dia_semana = %s
        """, (username, f"{titulo}%", dia_semana))
        count = c.fetchone()[0]
        
        # Add weeks to target date
        target_date = target_date + timedelta(weeks=count)
        
        # Format date in Spanish: "3 Dic 2025"
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        fecha_str = f"{target_date.day} {meses[target_date.month - 1]} {target_date.year}"
        
        # Append date identifier to title to make it unique
        #titulo_con_prefijo = f"{titulo_con_prefijo} - {fecha_str}"
    
    try:
        c.execute("""
            INSERT INTO tareas_diarias 
            (user_id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, 
             fecha_creacion, seccion_origen, puntos, estrategia_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, titulo_con_prefijo, descripcion, categoria, prioridad, frecuencia, dia_semana,
              now, seccion_origen, puntos, estrategia_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating task: {e}")
        conn.close()
        return False

def get_tasks_for_today(username, estrategia_id=None):
    """Get tasks scheduled for today based on assigned date from strategy creation."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    if estrategia_id:
        # Filter by exact date match using calculated assigned date (PostgreSQL)
        query = """
            SELECT id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, completada, puntos, fecha_completada, seccion_origen
            FROM tareas_diarias 
            WHERE user_id = %s AND estrategia_id = %s 
            AND CAST((SELECT created_at FROM estrategias_v2 WHERE id = estrategia_id) AS DATE) + (dia_semana || ' days')::interval = CAST(%s AS DATE)
        """
        params = [username, estrategia_id, datetime.now().strftime('%Y-%m-%d')]
    else:
        # Fallback: original logic by weekday (for backward compatibility)
        today_iso = datetime.now().isoweekday()
        query = """
            SELECT id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, completada, puntos, fecha_completada, seccion_origen
            FROM tareas_diarias 
            WHERE user_id = %s AND dia_semana = %s
        """
        params = [username, today_iso]
    
    c.execute(query, tuple(params))
    
    tasks = []
    for row in c.fetchall():
        tasks.append({
            'id': row[0],
            'titulo': row[1],
            'descripcion': row[2],
            'categoria': row[3],
            'prioridad': row[4],
            'frecuencia': row[5],
            'dia_semana': row[6],
            'completada': bool(row[7]),
            'puntos': row[8],
            'fecha_completada': row[9],
            'seccion_origen': row[10]
        })
    
    conn.close()
    return tasks

@st.cache_data(ttl=60, show_spinner=False)
def get_tasks_for_week(username, estrategia_id=None):
    """Get all tasks for the user, optionally filtered by strategy.
    CACHED for 1 minute to improve performance.
    """
    conn = db_config.get_connection()
    c = conn.cursor()
    
    query = """
        SELECT id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, completada, puntos, fecha_completada, seccion_origen
        FROM tareas_diarias 
        WHERE user_id = %s
    """
    params = [username]
    
    if estrategia_id:
        query += " AND estrategia_id = %s"
        params.append(estrategia_id)
    
    c.execute(query, tuple(params))
    
    tasks = []
    for row in c.fetchall():
        tasks.append({
            'id': row[0],
            'titulo': row[1],
            'descripcion': row[2],
            'categoria': row[3],
            'prioridad': row[4],
            'frecuencia': row[5],
            'dia_semana': row[6],
            'completada': bool(row[7]),
            'puntos': row[8],
            'fecha_completada': row[9],
            'seccion_origen': row[10]
        })
    
    conn.close()
    return tasks


def complete_task(username, task_id):
    """Mark a task as completed and award points."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    # Get task points
    c.execute("SELECT puntos FROM tareas_diarias WHERE id = %s AND user_id = %s", (task_id, username))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False
    
    puntos = result[0]
    
    # Mark task as completed
    c.execute("""
        UPDATE tareas_diarias
        SET completada = %s, fecha_completada = %s
        WHERE id = %s AND user_id = %s
    """, (db_config.true_value(), now, task_id, username))
    
    # Award points to user
    c.execute("""
        UPDATE users
        SET puntos_totales = puntos_totales + %s
        WHERE username = %s
    """, (puntos, username))
    
    conn.commit()
    conn.close()
    
    # Update streak and check achievements
    update_streak(username)
    check_achievements(username)
    
    return True


def uncomplete_task(username, task_id):
    """Unmark a task as completed."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    # Get task points
    c.execute("SELECT puntos FROM tareas_diarias WHERE id = %s AND user_id = %s", (task_id, username))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False
    
    puntos = result[0]
    
    # Unmark task
    c.execute("""
        UPDATE tareas_diarias
        SET completada = %s, fecha_completada = NULL
        WHERE id = %s AND user_id = %s
    """, (db_config.false_value(), task_id, username))
    
    # Remove points from user (use GREATEST for PostgreSQL compatibility)
    c.execute("""
        UPDATE users
        SET puntos_totales = GREATEST(0, puntos_totales - %s)
        WHERE username = %s
    """, (puntos, username))
    
    conn.commit()
    conn.close()
    
    return True


def delete_task(username, task_id):
    """Delete a task."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    c.execute("DELETE FROM tareas_diarias WHERE id = %s AND user_id = %s", (task_id, username))
    
    conn.commit()
    conn.close()
    return True


# ==================== PROGRESS TRACKING ====================

def get_weekly_progress(username, estrategia_id=None):
    """Calculate weekly progress percentage, optionally filtered by strategy."""
    tasks = get_tasks_for_week(username, estrategia_id)
    
    if not tasks:
        return 0, 0, 0
    
    total = len(tasks)
    completed = sum(1 for t in tasks if t['completada'])
    
    percentage = int((completed / total) * 100)
    
    return percentage, completed, total

def update_streak(username):
    """Update user's streak based on task completion."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    today = datetime.now().date().isoformat()
    
    # Get user's last active day and current streak
    c.execute("""
        SELECT ultimo_dia_activo, racha_actual, racha_maxima
        FROM users
        WHERE username = %s
    """, (username,))
    
    result = c.fetchone()
    
    if not result:
        conn.close()
        return
    
    ultimo_dia, racha_actual, racha_maxima = result
    
    # Check if user completed at least one task today
    c.execute("""
        SELECT COUNT(*)
        FROM tareas_diarias
        WHERE user_id = %s AND completada = %s AND DATE(fecha_completada) = DATE(%s)
    """, (username, db_config.true_value(), today))
    
    completed_today = c.fetchone()[0]
    
    if completed_today > 0:
        if ultimo_dia:
            last_date = datetime.fromisoformat(ultimo_dia).date()
            yesterday = datetime.now().date() - timedelta(days=1)
            
            if last_date == yesterday:
                # Continue streak
                racha_actual += 1
            elif last_date < yesterday:
                # Streak broken, restart
                racha_actual = 1
            # If last_date == today, don't increment (already counted)
        else:
            # First day
            racha_actual = 1
        
        # Update max streak
        racha_maxima = max(racha_maxima or 0, racha_actual)
        
        # Update user
        c.execute("""
            UPDATE users
            SET ultimo_dia_activo = %s,
                racha_actual = %s,
                racha_maxima = %s
            WHERE username = %s
        """, (today, racha_actual, racha_maxima, username))
        
        conn.commit()
    
    conn.close()


def check_achievements(username):
    """Check and award achievements based on user progress."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    # Get user stats
    c.execute("""
        SELECT puntos_totales, racha_actual, racha_maxima
        FROM users
        WHERE username = %s
    """, (username,))
    
    result = c.fetchone()
    if not result:
        conn.close()
        return
    
    puntos, racha_actual, racha_maxima = result
    
    # Count completed tasks
    c.execute("""
        SELECT COUNT(*)
        FROM tareas_diarias
        WHERE user_id = %s AND completada = %s
    """, (username, db_config.true_value()))
    
    total_completadas = c.fetchone()[0]
    
    # Define achievements
    achievements = []
    
    if total_completadas >= 1:
        achievements.append(("primer_dia", "🎯 Primer Día Completo"))
    if racha_actual >= 7:
        achievements.append(("racha_7", "🔥 Racha de 7 Días"))
    if racha_maxima >= 30:
        achievements.append(("racha_30", "💎 Racha de 30 Días"))
    if total_completadas >= 100:
        achievements.append(("100_tareas", "⭐ 100 Tareas Completadas"))
    if puntos >= 1000:
        achievements.append(("1000_puntos", "👑 1000 Puntos"))
    
    # Award new achievements
    now = datetime.utcnow().isoformat()
    for logro_id, logro_nombre in achievements:
        try:
            c.execute("""
                INSERT INTO logros_usuario (user_id, logro_id, logro_nombre, fecha_obtenido)
                VALUES (%s, %s, %s, %s)
            """, (username, logro_id, logro_nombre, now))
        except sqlite3.IntegrityError:
            # Achievement already awarded
            pass
    
    conn.commit()
    conn.close()


def get_user_achievements(username):
    """Get all achievements earned by user."""
    conn = db_config.get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT logro_id, logro_nombre, fecha_obtenido
        FROM logros_usuario
        WHERE user_id = %s
        ORDER BY fecha_obtenido DESC
    """, (username,))
    
    rows = c.fetchall()
    conn.close()
    
    achievements = []
    for row in rows:
        achievements.append({
            'id': row[0],
            'nombre': row[1],
            'fecha': row[2]
        })
    
    return achievements


@st.cache_data(ttl=120, show_spinner=False)
def get_user_stats(username, estrategia_id=None):
    """Get comprehensive user statistics. Optionally filter by estrategia_id.
    CACHED for 2 minutes to improve performance.
    """
    conn = db_config.get_connection()
    c = conn.cursor()
    
    # Get user gamification data (global, not filtered by strategy)
    c.execute("""
        SELECT puntos_totales, nivel, racha_actual, racha_maxima
        FROM users
        WHERE username = %s
    """, (username,))
    
    user_data = c.fetchone()
    
    # If user doesn't have gamification data, return defaults
    if not user_data:
        conn.close()
        return {
            'puntos': 0,
            'nivel': 1,
            'racha_actual': 0,
            'racha_maxima': 0,
            'total_tareas': 0,
            'completadas': 0,
            'pendientes': 0,
            'por_categoria': []
        }
    
    # Base query for stats
    base_where = "WHERE user_id = %s"
    params = [username]
    
    if estrategia_id:
        base_where += " AND estrategia_id = %s"
        params.append(estrategia_id)
    
    # Get task stats
    c.execute(f"""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN completada = %s THEN 1 ELSE 0 END) as completadas,
            SUM(CASE WHEN completada = %s THEN 1 ELSE 0 END) as pendientes
        FROM tareas_diarias
        {base_where}
    """, tuple([db_config.true_value(), db_config.false_value()] + params))
    
    task_stats = c.fetchone()
    
    # Get category breakdown
    c.execute(f"""
        SELECT categoria, 
               COUNT(*) as total,
               SUM(CASE WHEN completada = %s THEN 1 ELSE 0 END) as completadas
        FROM tareas_diarias
        {base_where}
        GROUP BY categoria
    """, tuple([db_config.true_value()] + params))
    
    category_stats = c.fetchall()
    
    conn.close()
    
    return {
        'puntos': user_data[0] or 0,
        'nivel': user_data[1] or 1,
        'racha_actual': user_data[2] or 0,
        'racha_maxima': user_data[3] or 0,
        'total_tareas': task_stats[0] or 0,
        'completadas': task_stats[1] or 0,
        'pendientes': task_stats[2] or 0,
        'por_categoria': [
            {'categoria': cat[0], 'total': cat[1], 'completadas': cat[2]}
            for cat in category_stats
        ]
    }

def reset_user_progress(username):
    """
    Resets all progress data for a user: tasks, achievements, points, levels, streaks.
    Does NOT affect plan limits or strategy creation limits.
    """
    print(f"⚠️ RESETTING PROGRESS FOR USER: {username}")
    conn = db_config.get_connection()
    c = conn.cursor()
    
    try:
        # 1. Delete all tasks
        c.execute("DELETE FROM tareas_diarias WHERE user_id = %s", (username,))
        deleted_tasks = c.rowcount
        
        # 2. Delete all achievements
        c.execute("DELETE FROM logros_usuario WHERE user_id = %s", (username,))
        deleted_achievements = c.rowcount
        
        # 3. Delete weekly progress if exists
        try:
            c.execute("DELETE FROM progreso_semanal WHERE user_id = %s", (username,))
            deleted_progress = c.rowcount
        except sqlite3.OperationalError:
            # Table might not exist yet
            deleted_progress = 0
            
        # 4. Reset User Stats
        c.execute("""
            UPDATE users 
            SET puntos_totales = 0,
                nivel = 1,
                racha_actual = 0,
                racha_maxima = 0,
                ultimo_dia_activo = NULL
            WHERE username = %s
        """, (username,))
        
        # 5. Reset all strategies to Week 1
        c.execute("UPDATE estrategias_v2 SET semana_actual = 1 WHERE user_id = %s", (username,))
        updated_strategies = c.rowcount
        
        conn.commit()
        print(f"✅ Reset complete. Deleted: {deleted_tasks} tasks, {deleted_achievements} achievements. Updated {updated_strategies} strategies.")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting progress: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
