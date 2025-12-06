"""
Strategy Selector Component for Multi-Strategy Support
This component allows users to select, create, edit, and delete strategies
"""

import streamlit as st
import auth
import time
from datetime import datetime

def strategy_selector_page():
    """
    Main strategy selector page.
    Shows list of strategies and allows CRUD operations.
    """
    st.title("🚀 Generador MiPymesIA")
    st.caption("Estrategias de Marketing y de Publicidad")
    
    user = st.session_state.user
    username = user['username']
    plan = user.get('plan_actual', 'gratuito')
    
    # Get user's strategy limit
    limite = auth.get_user_estrategias_limit(username)
    
    # Get all strategies
    estrategias = auth.get_all_estrategias(username)
    num_estrategias = len(estrategias)
    
    # Header with counter
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📊 Tus Estrategias ({num_estrategias}/{limite})")
    with col2:
        if num_estrategias < limite:
            if st.button("➕ Nueva", type="primary", use_container_width=True):
                # Limpiar cualquier estado previo
                if 'editing_strategy_id' in st.session_state:
                    del st.session_state.editing_strategy_id
                if 'deleting_strategy_id' in st.session_state:
                    del st.session_state.deleting_strategy_id
                if 'current_strategy_name' in st.session_state:
                    del st.session_state.current_strategy_name
                if 'strategy_result' in st.session_state:
                    del st.session_state.strategy_result
                # Setear modo creación
                st.session_state.creating_new_strategy = True
                st.session_state.step = 1  # Forzar paso 1 para formulario de creación
                st.rerun()
        else:
            st.button(f"🔒 Límite ({limite})", disabled=True, use_container_width=True, 
                     help=f"Has alcanzado el límite de {limite} estrategias de tu plan {plan}")
    
    # If no strategies, show welcome message
    if num_estrategias == 0:
        st.info("👋 ¡Bienvenido! Crea tu primera estrategia de marketing")
        if st.button("🚀 Crear Mi Primera Estrategia", type="primary", use_container_width=True):
            # Limpiar cualquier estado previo
            if 'editing_strategy_id' in st.session_state:
                del st.session_state.editing_strategy_id
            if 'deleting_strategy_id' in st.session_state:
                del st.session_state.deleting_strategy_id
            if 'current_strategy_name' in st.session_state:
                del st.session_state.current_strategy_name
            if 'strategy_result' in st.session_state:
                del st.session_state.strategy_result
            # Setear modo creación
            st.session_state.creating_new_strategy = True
            st.session_state.step = 1  # Forzar paso 1 para formulario de creación
            st.rerun()
        return
    
    # Search and sort (only if more than 3 strategies)
    if num_estrategias > 3:
        col_search, col_sort = st.columns([2, 1])
        with col_search:
            search_query = st.text_input("🔍 Buscar estrategia", placeholder="Nombre o producto...", key="search_estrategias")
        with col_sort:
            sort_by = st.selectbox("Ordenar por", 
                ["Más reciente", "Más antiguo", "Más tareas", "Nombre A-Z"],
                key="sort_estrategias")
        
        # Filter
        if search_query:
            estrategias = [e for e in estrategias 
                          if search_query.lower() in e['nombre'].lower() 
                          or search_query.lower() in e['producto'].lower()]
        
        # Sort
        if sort_by == "Más reciente":
            estrategias.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == "Más antiguo":
            estrategias.sort(key=lambda x: x['created_at'])
        elif sort_by == "Más tareas":
            estrategias.sort(key=lambda x: x['num_tareas'], reverse=True)
        elif sort_by == "Nombre A-Z":
            estrategias.sort(key=lambda x: x['nombre'])
    
    st.markdown("---")
    
    # Display strategies
    if num_estrategias <= 3:
        # Vertical list for few strategies
        for estrategia in estrategias:
            render_strategy_card_full(estrategia, username)
    else:
        # Grid of 3 columns for many strategies
        cols_per_row = 3
        for idx in range(0, len(estrategias), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx, estrategia in enumerate(estrategias[idx:idx+cols_per_row]):
                with cols[col_idx]:
                    render_strategy_card_compact(estrategia, username)


def render_strategy_card_full(estrategia, username):
    """Renders full strategy card with all info"""
    
    # Card container
    with st.container():
        # Header
        col_title, col_tasks = st.columns([3, 1])
        with col_title:
            # Mostrar producto + fecha para mejor identificación
            try:
                created = datetime.fromisoformat(estrategia['created_at'])
                fecha_str = created.strftime('%d/%m/%Y')
            except:
                fecha_str = "N/A"
            st.markdown(f"### 🎯 {estrategia['producto']} - {fecha_str}")
            st.caption(f"**Nombre:** {estrategia['nombre']}")
        with col_tasks:
            progress = estrategia['tareas_completadas'] / estrategia['num_tareas'] if estrategia['num_tareas'] > 0 else 0
            st.metric("Progreso", f"{int(progress*100)}%")
        
        # Info
        st.caption(f"**Producto:** {estrategia['producto']}")
        
        col_date, col_tasks_detail = st.columns(2)
        with col_date:
            try:
                created = datetime.fromisoformat(estrategia['created_at'])
                st.caption(f"📅 Creada: {created.strftime('%d/%m/%Y')}")
            except:
                pass
        with col_tasks_detail:
            st.caption(f"📋 Tareas: {estrategia['num_tareas']} ({estrategia['tareas_completadas']} completadas)")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Editar", key=f"edit_{estrategia['id']}", use_container_width=True):
                st.session_state.editing_strategy_id = estrategia['id']
                st.session_state.creating_new_strategy = False
                st.session_state.step = 2  # Forzar paso 2 para vista de resultados
                st.rerun()
        with col2:
            if st.button("🗑️ Eliminar", key=f"del_{estrategia['id']}", use_container_width=True):
                st.session_state.deleting_strategy_id = estrategia['id']
                st.rerun()
        with col3:
            if st.button("📥 Exportar", key=f"exp_{estrategia['id']}", use_container_width=True):
                # TODO: Implement PDF export
                st.info("Función de exportación próximamente")
        
        st.markdown("---")


def render_strategy_card_compact(estrategia, username):
    """Renders compact strategy card for grid view"""
    
    with st.container():
        # Mostrar producto + fecha
        try:
            created = datetime.fromisoformat(estrategia['created_at'])
            fecha_str = created.strftime('%d/%m')
        except:
            fecha_str = ""
        titulo = f"{estrategia['producto'][:30]}... - {fecha_str}" if len(estrategia['producto']) > 30 else f"{estrategia['producto']} - {fecha_str}"
        st.markdown(f"#### 🎯 {titulo}")
        st.caption(f"**{estrategia['nombre']}**")
        
        # Progress
        progress = estrategia['tareas_completadas'] / estrategia['num_tareas'] if estrategia['num_tareas'] > 0 else 0
        st.progress(progress)
        st.caption(f"{estrategia['tareas_completadas']}/{estrategia['num_tareas']} tareas")
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝", key=f"edit_{estrategia['id']}", use_container_width=True, help="Editar"):
                st.session_state.editing_strategy_id = estrategia['id']
                st.session_state.creating_new_strategy = False
                st.session_state.step = 2  # Forzar paso 2 para vista de resultados
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{estrategia['id']}", use_container_width=True, help="Eliminar"):
                st.session_state.deleting_strategy_id = estrategia['id']
                st.rerun()


def handle_strategy_deletion():
    """Handles strategy deletion with confirmation"""
    if 'deleting_strategy_id' not in st.session_state or not st.session_state.deleting_strategy_id:
        return
    
    estrategia_id = st.session_state.deleting_strategy_id
    username = st.session_state.user['username']
    
    # Get strategy info
    estrategia = auth.get_estrategia_by_id(estrategia_id, username)
    
    if not estrategia:
        st.error("Estrategia no encontrada")
        del st.session_state.deleting_strategy_id
        return
    
    # Show confirmation modal
    st.warning(f"⚠️ ¿Eliminar '{estrategia['nombre']}'?")
    st.info(f"📊 Esta estrategia tiene **{estrategia.get('num_tareas', 0)} tareas** asociadas")
    st.error("🗑️ Esta acción es **IRREVERSIBLE**. Todas las tareas se eliminarán.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Cancelar", use_container_width=True):
            del st.session_state.deleting_strategy_id
            st.rerun()
    with col2:
        if st.button("✅ Confirmar Eliminación", type="primary", use_container_width=True):
            success, message = auth.delete_estrategia(estrategia_id, username)
            if success:
                st.success("✅ Estrategia eliminada exitosamente")
                del st.session_state.deleting_strategy_id
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")


# Export functions for use in main.py
__all__ = ['strategy_selector_page', 'handle_strategy_deletion']
