import sqlite3
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")

# Ensure the directory exists
os.makedirs(DB_PATH, exist_ok=True)

DB_NAME = os.path.join(DB_PATH, "users.db")

# ==================== SUBSCRIPTION MANAGEMENT ====================

# Plan configurations
PLAN_CONFIGS = {
    'gratuito': {
        'duracion_dias': 999999,  # Permanent
        'estrategias_dia': 1,
        'consultas_ia_dia': 5
    },
    'prueba': {
        'duracion_dias': 7,
        'estrategias_dia': 3,
        'consultas_ia_dia': 10
    },
    'starter': {
        'duracion_dias': 30,
        'estrategias_dia': 3,
        'consultas_ia_dia': 10
    },
    'growth': {
        'duracion_dias': 30,
        'estrategias_dia': 5,
        'consultas_ia_dia': 20
    },
    'pro': {
        'duracion_dias': 30,
        'estrategias_dia': 10,
        'consultas_ia_dia': 30
    }
}

def get_plan_limits(plan_name):
    """Returns the limits for a given plan."""
    return PLAN_CONFIGS.get(plan_name, PLAN_CONFIGS['gratuito'])

def set_user_plan(username, plan_name, payment_date=None):
    """
    Sets a user's plan and calculates expiration date.
    """
    from datetime import datetime, timedelta
    
    if plan_name not in PLAN_CONFIGS:
        return False
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow()
    payment_date = payment_date or now
    plan_config = PLAN_CONFIGS[plan_name]
    expiration_date = payment_date + timedelta(days=plan_config['duracion_dias'])
    
    c.execute("""
        UPDATE users 
        SET plan_actual = ?,
            fecha_ultimo_pago = ?,
            fecha_vencimiento = ?,
            daily_request_limit = ?,
            ai_request_limit = ?
        WHERE username = ?
    """, (
        plan_name,
        payment_date.isoformat(),
        expiration_date.isoformat(),
        plan_config['estrategias_dia'],
        plan_config['consultas_ia_dia'],
        username
    ))
    
    conn.commit()
    conn.close()
    return True

def check_and_expire_users():
    """
    Checks all users and expires those whose fecha_vencimiento has passed.
    Changes them to 'gratuito' plan.
    Should be run daily at 2 AM via cron.
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    # Find expired users
    c.execute("""
        SELECT username, plan_actual, fecha_vencimiento
        FROM users
        WHERE fecha_vencimiento < ? 
        AND plan_actual != 'gratuito'
        AND is_active = 1
    """, (now,))
    
    expired_users = c.fetchall()
    
    if expired_users:
        print(f"Found {len(expired_users)} expired users")
        
        for username, old_plan, expiration in expired_users:
            print(f"Expiring user: {username} (was {old_plan}, expired {expiration})")
            set_user_plan(username, 'gratuito')
    
    conn.close()
    return len(expired_users)

def increment_ai_request(username):
    """
    Increments AI request counter for a user.
    Returns (can_request, remaining) tuple.
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get current user data
    c.execute("""
        SELECT ai_requests_today, ai_request_limit, last_request_date
        FROM users
        WHERE username = ?
    """, (username,))
    
    result = c.fetchone()
    if not result:
        conn.close()
        return (False, 0)
    
    ai_requests_today, ai_request_limit, last_request_date = result
    
    # Check if we need to reset (new day)
    today = datetime.utcnow().date().isoformat()
    last_date = last_request_date[:10] if last_request_date else None
    
    if last_date != today:
        # Reset counter for new day
        ai_requests_today = 0
    
    # Check if user can make request
    if ai_requests_today >= ai_request_limit:
        conn.close()
        return (False, 0)
    
    # Increment counter
    ai_requests_today += 1
    
    c.execute("""
        UPDATE users
        SET ai_requests_today = ?,
            last_request_date = ?
        WHERE username = ?
    """, (ai_requests_today, datetime.utcnow().isoformat(), username))
    
    conn.commit()
    conn.close()
    
    remaining = ai_request_limit - ai_requests_today
    return (True, remaining)

def get_ai_request_status(username):
    """
    Gets current AI request status for a user.
    Returns (used, limit, remaining) tuple.
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""
        SELECT ai_requests_today, ai_request_limit, last_request_date
        FROM users
        WHERE username = ?
    """, (username,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return (0, 10, 10)
    
    ai_requests_today, ai_request_limit, last_request_date = result
    
    # Check if we need to reset (new day)
    today = datetime.utcnow().date().isoformat()
    last_date = last_request_date[:10] if last_request_date else None
    
    if last_date != today:
        ai_requests_today = 0
    
    remaining = ai_request_limit - ai_requests_today
    return (ai_requests_today, ai_request_limit, remaining)

def track_tokens(username, tokens_used):
    """
    Tracks token usage for a user.
    Updates total, monthly, and daily counters.
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get current token data
    c.execute("""
        SELECT tokens_total, tokens_mes_actual, tokens_dia_actual, tokens_last_reset
        FROM users
        WHERE username = ?
    """, (username,))
    
    result = c.fetchone()
    if not result:
        conn.close()
        return False
    
    tokens_total, tokens_mes, tokens_dia, last_reset = result
    
    now = datetime.utcnow()
    last_reset_date = datetime.fromisoformat(last_reset) if last_reset else now
    
    # Check if we need to reset monthly counter
    if now.month != last_reset_date.month:
        tokens_mes = 0
    
    # Check if we need to reset daily counter
    if now.date() != last_reset_date.date():
        tokens_dia = 0
    
    # Update counters
    tokens_total = (tokens_total or 0) + tokens_used
    tokens_mes = (tokens_mes or 0) + tokens_used
    tokens_dia = (tokens_dia or 0) + tokens_used
    
    c.execute("""
        UPDATE users
        SET tokens_total = ?,
            tokens_mes_actual = ?,
            tokens_dia_actual = ?,
            tokens_last_reset = ?
        WHERE username = ?
    """, (tokens_total, tokens_mes, tokens_dia, now.isoformat(), username))
    
    conn.commit()
    conn.close()
    return True
