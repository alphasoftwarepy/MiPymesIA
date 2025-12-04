import streamlit as st
import auth

def business_brain_page():
    """
    Cerebro del Negocio - Multi-Service Knowledge Panel
    NEW: ChatGPT-style format with service cards and valuable insights only
    """
    st.title("🧠 Cerebro del Negocio")
    st.caption("Conocimiento acumulado sobre tu negocio y servicios")
    
    user = st.session_state.user
    username = user['username']
    
    brain_data = auth.get_brain_data(username)
    
    # ========== RESUMEN GENERAL DEL NEGOCIO ==========
    with st.expander("⭐ Resumen del Negocio", expanded=True):
        info_general = brain_data.get('info_general', {})
        
        if info_general.get('nombre_negocio') or info_general.get('rubros'):
            # Nombre del negocio
            if info_general.get('nombre_negocio'):
                st.markdown(f"### {info_general['nombre_negocio']}")
            
            # Descripción general si existe
            if info_general.get('descripcion_general'):
                st.markdown(info_general['descripcion_general'])
                st.markdown("")
            
            # Rubros, Tipos de Venta, Formas de Pago en columnas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                rubros = info_general.get('rubros', [])
                if rubros:
                    st.markdown("**Rubros:**")
                    for rubro in rubros:
                        st.markdown(f"• {rubro}")
            
            with col2:
                tipos_venta = info_general.get('tipos_venta', [])
                if tipos_venta:
                    st.markdown("**Tipos de Venta:**")
                    for tipo in tipos_venta:
                        st.markdown(f"• {tipo}")
            
            with col3:
                formas_pago = info_general.get('formas_pago', [])
                if formas_pago:
                    st.markdown("**Formas de Pago:**")
                    for pago in formas_pago:
                        st.markdown(f"• {pago}")
        else:
            st.info("📝 Genera tu primera estrategia para auto-poblar el cerebro")
    
    # ========== SERVICIOS Y PRODUCTOS ==========
    servicios = brain_data.get('servicios', [])
    
    if servicios:
        st.subheader("📦 Servicios y Productos")
        st.caption(f"Total: {len(servicios)} servicio(s)")
        
        for servicio in servicios:
            emoji = servicio.get('emoji', '📦')
            nombre = servicio.get('nombre', 'Servicio')
            
            with st.expander(f"{emoji} {nombre}", expanded=False):
                # Descripción
                if servicio.get('descripcion'):
                    st.markdown(servicio['descripcion'])
                    st.markdown("")
                
                # Info en columnas
                col1, col2 = st.columns(2)
                
                with col1:
                    if servicio.get('rubro'):
                        st.markdown(f"**Rubro:** {servicio['rubro']}")
                    if servicio.get('precio'):
                        st.markdown(f"**Precio:** {servicio['precio']}")
                
                with col2:
                    if servicio.get('tipo_venta'):
                        st.markdown(f"**Tipo:** {servicio['tipo_venta']}")
                    estrategias_count = servicio.get('estrategias_generadas', 0)
                    st.markdown(f"**Estrategias:** {estrategias_count}")
                
                # Diferenciadores con botón de borrado individual
                diferenciadores = servicio.get('diferenciadores', [])
                if diferenciadores:
                    st.markdown("**💎 Diferenciadores:**")
                    for i, dif in enumerate(diferenciadores):
                        col_dif, col_btn = st.columns([5, 1])
                        with col_dif:
                            st.markdown(f"• {dif}")
                        with col_btn:
                            if st.button("🗑️", key=f"del_dif_{servicio['id']}_{i}"):
                                auth.delete_diferenciador(username, servicio['id'], dif)
                                st.success("✅ Diferenciador eliminado")
                                st.rerun()
                
                # Botón eliminar servicio completo
                st.markdown("---")
                if st.button(f"🗑️ Eliminar {nombre}", key=f"del_srv_{servicio['id']}", type="secondary"):
                    auth.delete_service(username, servicio['id'])
                    st.success(f"✅ Servicio '{nombre}' eliminado")
                    st.rerun()
        
        # Separador visual después de Servicios y Productos
        st.markdown("---")
    
    # ========== INSIGHTS Y APRENDIZAJES ==========
    with st.expander("💡 Insights y Aprendizajes", expanded=True):
        insights = brain_data.get('insights', [])
        
        if insights:
            st.caption(f"Total: {len(insights)} insight(s)")
            
            # Emoji map for insight types
            emoji_map = {
                'feedback_cliente': '💬',
                'dolor_cliente': '😖',
                'objecion_real': '🛡️',
                'resultado': '📊',
                'cambio_estrategico': '🔄'
            }
            
            # Show last 20 insights in reverse chronological order
            for i, insight in enumerate(reversed(insights[-20:])):
                col_content, col_btn = st.columns([5, 1])
                
                with col_content:
                    emoji = emoji_map.get(insight.get('tipo', ''), '💡')
                    contenido = insight.get('contenido', '')
                    st.markdown(f"{emoji} {contenido}")
                    
                    # Metadata
                    fuente = insight.get('fuente', 'desconocido')
                    timestamp = insight.get('timestamp', '')[:10]
                    st.caption(f"Fuente: {fuente} • {timestamp}")
                
                with col_btn:
                    # Calculate actual index (reversed)
                    actual_index = len(insights) - 1 - i
                    if st.button("🗑️", key=f"del_insight_{actual_index}"):
                        auth.delete_insight(username, actual_index)
                        st.success("✅ Insight eliminado")
                        st.rerun()
            
            # Botón limpiar todos los insights
            st.markdown("---")
            if 'confirm_clear_insights' not in st.session_state:
                st.session_state.confirm_clear_insights = False
            
            if not st.session_state.confirm_clear_insights:
                if st.button("🗑️ Limpiar Todos los Insights", type="secondary"):
                    st.session_state.confirm_clear_insights = True
                    st.rerun()
            else:
                st.warning("⚠️ ¿Estás seguro? Esta acción eliminará todos los insights.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Sí, limpiar", type="primary"):
                        brain_data['insights'] = []
                        auth.update_brain_data(username, brain_data)
                        st.session_state.confirm_clear_insights = False
                        st.success("✅ Insights eliminados")
                        st.rerun()
                with col_no:
                    if st.button("❌ Cancelar"):
                        st.session_state.confirm_clear_insights = False
                        st.rerun()
        else:
            st.info("📝 El cerebro aprenderá automáticamente de tus interacciones con la IA")
            st.caption("Solo se guardan insights valiosos: feedback real de clientes, dolores específicos, objeciones reales, resultados medibles y cambios estratégicos.")
    
    # ========== CONTEXTO MANUAL ==========
    with st.expander("✏️ Contexto Adicional Manual", expanded=False):
        st.caption("Agrega información adicional que quieras que el Cerebro recuerde")
        
        current_manual = brain_data.get('contexto_manual', '')
        
        manual_text = st.text_area(
            "Contexto adicional",
            value=current_manual,
            height=200,
            placeholder="Ejemplo: Promoción de verano activa hasta marzo, enfoque en madres trabajadoras, etc.",
            label_visibility="collapsed",
            key="manual_context_editor"
        )
        
        if st.button("💾 Guardar Contexto Manual"):
            brain_data['contexto_manual'] = manual_text
            from datetime import datetime
            brain_data['ultima_actualizacion'] = datetime.utcnow().isoformat()
            auth.update_brain_data(username, brain_data)
            st.success("✅ Contexto guardado")
            st.rerun()
    
    # ========== LIMPIAR TODO ==========
    st.markdown("---")
    st.subheader("🗑️ Limpiar Información")
    
    if 'confirm_clear_all' not in st.session_state:
        st.session_state.confirm_clear_all = False
    
    if not st.session_state.confirm_clear_all:
        if st.button("🗑️ Limpiar TODA la Información del Negocio", type="secondary"):
            st.session_state.confirm_clear_all = True
            st.rerun()
    else:
        st.warning("⚠️ ¿Estás seguro? Esta acción eliminará TODOS los servicios e información general.")
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("✅ Sí, limpiar todo", type="primary", key="confirm_clear_all_yes"):
                auth.clear_base_info(username)
                st.session_state.confirm_clear_all = False
                st.success("✅ Información eliminada")
                st.rerun()
        with col_no:
            if st.button("❌ Cancelar", key="confirm_clear_all_no"):
                st.session_state.confirm_clear_all = False
                st.rerun()
    
    # ========== ÚLTIMA ACTUALIZACIÓN ==========
    if brain_data.get('ultima_actualizacion'):
        from datetime import datetime as dt
        try:
            updated = dt.fromisoformat(brain_data['ultima_actualizacion'])
            st.caption(f"🔄 Última actualización: {updated.strftime('%d/%m/%Y %H:%M')}")
        except:
            pass
