import streamlit as st
import auth

def chat_page():
    """
    MiPymes IA - Chat with full brain functionality.
    Uses enriched brain data for ultra-personalized responses.
    """
    st.title("💬 MiPymes IA")
    st.caption("Consultor Estratégico: Consultas basadas en tus datos reales y objetivos")
    
    user = st.session_state.get('user')
    if not user:
        st.error("No se encontró información del usuario. Por favor inicia sesión.")
        st.stop()
        
    username = user.get('username')
    
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
        
        # Get all user strategies to extract buyer personas
        all_estrategias = auth.get_all_estrategias(username)
        
        # Extract REAL business information from Cerebro
        base_context = ""
        
        # Get rubros (industries)
        rubros = brain_data.get('rubros', [])
        if rubros:
            rubros_text = ", ".join([r.get('nombre', '') for r in rubros if r.get('nombre')])
            base_context += f"\n🏢 RUBROS: {rubros_text}\n"
        
        # Get tipos de venta (sales types)
        tipos_venta = brain_data.get('tipos_venta', [])
        if tipos_venta:
            tipos_text = ", ".join([t.get('nombre', '') for t in tipos_venta if t.get('nombre')])
            base_context += f"💼 TIPOS DE VENTA: {tipos_text}\n"
        
        # Get servicios y productos
        servicios = brain_data.get('servicios', [])
        if servicios:
            base_context += f"\n📦 SERVICIOS Y PRODUCTOS ({len(servicios)} total):\n"
            for servicio in servicios[:10]:  # Max 10
                nombre = servicio.get('nombre', '')
                descripcion = servicio.get('descripcion', '')
                if nombre:
                    base_context += f"  • {nombre}"
                    if descripcion:
                        base_context += f": {descripcion[:100]}"
                    base_context += "\n"
        
        # Get base info if available (from form)
        base_info = brain_data.get('base', {})
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
        
        # Extract buyer personas from all strategies
        buyer_personas_context = ""
        if all_estrategias:
            avatares = []
            for estrategia in all_estrategias:
                avatar_content = estrategia.get('avatar', '')
                if avatar_content and len(avatar_content) > 50:  # Only if has meaningful content
                    estrategia_nombre = estrategia.get('producto', 'Estrategia')
                    avatares.append(f"\n📊 AVATAR DE '{estrategia_nombre}':\n{avatar_content[:500]}...")  # First 500 chars
            
            if avatares:
                buyer_personas_context = "\n\n🎯 BUYER PERSONAS CONOCIDOS (de tus estrategias):\n" + "\n".join(avatares[:3])  # Max 3 avatares
        
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
Eres MiPymes IA, un asistente de marketing experto que ayuda al usuario con su negocio.

IMPORTANTE SOBRE EL TONO:
- Habla en SEGUNDA PERSONA sobre el negocio del usuario (TU negocio, TUS servicios, TUS clientes)
- NO hables en primera persona como si fueras el negocio (NO digas "ofrezco", di "ofreces")
- SOLO cuando el usuario te saluda por primera vez (hola, buenos días, etc.), preséntate: "¡Hola! Soy MiPymes IA, tu asistente de marketing. ¿En qué puedo ayudarte hoy?"
- En las demás respuestas, NO te presentes, ve directo al punto
- Mantén un tono amigable, profesional y directo

{base_context}
{buyer_personas_context}

{insights_context}

CONTEXTO ADICIONAL DEL USUARIO:
{manual_context if manual_context else 'No hay contexto adicional.'}

PREGUNTA DEL USUARIO:
{prompt}

INSTRUCCIONES CRÍTICAS:
- USA TODA la información del negocio que tienes arriba para dar respuestas ULTRA PERSONALIZADAS
- NUNCA digas que no tienes información del negocio - YA LA TIENES
- Menciona el rubro, productos/servicios específicos cuando sea relevante
- Usa los buyer personas conocidos para dar sugerencias más precisas
- Menciona insights y aprendizajes recientes cuando sean relevantes
- Da ejemplos concretos basados en lo que ya sabes del negocio
- Sé específico y accionable, no genérico
- NO agregues secciones de "Recomendaciones" al final a menos que el usuario las pida explícitamente
- Responde de forma directa y concisa sin agregar consejos extra no solicitados
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
