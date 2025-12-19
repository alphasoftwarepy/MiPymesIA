"""
Tracking Panel - Visual UI for task management and progress tracking
"""

import streamlit as st
import tasks_manager
import time
from datetime import datetime, timedelta

def tracking_panel_page():
    """Main tracking panel page with tabs for multiple strategies"""
    st.title("📊 Mi Progreso")
    
    user = st.session_state.get('user')
    if not user:
        st.error("No se encontró información del usuario. Por favor inicia sesión.")
        st.stop()
        
    username = user.get('username')
    
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
    
    # Get current strategy info for context
    import auth
    estrategia_info = auth.get_estrategia_by_id(estrategia_id, username)
    
    current_week_real = estrategia_info.get('semana_actual', 1)
    total_weeks = int(estrategia_info.get('duracion_dias', 30) / 7)
    
    # Initialize view state
    if 'view_week_num' not in st.session_state or st.session_state.get('last_strat_id') != estrategia_id:
        st.session_state.view_week_num = current_week_real
        st.session_state.last_strat_id = estrategia_id

    week_view = st.session_state.view_week_num
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"#### 📅 Semana {week_view} de {total_weeks}")
        
        # Navigation
        c_prev, c_next = st.columns(2)
        if c_prev.button("⬅️", disabled=(week_view <= 1)):
            st.session_state.view_week_num -= 1
            st.rerun()
        if c_next.button("➡️", disabled=(week_view >= current_week_real)):
            st.session_state.view_week_num += 1
            st.rerun()
    
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
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Tareas de Hoy", "📅 Vista Semanal", "✅ Completadas", "🏆 Logros"])
    
    # ========== TAB 1: TAREAS ==========
    with tab1:
        if st.button("➕ Crear Tarea", key=f"btn_create_task_{estrategia_id or 'todas'}"):
            st.session_state.show_create_task = True
            st.rerun()
        
        # Get today's tasks based on assigned date from strategy creation
        today_tasks = tasks_manager.get_tasks_for_today(username, estrategia_id)
        today = datetime.now().date()
        
        if not today_tasks:
            st.info("🎉 ¡No tienes tareas pendientes para hoy! Puedes crear tareas manualmente o generar una nueva estrategia.")
            
            # Button for Manual Generation (Week 1 / Initial)
            if week_view == 1 and not tasks_manager.get_tasks_for_week(username, estrategia_id):
                 if st.button("🚀 COMENZAR SEMANA 1 (Generar Plan)", type="primary"):
                     # Custom Popup Overlay
                     loader_placeholder = st.empty()
                     loader_placeholder.markdown("""
                        <style>
                        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                        .custom-loader {
                            border: 5px solid #f3f3f3;
                            border-top: 5px solid #3498db;
                            border-radius: 50%;
                            width: 50px;
                            height: 50px;
                            animation: spin 1s linear infinite;
                            margin: 0 auto 20px auto;
                        }
                        .loading-overlay {
                            position: fixed;
                            top: 0;
                            left: 0;
                            width: 100%;
                            height: 100%;
                            background: rgba(255, 255, 255, 0.9);
                            z-index: 999999;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            flex-direction: column;
                        }
                        .loader-card {
                            background: white;
                            padding: 40px;
                            border-radius: 15px;
                            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                            text-align: center;
                            max-width: 400px;
                        }
                        .loading-text {
                            font-size: 1.2em;
                            color: #2c3e50;
                            font-weight: 600;
                        }
                        </style>
                        <div class="loading-overlay">
                            <div class="loader-card">
                                <div class="custom-loader"></div>
                                <div class="loading-text">🧠 Analizando Roadmap y diseñando tareas...</div>
                            </div>
                        </div>
                     """, unsafe_allow_html=True)
                     
                     try:
                         roadmap = estrategia_info.get('roadmap', [])
                         # Generate tasks manually
                         tasks_manager.generate_weekly_tasks(username, estrategia_id, 1, "", roadmap)
                         time.sleep(1)
                         loader_placeholder.empty()
                         
                         # ⭐ CLEAR CACHE TO REFRESH VIEW
                         st.cache_data.clear()
                         
                         st.success("✅ ¡Plan de Acción Generado!")
                         st.rerun()
                     except Exception as e:
                         loader_placeholder.empty()
                         st.error(f"Error: {e}")

            if st.button("➕ Crear Tarea Manual", key=f"btn_create_task_manual_{estrategia_id or 'todas'}"):
                st.session_state.show_create_task = True
                st.rerun()
        else:
            # Separate pending and completed
            pending_tasks = [t for t in today_tasks if not t['completada']]
            completed_tasks = [t for t in today_tasks if t['completada']]
            
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
        # Calculate dates for the VIEWED week
        if estrategia_info:
            base_date = datetime.fromisoformat(estrategia_info['created_at']).date()
        else:
            base_date = datetime.now().date()
            
        start_of_week_view = base_date + timedelta(days=(week_view-1)*7)
        end_of_week_view = start_of_week_view + timedelta(days=6)
        
        st.markdown(f"### 🗓️ Agenda Semanal: {start_of_week_view.strftime('%d %b')} - {end_of_week_view.strftime('%d %b %Y')}")
        
        # Get Focus for this week (from Roadmap)
        roadmap = estrategia_info.get('roadmap', [])
        week_focus = "General"
        if isinstance(roadmap, list):
            week_focus = next((item.get('foco', 'General') for item in roadmap if item.get('semana') == week_view), "General")
        
        st.info(f"🎯 **Foco de la Semana:** {week_focus}")
        
        # --- WEEKLY CYCLE CONTROLS ---
        # Only show controls if viewing the current real week
        if week_view == current_week_real:
            with st.expander("⚙️ Gestión de la Semana (Cierre y Feedback)", expanded=True):
                col_cycle1, col_cycle2 = st.columns(2)
                
                with col_cycle1:
                    # Regeneration Logic with Confirmation
                    if 'confirm_regen_week' not in st.session_state:
                        st.session_state.confirm_regen_week = False
                        
                    if not st.session_state.confirm_regen_week:
                        if st.button("🔄 Regenerar Tareas de esta Semana", help="Si no te gustan las tareas, géneralas de nuevo"):
                            st.session_state.confirm_regen_week = True
                            st.rerun()
                    else:
                        st.warning("¿Estás seguro%s Se borrarán las tareas actuales de esta semana.")
                        col_conf1, col_conf2 = st.columns(2)
                        with col_conf1:
                            if st.button("✅ Sí, Regenerar", type="primary"):
                                with st.spinner("🔄 Diseñando nuevas tareas para tu semana..."):
                                    # Delete and regenerate
                                    tasks_manager.delete_week_tasks(username, estrategia_id, week_view)
                                    # We need previous feedback to regenerate appropriately
                                    prev_feedback = "Feedback regenerado por usuario."
                                    if week_view > 1:
                                        hist = estrategia_info.get('feedback_historico', [])
                                        last_fb = next((i for i in hist if i['week'] == week_view-1), None)
                                        if last_fb: prev_feedback = last_fb.get('feedback', '')
                                        
                                    # Call regeneration (using generate_weekly logic)
                                    tasks_manager.generate_weekly_tasks(username, estrategia_id, week_view, prev_feedback, roadmap)
                                    time.sleep(1) # Visual confirmation
                                    
                                st.session_state.confirm_regen_week = False
                                st.success("✅ Tareas regeneradas con éxito")
                                time.sleep(1)
                                st.rerun()
                        with col_conf2:
                            if st.button("❌ Cancelar"):
                                st.session_state.confirm_regen_week = False
                                st.rerun()

                with col_cycle2:
                    if st.button("🏁 Cerrar Semana y Avanzar",
                               type="primary",
                               help="Completa la semana y genera la siguiente",
                               disabled=(current_week_real >= total_weeks)):
                        st.session_state.show_feedback_modal = True

            # Feedback Modal Logic
            if st.session_state.get('show_feedback_modal', False):
                with st.form("weekly_feedback_form"):
                    st.write("### 📝 Feedback de la Semana")
                    st.write("Antes de pasar a la siguiente semana, cuéntanos cómo te fue.")
                    
                    feedback_text = st.text_area("¿Qué funcionó? ¿Qué no? ¿Algún logro?", placeholder="Ej: Las campañas de ads trajeron buenos leads, pero muy caros.")
                    metric_input = st.text_input("Métrica Clave (opcional)", placeholder="Ej: 5 Ventas, CPL $2.5")
                    
                    submitted = st.form_submit_button("🚀 Generar Siguiente Semana")
                    
                    if submitted:
                        # Get strategy info to calculate weeks
                        import auth
                        estrategia_info = auth.get_estrategia_by_id(estrategia_id, username)
                        current_week_real = estrategia_info.get('semana_actual', 1)
                        total_weeks = int(estrategia_info.get('duracion_dias', 30) / 7)
                        roadmap = estrategia_info.get('roadmap', [])
                        
                        print(f"📊 Current week: {current_week_real}, Total weeks: {total_weeks}")
                        
                        # Save feedback logic would go here (need to add to auth.py or handle in tasks_manager/main)
                        
                        # Generate Next Week
                        next_week = current_week_real + 1
                        if next_week <= total_weeks:
                            # 1. Update Strategy current_week in DB
                            import db_config
                            conn = db_config.get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE estrategias_v2 SET semana_actual = %s WHERE id = %s", (next_week, estrategia_id))
                            conn.commit()
                            conn.close()
                            
                            # 2. Generate Tasks
                            print(f"🔄 Iniciando generación de tareas para semana {next_week}")
                            print(f"📊 Roadmap data: {roadmap}")
                            
                            with st.spinner("🧠 Diseñando tu próxima semana..."):
                                try:
                                    saved_count, created_tasks = tasks_manager.generate_weekly_tasks(
                                        username, estrategia_id, next_week, 
                                        f"{feedback_text}. Metrics: {metric_input}", 
                                        roadmap
                                    )
                                    print(f"✅ Generadas {saved_count} tareas para semana {next_week}")
                                except Exception as e:
                                    print(f"❌ Error generando tareas: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    st.error(f"Error al generar tareas: {e}")
                                    st.stop()
                            
                            # Clear cache to show new week tasks immediately
                            st.cache_data.clear()
                            st.session_state.show_feedback_modal = False
                            st.session_state.view_week_num = next_week # Update view
                            st.success("✅ ¡Semana iniciada!")
                            st.rerun()
                        else:
                            st.success("🎉 ¡Has completado toda la estrategia!")
                            st.session_state.show_feedback_modal = False


        st.markdown("---")
        
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
        
                # Get strategy creation date
        import auth
        estrategia_info = auth.get_estrategia_by_id(estrategia_id, username)
        if estrategia_info:
            created_date = datetime.fromisoformat(estrategia_info['created_at']).date()
        else:
            created_date = datetime.now().date()
        
        st.markdown(f"**Semana de la Estrategia: {created_date.strftime('%d %b')} - {(created_date + timedelta(days=6)).strftime('%d %b %Y')}**")
        
        # Track which unique tasks we've already shown (for unique tasks)
        shown_unique_tasks = set()
        
        # Show 7 days for the VIEWED week
        # Calculate day offset relative to Creation Date for the START of the viewed week
        week_start_offset = (week_view - 1) * 7
        
        for i in range(7):
            day_offset = week_start_offset + i
            fecha = created_date + timedelta(days=day_offset)
            dia_semana_num = fecha.weekday()  # Still needed for day name only
            dia_nombre = dias[dia_semana_num]
            es_hoy = fecha == datetime.now().date()
            
            # Filter tasks for this specific date using calculated assigned date
            tasks_dia = []
            for t in all_tasks:
                if estrategia_info:
                    # Calculate assigned date for this task (creation + dia_semana days)
                    task_assigned_date = datetime.fromisoformat(estrategia_info['created_at']).date() + timedelta(days=t['dia_semana'] if t['dia_semana'] is not None else 0)
                    
                    # Unique tasks logic (same as before)
                    if t['frecuencia'] == 'unica':
                        task_id = t['id']
                        if task_id not in shown_unique_tasks:
                            if not t['completada']:
                                # Show unique pending tasks on their assigned date
                                if task_assigned_date == fecha:
                                    tasks_dia.append(t)
                                    shown_unique_tasks.add(task_id)
                            elif t.get('fecha_completada'):
                                try:
                                    comp_date = datetime.fromisoformat(t['fecha_completada']).date()
                                    if comp_date == fecha:
                                        tasks_dia.append(t)
                                        shown_unique_tasks.add(task_id)
                                except:
                                    pass
                    # Date-specific tasks
                    elif task_assigned_date == fecha:
                        tasks_dia.append(t)
            
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
    
    # ========== TAB 3: TAREAS COMPLETADAS ==========
    with tab3:
        st.markdown("### ✅ Tareas Completadas de la Semana")
        
        # Get all completed tasks for the current week
        all_week_tasks = tasks_manager.get_tasks_for_week(username, estrategia_id)
        completed_week_tasks = [t for t in all_week_tasks if t['completada']]
        
        if not completed_week_tasks:
            st.info("🎯 Aún no has completado tareas esta semana. ¡Comienza ahora!")
        else:
            # Stats
            total_points = sum(t['puntos'] for t in completed_week_tasks)
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.metric("✅ Completadas", len(completed_week_tasks))
            with col_stat2:
                st.metric("⭐ Puntos Ganados", total_points)
            with col_stat3:
                # Calculate completion rate
                total_week = len(all_week_tasks)
                completion_rate = int((len(completed_week_tasks) / total_week * 100)) if total_week > 0 else 0
                st.metric("📈 Tasa de Completitud", f"{completion_rate}%")
            
            st.markdown("---")
            
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                filter_category = st.selectbox(
                    "Filtrar por categoría",
                    ["Todas"] + list(set(t['categoria'] for t in completed_week_tasks)),
                    key=f"filter_cat_completed_{estrategia_id}"
                )
            
            with col_filter2:
                sort_option = st.selectbox(
                    "Ordenar por",
                    ["Más recientes", "Más antiguas", "Mayor puntaje", "Categoría"],
                    key=f"sort_completed_{estrategia_id}"
                )
            
            # Apply filters
            filtered_tasks = completed_week_tasks
            if filter_category != "Todas":
                filtered_tasks = [t for t in filtered_tasks if t['categoria'] == filter_category]
            
            # Apply sorting
            if sort_option == "Más recientes":
                filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('fecha_completada', ''), reverse=True)
            elif sort_option == "Más antiguas":
                filtered_tasks = sorted(filtered_tasks, key=lambda x: x.get('fecha_completada', ''))
            elif sort_option == "Mayor puntaje":
                filtered_tasks = sorted(filtered_tasks, key=lambda x: x['puntos'], reverse=True)
            elif sort_option == "Categoría":
                filtered_tasks = sorted(filtered_tasks, key=lambda x: x['categoria'])
            
            st.markdown(f"**Mostrando {len(filtered_tasks)} tarea(s)**")
            st.markdown("---")
            
            # Display completed tasks
            today = datetime.now().date()
            for task in filtered_tasks:
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
                            date_str = f"Hace {days_ago} días"
                    except:
                        date_str = ""
                else:
                    date_str = ""
                
                # Render completed task
                render_task_card(task, username, is_completed=True, completion_date=date_str, estrategia_id=estrategia_id)
    
    # ========== TAB 4: LOGROS ==========
    with tab4:
        
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

    # ========== CONFIGURACIÓN / ZONA DE PELIGRO ==========
    st.markdown("---")
    with st.expander("⚙️ Configuración y Zona de Peligro"):
        st.warning("⚠️ **Zona de Peligro**: Las siguientes acciones son destructivas.")
        
        col_danger1, col_danger2 = st.columns([3, 1])
        with col_danger1:
            st.write("**Reiniciar Mi Progreso**")
            st.caption("Esto borrará TODAS tus tareas, logros y puntos. Tu estrategia volverá a la Semana 1. NO afecta tus límites de plan.")
        
        with col_danger2:
            if st.button("🗑️ Reiniciar Todo", type="primary", use_container_width=True, key="btn_reset_progress_init"):
                st.session_state.confirm_reset_progress = True
                st.rerun()
        
        if st.session_state.get('confirm_reset_progress', False):
            st.error("¿Estás COMPLETAMENTE SEGURO%s Esta acción no se puede deshacer.")
            col_conf_reset1, col_conf_reset2 = st.columns(2)
            with col_conf_reset1:
                # Double confirmation button
                if st.button("✅ SÍ, BORRAR TODO", type="primary", key="btn_reset_progress_confirm"):
                    with st.spinner("🗑️ Reiniciando tu progreso..."):
                        success = tasks_manager.reset_user_progress(username)
                        if success:
                            st.success("✅ Progreso reiniciado correctamente.")
                            time.sleep(1)
                            st.session_state.confirm_reset_progress = False
                            st.rerun()
                        else:
                            st.error("❌ Error al reiniciar progreso.")
            
            with col_conf_reset2:
                if st.button("❌ Cancelar", key="btn_reset_progress_cancel"):
                    st.session_state.confirm_reset_progress = False
                    st.rerun()

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
            chat_section_id = f"task_{task['id']}"
            
            if chat_history_key not in st.session_state:
                st.session_state[chat_history_key] = []
                # Load from database
                import auth
                saved_history = auth.get_section_history(username, chat_section_id)
                if saved_history:
                    for entry in saved_history:
                        st.session_state[chat_history_key].append({
                            "role": entry['tipo'],
                            "content": entry['contenido']
                        })
            
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
                            import auth
                            auth.clear_section_history(username, chat_section_id)
                            st.rerun()
                
                # Display chat messages with st.chat_message (like sections)
                for msg in st.session_state[chat_history_key]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                
                                # Proactive execution button
                if st.button("🚀 ¡Ayúdame con esta tarea!", key=f"exec_{task['id']}_e{estrategia_id or 'todas'}", use_container_width=True, type="primary"):
                    user_msg = "Ayúdame a ejecutar esta tarea con un borrador o guía específica para mi negocio"
                    st.session_state[chat_history_key].append({"role": "user", "content": user_msg})
                    
                    # Generate AI response immediately
                    with st.spinner("🤔 Creando tu borrador personalizado..."):
                        ai_response = get_task_ai_help(task, user_msg, username, proactive=True)
                        st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                    
                    # Save to DB
                    import auth
                    auth.save_section_history(username, chat_section_id, "user", user_msg)
                    auth.save_section_history(username, chat_section_id, "assistant", ai_response)
                    
                    # ⭐ ENRICH BRAIN FROM INTERACTION
                    try:
                        insights_added = auth.enrich_brain_from_interaction(username, chat_section_id, user_msg, ai_response)
                        if insights_added > 0:
                            print(f"✅ Added {insights_added} insight(s) to brain from task help (proactive)")
                    except Exception as e:
                        print(f"⚠️ Warning: Failed to enrich brain from task help: {e}")
                    
                    st.rerun()
                
                st.caption("💬 O escribe tu pregunta específica abajo:")
                
                # Chat input (like sections - supports Enter key)
                prompt = st.chat_input("Pregunta sobre esta tarea...", key=f"chat_input_{task['id']}_e{estrategia_id or 'todas'}")
                
                if prompt:
                    # Add user message
                    st.session_state[chat_history_key].append({"role": "user", "content": prompt})
                    
                    # Generate AI response
                    with st.spinner("🤔 Pensando..."):
                        ai_response = get_task_ai_help(task, prompt, username)
                        st.session_state[chat_history_key].append({"role": "assistant", "content": ai_response})
                    
                    # Save to DB
                    import auth
                    auth.save_section_history(username, chat_section_id, "user", prompt)
                    auth.save_section_history(username, chat_section_id, "assistant", ai_response)
                    
                    # ⭐ ENRICH BRAIN FROM INTERACTION
                    try:
                        insights_added = auth.enrich_brain_from_interaction(username, chat_section_id, prompt, ai_response)
                        if insights_added > 0:
                            print(f"✅ Added {insights_added} insight(s) to brain from task help")
                    except Exception as e:
                        print(f"⚠️ Warning: Failed to enrich brain from task help: {e}")
                    
                    st.rerun()
        
        st.markdown("")


