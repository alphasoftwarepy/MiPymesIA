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
        
    # Remove markdown bold markers
    text = text.replace('**', '').replace('__', '')
    
    # Common replacements
    replacements = {
        '"': '"', '"': '"', ''': "'", ''': "'",
        '—': '-', '–': '-', '…': '...',
        '¿': '?', '¡': '!',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'Ñ': 'N',
        'ü': 'u', 'Ü': 'U',
        '“': '"', '”': '"', '‘': "'", '’': "'"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
        
    # Ensure text is latin-1 compatible
    # We normalize to NFKD to decompose characters (e.g. é -> e + ´) then drop non-ascii
    # But for Spanish we want to keep accents if possible in Latin-1
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except:
        return text

def parse_sections(strategy_text):
    """Parses the strategy text into a dictionary of sections"""
    sections = {}
    current_section = None
    buffer = []
    
    lines = strategy_text.split('\n')
    for line in lines:
        if '<<<SECTION_START:' in line:
            if current_section:
                sections[current_section] = '\n'.join(buffer)
            
            current_section = line.split(':')[1].strip().replace('>>>', '')
            buffer = []
        else:
            if current_section:
                buffer.append(line)
                
    if current_section:
        sections[current_section] = '\n'.join(buffer)
        
    return sections

def render_markdown_content(pdf, text):
    """Renders markdown-like content to PDF"""
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue
            
        clean_line = clean_text(line)
        
        # Headers
        if line.startswith('###') or line.startswith('##'):
            pdf.ln(2)
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(41, 128, 185)
            pdf.multi_cell(0, 6, clean_line.replace('#', '').strip())
            pdf.set_text_color(0, 0, 0)
        
        # Bold lines (simple heuristic)
        elif line.startswith('**') and line.endswith('**'):
            pdf.ln(1)
            pdf.set_font('Arial', 'B', 10)
            pdf.multi_cell(0, 5, clean_line)
        
        # List items
        elif line.startswith('-') or line.startswith('•') or (len(line) > 0 and line[0].isdigit() and line[1] == '.'):
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, f"  {clean_line}")
            
        # Regular text
        else:
            # Check for inline bold (simple)
            if ':' in clean_line and len(clean_line.split(':')[0]) < 50:
                parts = clean_line.split(':', 1)
                pdf.set_font('Arial', 'B', 10)
                pdf.write(5, parts[0] + ':')
                pdf.set_font('Arial', '', 10)
                pdf.write(5, parts[1])
                pdf.ln()
            else:
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 5, clean_line)

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
        pdf.cell(0, 10, f"Empresa: {clean_text(business_info.get('nombre', ''))}", 0, 1, 'C')
        pdf.cell(0, 10, f"Rubro: {clean_text(business_info.get('rubro', ''))}", 0, 1, 'C')
    
    pdf.ln(30)
    pdf.set_font('Arial', 'I', 10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f"Generado el {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
    pdf.cell(0, 10, 'Powered by Generador MiPymesIA', 0, 1, 'C')
    
    # === PAGE 2: BUSINESS DATA ===
    pdf.add_page()
    pdf.section_title('Datos del Negocio')
    
    if business_info:
        pdf.info_card('Nombre del Negocio', clean_text(business_info.get('nombre', 'N/A')))
        pdf.info_card('Rubro', clean_text(business_info.get('rubro', 'N/A')))
        pdf.info_card('Tipo de Negocio', clean_text(business_info.get('tipo', 'N/A')))
        pdf.info_card('Producto/Servicio Estrella', clean_text(business_info.get('producto', 'N/A')))
        
        if business_info.get('precio'):
            pdf.info_card('Precio', f"${business_info.get('precio')} USD")
        
        pdf.info_card('Meta Principal', clean_text(business_info.get('meta', 'N/A')))
        pdf.info_card('Presupuesto Mensual', f"${business_info.get('presupuesto', 'N/A')} USD")
        pdf.info_card('Plataformas de Publicidad', clean_text(business_info.get('plataforma', 'N/A')))
        pdf.info_card('Modalidad de Venta', clean_text(business_info.get('modalidad_venta', 'N/A')))
    
    # === PAGE 3: EXECUTIVE SUMMARY ===
    pdf.add_page()
    pdf.section_title('Resumen Ejecutivo')
    
    summary_intro = f"""Esta estrategia de marketing ha sido diseñada específicamente para {business_info.get('nombre', 'su negocio') if business_info else 'su negocio'}, con el objetivo de {business_info.get('meta', 'alcanzar sus metas comerciales').lower() if business_info else 'alcanzar sus metas comerciales'}."""
    
    pdf.body_text(clean_text(summary_intro))
    pdf.ln(5)
    
    pdf.subsection_title("El Plan Incluye:")
    
    items = [
        ("1. Definición del Cliente Ideal (Avatar)", "Análisis detallado de quién es su cliente, sus dolores, deseos y objeciones."),
        ("2. Estrategia de Contenido (Embudo)", "Plan de contenidos semanal dividido en Atracción, Consideración y Venta."),
        ("3. Publicidad Pagada (Ads)", "Estructura de campañas segmentadas para tráfico frío, tibio y caliente."),
        ("4. Flujo de Cierre por WhatsApp", "Guiones y pasos exactos para convertir interesados en clientes en 7 días."),
        ("5. Manejo de Objeciones", "Respuestas preparadas para las principales barreras de compra."),
        ("6. Rutina de Alto Rendimiento", "Checklist de acciones diarias para mantener la constancia."),
        ("7. Métricas y Optimización", "Indicadores clave (KPIs) para medir y mejorar resultados.")
    ]
    
    for title, desc in items:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, clean_text(title), 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, clean_text(desc))
        pdf.ln(2)
        
    pdf.ln(5)
    pdf.body_text(clean_text("Este documento es su guía paso a paso para implementar una estrategia de marketing profesional."))
    
    # Parse the strategy text
    sections = parse_sections(strategy_text)
    
    # === PAGE 4: AVATAR ===
    pdf.add_page()
    pdf.section_title('1. Definición del Cliente Ideal (Avatar)')
    pdf.body_text(clean_text("Análisis detallado de quién es su cliente, sus dolores, deseos y objeciones para comunicar el mensaje correcto."))
    pdf.ln(5)
    render_markdown_content(pdf, sections.get('AVATAR', 'Contenido no disponible.'))
    
    # === PAGE 5: EMBUDO ===
    pdf.add_page()
    pdf.section_title('2. Estrategia de Contenido (Embudo)')
    pdf.body_text(clean_text("Plan de contenidos semanal dividido en Atracción (TOFU), Consideración (MOFU) y Venta (BOFU)."))
    pdf.ln(5)
    
    pdf.subsection_title("Atracción (TOFU)")
    render_markdown_content(pdf, sections.get('EMBUDO_TOFU', ''))
    pdf.ln(3)
    
    pdf.subsection_title("Consideración (MOFU)")
    render_markdown_content(pdf, sections.get('EMBUDO_MOFU', ''))
    pdf.ln(3)
    
    pdf.subsection_title("Venta (BOFU)")
    render_markdown_content(pdf, sections.get('EMBUDO_BOFU', ''))
    
    # === PAGE 6: ADS ===
    pdf.add_page()
    pdf.section_title('3. Publicidad Pagada (Ads)')
    pdf.body_text(clean_text("Estructura de campañas segmentadas para tráfico frío, tibio y caliente, optimizando su presupuesto."))
    pdf.ln(5)
    
    pdf.subsection_title("Tráfico Frío")
    render_markdown_content(pdf, sections.get('ADS_FRIO', ''))
    pdf.ln(3)
    
    pdf.subsection_title("Tráfico Tibio (Retargeting)")
    render_markdown_content(pdf, sections.get('ADS_TIBIO', ''))
    pdf.ln(3)
    
    pdf.subsection_title("Tráfico Caliente (Cierre)")
    render_markdown_content(pdf, sections.get('ADS_CALIENTE', ''))
    
    # === PAGE 7: WHATSAPP ===
    pdf.add_page()
    pdf.section_title('4. Flujo de Cierre por WhatsApp')
    pdf.body_text(clean_text("Guiones y pasos exactos para convertir interesados en clientes en un periodo de 7 días."))
    pdf.ln(5)
    
    days = ['DIA1', 'DIA2', 'DIA3', 'DIA4', 'DIA5', 'DIA6', 'DIA7']
    for day in days:
        content = sections.get(f'WHATSAPP_{day}', '')
        if content:
            # Extract title from first line if possible
            lines = content.split('\n')
            title = lines[0] if lines else f"Día {day[-1]}"
            body = '\n'.join(lines[1:]) if lines else ''
            
            pdf.subsection_title(clean_text(title))
            render_markdown_content(pdf, body)
            pdf.ln(3)
            
    # === PAGE 8: OBJECTIONS ===
    pdf.add_page()
    pdf.section_title('5. Manejo de Objeciones')
    pdf.body_text(clean_text("Respuestas preparadas para las principales barreras de compra de sus clientes."))
    pdf.ln(5)
    
    objections = ['COSTO', 'TIEMPO', 'PERSONAL', 'INTEGRACION', 'MIEDO']
    for obj in objections:
        content = sections.get(f'OBJECION_{obj}', '')
        if content:
            render_markdown_content(pdf, content)
            pdf.ln(3)
            
    # === PAGE 9: ROUTINE ===
    pdf.add_page()
    pdf.section_title('6. Rutina de Alto Rendimiento')
    pdf.body_text(clean_text("Checklist de acciones diarias para mantener la constancia y el crecimiento."))
    pdf.ln(5)
    render_markdown_content(pdf, sections.get('ACCIONES_DIARIAS', ''))
    
    # === PAGE 10: METRICS ===
    pdf.add_page()
    pdf.section_title('7. Métricas y Optimización')
    pdf.body_text(clean_text("Indicadores clave de rendimiento (KPIs) para medir y mejorar los resultados mes a mes."))
    pdf.ln(5)
    render_markdown_content(pdf, sections.get('METRICAS', ''))
    
    return pdf.output(dest='S').encode('latin-1')
