"""
Login Page - Landing page with carousel
"""
import streamlit as st
from components import header, footer, carousel

def render():
    """Render login/landing page"""
    
    # Header
    header.show(show_login_button=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1️⃣ HERO PRINCIPAL
    st.markdown("""
    <div style='text-align: center; padding: 40px 20px 30px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-bottom: 20px;'>
        <h1 style='font-size: 2.8em; color: white; margin-bottom: 15px; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);'>
            Estrategias de Marketing Profesionales
        </h1>
        <h2 style='color: #f0f0f0; font-size: 1.4em; margin-bottom: 25px; font-weight: 400;'>
            Impulsadas por Inteligencia Artificial
        </h2>
        <p style='font-size: 1.15em; color: white; margin-bottom: 30px; max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.6;'>
            Crea tu estrategia completa de marketing, publicidad y ventas en minutos.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Principal centrado
    col_cta_left, col_cta_center, col_cta_right = st.columns([1, 2, 1])
    with col_cta_center:
        if st.button("✨ Comenzar Prueba Gratis", use_container_width=True, type="primary", key="cta_hero"):
            st.session_state.page = 'register'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2️⃣ SUBTEXTO DE VALOR
    st.markdown("""
    <div style='text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px; margin-bottom: 30px;'>
        <p style='font-size: 1.05em; color: #555; margin: 0; font-style: italic;'>
            "Sin complicaciones, sin conocimientos técnicos. Solo completá tus datos y recibís tu plan listo para ejecutar."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3️⃣ BANNER / CARRUSEL (5 imágenes)
    carousel.show(num_images=5)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 4️⃣ SECCIÓN '¿QUÉ VAS A OBTENER?'
    st.markdown("""
    <div style='text-align: center; margin-bottom: 40px;'>
        <h2 style='font-size: 2.2em; color: #1a5276; margin-bottom: 10px;'>✨ ¿Qué vas a obtener en segundos?</h2>
        <p style='color: #666; font-size: 1.1em;'>Todo lo que necesitas para hacer crecer tu negocio</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features en cards modernas (2 columnas)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 5px solid #667eea;'>
            <h3 style='color: #1a5276; margin-bottom: 15px;'>👤 Tu Avatar de Cliente Ideal</h3>
            <p style='color: #555; line-height: 1.6; margin: 0;'>
                Perfil completo con dolores, deseos, objeciones y lenguaje real del cliente.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 5px solid #764ba2;'>
            <h3 style='color: #1a5276; margin-bottom: 15px;'>📢 Embudo de Contenido</h3>
            <p style='color: #555; line-height: 1.6; margin: 0;'>
                Plan semanal TOFU – MOFU – BOFU adaptado a tu negocio.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 5px solid #f093fb;'>
            <h3 style='color: #1a5276; margin-bottom: 15px;'>💰 Estrategia de Publicidad</h3>
            <p style='color: #555; line-height: 1.6; margin: 0;'>
                Campañas para públicos fríos, tibios y calientes con presupuesto recomendado.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 5px solid #4facfe;'>
            <h3 style='color: #1a5276; margin-bottom: 15px;'>💬 Flujo de WhatsApp para Ventas</h3>
            <p style='color: #555; line-height: 1.6; margin: 0;'>
                Secuencia de 7 días para convertir conversaciones en clientes.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 5px solid #43e97b;'>
            <h3 style='color: #1a5276; margin-bottom: 15px;'>🛡️ Respuestas a Objeciones</h3>
            <p style='color: #555; line-height: 1.6; margin: 0;'>
                Las 5 objeciones más comunes con respuestas profesionales.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); margin-bottom: 20px; border-left: 5px solid #fa709a;'>
            <h3 style='color: #1a5276; margin-bottom: 15px;'>📈 Métricas y Acciones Clave</h3>
            <p style='color: #555; line-height: 1.6; margin: 0;'>
                KPIs + plan de optimización para mejorar tus resultados semana a semana.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 5️⃣ CTA SECUNDARIO
    st.markdown("""
    <div style='text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin: 40px 0;'>
        <h2 style='color: white; font-size: 2em; margin-bottom: 20px;'>¿Listo para transformar tu negocio?</h2>
        <p style='color: #f0f0f0; font-size: 1.1em; margin-bottom: 30px;'>Comienza ahora y obtén resultados en minutos</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_cta2_left, col_cta2_center, col_cta2_right = st.columns([1, 2, 1])
    with col_cta2_center:
        if st.button("🚀 Empezar Ahora (Gratis)", use_container_width=True, type="primary", key="cta_secondary"):
            st.session_state.page = 'register'
            st.rerun()
        st.markdown("""
        <div style='text-align: center; margin-top: 15px;'>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>✨ Sin costo por 7 días</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
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
        if st.button("✨ Quiero Suscribirme", use_container_width=True, type="primary", key="footer_cta"):
            st.session_state.page = 'register'
            st.rerun()
    
    # Footer
    footer.show()
