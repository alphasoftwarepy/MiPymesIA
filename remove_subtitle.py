"""
Script para eliminar el subtítulo del loader
"""

# Leer el archivo
with open('c:/MiPymesIA/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la línea
old_line = '                                    <div class="step-text">✨ Creando tu estrategia personalizada ✨</div>'
new_line = ''

if old_line in content:
    content = content.replace(old_line + '\r\n', '')
    content = content.replace(old_line + '\n', '')
    content = content.replace(old_line, '')
    print("✅ Línea eliminada")
    
    # Guardar
    with open('c:/MiPymesIA/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo guardado")
else:
    print("❌ No se encontró la línea exacta")
    # Buscar variaciones
    if "Creando tu estrategia personalizada" in content:
        print("✅ Pero el texto sí existe en el archivo")
