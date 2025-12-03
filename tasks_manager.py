"""
Tasks Manager - Handles task generation, CRUD operations, and progress tracking
"""

import sqlite3
import json
from datetime import datetime, timedelta
from openai import OpenAI
import os

DB_NAME = "users.db"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==================== TASK GENERATION ====================

def generate_tasks_from_strategy(username, estrategia_dict, business_info):
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
        
        # POST-PROCESSING: Enforce balanced distribution across 7 days
        # Separate tasks by frequency
        weekly_tasks = []  # Tasks with specific day assignments
        unique_tasks = []  # Tasks without day assignment
        
        for task in tasks:
            if task.get('frecuencia') == 'semanal' and task.get('dia_semana') is not None:
                weekly_tasks.append(task)
            elif task.get('frecuencia') == 'unica':
                unique_tasks.append(task)
            # Skip 'diaria' tasks as they appear every day
        
        # Initialize day buckets (0=Monday, 6=Sunday)
        days_tasks = {i: [] for i in range(7)}
        
        # First, place weekly tasks in their assigned days
        for task in weekly_tasks:
            day = task['dia_semana']
            days_tasks[day].append(task)
        
        # Now distribute unique tasks evenly across days
        # Sort days by current task count (ascending)
        for task in unique_tasks:
            # Find day with fewest tasks
            min_day = min(days_tasks.keys(), key=lambda d: len(days_tasks[d]))
            # Assign task to that day as 'semanal'
            task['frecuencia'] = 'semanal'
            task['dia_semana'] = min_day
            days_tasks[min_day].append(task)
        
        # Final redistribution: if any day has more than 5 tasks, move excess
        max_iterations = 10  # Prevent infinite loop
        iteration = 0
        while iteration < max_iterations:
            needs_redistribution = False
            
            for day in range(7):
                if len(days_tasks[day]) > 5:
                    needs_redistribution = True
                    # Move excess tasks to days with fewer tasks
                    while len(days_tasks[day]) > 5:
                        # Find day with fewest tasks (excluding current day)
                        other_days = [d for d in range(7) if d != day and len(days_tasks[d]) < 5]
                        if not other_days:
                            # All other days are at capacity, stop
                            break
                        
                        min_day = min(other_days, key=lambda d: len(days_tasks[d]))
                        # Move last task from current day to min_day
                        task_to_move = days_tasks[day].pop()
                        task_to_move['dia_semana'] = min_day
                        days_tasks[min_day].append(task_to_move)
            
            if not needs_redistribution:
                break
            iteration += 1
        
        # Flatten back to list
        redistributed_tasks = []
        for day_tasks in days_tasks.values():
            redistributed_tasks.extend(day_tasks)
        
        # Add back daily tasks (they weren't in the redistribution)
        for task in tasks:
            if task.get('frecuencia') == 'diaria':
                redistributed_tasks.append(task)
        
        # Save tasks to database
        saved_count = 0
        for task in redistributed_tasks:
            success = create_task(
                username=username,
                titulo=task['titulo'],
                descripcion=task.get('descripcion', ''),
                categoria=task.get('categoria', 'general'),
                prioridad=task.get('prioridad', 'media'),
                frecuencia=task.get('frecuencia', 'unica'),
                dia_semana=task.get('dia_semana'),
                seccion_origen=task.get('seccion_origen', '')
            )
            if success:
                saved_count += 1
        
        return saved_count, redistributed_tasks
        
    except Exception as e:
        print(f"Error generating tasks: {e}")
        return 0, []


# ==================== TASK CRUD ====================

def create_task(username, titulo, descripcion="", categoria="general", prioridad="media", 
                frecuencia="unica", dia_semana=None, seccion_origen=""):
    """Create a new task."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    # Calculate points based on priority
    puntos = {"alta": 10, "media": 5, "baja": 3}.get(prioridad, 5)
    
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
            WHERE user_id = ? AND titulo LIKE ? AND dia_semana = ?
        """, (username, f"{titulo}%", dia_semana))
        count = c.fetchone()[0]
        
        # Add weeks to target date
        target_date = target_date + timedelta(weeks=count)
        
        # Format date in Spanish: "3 Dic 2025"
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", 
                 "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        fecha_str = f"{target_date.day} {meses[target_date.month - 1]} {target_date.year}"
        
        # Append date identifier to title to make it unique
        titulo = f"{titulo} - {fecha_str}"
    
    try:
        c.execute("""
            INSERT INTO tareas_diarias 
            (user_id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, 
             fecha_creacion, seccion_origen, puntos)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana,
              now, seccion_origen, puntos))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating task: {e}")
        conn.close()
        return False


def get_tasks_for_today(username):
    """Get all tasks for today (unique + recurring for this day)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    today_weekday = datetime.now().weekday()  # 0=Monday, 6=Sunday
    
    c.execute("""
        SELECT id, titulo, descripcion, categoria, prioridad, completada, puntos, seccion_origen
        FROM tareas_diarias
        WHERE user_id = ?
        AND (
            (frecuencia = 'unica' AND completada = 0)
            OR (frecuencia = 'diaria')
            OR (frecuencia = 'semanal' AND dia_semana = ?)
        )
        ORDER BY 
            CASE prioridad 
                WHEN 'alta' THEN 1
                WHEN 'media' THEN 2
                WHEN 'baja' THEN 3
            END,
            fecha_creacion ASC
    """, (username, today_weekday))
    
    rows = c.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        tasks.append({
            'id': row[0],
            'titulo': row[1],
            'descripcion': row[2],
            'categoria': row[3],
            'prioridad': row[4],
            'completada': bool(row[5]),
            'puntos': row[6],
            'seccion_origen': row[7]
        })
    
    return tasks


def get_tasks_for_week(username):
    """Get all tasks for the current week."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, titulo, descripcion, categoria, prioridad, frecuencia, dia_semana, 
               completada, puntos, fecha_creacion
        FROM tareas_diarias
        WHERE user_id = ?
        ORDER BY 
            CASE prioridad 
                WHEN 'alta' THEN 1
                WHEN 'media' THEN 2
                WHEN 'baja' THEN 3
            END,
            dia_semana ASC NULLS FIRST
    """, (username,))
    
    rows = c.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
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
            'fecha_creacion': row[9]
        })
    
    return tasks


