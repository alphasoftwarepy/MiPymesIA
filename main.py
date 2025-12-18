import streamlit as st
import auth
import pdf_gen
import ai_logic
from ai_logic import MarketingStrategist
from pdf_gen import generate_pdf
import business_brain
import chat_brain
from admin_panel import admin_panel
import tracking_panel
import tasks_manager
import strategy_selector
from datetime import datetime, timedelta
import time
import urllib.parse
from views import login_page as new_login_page
import auto_init_db
import db_migrations
import scheduler

# Page Config
st.set_page_config(page_title="Generador MiPymesIA", page_icon="🚀", layout="wide")

# Auto-initialize database if needed (before migrations)
try:
    auto_init_db.auto_initialize()
except Exception as e:
    st.error(f"Error initializing database: {e}")
    st.stop()

# Run database migrations automatically on startup
try:
    db_migrations.run_migrations()
except Exception as e:
    st.error(f"Error running database migrations: {e}")
    st.stop()

# Start scheduler for automatic tasks (user expiration at 2 AM daily)
# Initialize only once to avoid multiple scheduler instances
if 'scheduler_started' not in st.session_state:
    try:
        scheduler.start_scheduler()
        st.session_state.scheduler_started = True
    except Exception as e:
        # Log error but don't stop the app
        print(f"Warning: Could not start scheduler: {e}")

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
    st.session_state['user'] = None
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
    # Scroll to top script
    st.markdown("""
    <script>
    window.scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)
    
    col_logo, col_spacer, col_login = st.columns([2, 6, 2])
    with col_logo:
        if st.button("🚀 Generador MiPymesIA", key="logo_static", type="secondary"):
            st.session_state.page = 'login'
            st.rerun()
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
    
    # Segunda fila de características personalizadas
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        st.markdown("""
        ### 🎯 MiProgreso
        Seguimiento de tareas y objetivos
        """)
    with col5:
        st.markdown("""
        ### 🧠 Cerebro del Negocio
        Contexto y personalidad de tu marca
        """)
    with col6:
        st.markdown("""
        ### 💬 Chat MiPymes IA
        Asistente de marketing inteligente
        """)
    with col7:
        st.markdown("""
        ### 📚 Chat IA por Sección
        Profundiza en cada parte de tu estrategia
        """)
    st.markdown("<br>", unsafe_allow_html=True) # Add a break for spacing
    
    # Segunda fila de características personalizadas (4 nuevos items)
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        st.markdown("""
        ### 🎯 MiProgreso
        Seguimiento de tareas y objetivos
        """)
    with col5:
        st.markdown("""
        ### 🧠 Cerebro del Negocio
        Contexto y personalidad de tu marca
        """)
    with col6:
        st.markdown("""
        ### 💬 Chat MiPymes IA
        Asistente de marketing inteligente
        """)
    with col7:
        st.markdown("""
        ### 📚 Chat IA por Sección
        Profundiza en cada parte de tu estrategia
        """)
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
    
    st.markdown("<br>", unsafe_allow_html=True) # Add a break for spacing
    
    # Segunda fila de características personalizadas
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        st.markdown("""
        ### 🎯 MiProgreso
        Seguimiento de tareas y objetivos
        """)
    with col5:
        st.markdown("""
        ### 🧠 Cerebro del Negocio
        Contexto y personalidad de tu marca
        """)
    with col6:
        st.markdown("""
        ### 💬 Chat MiPymes IA
        Asistente de marketing inteligente
        """)
    with col7:
        st.markdown("""
        ### 📚 Chat IA por Sección
        Profundiza en cada parte de tu estrategia
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
                        # Initialize AI agent without business_profile to avoid validation errors
                        # The business_profile will be used later in chat contexts
                        st.session_state.ai_agent = MarketingStrategist(business_context="")
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
    
    st.info("🎁 Obtén acceso completo por 7 días con 3 estrategias y 10 consultas IA por día. ¡Sin tarjeta de crédito!")
    
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
    if st.button("⬅️ Volver al Inicio"):
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
        
        # Load history from database if available
        username = st.session_state.user['username']
        history = auth.get_section_history(username, section_key)
        
        if history:
            # Convert database history to chat format
            for entry in history:
                st.session_state[chat_key].append({
                    "role": entry['tipo'],
                    "content": entry['contenido']
                })
    
    # Expander for chat
    with st.expander(f"💬 Ampliar y Profundizar en {section_name}", expanded=False):
        st.caption("Pregunta sobre esta sección específica para obtener más detalles, ejemplos o ideas.")
        
        # ========== SHOW ARCHIVED CONVERSATIONS ==========
        username = st.session_state.user['username']
        archives = auth.get_archived_conversations(username, section_key, limit=3)
        
        if archives:
            st.markdown("**📦 Conversaciones Archivadas:**")
            for archive in archives:
                with st.expander(f"📦 {archive['mensajes_count']} mensajes - {archive['timestamp'][:10]}", expanded=False):
                    st.markdown(archive['resumen'])
            st.divider()
        # =================================================
        
        # Show history count and clear button if available
        if len(st.session_state[chat_key]) > 0:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📝 {len(st.session_state[chat_key]) // 2} interacciones guardadas")
            with col2:
                if st.button("📥 Compactar Conversación", key=f"clear_{section_key}", help="Compactar y reiniciar conversación"):
                    username = st.session_state.user['username']
                    
                    # ========== COMPACT BEFORE CLEARING ==========
                    # Compact conversation to preserve insights
                    try:
                        success, summary, insights_count = auth.compact_section_history(
                            username, 
                            section_key, 
                            st.session_state.ai_agent
                        )
                        if success:
                            st.success(f"✅ Conversación archivada. {insights_count} insights guardados en el cerebro.")
                            print(f"✅ Compacted {section_key} before clearing: {insights_count} insights")
                    except Exception as e:
                        print(f"Warning: Failed to compact before clearing: {e}")
                        # If compaction fails, just clear normally
                        auth.clear_section_history(username, section_key)
                    # ============================================
                    
                    # Clear from session state
                    st.session_state[chat_key] = []
                    st.rerun()
        
        # Display chat history for this section
        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        prompt = st.chat_input(f"Pregunta sobre {section_name}...", key=f"input_{section_key}")
        
        if prompt:
            # ========== CHECK AI REQUEST LIMIT ==========
            username = st.session_state.user['username']
            can_request, remaining = auth.increment_ai_request(username)
            
            if not can_request:
                st.error("❌ Has alcanzado el límite diario de consultas IA. Intenta mañana o mejora tu plan.")
                st.stop()
            # ============================================
            
            # Add user message
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            
            # Save user message to database
            auth.save_section_history(username, section_key, "user", prompt)
            
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
            
            # Save assistant response to database
            auth.save_section_history(username, section_key, "assistant", response)
            
            # ========== ENRICH BRAIN FROM INTERACTION ==========
            # Automatically detect and save valuable insights
            try:
                insights_added = auth.enrich_brain_from_interaction(username, section_key, prompt, response)
                if insights_added > 0:
                    print(f"✅ Added {insights_added} insight(s) to brain from {section_key}")
            except Exception as e:
                print(f"Warning: Failed to enrich brain: {e}")
            # ===================================================
            
            # ========== AUTO-COMPACTION AT 10 MESSAGES ==========
            # Check if we should compact this section
            message_count = len(st.session_state[chat_key])
            if message_count >= 20:  # 10 user + 10 assistant = 20 total
                try:
                    success, summary, insights_count = auth.compact_section_history(
                        username, 
                        section_key, 
                        st.session_state.ai_agent
                    )
                    if success:
                        print(f"✅ Auto-compacted {section_key}: {insights_count} insights extracted")
                        # Clear session state since messages are now archived
                        st.session_state[chat_key] = []
                except Exception as e:
                    print(f"Warning: Failed to auto-compact: {e}")
            # ===================================================
            
            st.rerun()

# Helper to parse sections
def clean_section_content(content, section_name):
    """
    Cleans AI-generated content by removing unwanted text that leaks from other sections.
    Also removes duplicate titles and improves formatting.
    """
    if not content or content == "Contenido no disponible.":
        return content
    
    import re
    
    # FIRST: Remove duplicate section titles that come from AI
    title_patterns = [
        r"^👤\s*AVATAR DE CLIENTE IDEAL.*?\n",
        r"^📢\s*EMBUDO.*?\n",
        r"^🎣\s*TOFU.*?\n",
        r"^🧠\s*MOFU.*?\n",
        r"^💰\s*BOFU.*?\n",
        r"^❄️\s*TRÁFICO FRÍO.*?\n",
        r"^🔥\s*TRÁFICO TIBIO.*?\n",
        r"^🌡️\s*TRÁFICO CALIENTE.*?\n",
        r"^💬\s*DÍA\s+\d+.*?\n",
        r"^🛡️\s*OBJECIÓN:.*?\n",
        r"^✅\s*CHECKLIST.*?\n",
        r"^📊\s*MÉTRICAS.*?\n"
    ]
    
    for pattern in title_patterns:
        content = re.sub(pattern, "", content, flags=re.MULTILINE | re.IGNORECASE)
    
    # Patterns to remove based on section
    unwanted_patterns = {
        "AVATAR": [
            r"\*\*EMBUDO DE CONTENIDO.*",
            r"Aquí tienes.*embudo.*",
            r"A continuación.*embudo.*"
        ],
        "EMBUDO_BOFU": [
            r"\*\*Aquí tienes la estrategia de ads.*",
            r"Aquí tienes.*ads.*completa.*",
            r"A continuación.*publicidad.*"
        ],
        "ADS_CALIENTE": [
            r"Claro, aquí tienes un flujo de WhatsApp.*",
            r"DÍA 1.*Contacto.*Diagnóstico.*",
            r"Espero que este flujo.*"
        ],
        "WHATSAPP_DIA7": [
            r"Claro, aquí tienes las respuestas para.*",
            r"Espero que este flujo.*",
            r"Espero que estas.*sean útiles.*"
        ],
        "OBJECION_MIEDO": [
            r"Espero que estas respuestas sean útiles.*",
            r"Espero que.*ayude.*aumentar las ventas.*"
        ],
        "ACCIONES_DIARIAS": [
            r"Con esta rutina.*podrá enfocar.*",
            r"Con esta rutina.*maximizar.*resultados.*"
        ]
    }
    
    # Apply cleaning for specific section
    if section_name in unwanted_patterns:
        for pattern in unwanted_patterns[section_name]:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.DOTALL)
    
    # General cleanup: remove common AI closing remarks
    general_patterns = [
        r"Espero que.*sea.*útil.*",
        r"Espero que.*ayude.*",
        r"¡Mucho éxito!.*",
        r"¡Éxito!.*"
    ]
    
    for pattern in general_patterns:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE | re.DOTALL)
    
    # IMPROVE FORMATTING: Add bold to key terms
    content = re.sub(r"^(Objetivo|Formato|Gancho|CTA|Segmentación|Presupuesto|Creativos|Copy|Ángulo|Mensaje|Respuestas condicionadas|Pregunta|Reframing|Propuesta|Mini Cierre):", 
                     r"**\1:**", content, flags=re.MULTILINE)
    
    # Ensure proper paragraph spacing
    content = re.sub(r"(\n)([A-Z][^:\n]{10,}:)", r"\n\n\2", content)
    
    return content.strip()

