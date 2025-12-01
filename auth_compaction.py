
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