def get_task_ai_help(task, user_question, username, proactive=False):
    """Get AI assistance for a specific task."""
    from openai import OpenAI
    import os
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Build context
    import auth
    
    # Get user's strategy and brain data
    estrategia = auth.get_estrategia(username)
    brain_data = auth.get_brain_data(username)
    
    # Get the SPECIFIC strategy for this task if available
    if task.get('estrategia_id'):
        estrategia_especifica = auth.get_estrategia_by_id(task['estrategia_id'])
        if estrategia_especifica:
            estrategia = estrategia_especifica
    
    # Build rich context
    context = f"""Eres un asistente experto en marketing digital que ayuda a ejecutar tareas específicas.

TAREA ACTUAL:
- Título: {task['titulo']}
- Descripción: {task['descripcion']}
- Categoría: {task['categoria']}
- Prioridad: {task['prioridad']}

CONTEXTO DEL NEGOCIO (Cerebro):
"""
    
    # Get REAL data from Cerebro
    if brain_data:
        rubros = brain_data.get('rubros', [])
        if rubros:
            rubros_text = ", ".join([r.get('nombre', '') for r in rubros if r.get('nombre')])
            context += f"- Rubros: {rubros_text}\n"
        
        servicios = brain_data.get('servicios', [])
        if servicios:
            servicios_text = ", ".join([s.get('nombre', '') for s in servicios[:5] if s.get('nombre')])
            context += f"- Servicios/Productos: {servicios_text}\n"
    
    # Add SPECIFIC strategy context
    if estrategia:
        context += f"\nESTRATEGIA ESPECÍFICA:\n"
        context += f"- Producto/Servicio: {estrategia.get('producto', 'N/A')}\n"
        context += f"- Nombre: {estrategia.get('nombre', 'N/A')}\n"
        
        # Add differentiator, price, and goal if available
        diferenciador = estrategia.get('diferenciador', '')
        precio = estrategia.get('precio', 0)
        meta = estrategia.get('meta', '')
        
        if diferenciador:
            context += f"- 🎯 DIFERENCIADOR COMPETITIVO: {diferenciador}\n"
        if precio and precio > 0:
            context += f"- 💰 PRECIO: ${precio} USD\n"
        if meta:
            context += f"- 🎯 META ACTUAL: {meta}\n"

        # Add relevant section content based on task category
        seccion = task.get('categoria', '')
        if seccion == 'contenido' or seccion == 'embudo':
            embudo_content = estrategia.get('embudo', '')
            if embudo_content:
                context += f"\nEmbudo de contenido (extracto):\n{embudo_content[:400]}...\n"
        elif seccion == 'ads':
            ads_content = estrategia.get('ads', '')
            if ads_content:
                context += f"\nEstrategia de Ads (extracto):\n{ads_content[:400]}...\n"
        elif seccion == 'whatsapp':
            whatsapp_content = estrategia.get('whatsapp', '')
            if whatsapp_content:
                context += f"\nFlujo WhatsApp (extracto):\n{whatsapp_content[:400]}...\n"
        
        # Add Avatar if available
        avatar_content = estrategia.get('avatar', '')
        if avatar_content:
            context += f"\nBuyer Persona (extracto):\n{avatar_content[:300]}...\n"
    
