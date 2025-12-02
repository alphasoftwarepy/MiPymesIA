import streamlit as st
import auth

def business_brain_page():
    """
    Cerebro del Negocio - Knowledge visualization panel only.
    Chat functionality is in MiPymes IA page.
    """
    st.title("🧠 Cerebro del Negocio")
    st.caption("Visualiza y edita el conocimiento que la IA tiene sobre tu negocio")
    
    user = st.session_state.user
    username = user['username']
    
    brain_data = auth.get_brain_data(username)
    
    # Base Information Card
    with st.expander("📊 Información del Negocio", expanded=True):
        base_info = brain_data.get('base', {})
        
        if base_info and base_info.get('rubro'):
            # Narrative format - more professional
            nombre = base_info.get('nombre', 'Tu Negocio')
            rubro = base_info.get('rubro', '')
            producto = base_info.get('producto', '')
            tipo = base_info.get('tipo', '')
            
            # Main description
            st.markdown(f"### {nombre} – Resumen Ejecutivo")
            st.markdown(f"**{nombre}** es un negocio de **{rubro}** enfocado en {tipo.lower()}.")
            st.markdown("")
            
            # Service/Product highlight
            st.markdown("#### 🎯 Producto/Servicio Principal")
            st.info(f"**{producto}**")
            
            # Key metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Precio", f"${base_info.get('precio', 0)}")
            with col2:
                st.metric("Presupuesto Mensual", f"${base_info.get('presupuesto', 0)}")
            with col3:
                st.metric("Meta", base_info.get('meta', 'N/A'))
            
            # Additional details
            st.markdown("#### 📋 Detalles Operativos")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Plataformas:** {base_info.get('plataforma', 'No especificado')}")
            with col_b:
                st.markdown(f"**Modalidad:** {base_info.get('modalidad_venta', 'No especificado')}")
            
            # Diferenciadores if available
            diferenciadores = brain_data.get('diferenciadores', [])
            if diferenciadores:
                st.markdown("#### 💎 Diferenciadores Clave")
                for dif in diferenciadores[-3:]:  # Last 3
                    st.success(f"✓ {dif.get('principal', '')}")
            
            # Clear base info button with confirmation
            st.markdown("---")
            if 'confirm_clear_base' not in st.session_state:
                st.session_state.confirm_clear_base = False
            
            if not st.session_state.confirm_clear_base:
                if st.button("🗑️ Limpiar Información del Negocio", type="secondary"):
                    st.session_state.confirm_clear_base = True
                    st.rerun()
            else:
                st.warning("⚠️ ¿Estás seguro? Esta acción eliminará toda la información base del negocio.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Sí, limpiar", type="primary"):
                        auth.clear_base_info(username)
                        st.session_state.confirm_clear_base = False
                        st.success("✅ Información base eliminada")
                        st.rerun()
                with col_no:
                    if st.button("❌ Cancelar"):
                        st.session_state.confirm_clear_base = False
                        st.rerun()
            
            # Cliente Ideal - Expandible
            if base_info.get('avatar', {}).get('descripcion'):
                st.markdown("#### 👤 Cliente Ideal")
                avatar_desc = base_info['avatar']['descripcion']
                st.text_area(
                    "Cliente Ideal",
                    value=avatar_desc,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                    key="avatar_display_readonly"
                )
            
            st.caption("✅ Auto-poblado y actualizado desde tus estrategias")
        else:
            st.warning("⚠️ Aún no hay información base. Genera tu primera estrategia para auto-poblar el cerebro.")
    
    # Insights Card
    with st.expander("💡 Insights y Aprendizajes Recientes", expanded=True):
        insights = brain_data.get('insights', [])
        
        if insights:
            st.caption(f"Total de insights: {len(insights)}")
            
            # Group by type
            by_type = {}
            for insight in insights:
                tipo = insight.get('tipo', 'otro')
                if tipo not in by_type:
                    by_type[tipo] = []
                by_type[tipo].append(insight)
            
            # Display by type
            type_labels = {
                'mensaje_ganador': '✅ Mensajes que Funcionan',
                'objecion': '🛡️ Objeciones Detectadas',
                'resultado': '📊 Resultados Obtenidos',
                'recomendacion': '💡 Recomendaciones Clave'
            }
            
            for tipo, label in type_labels.items():
                if tipo in by_type:
                    st.markdown(f"**{label}** ({len(by_type[tipo])})")
                    for item in by_type[tipo][-5:]:  # Show last 5
                        st.markdown(f"- {item.get('contenido', '')}")
                    st.markdown("")
            
            # Clear insights button with confirmation
            if 'confirm_clear_insights' not in st.session_state:
                st.session_state.confirm_clear_insights = False
            
            if not st.session_state.confirm_clear_insights:
                if st.button("🗑️ Limpiar Todos los Insights", key="clear_insights_btn", type="secondary"):
                    st.session_state.confirm_clear_insights = True
                    st.rerun()
            else:
                st.warning("⚠️ ¿Estás seguro? Esta acción eliminará todos los insights aprendidos.")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Sí, limpiar", key="confirm_clear_insights_yes", type="primary"):
                        brain_data['insights'] = []
                        auth.update_brain_data(username, brain_data)
                        st.session_state.confirm_clear_insights = False
                        st.success("✅ Insights eliminados")
                        st.rerun()
                with col_no:
                    if st.button("❌ Cancelar", key="confirm_clear_insights_no"):
                        st.session_state.confirm_clear_insights = False
                        st.rerun()
        else:
            st.info("📝 Aún no hay insights. El cerebro aprenderá automáticamente de tus interacciones.")
    
    # Manual Context Card
    with st.expander("✏️ Contexto Adicional Manual", expanded=False):
        st.caption("Agrega información adicional que quieras que el Cerebro recuerde")
        
        current_manual = brain_data.get('contexto_manual', '')
        
        manual_text = st.text_area(
            "Contexto adicional",
            value=current_manual,
            height=200,
            placeholder="Ejemplo: Tenemos una promoción especial de verano, nuestro público objetivo son madres trabajadoras, etc.",
            label_visibility="collapsed",
            key="manual_context_editor"
        )
        
        if st.button("💾 Guardar Contexto Manual", key="save_manual_context_btn"):
            brain_data['contexto_manual'] = manual_text
            from datetime import datetime
            brain_data['ultima_actualizacion'] = datetime.utcnow().isoformat()
            auth.update_brain_data(username, brain_data)
            st.success("✅ Contexto guardado")
            st.rerun()
    
    # Last Update Info
    if brain_data.get('ultima_actualizacion'):
        from datetime import datetime as dt
        try:
            updated = dt.fromisoformat(brain_data['ultima_actualizacion'])
            st.caption(f"🔄 Última actualización: {updated.strftime('%d/%m/%Y %H:%M')}")
        except:
            pass
