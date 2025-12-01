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
    with st.expander("📊 Información Base del Negocio", expanded=True):
        base_info = brain_data.get('base', {})
        
        if base_info and base_info.get('rubro'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Rubro:** {base_info.get('rubro', 'No especificado')}")
                st.markdown(f"**Producto:** {base_info.get('producto', 'No especificado')}")
                st.markdown(f"**Precio:** ${base_info.get('precio', 'No especificado')}")
                st.markdown(f"**Tipo:** {base_info.get('tipo', 'No especificado')}")
            with col2:
                st.markdown(f"**Meta:** {base_info.get('meta', 'No especificado')}")
                st.markdown(f"**Presupuesto:** ${base_info.get('presupuesto', 'No especificado')}")
                st.markdown(f"**Plataformas:** {base_info.get('plataforma', 'No especificado')}")
                st.markdown(f"**Modalidad:** {base_info.get('modalidad_venta', 'No especificado')}")
            
            # Cliente Ideal - Expandible para ver todo el texto
            if base_info.get('avatar', {}).get('descripcion'):
                st.markdown("---")
                st.markdown("**Cliente Ideal:**")
                avatar_desc = base_info['avatar']['descripcion']
                
                # Mostrar en text_area expandible (solo lectura) con más altura
                st.text_area(
                    "Cliente Ideal",
                    value=avatar_desc,
                    height=250,  # Aumentado de 150 a 250
                    disabled=True,
                    label_visibility="collapsed",
                    key="avatar_display_readonly"
                )
            
            st.caption("✅ Auto-poblado desde tu estrategia generada")
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
            
            # Clear insights button
            if st.button("🗑️ Limpiar Todos los Insights", key="clear_insights_btn"):
                brain_data['insights'] = []
                auth.update_brain_data(username, brain_data)
                st.success("✅ Insights eliminados")
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
