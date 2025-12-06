"""
Tracking Panel - Visual UI for task management and progress tracking
"""

import streamlit as st
import tasks_manager
from datetime import datetime, timedelta

def tracking_panel_page():
    """Main tracking panel page with tabs for multiple strategies"""
    st.title("📊 Mi Progreso")
    
    user = st.session_state.user
    username = user['username']
    
    # Obtener todas las estrategias del usuario
    import auth
    estrategias = auth.get_all_estrategias(username)
    
    if not estrategias:
        st.info("No tienes estrategias creadas aún. Ve a 'Generador' para crear una.")
        return
    
    # Determinar qué estrategia mostrar por defecto
    estrategia_activa_id = st.session_state.get('estrategia_activa_id')
    default_index = 0
    
    # Si hay estrategia activa guardada, buscar su índice
    if estrategia_activa_id:
        for idx, e in enumerate(estrategias):
            if e['id'] == estrategia_activa_id:
                default_index = idx
                break
    
    # Si NO hay estrategia activa guardada, auto-seleccionar la primera
    if not estrategia_activa_id or estrategia_activa_id not in [e['id'] for e in estrategias]:
        estrategia_activa_id = estrategias[0]['id']
        st.session_state['estrategia_activa_id'] = estrategia_activa_id

    # Si hay múltiples estrategias, mostrar selector de cards
    if len(estrategias) > 1:
        st.markdown("### 🎯 Selecciona una Estrategia")
        
        # Calcular cuántas columnas según cantidad de estrategias
        num_cols = min(len(estrategias), 4)  # Máximo 4 columnas
        cols = st.columns(num_cols)
        
        # Crear un card por cada estrategia
        for idx, estrategia in enumerate(estrategias):
            with cols[idx % num_cols]:
                # Verificar si esta estrategia está activa
                is_active = (estrategia['id'] == estrategia_activa_id)
                
                # Estilo del card (diferente si está activo)
                if is_active:
                    border_color = "#3498db"
                    bg_color = "#e8f4f8"
                    button_type = "primary"
                else:
                    border_color = "#ddd"
                    bg_color = "#f8f9fa"
                    button_type = "secondary"
                
                # Card visual
                st.markdown(f"""
                <div style='
                    background: {bg_color};
                    border: 3px solid {border_color};
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 10px;
                    text-align: center;
                    min-height: 100px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                '>
                    <h4 style='margin: 0; color: #2c3e50;'>🎯 {estrategia['producto']}</h4>
                    <p style='margin: 5px 0 0 0; color: #7f8c8d; font-size: 0.9em;'>{estrategia.get('nombre', 'Estrategia')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón para seleccionar esta estrategia
                if st.button(
                    "✅ Activa" if is_active else "Ver Tareas",
                    key=f"select_estrategia_{estrategia['id']}",
                    use_container_width=True,
                    type=button_type,
                    disabled=is_active  # Deshabilitar si ya está activa
                ):
                    # Guardar como estrategia activa y recargar
                    st.session_state['estrategia_activa_id'] = estrategia['id']
                    st.rerun()
        
        st.markdown("---")
        
        # Mostrar tareas de la estrategia activa
        estrategia_activa = next((e for e in estrategias if e['id'] == estrategia_activa_id), estrategias[0])
        show_tasks_for_strategy(username, estrategia_activa['id'], estrategia_activa['producto'])
    else:
        # Una sola estrategia, sin selector
        show_tasks_for_strategy(username, estrategias[0]['id'], estrategias[0]['producto'])

def show_tasks_for_strategy(username, estrategia_id, estrategia_nombre):
    """
    Muestra las tareas de una estrategia específica.
    Si estrategia_id es None, muestra TODAS las tareas.
    """
    
    st.caption("Gestiona tus tareas y visualiza tu progreso semanal")
    
    # Check if we should show create task form
    if st.session_state.get('show_create_task', False):
        show_create_task_form(username, estrategia_id)
        return
    
    # Get user stats
    stats = tasks_manager.get_user_stats(username, estrategia_id)
    
    # Provide default values if stats are None
    if stats is None:
        stats = {
            'racha_actual': 0,
            'puntos': 0,
            'nivel': 1,
            'por_categoria': []
        }
    
    # Get weekly progress
    weekly_progress = tasks_manager.get_weekly_progress(username, estrategia_id)
    
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
    
    st.markdown("---")
    
    with col4:
        # Obtener progreso solo para mostrar porcentaje
        prog_pct, _, _ = tasks_manager.get_weekly_progress(username, estrategia_id)
        st.metric("📈 Progreso Semana", f"{prog_pct}%")

    # ========== TABS ==========
    tab1, tab2, tab3 = st.tabs(["📋 Tareas de Hoy", "📅 Vista Semanal", "🏆 Logros"])
    
    
    # ========== TAB 1: TAREAS ==========
    with tab1:
        if st.button("➕ Crear Tarea", key=f"btn_create_task_{estrategia_id or 'todas'}"):
            st.session_state.show_create_task = True
            st.rerun()
        
        # Get all tasks for the week (filtered by estrategia_id)
        all_tasks = tasks_manager.get_tasks_for_week(username, estrategia_id)
        
        if not all_tasks:
            st.info("🎉 ¡No tienes tareas pendientes! Puedes crear tareas manualmente o generar una nueva estrategia.")
            
            if st.button("➕ Crear Tarea Manual", key=f"btn_create_task_manual_{estrategia_id or 'todas'}"):
                st.session_state.show_create_task = True
                st.rerun()
        else:
            # Separate pending and completed
            pending_tasks = [t for t in all_tasks if not t['completada']]
            completed_tasks = [t for t in all_tasks if t['completada']]
            
            # Filter ONLY today's tasks (not future days)
            today = datetime.now().date()
            today_weekday = today.weekday()
            
            today_tasks = []
            for task in pending_tasks:
                # Include task if it's for today
                if task['frecuencia'] == 'diaria':
                    today_tasks.append(task)
                elif task['frecuencia'] == 'semanal' and task['dia_semana'] == today_weekday:
                    today_tasks.append(task)
                elif task['frecuencia'] == 'unica':
                    today_tasks.append(task)
            
            # Display today's tasks
            if today_tasks:
                st.markdown(f"### 📍 Tareas de Hoy - {today.strftime('%d %B %Y')}")
                
                # Sort by priority
                today_tasks_sorted = sorted(today_tasks, 
                                          key=lambda x: {'alta': 0, 'media': 1, 'baja': 2}.get(x['prioridad'], 3))
                
                for task in today_tasks_sorted:
                    render_task_card(task, username, show_date=False, estrategia_id=estrategia_id)
            
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

                # Week calendar - start from today
        today = datetime.now().date()
        
        # Calculate end of week (6 days from today)
        end_of_week = today + timedelta(days=6)
        
        st.markdown(f"**Semana del {today.strftime('%d %b')} - {end_of_week.strftime('%d %b %Y')}**")
        
        # Progress bar
        percentage, completed, total = tasks_manager.get_weekly_progress(username, estrategia_id)
        
        if total > 0:
            st.progress(percentage / 100)
            st.caption(f"{completed} de {total} tareas completadas ({percentage}%)")
        else:
            st.info("No hay tareas para esta semana")
        
        st.markdown("---")
        
        # Day-by-day breakdown - starting from today
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        all_tasks = tasks_manager.get_tasks_for_week(username, estrategia_id)
        
        # Track which unique tasks we've already shown
        shown_unique_tasks = set()
        
        # Show next 7 days starting from today
        for day_offset in range(7):
            fecha = today + timedelta(days=day_offset)
            dia_semana_num = fecha.weekday()  # 0=Monday, 6=Sunday
            dia_nombre = dias[dia_semana_num]
            es_hoy = day_offset == 0
            
            # Filter tasks for this specific day
            tasks_dia = []
            for t in all_tasks:
                # Daily tasks appear every day
                if t['frecuencia'] == 'diaria':
                    tasks_dia.append(t)
                # Weekly tasks appear on their assigned day
                elif t['frecuencia'] == 'semanal' and t['dia_semana'] == dia_semana_num:
                    tasks_dia.append(t)
                # Unique tasks appear only once (on first day if not completed, or on completion day)
                elif t['frecuencia'] == 'unica':
                    task_id = t['id']
                    if task_id not in shown_unique_tasks:
                        # Show on first day if not completed
                        if not t['completada']:
                            tasks_dia.append(t)
                            shown_unique_tasks.add(task_id)
                        # Or show on completion day if completed
                        elif t.get('fecha_completada'):
                            try:
                                comp_date = datetime.fromisoformat(t['fecha_completada']).date()
                                if comp_date == fecha:
                                    tasks_dia.append(t)
                                    shown_unique_tasks.add(task_id)
                            except:
                                pass
            
            # Show day section if there are tasks OR if it's today
            if tasks_dia or es_hoy:
                completadas_dia = len([t for t in tasks_dia if t['completada']])
                total_dia = len(tasks_dia)
                
                emoji = "📍" if es_hoy else "📅"
                
                # Show expander with task count
                if total_dia > 0:
                    with st.expander(f"{emoji} **{dia_nombre}** {fecha.strftime('%d/%m')} - {completadas_dia}/{total_dia}", expanded=es_hoy):
                        for task in tasks_dia:
                            render_task_card(task, username, compact=True, day_context=day_offset, estrategia_id=estrategia_id)
    
    # ========== TAB 3: LOGROS ==========
    with tab3:
        
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

def render_task_card(task, username, is_completed=False, compact=False, day_context=None, show_date=True, completion_date=None, estrategia_id=None):
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
            task_text = f"{priority_colors.get(task['prioridad'], '')} {cat_emoji} {task['titulo']}"
            if task['completada']:
                task_text += f" (+{task['puntos']} pts)"
            st.markdown(f"<span style='{style}'>{task_text}</span>", unsafe_allow_html=True)
    
    else:
        # Full view for today tab
        with st.container():
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            
            with col1:
                # Unified checkbox for both pending and completed tasks
                checked = st.checkbox("", value=task['completada'], key=f"task_{task['id']}_e{estrategia_id or 'todas'}")
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
                
                if task['completada'] and completion_date:
                    st.caption(f"✅ {completion_date} - +{task['puntos']} puntos")
                elif task['completada']:
                    st.caption(f"✅ Completada - +{task['puntos']} puntos")
            
            with col3:
                if not task['completada']:
                    if st.button("🗑️", key=f"delete_{task['id']}_e{estrategia_id or 'todas'}", help="Eliminar tarea"):
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
                        if st.button("🗑️ Limpiar", key=f"clear_chat_{task['id']}_e{estrategia_id or 'todas'}", help="Reiniciar conversación"):
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
                    if st.button("📝 Dame un ejemplo", key=f"sugg1_{task['id']}_e{estrategia_id or 'todas'}", use_container_width=True):
                        user_msg = "Dame un ejemplo concreto de cómo hacer esta tarea"
                        st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                        # Generate AI response immediately
                        with st.spinner("🤔 Pensando..."):
                            ai_response = get_task_ai_help(task, user_msg, username)
                            st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                        st.rerun()
                
                with col_s2:
                    if st.button("⏰ ¿Cuándo hacerlo?", key=f"sugg2_{task['id']}_e{estrategia_id or 'todas'}", use_container_width=True):
                        user_msg = "¿Cuál es el mejor momento para hacer esta tarea?"
                        st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                        with st.spinner("🤔 Pensando..."):
                            ai_response = get_task_ai_help(task, user_msg, username)
                            st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                        st.rerun()
                
                with col_s3:
                    if st.button("🎯 Tips y trucos", key=f"sugg3_{task['id']}_e{estrategia_id or 'todas'}", use_container_width=True):
                        user_msg = "Dame tips y mejores prácticas para esta tarea"
                        st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                        with st.spinner("🤔 Pensando..."):
                            ai_response = get_task_ai_help(task, user_msg, username)
                            st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                        st.rerun()
                
                # Chat input (like sections - supports Enter key)
                prompt = st.chat_input("Pregunta sobre esta tarea...", key=f"chat_input_{task['id']}_e{estrategia_id or 'todas'}")
                
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
        seccion = task.get('seccion_origen', '')
        if seccion == 'embudo':
            context += f"Embudo de contenido: {estrategia.get('embudo', '')[:500]}...\n"
        elif seccion == 'ads':
            context += f"Estrategia de Ads: {estrategia.get('ads', '')[:500]}...\n"
        elif seccion == 'whatsapp':
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


def show_create_task_form(username, estrategia_id=None):
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
                    dia_semana=dia_semana,
                    estrategia_id=estrategia_id
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
