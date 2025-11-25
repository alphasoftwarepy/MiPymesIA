from fpdf import FPDF
import re
from datetime import datetime

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.business_name = ""
        
    def header(self):
        # Professional header
        self.set_fill_color(26, 82, 118)  # Dark blue
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 22)
        self.cell(0, 15, '', 0, 1)
        self.cell(0, 10, 'Estrategia de Marketing Profesional', 0, 1, 'C')
        
        if self.business_name:
            self.set_font('Arial', 'I', 12)
            self.cell(0, 5, self.business_name, 0, 1, 'C')
        
        self.set_text_color(0, 0, 0)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generado por Generador MiPymesIA - {datetime.now().strftime("%d/%m/%Y")} - Pagina {self.page_no()}', 0, 0, 'C')

    def section_title(self, title):
        """Main section title with blue background and text wrapping"""
        self.set_fill_color(41, 128, 185)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        
        # Calculate height needed
        # Standard cell height is 10, but we might need more
        self.multi_cell(0, 10, title, 0, 'L', True)
        
        self.set_text_color(0, 0, 0)
        self.ln(4)
    
    def subsection_title(self, title):
        """Subsection title in bold blue"""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(41, 128, 185)
        self.multi_cell(0, 7, title)
        self.set_text_color(0, 0, 0)
        self.ln(2)
    
    def subsubsection_title(self, title):
        """Sub-subsection in bold"""
        self.set_font('Arial', 'B', 10)
        self.multi_cell(0, 6, title)
        self.ln(1)
    
    def body_text(self, text, bold=False):
        """Regular body text"""
        if bold:
            self.set_font('Arial', 'B', 10)
        else:
            self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, text)
        self.ln(2)
    
    def bullet_item(self, text):
        """Bullet point item with light background"""
        self.set_fill_color(245, 250, 252)
        self.set_font('Arial', '', 10)
        # Add bullet symbol
        self.multi_cell(0, 5, f"  - {text}", 0, 'L', True)
        self.ln(1)
    
    def info_card(self, title, content):
        """Info card with title and content"""
        self.set_fill_color(236, 240, 241)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(41, 128, 185)
        self.cell(0, 7, title, 0, 1)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, content)
        self.ln(3)

def clean_text(text):
    """Cleans text for PDF compatibility"""
    if not text:
        return ""
        
    # Remove markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = text.replace('**', '').replace('__', '')
    
    # Special characters replacements
    replacements = {
        '"': '"', '"': '"', ''': "'", ''': "'",
        '—': '-', '–': '-', '…': '...',
        '¿': '?', '¡': '!',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'Ñ': 'N',
        'ü': 'u', 'Ü': 'U'
    }
    
    # Try to handle encoding issues before replacement
    try:
        # First try to fix common encoding errors
        text = text.encode('latin-1', 'ignore').decode('utf-8', 'ignore')
    except:
        pass

    # Apply manual replacements for problematic chars
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Final safety encode
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except:
        # Fallback: remove non-ascii
        return ''.join([i if ord(i) < 128 else ' ' for i in text])

def extract_bold_text(line):
    """Extract text between ** markers and return (text, is_bold)"""
    bold_pattern = r'\*\*(.+?)\*\*'
    if '**' in line:
        # Has bold text
        return re.sub(bold_pattern, r'\1', line), True
    return line, False

