/**
 * Client-side search for static accessibility reports
 * Searches across issue descriptions, XPaths, code snippets, and WCAG criteria
 */

class ReportSearch {
    constructor() {
        this.searchTerm = '';
        this.results = [];
        this.currentResultIndex = -1;
        this.highlightClass = 'search-highlight';
        this.initializeSearchUI();
    }

    /**
     * Initialize search UI
     */
    initializeSearchUI() {
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');
        const clearButton = document.getElementById('clear-search');

        if (searchInput) {
            // Search on Enter key
            searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.search(searchInput.value);
                }
            });

            // Debounced search on input
            let debounceTimer;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    if (e.target.value.length >= 3 || e.target.value.length === 0) {
                        this.search(e.target.value);
                    }
                }, 300);
            });
        }

        if (searchButton) {
            searchButton.addEventListener('click', () => {
                if (searchInput) {
                    this.search(searchInput.value);
                }
            });
        }

        if (clearButton) {
            clearButton.addEventListener('click', () => {
                if (searchInput) {
                    searchInput.value = '';
                }
                this.clearSearch();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + F - focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Escape - clear search
            else if (e.key === 'Escape' && document.activeElement === searchInput) {
                this.clearSearch();
                searchInput.blur();
            }

            // F3 or Ctrl/Cmd + G - next result
            else if (e.key === 'F3' || ((e.ctrlKey || e.metaKey) && e.key === 'g')) {
                e.preventDefault();
                if (!e.shiftKey) {
                    this.nextResult();
                } else {
                    this.prevResult();
                }
            }
        });
    }

    /**
     * Perform search across all searchable content
     */
    search(term) {
        this.clearHighlights();
        this.searchTerm = term.trim().toLowerCase();

        if (this.searchTerm.length < 3) {
            this.updateSearchUI(0);
            return;
        }

        this.results = [];

        // Search in accordion items
        const accordionItems = document.querySelectorAll('.accordion-item');
        accordionItems.forEach((item, index) => {
            const content = this.getTextContent(item);
            if (content.toLowerCase().includes(this.searchTerm)) {
                this.results.push({
                    element: item,
                    index: index,
                    type: 'accordion'
                });
            }
        });

        // Search in page cards (for index page)
        const pageCards = document.querySelectorAll('.page-card');
        pageCards.forEach((card, index) => {
            const content = this.getTextContent(card);
            if (content.toLowerCase().includes(this.searchTerm)) {
                this.results.push({
                    element: card,
                    index: index,
                    type: 'page-card'
                });
            }
        });

        // Highlight all results
        this.highlightResults();
        this.updateSearchUI(this.results.length);

        // Show first result
        if (this.results.length > 0) {
            this.currentResultIndex = 0;
            this.scrollToResult(0);
        }
    }

    /**
     * Get text content from element for searching
     */
    getTextContent(element) {
        // Get all text content including data attributes
        let text = element.textContent || '';

        // Include XPath data
        const xpath = element.dataset.xpath;
        if (xpath) {
            text += ' ' + xpath;
        }

        // Include other searchable data attributes
        const searchableAttrs = ['touchpoint', 'impact', 'wcag'];
        searchableAttrs.forEach(attr => {
            const value = element.dataset[attr];
            if (value) {
                text += ' ' + value;
            }
        });

        return text;
    }

    /**
     * Highlight search results
     */
    highlightResults() {
        if (!this.searchTerm) return;

        this.results.forEach(result => {
            this.highlightInElement(result.element, this.searchTerm);
        });
    }

    /**
     * Highlight search term in element
     */
    highlightInElement(element, term) {
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const nodesToReplace = [];
        let node;

        while (node = walker.nextNode()) {
            if (node.nodeValue && node.nodeValue.toLowerCase().includes(term)) {
                nodesToReplace.push(node);
            }
        }

        nodesToReplace.forEach(node => {
            const text = node.nodeValue;
            const regex = new RegExp(`(${this.escapeRegex(term)})`, 'gi');
            const parts = text.split(regex);

            if (parts.length > 1) {
                const fragment = document.createDocumentFragment();

                parts.forEach(part => {
                    if (part.toLowerCase() === term) {
                        const mark = document.createElement('mark');
                        mark.className = this.highlightClass;
                        mark.textContent = part;
                        fragment.appendChild(mark);
                    } else if (part) {
                        fragment.appendChild(document.createTextNode(part));
                    }
                });

                node.parentNode.replaceChild(fragment, node);
            }
        });
    }

    /**
     * Clear all search highlights
     */
    clearHighlights() {
        const highlights = document.querySelectorAll('.' + this.highlightClass);
        highlights.forEach(mark => {
            const parent = mark.parentNode;
            parent.replaceChild(document.createTextNode(mark.textContent), mark);
            parent.normalize();
        });
    }

    /**
     * Clear search and reset UI
     */
    clearSearch() {
        this.searchTerm = '';
        this.results = [];
        this.currentResultIndex = -1;
        this.clearHighlights();
        this.updateSearchUI(0);

        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = '';
        }
    }

    /**
     * Navigate to next search result
     */
    nextResult() {
        if (this.results.length === 0) return;

        this.currentResultIndex = (this.currentResultIndex + 1) % this.results.length;
        this.scrollToResult(this.currentResultIndex);
        this.updateSearchUI(this.results.length, this.currentResultIndex + 1);
    }

    /**
     * Navigate to previous search result
     */
    prevResult() {
        if (this.results.length === 0) return;

        this.currentResultIndex = this.currentResultIndex <= 0
            ? this.results.length - 1
            : this.currentResultIndex - 1;

        this.scrollToResult(this.currentResultIndex);
        this.updateSearchUI(this.results.length, this.currentResultIndex + 1);
    }

    /**
     * Scroll to specific result
     */
    scrollToResult(index) {
        if (index < 0 || index >= this.results.length) return;

        const result = this.results[index];
        const element = result.element;

        // Open accordion if needed
        if (result.type === 'accordion') {
            const button = element.querySelector('.accordion-button');
            if (button && button.classList.contains('collapsed')) {
                button.click();
            }
        }

        // Scroll to element
        setTimeout(() => {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            // Add temporary highlight
            element.classList.add('search-result-highlight');
            setTimeout(() => {
                element.classList.remove('search-result-highlight');
            }, 2000);
        }, 100);
    }

    /**
     * Update search UI with results count
     */
    updateSearchUI(totalResults, currentResult = null) {
        const counter = document.getElementById('search-results-count');
        if (!counter) return;

        if (totalResults === 0) {
            counter.textContent = this.searchTerm.length >= 3 ? 'No results' : '';
        } else if (currentResult !== null) {
            counter.textContent = `${currentResult} of ${totalResults}`;
        } else {
            counter.textContent = `${totalResults} result${totalResults !== 1 ? 's' : ''}`;
        }
    }

    /**
     * Escape special regex characters
     */
    escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// Add CSS for search highlights
const style = document.createElement('style');
style.textContent = `
    .search-highlight {
        background-color: #ffeb3b;
        padding: 0 2px;
        border-radius: 2px;
    }

    .search-result-highlight {
        outline: 3px solid #2196F3;
        outline-offset: 2px;
        transition: outline 0.3s;
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ReportSearch;
}

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.reportSearch === 'undefined') {
        window.reportSearch = new ReportSearch();
    }
});
