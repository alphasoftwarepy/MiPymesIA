"""
Database configuration module - PostgreSQL Only
Handles database connection for PostgreSQL.
"""
import os
try:
    import psycopg2
    from psycopg2 import pool
except ImportError:
    psycopg2 = None
    print("⚠️ psycopg2 not installed. Install with: pip install psycopg2-binary")

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL environment variable is required for PostgreSQL")

# Connection pool for better performance
_connection_pool = None

def get_connection_pool():
    """Get or create connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min and max connections
            DATABASE_URL
        )
    return _connection_pool

def get_connection():
    """
    Returns a PostgreSQL database connection.
    """
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"⚠️ PostgreSQL connection failed: {e}")
        raise

class PostgresCursorWrapper:
    """
    Wraps psycopg2 cursor to support '?' placeholders like SQLite.
    """
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None

    def execute(self, query, params=None):
        # Convert '?' to '%s' for PostgreSQL
        pg_query = query.replace('?', '%s')
        
        try:
            if params is None:
                self.cursor.execute(pg_query)
            else:
                self.cursor.execute(pg_query, params)
        except Exception as e:
            print(f"❌ DB Error: {e} | Query: {pg_query}")
            raise e
            
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()
        
    def fetchmany(self, size=None):
        return self.cursor.fetchmany(size)
        
    @property
    def rowcount(self):
        return self.cursor.rowcount
    
    def close(self):
        self.cursor.close()

class PostgresConnectionWrapper:
    """Wraps Postgres connection to provide cursor wrapper"""
    def __init__(self, pg_conn):
        self.pg_conn = pg_conn
    
    def cursor(self):
        return PostgresCursorWrapper(self.pg_conn.cursor())
    
    def commit(self):
        self.pg_conn.commit()
        
    def rollback(self):
        self.pg_conn.rollback()
        
    def close(self):
        self.pg_conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

# Helper functions for boolean values (PostgreSQL uses TRUE/FALSE)
def bool_value(value):
    """Returns boolean value for PostgreSQL."""
    return bool(value) if value is not None else None

def true_value():
    """Returns TRUE for PostgreSQL."""
    return True

def false_value():
    """Returns FALSE for PostgreSQL."""
    return False
