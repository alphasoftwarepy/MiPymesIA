"""
Script para integrar el selector de estrategias en el routing
"""

# Leer el archivo
with open('c:/MiPymesIA/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar el bloque de routing
old_routing = '''        if page == "Generador":
            wizard_page()
        elif page == "Mi Progreso":'''

new_routing = '''        if page == "Generador":
            # Check if user is creating/editing a strategy
            if st.session_state.get('creating_new_strategy') or st.session_state.get('editing_strategy_id'):
                wizard_page()
            elif st.session_state.get('deleting_strategy_id'):
                # Show deletion confirmation
                strategy_selector.handle_strategy_deletion()
                # Also show the selector
                strategy_selector.strategy_selector_page()
            else:
                # Show strategy selector
                strategy_selector.strategy_selector_page()
        elif page == "Mi Progreso":'''

if old_routing in content:
    content = content.replace(old_routing, new_routing)
    print("✅ Routing actualizado correctamente")
    
    # Guardar
    with open('c:/MiPymesIA/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo guardado")
else:
    print("❌ No se encontró el bloque de routing exacto")
    if 'if page == "Generador":' in content:
        print("✅ Pero el routing del Generador existe")
