// Auto-playing carousel WITHOUT controls - ErrTimersWithoutControls
// This will trigger the accessibility error for timers without pause/stop controls

(function() {
    const carousel = document.getElementById('carousel');
    if (!carousel) return;

    const items = carousel.querySelectorAll('.carousel-item');
    let currentIndex = 0;

    // Auto-advance carousel every 5 seconds without any user controls
    function nextSlide() {
        // Add exit animation to current slide
        items[currentIndex].classList.add('slide-out');

        // Wait for exit animation, then switch
        setTimeout(() => {
            items[currentIndex].classList.remove('active', 'slide-out');
            currentIndex = (currentIndex + 1) % items.length;

            // Add enter animation to next slide
            items[currentIndex].classList.add('slide-in');
            items[currentIndex].classList.add('active');

            // Remove slide-in class after animation completes
            setTimeout(() => {
                items[currentIndex].classList.remove('slide-in');
            }, 600);
        }, 600);
    }

    // Start auto-playing immediately - no pause button provided
    const interval = setInterval(nextSlide, 5000);

    // Note: No way for users to pause, stop, or hide this animation
    // This violates WCAG 2.2.2 Pause, Stop, Hide
})();
