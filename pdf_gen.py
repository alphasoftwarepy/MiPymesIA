from fpdf import FPDF
import re
from datetime import datetime

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.business_name = ""
        
    def header(self):
        # Professional header with gradient effect (simulated with colors)
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

    def chapter_title(self, label, level=1):
        if level == 1:
            # Main section header
            self.set_fill_color(41, 128, 185)  # Blue
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, label, 0, 1, 'L', True)
            self.set_text_color(0, 0, 0)
            self.ln(3)
        elif level == 2:
            # Subsection header
            self.set_font('Arial', 'B', 12)
            self.set_text_color(41, 128, 185)
            self.cell(0, 8, label, 0, 1, 'L')
            self.set_text_color(0, 0, 0)
            self.ln(2)
        elif level == 3:
            # Sub-subsection
            self.set_font('Arial', 'B', 11)
            self.set_text_color(52, 73, 94)
            self.cell(0, 7, label, 0, 1, 'L')
            self.set_text_color(0, 0, 0)
            self.ln(1)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln(2)
    
    def add_box(self, text, color=(240, 240, 240)):
        """Add a colored box with text"""
        self.set_fill_color(*color)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, text, 0, 'L', True)
        self.ln(2)
    
    def add_info_card(self, title, content, icon=""):
        """Add an info card with title and content"""
        self.set_fill_color(236, 240, 241)
        self.set_draw_color(189, 195, 199)
        
        # Card background
        y_start = self.get_y()
        self.rect(self.get_x() + 5, y_start, 190, 0, 'D')  # Will calculate height
        
        # Title
        self.set_x(self.get_x() + 8)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(41, 128, 185)
        self.cell(0, 7, f"{icon} {title}", 0, 1)
        
        # Content
        self.set_x(self.get_x() + 8)
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(180, 5, content)
        self.ln(3)

def clean_text(text):
    """Cleans text to be compatible with standard FPDF (latin-1)."""
    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = text.replace('**', '').replace('__', '')
    
    # Handle special characters
    replacements = {
        '"': '"', '"': '"', ''': "'", ''': "'",
        '—': '-', '–': '-', '…': '...',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Encode to latin-1, replacing errors
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except:
        return text

def generate_pdf(strategy_text, business_info=None):
    pdf = PDF()
    
    # Set business name for header
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
    
    # === PAGE 2: USER INPUT DATA ===
    pdf.add_page()
    pdf.chapter_title('Datos del Negocio', level=1)
    
    if business_info:
        pdf.add_info_card('Nombre del Negocio', business_info.get('nombre', 'N/A'), '')
        pdf.add_info_card('Rubro', business_info.get('rubro', 'N/A'), '')
        pdf.add_info_card('Tipo de Negocio', business_info.get('tipo', 'N/A'), '')
        pdf.add_info_card('Producto/Servicio Estrella', business_info.get('producto', 'N/A'), '')
        
        if business_info.get('precio'):
            pdf.add_info_card('Precio', f"${business_info.get('precio')} USD", '')
        
        pdf.add_info_card('Meta Principal', business_info.get('meta', 'N/A'), '')
        pdf.add_info_card('Presupuesto Mensual', f"${business_info.get('presupuesto', 'N/A')} USD", '')
        pdf.add_info_card('Plataformas de Publicidad', business_info.get('plataforma', 'N/A'), '')
        pdf.add_info_card('Modalidad de Venta', business_info.get('modalidad_venta', 'N/A'), '')
    
    # === PAGE 3: EXECUTIVE SUMMARY ===
    pdf.add_page()
    pdf.chapter_title('Resumen Ejecutivo', level=1)
    
    pdf.set_font('Arial', '', 10)
    summary_text = f"""Esta estrategia de marketing ha sido disenada especificamente para {business_info.get('nombre', 'su negocio') if business_info else 'su negocio'}, con el objetivo de {business_info.get('meta', 'alcanzar sus metas comerciales').lower() if business_info else 'alcanzar sus metas comerciales'}.

El plan incluye:
- Definicion del cliente ideal (Avatar)
- Estrategia de contenido organico (Embudo TOFU/MOFU/BOFU)
- Campanas de publicidad pagada segmentadas
- Flujo de cierre por WhatsApp de 7 dias
- Manejo profesional de objeciones
- Rutina diaria de acciones de alto rendimiento
- Metricas clave para optimizacion continua

Este documento es su guia paso a paso para implementar una estrategia de marketing profesional que genere resultados medibles."""
    
    pdf.multi_cell(0, 6, clean_text(summary_text))
    pdf.ln(5)
    
    # === DETAILED STRATEGY ===
    pdf.add_page()
    pdf.chapter_title('Estrategia Detallada', level=1)
    
    # Clean text
    clean_strategy = clean_text(strategy_text)
    
    # Split into lines
    lines = clean_strategy.split('\n')
    
    current_section = ""
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip section markers
        if '<<<SECTION_START:' in line or '<<<' in line:
            continue
        
        # Detect main headers (1., 2., 3., etc. or **Header**)
        if re.match(r'^\d+\.?\s+[A-Z]', line) or re.match(r'^#+\s', line):
            # Main section
            header_text = re.sub(r'^\d+\.?\s+', '', line)
            header_text = re.sub(r'^#+\s+', '', header_text)
            header_text = header_text.replace('**', '').replace('*', '')
            pdf.chapter_title(header_text, level=1)
            in_list = False
        
        # Detect subsections (ALL CAPS with colon or **Subsection**)
        elif (line.isupper() and ':' in line) or re.match(r'^\*\*[A-Z].*\*\*', line):
            subsection_text = line.replace('**', '').replace('*', '')
            pdf.chapter_title(subsection_text, level=2)
            in_list = False
        
        # Detect sub-subsections (### or Bold text)
        elif line.startswith('###'):
            subsubsection_text = line.replace('###', '').strip()
            pdf.chapter_title(subsubsection_text, level=3)
            in_list = False
        
        # Detect list items (-, •, [ ], numbers)
        elif line.startswith('-') or line.startswith('•') or line.startswith('[ ]') or re.match(r'^\d+\.', line):
            if not in_list:
                in_list = True
            # Add as box item
            item_text = re.sub(r'^[-•\[\]\d\.]\s*', '', line).strip()
            pdf.add_box(f"  {item_text}", color=(245, 250, 252))
        
        # Regular paragraph
        else:
            pdf.chapter_body(line)
            in_list = False
    
    return pdf.output(dest='S').encode('latin-1')
