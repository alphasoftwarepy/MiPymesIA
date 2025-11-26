"""
Carousel component - Auto-rotating image carousel
"""
import base64
import os
import streamlit as st

def get_img_as_base64(file_path):
    """Read image file and convert to base64 string"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return ""

def show(num_images=5):
    """
    Display auto-rotating carousel with images from assets/banner/
    
    Args:
        num_images: Number of images in carousel (default: 5)
    """
    # Generate HTML strings with Base64 images
    slides_html = ""
    for i in range(num_images):
        img_path = f"assets/banner/banner{i+1}.jpg"
        # Check if file exists before trying to load
        if os.path.exists(img_path):
            img_b64 = get_img_as_base64(img_path)
            img_src = f"data:image/jpeg;base64,{img_b64}"
        else:
            # Fallback color if image missing
            img_src = "" 
            
        active_class = "active" if i == 0 else ""
        
        # Use inline style for background image with base64
        if img_src:
            style = f"background-image: url('{img_src}');"
        else:
            style = "background-color: #ddd;" # Fallback gray
            
        slides_html += f'<div class="carousel-slide {active_class}" style="{style}"><div class="carousel-overlay"></div></div>'
    
    indicators_html = ""
    for i in range(num_images):
        active_class = "active" if i == 0 else ""
        indicators_html += f'<div class="carousel-dot {active_class}"></div>'

    # Combine everything into one clean HTML block
    carousel_html = f"""
    <style>
    .carousel-container {{
        position: relative;
        width: 100%;
        height: 350px;
        overflow: hidden;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }}
    .carousel-slide {{
        position: absolute;
        width: 100%;
        height: 100%;
        opacity: 0;
        transition: opacity 1s ease-in-out;
        background-size: cover;
        background-position: center;
    }}
    .carousel-slide.active {{
        opacity: 1;
    }}
    .carousel-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.5));
    }}
    .carousel-indicators {{
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 10px;
        z-index: 10;
    }}
    .carousel-dot {{
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: rgba(255,255,255,0.5);
        cursor: pointer;
        transition: all 0.3s;
    }}
    .carousel-dot.active {{
        background: white;
        width: 30px;
        border-radius: 6px;
    }}
    @media (max-width: 768px) {{
        .carousel-container {{
            height: 200px;
        }}
    }}
    </style>
    
    <div class="carousel-container">
        {slides_html}
        <div class="carousel-indicators">
            {indicators_html}
        </div>
    </div>
    
    <script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-dot');
    const totalSlides = {num_images};
    
    function showSlide(index) {{
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        slides[index].classList.add('active');
        dots[index].classList.add('active');
    }}
    
    function nextSlide() {{
        currentSlide = (currentSlide + 1) % totalSlides;
        showSlide(currentSlide);
    }}
    
    setInterval(nextSlide, 4000);
    
    dots.forEach((dot, index) => {{
        dot.addEventListener('click', () => {{
            currentSlide = index;
            showSlide(currentSlide);
        }});
    }});
    </script>
    """
    
    st.markdown(carousel_html, unsafe_allow_html=True)
