"""
Carousel component - Auto-rotating image carousel
"""
import base64
import os
import streamlit as st
import uuid

def get_img_as_base64(file_path):
    """Read image file and convert to base64 string"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return ""

def show(num_images=5, height=500):
    """
    Display auto-rotating carousel with images from assets/banner/
    
    Args:
        num_images: Number of images in carousel (default: 5)
        height: Height of the carousel in pixels (default: 500)
    """
    # Generate unique ID for this carousel instance to avoid JS conflicts
    carousel_id = f"carousel-{uuid.uuid4()}"
    
    # Generate HTML strings with Base64 images
    slides_html = ""
    for i in range(num_images):
        img_path = f"assets/banner/banner{i+1}.jpg"
        # Check if file exists before trying to load
        if os.path.exists(img_path):
            img_b64 = get_img_as_base64(img_path)
            img_src = f"data:image/jpeg;base64,{img_b64}"
        else:
            img_src = "" 
            
        active_class = "active" if i == 0 else ""
        
        if img_src:
            style = f"background-image: url('{img_src}');"
        else:
            style = "background-color: #f0f2f6;" # Fallback light gray
            
        slides_html += f'<div class="carousel-slide {active_class}" style="{style}"><div class="carousel-overlay"></div></div>'
    
    indicators_html = ""
    for i in range(num_images):
        active_class = "active" if i == 0 else ""
        # Add onclick handler directly to HTML for robustness
        indicators_html += f'<div class="carousel-dot {active_class}" onclick="moveSlide(\'{carousel_id}\', {i})"></div>'

    # Combine everything into one clean HTML block
    carousel_html = f"""
    <style>
    #{carousel_id} {{
        position: relative;
        width: 100%;
        height: {height}px;
        overflow: hidden;
        border-radius: 20px;
        margin: 20px 0 40px 0;
        box-shadow: 0 15px 40px rgba(0,0,0,0.12);
    }}
    #{carousel_id} .carousel-slide {{
        position: absolute;
        width: 100%;
        height: 100%;
        opacity: 0;
        transition: opacity 0.8s ease-in-out;
        background-size: cover;
        background-position: center;
    }}
    #{carousel_id} .carousel-slide.active {{
        opacity: 1;
    }}
    #{carousel_id} .carousel-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.1) 50%, rgba(0,0,0,0.4) 100%);
    }}
    #{carousel_id} .carousel-indicators {{
        position: absolute;
        bottom: 25px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 12px;
        z-index: 10;
        background: rgba(0,0,0,0.3);
        padding: 8px 16px;
        border-radius: 20px;
        backdrop-filter: blur(4px);
    }}
    #{carousel_id} .carousel-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: rgba(255,255,255,0.6);
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }}
    #{carousel_id} .carousel-dot:hover {{
        background: rgba(255,255,255,0.9);
        transform: scale(1.2);
    }}
    #{carousel_id} .carousel-dot.active {{
        background: white;
        width: 12px;
        height: 12px;
        border-color: rgba(255,255,255,0.3);
        box-shadow: 0 0 10px rgba(255,255,255,0.5);
        transform: scale(1.3);
    }}
    @media (max-width: 768px) {{
        #{carousel_id} {{
            height: 250px;
        }}
    }}
    </style>
    
    <div id="{carousel_id}" class="carousel-container">
        {slides_html}
        {"" if num_images <= 1 else f'<div class="carousel-indicators">{indicators_html}</div>'}
    </div>
    
    <script>
    // Encapsulate logic to avoid global scope pollution
    (function() {{
        const carouselId = "{carousel_id}";
        const totalSlides = {num_images};
        let currentSlide = 0;
        let intervalId;
        
        // Define global function for onclick handlers (attached to window)
        window.moveSlide = function(cId, index) {{
            if (cId !== carouselId) return;
            
            currentSlide = index;
            updateCarousel();
            resetTimer();
        }};
        
        function updateCarousel() {{
            const container = document.getElementById(carouselId);
            if (!container) return;
            
            const slides = container.querySelectorAll('.carousel-slide');
            const dots = container.querySelectorAll('.carousel-dot');
            
            slides.forEach((slide, idx) => {{
                if (idx === currentSlide) {{
                    slide.classList.add('active');
                }} else {{
                    slide.classList.remove('active');
                }}
            }});
            
            dots.forEach((dot, idx) => {{
                if (idx === currentSlide) {{
                    dot.classList.add('active');
                }} else {{
                    dot.classList.remove('active');
                }}
            }});
        }}
        
        function nextSlide() {{
            currentSlide = (currentSlide + 1) % totalSlides;
            updateCarousel();
        }}
        
        function startTimer() {{
            intervalId = setInterval(nextSlide, 5000);
        }}
        
        function resetTimer() {{
            clearInterval(intervalId);
            startTimer();
        }}
        
        // Start auto-rotation
        startTimer();
    }})();
    </script>
    """
    
    st.markdown(carousel_html, unsafe_allow_html=True)
