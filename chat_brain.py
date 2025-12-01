import streamlit as st
import auth

def chat_page():
    """
    MiPymes IA - Chat with full brain functionality.
    Uses enriched brain data for ultra-personalized responses.
    """
    st.title("💬 MiPymes IA")
    st.caption("Tu asistente de marketing que conoce profundamente tu negocio")
    
    user = st.session_state.user
    username = user['username']
    
    # Initialize chat history
    if 'brain_chat_history' not in st.session_state:
        st.session_state.brain_chat_history = []
        
        # Load history from database
        history = auth.get_section_history(username, 'cerebro')
        if history:
            for entry in history:
                st.session_state.brain_chat_history.append({
                    "role": entry['tipo'],
                    "content": entry['contenido']
                })
    
    # Show chat count and clear button
    if len(st.session_state.brain_chat_history) > 0:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.caption(f"📝 {len(st.session_state.brain_chat_history) // 2} conversaciones guardadas")
        with col2:
            if st.button("🗑️ Limpiar Chat", help="Reiniciar conversación"):
                st.session_state.brain_chat_history = []
                auth.clear_section_history(username, 'cerebro')
                st.rerun()
    
    # Display chat messages
    for msg in st.session_state.brain_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    prompt = st.chat_input("Pregunta sobre tu negocio, estrategia, marketing...")
    
    if prompt:
        # ========== CHECK AI REQUEST LIMIT ==========
        can_request, remaining = auth.increment_ai_request(username)
        
        if not can_request:
            st.error("❌ Has alcanzado el límite diario de consultas IA. Intenta mañana o mejora tu plan.")
            st.stop()
        # ============================================
        
        # Add user message
        st.session_state.brain_chat_history.append({"role": "user", "content": prompt})
        
        # Save to database
        auth.save_section_history(username, 'cerebro', "user", prompt)
        
        # Get enriched brain data
        brain_data = auth.get_brain_data(username)
        
        # Format base information
        base_info = brain_data.get('base', {})
        base_context = ""
        if base_info:
            base_context = f"""
INFORMACIÓN BASE DEL NEGOCIO:
- Rubro: {base_info.get('rubro', 'No especificado')}
- Nombre: {base_info.get('nombre', 'No especificado')}
- Producto/Servicio: {base_info.get('producto', 'No especificado')}
- Precio: ${base_info.get('precio', 'No especificado')}
- Tipo: {base_info.get('tipo', 'No especificado')}
- Meta: {base_info.get('meta', 'No especificado')}
- Presupuesto mensual: ${base_info.get('presupuesto', 'No especificado')}
- Plataformas: {base_info.get('plataforma', 'No especificado')}
- Modalidad de venta: {base_info.get('modalidad_venta', 'No especificado')}
"""
            if base_info.get('avatar', {}).get('descripcion'):
                base_context += f"\nCLIENTE IDEAL:\n{base_info['avatar']['descripcion']}\n"
        
        # Format insights
        insights = brain_data.get('insights', [])
        insights_context = ""
        if insights:
            insights_context = "\n📝 APRENDIZAJES E INSIGHTS RECIENTES:\n"
            # Group by type
            by_type = {}
            for insight in insights[-20:]:  # Last 20 insights
                tipo = insight.get('tipo', 'otro')
                if tipo not in by_type:
                    by_type[tipo] = []
                by_type[tipo].append(insight)
            
            # Format by type
            type_labels = {
                'mensaje_ganador': '✅ Mensajes que funcionan',
                'objecion': '🛡️ Objeciones detectadas',
                'resultado': '📊 Resultados obtenidos',
                'recomendacion': '💡 Recomendaciones clave'
            }
            
            for tipo, items in by_type.items():
                if items:
                    insights_context += f"\n{type_labels.get(tipo, tipo.upper())}:\n"
                    for item in items[-5:]:  # Last 5 of each type
                        insights_context += f"- {item.get('contenido', '')[:150]}...\n"
        
        # Get manual context
        manual_context = brain_data.get('contexto_manual', '')
        
        # Build comprehensive prompt
        contextual_prompt = f"""
Eres MiPymes IA, un asistente de marketing experto que conoce profundamente este negocio.

{base_context}

{insights_context}

CONTEXTO ADICIONAL DEL USUARIO:
{manual_context if manual_context else 'No hay contexto adicional.'}

PREGUNTA DEL USUARIO:
{prompt}

INSTRUCCIONES:
- Usa TODA la información del negocio para dar respuestas ultra personalizadas
- Menciona insights y aprendizajes recientes cuando sean relevantes
- Sé específico con el rubro, producto y tipo de cliente
- Da ejemplos concretos basados en lo que ya sabes del negocio
- Si detectas información valiosa en la pregunta del usuario, será guardada automáticamente
"""
        
        # Generate response
        with st.spinner("🧠 Pensando..."):
            response = st.session_state.ai_agent.chat(contextual_prompt)
        
        # Add assistant message
        st.session_state.brain_chat_history.append({"role": "assistant", "content": response})
        
        # Save to database
        auth.save_section_history(username, 'cerebro', "assistant", response)
        
        # Enrich brain from interaction
        try:
            insights_added = auth.enrich_brain_from_interaction(username, 'cerebro', prompt, response)
            if insights_added > 0:
                print(f"✅ Added {insights_added} insight(s) to brain from cerebro")
        except Exception as e:
            print(f"Warning: Failed to enrich brain: {e}")
        
        st.rerun()
