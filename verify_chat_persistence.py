
import sqlite3
import os
import auth
import time

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def verify_chat():
    print("🧪 Verifying Chat Persistence...\n")
    
    username = "test_chat_user"
    section = "test_section_v1"
    
    # 1. Setup User (ensure exists)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Ensure user exists for FK constraints if any (users table structure handles basic info)
    
    # Check if user exists, if not create
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if not c.fetchone():
        print(f"Creating test user {username}...")
        auth.create_user(username, "pass123", "chat@test.com", "Chat Biz")
    
    # 2. Clear previous history for test section
    print(f"Clearing history for section '{section}'...")
    auth.clear_section_history(username, section)
    
    # 3. Save Messages
    print("Saving messages...")
    msg1_content = "Hola, necesito ayuda con mi buyer persona."
    msg2_content = "Claro, ¿cuál es tu producto principal?"
    
    auth.save_section_history(username, section, "user", msg1_content)
    time.sleep(0.1) # Ensure timestamp diff
    auth.save_section_history(username, section, "assistant", msg2_content)
    
    # 4. Retrieve History
    print("Retrieving history...")
    history = auth.get_section_history(username, section)
    
    # 5. Verify
    print(f"Found {len(history)} messages.")
    
    success = True
    if len(history) != 2:
        print("❌ Error: Expected 2 messages.")
        success = False
    else:
        # Check content (history is ordered by timestamp ASC usually, let's check order)
        # auth.get_section_history returns ordered by ASC (oldest first)?
        # Let's check implementation again.
        # auth.get_section_history:
        # if limit: ORDER BY timestamp DESC
        # else: ORDER BY timestamp ASC
        # So we expect ASC order: User then Assistant
        
        m1 = history[0]
        m2 = history[1]
        
        print(f"Msg 1: [{m1['tipo']}] {m1['contenido']}")
        print(f"Msg 2: [{m2['tipo']}] {m2['contenido']}")
        
        if m1['contenido'] != msg1_content or m1['tipo'] != 'user':
            print("❌ Error: Message 1 mismatch.")
            success = False
            
        if m2['contenido'] != msg2_content or m2['tipo'] != 'assistant':
            print("❌ Error: Message 2 mismatch.")
            success = False
            
    if success:
        print("\n✅ Chat Persistence Verified Successfully!")
    else:
        print("\n❌ Verification FAILED.")

    # Cleanup
    print("\nCleaning up...")
    auth.clear_section_history(username, section)
    # We might leave the user for other tests or delete it.
    # auth.delete_user(username) # Careful with this one
    
    # Just delete user row manually to be clean
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    verify_chat()