def format_whatsapp_content(text):
    """
    Formats the WhatsApp content with better line breaks and separation.
    Specific improvement for readability of Messages and Conditional Responses.
    Handles existing formatting to avoid duplication.
    """
    if not text: return text
    
    import re
    
    # 1. Format Headers (Mensaje and Respuestas condicionadas) with Bold and newlines
    # Pattern matches optional ** before and after the keyword to capture just the keyword text
    # Result strips old ** and enforces new \n\n**KEYWORD** format
    
    # Mensaje
    text = re.sub(r"(?:\*\*|)?(Mensaje:)(?:\*\*|)?", r"\n\n**\1**", text, flags=re.IGNORECASE)
    
    # Respuestas condicionadas
    text = re.sub(r"(?:\*\*|)?(Respuestas condicionadas:)(?:\*\*|)?", r"\n\n**\1**", text, flags=re.IGNORECASE)
    
    # 2. Format Conditions "Si dice..."
    text = re.sub(r"(Si dice)", r"\n\n\1", text)
    
    # 3. Cleanup multiple newlines (max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()

def format_objections_content(text):
    """
    Formats the Objections content with better line breaks and separation.
    Specific improvement for readability of Objection handling structure.
    Handles existing formatting.
    """
    if not text: return text
    
    import re
    
    # Format common headers in Objections section
    # Objeción, Respuesta, Explicación, Mini Cierre, etc.
    patterns = [
        r"(Objeción:)", 
        r"(Respuesta:)", 
        r"(Respuesta Sugerida:)", 
        r"(Respuesta sugerida:)",
        r"(Explicación:)",
        r"(Mini Cierre:)", 
        r"(Por qué funciona:)",
        r"(Reframing:)",
        r"(Propuesta:)",
        r"(Pregunta:)"
    ]
    
    for pattern in patterns:
        # Construct regex: optional ** + keyword + optional **
        # pattern is like (Objeción:) including capturing group
        # we need to strip parens from pattern to build the regex correctly or use it as is?
        # pattern has capturing parens e.g. (Objeción:)
        # We need to construct: (?:\*\*|)?(Objeción:)(?:\*\*|)?
        
        # Strip parens from predefined pattern for cleaner construction
        clean_pat = pattern.replace('(', '').replace(')', '')
        
        # Regex: Optional ** -> Capture Keyword -> Optional **
        full_regex = f"(?:\\*\\*|)?({clean_pat})(?:\\*\\*|)?"
        
        text = re.sub(full_regex, r"\n\n**\1**", text, flags=re.IGNORECASE)
    
    # Cleanup multiple newlines (max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()

def get_tasks_text_summary(estrategia_id):
    """Generates a text summary of dynamic tasks for AI context."""
    user = st.session_state.user
    if not user: return ""
    
    tasks = tasks_manager.get_tasks_for_week(user['username'], estrategia_id)
    if not tasks: return "No hay tareas dinámicas generadas."
    
    summary = ["\n\n--- LISTA ACTUALIZADA DE TAREAS (BASE DE DATOS) ---"]
    
    # Sort by day
    days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    tasks_by_day = {i: [] for i in range(7)}
    for task in tasks:
        if task.get('dia_semana') is not None:
            tasks_by_day[task['dia_semana']].append(task)
            
    today_idx = datetime.now().weekday()
    
    for i in range(7):
        day_idx = (today_idx + i) % 7
        day_tasks = tasks_by_day.get(day_idx, [])
        if day_tasks:
            summary.append(f"\n[{days_es[day_idx]}]")
            for t in day_tasks:
                status = "✅ COMPLETADA" if t['completada'] else "PENDIENTE"
                summary.append(f"- {t['titulo']} ({status})")
                
    return "\n".join(summary)

def render_daily_tasks(estrategia_id):
    """
    Renders the tasks for the current strategy grouped by day.
    Replaces static text with dynamic database content.
    """
    user = st.session_state.user
    if not user: return

    # fetches all tasks for this strategy
    tasks = tasks_manager.get_tasks_for_week(user['username'], estrategia_id)
    
    if not tasks:
        st.info("ℹ️ No hay tareas generadas para esta estrategia aún.")
        return

    # Helper: Map day index to Spanish Name
    days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    # Organize tasks by day
    # dict: { day_index: [task1, task2...] }
    tasks_by_day = {i: [] for i in range(7)}
    
    for task in tasks:
        day_idx = task.get('dia_semana')
        if day_idx is not None and 0 <= day_idx <= 6:
            tasks_by_day[day_idx].append(task)
            
    # Calculate dates for the upcoming week starting from today
    # We want to show "Today" -> "Today + 6"
    today = datetime.now()
    current_day_idx = today.weekday() # 0=Monday
    
    ordered_days = []
    for i in range(7):
        day_offset = (current_day_idx + i) % 7
        target_date = today + timedelta(days=i)
        ordered_days.append((day_offset, target_date))
        
    # Render
    for day_idx, date_obj in ordered_days:
        day_name = days_es[day_idx]
        formatted_date = f"{day_name} {date_obj.day:02d}/{date_obj.month:02d}"
        
        day_tasks = tasks_by_day[day_idx]
        total_day = len(day_tasks)
        completed_day = sum(1 for t in day_tasks if t['completada'])
        
        # Header: "📅 Lunes 08/12 - 0/7"
        icon = "📍" if i == 0 else "📅"
        
        st.markdown(f"### {icon} {formatted_date} - {completed_day}/{total_day}")
        
        if not day_tasks:
            st.caption("No hay tareas programadas.")
        
        for task in day_tasks:
            # Priority Color
            prio_color = "🟢" # baja
            if task['prioridad'] == 'media': prio_color = "🟡"
            elif task['prioridad'] == 'alta': prio_color = "🔴"
            
            # Category Icon
            cat_icon = "📝" # contenido default
            cat = task.get('categoria', '').lower()
            if 'ads' in cat: cat_icon = "📢"
            elif 'whatsapp' in cat: cat_icon = "💬"
            elif 'setup' in cat: cat_icon = "⚙️"
            elif 'metricas' in cat: cat_icon = "📊"
            
            check_icon = "✅" if task['completada'] else prio_color
            
            # Task format: ICON TYPE ID ; Title
            st.markdown(f"{check_icon} {cat_icon} {task['titulo']}")
            
        st.markdown("<br>", unsafe_allow_html=True)

def get_section_content(text, section_name):
    if not text: return "Contenido no disponible."
    import re
    try:
        # Regex for flexible parsing (handling bold **, headers ##, spacing)
        # Matches optional * or #, then <<<, optional space, SECTION_START, optional space, :, optional space, NAME, optional space, >>>, optional * or #
        pattern = r"[\*#]*<<<\s*SECTION_START\s*:\s*" + re.escape(section_name) + r"\s*>>>[\*#]*"
        
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        if len(parts) > 1:
            # Look for next section start (any section) to split end
            # Matches any next section start marker
            content = re.split(r"[\*#]*<<<\s*SECTION_START", parts[1], flags=re.IGNORECASE)[0].strip()
            return clean_section_content(content, section_name)
            
        return "Contenido no disponible."
    except Exception as e:
        print(f"Error parsing section {section_name}: {e}")
        return "Error al cargar contenido."

