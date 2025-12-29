// Infinite loading spinner without screen reader announcement
// WarnInfiniteAnimationSpinner - spinner that never announces completion

(function() {
    const spinner = document.querySelector('.spinner');
    const loadingSection = document.querySelector('.loading-section');

    if (!spinner || !loadingSection) return;

    // Spinner is animated infinitely via CSS
    // It's marked with aria-hidden="true" so screen readers don't know it exists
    // There's no ARIA live region to announce when loading completes
    // The spinner just keeps spinning forever with no status updates

    // Simulate "loading" that never completes
    setTimeout(() => {
        // After 5 seconds, we could hide the spinner, but we don't update screen readers
        // loadingSection.style.display = 'none'; // Commented out to keep it visible

        // No aria-live region, no status update, no announcement
        // Screen reader users have no idea what's happening
    }, 5000);

    // The correct implementation would be:
    // 1. Add aria-live="polite" role="status" to a status element
    // 2. Update the status text when loading completes
    // 3. Either hide the spinner or stop the animation
    // 4. Don't use aria-hidden="true" on important loading indicators
})();
