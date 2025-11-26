"""
Carousel component - Auto-rotating image carousel
"""
import streamlit as st

def show(num_images=5):
    """
    Display auto-rotating carousel with images from assets/banner/
    
    Args:
        num_images: Number of images in carousel (default: 5)
    """
    # Generate slides HTML separately to avoid f-string nesting issues
    slides_html = ""
    for i in range(num_images):
        active_class = "active" if i == 0 else ""
        slides_html += f"""<div class="carousel-slide {active_class}" style="background-image: url('assets/banner/banner{i+1}.jpg');"><div class="carousel-overlay"></div></div>"""
    
    # Generate indicators HTML separately
    indicators_html = ""
    for i in range(num_images):
        active_class = "active" if i == 0 else ""
        indicators_html += f'<div class="carousel-dot {active_class}"></div>'

    st.markdown(f"""
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
    
    // Auto-rotate every 4 seconds
    setInterval(nextSlide, 4000);
    
    // Click handlers for dots
    dots.forEach((dot, index) => {{
        dot.addEventListener('click', () => {{
            currentSlide = index;
            showSlide(currentSlide);
        }});
    }});
    </script>
    """, unsafe_allow_html=True)
