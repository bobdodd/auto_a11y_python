/**
 * Issue Filtering System for Accessibility Test Results
 * Provides comprehensive filtering by type, impact, WCAG criteria, touchpoint, and affected users
 */

class IssueFilterManager {
    constructor() {
        this.activeFilters = {
            type: new Set(),
            impact: new Set(),
            wcag: new Set(),
            touchpoint: new Set(),
            user: new Set(),
            testUser: new Set(),  // Filter by authenticated test user
            search: ''
        };
        
        // Map issue patterns to affected user groups
        this.issueUserMapping = {
            // Vision impairments
            'color': ['vision'],
            'contrast': ['vision'],
            'images': ['vision'],
            'alt': ['vision'],
            'aria-label': ['vision'],
            'sr-only': ['vision'],
            'screen-reader': ['vision'],
            
            // Motor impairments
            'focus': ['motor', 'vision'],
            'keyboard': ['motor'],
            'tabindex': ['motor'],
            'mouse': ['motor'],
            'hover': ['motor'],
            'click': ['motor'],
            'touch': ['motor'],
            
            // Hearing impairments
            'captions': ['hearing'],
            'audio': ['hearing'],
            'video': ['hearing', 'vision'],
            'transcript': ['hearing'],
            
            // Cognitive impairments
            'headings': ['vision', 'cognitive'],
            'landmarks': ['vision', 'motor', 'cognitive'],
            'forms': ['vision', 'motor', 'cognitive'],
            'labels': ['vision', 'motor', 'cognitive'],
            'language': ['vision', 'cognitive'],
            'timeout': ['motor', 'cognitive'],
            'errors': ['cognitive', 'vision'],
            'instructions': ['cognitive'],
            'navigation': ['cognitive', 'motor'],
            
            // Seizure disorders
            'animation': ['seizure', 'cognitive'],
            'flashing': ['seizure'],
            'blink': ['seizure'],
            'motion': ['seizure', 'cognitive']
        };
        
        this.init();
    }
    
    init() {
        if (!document.querySelector('[data-filterable="true"]')) {
            // No filterable content found
            return;
        }
        
        this.injectFilterUI();
        this.populateFilterOptions();
        this.attachEventListeners();
        this.updateCounts();
        this.updateDisplay();
    }
    
