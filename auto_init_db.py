"""
Auto Database Initialization - PostgreSQL Only
This module ensures PostgreSQL database is properly initialized
"""
import db_config

def needs_initialization():
    """Check if database needs initialization."""
    # For PostgreSQL, initialization is handled by auth.init_db() and migrations
    # This function always returns False for PostgreSQL
    return False

def auto_initialize():
    """Automatically initialize database if needed."""
    # PostgreSQL initialization is handled by auth.init_db() on first run
    print("✅ PostgreSQL database initialization handled by auth.init_db()")
    return True

if __name__ == "__main__":
    auto_initialize()
