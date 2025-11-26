import streamlit as st
import auth
from ai_logic import MarketingStrategist
from pdf_gen import generate_pdf
import time
from datetime import datetime, timedelta

# Page Config
st.set_page_config(page_title="SG MiPymes IA", page_icon="🚀", layout="wide")

# Session State Initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'strategy_result' not in st.session_state:
    st.session_state.strategy_result = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ai_agent' not in st.session_state:
    st.session_state.ai_agent = None

def login_page():
    st.title("🔐 SG MiPymes IA - Login")
    
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")
        
        if submit:
            user = auth.login_user(username, password)
            if user:
                if not user['is_active']:
                    st.error("Tu cuenta no está activa. Contacta a soporte.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.ai_agent = MarketingStrategist()
                    st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

def admin_panel():
    st.title("🛠️ Panel de Administración")
    
    # Logout button at the top
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.step = 1
        st.rerun()
    
    st.divider()
    st.subheader("Gestión de Usuarios")
    
    # Create User
    with st.expander("Crear Nuevo Usuario"):
        with st.form("create_user_form"):
            new_user = st.text_input("Nuevo Usuario")
            new_pass = st.text_input("Contraseña", type="password")
            new_business = st.text_input("Nombre del Negocio")
            create_submit = st.form_submit_button("Crear Usuario")
            
            if create_submit:
                if auth.create_user(new_user, new_pass, new_business, is_active=True):
                    st.success(f"Usuario {new_user} creado exitosamente.")
                    st.rerun()
                else:
                    st.error("Error al crear usuario. El nombre puede ya existir.")
    
    # List Users
    users = auth.get_all_users()
    
    for index, row in users.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{row['username']}**")
        with col2:
            st.write(row['business_name'])
        with col3:
            status = "Activo" if row['is_active'] else "Inactivo"
            st.write(status)
        with col4:
            if st.button("Cambiar Estado", key=f"btn_{row['username']}"):
                auth.toggle_user_active(row['username'], row['is_active'])
                st.rerun()
    
    # Admin subscription extension controls
    st.divider()
    st.subheader("Extender Suscripción de Usuario")
    
    with st.form("extend_subscription_form"):
        usernames = users['username'].tolist()
        selected_user = st.selectbox("Seleccionar Usuario", usernames)
        days = st.selectbox("Días a añadir", [30, 90, 180, 360])
        extend_submit = st.form_submit_button("Extender Suscripción")
        
        if extend_submit:
            auth.extend_subscription(selected_user, days)
            st.success(f"Suscripción de {selected_user} extendida {days} días.")
            st.rerun()

def wizard_page():
    st.title("🚀 Generador MiPymesIA")
    st.caption("Estrategias de Marketing y de Publicidad")
    
    if st.session_state.step == 1:
        st.subheader("📋 Diagnóstico y Contexto")
        
        # Add custom CSS for better styling
        st.markdown("""
        <style>
        .stButton>button {
            border-radius: 10px;
            font-weight: bold;
        }
        .section-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #3498db;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.form("diagnosis_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏢 Información del Negocio")
                rubro = st.text_input("📌 Rubro del Negocio", placeholder="ej: Gastronomía, Moda, Tecnología")
                nombre = st.text_input("✨ Nombre del Negocio", placeholder="ej: Mi Empresa")
                tipo = st.selectbox("🏪 Tipo de Negocio", ["Físico", "Tienda Online", "Dropshipping", "Productos Digitales", "Servicios"])
            
            with col2:
                st.markdown("### 🎯 Objetivos y Presupuesto")
                producto = st.text_input("⭐ Producto/Servicio Estrella", placeholder="ej: Curso de Marketing Digital")
                precio = st.number_input("💵 Precio del Producto/Servicio (USD) - Opcional", min_value=0.0, value=0.0, step=1.0)
                meta = st.selectbox("📈 Meta Actual", ["Aumentar Ventas", "Ganar Seguidores", "Reconocimiento de Marca", "Generar Leads"])
                presupuesto = st.slider("💰 Presupuesto Mensual (USD)", min_value=100, max_value=1000, value=300, step=50)
                modalidad = st.selectbox("💳 Modalidad de Venta", ["Mayoría Contado", "Mayoría Crédito", "Mensual / SaaS"])
            
            st.markdown("### 📱 Plataformas de Publicidad")
            plataforma = st.multiselect(
                "¿Dónde deseas hacer publicidad?",
                ["Facebook/Instagram", "Google Ads"],
                default=["Facebook/Instagram"]
            )
            
            generate = st.form_submit_button("🧠 Generar Estrategia Completa", use_container_width=True, type="primary")
            
            if generate:
                if not rubro or not nombre or not producto or not plataforma:
                    st.warning("⚠️ Por favor completa todos los campos obligatorios.")
                else:
                    # Check subscription status and request limits
                    user = st.session_state.user
                    
                    # Check if subscription is expired
                    if user.get('expiration_date'):
                        exp_date = datetime.fromisoformat(user['expiration_date'])
                        if datetime.now() > exp_date:
                            st.error("❌ Tu suscripción ha expirado. Contacta a soporte para renovar.")
                            st.stop()
                    
                    # Check daily request limit
                    can_request, remaining = auth.increment_request_count(user['username'])
                    if not can_request:
                        st.error(f"❌ Has alcanzado el límite diario de 20 consultas. Quedan {remaining} consultas disponibles hoy.")
                        st.stop()
                    
                    # Show loading overlay
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown("""
                    <style>
                    .loading-overlay {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.8);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        z-index: 9999;
                        color: white;
                        font-size: 24px;
                        font-weight: bold;
                    }
                    </style>
                    <div class="loading-overlay">
                        <div>🧠 Generando tu estrategia profesional...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        business_info = {
                            "rubro": rubro,
                            "nombre": nombre,
                            "tipo": tipo,
                            "producto": producto,
                            "precio": precio if precio > 0 else None,
                            "meta": meta,
                            "presupuesto": presupuesto,
                            "presupuesto_diario": round(presupuesto/30, 2),
                            "plataforma": ", ".join(plataforma),
                            "modalidad_venta": modalidad,
                            "sistema_actual": "No especificado"
                        }
                        result = st.session_state.ai_agent.generate_strategy(business_info)
                        st.session_state.strategy_result = result
                        st.session_state.business_info = business_info
                        st.session_state.step = 3
                        
                        # Update user session with new request count
                        st.session_state.user['requests_today'] = user.get('requests_today', 0) + 1
                        
                        loading_placeholder.empty()
                        st.rerun()
                    except Exception as e:
                        loading_placeholder.empty()
                        st.error(f"Ocurrió un error: {e}")

    elif st.session_state.step == 2:
        st.session_state.step = 3
        st.rerun()

    elif st.session_state.step == 3:
        # Helper to parse sections
        def get_section_content(text, section_name):
            try:
                start_marker = f"<<<SECTION_START: {section_name}>>>"
                parts = text.split(start_marker)
                if len(parts) > 1:
                    content = parts[1].split("<<<SECTION_START:")[0].strip()
                    return content
                return "Contenido no disponible."
            except Exception:
                return "Error al cargar contenido."

        strategy_text = st.session_state.strategy_result
        
        # Sidebar Navigation
        with st.sidebar:
            # Logout button BEFORE "Resultados"
            if st.button("🚪 SALIR", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.step = 1
                st.rerun()
            
            st.markdown("---")
            
            # Display subscription info
            user = st.session_state.user
            if user.get('expiration_date'):
                exp_date = datetime.fromisoformat(user['expiration_date'])
                days_remaining = (exp_date - datetime.now()).days
                
                # Color coding
                if days_remaining > 10:
                    color = "green"
                elif days_remaining >= 4:
                    color = "orange"
                else:
                    color = "red"
                
                st.markdown(f"**Días restantes:** :{color}[{days_remaining}]")
            
            # Display request count
            requests_today = user.get('requests_today', 0)
            remaining_requests = 20 - requests_today
            st.markdown(f"**Consultas disponibles:** {remaining_requests}/20")
            
            # Calculate hours until midnight (renewal time)
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            hours_until_renewal = int((midnight - now).total_seconds() / 3600)
            st.caption(f"Se renueva en {hours_until_renewal} horas")
            
            # Payment link
            st.markdown("[💳 Pagar Suscripción](https://wa.link/qf8pf2)")
            
            st.markdown("---")
            st.header("Resultados")
            selected_section = st.radio(
                "Navegar a:",
                ["1. Avatars de Cliente", "2. Embudo de Contenido", "3. Estrategia de Ads", 
                 "4. Flujo WhatsApp", "5. Manejo Objeciones", "6. Acciones Diarias", "7. Métricas"],
                label_visibility="collapsed"
            )
            
            # Nueva Estrategia button below Results
            if st.button("🔄 Nueva Estrategia", use_container_width=True, type="primary"):
                st.session_state.step = 1
                st.rerun()


        # 1. AVATARS
        if "Avatars" in selected_section:
            st.subheader("👤 1. Avatar de Cliente Ideal")
            content = get_section_content(strategy_text, "AVATAR")
            
            # Parse Avatar content for better display
            lines = content.split('\n')
            avatar_data = {}
            
            for line in lines:
                if "Nombre:" in line:
                    avatar_data["Nombre"] = line.split("Nombre:")[1].strip()
                elif "Dolor Principal:" in line:
                    avatar_data["Dolor"] = line.split("Dolor Principal:")[1].strip()
                elif "Objeciones Típicas:" in line:
                    avatar_data["Objeciones"] = line.split("Objeciones Típicas:")[1].strip()
                elif "Vocabulario:" in line:
                    avatar_data["Vocabulario"] = line.split("Vocabulario:")[1].strip()
            
            # Display in cards if parsing worked, otherwise raw
            if len(avatar_data) >= 3:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="section-card">
                        <h4>👤 {avatar_data.get('Nombre', 'Avatar')}</h4>
                        <p><strong>😖 Dolor Principal:</strong><br>{avatar_data.get('Dolor', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="section-card">
                        <p><strong>🛡️ Objeciones:</strong><br>{avatar_data.get('Objeciones', '')}</p>
                        <p><strong>🗣️ Vocabulario:</strong><br>{avatar_data.get('Vocabulario', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(content)

        # 2. EMBUDO DE CONTENIDO
        elif "Embudo" in selected_section:
            st.subheader("📢 2. Embudo de Contenido Semanal")
            
            tab1, tab2, tab3 = st.tabs(["TOFU (Descubrimiento)", "MOFU (Consideración)", "BOFU (Venta)"])
            
            with tab1:
                st.markdown("### 🎣 TOFU: Atracción")
                st.markdown(get_section_content(strategy_text, "EMBUDO_TOFU"))
            with tab2:
                st.markdown("### 🧠 MOFU: Educación")
                st.markdown(get_section_content(strategy_text, "EMBUDO_MOFU"))
            with tab3:
                st.markdown("### 💰 BOFU: Cierre")
                st.markdown(get_section_content(strategy_text, "EMBUDO_BOFU"))

        # 3. ADS STRATEGY
        elif "Ads" in selected_section:
            st.subheader("💰 3. Estrategia de Publicidad Pagada")
            st.info(f"Presupuesto Mensual: ${st.session_state.business_info.get('presupuesto')} USD")
            
            tab_frio, tab_tibio, tab_caliente = st.tabs(["❄️ Tráfico Frío", "🔥 Tráfico Tibio", "🌋 Tráfico Caliente"])
            
            with tab_frio:
                st.markdown(get_section_content(strategy_text, "ADS_FRIO"))
            with tab_tibio:
                st.markdown(get_section_content(strategy_text, "ADS_TIBIO"))
            with tab_caliente:
                st.markdown(get_section_content(strategy_text, "ADS_CALIENTE"))

        # 4. WHATSAPP FLOW
        elif "WhatsApp" in selected_section:
            st.subheader("💬 4. Flujo de Cierre por WhatsApp (7 Días)")
            
            tabs = st.tabs(["Día 1", "Día 2", "Día 3", "Día 4", "Día 5", "Día 6", "Día 7"])
            for i, tab in enumerate(tabs):
                with tab:
                    st.markdown(get_section_content(strategy_text, f"WHATSAPP_DIA{i+1}"))

        # 5. OBJECIONES
        elif "Objeciones" in selected_section:
            st.subheader("🛡️ 5. Manejo de Objeciones")
            
            tabs = st.tabs(["Costo", "Tiempo", "Personal", "Integración", "Miedo"])
            obj_keys = ["COSTO", "TIEMPO", "PERSONAL", "INTEGRACION", "MIEDO"]
            
            for tab, key in zip(tabs, obj_keys):
                with tab:
                    st.markdown(get_section_content(strategy_text, f"OBJECION_{key}"))

        # 6. ACCIONES DIARIAS
        elif "Acciones" in selected_section:
            st.subheader("✅ 6. Checklist de Acciones Diarias")
            content = get_section_content(strategy_text, "ACCIONES_DIARIAS")
            st.success("🔥 Rutina de Alto Rendimiento para vender todos los días.")
            st.markdown(content)

        # 7. METRICAS (WITHOUT DEMOS)
        elif "Métricas" in selected_section:
            st.subheader("📈 7. Métricas y Optimización")
            content = get_section_content(strategy_text, "METRICAS")
            
            # Parse Metrics - REMOVED "Demos" tab
            metric_tabs = st.tabs(["CPL", "Tasa Cierre", "Conversión", "Engagement"])
            metric_keywords = ["Costo por Lead", "Tasa de Cierre", "Tasa de Conversión", "Engagement"]
            
            # Split by ### headers
            sections = content.split('###')
            
            for tab, keyword in zip(metric_tabs, metric_keywords):
                with tab:
                    found = False
                    for section in sections:
                        if keyword.lower() in section.lower():
                            st.markdown(section)
                            found = True
                    if not found:
                        st.write("Información detallada en el resumen general.")
            
            with st.expander("Ver Resumen Completo de Métricas"):
                st.markdown(content)

        # Footer Actions
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            # PDF Button Hidden as requested
            pass
        with col2:
            if st.button("🔄 Nueva Estrategia", use_container_width=True):
                st.session_state.step = 1
                st.rerun()

        # Chat
        st.divider()
        st.subheader("💬 Asistente MiPymes IA")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Pregunta sobre tu estrategia..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Pensando..."):
                response = st.session_state.ai_agent.chat(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

# Main Logic
if not st.session_state.authenticated:
    login_page()
else:
    # Sidebar Header (Always visible)
    with st.sidebar:
        st.title("Generador MiPymesIA")
        st.caption("Estrategias de Marketing y de Publicidad")
        st.write(f"Hola, **{st.session_state.user['username']}**")
    
    # Page Routing
    if st.session_state.user['is_admin']:
        with st.sidebar:
             page = st.radio("Modo", ["Generador", "Admin Panel"])
    else:
        page = "Generador"

    if page == "Generador":
        wizard_page()
    elif page == "Admin Panel":
        admin_panel()
