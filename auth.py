import sqlite3
import hashlib
from passlib.context import CryptContext
import pandas as pd

# Password hashing configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

#DB_NAME = "users.db"
import os

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")

# Ensure the directory exists
os.makedirs(DB_PATH, exist_ok=True)

DB_NAME = os.path.join(DB_PATH, "users.db")

def init_db():
    """Initializes the SQLite database and creates the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            business_name TEXT,
            is_active BOOLEAN NOT NULL CHECK (is_active IN (0, 1)),
            is_admin BOOLEAN NOT NULL CHECK (is_admin IN (0, 1)),
            start_date TEXT,
            expiration_date TEXT,
            requests_today INTEGER DEFAULT 0,
            last_request_date TEXT,
            email TEXT DEFAULT '',
            daily_request_limit INTEGER DEFAULT 20,
            failed_login_attempts INTEGER DEFAULT 0,
            lockout_until TEXT,
            business_profile TEXT DEFAULT ''
        )
    ''')
    
    # Migration: Add business_profile column if it doesn't exist
    try:
        c.execute("SELECT business_profile FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        print("Adding business_profile column to users table...")
        c.execute("ALTER TABLE users ADD COLUMN business_profile TEXT DEFAULT ''")
        print("Migration completed successfully.")
    
    # Migration: Add last_form_data column if it doesn't exist
    try:
        c.execute("SELECT last_form_data FROM users LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        print("Adding last_form_data column to users table...")
        c.execute("ALTER TABLE users ADD COLUMN last_form_data TEXT DEFAULT ''")
        print("Migration completed successfully.")
    
    conn.commit()
    conn.close()

def verify_password(plain_password, hashed_password):
    """Verifies a plain password against the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashes a password."""
    return pwd_context.hash(password)

def create_user(username, password, email, business_name="", is_active=False, is_admin=False, daily_request_limit=20):
    """Creates a new user in the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_password = get_password_hash(password)
    # Set trial period of 7 days for new users if not explicitly active
    start_date = None
    expiration_date = None
    if not is_active and not is_admin:
        # New user will start trial automatically
        from datetime import datetime, timedelta
        start_date = datetime.utcnow().strftime('%Y-%m-%d')
        expiration_date = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
        is_active = True  # trial users are active until expiration
        daily_request_limit = 5  # Free trial gets 5 requests
    try:
        c.execute("""INSERT INTO users 
                     (username, password, email, business_name, is_active, is_admin, start_date, expiration_date, 
                      requests_today, last_request_date, daily_request_limit, failed_login_attempts, lockout_until) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?, 0, NULL)""",
                  (username, hashed_password, email, business_name, is_active, is_admin, start_date, expiration_date, daily_request_limit))
        conn.commit()
        
        # Apply full plan configuration (including AI limits)
        if not is_admin:
            # We need to close this connection before calling set_user_plan to avoid locking if it opens its own
            conn.close()
            from auth_subscription import set_user_plan
            set_user_plan(username, 'prueba')
            return True
            
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def login_user(username, password):
    """Checks credentials, updates subscription status, and returns the user object if valid."""
    from datetime import datetime
    
    # Check if user is locked out
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT lockout_until, failed_login_attempts FROM users WHERE username = ?", (username,))
    lockout_data = c.fetchone()
    
    if lockout_data and lockout_data[0]:
        lockout_until = datetime.fromisoformat(lockout_data[0])
        if datetime.utcnow() < lockout_until:
            conn.close()
            remaining_seconds = int((lockout_until - datetime.utcnow()).total_seconds())
            return {"error": "locked", "remaining_seconds": remaining_seconds}
        else:
            # Lockout expired, reset
            c.execute("UPDATE users SET lockout_until = NULL, failed_login_attempts = 0 WHERE username = ?", (username,))
            conn.commit()
    
    c.execute("""SELECT username, password, business_name, is_active, is_admin, start_date, expiration_date, 
                        requests_today, last_request_date, email, daily_request_limit, business_profile, last_form_data,
                        plan_actual, fecha_registro, fecha_ultimo_pago, fecha_vencimiento,
                        ai_requests_today, ai_request_limit
                 FROM users WHERE username = ?""", (username,))
    user = c.fetchone()

    if user:
        # user structure: (username, password_hash, business_name, is_active, is_admin, start_date, expiration_date, 
        #                  requests_today, last_request_date, email, daily_request_limit, business_profile, last_form_data,
        #                  plan_actual, fecha_registro, fecha_ultimo_pago, fecha_vencimiento, ai_requests_today, ai_request_limit)
        if verify_password(password, user[1]):
            # Reset failed attempts on successful login
            c.execute("UPDATE users SET failed_login_attempts = 0, lockout_until = NULL WHERE username = ?", (username,))
            conn.commit()
            
            # Update subscription status based on expiration_date
            is_active = bool(user[3])
            expiration = user[6]
            if expiration:
                if datetime.utcnow().strftime('%Y-%m-%d') > expiration:
                    # Expired: deactivate user
                    toggle_user_active(username, False)
                    is_active = False
            
            conn.close()
            return {
                "username": user[0],
                "business_name": user[2],
                "is_active": is_active,
                "is_admin": bool(user[4]),
                "start_date": user[5],
                "expiration_date": user[6],
                "requests_today": user[7] or 0,
                "last_request_date": user[8],
                "email": user[9] or "",
                "daily_request_limit": user[10] or 5,
                "business_profile": user[11] or "",
                "last_form_data": user[12] or "",
                "plan_actual": user[13] or "prueba",
                "fecha_registro": user[14],
                "fecha_ultimo_pago": user[15],
                "fecha_vencimiento": user[16],
                "ai_requests_today": user[17] or 0,
                "ai_request_limit": user[18] or 10
            }


        else:
            # Increment failed attempts
            failed_attempts = (lockout_data[1] if lockout_data else 0) + 1
            
            if failed_attempts >= 3:
                # Lock out for 5 minutes
                from datetime import timedelta
                lockout_until = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
                c.execute("UPDATE users SET failed_login_attempts = ?, lockout_until = ? WHERE username = ?", 
                         (failed_attempts, lockout_until, username))
                conn.commit()
                conn.close()
                return {"error": "locked", "remaining_seconds": 300}
            else:
                c.execute("UPDATE users SET failed_login_attempts = ? WHERE username = ?", (failed_attempts, username))
                conn.commit()
                conn.close()
                return None
    
    conn.close()
    return None