    injectFilterUI() {
        // Find the test results container
        const testResultsCard = document.querySelector('.test-results-card');
        if (!testResultsCard) return;

        // Get translations (fallback to English if not available)
        const t = window.i18n || {};
        const translate = (key) => t[key] || key;

        // Create filter panel HTML
        const filterPanelHTML = `
            <div class="filter-panel mb-3" style="background: #f8f9fa; border-radius: 8px; padding: 1.5rem;">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0"><i class="bi bi-funnel"></i> ${translate('Filter Test Results')}</h5>
                    <button class="btn btn-sm btn-outline-secondary" id="clearFilters">
                        <i class="bi bi-x-circle"></i> ${translate('Clear All')}
                    </button>
                </div>

                <!-- Active Filters Display -->
                <div id="activeFilters" class="mb-3" style="display: none; padding: 1rem; background: #e7f3ff; border-radius: 8px;">
                    <strong>${translate('Active Filters:')}</strong>
                    <div id="activeFilterTags" class="mt-2"></div>
                </div>

                <!-- Filter Statistics -->
                <div class="filter-stats mb-3" style="padding: 0.75rem; background: white; border-radius: 8px; border: 1px solid #dee2e6;">
                    <strong>${translate('Showing:')}</strong>
                    <span id="visibleCount">0</span> ${translate('of')} <span id="totalCount">0</span> ${translate('items')}
                    <span class="text-muted mx-2">|</span>
                    <span id="filterSummary"></span>
                </div>

                <!-- Filter Controls -->
                <div class="row g-3">
                    <!-- Issue Type Filter -->
                    <div class="col-md-6 col-lg-3">
                        <label class="form-label fw-bold small">${translate('Issue Type')}</label>
                        <div class="filter-chips">
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="type" data-filter-value="error">
                                ${translate('Errors')} <span class="badge bg-danger ms-1 error-count">0</span>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="type" data-filter-value="warning">
                                ${translate('Warnings')} <span class="badge bg-warning text-dark ms-1 warning-count">0</span>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="type" data-filter-value="info">
                                ${translate('Info')} <span class="badge bg-info ms-1 info-count">0</span>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="type" data-filter-value="discovery">
                                ${translate('Discovery')} <span class="badge bg-purple ms-1 discovery-count" style="background-color: #6f42c1;">0</span>
                            </button>
                        </div>
                    </div>

                    <!-- Impact Level Filter -->
                    <div class="col-md-6 col-lg-3">
                        <label class="form-label fw-bold small">${translate('Impact Level')}</label>
                        <div class="filter-chips">
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="impact" data-filter-value="high">
                                ${translate('High')} <span class="badge bg-danger ms-1" id="highImpactCount">0</span>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="impact" data-filter-value="medium">
                                ${translate('Medium')} <span class="badge bg-warning text-dark ms-1" id="mediumImpactCount">0</span>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="impact" data-filter-value="low">
                                ${translate('Low')} <span class="badge bg-info ms-1" id="lowImpactCount">0</span>
                            </button>
                        </div>
                    </div>

                    <!-- WCAG Criteria Filter -->
                    <div class="col-md-6 col-lg-3">
                        <label class="form-label fw-bold small">${translate('WCAG Criteria')}</label>
                        <select class="form-select form-select-sm" id="wcagFilter" multiple style="height: 100px;">
                            <option value="">${translate('Loading...')}</option>
                        </select>
                    </div>

                    <!-- Touchpoint Filter -->
                    <div class="col-md-6 col-lg-3">
                        <label class="form-label fw-bold small">${translate('Touchpoint')}</label>
                        <select class="form-select form-select-sm" id="touchpointFilter" multiple style="height: 100px;">
                            <option value="">${translate('Loading...')}</option>
                        </select>
                    </div>
                </div>

                <!-- User Impact Filter -->
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <label class="form-label fw-bold small">${translate('Affected User Groups')}</label>
                        <div class="filter-chips">
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="user" data-filter-value="vision">
                                <i class="bi bi-eye-slash me-1"></i>${translate('Vision')}
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="user" data-filter-value="hearing">
                                <i class="bi bi-ear me-1"></i>${translate('Hearing')}
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="user" data-filter-value="motor">
                                <i class="bi bi-hand-index me-1"></i>${translate('Motor')}
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="user" data-filter-value="cognitive">
                                <i class="bi bi-brain me-1"></i>${translate('Cognitive')}
                            </button>
                            <button class="btn btn-sm btn-outline-secondary filter-chip me-2 mb-2" data-filter-type="user" data-filter-value="seizure">
                                <i class="bi bi-lightning me-1"></i>${translate('Seizure')}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Test User Filter -->
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <label class="form-label fw-bold small">${translate('Test User')}</label>
                        <div class="filter-chips" id="testUserFilterChips">
                            <!-- Dynamically populated based on test results -->
                        </div>
                    </div>
                </div>

                <!-- Quick Search -->
                <div class="row g-3 mt-2">
                    <div class="col-12">
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-search"></i></span>
                            <input type="text" class="form-control" id="quickSearch"
                                   placeholder="${translate('Search in issue descriptions, IDs, or code...')}">
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insert filter panel before test results
        testResultsCard.insertAdjacentHTML('beforebegin', filterPanelHTML);
    }
    
    populateFilterOptions() {
        const wcagCriteria = new Set();
        const touchpoints = new Set();
        const testUsers = new Map();  // Map of user_id -> {display_name, roles}
        const typeCounts = { error: 0, warning: 0, info: 0, discovery: 0 };

        // Mark all issue items with data attributes for filtering
        document.querySelectorAll('.accordion-item').forEach(item => {
            // Determine type from parent accordion
            const parentId = item.closest('.accordion')?.id || '';
            let type = 'unknown';
            
            if (parentId.includes('violations')) type = 'error';
            else if (parentId.includes('warnings')) type = 'warning';
            else if (parentId.includes('info')) type = 'info';
            else if (parentId.includes('discovery')) type = 'discovery';
            
            item.dataset.filterType = type;
            typeCounts[type]++;
            
            // Extract impact level
            const impactBadge = item.querySelector('.impact-badge, .badge');
            if (impactBadge) {
                const impactText = impactBadge.textContent.toLowerCase();
                if (impactText.includes('high') || impactText.includes('critical')) {
                    item.dataset.filterImpact = 'high';
                } else if (impactText.includes('medium') || impactText.includes('moderate')) {
                    item.dataset.filterImpact = 'medium';
                } else if (impactText.includes('low') || impactText.includes('minor')) {
                    item.dataset.filterImpact = 'low';
                }
            }
            
            // Extract WCAG criteria
            const wcagText = item.textContent;
            const wcagMatches = wcagText.match(/\d+\.\d+\.\d+/g);
            if (wcagMatches) {
                item.dataset.filterWcag = wcagMatches.join(',');
                wcagMatches.forEach(criterion => wcagCriteria.add(criterion));
            }
            
            // Extract touchpoint
            const touchpointMatch = item.textContent.match(/Touchpoint:\s*(\w+)/i);
            if (touchpointMatch) {
                const touchpoint = touchpointMatch[1].toLowerCase();
                item.dataset.filterTouchpoint = touchpoint;
                touchpoints.add(touchpoint);
            }
            // Also check for legacy category field
            const categoryMatch = item.textContent.match(/Category:\s*(\w+)/i);
            if (categoryMatch && !touchpointMatch) {
                const category = categoryMatch[1].toLowerCase();
                item.dataset.filterTouchpoint = category;
                touchpoints.add(category);
            }
            
            // Extract test user from badge
            const button = item.querySelector('.accordion-button');
            const userBadge = button?.querySelector('.badge.bg-secondary');
            const userIds = new Set();

            if (userBadge) {
                // Direct user badge on this item (single instance or nested instance)
                const badgeText = userBadge.textContent.trim();
                // Extract user info from badge text like "Guest" or "Admin (admin, editor)"
                const userMatch = badgeText.match(/^(.*?)\s*(?:\((.*?)\))?$/);
                if (userMatch) {
                    const displayName = userMatch[1].trim();
                    const roles = userMatch[2] ? userMatch[2].trim() : '';

                    // Create a unique ID for the user (use display name as key)
                    const userId = displayName.toLowerCase();
                    userIds.add(userId);

                    // Store user info
                    if (!testUsers.has(userId)) {
                        testUsers.set(userId, { displayName, roles });
                    }
                }
            } else {
                // No direct badge - check if this is a group with nested instances
                const nestedInstances = item.querySelectorAll('.accordion-item .badge.bg-secondary');
                nestedInstances.forEach(nestedBadge => {
                    const badgeText = nestedBadge.textContent.trim();
                    const userMatch = badgeText.match(/^(.*?)\s*(?:\((.*?)\))?$/);
                    if (userMatch) {
                        const displayName = userMatch[1].trim();
                        const roles = userMatch[2] ? userMatch[2].trim() : '';
                        const userId = displayName.toLowerCase();
                        userIds.add(userId);

                        // Store user info
                        if (!testUsers.has(userId)) {
                            testUsers.set(userId, { displayName, roles });
                        }
                    }
                });
            }

            // Store user IDs as comma-separated list
            if (userIds.size > 0) {
                item.dataset.filterTestUser = Array.from(userIds).join(',');
            }

            // Extract searchable text
            const body = item.querySelector('.accordion-body');
            item.dataset.searchText = [
                button?.textContent || '',
                body?.textContent || ''
            ].join(' ').toLowerCase();
        });
        
        // Update type counts
        document.querySelector('.error-count').textContent = typeCounts.error;
        document.querySelector('.warning-count').textContent = typeCounts.warning;
        document.querySelector('.info-count').textContent = typeCounts.info;
        document.querySelector('.discovery-count').textContent = typeCounts.discovery;
        
        // Populate WCAG filter
        const wcagSelect = document.getElementById('wcagFilter');
        if (wcagSelect) {
            wcagSelect.innerHTML = '';
            if (wcagCriteria.size === 0) {
                wcagSelect.innerHTML = '<option value="">No WCAG criteria found</option>';
            } else {
                [...wcagCriteria].sort().forEach(criterion => {
                    const option = document.createElement('option');
                    option.value = criterion;
                    option.textContent = `WCAG ${criterion}`;
                    wcagSelect.appendChild(option);
                });
            }
        }
        
        // Populate Touchpoint filter
        const touchpointSelect = document.getElementById('touchpointFilter');
        if (touchpointSelect) {
            touchpointSelect.innerHTML = '';
            if (touchpoints.size === 0) {
                touchpointSelect.innerHTML = '<option value="">No touchpoints found</option>';
            } else {
                [...touchpoints].sort().forEach(touchpoint => {
                    const option = document.createElement('option');
                    option.value = touchpoint;
                    option.textContent = touchpoint.charAt(0).toUpperCase() + touchpoint.slice(1);
                    touchpointSelect.appendChild(option);
                });
            }
        }

        // Populate Test User filter
        const testUserChips = document.getElementById('testUserFilterChips');
        if (testUserChips && testUsers.size > 0) {
            testUserChips.innerHTML = '';
            // Sort users: Guest first, then alphabetically by display name
            const sortedUsers = [...testUsers.entries()].sort((a, b) => {
                if (a[0] === 'guest') return -1;
                if (b[0] === 'guest') return 1;
                return a[1].displayName.localeCompare(b[1].displayName);
            });

            sortedUsers.forEach(([userId, userInfo]) => {
                const chip = document.createElement('button');
                chip.className = 'btn btn-sm btn-outline-secondary filter-chip me-2 mb-2';
                chip.setAttribute('data-filter-type', 'testUser');
                chip.setAttribute('data-filter-value', userId);

                const icon = userId === 'guest' ? 'bi-person' : 'bi-person-fill';
                const roleText = userInfo.roles ? ` (${userInfo.roles})` : '';
                chip.innerHTML = `<i class="bi ${icon} me-1"></i>${userInfo.displayName}${roleText}`;

                testUserChips.appendChild(chip);
            });

            // Attach event listeners to the new chips
            testUserChips.querySelectorAll('.filter-chip').forEach(chip => {
                chip.addEventListener('click', () => this.toggleFilter(chip));
            });
        }
    }
    
    attachEventListeners() {
        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => this.toggleFilter(chip));
        });
        
        // Select filters
        document.getElementById('wcagFilter')?.addEventListener('change', (e) => {
            this.updateMultiSelect('wcag', e.target);
        });
        
        document.getElementById('touchpointFilter')?.addEventListener('change', (e) => {
            this.updateMultiSelect('touchpoint', e.target);
        });
        
        // Quick search
        document.getElementById('quickSearch')?.addEventListener('input', (e) => {
            this.activeFilters.search = e.target.value.toLowerCase();
            this.applyFilters();
        });
        
        // Clear filters button
        document.getElementById('clearFilters')?.addEventListener('click', () => {
            this.clearAllFilters();
        });
    }
    
    toggleFilter(chip) {
        const filterType = chip.dataset.filterType;
        const filterValue = chip.dataset.filterValue;
        
        if (this.activeFilters[filterType].has(filterValue)) {
            this.activeFilters[filterType].delete(filterValue);
            chip.classList.remove('btn-primary');
            chip.classList.add('btn-outline-secondary');
        } else {
            this.activeFilters[filterType].add(filterValue);
            chip.classList.remove('btn-outline-secondary');
            chip.classList.add('btn-primary');
        }
        
        this.applyFilters();
    }
    
    updateMultiSelect(filterType, selectElement) {
        this.activeFilters[filterType].clear();
        
        for (let option of selectElement.selectedOptions) {
            if (option.value) {
                this.activeFilters[filterType].add(option.value);
            }
        }
        
        this.applyFilters();
    }
    
    applyFilters() {
        const allItems = document.querySelectorAll('.accordion-item');
        let visibleCount = 0;
        const visibleByType = { error: 0, warning: 0, info: 0, discovery: 0 };
        
        allItems.forEach(item => {
            const shouldShow = this.shouldShowItem(item);
            
            if (shouldShow) {
                item.style.display = '';
                visibleCount++;
                const type = item.dataset.filterType;
                if (type) visibleByType[type]++;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Update section headers with counts
        this.updateSectionCounts(visibleByType);
        this.updateDisplay();
        this.updateStatistics(visibleCount, allItems.length, visibleByType);
    }
    
    shouldShowItem(item) {
        // Check type filter
        if (this.activeFilters.type.size > 0) {
            if (!this.activeFilters.type.has(item.dataset.filterType)) {
                return false;
            }
        }
        
        // Check impact filter
        if (this.activeFilters.impact.size > 0) {
            if (!this.activeFilters.impact.has(item.dataset.filterImpact)) {
                return false;
            }
        }
        
        // Check WCAG filter
        if (this.activeFilters.wcag.size > 0) {
            const itemWcag = (item.dataset.filterWcag || '').split(',');
            const hasMatch = [...this.activeFilters.wcag].some(criterion => 
                itemWcag.includes(criterion)
            );
            if (!hasMatch) return false;
        }
        
        // Check touchpoint filter
        if (this.activeFilters.touchpoint.size > 0) {
            if (!this.activeFilters.touchpoint.has(item.dataset.filterTouchpoint)) {
                return false;
            }
        }
        
        // Check user impact filter
        if (this.activeFilters.user.size > 0) {
            const affectedUsers = this.getAffectedUsers(item);
            const hasMatch = [...this.activeFilters.user].some(user =>
                affectedUsers.includes(user)
            );
            if (!hasMatch) return false;
        }

        // Check test user filter
        if (this.activeFilters.testUser.size > 0) {
            const itemTestUsers = (item.dataset.filterTestUser || '').split(',');
            const hasMatch = itemTestUsers.some(user =>
                this.activeFilters.testUser.has(user)
            );
            if (!hasMatch) {
                return false;
            }
        }

        // Check search filter
        if (this.activeFilters.search) {
            const searchText = item.dataset.searchText || '';
            if (!searchText.includes(this.activeFilters.search)) {
                return false;
            }
        }

        return true;
    }
    
    getAffectedUsers(item) {
        const affectedUsers = new Set();
        const itemText = (item.dataset.searchText || '').toLowerCase();
        
        for (const [keyword, users] of Object.entries(this.issueUserMapping)) {
            if (itemText.includes(keyword)) {
                users.forEach(user => affectedUsers.add(user));
            }
        }
        
        return [...affectedUsers];
    }
    
    updateSectionCounts(visibleByType) {
        // Update section headers with filtered counts
        const sections = {
            'violations': 'error',
            'warnings': 'warning',
            'info': 'info',
            'discovery': 'discovery'
        };
        
        Object.entries(sections).forEach(([sectionName, type]) => {
            const section = document.querySelector(`#${sectionName}Accordion`);
            if (section) {
                const header = section.previousElementSibling;
                if (header) {
                    const countSpan = header.querySelector('span:last-child') || 
                                     header.querySelector('.count');
                    if (countSpan) {
                        const total = section.querySelectorAll('.accordion-item').length;
                        const visible = visibleByType[type];
                        
                        if (visible < total) {
                            countSpan.textContent = `(${visible} of ${total})`;
                        } else {
                            countSpan.textContent = `(${total})`;
                        }
                    }
                }
            }
        });
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
                    const tag = `
                        <span class="badge bg-primary me-2 mb-1">
                            Search: "${values}" 
                            <span class="ms-1" style="cursor: pointer;" onclick="filterManager.removeFilter('${type}')">×</span>
                        </span>
                    `;
                    activeFilterTags.insertAdjacentHTML('beforeend', tag);
                } else if (values.size > 0) {
                    // Other filters
                    values.forEach(value => {
                        const tag = `
                            <span class="badge bg-primary me-2 mb-1">
                                ${type}: ${value} 
                                <span class="ms-1" style="cursor: pointer;" onclick="filterManager.removeFilter('${type}', '${value}')">×</span>
                            </span>
                        `;
                        activeFilterTags.insertAdjacentHTML('beforeend', tag);
                    });
                }
            });
        } else {
            activeFiltersDiv.style.display = 'none';
        }
    }
    
    removeFilter(type, value) {
        if (type === 'search') {
            this.activeFilters.search = '';
            document.getElementById('quickSearch').value = '';
        } else if (value) {
            this.activeFilters[type].delete(value);
            // Update UI
            const chip = document.querySelector(`[data-filter-type="${type}"][data-filter-value="${value}"]`);
            if (chip) {
                chip.classList.remove('btn-primary');
                chip.classList.add('btn-outline-secondary');
            }
        }
        
        this.applyFilters();
    }
    
    updateStatistics(visible, total, visibleByType) {
        document.getElementById('visibleCount').textContent = visible;
        document.getElementById('totalCount').textContent = total;
        
        // Update filter summary
        const summary = [];
        if (visibleByType.error > 0) summary.push(`${visibleByType.error} errors`);
        if (visibleByType.warning > 0) summary.push(`${visibleByType.warning} warnings`);
        if (visibleByType.info > 0) summary.push(`${visibleByType.info} info`);
        if (visibleByType.discovery > 0) summary.push(`${visibleByType.discovery} discovery`);
        
        document.getElementById('filterSummary').textContent = summary.join(', ') || 'No items visible';
    }
    
    updateCounts() {
        // Count impact levels
        const impactCounts = { high: 0, medium: 0, low: 0 };
        
        document.querySelectorAll('.accordion-item').forEach(item => {
            const impact = item.dataset.filterImpact;
            if (impact && impactCounts.hasOwnProperty(impact)) {
                impactCounts[impact]++;
            }
        });
        
        document.getElementById('highImpactCount').textContent = impactCounts.high;
        document.getElementById('mediumImpactCount').textContent = impactCounts.medium;
        document.getElementById('lowImpactCount').textContent = impactCounts.low;
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
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.classList.remove('btn-primary');
            chip.classList.add('btn-outline-secondary');
        });
        
        const wcagFilter = document.getElementById('wcagFilter');
        const touchpointFilter = document.getElementById('touchpointFilter');
        const quickSearch = document.getElementById('quickSearch');
        
        if (wcagFilter) wcagFilter.selectedIndex = -1;
        if (touchpointFilter) touchpointFilter.selectedIndex = -1;
        if (quickSearch) quickSearch.value = '';
        
        this.applyFilters();
    }
}

// Global instance for easy access
let filterManager;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        filterManager = new IssueFilterManager();
    });
} else {
    filterManager = new IssueFilterManager();
}