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
    
    # ========== HEADER STATS ==========
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔥 Racha Actual", f"{stats['racha_actual']} días")
    
    with col2:
        st.metric("⭐ Puntos Totales", stats['puntos'])
    
    with col3:
        nivel = stats['nivel']
        st.metric("👑 Nivel", nivel)
    
    with col4:
        progreso_semana = 0
        if weekly_progress['tareas_totales'] > 0:
            progreso_semana = int((weekly_progress['tareas_completadas'] / weekly_progress['tareas_totales']) * 100)
        st.metric("📈 Progreso Semana", f"{progreso_semana}%")
    
    st.markdown("---")
    
    # ========== TABS ==========
    tab1, tab2, tab3 = st.tabs(["📋 Tareas de Hoy", "📅 Vista Semanal", "🏆 Logros"])
    
    # ========== TAB 1: TAREAS DE HOY ==========
    with tab1:
        st.subheader(f"📋 Tareas de Hoy - {datetime.now().strftime('%A %d %b')}")
        
        tasks_today = tasks_manager.get_tasks_for_today(username)
        
        if not tasks_today:
            st.info("🎉 ¡No tienes tareas pendientes para hoy! Puedes crear tareas manualmente o generar una nueva estrategia.")
            
            if st.button("➕ Crear Tarea Manual"):
                st.session_state.show_create_task = True
                st.rerun()
        else:
            # Group by priority
            alta = [t for t in tasks_today if t['prioridad'] == 'alta' and not t['completada']]
            media = [t for t in tasks_today if t['prioridad'] == 'media' and not t['completada']]
            baja = [t for t in tasks_today if t['prioridad'] == 'baja' and not t['completada']]
            completadas = [t for t in tasks_today if t['completada']]
            
            # High Priority
            if alta:
                st.markdown("### 🔴 Alta Prioridad")
                for task in alta:
                    render_task_card(task, username)
            
            # Medium Priority
            if media:
                st.markdown("### 🟡 Media Prioridad")
                for task in media:
                    render_task_card(task, username)
            
            # Low Priority
            if baja:
                st.markdown("### 🟢 Baja Prioridad")
                for task in baja:
                    render_task_card(task, username)
            
            # Completed
            if completadas:
                st.markdown("---")
                with st.expander(f"✅ Completadas ({len(completadas)})", expanded=False):
                    for task in completadas:
                        render_task_card(task, username, is_completed=True)
    
    # ========== TAB 2: VISTA SEMANAL ==========
    with tab2:
        st.subheader("📅 Vista Semanal")
        
        # Week calendar
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        
        st.markdown(f"**Semana del {monday.strftime('%d %b')} - {(monday + timedelta(days=6)).strftime('%d %b %Y')}**")
        
        # Progress bar
        if weekly_progress['tareas_totales'] > 0:
            progress_pct = weekly_progress['tareas_completadas'] / weekly_progress['tareas_totales']
            st.progress(progress_pct)
            st.caption(f"{weekly_progress['tareas_completadas']} de {weekly_progress['tareas_totales']} tareas completadas ({int(progress_pct * 100)}%)")
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
        
        if stats['por_categoria']:
            for cat_stat in stats['por_categoria']:
                cat = cat_stat['categoria']
                total = cat_stat['total']
                completadas = cat_stat['completadas']
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


def render_task_card(task, username, is_completed=False, compact=False, day_context=None):
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
            
            with col2:
                style = "text-decoration: line-through; opacity: 0.6;" if task['completada'] else ""
                st.markdown(f"<span style='{style}'>**{priority_colors.get(task['prioridad'], '')} {cat_emoji} {task['titulo']}**</span>", unsafe_allow_html=True)
                
                if task['descripcion'] and not task['completada']:
                    st.caption(task['descripcion'])
                
                if task['completada']:
                    st.caption(f"✅ Completada - +{task['puntos']} puntos")
            
            with col3:
                if not task['completada']:
                    if st.button("🗑️", key=f"delete_{task['id']}", help="Eliminar tarea"):
                        tasks_manager.delete_task(username, task['id'])
                        st.rerun()
        
        st.markdown("")


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
