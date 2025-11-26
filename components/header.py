"""
Header component - Reusable navigation bar
"""
import streamlit as st

def show(show_login_button=True):
    """Display header with logo and optional login button"""
    col_logo, col_spacer, col_login = st.columns([2, 6, 2])
    
    with col_logo:
        st.markdown("### 🚀 Generador MiPymesIA")
    
    if show_login_button:
        with col_login:
            if st.button("🔐 Iniciar Sesión", use_container_width=True, type="primary", key="header_login"):
                st.session_state.page = 'login_form'
                st.rerun()