def check_subscription_status(username):
    """Deactivate user if trial/paid period has expired."""
    from datetime import datetime
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT expiration_date FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if row and row[0]:
        if datetime.utcnow().strftime('%Y-%m-%d') > row[0]:
            c.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
            conn.commit()
    conn.close()

def increment_request_count(username):
    """Increment daily request count, reset if new day. Returns (can_request, remaining_requests)."""
    from datetime import datetime
    today = datetime.utcnow().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT requests_today, last_request_date, daily_request_limit FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    requests = row[0] or 0
    last_date = row[1]
    limit = row[2] or 20
    
    if last_date != today:
        requests = 0  # reset for new day
    if requests >= limit:
        conn.close()
        return False, 0  # No more requests allowed, 0 remaining
    requests += 1
    c.execute("UPDATE users SET requests_today = ?, last_request_date = ? WHERE username = ?", (requests, today, username))
    conn.commit()
    conn.close()
    remaining = limit - requests
    return True, remaining  # Request allowed, return remaining count

def extend_subscription(username, days):
    """Add `days` to the user's expiration_date (admin use)."""
    from datetime import datetime, timedelta
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT expiration_date FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    if row and row[0]:
        current = datetime.strptime(row[0], '%Y-%m-%d')
        new_date = current + timedelta(days=days)
    else:
        new_date = datetime.utcnow() + timedelta(days=days)
    c.execute("UPDATE users SET expiration_date = ?, is_active = 1 WHERE username = ?", (new_date.strftime('%Y-%m-%d'), username))
    conn.commit()
    conn.close()

def get_all_users():
    """Returns a list of all users for the admin panel."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT username, business_name, email, is_active, is_admin, daily_request_limit FROM users", conn)
    conn.close()
    return df

def toggle_user_active(username, current_status):
    """Toggles the is_active status of a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    new_status = not current_status
    c.execute("UPDATE users SET is_active = ? WHERE username = ?", (new_status, username))
    conn.commit()
    conn.close()

def create_default_admin():
    """Creates a default admin user if no admin exists."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM users WHERE is_admin = 1")
    if c.fetchone()[0] == 0:
        # Create default admin: rvargas91 / alphaSoftware!
        print("Creating default admin user...")
        create_user("rvargas91", "alphaSoftware!", "alphasoftpy@gmail.com", "System Admin", is_active=True, is_admin=True, daily_request_limit=30)
    conn.close()

def request_password_reset(username, email):
    """Validates username and email combination. Returns True if match found."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0].lower() == email.lower():
        return True
    return False

