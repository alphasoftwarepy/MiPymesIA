"""
Tracking Panel - Visual UI for task management and progress tracking
"""

import streamlit as st
import tasks_manager
from datetime import datetime, timedelta

def tracking_panel_page():
    """Main tracking panel page with tasks and progress visualization."""
    
    st.title("📊 Mi Progreso")
    st.caption("Gestiona tus tareas y visualiza tu progreso semanal")
    
    user = st.session_state.user
    username = user['username']
    
    # Get user stats
    stats = tasks_manager.get_user_stats(username)
    weekly_progress = tasks_manager.get_weekly_progress(username)
    
    # Provide default values if stats are None
    if stats is None:
        stats = {
            'racha_actual': 0,
            'puntos': 0,
            'nivel': 1,
            'por_categoria': []
        }
    
    if weekly_progress is None:
        weekly_progress = {
            'tareas_completadas': 0,
            'tareas_totales': 0,
            'racha_dias': 0,
            'puntos_ganados': 0
        }
    
    # ========== HEADER STATS ==========
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔥 Racha Actual", f"{stats.get('racha_actual', 0)} días")
    
    with col2:
        st.metric("⭐ Puntos Totales", stats.get('puntos', 0))
    
    with col3:
        nivel = stats.get('nivel', 1)
        st.metric("👑 Nivel", nivel)
    
    with col4:
        progreso_semana = 0
        if weekly_progress.get('tareas_totales', 0) > 0:
            progreso_semana = int((weekly_progress['tareas_completadas'] / weekly_progress['tareas_totales']) * 100)
        st.metric("📈 Progreso Semana", f"{progreso_semana}%")
    
    st.markdown("---")
    
    # ========== TABS ==========
    tab1, tab2, tab3 = st.tabs(["📋 Tareas de Hoy", "📅 Vista Semanal", "🏆 Logros"])
    
    
    # ========== TAB 1: TAREAS ==========
    with tab1:
        st.subheader("📋 Tareas")
        
        # Get all tasks for the week
        all_tasks = tasks_manager.get_tasks_for_week(username)
        
        if not all_tasks:
            st.info("🎉 ¡No tienes tareas pendientes! Puedes crear tareas manualmente o generar una nueva estrategia.")
            
            if st.button("➕ Crear Tarea Manual"):
                st.session_state.show_create_task = True
                st.rerun()
        else:
            # Separate pending and completed
            pending_tasks = [t for t in all_tasks if not t['completada']]
            completed_tasks = [t for t in all_tasks if t['completada']]
            
            # Group pending tasks by date
            from collections import defaultdict
            tasks_by_date = defaultdict(list)
            
            today = datetime.now().date()
            
            for task in pending_tasks:
                # Determine task date
                if task['frecuencia'] == 'diaria':
                    task_date = today
                elif task['frecuencia'] == 'semanal' and task['dia_semana'] is not None:
                    # Calculate next occurrence
                    days_ahead = task['dia_semana'] - today.weekday()
                    if days_ahead < 0:
                        days_ahead += 7
                    task_date = today + timedelta(days=days_ahead)
                else:  # unica
                    task_date = today
                
                tasks_by_date[task_date].append(task)
            
            # Sort dates
            sorted_dates = sorted(tasks_by_date.keys())
            
            # Display tasks grouped by date
            for task_date in sorted_dates:
                # Format date label
                days_diff = (task_date - today).days
                if days_diff == 0:
                    date_label = f"📍 Hoy, {task_date.strftime('%d %B')}"
                elif days_diff == 1:
                    date_label = f"📅 Mañana, {task_date.strftime('%d %B')}"
                else:
                    weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                    weekday = weekday_names[task_date.weekday()]
                    date_label = f"📅 {weekday}, {task_date.strftime('%d %B')}"
                
                st.markdown(f"### {date_label}")
                
                # Sort by priority within date
                day_tasks = sorted(tasks_by_date[task_date], 
                                 key=lambda x: {'alta': 0, 'media': 1, 'baja': 2}.get(x['prioridad'], 3))
                
                for task in day_tasks:
                    render_task_card(task, username, show_date=False)
            
            # Completed tasks section
            if completed_tasks:
                st.markdown("---")
                st.markdown("### ✅ Completadas")
                
                # Sort by completion date (most recent first)
                completed_sorted = sorted(completed_tasks, 
                                        key=lambda x: x.get('fecha_completada', ''), 
                                        reverse=True)
                
                for task in completed_sorted[:10]:  # Show last 10 completed
                    # Format completion date
                    if task.get('fecha_completada'):
                        try:
                            comp_date = datetime.fromisoformat(task['fecha_completada']).date()
                            days_ago = (today - comp_date).days
                            if days_ago == 0:
                                date_str = "Hoy"
                            elif days_ago == 1:
                                date_str = "Ayer"
                            else:
                                date_str = f"{days_ago} días atrás"
                        except:
                            date_str = ""
                    else:
                        date_str = ""
                    
                    # Render completed task with points
                    render_task_card(task, username, is_completed=True, completion_date=date_str)
    
    # ========== TAB 2: VISTA SEMANAL ==========
    with tab2:
        st.subheader("📅 Vista Semanal")
        
        # Week calendar
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        
        st.markdown(f"**Semana del {monday.strftime('%d %b')} - {(monday + timedelta(days=6)).strftime('%d %b %Y')}**")
        
        # Progress bar
        if weekly_progress.get('tareas_totales', 0) > 0:
            progress_pct = weekly_progress.get('tareas_completadas', 0) / weekly_progress.get('tareas_totales', 1)
            st.progress(progress_pct)
            st.caption(f"{weekly_progress.get('tareas_completadas', 0)} de {weekly_progress.get('tareas_totales', 0)} tareas completadas ({int(progress_pct * 100)}%)")
        else:
            st.info("No hay tareas para esta semana")
        
        st.markdown("---")
        
        # Day-by-day breakdown
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        all_tasks = tasks_manager.get_tasks_for_week(username)
        
        for i, dia in enumerate(dias):
            fecha = monday + timedelta(days=i)
            es_hoy = fecha == today
            
            # Filter tasks for this day
            tasks_dia = [t for t in all_tasks if (
                (t['frecuencia'] == 'diaria') or
                (t['frecuencia'] == 'semanal' and t['dia_semana'] == i) or
                (t['frecuencia'] == 'unica' and not t['completada'])
            )]
            
            if tasks_dia:
                completadas_dia = len([t for t in tasks_dia if t['completada']])
                total_dia = len(tasks_dia)
                
                emoji = "📍" if es_hoy else "📅"
                with st.expander(f"{emoji} **{dia}** {fecha.strftime('%d/%m')} - {completadas_dia}/{total_dia}", expanded=es_hoy):
                    for task in tasks_dia:
                        render_task_card(task, username, compact=True, day_context=i)
    
    # ========== TAB 3: LOGROS ==========
    with tab3:
        st.subheader("🏆 Logros y Estadísticas")
        
        # Achievements
        achievements = tasks_manager.get_user_achievements(username)
        
        if achievements:
            st.markdown("### 🎖️ Logros Desbloqueados")
            cols = st.columns(3)
            for i, logro in enumerate(achievements):
                with cols[i % 3]:
                    st.success(f"{logro['nombre']}")
                    st.caption(f"Obtenido: {datetime.fromisoformat(logro['fecha']).strftime('%d/%m/%Y')}")
        else:
            st.info("🎯 Completa tareas para desbloquear logros")
        
        st.markdown("---")
        
        # Category breakdown
        st.markdown("### 📊 Progreso por Categoría")
        
        if stats.get('por_categoria') and len(stats['por_categoria']) > 0:
            for cat_stat in stats['por_categoria']:
                cat = cat_stat.get('categoria', 'general')
                total = cat_stat.get('total', 0)
                completadas = cat_stat.get('completadas', 0)
                pct = (completadas / total * 100) if total > 0 else 0
                
                # Category emoji
                cat_emoji = {
                    'contenido': '📝',
                    'ads': '📢',
                    'whatsapp': '💬',
                    'metricas': '📊',
                    'setup': '⚙️',
                    'general': '📋'
                }.get(cat, '📌')
                
                st.markdown(f"**{cat_emoji} {cat.title()}**")
                st.progress(pct / 100)
                st.caption(f"{completadas}/{total} tareas ({int(pct)}%)")
                st.markdown("")
        else:
            st.info("No hay estadísticas por categoría aún")


