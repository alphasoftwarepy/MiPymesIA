import sqlite3
import hashlib
from passlib.context import CryptContext
import pandas as pd

# Password hashing configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

DB_NAME = "users.db"

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
            last_request_date TEXT
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

def create_user(username, password, business_name="", is_active=False, is_admin=False):
    """Creates a new user in the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_password = get_password_hash(password)
    # Set trial period of 7 days for new users if not explicitly active
    start_date = None
    expiration_date = None
    if not is_active:
        # New user will start trial automatically
        from datetime import datetime, timedelta
        start_date = datetime.utcnow().strftime('%Y-%m-%d')
        expiration_date = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
        is_active = True  # trial users are active until expiration
    try:
        c.execute("INSERT INTO users (username, password, business_name, is_active, is_admin, start_date, expiration_date, requests_today, last_request_date) VALUES (?, ?, ?, ?, ?, ?, ?, 0, NULL)",
                  (username, hashed_password, business_name, is_active, is_admin, start_date, expiration_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Checks credentials, updates subscription status, and returns the user object if valid."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, password, business_name, is_active, is_admin, start_date, expiration_date, requests_today, last_request_date FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if user:
        # user structure: (username, password_hash, business_name, is_active, is_admin, start_date, expiration_date, requests_today, last_request_date)
        if verify_password(password, user[1]):
            # Update subscription status based on expiration_date
            from datetime import datetime
            is_active = bool(user[3])
            expiration = user[6]
            if expiration:
                if datetime.utcnow().strftime('%Y-%m-%d') > expiration:
                    # Expired: deactivate user
                    toggle_user_active(username, False)
                    is_active = False
            return {
                "username": user[0],
                "business_name": user[2],
                "is_active": is_active,
                "is_admin": bool(user[4]),
                "start_date": user[5],
                "expiration_date": user[6],
                "requests_today": user[7] or 0,
                "last_request_date": user[8]
            }
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
    c.execute("SELECT requests_today, last_request_date FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    requests = row[0] or 0
    last_date = row[1]
    if last_date != today:
        requests = 0  # reset for new day
    if requests >= 20:
        conn.close()
        return False, 0  # No more requests allowed, 0 remaining
    requests += 1
    c.execute("UPDATE users SET requests_today = ?, last_request_date = ? WHERE username = ?", (requests, today, username))
    conn.commit()
    conn.close()
    remaining = 20 - requests
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
    df = pd.read_sql_query("SELECT username, business_name, is_active, is_admin FROM users", conn)
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
        # Create default admin: admin / admin123
        # In a real app, this should be changed immediately
        print("Creating default admin user...")
        create_user("admin", "admin123", "System Admin", is_active=True, is_admin=True)
    conn.close()

if __name__ == "__main__":
    init_db()
    create_default_admin()