def change_password(username, old_password, new_password):
    """Changes user password after validating old password. Returns True if successful."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    
    if result and verify_password(old_password, result[0]):
        new_hash = get_password_hash(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def search_users(query):
    """Search users by username or email. Returns filtered DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT username, business_name, email, is_active, is_admin, daily_request_limit FROM users WHERE username LIKE ? OR email LIKE ?",
        conn,
        params=(f"%{query}%", f"%{query}%")
    )
    conn.close()
    return df

def update_business_profile(username, profile_text):
    """Updates the business profile for a user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET business_profile = ? WHERE username = ?", (profile_text, username))
    conn.commit()
    conn.close()

def get_brain_data(username):
    """
    Gets the brain data as a structured dict.
    NEW STRUCTURE: Multi-service support
    Returns: {
        'info_general': {...},
        'servicios': [...],
        'insights': [...],
        'contexto_manual': ''
    }
    """
    import json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT business_profile FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        try:
            data = json.loads(result[0])
            
            # Migrate old format to new format if needed
            if 'base' in data and 'servicios' not in data:
                # Old format detected, migrate
                return {
                    "info_general": {},
                    "servicios": [],
                    "insights": data.get('insights', []),
                    "contexto_manual": data.get('contexto_manual', '')
                }
            
            # Return data (new or already migrated)
            return data
        except:
            # Invalid JSON, return empty structure
            return {
                "info_general": {},
                "servicios": [],
                "insights": [],
                "contexto_manual": ""
            }
    
    # No data, return empty structure
    return {
        "info_general": {},
        "servicios": [],
        "insights": [],
        "contexto_manual": ""
    }

def update_brain_data(username, brain_data):
    """Updates the brain data with a structured dict."""
    import json
    update_business_profile(username, json.dumps(brain_data, ensure_ascii=False))

def enrich_brain_from_interaction(username, seccion, user_msg, ai_response):
    """
    Analyzes interaction and extracts ONLY valuable insights.
    NEW: Stricter patterns to avoid garbage insights.
    Only captures: real client feedback, specific pain points, actual objections, 
    measurable results, and strategic changes.
    """
    from datetime import datetime
    import json
    
    # Get current brain data
    brain_data = get_brain_data(username)
    
    # Ensure insights list exists
    if 'insights' not in brain_data:
        brain_data['insights'] = []
    
    # Detect insights using STRICT keyword patterns
    insights_to_add = []
    user_lower = user_msg.lower()
    
    # ========== VALUABLE PATTERNS ONLY ==========
    
    # 1. REAL Client Feedback (not generic questions)
    if any(phrase in user_lower for phrase in [
        'mi cliente dijo', 'mi cliente me dijo', 'me dijeron', 'me preguntaron',
        'el cliente me comentó', 'me pidieron', 'me solicitaron',
        'el cliente preguntó', 'me consultaron'
    ]):
        insights_to_add.append({
            'tipo': 'feedback_cliente',
            'contenido': user_msg[:250],
            'timestamp': datetime.utcnow().isoformat(),
            'fuente': seccion
        })
    
    # 2. Specific Pain Points (not generic problems)
    elif any(phrase in user_lower for phrase in [
        'el problema es que', 'el dolor es', 'sufren de', 'les cuesta',
        'no pueden', 'tienen dificultad', 'se les complica',
        'el dolor principal', 'la mayor dificultad'
    ]):
        insights_to_add.append({
            'tipo': 'dolor_cliente',
            'contenido': user_msg[:250],
            'timestamp': datetime.utcnow().isoformat(),
            'fuente': seccion
        })
    
    # 3. REAL Objections (not hypothetical)
    elif any(phrase in user_lower for phrase in [
        'me rechazan porque', 'no compran porque', 'dicen que es muy',
        'se quejan de', 'me objetan', 'no quieren porque',
        'rechazan por', 'no aceptan porque'
    ]):
        insights_to_add.append({
            'tipo': 'objecion_real',
            'contenido': user_msg[:250],
            'timestamp': datetime.utcnow().isoformat(),
            'fuente': seccion
        })
    
    # 4. Measurable Results (must have numbers)
    elif (any(word in user_lower for word in [
        'vendí', 'vendi', 'conseguí', 'consegui', 'logré', 'logre',
        'aumenté', 'aumento', 'cerré', 'cerre', 'generé', 'genere'
    ]) and any(char.isdigit() for char in user_msg)):
        insights_to_add.append({
            'tipo': 'resultado',
            'contenido': user_msg[:250],
            'timestamp': datetime.utcnow().isoformat(),
            'fuente': seccion
        })
    
    # 5. Strategic Changes (actual changes made)
    elif any(phrase in user_lower for phrase in [
        'ahora uso', 'ahora utilizo', 'cambié a', 'cambie a',
        'empecé a', 'empece a', 'dejé de', 'deje de',
        'implementé', 'implemente', 'adopté', 'adopte'
    ]):
        insights_to_add.append({
            'tipo': 'cambio_estrategico',
            'contenido': user_msg[:250],
            'timestamp': datetime.utcnow().isoformat(),
            'fuente': seccion
        })
    
    # ========== IGNORE EVERYTHING ELSE ==========
    # - Generic questions ("¿Cómo hago...?")
    # - AI responses
    # - Avatar information
    # - Generic recommendations
    
    # Add new insights
    for insight in insights_to_add:
        brain_data['insights'].append(insight)
    
    # Limit to last 50 insights
    if len(brain_data['insights']) > 50:
        brain_data['insights'] = brain_data['insights'][-50:]
    
    # Update last modification timestamp
    brain_data['ultima_actualizacion'] = datetime.utcnow().isoformat()
    
    # Save if we added any insights
    if insights_to_add:
        update_brain_data(username, brain_data)
        return len(insights_to_add)
    
    return 0

def save_last_form_data(username, form_data):
    """Saves the last form data for a user as JSON."""
    import json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    form_json = json.dumps(form_data)
    c.execute("UPDATE users SET last_form_data = ? WHERE username = ?", (form_json, username))
    conn.commit()
    conn.close()

def get_last_form_data(username):
    """Retrieves the last form data for a user."""
    import json
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT last_form_data FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        try:
            return json.loads(result[0])
        except:
            return None
    return None

# ========== ESTRATEGIAS FUNCTIONS ==========

def save_estrategia(username, estrategia_data):
    """
    Saves or updates a user's complete strategy.
    estrategia_data should be a dict with keys: avatar, embudo, ads, objeciones, whatsapp, acciones_diarias, kpis
    """
    import json
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if user already has a strategy
    c.execute("SELECT id FROM estrategias WHERE user_id = ?", (username,))
    existing = c.fetchone()
    
    now = datetime.utcnow().isoformat()
    
    # Convert dict values to JSON strings
    avatar_json = json.dumps(estrategia_data.get('avatar', ''))
    embudo_json = json.dumps(estrategia_data.get('embudo', ''))
    ads_json = json.dumps(estrategia_data.get('ads', ''))
    objeciones_json = json.dumps(estrategia_data.get('objeciones', ''))
    whatsapp_json = json.dumps(estrategia_data.get('whatsapp', ''))
    acciones_json = json.dumps(estrategia_data.get('acciones_diarias', ''))
    kpis_json = json.dumps(estrategia_data.get('kpis', ''))
    
    if existing:
        # Update existing strategy
        c.execute("""
            UPDATE estrategias 
            SET avatar = ?, embudo = ?, ads = ?, objeciones = ?, whatsapp = ?, 
                acciones_diarias = ?, kpis = ?, updated_at = ?
            WHERE user_id = ?
        """, (avatar_json, embudo_json, ads_json, objeciones_json, whatsapp_json, 
              acciones_json, kpis_json, now, username))
    else:
        # Insert new strategy
        c.execute("""
            INSERT INTO estrategias 
            (user_id, avatar, embudo, ads, objeciones, whatsapp, acciones_diarias, kpis, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, avatar_json, embudo_json, ads_json, objeciones_json, whatsapp_json,
              acciones_json, kpis_json, now, now))
    
    conn.commit()
    conn.close()
    return True