# Add proactive mode instructions
    if proactive:
        context += f"""
MODO PROACTIVO - EJECUTOR:
Tu objetivo es darle al usuario un BORRADOR LISTO PARA USAR, no solo consejos.
INSTRUCCIONES CRÍTICAS:
1. Crea un borrador completo y específico para esta tarea usando el producto/servicio real
2. Si es contenido/copy: Escribe el texto completo con emojis, hashtags y CTA
3. Si es Reel/video: Escribe el guion completo escena por escena
4. Si es ads: Escribe 3 variantes de copy listas para publicar
5. Si es WhatsApp: Escribe el mensaje completo listo para enviar
6. SIEMPRE integra el DIFERENCIADOR COMPETITIVO de forma natural en el mensaje
7. Ajusta el tono según el PRECIO (bajo=urgencia, alto=valor/exclusividad)
8. Alinea el mensaje con la META ACTUAL del negocio
9. Máximo 250 palabras, formato listo para copiar y pegar
💡 OPORTUNIDAD ESTRATÉGICA (solo si aplica):
- Si detectas que el borrador puede mejorar significativamente usando el diferenciador, agrega al final:
  "💡 Oportunidad: [Breve sugerencia de cómo potenciar el mensaje con el diferenciador]"
- NO agregues esta sección si el diferenciador ya está bien integrado
PREGUNTA DEL USUARIO: {user_question}
"""
    else:
        context += f"""
INSTRUCCIONES CRÍTICAS:
1. USA el producto/servicio específico de la estrategia en tus ejemplos
2. Adapta tu respuesta según el PRECIO del producto:
   - Precio bajo (<$50): Enfócate en urgencia, volumen, promociones
   - Precio medio ($50-$500): Enfócate en valor, beneficios, comparación
   - Precio alto (>$500): Enfócate en exclusividad, transformación, ROI
3. Alinea tu consejo con la META ACTUAL (si es ganar seguidores, no vendas directo; si es vender, sé más agresivo)
4. Si es contenido/copy: Usa fórmulas probadas (AIDA, PAS) con el diferenciador integrado
5. Si es ads: Sugiere segmentación específica según el buyer persona y presupuesto real
6. Si es Reel/video: Crea estructura con hook, valor y CTA alineados a la meta
7. Si es WhatsApp: Ajusta el tono según el precio (bajo=casual, alto=profesional)
8. Si es análisis/métricas: Usa los KPIs relevantes para la meta actual
9. Sé breve pero completo (máximo 200 palabras)
10. NO inventes campañas genéricas, usa el contexto real
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
                    # Clear cache to show new task immediately
                    st.cache_data.clear()
                    st.success("✅ Tarea creada exitosamente")
                    st.session_state.show_create_task = False
                    st.rerun()
                else:
                    st.error("Error al crear la tarea")
        
        if cancel:
            st.session_state.show_create_task = False
            st.rerun()
