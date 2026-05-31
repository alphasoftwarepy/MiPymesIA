"""
Auto Database Initialization - PostgreSQL Only
Ensures all PostgreSQL tables exist on every app startup (idempotent).
"""
import auth


def auto_initialize():
    """
    Initialize PostgreSQL database on startup.
    Uses CREATE TABLE IF NOT EXISTS — safe to call multiple times.
    """
    print("🔄 Initializing PostgreSQL database schema...")
    try:
        auth.init_db()
        print("✅ PostgreSQL tables verified/created.")
    except Exception as e:
        print(f"❌ Error during DB initialization: {e}")
        raise

    try:
        auth.create_default_admin()
        print("✅ Admin user verified.")
    except Exception as e:
        # Non-fatal: admin may already exist or subscription module unavailable
        print(f"⚠️ Warning during admin setup: {e}")

    return True


if __name__ == "__main__":
    auto_initialize()
