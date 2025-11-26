"""
Footer component - Reusable footer
"""
import streamlit as st

def show():
    """Display minimalist footer"""
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee;'>
        Generador MiPymes I.A. Todos los derechos © 2025 | By <a href="https://www.alphasoft.com.py/" target="_blank" style="color: #666; text-decoration: none;">Alpha Software</a>
    </div>
    """, unsafe_allow_html=True)