def render_task_card(task, username, is_completed=False, compact=False, day_context=None, show_date=True, completion_date=None):
    """Render a single task card with actions."""
    
    # Priority color
    priority_colors = {
        'alta': '🔴',
        'media': '🟡',
        'baja': '🟢'
    }
    
    # Category emoji
    cat_emoji = {
        'contenido': '📝',
        'ads': '📢',
        'whatsapp': '💬',
        'metricas': '📊',
        'setup': '⚙️',
        'general': '📋'
    }.get(task['categoria'], '📌')
    
    if compact:
        # Compact view for weekly tab - add day_context to make keys unique
        key_suffix = f"_day{day_context}" if day_context is not None else ""
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            checked = st.checkbox("", value=task['completada'], key=f"task_{task['id']}_compact{key_suffix}")
            if checked != task['completada']:
                if checked:
                    tasks_manager.complete_task(username, task['id'])
                else:
                    tasks_manager.uncomplete_task(username, task['id'])
                st.rerun()
        
        with col2:
            style = "text-decoration: line-through; opacity: 0.6;" if task['completada'] else ""
            st.markdown(f"<span style='{style}'>{priority_colors.get(task['prioridad'], '')} {cat_emoji} {task['titulo']}</span>", unsafe_allow_html=True)
    
    else:
        # Full view for today tab
        with st.container():
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            
            with col1:
                if not is_completed:
                    checked = st.checkbox("", value=task['completada'], key=f"task_{task['id']}")
                    if checked != task['completada']:
                        if checked:
                            success = tasks_manager.complete_task(username, task['id'])
                            if success:
                                st.success(f"✅ +{task['puntos']} puntos!")
                                st.rerun()
                        else:
                            tasks_manager.uncomplete_task(username, task['id'])
                            st.rerun()
                else:
                    st.markdown("✅")
            
            with col2:
                style = "text-decoration: line-through; opacity: 0.6;" if task['completada'] else ""
                st.markdown(f"<span style='{style}'>**{priority_colors.get(task['prioridad'], '')} {cat_emoji} {task['titulo']}**</span>", unsafe_allow_html=True)
                
                if task['descripcion'] and not task['completada']:
                    st.caption(task['descripcion'])
                
                if task['completada'] and completion_date:
                    st.caption(f"✅ {completion_date} - +{task['puntos']} puntos")
                elif task['completada']:
                    st.caption(f"✅ Completada - +{task['puntos']} puntos")
            
            with col3:
                if not task['completada']:
                    if st.button("🗑️", key=f"delete_{task['id']}", help="Eliminar tarea"):
                        tasks_manager.delete_task(username, task['id'])
                        st.rerun()
        
        # AI Chat Helper - Only for non-completed tasks
        if not task['completada']:
            # Get task-specific chat history
            chat_history_key = f"task_chat_{task['id']}"
            if chat_history_key not in st.session_state:
                st.session_state[chat_history_key] = []
            
            # Use expander for chat (like sections)
            with st.expander("💬 Asistente IA - Ayuda con esta tarea", expanded=False):
                # Show chat count and clear button
                if len(st.session_state[chat_history_key]) > 0:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.caption(f"📝 {len(st.session_state[chat_history_key]) // 2} mensajes")
                    with col2:
                        if st.button("🗑️ Limpiar", key=f"clear_chat_{task['id']}", help="Reiniciar conversación"):
                            st.session_state[chat_history_key] = []
                            st.rerun()
                
                # Display chat messages with st.chat_message (like sections)
                for msg in st.session_state[chat_history_key]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                
                # Quick suggestions
                st.caption("💡 **Sugerencias rápidas:**")
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    if st.button("📝 Dame un ejemplo", key=f"sugg1_{task['id']}", use_container_width=True):
                        user_msg = "Dame un ejemplo concreto de cómo hacer esta tarea"
                        st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                        # Generate AI response immediately
                        with st.spinner("🤔 Pensando..."):
                            ai_response = get_task_ai_help(task, user_msg, username)
                            st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                        st.rerun()
                
                with col_s2:
                    if st.button("⏰ ¿Cuándo hacerlo?", key=f"sugg2_{task['id']}", use_container_width=True):
                        user_msg = "¿Cuál es el mejor momento para hacer esta tarea?"
                        st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                        with st.spinner("🤔 Pensando..."):
                            ai_response = get_task_ai_help(task, user_msg, username)
                            st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                        st.rerun()
                
                with col_s3:
                    if st.button("🎯 Tips y trucos", key=f"sugg3_{task['id']}", use_container_width=True):
                        user_msg = "Dame tips y mejores prácticas para esta tarea"
                        st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                        with st.spinner("🤔 Pensando..."):
                            ai_response = get_task_ai_help(task, user_msg, username)
                            st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                        st.rerun()
                
                # Chat input (like sections - supports Enter key)
                prompt = st.chat_input("Pregunta sobre esta tarea...", key=f"chat_input_{task['id']}")
                
                if prompt:
                    # Add user message
                    st.session_state[chat_history_key].append({"role": "user", "content": prompt})
                    
                    # Generate AI response
                    with st.spinner("🤔 Pensando..."):
                        ai_response = get_task_ai_help(task, prompt, username)
                        st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                    
                    st.rerun()
        
        st.markdown("")


