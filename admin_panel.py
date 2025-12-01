import streamlit as st
import auth
import sqlite3
from datetime import datetime

def admin_panel():
    """
    Admin panel to manage users, subscriptions, and view usage statistics.
    """
    st.title("🔧 Panel de Administración")
    
    # Check if user is admin
    if not st.session_state.user.get('is_admin'):
        st.error("❌ No tienes permisos para acceder a esta página.")
        return
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["👥 Usuarios", "📊 Estadísticas", "⚙️ Configuración"])
    
    with tab1:
        st.subheader("Gestión de Usuarios")
        
        # Search filter
        search_query = st.text_input("🔍 Buscar usuario", placeholder="Buscar por nombre de usuario, email o negocio...")
        
        # Get all users
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("""
            SELECT username, email, business_name, is_active, plan_actual, 
                   fecha_vencimiento, requests_today, daily_request_limit,
                   ai_requests_today, ai_request_limit, tokens_total,
                   tokens_mes_actual, tokens_dia_actual
            FROM users
            ORDER BY username
        """)
        users = c.fetchall()
        conn.close()
        
        # Filter users based on search query
        if search_query:
            filtered_users = []
            search_lower = search_query.lower()
            for user in users:
                username, email, business_name = user[0], user[1], user[2]
                if (search_lower in (username or '').lower() or 
                    search_lower in (email or '').lower() or 
                    search_lower in (business_name or '').lower()):
                    filtered_users.append(user)
            users = filtered_users
        
        # Display users in a table
        st.markdown(f"**Total de usuarios:** {len(users)}")
        
        for user in users:
            username, email, business_name, is_active, plan_actual, fecha_venc, \
            req_today, req_limit, ai_today, ai_limit, tokens_total, tokens_mes, tokens_dia = user
            
            with st.expander(f"👤 {username} - {plan_actual or 'prueba'}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Información Básica**")
                    st.text(f"Email: {email or 'No especificado'}")
                    st.text(f"Negocio: {business_name or 'No especificado'}")
                    st.text(f"Estado: {'✅ Activo' if is_active else '❌ Inactivo'}")
                
                with col2:
                    st.markdown("**Suscripción**")
                    plan_names = {
                        'gratuito': 'GRATUITO',
                        'prueba': 'PRUEBA',
                        'mensual': 'MENSUAL',
                        'trimestral': 'TRIMESTRAL',
                        'semestral': 'SEMESTRAL',
                        'anual': 'ANUAL'
                    }
                    st.text(f"Plan: {plan_names.get(plan_actual or 'prueba', 'PRUEBA')}")
                    
                    if fecha_venc:
                        try:
                            exp_date = datetime.fromisoformat(fecha_venc)
                            days_left = (exp_date - datetime.now()).days
                            color = "🟢" if days_left > 10 else "🟡" if days_left > 0 else "🔴"
                            st.text(f"Vence: {color} {days_left} días")
                        except:
                            st.text(f"Vence: {fecha_venc[:10]}")
                    else:
                        st.text("Vence: No definido")
                
                with col3:
                    st.markdown("**Uso Actual**")
                    st.text(f"Estrategias: {req_today or 0}/{req_limit or 5}")
                    st.text(f"Consultas IA: {ai_today or 0}/{ai_limit or 10}")
                    st.text(f"Tokens hoy: {tokens_dia or 0}")
                    st.text(f"Tokens mes: {tokens_mes or 0}")
                    st.text(f"Tokens total: {tokens_total or 0}")
                
                # Admin actions
                st.markdown("---")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    # Change plan
                    new_plan = st.selectbox(
                        "Cambiar Plan",
                        ['gratuito', 'prueba', 'mensual', 'trimestral', 'semestral', 'anual'],
                        index=['gratuito', 'prueba', 'mensual', 'trimestral', 'semestral', 'anual'].index(plan_actual or 'prueba'),
                        key=f"plan_{username}"
                    )
                    if st.button("💾 Guardar Plan", key=f"save_plan_{username}"):
                        if auth.set_user_plan(username, new_plan):
                            st.success(f"✅ Plan actualizado a {new_plan}")
                            st.rerun()
                
                with col_b:
                    # Extend subscription
                    days_to_add = st.number_input(
                        "Extender días",
                        min_value=1,
                        max_value=365,
                        value=30,
                        key=f"days_{username}"
                    )
                    if st.button("➕ Extender", key=f"extend_{username}"):
                        from datetime import timedelta
                        conn = sqlite3.connect('users.db')
                        c = conn.cursor()
                        
                        # Get current expiration or use now
                        if fecha_venc:
                            try:
                                current_exp = datetime.fromisoformat(fecha_venc)
                            except:
                                current_exp = datetime.now()
                        else:
                            current_exp = datetime.now()
                        
                        new_exp = current_exp + timedelta(days=days_to_add)
                        c.execute("UPDATE users SET fecha_vencimiento = ? WHERE username = ?",
                                (new_exp.isoformat(), username))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Extendido {days_to_add} días")
                        st.rerun()
                
                with col_c:
                    # Toggle active status
                    if st.button(
                        "🔴 Desactivar" if is_active else "🟢 Activar",
                        key=f"toggle_{username}"
                    ):
                        conn = sqlite3.connect('users.db')
                        c = conn.cursor()
                        c.execute("UPDATE users SET is_active = ? WHERE username = ?",
                                (not is_active, username))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Usuario {'desactivado' if is_active else 'activado'}")
                        st.rerun()
    
    with tab2:
        st.subheader("Estadísticas Generales")
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Total users by plan
        c.execute("""
            SELECT plan_actual, COUNT(*) 
            FROM users 
            GROUP BY plan_actual
        """)
        plan_stats = c.fetchall()
        
        st.markdown("**Usuarios por Plan:**")
        for plan, count in plan_stats:
            st.text(f"{plan or 'prueba'}: {count} usuarios")
        
        # Total tokens usage
        c.execute("SELECT SUM(tokens_total), SUM(tokens_mes_actual), SUM(tokens_dia_actual) FROM users")
        total_tokens, mes_tokens, dia_tokens = c.fetchone()
        
        st.markdown("---")
        st.markdown("**Consumo de Tokens:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", f"{total_tokens or 0:,}")
        with col2:
            st.metric("Este Mes", f"{mes_tokens or 0:,}")
        with col3:
            st.metric("Hoy", f"{dia_tokens or 0:,}")
        
        # Active users
        c.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        active_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users")
        total_count = c.fetchone()[0]
        
        st.markdown("---")
        st.markdown(f"**Usuarios Activos:** {active_count}/{total_count}")
        
        conn.close()
    
    with tab3:
        st.subheader("Configuración del Sistema")
        
        st.markdown("**Expiración Automática de Usuarios**")
        st.info("El script `expire_users_cron.py` debe ejecutarse diariamente a las 2 AM para expirar usuarios automáticamente.")
        
        if st.button("🔄 Ejecutar Expiración Manual"):
            expired_count = auth.check_and_expire_users()
            if expired_count > 0:
                st.success(f"✅ {expired_count} usuarios expirados y movidos a plan gratuito")
            else:
                st.info("No hay usuarios para expirar")
        
        st.markdown("---")
        st.markdown("**Comando Cron:**")
        st.code("0 2 * * * /usr/bin/python3 /path/to/expire_users_cron.py", language="bash")
