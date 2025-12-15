
import os
# Set dummy API key BEFORE importing tasks_manager to avoid init error
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing-persistence"

import sqlite3
import auth
import tasks_manager
import time

# Use /app/data for production (Easypanel persistent volume), current dir for local dev
DB_PATH = os.getenv("DB_PATH", "/app/data" if os.path.exists("/app/data") else ".")
DB_NAME = os.path.join(DB_PATH, "users.db")

def verify_all():
    print("🧪 Verifying Persistence for 'Mi Progreso' & 'MiPymes IA'...\n")
    
    username = "test_persist_user"
    
    # 1. Setup User
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    auth.create_user(username, "pass123", "persist@test.com", "Persist Biz")
    
    # ==========================================
    # TEST 1: MiPymes IA (General Chat)
    # ==========================================
    print("🔹 Testing 'MiPymes IA' Persistence...")
    auth.clear_section_history(username, 'cerebro')
    
    auth.save_section_history(username, 'cerebro', 'user', 'Hola MiPymes IA')
    time.sleep(0.1)
    auth.save_section_history(username, 'cerebro', 'assistant', 'Hola, ¿en qué puedo ayudarte?')
    
    history = auth.get_section_history(username, 'cerebro')
    if len(history) == 2:
        print("✅ MiPymes IA Chat Saved & Retrieved (2 messages).")
    else:
        print(f"❌ MiPymes IA Failed. Found {len(history)} messages.")

    # ==========================================
    # TEST 2: Mi Progreso (Tasks & Task Chat)
    # ==========================================
    print("\n🔹 Testing 'Mi Progreso' (Tasks & Chat) Persistence...")
    
    # Create Task
    task_title = "Test Persistence Task"
    tasks_manager.create_task(
        username, 
        task_title, 
        "Description", 
        "general", 
        "media", 
        "unica", 
        None
    )
    
    # Retrieve Task
    tasks = tasks_manager.get_tasks_for_week(username) # Should find it in list
    found_task = next((t for t in tasks if t['titulo'] == task_title), None)
    
    if found_task:
        print(f"✅ Task '{task_title}' Saved & Retrieved.")
        
        # --- TEST TASK CHAT PERSISTENCE ---
        task_id = found_task['id']
        chat_section_id = f"task_{task_id}"
        
        print(f"   🔸 Verification Task Chat for Task ID: {task_id}")
        auth.clear_section_history(username, chat_section_id)
        
        auth.save_section_history(username, chat_section_id, "user", "Ayuda con esta tarea")
        time.sleep(0.1)
        auth.save_section_history(username, chat_section_id, "assistant", "Aquí tienes ayuda...")
        
        task_chat_history = auth.get_section_history(username, chat_section_id)
        
        if len(task_chat_history) == 2:
             print("   ✅ Task Chat Persistence Verified.")
        else:
             print(f"   ❌ Task Chat Persistence FAILED. Found {len(task_chat_history)} messages.")
        # ----------------------------------
        
        # Complete Task
        tasks_manager.complete_task(username, found_task['id'])
        
        # Verify Completion Persistence
        tasks_updated = tasks_manager.get_tasks_for_week(username)
        completed_task = next((t for t in tasks_updated if t['id'] == found_task['id']), None)
        
        if completed_task and completed_task['completada']:
             print("✅ Task Completion Persisted.")
        else:
             print("❌ Task Completion Update Failed.")
             
        # Cleanup Task
        tasks_manager.delete_task(username, found_task['id'])
        # Cleanup Chat for Task
        auth.clear_section_history(username, chat_section_id)
        print("✅ Task & Chat Cleanup Verified.")
        
    else:
        print("❌ Task Creation Failed (Not found in DB).")

    # Cleanup User
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    print("\n✅ All Verification Tests Complete.")

if __name__ == "__main__":
    verify_all()