def wizard_page():
    # Detectar modo de edición
    editing_id = st.session_state.get('editing_strategy_id')
    creating_new = st.session_state.get('creating_new_strategy')
    
    # Botón volver al selector
    if editing_id or creating_new:
        if st.button("⬅️ Volver al Selector"):
            st.session_state.creating_new_strategy = False
            st.session_state.editing_strategy_id = None
            st.session_state.step = 1  # Resetear a paso 1
            # Limpiar estados adicionales
            if 'current_strategy_name' in st.session_state:
                del st.session_state.current_strategy_name
            if 'strategy_result' in st.session_state:
                del st.session_state.strategy_result
            st.rerun()
    
    # Título según modo
    if editing_id:
        estrategia = auth.get_estrategia_by_id(editing_id, st.session_state.user['username'])
        if estrategia:
            st.title(f"📝 Editando: {estrategia['nombre']}")
            st.caption(f"Producto: {estrategia['producto']}")
        else:
            st.error("❌ Estrategia no encontrada")
            return
    elif creating_new:
        # Mostrar nombre si ya fue guardado
        if st.session_state.get('current_strategy_name'):
            st.title(f"🆕 {st.session_state.current_strategy_name}")
            st.caption("Generando estrategia personalizada...")
        else:
            st.title("🆕 Nueva Estrategia")
            st.caption("Crea una estrategia de marketing personalizada")
    else:
        st.title("🚀 Generador MiPymesIA")
        st.caption("Estrategias de Marketing y de Publicidad")
    
    # ========== LOAD STRATEGY IF EDITING (BEFORE STEP CHECK) ==========
    # This runs BEFORE checking step, but only when editing and going to step 2
    editing_id = st.session_state.get('editing_strategy_id')
    if editing_id and st.session_state.step == 2:
        # User is editing a specific strategy, load it
        user = st.session_state.user
        estrategia = auth.get_estrategia_by_id(editing_id, user['username'])
        
        if estrategia:
            # Reconstruct the strategy_result format
            strategy_sections = []
            
            # Add each section with markers
            if estrategia.get('avatar'):
                strategy_sections.append(f"<<<SECTION_START: AVATAR>>>\n{estrategia['avatar']}")
            
            # Parse embudo back into subsections
            if estrategia.get('embudo'):
                embudo_text = estrategia['embudo']
                if 'TOFU:' in embudo_text and 'MOFU:' in embudo_text and 'BOFU:' in embudo_text:
                    parts = embudo_text.split('MOFU:')
                    tofu = parts[0].replace('TOFU:', '').strip()
                    mofu_bofu = parts[1].split('BOFU:')
                    mofu = mofu_bofu[0].strip()
                    bofu = mofu_bofu[1].strip() if len(mofu_bofu) > 1 else ''
                    
                    strategy_sections.append(f"<<<SECTION_START: EMBUDO_TOFU>>>\n{tofu}")
                    strategy_sections.append(f"<<<SECTION_START: EMBUDO_MOFU>>>\n{mofu}")
                    strategy_sections.append(f"<<<SECTION_START: EMBUDO_BOFU>>>\n{bofu}")
                else:
                    strategy_sections.append(f"<<<SECTION_START: EMBUDO_TOFU>>>\n{embudo_text}")
            
            # Parse ads back into subsections
            if estrategia.get('ads'):
                ads_text = estrategia['ads']
                if 'FRÍO:' in ads_text and 'TIBIO:' in ads_text and 'CALIENTE:' in ads_text:
                    parts = ads_text.split('TIBIO:')
                    frio = parts[0].replace('FRÍO:', '').strip()
                    tibio_caliente = parts[1].split('CALIENTE:')
                    tibio = tibio_caliente[0].strip()
                    caliente = tibio_caliente[1].strip() if len(tibio_caliente) > 1 else ''
                    
                    strategy_sections.append(f"<<<SECTION_START: ADS_FRIO>>>\n{frio}")
                    strategy_sections.append(f"<<<SECTION_START: ADS_TIBIO>>>\n{tibio}")
                    strategy_sections.append(f"<<<SECTION_START: ADS_CALIENTE>>>\n{caliente}")
                else:
                    strategy_sections.append(f"<<<SECTION_START: ADS_FRIO>>>\n{ads_text}")
            
            # WhatsApp days
            if estrategia.get('whatsapp'):
                whatsapp_text = estrategia['whatsapp']
                days = whatsapp_text.split('\n\n')
                for i, day_content in enumerate(days[:7], 1):
                    strategy_sections.append(f"<<<SECTION_START: WHATSAPP_DIA{i}>>>\n{day_content}")
            
            # Objeciones
            if estrategia.get('objeciones'):
                objeciones_text = estrategia['objeciones']
                objeciones = objeciones_text.split('\n\n')
                tipos = ["COSTO", "TIEMPO", "PERSONAL", "INTEGRACION", "MIEDO"]
                for i, objecion_content in enumerate(objeciones[:5]):
                    if i < len(tipos):
                        strategy_sections.append(f"<<<SECTION_START: OBJECION_{tipos[i]}>>>\n{objecion_content}")
            
            # Acciones diarias
            if estrategia.get('acciones_diarias'):
                strategy_sections.append(f"<<<SECTION_START: ACCIONES_DIARIAS>>>\n{estrategia['acciones_diarias']}")
            
            # KPIs/Métricas
            if estrategia.get('kpis'):
                strategy_sections.append(f"<<<SECTION_START: METRICAS>>>\n{estrategia['kpis']}")
            
            # Reconstruct full strategy text
            st.session_state.strategy_result = '\n\n'.join(strategy_sections)
            
            # Also populate business_info if we have saved form data
            if user.get('last_form_data'):
                try:
                    import json
                    if isinstance(user['last_form_data'], str):
                        st.session_state.business_info = json.loads(user['last_form_data'])
                    else:
                        st.session_state.business_info = user['last_form_data']
                    
                    # Normalize plataforma field for PDF generation
                    if 'plataforma' in st.session_state.business_info:
                        plat = st.session_state.business_info['plataforma']
                        if isinstance(plat, list):
                            st.session_state.business_info['plataforma'] = ', '.join(plat)
                except:
                    st.session_state.business_info = {}
        else:
            st.error("❌ Estrategia no encontrada")
            return
    # ===================================================================
    
    if st.session_state.step == 1:
        st.subheader("📋 Diagnóstico y Contexto")
        
        # ========== CHECK FOR SAVED STRATEGY ==========
        user = st.session_state.user
        saved_estrategia = auth.get_estrategia(user['username'])
        
        # Skip intermediate step if user explicitly clicked "Nueva estrategia" or "Editar" from selector
        if saved_estrategia and not st.session_state.get('creating_new_strategy', False) and not st.session_state.get('editing_strategy_id'):
            # User has a saved strategy - offer choice
            st.success("✅ Tienes una estrategia guardada")
            
            # Show strategy info
            col1, col2 = st.columns(2)
            with col1:
                if saved_estrategia.get('created_at'):
                    from datetime import datetime as dt
                    try:
                        created = dt.fromisoformat(saved_estrategia['created_at'])
                        st.info(f"📅 **Creada:** {created.strftime('%d/%m/%Y %H:%M')}")
                    except:
                        pass
            with col2:
                if saved_estrategia.get('updated_at'):
                    from datetime import datetime as dt
                    try:
                        updated = dt.fromisoformat(saved_estrategia['updated_at'])
                        st.info(f"🔄 **Actualizada:** {updated.strftime('%d/%m/%Y %H:%M')}")
                    except:
                        pass
            
            st.markdown("---")
            st.markdown("### ¿Qué deseas hacer?")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("📂 Continuar con Estrategia Guardada", use_container_width=True, type="primary"):
                    # Load saved strategy into session state
                    # Reconstruct the strategy_result format that the app expects
                    strategy_sections = []
                    
                    # Add each section with markers
                    if saved_estrategia.get('avatar'):
                        strategy_sections.append(f"<<<SECTION_START: AVATAR>>>\n{saved_estrategia['avatar']}")
                    
                    # Parse embudo back into subsections
                    if saved_estrategia.get('embudo'):
                        embudo_text = saved_estrategia['embudo']
                        # Try to split back into TOFU, MOFU, BOFU
                        if 'TOFU:' in embudo_text and 'MOFU:' in embudo_text and 'BOFU:' in embudo_text:
                            parts = embudo_text.split('MOFU:')
                            tofu = parts[0].replace('TOFU:', '').strip()
                            mofu_bofu = parts[1].split('BOFU:')
                            mofu = mofu_bofu[0].strip()
                            bofu = mofu_bofu[1].strip() if len(mofu_bofu) > 1 else ''
                            
                            strategy_sections.append(f"<<<SECTION_START: EMBUDO_TOFU>>>\n{tofu}")
                            strategy_sections.append(f"<<<SECTION_START: EMBUDO_MOFU>>>\n{mofu}")
                            strategy_sections.append(f"<<<SECTION_START: EMBUDO_BOFU>>>\n{bofu}")
                        else:
                            strategy_sections.append(f"<<<SECTION_START: EMBUDO_TOFU>>>\n{embudo_text}")
                    
                    # Parse ads back into subsections
                    if saved_estrategia.get('ads'):
                        ads_text = saved_estrategia['ads']
                        if 'FRÍO:' in ads_text and 'TIBIO:' in ads_text and 'CALIENTE:' in ads_text:
                            parts = ads_text.split('TIBIO:')
                            frio = parts[0].replace('FRÍO:', '').strip()
                            tibio_caliente = parts[1].split('CALIENTE:')
                            tibio = tibio_caliente[0].strip()
                            caliente = tibio_caliente[1].strip() if len(tibio_caliente) > 1 else ''
                            
                            strategy_sections.append(f"<<<SECTION_START: ADS_FRIO>>>\n{frio}")
                            strategy_sections.append(f"<<<SECTION_START: ADS_TIBIO>>>\n{tibio}")
                            strategy_sections.append(f"<<<SECTION_START: ADS_CALIENTE>>>\n{caliente}")
                        else:
                            strategy_sections.append(f"<<<SECTION_START: ADS_FRIO>>>\n{ads_text}")
                    
                    # WhatsApp days
                    if saved_estrategia.get('whatsapp'):
                        whatsapp_text = saved_estrategia['whatsapp']
                        # Try to split into days (basic split by double newline)
                        days = whatsapp_text.split('\n\n')
                        for i, day_content in enumerate(days[:7], 1):
                            strategy_sections.append(f"<<<SECTION_START: WHATSAPP_DIA{i}>>>\n{day_content}")
                    
                    # Objeciones
                    if saved_estrategia.get('objeciones'):
                        objeciones_text = saved_estrategia['objeciones']
                        objeciones = objeciones_text.split('\n\n')
                        tipos = ["COSTO", "TIEMPO", "PERSONAL", "INTEGRACION", "MIEDO"]
                        for i, objecion_content in enumerate(objeciones[:5]):
                            if i < len(tipos):
                                strategy_sections.append(f"<<<SECTION_START: OBJECION_{tipos[i]}>>>\n{objecion_content}")
                    
                    # Acciones diarias
                    if saved_estrategia.get('acciones_diarias'):
                        strategy_sections.append(f"<<<SECTION_START: ACCIONES_DIARIAS>>>\n{saved_estrategia['acciones_diarias']}")
                    
                    # KPIs/Métricas
                    if saved_estrategia.get('kpis'):
                        strategy_sections.append(f"<<<SECTION_START: METRICAS>>>\n{saved_estrategia['kpis']}")
                    
                    # Reconstruct full strategy text
                    st.session_state.strategy_result = '\n\n'.join(strategy_sections)
                    st.session_state.step = 2
                    
                    # Also populate business_info if we have saved form data
                    if user.get('last_form_data'):
                        try:
                            import json
                            if isinstance(user['last_form_data'], str):
                                st.session_state.business_info = json.loads(user['last_form_data'])
                            else:
                                st.session_state.business_info = user['last_form_data']
                            
                            # Normalize plataforma field for PDF generation
                            if 'plataforma' in st.session_state.business_info:
                                plat = st.session_state.business_info['plataforma']
                                if isinstance(plat, list):
                                    st.session_state.business_info['plataforma'] = ', '.join(plat)
                        except:
                            st.session_state.business_info = {}
                    
                    st.rerun()
            
            with col_btn2:
                if st.button("🆕 Crear Nueva Estrategia", use_container_width=True):
                    # User wants to create new strategy, continue to form below
                    st.session_state.show_new_strategy_form = True
                    st.rerun()
            
            # If user hasn't clicked "Create New", don't show the form
            if not st.session_state.get('show_new_strategy_form', False):
                return
            else:
                st.markdown("---")
                st.markdown("### Nueva Estrategia")
        # ================================================
        
        # Load saved form data if available
        saved_data = {}
        if user and user.get('last_form_data'):
            try:
                import json
                if isinstance(user['last_form_data'], str):
                    saved_data = json.loads(user['last_form_data'])
                else:
                    saved_data = user['last_form_data']
            except:
                saved_data = {}
        
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
        
        # Clear form button
        if saved_data:
            col_clear = st.columns([6, 1])[1]
            with col_clear:
                if st.button("🗑️ Limpiar", help="Borrar datos guardados"):
                    auth.save_last_form_data(user['username'], {})
                    user['last_form_data'] = ""
                    st.rerun()
        with st.form("diagnosis_form"):
            # ========== STRATEGY IDENTIFICATION ==========
            st.markdown("### 🎯 Identificación de la Estrategia")
            st.caption("Dale un nombre único a esta estrategia")
            
            col_strat1, col_strat2 = st.columns(2)
            with col_strat1:
                nombre_estrategia = st.text_input(
                    "📝 Nombre de la Estrategia",
                    value=saved_data.get('nombre_estrategia', ''),
                    placeholder="ej: Sistema Principal, Hotmart",
                    help="Nombre descriptivo para esta estrategia"
                )
            with col_strat2:
                producto_servicio_desc = st.text_input(
                    "📦 Producto/Servicio",
                    value=saved_data.get('producto_servicio_desc', ''),
                    placeholder="ej: Software SaaS, Curso Online",
                    help="Descripción del producto/servicio"
                )
            
            st.markdown("---")
            # ================================================
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏢 Información del Negocio")
                rubro = st.text_input("📌 Rubro del Negocio", value=saved_data.get('rubro', ''), placeholder="ej: Gastronomía, Moda, Tecnología")
                nombre = st.text_input("✨ Nombre del Negocio", value=saved_data.get('nombre', ''), placeholder="ej: Mi Empresa")
                
                tipo_options = ["Físico", "Tienda Online", "Dropshipping", "Productos Digitales", "Servicios"]
                tipo_idx = 0
                if saved_data.get('tipo') in tipo_options:
                    tipo_idx = tipo_options.index(saved_data.get('tipo'))
                tipo = st.selectbox("🏪 Tipo de Negocio", tipo_options, index=tipo_idx)
            
            with col2:
                st.markdown("### 🎯 Objetivos y Presupuesto")
                
                # NEW: Diferenciador clave
                diferenciador = st.text_area(
                    "💎 ¿Qué te hace diferente de la competencia?",
                    value=saved_data.get('diferenciador', ''),
                    placeholder="ej: Entrega en 24hs, Garantía de por vida, Atención 24/7",
                    help="Tu ventaja competitiva única",
                    height=100
                )
                
                precio = st.number_input("💵 Precio del Producto/Servicio (USD) - Opcional", min_value=0.0, value=float(saved_data.get('precio', 0.0)) if saved_data.get('precio') else 0.0, step=1.0)
                
                meta_options = ["Aumentar Ventas", "Ganar Seguidores", "Reconocimiento de Marca", "Generar Leads"]
                meta_idx = 0
                if saved_data.get('meta') in meta_options:
                    meta_idx = meta_options.index(saved_data.get('meta'))
                meta = st.selectbox("📈 Meta Actual", meta_options, index=meta_idx)
                
                presupuesto = st.slider("💰 Presupuesto Mensual (USD)", min_value=50, max_value=1000, value=int(saved_data.get('presupuesto', 150)), step=50)

                # NEW: Duration Selector
                duration_options = [15, 30, 60, 90]
                duration_days = st.selectbox(
                    "📅 Duración de la Estrategia",
                    duration_options,
                    index=0,
                    format_func=lambda x: f"{x} Días",
                    help="Define la duración del plan estratégico (Roadmap)."
                )
                
                mod_options = ["Mayoría Contado", "Mayoría Crédito", "Mensual / SaaS"]
                mod_idx = 0
                if saved_data.get('modalidad_venta') in mod_options:
                    mod_idx = mod_options.index(saved_data.get('modalidad_venta'))
                modalidad = st.selectbox("💳 Modalidad de Venta", mod_options, index=mod_idx)
            
            st.markdown("### 📱 Plataformas de Publicidad")
            
            plat_default = ["Facebook/Instagram"]
            if saved_data.get('plataforma'):
                saved_plat = saved_data.get('plataforma')
                if isinstance(saved_plat, str):
                    plat_default = [p.strip() for p in saved_plat.split(',')]
                elif isinstance(saved_plat, list):
                    plat_default = saved_plat
            
            valid_options = ["Facebook/Instagram", "Google Ads"]
            plat_default = [p for p in plat_default if p in valid_options]
            
            plataforma = st.multiselect(
                "¿Dónde deseas hacer publicidad?",
                valid_options,
                default=plat_default
            )
            
            st.markdown("### 👤 Buyer Persona (Opcional)")
            buyer_persona = st.text_area(
                "Si ya tienes un perfil de cliente ideal, descríbelo aquí. La IA lo usará como base para expandir el análisis.",
                value=saved_data.get('buyer_persona', ''),
                placeholder="Ejemplo: Mujer de 25-35 años, profesional independiente, interesada en desarrollo personal...",
                height=100
            )
            
            generate = st.form_submit_button("🧠 Generar Estrategia Completa", use_container_width=True, type="primary")
            
            if generate:
                if not rubro or not nombre or not producto_servicio_desc or not plataforma:
                    st.warning("⚠️ Por favor completa todos los campos obligatorios.")
                else:
                    # Check subscription status and request limits
                    user = st.session_state.get('user')
                    if not user:
                        st.error("❌ Sesión expirada. Por favor, vuelve a iniciar sesión.")
                        st.stop()
                    
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
                    
                    # Save form data
                    business_info_save = {
                        "nombre_estrategia": nombre_estrategia,
                        "producto_servicio_desc": producto_servicio_desc,
                        "rubro": rubro,
                        "nombre": nombre,
                        "tipo": tipo,
                        "producto": producto_servicio_desc,
                        "diferenciador": diferenciador,  # NEW
                        "precio": precio,
                        "meta": meta,
                        "presupuesto": presupuesto,
                        "modalidad_venta": modalidad,
                        "plataforma": plataforma,
                        "buyer_persona": buyer_persona
                    }
                    auth.save_last_form_data(user['username'], business_info_save)
                    import json
                    save_user = st.session_state.get('user')
                    if save_user:
                        save_user['last_form_data'] = json.dumps(business_info_save)
                    
                    # ========== CLEAR OLD DATA WHEN GENERATING NEW STRATEGY ==========
                    # Clear section chat histories
                    chat_keys = [key for key in st.session_state.keys() if key.startswith('chat_')]
                    for key in chat_keys:
                        del st.session_state[key]
                    
                    # Clear old tasks and progress from database
                    # Clear old tasks and progress from database
                    import db_config
                    
                    conn = db_config.get_connection()
                    c = conn.cursor()
                    
                    # Safe deletion - only delete if tables exist
                    tables_to_clear = [
                        'historial_secciones',
                        'conversaciones_archivadas'
                    ]
                    
                    for table in tables_to_clear:
                        try:
                            c.execute(f"DELETE FROM {table} WHERE user_id = %s", (user['username'],))
                        except Exception as e:
                            # Table doesn't exist yet, skip
                            print(f"⚠️ Table {table} doesn't exist or error: {e}, skipping cleanup")
                            pass
                    
                    conn.commit()
                    conn.close()
                    # ================================================================
                    
                    # Show loading overlay
                    try:
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
                                </div>
                            </div>
                            """, unsafe_allow_html=True)                      
                        
                        # Define business_info HERE before using it anywhere (FIXED NameError)
                        business_info = {
                            "rubro": rubro,
                            "nombre": nombre,
                            "tipo": tipo,
                            "producto": producto_servicio_desc,
                            "precio": precio if precio > 0 else None,
                            "meta": meta,
                            "presupuesto": presupuesto,
                            "presupuesto_diario": round(presupuesto/30, 2),
                            "plataforma": ", ".join(plataforma),
                            "modalidad_venta": modalidad,
                            "buyer_persona": buyer_persona if buyer_persona else None,
                            "duration_days": duration_days
                        }

                        # Create progress container
                        progress_container = st.empty()

                        # --- PARALLEL EXECUTION: AI + VISUALS ---
                        import concurrent.futures

                        # Capture required variables in MAIN THREAD
                        agent = st.session_state.get('ai_agent')
                        current_user = st.session_state.get('user')
                        
                        if not current_user or not agent:
                            st.error("❌ Los datos de sesión no están disponibles. Intenta iniciar sesión de nuevo.")
                            st.stop()
                            
                        current_username = current_user.get('username')
                        
                        # 1. Define the AI task wrapper (to run in background)
                        def run_ai_generation():
                            # Use captured variables
                            return agent.generate_strategy_progressive(
                                business_info, 
                                None,
                                username=current_username
                            )

                        # 2. Launch AI in background thread
                        # This starts the heavy processing RIGHT NOW
                        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                        future = executor.submit(run_ai_generation)

                        # 3. Run the "Movie" (Visual Sequence) in the Main Thread
                        # While the AI is working in the background, we entertain the user
                        
                        # Step 1
                        update_loader("✨ Creando tu estrategia personalizada ✨", 1)
                        time.sleep(3.5)
                        
                        # Step 2
                        update_loader("🧠 Analizando ADN de tu negocio...", 2)
                        time.sleep(4)
                        
                        # Step 3
                        update_loader("🔍 Detectando oportunidades de mercado...", 3)
                        time.sleep(4)

                        # Step 4
                        update_loader("✅ Generando Avatar de Cliente...", 4)
                        time.sleep(4)

                        # Step 5
                        update_loader("📝 Estructurando Estrategia...", 5)
                        time.sleep(3.5)
                        
                        # Step 6
                        update_loader("🎯 Diseñando Embudos de Ventas...", 6)
                        time.sleep(3)

                        # Step 6-A
                        update_loader("✅ Estrategias TOFU, MOFU y BOFU Listas...", 7)
                        time.sleep(3)
                        
                        # Step 7
                        update_loader("🎯 Diseñando Estrategia de Ads...", 8)
                        time.sleep(3.5)
                        
                        # Step 8
                        update_loader("✅ Segmentación de anuncios Lista...", 9)
                        time.sleep(3)

                        # Step 8-A
                        update_loader("✅ Generación de contenidos Lista...", 10)
                        time.sleep(3)

                        # Step 9
                        update_loader("📲 Configurando secuencias de mensajes...", 11)
                        time.sleep(3.5)
                        
                        # Step 10
                        update_loader("✅ Flujo de WhatsApp Listo...", 12)
                        time.sleep(3)
                        
                        # Step 11
                        update_loader("🛡️ Blindando contra objeciones...", 13)
                        time.sleep(3.5)
                        
                        # Step 12
                        update_loader("✅ Manejo de Objeciones Listo...", 14)
                        time.sleep(3)
                        
                        # Step 13
                        update_loader("✅ Generando tareas personalizadas...", 15)
                        time.sleep(3.5)
                        
                        # Step 14 - Final Wait
                        update_loader("✅ Ajustando ultimos detalles...", 16)
                        
                        # 4. Wait for AI to finish (if it hasn't already)
                        try:
                            result = future.result()
                            executor.shutdown(wait=False)
                        except Exception as e:
                            # CRITICAL: Clear loader so user can see the error
                            overlay_placeholder.empty()
                            progress_container.empty()
                            
                            # Log the full error
                            import traceback
                            error_trace = traceback.format_exc()
                            print(f"❌ ERROR EN GENERACIÓN: {e}")
                            print(f"❌ TRACEBACK COMPLETO:\n{error_trace}")
                            
                            # Show detailed error to user
                            st.error(f"❌ Error en generación: {e}")
                            with st.expander("🔍 Ver detalles técnicos del error"):
                                st.code(error_trace)
                            st.stop()
                        
                        # Check if result is an error message
                        if result and result.startswith("Error:"):
                            overlay_placeholder.empty()
                            progress_container.empty()
                            st.error(result)
                            st.warning("💡 **Posible solución:** Verifica que la variable de entorno OPENAI_API_KEY esté configurada en Easypanel.")
                            st.stop()
                        # 🎉 SUCCESS - Strategy Generated
                        overlay_placeholder.empty()
                        progress_container.empty()
                        
                        # Clear cache to show weekly tasks immediately
                        st.cache_data.clear()
                        
                        st.success("✅ ¡Estrategia generada exitosamente!")
                        st.session_state.strategy_result = result
                        st.session_state.business_info = business_info
                        
                        # Force reload to show strategy
                        time.sleep(1)
                        st.rerun()
                        
                        # Wrap everything after AI generation in try-finally to ensure loader clears
                        try:
                            # 5. Process result and save strategy
                            st.session_state.strategy_result = result
                            st.session_state.business_info = business_info
                            st.session_state.step = 3
                            
                            # Initialize sections_generated with all sections since they are all done
                            if 'sections_generated' not in st.session_state:
                                st.session_state.sections_generated = {}
                            
                            # Populate sections_generated from the result text
                            sections = ["ROADMAP", "AVATAR", "EMBUDO", "ADS", "WHATSAPP", "OBJECIONES", "ACCIONES_DIARIAS", "METRICAS"]
                            for section in sections:
                                content = get_section_content(result, section)
                                if content and content != "Contenido no disponible.":
                                    st.session_state.sections_generated[section] = content
                            
                            # ========== SAVE STRATEGY TO DATABASE ==========
                            # Save the complete strategy to database for persistence
                            try:
                                estrategia_data = {
                                    'avatar': get_section_content(result, "AVATAR"),
                                    'embudo': f"TOFU:\n{get_section_content(result, 'EMBUDO_TOFU')}\n\nMOFU:\n{get_section_content(result, 'EMBUDO_MOFU')}\n\nBOFU:\n{get_section_content(result, 'EMBUDO_BOFU')}",
                                    'ads': f"FRÍO:\n{get_section_content(result, 'ADS_FRIO')}\n\nTIBIO:\n{get_section_content(result, 'ADS_TIBIO')}\n\nCALIENTE:\n{get_section_content(result, 'ADS_CALIENTE')}",
                                    'objeciones': '\n\n'.join([get_section_content(result, f"OBJECION_{tipo}") for tipo in ["COSTO", "TIEMPO", "PERSONAL", "INTEGRACION", "MIEDO"]]),
                                    'whatsapp': '\n\n'.join([get_section_content(result, f"WHATSAPP_DIA{i}") for i in range(1, 8)]),
                                    'acciones_diarias': "", # Will be generated in background
                                    'kpis': get_section_content(result, "METRICAS")
                                }
                                
                                # Parse Roadmap JSON
                                roadmap_json = {}
                                try:
                                    import json
                                    roadmap_text = get_section_content(result, "ROADMAP")
                                    if roadmap_text and roadmap_text != "Contenido no disponible.":
                                        # Try to find JSON content if it's wrapped in code blocks
                                        if "```json" in roadmap_text:
                                            roadmap_text = roadmap_text.split("```json")[1].split("```")[0].strip()
                                        elif "```" in roadmap_text:
                                            roadmap_text = roadmap_text.split("```")[1].split("```")[0].strip()
                                        
                                        roadmap_json = json.loads(roadmap_text)
                                except Exception as e:
                                    print(f"⚠️ Error parsing roadmap JSON: {e}")
                                    roadmap_json = {}

                                # Create new strategy (don't use save_estrategia as it updates the first one)
                                success, message, estrategia_id = auth.create_estrategia(
                                    username=st.session_state.user['username'], 
                                    nombre_estrategia=business_info.get('producto', 'Mi Estrategia'),
                                    producto_servicio=producto_servicio_desc if producto_servicio_desc else "Producto/Servicio",
                                    estrategia_data=estrategia_data,
                                    duracion_dias=business_info.get('duration_days', 30),
                                    roadmap=roadmap_json
                                )
                                
                                if not success:
                                    st.error(f"❌ Error al guardar estrategia: {message}")
                                    return
                                
                                st.session_state.editing_strategy_id = estrategia_id
                                st.session_state.creating_new_strategy = False
                                
                                # ========== MANUAL TASK GENERATION ==========
                                # We stop auto-generation to prevent AI overload.
                                # User will generate tasks manually in "Mi Progreso"
                                update_loader("✅ Estrategia Guardada. Ve a 'Mi Progreso' para activar tus tareas.", 16)
                                time.sleep(2)
                                
                            except Exception as e:
                                print(f"❌ Error saving strategy: {e}")
                                import traceback
                                traceback.print_exc()
                                st.error(f"❌ Error al guardar estrategia: {e}")
                                return
                        
                        finally:
                            # ALWAYS clear the loader, no matter what happens
                            print("🧹 Clearing loader overlay...")
                            overlay_placeholder.empty()
                            progress_container.empty()
                        
                        # ================================================
                        
                        # ========== AUTO-POPULATE BRAIN (MULTI-SERVICE) ==========
                        # NEW: Add or update service, accumulate info, NO avatar storage
                        
                        # Prepare service data from current strategy
                        service_data = {
                            'nombre': business_info.get('producto', ''),
                            'rubro': business_info.get('rubro', ''),
                            'precio': str(business_info.get('precio', '')),
                            'tipo_venta': business_info.get('tipo', ''),
                            'diferenciador': business_info.get('diferenciador', ''),
                            'descripcion': f"{business_info.get('producto', '')} - {business_info.get('rubro', '')}"
                        }
                        section_keys = [
                            'objecion_costo', 'objecion_tiempo', 'objecion_personal',
                            'objecion_integracion', 'objecion_miedo',
                            'acciones_diarias', 'metricas'
                        ]
                            
                        for section_key in section_keys:
                            try:
                                # Check if section has messages
                                messages = auth.get_section_history(user['username'], section_key)
                                if messages and len(messages) > 0:
                                    # Compact before clearing
                                    success, summary, insights_count = auth.compact_section_history(
                                        user['username'], 
                                        section_key, 
                                        st.session_state.ai_agent
                                    )
                                    if success:
                                        print(f"✅ Compacted old {section_key} chat: {insights_count} insights")
                                    
                                    # Clear from session state if exists
                                    chat_key = f"chat_{section_key}"
                                    if chat_key in st.session_state:
                                        st.session_state[chat_key] = []
                            except Exception as e:
                                print(f"Warning: Failed to compact {section_key}: {e}")
                        
                        print("✅ All old section chats cleared for new strategy")
                        # ============================================
                        
                    except Exception as save_error:
                        # Don't fail the whole process if save fails, just log it
                        print(f"Warning: Failed to save strategy to database: {save_error}")
                    # ================================================
                    
                    # Update user session with new request count
                    if 'user' in st.session_state and st.session_state.user:
                        st.session_state.user['requests_today'] = user.get('requests_today', 0) + 1
                    
                    overlay_placeholder.empty()
                    progress_container.empty()
                    st.rerun()
                    
    elif st.session_state.step == 2:
        st.session_state.step = 3
        st.rerun()

    elif st.session_state.step == 3:


        strategy_text = st.session_state.strategy_result
        
        # DEBUG: Show raw text to identify parsing issues
        # This allows us to see exactly what the AI returned
        # HIDDEN: Uncomment if needed for debugging
        # with st.expander("🛠️ Debug: Ver Texto Crudo (Útil si faltan secciones)", expanded=False):
        #     st.code(strategy_text)
        

        
        # Sidebar Navigation
        with st.sidebar:
            # Display subscription info FIRST
            user = st.session_state.user
            
            # ========== SHOW PLAN NAME ==========
            plan_actual = user.get('plan_actual', 'prueba')
            plan_names = {
                'gratuito': 'GRATUITO',
                'prueba': 'PRUEBA GRATUITA',
                'starter': 'STARTER',
                'growth': 'GROWTH',
                'pro': 'PRO'
            }
            st.markdown(f"**Plan:** {plan_names.get(plan_actual, plan_actual.upper())}")
            
            # Show renewal date only for non-free plans
            if plan_actual != 'gratuito' and user.get('fecha_vencimiento'):
                try:
                    exp_date = datetime.fromisoformat(user['fecha_vencimiento'])
                    days_remaining = (exp_date - datetime.now()).days
                    
                    # Format date as "6/diciembre/2025"
                    months_es = {
                        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
                    }
                    fecha_renovacion = f"{exp_date.day}/{months_es[exp_date.month]}/{exp_date.year}"
                    
                    # Color coding for days remaining
                    if days_remaining > 10:
                        color = "green"
                    elif days_remaining >= 4:
                        color = "orange"
                    else:
                        color = "red"
                    
                    st.markdown(f"**Renovación:** {fecha_renovacion}")
                    st.markdown(f"**Días restantes:** :{color}[{days_remaining}]")
                except Exception as e:
                    print(f"Error parsing expiration date: {e}")
            # ====================================
            
            # ========== STRATEGY COUNTER ==========
            from auth_subscription import get_plan_limits
            
            # Get limits from plan configuration
            plan_config = get_plan_limits(user.get('plan_actual', 'gratuito'))
            daily_limit = plan_config.get('estrategias_dia', 1)
            
            # Get usage from user object (updated in auth.py)
            current_usage = int(user.get('daily_strategies_count', 0))
            remaining_strategies = max(0, daily_limit - current_usage)
            
            # Color coding for strategies
            if remaining_strategies > daily_limit * 0.5:
                strat_color = "green"
            elif remaining_strategies > 0:
                strat_color = "orange"
            else:
                strat_color = "red"
            
            st.markdown(f"**Estrategias disponibles:** :{strat_color}[{remaining_strategies}/{daily_limit}]")
            # ======================================
            
            # ========== AI REQUEST COUNTER ==========
            ai_used, ai_limit, ai_remaining = auth.get_ai_request_status(user['username'])
            
            # Color coding for AI requests
            if ai_remaining > ai_limit * 0.5:
                ai_color = "green"
            elif ai_remaining > 0:
                ai_color = "orange"
            else:
                ai_color = "red"
            
            st.markdown(f"**Consultas IA disponibles:** :{ai_color}[{ai_remaining}/{ai_limit}]")
            # ========================================
            
            # Calculate hours until midnight (renewal time)
            now = datetime.now()
            midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            hours_until_renewal = int((midnight - now).total_seconds() / 3600)
            st.caption(f"Se renueva en {hours_until_renewal} horas")
            
            # Payment link
            st.markdown("[💳 Pagar Suscripción](https://wa.link/7q1i5z)")
            
            # Strategy Status Indicator
            if auth.has_estrategia(user['username']):
                estrategia = auth.get_estrategia(user['username'])
                if estrategia:
                    st.success("✅ Estrategia Guardada")
                    # Guardar estrategia activa en session_state
                    st.session_state['estrategia_activa_id'] = estrategia.get('id')
                    if estrategia.get('created_at'):
                        from datetime import datetime as dt
                        try:
                            created = dt.fromisoformat(estrategia['created_at'])
                            st.caption(f"Creada: {created.strftime('%d/%m/%Y')}")
                        except:
                            pass
            
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
            # if st.button("🔄 Nueva Estrategia", use_container_width=True, type="primary"):
            #     st.session_state.step = 1
            #     st.session_state.show_new_strategy_form = False  # Reset flag
            #     st.rerun()
            
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
            st.success("🎯 Conoce a fondo a tu cliente ideal para crear mensajes que realmente conecten.")
            
            # Avatar is already loaded, just display it
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
            st.success("📝 Contenido estratégico para atraer, educar y convertir a tu audiencia.")
            
            # Load section on-demand
            # load_section_on_demand("EMBUDO")
            
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
            st.success("📈 Invierte tu presupuesto de forma inteligente para maximizar resultados.")
            st.info(f"Presupuesto Mensual: ${st.session_state.business_info.get('presupuesto')} USD")
            
            # Load section on-demand
            # load_section_on_demand("ADS")
            
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
            st.subheader("💬 4. Flujo de WhatsApp para Ventas")
            st.success("🔥 Mensajes probados para cerrar ventas por WhatsApp día a día.")
            
            # Load section on-demand
            # load_section_on_demand("WHATSAPP")
            
            tabs = st.tabs(["Día 1", "Día 2", "Día 3", "Día 4", "Día 5", "Día 6", "Día 7"])
            for i, tab in enumerate(tabs):
                with tab:
                    content = get_section_content(strategy_text, f"WHATSAPP_DIA{i+1}")
                    st.markdown(format_whatsapp_content(content))
            
            # Add contextual chat for this section
            whatsapp_content = "\n\n".join([f"DÍA {i+1}:\n{get_section_content(strategy_text, f'WHATSAPP_DIA{i+1}')}" for i in range(7)])
            section_chat("Flujo de WhatsApp", whatsapp_content, "whatsapp")

        # 5. OBJECIONES
        elif "Objeciones" in selected_section:
            st.subheader("🛡️ 5. Manejo de Objeciones")
            st.success("💬 Convierte objeciones en oportunidades de venta con respuestas efectivas.")
            
            # Load section on-demand
            # load_section_on_demand("OBJECIONES")
            
            tabs = st.tabs(["Costo", "Tiempo", "Personal", "Integración", "Miedo"])
            obj_keys = ["COSTO", "TIEMPO", "PERSONAL", "INTEGRACION", "MIEDO"]
            
            for tab, key in zip(tabs, obj_keys):
                with tab:
                    content = get_section_content(strategy_text, f"OBJECION_{key}")
                    st.markdown(format_objections_content(content))
            
            # Add contextual chat for this section
            objeciones_content = "\n\n".join([f"{key}:\n{get_section_content(strategy_text, f'OBJECION_{key}')}" for key in obj_keys])
            section_chat("Manejo de Objeciones", objeciones_content, "objeciones")

        # 6. ACCIONES DIARIAS
        elif "Acciones" in selected_section:
            st.success("🎯 Acciones diarias para optimizar tus resultados.")

            # Load section on-demand
            # load_section_on_demand("ACCIONES_DIARIAS")
            
            # Retrieve content for chat context (and fallback)
            content = get_section_content(strategy_text, "ACCIONES_DIARIAS")
            
            # Determine current strategy ID
            current_strat_id = st.session_state.get('editing_strategy_id') or st.session_state.get('estrategia_activa_id')
            
            if current_strat_id:
                render_daily_tasks(current_strat_id)
                # Append real tasks to context so AI knows about them
                tasks_context = get_tasks_text_summary(current_strat_id)
                # FORCE PRIORITY to dynamic tasks
                content = f"⚠️ INSTRUCCIÓN CLAVE: La siguiente es la LISTA REAL DE TAREAS programadas en la agenda del usuario. Úsala como fuente VERDADERA para 'hoy' o 'esta semana'. Ignora el checklist genérico si contradice estas tareas.\n\n{tasks_context}\n\n--- CHECKLIST GENÉRICO (REFERENCIA) ---\n{content}"
            else:
                st.warning("⚠️ No se identificó la estrategia activa para mostrar las tareas.")
                 # Fallback to static content if no ID found
                st.markdown(content)
            
            # Add contextual chat for this section
            section_chat("Acciones Diarias", content, "acciones")

        # 7. METRICAS (WITHOUT DEMOS)
        elif "Métricas" in selected_section:
            st.subheader("📈 7. Métricas y Optimización")
            st.success("📊 Mide, analiza y optimiza para escalar tu negocio de forma sostenible.")
            
            # Load section on-demand
            # load_section_on_demand("METRICAS")
            
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
            
            # Add contextual chat for this section
            section_chat("Métricas y Optimización", content, "metricas")

        # Footer Actions
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            # Single PDF Download Button with improved error handling
            try:
                # Fetch tasks for PDF
                current_strat_id_pdf = st.session_state.get('editing_strategy_id') or st.session_state.get('estrategia_activa_id')
                tasks_for_pdf = []
                if current_strat_id_pdf:
                     tasks_for_pdf = tasks_manager.get_tasks_for_week(st.session_state.user['username'], current_strat_id_pdf)
                
                # Validate required data
                if not st.session_state.get('strategy_result'):
                    st.warning("⚠️ No hay estrategia disponible para generar PDF")
                elif not st.session_state.get('business_info'):
                    st.warning("⚠️ Falta información del negocio para generar PDF")
                else:
                    # Generate PDF fresh on each render
                    pdf_bytes = generate_pdf(
                        st.session_state.strategy_result, 
                        st.session_state.business_info, 
                        tasks=tasks_for_pdf
                    )
                    
                    # Ensure we have valid PDF data
                    if pdf_bytes and len(pdf_bytes) > 0:
                        st.download_button(
                            label="📄 Descargar PDF",
                            data=pdf_bytes,
                            file_name=f"estrategia_{st.session_state.business_info.get('nombre', 'negocio').replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary",
                            key="download_pdf_btn"  # Unique key to avoid conflicts
                        )
                    else:
                        st.error("❌ Error: PDF generado está vacío")
                        
            except Exception as e:
                st.error(f"❌ Error al generar PDF: {str(e)}")
                st.caption("💡 Intenta recargar la página o generar una nueva estrategia")
                # Log error for debugging
                import traceback
                print(f"PDF Generation Error: {traceback.format_exc()}")
        # with col2:
        #     if st.button("🔄 Nueva Estrategia", use_container_width=True):
        #         st.session_state.step = 1
        #         st.rerun()
    
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
        
        # Callback to handle suggestion click
        def on_suggestion_click(text):
            st.session_state.pending_suggestion = text

        # Check if we are processing
        is_processing = st.session_state.get('is_processing_chat', False)

        for i, suggestion in enumerate(suggestions):
            with [col1, col2, col3][i % 3]:
                st.button(
                    suggestion, 
                    key=f"suggestion_{i}", 
                    use_container_width=True,
                    disabled=is_processing,
                    on_click=on_suggestion_click,
                    args=(suggestion,)
                )
        
        # Process pending suggestion
        if 'pending_suggestion' in st.session_state and st.session_state.pending_suggestion:
            suggestion = st.session_state.pending_suggestion
            del st.session_state.pending_suggestion # Clear immediately
            
            # Set processing flag and rerun to update UI (disable buttons)
            st.session_state.is_processing_chat = True
            st.session_state.current_suggestion_processing = suggestion
            st.rerun()

        # If we are in processing state
        if st.session_state.get('is_processing_chat') and 'current_suggestion_processing' in st.session_state:
            suggestion = st.session_state.current_suggestion_processing
            
            # Add to chat history if not already added (check last message)
            if not st.session_state.chat_messages or st.session_state.chat_messages[-1]['content'] != suggestion:
                 st.session_state.chat_messages.append({"role": "user", "content": suggestion})
            
            with st.spinner("Pensando..."):
                response = st.session_state.ai_agent.chat(suggestion)
            
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            
            # Clear processing state
            st.session_state.is_processing_chat = False
            del st.session_state.current_suggestion_processing
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
    
    # First row - 3 cards centered
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 550px; display: flex; flex-direction: column; justify-content: space-between;'>
            <div>
                <h3 style='font-size: 1.5em; margin-bottom: 10px;'>Plan Starter</h3>
                <h1 style='font-size: 3em; margin: 20px 0;'>$5 USD</h1>
                <p style='font-size: 1.1em; margin-bottom: 10px;'>Facturado cada mes</p>
                <hr style='border-color: rgba(255,255,255,0.3); margin: 15px 0;'>
                <div style='display: flex; justify-content: center;'>
                    <ul style='list-style: none; padding: 0; margin-bottom: 20px; text-align: left;'>
                        <li style='margin-bottom: 8px;'>✅ 3 Estrategias por día</li>
                        <li style='margin-bottom: 8px;'>✅ 10 Consultas IA por día</li>
                        <li style='margin-bottom: 8px;'>✅ Acceso a todas las herramientas</li>
                    </ul>
                </div>
            </div>
            <p style='font-style: italic; font-size: 0.9em;'>Ideal para comenzar</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 550px; display: flex; flex-direction: column; justify-content: space-between;'>
            <div>
                <h3 style='font-size: 1.5em; margin-bottom: 10px;'>Plan Growth</h3>
                <h1 style='font-size: 3em; margin: 10px 0;'>$7 USD</h1>
                <p style='font-size: 1.1em; margin-bottom: 10px;'>Facturado cada mes</p>
                <hr style='border-color: rgba(255,255,255,0.3); margin: 15px 0;'>
                <div style='display: flex; justify-content: center;'>
                    <ul style='list-style: none; padding: 0; margin-bottom: 20px; text-align: left;'>
                        <li style='margin-bottom: 8px;'>✅ 5 Estrategias por día</li>
                        <li style='margin-bottom: 8px;'>✅ 20 Consultas IA por día</li>
                        <li style='margin-bottom: 8px;'>✅ Acceso a todas las herramientas</li>
                    </ul>
                </div>
            </div>
            <p style='font-style: italic; font-size: 0.9em;'>Ahorra y crece más rápido</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); height: 550px; display: flex; flex-direction: column; justify-content: space-between;'>
            <div>
                <h3 style='font-size: 1.5em; margin-bottom: 10px;'>Plan Pro</h3>
                <h1 style='font-size: 3em; margin: 20px 0;'>$10 USD</h1>
                <p style='font-size: 1.1em; margin-bottom: 10px;'>Facturado cada mes</p>
                <hr style='border-color: rgba(255,255,255,0.3); margin: 15px 0;'>
                <div style='display: flex; justify-content: center;'>
                    <ul style='list-style: none; padding: 0; margin-bottom: 20px; text-align: left;'>
                        <li style='margin-bottom: 8px;'>✅ 10 Estrategias por día</li>
                        <li style='margin-bottom: 8px;'>✅ 30 Consultas IA por día</li>
                        <li style='margin-bottom: 8px;'>✅ Acceso a todas las herramientas</li>
                    </ul>
                </div>
            </div>
            <p style='font-style: italic; font-size: 0.9em;'>La mejor inversión a largo plazo</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # What's included section - Redesigned with Expanders
    st.markdown("""
    <div style='background: #f8f9fa; padding: 20px; border-radius: 15px; margin: 0px 0;'>
        <h2 style='text-align: center; color: #1a5276; margin-bottom: 0px;'>🚀 Todo lo que puedes hacer con MiPymesIA</h2>
        <p style='text-align: center; color: #5d6d7e; margin-top: 10px;'>Más que un chatbot, un sistema operativo de marketing completo.</p>
        <div style='max-width: 1000px; margin: 0 auto;'>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 1. PERFIL & CONTEXTO (CEREBRO)
    with st.expander("1. PERFIL & CONTEXTO DE NEGOCIO (CEREBRO)"):
        st.markdown("""
        **El sistema actúa como un estratega de marketing dedicado.**
        
        *   **Contexto Centralizado:** Define una vez la identidad de tu negocio: nombre, rubro, tipos de productos/servicios y diferencial único.
        *   **Memoria Inteligente:** La IA utiliza este "Cerebro" para personalizar todas las estrategias subsequentes, asegurando coherencia en todos los mensajes y materiales generados.
        """)

    # 2. GENERACIÓN DE ESTRATEGIAS
    with st.expander("2. GENERACIÓN DE ESTRATEGIAS (EL CORE)"):
        st.markdown("""
        **Crea planes de marketing completos en minutos a partir de datos básicos.**
        
        *   **👤 Avatar de Cliente Ideal:** Identificación profunda de demografía, psicografía, dolores y deseos.
        *   **📢 Embudo de Contenido (Full Funnel):**
            *   *TOFU (Atracción):* Ideas para atraer desconocidos.
            *   *MOFU (Consideración):* Contenido para educar y nutrir.
            *   *BOFU (Conversión):* Ofertas directas para cerrar ventas.
        *   **💰 Estrategia de Publicidad (Ads):** Estructura de campañas para Tráfico Frío, Tibio y Caliente con scripts y segmentación.
        *   **💬 Flujo de Ventas (WhatsApp):** Guiones de conversación día a día y respuestas condicionadas.
        *   **🛡️ Manejo de Objeciones:** Respuestas preparadas para objeciones de Costo, Tiempo, Miedo, etc.
        """)

    # 3. EJECUCIÓN DIARIA
    with st.expander("3. SISTEMA DE EJECUCIÓN DIARIA"):
        st.markdown("""
        **Transforma la estrategia teórica en un plan de acción real.**
        
        *   **📅 Calendario Dinámico:** Convierte el plan en una lista de tareas específicas para la semana y el día actual.
        *   **☑️ Checklist Interactivo:** Marca tareas completadas directamente en la plataforma.
        *   **🔄 Carga Dinámica:** Las tareas se adaptan automáticamente a la estrategia activa.
        """)
        
    # 4. SEGUIMIENTO & GAMIFICACIÓN
    with st.expander("4. SEGUIMIENTO Y GAMIFICACIÓN"):
        st.markdown("""
        **Panel diseñado para mantener la constancia y disciplina.**
        
        *   **🔥 Estadísticas en Tiempo Real:** Visualiza tu "Racha Actual" (días seguidos), Puntos Totales y Nivel.
        *   **📈 Barra de Progreso Semanal:** Visual claro del avance (%) de tus objetivos.
        *   **🏆 Historial de Logros:** Desbloquea medallas por constancia y ejecución.
        """)

    # 5. ASISTENTE IA
    with st.expander("5. ASISTENTE IA CONTEXTUAL"):
        st.markdown("""
        **Un chat inteligente que conoce tu estrategia sección por sección.**
        
        *   **📚 Especialista por Sección:** ¿Dudas sobre Ads? Pregunta en Ads. La IA responde con contexto específico.
        *   **📥 Compactación Inteligente:** El botón "Compactar Conversación" resume tus charlas y guarda "insights" en el Cerebro.
        *   **📦 Historial Archivado:** Acceso a resúmenes de conversaciones pasadas.
        """)

    # 6. EXPORTACIÓN
    with st.expander("6. HERRAMIENTAS Y EXPORTACIÓN"):
        st.markdown("""
        *   **🔄 Soporte Multi-Estrategia:** Gestiona diferentes líneas de negocio o productos.
        *   **📄 Exportación PDF:** Descarga la estrategia completa en un documento profesional PDF listo para compartir.
        *   **💎 Control de Suscripción:** Vista clara de tu plan actual y límites.
        """)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # FAQ Section
    st.markdown("""
    <div style='max-width: 1000px; margin: 0 auto;'>
        <h3 style='text-align: center; color: #1a5276;'>Preguntas Frecuentes</h3>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("¿Necesito tarjeta de crédito para la prueba gratuita?"):
        st.write("No. Tienes acceso total durante el periodo de prueba sin necesidad de ingresar tarjeta de crédito.")

    with st.expander("¿La IA realmente aprende de mi negocio?"):
        st.write("Sí. Gracias a la función de 'Cerebro del Negocio' y 'Compactar Conversación', el sistema guarda preferencias y aprendizajes clave para mejorar con el tiempo.")

    with st.expander("¿Puedo gestionar múltiples negocios?"):
        st.write("Sí. Con los planes de pago (Prueba, Mensual, Trimestral, Anual) puedes crear múltiples estrategias para diferentes productos o líneas de negocio.")
        
    with st.expander("¿Qué pasa si no renuevo mi suscripción?"):
        st.write("Tu cuenta pasará al plan Gratuito. Tus datos se conservarán, pero tendrás límites de acceso y generación hasta que reactives tu plan.")

    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Payment methods
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);'>
        <h3 style='color: #1a5276; margin-bottom: 20px;'>💳 Métodos de Pago</h3>
        <p style='font-size: 1.1em; color: #5d6d7e;'>Transferencia bancaria • Tarjetas de crédito/débito</p>
        <br>
        <a href='https://wa.link/7q1i5z' target='_blank' style='background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; padding: 15px 40px; border-radius: 30px; text-decoration: none; font-weight: bold; font-size: 1.1em; display: inline-block;'>
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
        new_login_page.render()
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
        user_auth = st.session_state.get('user', {})
        if user_auth.get('is_admin', False):
            with st.sidebar:
                 page = st.radio("Modo", ["Selector de Estrategias", "Mi Progreso", "Cerebro del Negocio", "MiPymes IA", "Admin Panel"])
        else:
            with st.sidebar:
                page = st.radio("Menú", ["Selector de Estrategias", "Mi Progreso", "Cerebro del Negocio", "MiPymes IA"])
        
        if page == "Selector de Estrategias":
            # Check if user is creating/editing a strategy
            if st.session_state.get('creating_new_strategy') or st.session_state.get('editing_strategy_id'):
                wizard_page()
            elif st.session_state.get('deleting_strategy_id'):
                # Show deletion confirmation
                strategy_selector.handle_strategy_deletion()
                # Also show the selector
                strategy_selector.strategy_selector_page()
            else:
                # Show strategy selector
                strategy_selector.strategy_selector_page()
        elif page == "Mi Progreso":
            tracking_panel.tracking_panel_page()
        elif page == "Cerebro del Negocio":
            business_brain.business_brain_page()
        elif page == "MiPymes IA":
            chat_brain.chat_page()
        elif page == "Admin Panel":
            admin_panel()
