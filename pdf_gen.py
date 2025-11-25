from fpdf import FPDF
import re

class PDF(FPDF):
    def header(self):
        # Logo/Title area with color
        self.set_fill_color(41, 128, 185)  # Blue background
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_text_color(255, 255, 255)  # White text
        self.set_font('Arial', 'B', 24)
        self.cell(0, 20, '', 0, 1)
        self.cell(0, 10, 'Estrategia de Marketing', 0, 1, 'C')
        self.set_text_color(0, 0, 0)  # Reset to black
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generado por SG MiPymes IA - Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label, level=1):
        if level == 1:
            # Main section header with colored background
            self.set_fill_color(52, 152, 219)  # Light blue
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

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln(2)
    
    def add_box(self, text, color=(240, 240, 240)):
        """Add a colored box with text"""
        self.set_fill_color(*color)
        self.set_font('Arial', '', 10)
        # Calculate height needed
        self.multi_cell(0, 6, text, 0, 'L', True)
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

def generate_pdf(strategy_text):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
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
        
        # Detect main headers (1., 2., 3., etc. or **Header**)
        if re.match(r'^\d+\.\s+\*\*.*\*\*', line) or re.match(r'^\d+\.\s+[A-Z]', line):
            # Main section
            header_text = re.sub(r'^\d+\.\s+', '', line)
            header_text = header_text.replace('**', '').replace('*', '')
            pdf.chapter_title(header_text, level=1)
            in_list = False
        
        # Detect subsections (LUNES, MARTES, etc. or **Subsection**)
        elif re.match(r'^\*\*[A-Z]+.*\*\*:', line) or line.isupper() and ':' in line:
            subsection_text = line.replace('**', '').replace('*', '')
            pdf.chapter_title(subsection_text, level=2)
            in_list = False
        
        # Detect list items (-, •, [ ])
        elif line.startswith('-') or line.startswith('•') or line.startswith('[ ]'):
            if not in_list:
                in_list = True
            # Add as box item
            item_text = line.lstrip('-•[ ]').strip()
            pdf.add_box(f"  {item_text}", color=(245, 245, 245))
        
        # Regular paragraph
        else:
            pdf.chapter_body(line)
            in_list = False
    
    return pdf.output(dest='S').encode('latin-1')
