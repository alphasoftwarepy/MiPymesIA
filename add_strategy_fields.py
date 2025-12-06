"""
Script para agregar campos de identificación de estrategia
"""

# Leer el archivo
with open('c:/MiPymesIA/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar
old_code = '''        with st.form("diagnosis_form"):
            col1, col2 = st.columns(2)'''

new_code = '''        with st.form("diagnosis_form"):
            # ========== STRATEGY IDENTIFICATION ==========
            st.markdown("### 🎯 Identificación de la Estrategia")
            st.caption("Dale un nombre único a esta estrategia")
            
            col_strat1, col_strat2 = st.columns(2)
            with col_strat1:
                nombre_estrategia = st.text_input(
                    "📝 Nombre de la Estrategia",
                    value=saved_data.get('nombre_estrategia', ''),
                    placeholder="ej: Sistema Principal, Hotmart",
                    help="Nombre descriptivo para esta estrategia"
                )
            with col_strat2:
                producto_servicio_desc = st.text_input(
                    "📦 Producto/Servicio",
                    value=saved_data.get('producto_servicio_desc', ''),
                    placeholder="ej: Software SaaS, Curso Online",
                    help="Descripción del producto/servicio"
                )
            
            st.markdown("---")
            # ================================================
            
            col1, col2 = st.columns(2)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✅ Campos de identificación agregados")
    
    # Guardar
    with open('c:/MiPymesIA/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo guardado")
else:
    print("❌ No se encontró el código a reemplazar")
