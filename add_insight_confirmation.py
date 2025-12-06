"""
Script para agregar confirmación al borrar insights individuales
"""

# Leer el archivo
with open('c:/MiPymesIA/business_brain.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Buscar la sección de insights (línea ~143-149)
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Buscar el bloque del botón de borrar insight
    if 'with col_btn:' in line and i > 140 and i < 150:
        # Agregar la línea actual
        new_lines.append(line)
        i += 1
        
        # Agregar comentario
        new_lines.append('                    # Calculate actual index (reversed)\n')
        i += 1  # Saltar la línea del comentario original
        
        # Agregar cálculo del índice
        new_lines.append('                    actual_index = len(insights) - 1 - i\n')
        i += 1  # Saltar la línea del cálculo original
        
        # Agregar lógica de confirmación
        new_lines.append('                    \n')
        new_lines.append('                    # Check if this insight is being deleted\n')
        new_lines.append('                    confirm_key = f"confirm_del_insight_{actual_index}"\n')
        new_lines.append('                    if confirm_key not in st.session_state:\n')
        new_lines.append('                        st.session_state[confirm_key] = False\n')
        new_lines.append('                    \n')
        new_lines.append('                    if not st.session_state[confirm_key]:\n')
        new_lines.append('                        if st.button("🗑️", key=f"del_insight_{actual_index}"):\n')
        new_lines.append('                            st.session_state[confirm_key] = True\n')
        new_lines.append('                            st.rerun()\n')
        new_lines.append('                    else:\n')
        new_lines.append('                        # Show confirmation\n')
        new_lines.append('                        if st.button("✅", key=f"confirm_del_insight_{actual_index}", help="Confirmar eliminación"):\n')
        new_lines.append('                            auth.delete_insight(username, actual_index)\n')
        new_lines.append('                            st.session_state[confirm_key] = False\n')
        new_lines.append('                            st.success("✅ Insight eliminado")\n')
        new_lines.append('                            st.rerun()\n')
        new_lines.append('                        if st.button("❌", key=f"cancel_del_insight_{actual_index}", help="Cancelar"):\n')
        new_lines.append('                            st.session_state[confirm_key] = False\n')
        new_lines.append('                            st.rerun()\n')
        
        # Saltar las líneas viejas del botón (4 líneas)
        i += 4
    else:
        new_lines.append(line)
        i += 1

# Guardar
with open('c:/MiPymesIA/business_brain.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Confirmación agregada para borrar insights individuales")