def get_task_ai_help(task, user_question, username):
    """Get AI assistance for a specific task."""
    from openai import OpenAI
    import os
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Build context
    import auth
    
    # Get user's strategy and brain data
    estrategia = auth.get_estrategia(username)
    brain_data = auth.get_brain_data(username)
    
    # Build rich context
    context = f"""Eres un asistente experto en marketing digital que ayuda a ejecutar tareas específicas.

TAREA ACTUAL:
- Título: {task['titulo']}
- Descripción: {task['descripcion']}
- Categoría: {task['categoria']}
- Prioridad: {task['prioridad']}

CONTEXTO DEL NEGOCIO:
"""
    
    if brain_data and brain_data.get('base'):
        base = brain_data['base']
        context += f"""- Negocio: {base.get('nombre', 'N/A')}
- Rubro: {base.get('rubro', 'N/A')}
- Producto/Servicio: {base.get('producto', 'N/A')}
- Plataformas: {base.get('plataforma', 'N/A')}
"""
    
    if estrategia:
        context += f"\nESTRATEGIA RELACIONADA:\n"
        if task['seccion_origen'] == 'embudo':
            context += f"Embudo de contenido: {estrategia.get('embudo', '')[:500]}...\n"
        elif task['seccion_origen'] == 'ads':
            context += f"Estrategia de Ads: {estrategia.get('ads', '')[:500]}...\n"
        elif task['seccion_origen'] == 'whatsapp':
            context += f"Flujo WhatsApp: {estrategia.get('whatsapp', '')[:500]}...\n"
    
    context += f"""
INSTRUCCIONES:
1. Sé específico y práctico
2. Da ejemplos concretos aplicados a este negocio
3. Si es contenido, sugiere copy, hashtags, CTAs
4. Si es ads, sugiere textos, segmentación, presupuesto
5. Sé breve pero completo (máximo 200 palabras)

PREGUNTA DEL USUARIO: {user_question}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un experto en marketing digital que da consejos prácticos y específicos."},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"⚠️ Error al obtener ayuda: {e}. Por favor intenta de nuevo."


def show_create_task_form(username):
    """Show form to create a manual task."""
    
    st.subheader("➕ Crear Tarea Manual")
    
    with st.form("create_task_form"):
        titulo = st.text_input("Título de la tarea*", placeholder="ej: Publicar post en Instagram")
        descripcion = st.text_area("Descripción (opcional)", placeholder="Detalles adicionales...")
        
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Categoría", ["contenido", "ads", "whatsapp", "metricas", "setup", "general"])
            prioridad = st.selectbox("Prioridad", ["alta", "media", "baja"])
        
        with col2:
            frecuencia = st.selectbox("Frecuencia", ["unica", "diaria", "semanal"])
            dia_semana = None
            if frecuencia == "semanal":
                dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                dia_seleccionado = st.selectbox("Día de la semana", dias)
                dia_semana = dias.index(dia_seleccionado)
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("✅ Crear Tarea", use_container_width=True, type="primary")
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submitted:
            if not titulo:
                st.error("El título es obligatorio")
            else:
                success = tasks_manager.create_task(
                    username=username,
                    titulo=titulo,
                    descripcion=descripcion,
                    categoria=categoria,
                    prioridad=prioridad,
                    frecuencia=frecuencia,
                    dia_semana=dia_semana
                )
                
                if success:
                    st.success("✅ Tarea creada exitosamente")
                    st.session_state.show_create_task = False
                    st.rerun()
                else:
                    st.error("Error al crear la tarea")
        
        if cancel:
            st.session_state.show_create_task = False
            st.rerun()
