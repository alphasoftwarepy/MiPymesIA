"""
Database configuration module
Handles database path for both development and production environments
"""
import os

# Determine database path based on environment
# In production (EasyPanel), use /app/data/ (mounted volume)
# In development, use current directory
def get_db_path():
    """Get the correct database path based on environment."""
    # Check if we're in production (EasyPanel has /app/data directory)
    data_dir = "/app/data"
    if os.path.exists(data_dir) and os.path.isdir(data_dir):
        # Production: use volume-mounted directory
        db_path = os.path.join(data_dir, "users.db")
        print(f"📍 Using production database path: {db_path}")
        return db_path
    else:
        # Development: use current directory
        db_path = "users.db"
        print(f"📍 Using development database path: {db_path}")
        return db_path

# Export DB_NAME for all modules to use
DB_NAME = get_db_path()
