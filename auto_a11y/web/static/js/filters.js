/**
 * Enhanced filtering system for accessibility reports
 * Supports multiple filter types: issue type, impact, touchpoint, and search
 */

class IssueFilterManager {
    constructor() {
        this.activeFilters = {
            type: new Set(),
            impact: new Set(),
            touchpoint: new Set(),
            testUser: new Set(),  // Filter by authenticated test user
            search: ''
        };

        this.init();
    }

    init() {
        // Only initialize if filter panel exists
        if (!document.querySelector('.filter-panel')) {
            return;
        }

        this.attachEventListeners();
        this.updateCounts();
        this.updateDisplay();
    }

    attachEventListeners() {
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => this.toggleFilter(chip));
        });

        // Touchpoint select filter
        const touchpointFilter = document.getElementById('touchpointFilter');
        if (touchpointFilter) {
            touchpointFilter.addEventListener('change', (e) => {
                this.updateMultiSelect('touchpoint', e.target);
            });
        }

        // Quick search
        const quickSearch = document.getElementById('quickSearch');
        if (quickSearch) {
            quickSearch.addEventListener('input', (e) => {
                this.activeFilters.search = e.target.value.toLowerCase();
                this.applyFilters();
            });
        }

        // Clear filters button
        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }
    }

    toggleFilter(chip) {
        const filterType = chip.dataset.filterType;
        const filterValue = chip.dataset.filterValue;

        if (this.activeFilters[filterType].has(filterValue)) {
            this.activeFilters[filterType].delete(filterValue);
            chip.classList.remove('active');
        } else {
            this.activeFilters[filterType].add(filterValue);
            chip.classList.add('active');
        }

        this.applyFilters();
    }

    updateMultiSelect(filterType, selectElement) {
        this.activeFilters[filterType].clear();

        for (let option of selectElement.selectedOptions) {
            if (option.value && option.value !== '') {
                this.activeFilters[filterType].add(option.value);
            }
        }

        this.applyFilters();
    }

    applyFilters() {
        const allItems = document.querySelectorAll('.issue-item');
        let visibleCount = 0;

        allItems.forEach(item => {
            const shouldShow = this.shouldShowItem(item);

            if (shouldShow) {
                item.classList.remove('filtered-out');
                visibleCount++;
            } else {
                item.classList.add('filtered-out');
            }
        });

        this.updateDisplay();
        this.updateStatistics(visibleCount, allItems.length);
    }

    shouldShowItem(item) {
        // Check type filter
        if (this.activeFilters.type.size > 0) {
            if (!this.activeFilters.type.has(item.dataset.type)) {
                return false;
            }
        }

        // Check impact filter
        if (this.activeFilters.impact.size > 0) {
            if (!this.activeFilters.impact.has(item.dataset.impact)) {
                return false;
            }
        }

        // Check touchpoint filter
        if (this.activeFilters.touchpoint.size > 0) {
            if (!this.activeFilters.touchpoint.has(item.dataset.touchpoint)) {
                return false;
            }
        }

        // Check search filter
        if (this.activeFilters.search) {
            const searchText = [
                item.dataset.id,
                item.dataset.description,
                item.dataset.xpath
            ].join(' ').toLowerCase();

            if (!searchText.includes(this.activeFilters.search)) {
                return false;
            }
        }

        return true;
    }

    updateDisplay() {
        const activeFiltersDiv = document.getElementById('activeFilters');
        const activeFilterTags = document.getElementById('activeFilterTags');

        if (!activeFiltersDiv || !activeFilterTags) return;

        const hasActiveFilters = Object.values(this.activeFilters).some(filter => {
            if (typeof filter === 'string') return filter.length > 0;
            return filter.size > 0;
        });

        if (hasActiveFilters) {
            activeFiltersDiv.style.display = 'block';
            activeFilterTags.innerHTML = '';

            // Display active filters as tags
            Object.entries(this.activeFilters).forEach(([type, values]) => {
                if (typeof values === 'string' && values) {
                    // Search filter
                    const tag = document.createElement('span');
                    tag.className = 'active-filter-tag';
                    tag.innerHTML = `Search: "${values}" <span class="remove-filter" data-type="${type}">×</span>`;
                    activeFilterTags.appendChild(tag);
                } else if (values.size > 0) {
                    // Other filters
                    values.forEach(value => {
                        const tag = document.createElement('span');
                        tag.className = 'active-filter-tag';
                        tag.innerHTML = `${type}: ${value} <span class="remove-filter" data-type="${type}" data-value="${value}">×</span>`;
                        activeFilterTags.appendChild(tag);
                    });
                }
            });

            // Add remove handlers
            activeFilterTags.querySelectorAll('.remove-filter').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const type = e.target.dataset.type;
                    const value = e.target.dataset.value;

                    if (type === 'search') {
                        this.activeFilters.search = '';
                        const searchInput = document.getElementById('quickSearch');
                        if (searchInput) searchInput.value = '';
                    } else if (value) {
                        this.activeFilters[type].delete(value);
                        // Update UI
                        const chip = document.querySelector(`[data-filter-type="${type}"][data-filter-value="${value}"]`);
                        if (chip) chip.classList.remove('active');
                    }

                    this.applyFilters();
                });
            });
        } else {
            activeFiltersDiv.style.display = 'none';
        }
    }

    updateStatistics(visible, total) {
        const visibleCountEl = document.getElementById('visibleCount');
        const totalCountEl = document.getElementById('totalCount');
        const filterSummaryEl = document.getElementById('filterSummary');

        if (visibleCountEl) visibleCountEl.textContent = visible;
        if (totalCountEl) totalCountEl.textContent = total;

        if (filterSummaryEl) {
            // Count by type
            const typeCounts = {};
            document.querySelectorAll('.issue-item:not(.filtered-out)').forEach(item => {
                const type = item.dataset.type;
                typeCounts[type] = (typeCounts[type] || 0) + 1;
            });

            const summary = [];
            if (typeCounts.error) summary.push(`${typeCounts.error} errors`);
            if (typeCounts.warning) summary.push(`${typeCounts.warning} warnings`);
            if (typeCounts.info) summary.push(`${typeCounts.info} info`);
            if (typeCounts.discovery) summary.push(`${typeCounts.discovery} discovery`);

            filterSummaryEl.textContent = summary.join(', ') || 'No items';
        }
    }

    updateCounts() {
        // Count impact levels
        const impactCounts = { high: 0, medium: 0, low: 0 };

        document.querySelectorAll('.issue-item').forEach(item => {
            const impact = item.dataset.impact;
            if (impact && impactCounts.hasOwnProperty(impact)) {
                impactCounts[impact]++;
            }
        });

        const highImpactCount = document.getElementById('highImpactCount');
        const mediumImpactCount = document.getElementById('mediumImpactCount');
        const lowImpactCount = document.getElementById('lowImpactCount');

        if (highImpactCount) highImpactCount.textContent = impactCounts.high;
        if (mediumImpactCount) mediumImpactCount.textContent = impactCounts.medium;
        if (lowImpactCount) lowImpactCount.textContent = impactCounts.low;

        // Update total count
        const totalCount = document.querySelectorAll('.issue-item').length;
        const visibleCount = totalCount;
        this.updateStatistics(visibleCount, totalCount);
    }

    clearAllFilters() {
        // Clear all filter sets
        Object.keys(this.activeFilters).forEach(key => {
            if (typeof this.activeFilters[key] === 'string') {
                this.activeFilters[key] = '';
            } else {
                this.activeFilters[key].clear();
            }
        });

        // Reset UI
        document.querySelectorAll('.filter-chip.active').forEach(chip => {
            chip.classList.remove('active');
        });

        const touchpointFilter = document.getElementById('touchpointFilter');
        if (touchpointFilter) touchpointFilter.selectedIndex = -1;

        const quickSearch = document.getElementById('quickSearch');
        if (quickSearch) quickSearch.value = '';

        this.applyFilters();
    }
}

// Initialize filter manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.filter-panel')) {
        window.issueFilterManager = new IssueFilterManager();
    }
});