def get_estrategia(username):
    """
    Retrieves a user's complete strategy.
    Returns a dict with keys: avatar, embudo, ads, objeciones, whatsapp, acciones_diarias, kpis, created_at, updated_at
    Returns None if no strategy exists.
    """
    import json
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT avatar, embudo, ads, objeciones, whatsapp, acciones_diarias, kpis, created_at, updated_at
        FROM estrategias WHERE user_id = ?
    """, (username,))
    result = c.fetchone()
    conn.close()
    
    if result:
        try:
            return {
                'avatar': json.loads(result[0]) if result[0] else '',
                'embudo': json.loads(result[1]) if result[1] else '',
                'ads': json.loads(result[2]) if result[2] else '',
                'objeciones': json.loads(result[3]) if result[3] else '',
                'whatsapp': json.loads(result[4]) if result[4] else '',
                'acciones_diarias': json.loads(result[5]) if result[5] else '',
                'kpis': json.loads(result[6]) if result[6] else '',
                'created_at': result[7],
                'updated_at': result[8]
            }
        except json.JSONDecodeError:
            return None
    return None

def update_estrategia_section(username, section_name, section_content):
    """
    Updates a specific section of the user's strategy.
    section_name should be one of: avatar, embudo, ads, objeciones, whatsapp, acciones_diarias, kpis
    """
    import json
    from datetime import datetime
    
    valid_sections = ['avatar', 'embudo', 'ads', 'objeciones', 'whatsapp', 'acciones_diarias', 'kpis']
    if section_name not in valid_sections:
        return False
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    content_json = json.dumps(section_content)
    
    # Check if strategy exists
    c.execute("SELECT id FROM estrategias WHERE user_id = ?", (username,))
    if c.fetchone():
        # Update specific section
        query = f"UPDATE estrategias SET {section_name} = ?, updated_at = ? WHERE user_id = ?"
        c.execute(query, (content_json, now, username))
        conn.commit()
        conn.close()
        return True
    else:
        # No strategy exists yet, create one with this section
        conn.close()
        estrategia_data = {section_name: section_content}
        return save_estrategia(username, estrategia_data)

def has_estrategia(username):
    """Checks if a user has a saved strategy."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM estrategias WHERE user_id = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# ========== HISTORIAL SECCIONES FUNCTIONS ==========

