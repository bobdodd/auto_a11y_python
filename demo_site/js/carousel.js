// Auto-playing carousel WITHOUT controls - ErrTimersWithoutControls
// This will trigger the accessibility error for timers without pause/stop controls

(function() {
    const carousel = document.getElementById('carousel');
    if (!carousel) return;

    const items = carousel.querySelectorAll('.carousel-item');
    let currentIndex = 0;

    // Auto-advance carousel every 3 seconds without any user controls
    function nextSlide() {
        items[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % items.length;
        items[currentIndex].classList.add('active');
    }

    // Start auto-playing immediately - no pause button provided
    const interval = setInterval(nextSlide, 3000);

    // Note: No way for users to pause, stop, or hide this animation
    // This violates WCAG 2.2.2 Pause, Stop, Hide
})();
