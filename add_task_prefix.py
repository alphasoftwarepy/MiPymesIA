"""
Script para agregar prefijo debug a las tareas
"""

# Leer el archivo
with open('c:/MiPymesIA/tasks_manager.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la línea donde se calculan los puntos
insert_after_line = None
for i, line in enumerate(lines):
    if 'puntos = {"alta": 10, "media": 5, "baja": 3}.get(prioridad, 5)' in line:
        insert_after_line = i
        break

if insert_after_line is not None:
    # Código a insertar
    new_code = '''    
    # ========== AGREGAR PREFIJO DEBUG PARA ESTRATEGIAS ==========
    # Formato: E{id}-{num} ; titulo original
    if estrategia_id:
        # Contar tareas existentes para esta estrategia
        c.execute("""
            SELECT COUNT(*) FROM tareas_diarias 
            WHERE user_id = ? AND estrategia_id = ?
        """, (username, estrategia_id))
        task_count = c.fetchone()[0]
        task_num = task_count + 1
        
        # Agregar prefijo
        titulo_con_prefijo = f"E{estrategia_id}-{task_num} ; {titulo}"
    else:
        titulo_con_prefijo = titulo
    # ============================================================
    
'''
    
    # Insertar el nuevo código
    lines.insert(insert_after_line + 1, new_code)
    
    # Ahora necesitamos reemplazar "titulo" por "titulo_con_prefijo" en el INSERT
    for i in range(insert_after_line, len(lines)):
        if 'INSERT INTO tareas_diarias' in lines[i]:
            # Buscar la línea con VALUES que tiene titulo
            for j in range(i, min(i + 10, len(lines))):
                if 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)' in lines[j]:
                    # Reemplazar en la línea siguiente que tiene los valores
                    for k in range(j, min(j + 3, len(lines))):
                        if '(username, titulo, descripcion' in lines[k]:
                            lines[k] = lines[k].replace('(username, titulo,', '(username, titulo_con_prefijo,')
                            print(f"✅ Reemplazado 'titulo' por 'titulo_con_prefijo' en línea {k+1}")
                            break
                    break
            break
    
    # Guardar el archivo
    with open('c:/MiPymesIA/tasks_manager.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Código insertado después de línea {insert_after_line + 1}")
    print("✅ Archivo guardado")
else:
    print("❌ No se encontró la línea de cálculo de puntos")