def complete_task(username, task_id):
    """Mark a task as completed and award points."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    # Get task points
    c.execute("SELECT puntos FROM tareas_diarias WHERE id = ? AND user_id = ?", (task_id, username))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False
    
    puntos = result[0]
    
    # Mark task as completed
    c.execute("""
        UPDATE tareas_diarias
        SET completada = 1, fecha_completada = ?
        WHERE id = ? AND user_id = ?
    """, (now, task_id, username))
    
    # Award points to user
    c.execute("""
        UPDATE users
        SET puntos_totales = puntos_totales + ?
        WHERE username = ?
    """, (puntos, username))
    
    conn.commit()
    conn.close()
    
    # Update streak and check achievements
    update_streak(username)
    check_achievements(username)
    
    return True


def uncomplete_task(username, task_id):
    """Unmark a task as completed."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get task points
    c.execute("SELECT puntos FROM tareas_diarias WHERE id = ? AND user_id = ?", (task_id, username))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False
    
    puntos = result[0]
    
    # Unmark task
    c.execute("""
        UPDATE tareas_diarias
        SET completada = 0, fecha_completada = NULL
        WHERE id = ? AND user_id = ?
    """, (task_id, username))
    
    # Remove points from user
    c.execute("""
        UPDATE users
        SET puntos_totales = MAX(0, puntos_totales - ?)
        WHERE username = ?
    """, (puntos, username))
    
    conn.commit()
    conn.close()
    
    return True


def delete_task(username, task_id):
    """Delete a task."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("DELETE FROM tareas_diarias WHERE id = ? AND user_id = ?", (task_id, username))
    
    conn.commit()
    conn.close()
    return True


# ==================== PROGRESS TRACKING ====================

def get_weekly_progress(username):
    """Get progress for current week."""
    # Get Monday of current week
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    semana_inicio = monday.isoformat()
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get or create weekly progress
    c.execute("""
        SELECT tareas_completadas, tareas_totales, racha_dias, puntos_ganados
        FROM progreso_semanal
        WHERE user_id = ? AND semana_inicio = ?
    """, (username, semana_inicio))
    
    result = c.fetchone()
    
    if not result:
        # Create new week entry
        c.execute("""
            INSERT INTO progreso_semanal (user_id, semana_inicio)
            VALUES (?, ?)
        """, (username, semana_inicio))
        conn.commit()
        result = (0, 0, 0, 0)
    
    # Count actual tasks for this week
    c.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN completada = 1 THEN 1 ELSE 0 END) as completadas
        FROM tareas_diarias
        WHERE user_id = ?
    """, (username,))
    
    counts = c.fetchone()
    conn.close()
    
    return {
        'semana_inicio': semana_inicio,
        'tareas_completadas': counts[1] or 0,
        'tareas_totales': counts[0] or 0,
        'racha_dias': result[2],
        'puntos_ganados': result[3]
    }


def update_streak(username):
    """Update user's streak based on task completion."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    today = datetime.now().date().isoformat()
    
    # Get user's last active day and current streak
    c.execute("""
        SELECT ultimo_dia_activo, racha_actual, racha_maxima
        FROM users
        WHERE username = ?
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
        WHERE user_id = ? AND completada = 1 AND DATE(fecha_completada) = DATE(?)
    """, (username, today))
    
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
            SET ultimo_dia_activo = ?,
                racha_actual = ?,
                racha_maxima = ?
            WHERE username = ?
        """, (today, racha_actual, racha_maxima, username))
        
        conn.commit()
    
    conn.close()


def check_achievements(username):
    """Check and award achievements based on user progress."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get user stats
    c.execute("""
        SELECT puntos_totales, racha_actual, racha_maxima
        FROM users
        WHERE username = ?
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
        WHERE user_id = ? AND completada = 1
    """, (username,))
    
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
                VALUES (?, ?, ?, ?)
            """, (username, logro_id, logro_nombre, now))
        except sqlite3.IntegrityError:
            # Achievement already awarded
            pass
    
    conn.commit()
    conn.close()


def get_user_achievements(username):
    """Get all achievements earned by user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""
        SELECT logro_id, logro_nombre, fecha_obtenido
        FROM logros_usuario
        WHERE user_id = ?
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


def get_user_stats(username):
    """Get comprehensive user statistics."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get user gamification data
    c.execute("""
        SELECT puntos_totales, nivel, racha_actual, racha_maxima
        FROM users
        WHERE username = ?
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
    
    # Get task stats
    c.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN completada = 1 THEN 1 ELSE 0 END) as completadas,
            SUM(CASE WHEN completada = 0 THEN 1 ELSE 0 END) as pendientes
        FROM tareas_diarias
        WHERE user_id = ?
    """, (username,))
    
    task_stats = c.fetchone()
    
    # Get category breakdown
    c.execute("""
        SELECT categoria, 
               COUNT(*) as total,
               SUM(CASE WHEN completada = 1 THEN 1 ELSE 0 END) as completadas
        FROM tareas_diarias
        WHERE user_id = ?
        GROUP BY categoria
    """, (username,))
    
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