def save_section_history(username, seccion, tipo, contenido):
    """
    Saves a section interaction to history.
    
    Args:
        username: user's username
        seccion: section name (e.g., 'avatar', 'embudo', 'ads', etc.)
        tipo: interaction type ('user' or 'assistant')
        contenido: content of the interaction
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    c.execute("""
        INSERT INTO historial_secciones (user_id, seccion, tipo, contenido, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (username, seccion, tipo, contenido, now))
    
    conn.commit()
    conn.close()
    return True

def get_section_history(username, seccion, limit=None):
    """
    Retrieves history for a specific section.
    
    Args:
        username: user's username
        seccion: section name
        limit: optional limit on number of entries to return (most recent first)
    
    Returns:
        List of dicts with keys: id, tipo, contenido, timestamp
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if limit:
        c.execute("""
            SELECT id, tipo, contenido, timestamp
            FROM historial_secciones
            WHERE user_id = ? AND seccion = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (username, seccion, limit))
    else:
        c.execute("""
            SELECT id, tipo, contenido, timestamp
            FROM historial_secciones
            WHERE user_id = ? AND seccion = ?
            ORDER BY timestamp ASC
        """, (username, seccion))
    
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'tipo': row[1],
            'contenido': row[2],
            'timestamp': row[3]
        })
    
    return history

def get_all_section_history(username):
    """
    Retrieves all section history for a user, grouped by section.
    
    Returns:
        Dict with section names as keys and list of interactions as values
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""
        SELECT seccion, tipo, contenido, timestamp
        FROM historial_secciones
        WHERE user_id = ?
        ORDER BY seccion, timestamp ASC
    """, (username,))
    
    rows = c.fetchall()
    conn.close()
    
    history_by_section = {}
    for row in rows:
        seccion = row[0]
        if seccion not in history_by_section:
            history_by_section[seccion] = []
        
        history_by_section[seccion].append({
            'tipo': row[1],
            'contenido': row[2],
            'timestamp': row[3]
        })
    
    return history_by_section

