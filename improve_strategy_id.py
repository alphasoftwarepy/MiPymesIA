"""
Script para mejorar identificación de estrategias
"""

# Leer el archivo
with open('c:/MiPymesIA/strategy_selector.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar en render_strategy_card_full (línea 104)
content = content.replace(
    '            st.markdown(f"### 🎯 {estrategia[\'nombre\']}")',
    '''            # Mostrar producto + fecha para mejor identificación
            try:
                created = datetime.fromisoformat(estrategia['created_at'])
                fecha_str = created.strftime('%d/%m/%Y')
            except:
                fecha_str = "N/A"
            st.markdown(f"### 🎯 {estrategia['producto']} - {fecha_str}")
            st.caption(f"**Nombre:** {estrategia['nombre']}")'''
)

# Reemplazar en render_strategy_card_compact (línea 145)
content = content.replace(
    '        st.markdown(f"#### 🎯 {estrategia[\'nombre\']}")\n        st.caption(estrategia[\'producto\'][:50] + "..." if len(estrategia[\'producto\']) > 50 else estrategia[\'producto\'])',
    '''        # Mostrar producto + fecha
        try:
            created = datetime.fromisoformat(estrategia['created_at'])
            fecha_str = created.strftime('%d/%m')
        except:
            fecha_str = ""
        titulo = f"{estrategia['producto'][:30]}... - {fecha_str}" if len(estrategia['producto']) > 30 else f"{estrategia['producto']} - {fecha_str}"
        st.markdown(f"#### 🎯 {titulo}")
        st.caption(f"**{estrategia['nombre']}**")'''
)

# Guardar
with open('c:/MiPymesIA/strategy_selector.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Identificación de estrategias mejorada")
