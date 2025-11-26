import streamlit as st
import auth
from ai_logic import MarketingStrategist
from pdf_gen import generate_pdf
import time
from datetime import datetime, timedelta
import urllib.parse

# Page Config
st.set_page_config(page_title="Generador MiPymesIA", page_icon="🚀", layout="wide")

# Prevent accidental page refresh - show warning
st.markdown("""
<script>
window.addEventListener('beforeunload', function (e) {
    // Only show warning if user is authenticated
    if (window.location.pathname !== '/') {
        e.preventDefault();
        e.returnValue = '';
        return '¿Estás seguro de que quieres salir? Se perderá el historial de chat.';
    }
});
</script>
""", unsafe_allow_html=True)

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
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def load_markdown_file(filepath):
    """Load markdown content from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Contenido no disponible."

def show_static_page(title, filepath):
    """Display a static markdown page with modern, minimalist design"""
    # Custom CSS for modern design
    st.markdown("""
    <style>
    /* Modern Typography */
    .main h1 {
        font-size: 2.5em;
        font-weight: 700;
        color: #1a5276;
        margin-bottom: 0.5em;
        letter-spacing: -0.02em;
    }
    .main h2 {
        font-size: 1.8em;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        border-left: 4px solid #3498db;
        padding-left: 15px;
    }
    .main h3 {
        font-size: 1.3em;
        font-weight: 600;
        color: #34495e;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
    }
    .main p {
        font-size: 1.05em;
        line-height: 1.8;
        color: #4a5568;
        margin-bottom: 1em;
    }
    .main ul, .main ol {
        font-size: 1.05em;
        line-height: 1.8;
        color: #4a5568;
        margin-left: 1.5em;
    }
    .main li {
        margin-bottom: 0.5em;
    }
    /* Card-like sections */
    .content-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    /* Accent colors */
    .highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Top navigation bar
    col_logo, col_spacer, col_login = st.columns([2, 6, 2])
    with col_logo:
        st.markdown("### 🚀 Generador MiPymesIA")
    with col_login:
        if st.button("🔐 Iniciar Sesión", use_container_width=True, type="primary", key="login_static"):
            st.session_state.page = 'login_form'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Page title with modern styling
    st.markdown(f"""
    <div style='text-align: center; padding: 30px 0;'>
        <h1 style='font-size: 2.8em; color: #1a5276; margin-bottom: 10px;'>{title}</h1>
        <div style='width: 80px; height: 4px; background: linear-gradient(90deg, #3498db, #9b59b6); margin: 0 auto; border-radius: 2px;'></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and display content in a container
    content = load_markdown_file(filepath)
    
    # Wrap content in a max-width container for better readability
    st.markdown("""
    <div style='max-width: 900px; margin: 0 auto; padding: 20px;'>
    """, unsafe_allow_html=True)
    
    st.markdown(content)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Modern footer navigation
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer navigation buttons
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("📋 Términos", use_container_width=True, key="terms_footer"):
            st.session_state.page = 'terms'
            st.rerun()
    with col_b:
        if st.button("🔒 Privacidad", use_container_width=True, key="privacy_footer"):
            st.session_state.page = 'privacy'
            st.rerun()
    with col_c:
        if st.button("💎 Precios", use_container_width=True, key="pricing_footer"):
            st.session_state.page = 'pricing'
            st.rerun()
    with col_d:
        if st.button("⬅️ Inicio", use_container_width=True, key="back_footer"):
            st.session_state.page = 'login'
            st.rerun()
    
    show_footer()

def show_footer():
    """Display minimalist footer"""
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee;'>
        Generador MiPymes I.A. Todos los derechos © 2025 | By <a href="https://www.alphasoft.com.py/" target="_blank" style="color: #666; text-decoration: none;">Alpha Software</a>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    # Top navigation bar with login button
    col_logo, col_spacer, col_login = st.columns([2, 6, 2])
    with col_logo:
        st.markdown("### 🚀 Generador MiPymesIA")
    with col_login:
        if st.button("🔐 Iniciar Sesión", use_container_width=True, type="primary", key="open_login"):
            st.session_state.page = 'login_form'
            st.rerun()
    
    st.divider()
    
    # Hero Section - Compact version
    st.markdown("""
    <div style='text-align: center; padding: 20px 0 15px 0;'>
        <h1 style='font-size: 2.2em; color: #1a5276; margin-bottom: 8px;'>Estrategias de Marketing Profesionales</h1>
        <h3 style='color: #5d6d7e; font-size: 1.1em; margin-bottom: 8px;'>Impulsadas por Inteligencia Artificial</h3>
        <p style='font-size: 1em; margin-top: 10px;'>Genera estrategias completas de marketing y publicidad para tu negocio en minutos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("## ✨ ¿Qué Obtendrás?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 👤 Avatar de Cliente
        Perfil detallado de tu cliente ideal con dolores, objeciones y vocabulario específico.
        
        ### 📢 Embudo de Contenido
        Plan semanal de contenido TOFU, MOFU y BOFU para redes sociales.
        """)
    
    with col2:
        st.markdown("""
        ### 💰 Estrategia de Ads
        Campañas segmentadas para tráfico frío, tibio y caliente con presupuesto optimizado.
        
        ### 💬 Flujo de WhatsApp
        Secuencia de 7 días para cerrar ventas por WhatsApp.
        """)
    
    with col3:
        st.markdown("""
        ### 🛡️ Manejo de Objeciones
        Respuestas profesionales para las 5 objeciones más comunes.
        
        ### 📈 Métricas Clave
        KPIs y acciones de optimización para mejorar resultados.
        """)
    
    st.divider()
    
    # Video Section
    col_video_left, col_video, col_video_right = st.columns([1, 2, 1])
    with col_video:
        st.markdown("""
        <div style="padding:56.25% 0 0 0;position:relative;">
        <iframe src="https://player.vimeo.com/video/1140470002?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479&amp;title=0&amp;byline=0&amp;portrait=0" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Video Tutorial"></iframe>
        </div>
        <script src="https://player.vimeo.com/api/player.js"></script>
        """, unsafe_allow_html=True)
    
    st.divider()
    

    
    # Footer Links
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("📋 Términos de Uso", use_container_width=True):
            st.session_state.page = 'terms'
            st.rerun()
    with col_b:
        if st.button("🔒 Privacidad", use_container_width=True):
            st.session_state.page = 'privacy'
            st.rerun()
    with col_c:
        if st.button("💎 Ver Todos los Precios", use_container_width=True):
            st.session_state.page = 'pricing'
            st.rerun()
    with col_d:
        if st.button("✨ Quiero Suscribirme", use_container_width=True, type="primary"):
            st.session_state.page = 'register'
            st.rerun()
    
    show_footer()

def login_form_page():
    """Clean login page similar to registration"""
    st.title("🔐 Iniciar Sesión")
    
    st.info("Ingresa tus credenciales para acceder a tu cuenta")
    
    with st.form("login_form"):
        username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
        password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
        submit = st.form_submit_button("Ingresar", use_container_width=True, type="primary")
        
        if submit:
            if not username or not password:
                st.warning("⚠️ Por favor completa todos los campos.")
            else:
                user = auth.login_user(username, password)
                
                if user and isinstance(user, dict):
                    if user.get('error') == 'locked':
                        remaining = user.get('remaining_seconds', 300)
                        minutes = remaining // 60
                        seconds = remaining % 60
                        st.error(f"🔒 Cuenta bloqueada por intentos fallidos. Intenta de nuevo en {minutes}m {seconds}s.")
                    elif not user.get('is_active'):
                        st.error("❌ Tu cuenta no está activa. Contacta a soporte.")
                        admin_phone = "595994209224"
                        message = f"🔑 Solicitud de activación de cuenta\n\nUsuario: {username}"
                        whatsapp_url = f"https://wa.me/{admin_phone}?text={urllib.parse.quote(message)}"
                        st.info(f"📱 Puedes contactar directamente por WhatsApp:")
                        st.markdown(f"[Abrir WhatsApp]({whatsapp_url})")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.ai_agent = MarketingStrategist(business_context=user.get('business_profile', ''))
                        st.success("✅ Inicio de sesión exitoso!")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    
    st.divider()
    
    col_forgot, col_register, col_back = st.columns(3)
    with col_forgot:
        if st.button("🔑 Olvidé mi contraseña", use_container_width=True):
            st.session_state.page = 'forgot_password'
            st.rerun()
    with col_register:
        if st.button("✨ Registrarme", use_container_width=True, type="secondary"):
            st.session_state.page = 'register'
            st.rerun()
    with col_back:
        if st.button("⬅️ Volver al Inicio", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    
    show_footer()

def registration_page():
    st.title("✨ Crear Cuenta - Prueba Gratuita 7 Días")
    
    st.info("🎁 Obtén acceso completo por 7 días con 5 solicitudes diarias. ¡Sin tarjeta de crédito!")
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Usuario (Alias)", help="Elige un nombre de usuario único")
            email = st.text_input("Correo Electrónico", help="Necesario para recuperación de contraseña")
        
        with col2:
            password = st.text_input("Contraseña", type="password")
            password_confirm = st.text_input("Confirmar Contraseña", type="password")
        
        business_name = st.text_input("Nombre del Negocio (Opcional)")
        
        agree = st.checkbox("Acepto los Términos de Uso y Política de Privacidad")
        
        submit = st.form_submit_button("🚀 Crear Cuenta Gratuita", use_container_width=True, type="primary")
        
        if submit:
            if not username or not email or not password or not password_confirm:
                st.warning("⚠️ Por favor completa todos los campos obligatorios.")
            elif password != password_confirm:
                st.error("❌ Las contraseñas no coinciden.")
            elif not agree:
                st.warning("⚠️ Debes aceptar los términos para continuar.")
            elif '@' not in email:
                st.error("❌ Por favor ingresa un correo electrónico válido.")
            else:
                # Create user with 7-day trial
                success = auth.create_user(username, password, email, business_name)
                if success:
                    st.success("✅ ¡Cuenta creada exitosamente! Ya puedes iniciar sesión.")
                    st.balloons()
                    time.sleep(2)
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error("❌ El usuario ya existe. Intenta con otro nombre.")
    
    st.divider()
    if st.button("⬅️ Volver al Login"):
        st.session_state.page = 'login'
        st.rerun()
    
    show_footer()

def forgot_password_page():
    st.title("🔑 Recuperar Contraseña")
    
    st.info("Ingresa tu usuario y correo electrónico. Si coinciden, enviaremos una notificación al administrador para restablecer tu contraseña.")
    
    with st.form("forgot_password_form"):
        username = st.text_input("Usuario (Alias)")
        email = st.text_input("Correo Electrónico Registrado")
        
        submit = st.form_submit_button("Solicitar Recuperación", use_container_width=True, type="primary")
        
        if submit:
            if not username or not email:
                st.warning("⚠️ Por favor completa todos los campos.")
            else:
                # Validate username and email combination
                if auth.request_password_reset(username, email):
                    # Send WhatsApp notification to admin
                    admin_phone = "595994209224"
                    message = f"🔑 Solicitud de cambio de contraseña\n\nUsuario: {username}\nCorreo: {email}"
                    whatsapp_url = f"https://wa.me/{admin_phone}?text={urllib.parse.quote(message)}"
                    
                    st.success("✅ Datos encontrados!")
                    st.info(f"📱 Puedes contactar directamente por WhatsApp:")
                    st.markdown(f"[Abrir WhatsApp]({whatsapp_url})")
                else:
                    st.error("❌ No se encontró la combinación de usuario/correo en el sistema.")
    
    st.divider()
    if st.button("⬅️ Volver al Login"):
        st.session_state.page = 'login'
        st.rerun()
    
    show_footer()

def change_password_page():
    st.title("🔐 Cambiar Contraseña")
    
    with st.form("change_password_form"):
        old_password = st.text_input("Contraseña Actual", type="password")
        new_password = st.text_input("Nueva Contraseña", type="password")
        confirm_password = st.text_input("Confirmar Nueva Contraseña", type="password")
        
        submit = st.form_submit_button("Cambiar Contraseña", use_container_width=True, type="primary")
        
        if submit:
            if not old_password or not new_password or not confirm_password:
                st.warning("⚠️ Por favor completa todos los campos.")
            elif new_password != confirm_password:
                st.error("❌ Las contraseñas nuevas no coinciden.")
            elif len(new_password) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres.")
            else:
                username = st.session_state.user['username']
                if auth.change_password(username, old_password, new_password):
                    st.success("✅ Contraseña cambiada exitosamente!")
                    time.sleep(1)
                    st.session_state.page = 'main'
                    st.rerun()
                else:
                    st.error("❌ La contraseña actual es incorrecta.")
    
    st.divider()
    if st.button("⬅️ Volver"):
        st.session_state.page = 'main'
        st.rerun()
    
    show_footer()

def admin_panel():
    st.title("🛠️ Panel de Administración")
    
    # Logout button at the top
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.step = 1
        st.session_state.page = 'login'
        st.rerun()
    
    st.divider()
    
    # Search users
    st.subheader("🔍 Buscar Usuarios")
    search_query = st.text_input("Buscar por usuario o correo", placeholder="Ingresa usuario o email...")
    
    if search_query:
        users = auth.search_users(search_query)
    else:
        users = auth.get_all_users()
    
    st.caption(f"Mostrando {len(users)} usuario(s)")
    
    # Create User
    with st.expander("➕ Crear Nuevo Usuario"):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_user = st.text_input("Usuario")
                new_email = st.text_input("Correo Electrónico")
                new_business = st.text_input("Nombre del Negocio")
            with col2:
                new_pass = st.text_input("Contraseña", type="password")
                daily_limit = st.selectbox("Solicitudes Diarias", [5, 10, 15, 20, 25, 30], index=3)
            
            create_submit = st.form_submit_button("Crear Usuario", use_container_width=True)
            
            if create_submit:
                if not new_user or not new_email or not new_pass:
                    st.warning("⚠️ Usuario, email y contraseña son obligatorios.")
                elif '@' not in new_email:
                    st.error("❌ Ingresa un correo válido.")
                else:
                    if auth.create_user(new_user, new_pass, new_email, new_business, is_active=True, daily_request_limit=daily_limit):
                        st.success(f"✅ Usuario {new_user} creado exitosamente.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error al crear usuario. El nombre puede ya existir.")
    
    # List Users
    st.divider()
    st.subheader("👥 Gestión de Usuarios")
    
    for index, row in users.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])
            with col1:
                st.write(f"**{row['username']}**")
            with col2:
                st.write(row['business_name'] or "-")
            with col3:
                st.write(row['email'] or "-")
            with col4:
                st.write(f"{row['daily_request_limit']}/día")
            with col5:
                status = "✅ Activo" if row['is_active'] else "❌ Inactivo"
                st.write(status)
            with col6:
                if st.button("Cambiar", key=f"btn_{row['username']}"):
                    auth.toggle_user_active(row['username'], row['is_active'])
                    st.rerun()
            st.divider()
    
    # Admin subscription extension controls
    st.divider()
    st.subheader("📅 Extender Suscripción de Usuario")
    
    with st.form("extend_subscription_form"):
        all_users = auth.get_all_users()
        usernames = all_users['username'].tolist()
        selected_user = st.selectbox("Seleccionar Usuario", usernames)
        days = st.selectbox("Días a añadir", [30, 90, 180, 360])
        extend_submit = st.form_submit_button("Extender Suscripción", use_container_width=True)
        
        if extend_submit:
            auth.extend_subscription(selected_user, days)
            st.success(f"✅ Suscripción de {selected_user} extendida {days} días.")
            time.sleep(1)
            st.rerun()

def section_chat(section_name, section_content, section_key):
    """
    Contextual chat for each strategy section.
    Allows users to expand and discuss specific parts of their strategy.
    """
    st.divider()
    
    # Initialize section-specific chat history
    chat_key = f"chat_{section_key}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Expander for chat
    with st.expander(f"💬 Ampliar y Profundizar en {section_name}", expanded=False):
        st.caption("Pregunta sobre esta sección específica para obtener más detalles, ejemplos o ideas.")
        
        # Display chat history for this section
        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        prompt = st.chat_input(f"Pregunta sobre {section_name}...", key=f"input_{section_key}")
        
        if prompt:
            # Add user message
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            
            # Create context-aware prompt for AI
            business_context = st.session_state.user.get('business_profile', '')
            business_info = st.session_state.get('business_info', {})
            
            contextual_prompt = f"""
CONTEXTO DE LA SECCIÓN: {section_name}

CONTENIDO ACTUAL DE LA SECCIÓN:
{section_content}

INFORMACIÓN DEL NEGOCIO:
- Rubro: {business_info.get('rubro', 'No especificado')}
- Nombre: {business_info.get('nombre', 'No especificado')}
- Producto: {business_info.get('producto', 'No especificado')}

CONTEXTO DEL CEREBRO DEL NEGOCIO:
{business_context if business_context else 'No hay contexto adicional guardado.'}

PREGUNTA DEL USUARIO:
{prompt}

INSTRUCCIONES:
- Responde ESPECÍFICAMENTE sobre la sección "{section_name}"
- Usa el contenido actual como base para ampliar, dar ejemplos o profundizar
- Mantén coherencia con el rubro y producto del negocio
- Usa el contexto del Cerebro del Negocio para personalizar tu respuesta
- Sé práctico y accionable
"""
            
            # Generate response
            with st.spinner("Pensando..."):
                response = st.session_state.ai_agent.chat(contextual_prompt)
            
            # Add assistant message
            st.session_state[chat_key].append({"role": "assistant", "content": response})
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
                presupuesto = st.slider("💰 Presupuesto Mensual (USD)", min_value=50, max_value=1000, value=150, step=50)
                modalidad = st.selectbox("💳 Modalidad de Venta", ["Mayoría Contado", "Mayoría Crédito", "Mensual / SaaS"])
            
            st.markdown("### 📱 Plataformas de Publicidad")
            plataforma = st.multiselect(
                "¿Dónde deseas hacer publicidad?",
                ["Facebook/Instagram", "Google Ads"],
                default=["Facebook/Instagram"]
            )
            
            st.markdown("### 👤 Buyer Persona (Opcional)")
            buyer_persona = st.text_area(
                "Si ya tienes un perfil de cliente ideal, descríbelo aquí. La IA lo usará como base para expandir el análisis.",
                placeholder="Ejemplo: Mujer de 25-35 años, profesional independiente, interesada en desarrollo personal...",
                height=100
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
                        st.error(f"❌ Has alcanzado el límite diario de {user.get('daily_request_limit', 20)} consultas. Quedan {remaining} consultas disponibles hoy.")
                        st.stop()
                    
                    # Show loading overlay
                    # Modern dynamic loading overlay
                    try:
                        # Load custom loader image
                        import base64
                        def get_base64_image(image_path):
                            with open(image_path, "rb") as img_file:
                                return base64.b64encode(img_file.read()).decode()
                        
                        loader_b64 = get_base64_image("assets/loader.png")
                        
                        overlay_placeholder = st.empty()
                        
                        def update_loader(text, step):
                            overlay_placeholder.markdown(f"""
                            <style>
                            .loading-overlay {{
                                position: fixed;
                                top: 0;
                                left: 0;
                                width: 100%;
                                height: 100%;
                                background: rgba(0, 0, 0, 0.4);
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                z-index: 999999;
                                backdrop-filter: blur(4px);
                            }}
                            .loader-card {{
                                background: white;
                                padding: 40px;
                                border-radius: 20px;
                                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                                text-align: center;
                                max-width: 400px;
                                width: 90%;
                                animation: popIn 0.3s ease-out;
                            }}
                            @keyframes popIn {{
                                0% {{ transform: scale(0.8); opacity: 0; }}
                                100% {{ transform: scale(1); opacity: 1; }}
                            }}
                            @keyframes spin {{
                                0% {{ transform: rotate(0deg); }}
                                100% {{ transform: rotate(360deg); }}
                            }}
                            .custom-loader {{
                                animation: spin 2s linear infinite;
                                width: 80px;
                                height: 80px;
                                display: block;
                                margin: 0 auto 20px auto;
                            }}
                            .loading-text {{
                                font-size: 1.3em;
                                color: #2c3e50;
                                font-weight: 600;
                                margin-bottom: 8px;
                            }}
                            .step-text {{
                                font-size: 0.9em;
                                color: #7f8c8d;
                                font-weight: 500;
                                letter-spacing: 1px;
                                text-transform: uppercase;
                            }}
                            </style>
                            <div class="loading-overlay">
                                <div class="loader-card">
                                    <img src="data:image/png;base64,{loader_b64}" class="custom-loader">
                                    <div class="loading-text">{text}</div>
                                    <div class="step-text">PASO {step} DE 6</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Step 1
                        update_loader("🚀 Iniciando motor de IA...", 1)
                        time.sleep(0.5)
                        
                        # Step 2
                        update_loader("🔌 Conectando con base de conocimientos...", 2)
                        time.sleep(0.5)
                        
                        # Step 3
                        update_loader("🧠 Analizando perfil del negocio...", 3)
                        time.sleep(0.5)
                        
                        # Step 4
                        update_loader("🔍 Investigando tendencias del mercado...", 4)
                        time.sleep(0.5)
                        
                        # Step 5
                        update_loader("💡 Diseñando estrategia personalizada...", 5)
                        
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
                            "buyer_persona": buyer_persona if buyer_persona else None
                        }
                        
                        # Generate strategy
                        result = st.session_state.ai_agent.generate_strategy(business_info)
                        
                        # Check if result is an error message
                        if result and result.startswith("Error:"):
                            overlay_placeholder.empty()
                            st.error(result)
                            st.warning("💡 **Posible solución:** Verifica que la variable de entorno OPENAI_API_KEY esté configurada en Easypanel.")
                            st.stop()
                        
                        # Step 6
                        update_loader("✨ Finalizando detalles...", 6)
                        time.sleep(1)
                        
                        st.session_state.strategy_result = result
                        st.session_state.business_info = business_info
                        st.session_state.step = 3
                        
                        # Update user session with new request count
                        st.session_state.user['requests_today'] = user.get('requests_today', 0) + 1
                        
                        overlay_placeholder.empty()
                        st.rerun()
                        
                    except Exception as e:
                        if 'overlay_placeholder' in locals():
                            overlay_placeholder.empty()
                        st.error(f"❌ Ocurrió un error: {e}")
                        st.warning("💡 **Posible solución:** Verifica que la variable de entorno OPENAI_API_KEY esté configurada correctamente.")
                        import traceback
                        st.code(traceback.format_exc())


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
            # Display subscription info FIRST
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
            daily_limit = user.get('daily_request_limit', 20)
            remaining_requests = daily_limit - requests_today
            st.markdown(f"**Consultas disponibles:** {remaining_requests}/{daily_limit}")
            
            # Calculate hours until midnight (renewal time)
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            hours_until_renewal = int((midnight - now).total_seconds() / 3600)
            st.caption(f"Se renueva en {hours_until_renewal} horas")
            
            # Payment link
            st.markdown("[💳 Pagar Suscripción](https://wa.link/qf8pf2)")
            
            st.markdown("---")
            
            # RESULTS NAVIGATION
            st.header("Resultados")
            selected_section = st.radio(
                "Navegar a:",
                ["1. Avatars de Cliente", "2. Embudo de Contenido", "3. Estrategia de Ads", 
                 "4. Flujo WhatsApp", "5. Manejo Objeciones", "6. Acciones Diarias", "7. Métricas"],
                label_visibility="collapsed"
            )
            
            # Nueva Estrategia button
            if st.button("🔄 Nueva Estrategia", use_container_width=True, type="primary"):
                st.session_state.step = 1
                st.rerun()
            
            st.markdown("---")
            
            # LOGOUT AND PASSWORD CHANGE AT THE END
            if st.button("🚪 Cerrar Sesión", use_container_width=True, key="logout_results"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.step = 1
                st.session_state.page = 'login'
                st.rerun()
            
            if st.button("🔐 Cambiar Contraseña", use_container_width=True, key="change_pwd_results"):
                st.session_state.page = 'change_password'
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
            
            # Add contextual chat for this section
            section_chat("Avatar de Cliente", content, "avatar")

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
            
            # Add contextual chat for this section
            embudo_content = f"TOFU:\n{get_section_content(strategy_text, 'EMBUDO_TOFU')}\n\nMOFU:\n{get_section_content(strategy_text, 'EMBUDO_MOFU')}\n\nBOFU:\n{get_section_content(strategy_text, 'EMBUDO_BOFU')}"
            section_chat("Embudo de Contenido", embudo_content, "embudo")

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
            
            # Add contextual chat for this section
            ads_content = f"FRÍO:\n{get_section_content(strategy_text, 'ADS_FRIO')}\n\nTIBIO:\n{get_section_content(strategy_text, 'ADS_TIBIO')}\n\nCALIENTE:\n{get_section_content(strategy_text, 'ADS_CALIENTE')}"
            section_chat("Estrategia de Ads", ads_content, "ads")

        # 4. WHATSAPP FLOW
        elif "WhatsApp" in selected_section:
            st.subheader("💬 4. Flujo de Cierre por WhatsApp (7 Días)")
            
            tabs = st.tabs(["Día 1", "Día 2", "Día 3", "Día 4", "Día 5", "Día 6", "Día 7"])
            for i, tab in enumerate(tabs):
                with tab:
                    st.markdown(get_section_content(strategy_text, f"WHATSAPP_DIA{i+1}"))
            
            # Add contextual chat for this section
            whatsapp_content = "\n\n".join([f"DÍA {i+1}:\n{get_section_content(strategy_text, f'WHATSAPP_DIA{i+1}')}" for i in range(7)])
            section_chat("Flujo de WhatsApp", whatsapp_content, "whatsapp")

        # 5. OBJECIONES
        elif "Objeciones" in selected_section:
            st.subheader("🛡️ 5. Manejo de Objeciones")
            
            tabs = st.tabs(["Costo", "Tiempo", "Personal", "Integración", "Miedo"])
            obj_keys = ["COSTO", "TIEMPO", "PERSONAL", "INTEGRACION", "MIEDO"]
            
            for tab, key in zip(tabs, obj_keys):
                with tab:
                    st.markdown(get_section_content(strategy_text, f"OBJECION_{key}"))
            
            # Add contextual chat for this section
            objeciones_content = "\n\n".join([f"{key}:\n{get_section_content(strategy_text, f'OBJECION_{key}')}" for key in obj_keys])
            section_chat("Manejo de Objeciones", objeciones_content, "objeciones")

        # 6. ACCIONES DIARIAS
        elif "Acciones" in selected_section:
            st.subheader("✅ 6. Checklist de Acciones Diarias")
            content = get_section_content(strategy_text, "ACCIONES_DIARIAS")
            st.success("🔥 Rutina de Alto Rendimiento para vender todos los días.")
            st.markdown(content)
            
            # Add contextual chat for this section
            section_chat("Acciones Diarias", content, "acciones")

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
            
            # Add contextual chat for this section
            section_chat("Métricas y Optimización", content, "metricas")

        # Footer Actions
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            # Single PDF Download Button
            try:
                pdf_bytes = generate_pdf(st.session_state.strategy_result, st.session_state.business_info)
                st.download_button(
                    label="📄 Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"estrategia_{st.session_state.business_info.get('nombre', 'negocio').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")
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
    
    show_footer()

def business_brain_page():
    st.title("🧠 Cerebro del Negocio")
    st.markdown("""
    Aquí puedes definir la **personalidad y contexto** de tu negocio. 
    La IA usará esta información para darte respuestas más precisas y alineadas a tu marca.
    """)
    
    current_profile = st.session_state.user.get('business_profile', '')
    
    with st.form("business_profile_form"):
        new_profile = st.text_area(
            "Contexto del Negocio (Prompt Base)", 
            value=current_profile,
            height=300,
            placeholder="Ej: Mi negocio es una panadería artesanal con enfoque en masa madre. Mi tono de voz es cálido y familiar. Mis clientes valoran la calidad sobre el precio..."
        )
        
        submit = st.form_submit_button("💾 Guardar Cerebro", type="primary")
        
        if submit:
            auth.update_business_profile(st.session_state.user['username'], new_profile)
            st.session_state.user['business_profile'] = new_profile
            # Re-initialize AI with new context
            st.session_state.ai_agent = MarketingStrategist(business_context=new_profile)
            st.success("✅ Cerebro actualizado correctamente!")
            time.sleep(1)
            st.rerun()
    
    show_footer()

def chat_page():
    """Modern Claude-style chat interface"""
    
    # Custom CSS for modern chat design
    st.markdown("""
    <style>
    /* Main chat container */
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: transparent;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* User messages */
    [data-testid="stChatMessageContent"] {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 1.5rem;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid="assistant"] {
        background-color: transparent;
    }
    
    /* Input area */
    .stChatInputContainer {
        border-top: 1px solid #e0e0e0;
        padding-top: 1rem;
        background-color: white;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Header styling */
    h1 {
        color: #1a5276;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* Welcome message */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .welcome-card h2 {
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .welcome-card p {
        color: rgba(255,255,255,0.9);
        font-size: 1.05rem;
    }
    
    /* Suggestion chips */
    .suggestion-chip {
        display: inline-block;
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        font-size: 0.9rem;
        color: #333;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggestion-chip:hover {
        background-color: #e0e0e0;
        border-color: #3498db;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("💬 MiPymes IA")
    st.caption("Tu asistente de marketing inteligente")
    
    # Warning about refresh
    if len(st.session_state.get('chat_messages', [])) > 0:
        st.info("💡 **Tip:** Evita recargar la página (F5) para no perder tu historial de conversación.")
    
    # Initialize chat history if not exists
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Welcome message if no chat history
    if len(st.session_state.chat_messages) == 0:
        st.markdown("""
        <div class="welcome-card">
            <h2>👋 ¡Hola! Soy tu asistente de marketing</h2>
            <p>Estoy aquí para ayudarte con estrategias de marketing, publicidad, ventas y todo lo relacionado con hacer crecer tu negocio.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Suggestion chips
        st.markdown("**💡 Prueba preguntarme sobre:**")
        col1, col2, col3 = st.columns(3)
        
        suggestions = [
            "¿Cómo mejorar mis ventas?",
            "Ideas para redes sociales",
            "Estrategia de contenido",
            "Campañas de Facebook Ads",
            "Embudos de venta",
            "Email marketing efectivo"
        ]
        
        for i, suggestion in enumerate(suggestions):
            with [col1, col2, col3][i % 3]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    # Add suggestion to chat
                    st.session_state.chat_messages.append({"role": "user", "content": suggestion})
                    with st.spinner("Pensando..."):
                        response = st.session_state.ai_agent.chat(suggestion)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = st.session_state.ai_agent.chat(prompt)
            st.markdown(response)
        
        # Add assistant message
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Clear chat button in sidebar
    with st.sidebar:
        st.divider()
        if st.button("🗑️ Limpiar Conversación", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()
    
    show_footer()


def pricing_page():
    """Professional pricing page with attractive card design"""
    # Top navigation bar
    col_logo, col_spacer, col_login = st.columns([2, 6, 2])
    with col_logo:
        st.markdown("### 🚀 Generador MiPymesIA")
    with col_login:
        if st.button("🔐 Iniciar Sesión", use_container_width=True, type="primary", key="login_pricing"):
            st.session_state.page = 'login_form'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div style='text-align: center; padding: 30px 0;'>
        <h1 style='font-size: 2.8em; color: #1a5276; margin-bottom: 10px;'>💎 Planes y Precios</h1>
        <div style='width: 80px; height: 4px; background: linear-gradient(90deg, #3498db, #9b59b6); margin: 0 auto; border-radius: 2px;'></div>
        <p style='font-size: 1.2em; color: #5d6d7e; margin-top: 20px;'>Elige el plan perfecto para tu negocio</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # First row - 3 cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 350px;'>
            <h3 style='font-size: 1.5em; margin-bottom: 10px;'>🆓 Prueba Gratuita</h3>
            <h1 style='font-size: 3em; margin: 20px 0;'>$0 USD</h1>
            <p style='font-size: 1.1em; margin-bottom: 20px;'>7 días • 5 solicitudes/día</p>
            <p style='margin-top: 40px; font-style: italic; font-size: 0.9em;'>Ideal para probar la plataforma</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 350px;'>
            <h3 style='font-size: 1.5em; margin-bottom: 10px;'>💼 Plan Básico</h3>
            <h1 style='font-size: 3em; margin: 20px 0;'>$7 USD</h1>
            <p style='font-size: 1.1em; margin-bottom: 20px;'>30 días • 10 solicitudes/día</p>
            <p style='margin-top: 40px; font-style: italic; font-size: 0.9em;'>Ideal para emprendedores</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 350px;'>
            <h3 style='font-size: 1.5em; margin-bottom: 10px;'>🚀 Plan Estándar</h3>
            <h1 style='font-size: 3em; margin: 20px 0;'>$21 USD</h1>
            <p style='font-size: 1.1em; margin-bottom: 20px;'>90 días • 15 solicitudes/día</p>
            <p style='margin-top: 40px; font-style: italic; font-size: 0.9em;'>Ideal para negocios en crecimiento</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Second row - 2 cards centered
    col_left, col4, col5, col_right = st.columns([0.5, 1, 1, 0.5])
    
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 350px;'>
            <h3 style='font-size: 1.5em; margin-bottom: 10px;'>💎 Plan Profesional</h3>
            <h1 style='font-size: 3em; margin: 20px 0;'>$42 USD</h1>
            <p style='font-size: 1.1em; margin-bottom: 20px;'>180 días • 20 solicitudes/día</p>
            <p style='margin-top: 40px; font-style: italic; font-size: 0.9em;'>Ideal para PYMEs establecidas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 350px; border: 3px solid gold;'>
            <h3 style='font-size: 1.5em; margin-bottom: 10px;'>👑 Plan Empresarial</h3>
            <h1 style='font-size: 3em; margin: 20px 0;'>$84 USD</h1>
            <p style='font-size: 1.1em; margin-bottom: 20px;'>360 días • 25 solicitudes/día</p>
            <p style='margin-top: 40px; font-style: italic; font-size: 0.9em;'>Ideal para empresas grandes</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # What's included section - Redesigned
    st.markdown("""
    <div style='background: #f8f9fa; padding: 40px; border-radius: 15px; margin: 40px 0;'>
        <h2 style='text-align: center; color: #1a5276; margin-bottom: 40px;'>🎁 ¿Qué Incluyen Todos los Planes?</h2>
        <div style='max-width: 1000px; margin: 0 auto;'>
    """, unsafe_allow_html=True)
    
    # Grid layout for features
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>👤</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>Avatar IA</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Perfil de cliente ideal detallado</p>
        </div>
        <div style='text-align: center; padding: 10px; margin-top: 20px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>🛡️</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>Objeciones</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Manejo profesional de rechazos</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_f2:
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>📢</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>Contenido</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Embudo semanal completo</p>
        </div>
        <div style='text-align: center; padding: 10px; margin-top: 20px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>✅</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>Checklist</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Acciones diarias de venta</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_f3:
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>💰</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>Publicidad</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Estrategia de Ads pagada</p>
        </div>
        <div style='text-align: center; padding: 10px; margin-top: 20px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>📈</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>Métricas</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>KPIs y optimización</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_f4:
        st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>💬</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>WhatsApp</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Flujo de cierre de 7 días</p>
        </div>
        <div style='text-align: center; padding: 10px; margin-top: 20px;'>
            <div style='font-size: 2.5em; margin-bottom: 10px;'>📄</div>
            <h4 style='color: #2c3e50; margin-bottom: 5px;'>PDF Export</h4>
            <p style='font-size: 0.9em; color: #7f8c8d;'>Reportes profesionales</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Payment methods
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);'>
        <h3 style='color: #1a5276; margin-bottom: 20px;'>💳 Métodos de Pago</h3>
        <p style='font-size: 1.1em; color: #5d6d7e;'>Transferencia bancaria • Tarjetas de crédito/débito</p>
        <br>
        <a href='https://wa.link/qf8pf2' target='_blank' style='background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; padding: 15px 40px; border-radius: 30px; text-decoration: none; font-weight: bold; font-size: 1.1em; display: inline-block;'>
            📱 Contactar por WhatsApp
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer navigation
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("📋 Términos", use_container_width=True, key="terms_pricing"):
            st.session_state.page = 'terms'
            st.rerun()
    with col_b:
        if st.button("🔒 Privacidad", use_container_width=True, key="privacy_pricing"):
            st.session_state.page = 'privacy'
            st.rerun()
    with col_c:
        if st.button("✨ Registrarme", use_container_width=True, type="primary", key="register_pricing"):
            st.session_state.page = 'register'
            st.rerun()
    with col_d:
        if st.button("⬅️ Inicio", use_container_width=True, key="back_pricing"):
            st.session_state.page = 'login'
            st.rerun()
    
    show_footer()

if not st.session_state.authenticated:
    # Route to different pages
    if st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'login_form':
        login_form_page()
    elif st.session_state.page == 'register':
        registration_page()
    elif st.session_state.page == 'forgot_password':
        forgot_password_page()
    elif st.session_state.page == 'terms':
        show_static_page("📋 Términos de Uso", "content/terms_of_service.md")
    elif st.session_state.page == 'privacy':
        show_static_page("🔒 Política de Privacidad", "content/privacy_policy.md")
    elif st.session_state.page == 'pricing':
        pricing_page()
else:
    # Authenticated users
    if st.session_state.page == 'change_password':
        change_password_page()
    else:
        # Sidebar Header (Always visible)
        with st.sidebar:
            st.title("Generador MiPymesIA")
            
        # Page Routing
        if st.session_state.user.get('is_admin', False):
            with st.sidebar:
                 page = st.radio("Modo", ["Generador", "Cerebro del Negocio", "MiPymes IA", "Admin Panel"])
        else:
            with st.sidebar:
                page = st.radio("Menú", ["Generador", "Cerebro del Negocio", "MiPymes IA"])
        
        if page == "Generador":
            wizard_page()
        elif page == "Cerebro del Negocio":
            business_brain_page()
        elif page == "MiPymes IA":
            chat_page()
        elif page == "Admin Panel":
            admin_panel()
