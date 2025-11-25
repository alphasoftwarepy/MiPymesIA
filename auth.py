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
            lockout_until TEXT
        )
    ''')
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
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

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
                        requests_today, last_request_date, email, daily_request_limit, business_profile 
                 FROM users WHERE username = ?""", (username,))
    user = c.fetchone()

    if user:
        # user structure: (username, password_hash, business_name, is_active, is_admin, start_date, expiration_date, requests_today, last_request_date, email, daily_request_limit, business_profile)
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
                "daily_request_limit": user[10] or 20,
                "business_profile": user[11] or ""
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

# Auto-initialize database when module is imported
# This ensures the database and table exist before any operations
try:
    init_db()
    create_default_admin()
except Exception as e:
    print(f"Warning: Database initialization error: {e}")