def generate_pdf(strategy_text, business_info=None):
    pdf = PDF()
    
    if business_info:
        pdf.business_name = business_info.get('nombre', '')
    
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # === COVER PAGE ===
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(26, 82, 118)
    pdf.ln(20)
    pdf.cell(0, 15, 'Plan de Marketing', 0, 1, 'C')
    pdf.cell(0, 15, 'y Ventas', 0, 1, 'C')
    
    pdf.set_font('Arial', '', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    if business_info:
        pdf.cell(0, 10, f"Empresa: {business_info.get('nombre', '')}", 0, 1, 'C')
        pdf.cell(0, 10, f"Rubro: {business_info.get('rubro', '')}", 0, 1, 'C')
    
    pdf.ln(30)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f"Generado el {datetime.now().strftime('%d de %B de %Y')}", 0, 1, 'C')
    pdf.cell(0, 10, 'Powered by Generador MiPymesIA', 0, 1, 'C')
    
    # === PAGE 2: BUSINESS DATA ===
    pdf.add_page()
    pdf.section_title('Datos del Negocio')
    
    if business_info:
        pdf.info_card('Nombre del Negocio', business_info.get('nombre', 'N/A'))
        pdf.info_card('Rubro', business_info.get('rubro', 'N/A'))
        pdf.info_card('Tipo de Negocio', business_info.get('tipo', 'N/A'))
        pdf.info_card('Producto/Servicio Estrella', business_info.get('producto', 'N/A'))
        
        if business_info.get('precio'):
            pdf.info_card('Precio', f"${business_info.get('precio')} USD")
        
        pdf.info_card('Meta Principal', business_info.get('meta', 'N/A'))
        pdf.info_card('Presupuesto Mensual', f"${business_info.get('presupuesto', 'N/A')} USD")
        pdf.info_card('Plataformas de Publicidad', business_info.get('plataforma', 'N/A'))
        pdf.info_card('Modalidad de Venta', business_info.get('modalidad_venta', 'N/A'))
    
    # === PAGE 3: EXECUTIVE SUMMARY ===
    pdf.add_page()
    pdf.section_title('Resumen Ejecutivo')
    
    summary_intro = f"""Esta estrategia de marketing ha sido diseñada específicamente para {business_info.get('nombre', 'su negocio') if business_info else 'su negocio'}, con el objetivo de {business_info.get('meta', 'alcanzar sus metas comerciales').lower() if business_info else 'alcanzar sus metas comerciales'}."""
    
    pdf.body_text(clean_text(summary_intro))
    pdf.ln(5)
    
    pdf.subsection_title("El Plan Incluye:")
    
    # Detailed breakdown instead of simple list
    pdf.subsubsection_title("1. Definición del Cliente Ideal (Avatar)")
    pdf.body_text("Análisis detallado de quién es su cliente, sus dolores, deseos y objeciones para comunicar el mensaje correcto.")
    
    pdf.subsubsection_title("2. Estrategia de Contenido (Embudo)")
    pdf.body_text("Plan de contenidos semanal dividido en Atracción (TOFU), Consideración (MOFU) y Venta (BOFU).")
    
    pdf.subsubsection_title("3. Publicidad Pagada (Ads)")
    pdf.body_text("Estructura de campañas segmentadas para tráfico frío, tibio y caliente, optimizando su presupuesto.")
    
    pdf.subsubsection_title("4. Flujo de Cierre por WhatsApp")
    pdf.body_text("Guiones y pasos exactos para convertir interesados en clientes en un periodo de 7 días.")
    
    pdf.subsubsection_title("5. Manejo de Objeciones")
    pdf.body_text("Respuestas preparadas para las principales barreras de compra de sus clientes.")
    
    pdf.subsubsection_title("6. Rutina de Alto Rendimiento")
    pdf.body_text("Checklist de acciones diarias para mantener la constancia y el crecimiento.")
    
    pdf.subsubsection_title("7. Métricas y Optimización")
    pdf.body_text("Indicadores clave de rendimiento (KPIs) para medir y mejorar los resultados mes a mes.")
    
    pdf.ln(5)
    pdf.body_text("Este documento es su guía paso a paso para implementar una estrategia de marketing profesional que genere resultados medibles.")
    
    # === DETAILED STRATEGY ===
    pdf.add_page()
    pdf.section_title('Estrategia Detallada')
    
    clean_strategy = clean_text(strategy_text)
    lines = clean_strategy.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or '<<<' in line:
            continue
        
        # Main section (1., 2., 3. or ## )
        if re.match(r'^\d+\.\s+[A-Z]', line) or re.match(r'^##\s', line):
            header = re.sub(r'^\d+\.\s+', '', line)
            header = re.sub(r'^##\s+', '', header)
            pdf.section_title(clean_text(header))
        
        # Subsection (ALL CAPS: or **Bold**)
        elif (line.isupper() and ':' in line) or (line.startswith('**') and line.endswith('**')):
            pdf.subsection_title(clean_text(line))
        
        # Sub-subsection (### or bold text with :)
        elif line.startswith('###') or (': ' in line and len(line) < 80):
            text, is_bold = extract_bold_text(line)
            pdf.subsubsection_title(clean_text(text))
        
        # List items
        elif line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
            item = re.sub(r'^[-•\d\.]\s*', '', line).strip()
            pdf.bullet_item(clean_text(item))
        
        # Regular text
        else:
            text, is_bold = extract_bold_text(line)
            pdf.body_text(clean_text(text), bold=is_bold)
    
    return pdf.output(dest='S').encode('latin-1')