def clear_section_history(username, seccion=None):
    """
    Clears section history.
    
    Args:
        username: user's username
        seccion: optional section name. If None, clears all history for user
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if seccion:
        c.execute("DELETE FROM historial_secciones WHERE user_id = ? AND seccion = ?", (username, seccion))
    else:
        c.execute("DELETE FROM historial_secciones WHERE user_id = ?", (username,))
    
    conn.commit()
    conn.close()
    return True

# ==================== COMPACTION FUNCTIONS ====================

def save_archived_conversation(username, seccion, resumen, mensajes_count):
    """
    Saves a compacted conversation summary to conversaciones_archivadas table.
    """
    from datetime import datetime
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    timestamp = datetime.utcnow().isoformat()
    
    c.execute("""
        INSERT INTO conversaciones_archivadas 
        (user_id, seccion, resumen, mensajes_count, timestamp, expandible)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (username, seccion, resumen, mensajes_count, timestamp))
    
    conn.commit()
    conn.close()
    return True

def get_archived_conversations(username, seccion=None, limit=3):
    """
    Retrieves archived conversations for a user.
    If seccion is specified, only returns archives for that section.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if seccion:
        c.execute("""
            SELECT id, seccion, resumen, mensajes_count, timestamp
            FROM conversaciones_archivadas
            WHERE user_id = ? AND seccion = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (username, seccion, limit))
    else:
        c.execute("""
            SELECT id, seccion, resumen, mensajes_count, timestamp
            FROM conversaciones_archivadas
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (username, limit))
    
    results = c.fetchall()
    conn.close()
    
    archives = []
    for row in results:
        archives.append({
            'id': row[0],
            'seccion': row[1],
            'resumen': row[2],
            'mensajes_count': row[3],
            'timestamp': row[4]
        })
    
    return archives

def compact_section_history(username, seccion, ai_agent):
    """
    Compacts section history by:
    1. Getting all messages from historial_secciones
    2. Generating summary with AI
    3. Extracting valuable insights
    4. Saving to conversaciones_archivadas
    5. Deleting individual messages
    
    Returns: (success, summary, insights_count)
    """
    from datetime import datetime
    
    # Get all messages for this section
    messages = get_section_history(username, seccion)
    
    if not messages or len(messages) == 0:
        return (False, "No messages to compact", 0)
    
    # Build conversation text for AI
    conversation_text = ""
    for msg in messages:
        role = "Usuario" if msg['tipo'] == 'user' else "Asistente"
        conversation_text += f"{role}: {msg['contenido']}\n\n"
    
    # Generate summary with AI
    try:
        summary_prompt = f"""Analiza la siguiente conversación y genera un resumen CONCISO (máximo 150 palabras) que capture:
1. El tema principal discutido
2. Las decisiones o conclusiones clave
3. Información valiosa para recordar

Conversación:
{conversation_text}

Resumen:"""
        
        summary = ai_agent.chat(summary_prompt)
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        summary = f"Conversación sobre {seccion} ({len(messages)} mensajes)"
    
    # Extract insights from the conversation
    insights_count = 0
    for msg in messages:
        if msg['tipo'] == 'user':
            # Find corresponding assistant response
            assistant_msg = next((m for m in messages if m['tipo'] == 'assistant' and m['timestamp'] > msg['timestamp']), None)
            if assistant_msg:
                insights_added = enrich_brain_from_interaction(username, seccion, msg['contenido'], assistant_msg['contenido'])
                insights_count += insights_added
    
    # Save archived conversation
    save_archived_conversation(username, seccion, summary, len(messages))
    
    # Delete individual messages
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM historial_secciones WHERE user_id = ? AND seccion = ?", (username, seccion))
    conn.commit()
    conn.close()
    
    return (True, summary, insights_count)

def should_compact_section(username, seccion, message_count_threshold=10):
    """
    Checks if a section should be compacted based on message count.
    """
    messages = get_section_history(username, seccion)
    return len(messages) >= message_count_threshold

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
        'estrategias_dia': 5,
        'consultas_ia_dia': 10
    },
    'mensual': {
        'duracion_dias': 30,
        'estrategias_dia': 5,
        'consultas_ia_dia': 10
    },
    'trimestral': {
        'duracion_dias': 90,
        'estrategias_dia': 10,
        'consultas_ia_dia': 20
    },
    'semestral': {
        'duracion_dias': 180,
        'estrategias_dia': 15,
        'consultas_ia_dia': 30
    },
    'anual': {
        'duracion_dias': 360,
        'estrategias_dia': 15,
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

def clear_base_info(username):
    """
    Clears ALL business information from the brain (servicios + info_general).
    """
    brain_data = get_brain_data(username)
    brain_data['info_general'] = {}
    brain_data['servicios'] = []
    update_brain_data(username, brain_data)
    return True

def delete_insight(username, insight_index):
    """
    Deletes a single insight by index.
    """
    brain_data = get_brain_data(username)
    insights = brain_data.get('insights', [])
    
    if 0 <= insight_index < len(insights):
        del insights[insight_index]
        brain_data['insights'] = insights
        update_brain_data(username, brain_data)
        return True
    return False

def delete_service(username, service_id):
    """
    Deletes a complete service by ID.
    """
    brain_data = get_brain_data(username)
    servicios = brain_data.get('servicios', [])
    
    brain_data['servicios'] = [s for s in servicios if s.get('id') != service_id]
    update_brain_data(username, brain_data)
    return True

def delete_diferenciador(username, service_id, diferenciador_text):
    """
    Deletes a single diferenciador from a service.
    """
    brain_data = get_brain_data(username)
    servicios = brain_data.get('servicios', [])
    
    for servicio in servicios:
        if servicio.get('id') == service_id:
            difs = servicio.get('diferenciadores', [])
            servicio['diferenciadores'] = [d for d in difs if d != diferenciador_text]
            break
    
    brain_data['servicios'] = servicios
    update_brain_data(username, brain_data)
    return True

def generate_service_id(nombre_servicio):
    """
    Generates a unique ID for a service based on its name.
    """
    import re
    # Remove special chars, convert to lowercase, replace spaces with underscores
    service_id = re.sub(r'[^a-z0-9\s]', '', nombre_servicio.lower())
    service_id = service_id.replace(' ', '_')
    return service_id[:50]  # Limit length

def add_or_update_service(username, service_data):
    """
    Adds a new service or updates existing one.
    service_data should include: nombre, rubro, precio, tipo_venta, diferenciador, etc.
    """
    from datetime import datetime
    
    brain_data = get_brain_data(username)
    servicios = brain_data.get('servicios', [])
    
    # Generate service ID
    service_id = generate_service_id(service_data['nombre'])
    
    # Check if service already exists
    existing_service = next((s for s in servicios if s['id'] == service_id), None)
    
    if existing_service:
        # UPDATE existing service
        existing_service['precio'] = service_data.get('precio', existing_service.get('precio'))
        existing_service['rubro'] = service_data.get('rubro', existing_service.get('rubro'))
        existing_service['tipo_venta'] = service_data.get('tipo_venta', existing_service.get('tipo_venta'))
        existing_service['estrategias_generadas'] = existing_service.get('estrategias_generadas', 0) + 1
        existing_service['ultima_estrategia'] = datetime.utcnow().isoformat()
        
        # Add diferenciador if new
        if service_data.get('diferenciador'):
            difs = existing_service.get('diferenciadores', [])
            if service_data['diferenciador'] not in difs:
                difs.append(service_data['diferenciador'])
            existing_service['diferenciadores'] = difs
    else:
        # ADD new service
        new_service = {
            'id': service_id,
            'nombre': service_data['nombre'],
            'emoji': detect_emoji_for_service(service_data.get('rubro', '')),
            'descripcion': service_data.get('descripcion', ''),
            'rubro': service_data.get('rubro', ''),
            'precio': service_data.get('precio', ''),
            'tipo_venta': service_data.get('tipo_venta', ''),
            'diferenciadores': [service_data.get('diferenciador')] if service_data.get('diferenciador') else [],
            'estrategias_generadas': 1,
            'ultima_estrategia': datetime.utcnow().isoformat()
        }
        servicios.append(new_service)
    
    brain_data['servicios'] = servicios
    update_brain_data(username, brain_data)
    return True

def detect_emoji_for_service(rubro):
    """
    Detects appropriate emoji based on service rubro/category.
    """
    rubro_lower = rubro.lower()
    
    emoji_map = {
        'software': '💻',
        'tecnología': '⚙️',
        'web': '🌐',
        'marketing': '📊',
        'automatización': '🤖',
        'consultoría': '💼',
        'educación': '🎓',
        'capacitación': '📚',
        'diseño': '🎨',
        'ventas': '💰',
        'desarrollo': '🔧'
    }
    
    for key, emoji in emoji_map.items():
        if key in rubro_lower:
            return emoji
    
    return '📦'  # Default emoji

# Auto-initialize database when module is imported
# This ensures the database and table exist before any operations
try:
    init_db()
    create_default_admin()
except Exception as e:
    print(f"Warning: Database initialization error: {e}")
