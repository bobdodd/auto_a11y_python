/**
 * Client-side navigation helpers for static accessibility reports
 * Provides keyboard shortcuts and navigation utilities
 */

class ReportNavigation {
    constructor() {
        this.currentPage = this.getCurrentPageNumber();
        this.totalPages = this.getTotalPages();
        this.initializeKeyboardShortcuts();
    }

    /**
     * Get current page number from URL
     */
    getCurrentPageNumber() {
        const match = window.location.pathname.match(/page_(\d+)\.html/);
        return match ? parseInt(match[1], 10) : null;
    }

    /**
     * Get total number of pages from manifest or navigation
     */
    getTotalPages() {
        // Try to get from navigation dropdown
        const dropdown = document.querySelector('.dropdown-menu');
        if (dropdown) {
            const items = dropdown.querySelectorAll('.dropdown-item');
            return items.length;
        }
        return 0;
    }

    /**
     * Navigate to a specific page number
     */
    goToPage(pageNum) {
        if (pageNum < 1 || pageNum > this.totalPages) {
            console.warn('Invalid page number:', pageNum);
            return;
        }

        const paddedNum = String(pageNum).padStart(3, '0');
        window.location.href = `page_${paddedNum}.html`;
    }

    /**
     * Navigate to next page
     */
    nextPage() {
        if (this.currentPage && this.currentPage < this.totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }

    /**
     * Navigate to previous page
     */
    prevPage() {
        if (this.currentPage && this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    /**
     * Navigate to index page
     */
    goToIndex() {
        window.location.href = '../index.html';
    }

    /**
     * Navigate to summary page
     */
    goToSummary() {
        window.location.href = '../summary.html';
    }

    /**
     * Initialize keyboard shortcuts
     */
    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ignore if user is typing in an input field
            if (e.target.tagName === 'INPUT' ||
                e.target.tagName === 'TEXTAREA' ||
                e.target.tagName === 'SELECT') {
                return;
            }

            // Arrow keys for navigation
            if (e.key === 'ArrowLeft' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.prevPage();
            } else if (e.key === 'ArrowRight' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.nextPage();
            }

            // Home key - go to index
            else if (e.key === 'Home' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.goToIndex();
            }

            // 'i' key - go to index
            else if (e.key === 'i' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.goToIndex();
            }

            // 's' key - go to summary
            else if (e.key === 's' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.goToSummary();
            }

            // 'g' key - go to page (show prompt)
            else if (e.key === 'g' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.promptGoToPage();
            }
        });
    }

    /**
     * Show prompt to go to specific page
     */
    promptGoToPage() {
        const pageNum = prompt(`Go to page (1-${this.totalPages}):`);
        if (pageNum) {
            const num = parseInt(pageNum, 10);
            if (!isNaN(num)) {
                this.goToPage(num);
            }
        }
    }

    /**
     * Scroll to top of page
     */
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    /**
     * Add "Back to Top" button
     */
    addBackToTopButton() {
        const button = document.createElement('button');
        button.id = 'back-to-top';
        button.className = 'btn btn-primary';
        button.innerHTML = '<i class="bi bi-arrow-up"></i>';
        button.title = 'Back to top';
        button.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
            display: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        `;

        button.addEventListener('click', () => this.scrollToTop());

        document.body.appendChild(button);

        // Show/hide button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                button.style.display = 'block';
            } else {
                button.style.display = 'none';
            }
        });
    }

    /**
     * Update page navigation UI
     */
    updateNavigationUI() {
        // Highlight current page in dropdown
        if (this.currentPage) {
            const dropdownItems = document.querySelectorAll('.dropdown-item');
            dropdownItems.forEach((item, index) => {
                if (index + 1 === this.currentPage) {
                    item.classList.add('active');
                }
            });
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReportNavigation;
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.reportNav === 'undefined') {
        window.reportNav = new ReportNavigation();
        window.reportNav.addBackToTopButton();
        window.reportNav.updateNavigationUI();
    }
});
