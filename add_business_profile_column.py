import sqlite3

DB_NAME = "users.db"

def add_business_profile_column():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN business_profile TEXT DEFAULT ''")
        print("Column 'business_profile' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error (column might already exist): {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_business_profile_column()
