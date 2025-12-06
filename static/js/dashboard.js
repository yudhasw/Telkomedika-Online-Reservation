document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.getElementById('slider-wrapper');
    const indicators = document.getElementById('slider-indicators').children;
    let currentSlide = 0;
    const totalSlides = indicators.length;

    const updateSlider = (index) => {
        const offset = index * -100; 
        wrapper.style.transform = `translateX(${offset / totalSlides}%)`;
        
        Array.from(indicators).forEach((indicator, i) => {
            if (i === index) {
                indicator.classList.replace('bg-gray-300', 'bg-tm-red');
            } else {
                indicator.classList.replace('bg-tm-red', 'bg-gray-300');
            }
        });
        currentSlide = index;
    };

    Array.from(indicators).forEach(indicator => {
        indicator.addEventListener('click', (event) => {
            const slideIndex = parseInt(event.target.getAttribute('data-slide'));
            updateSlider(slideIndex);
        });
    });

    setInterval(() => {
        let nextSlide = (currentSlide + 1) % totalSlides;
        updateSlider(nextSlide);
    }, 5000);

    updateSlider(0);
});