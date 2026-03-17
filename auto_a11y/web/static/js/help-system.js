/**
 * Contextual Help System for Auto A11y
 * Provides tooltips, modals, and help documentation
 */

class HelpSystem {
    constructor() {
        this.helpContent = {
            scoring: {
                accessibility_score: {
                    title: "Accessibility Score",
                    brief: "Percentage of individual accessibility checks that passed",
                    detailed: `
                        <h3>How Accessibility Score is Calculated</h3>
                        <p>The accessibility score represents the percentage of individual accessibility checks that passed across all tests.</p>
                        
                        <h4>Formula:</h4>
                        <code>(Passed Checks / Applicable Checks) × 100</code>
                        
                        <h4>Example:</h4>
                        <ul>
                            <li>If 100 checks were performed</li>
                            <li>And 66 checks passed</li>
                            <li>Score = 66%</li>
                        </ul>
                        
                        <h4>What Counts:</h4>
                        <ul>
                            <li>✓ Each individual check within a test</li>
                            <li>✓ Partial passes within tests</li>
                            <li>✗ Discovery items (informational only)</li>
                            <li>✗ Info items (best practices)</li>
                        </ul>
                        
                        <p><strong>This score shows progress</strong> and helps identify how close you are to full compliance.</p>
                    `
                },
                compliance_score: {
                    title: "Compliance Score",
                    brief: "Percentage of tests with zero violations",
                    detailed: `
                        <h3>How Compliance Score is Calculated</h3>
                        <p>The compliance score represents the percentage of accessibility tests that passed completely without any violations.</p>
                        
                        <h4>Formula:</h4>
                        <code>(Tests with Zero Violations / Total Tests) × 100</code>
                        
                        <h4>Example:</h4>
                        <ul>
                            <li>If 10 tests were run</li>
                            <li>And 3 tests had zero violations</li>
                            <li>Score = 30%</li>
                        </ul>
                        
                        <h4>Key Difference:</h4>
                        <p>A test with even one violation counts as failed for compliance, even if 99% of its checks passed.</p>
                        
                        <h4>Why It's Stricter:</h4>
                        <ul>
                            <li>Reflects true WCAG compliance</li>
                            <li>One barrier can block users completely</li>
                            <li>Legal compliance often requires zero violations</li>
                        </ul>
                        
                        <p><strong>This score shows actual compliance</strong> with accessibility standards.</p>
                    `
                },
                score_difference: {
                    title: "Why Scores Differ",
                    brief: "Understanding the gap between accessibility and compliance scores",
                    detailed: `
                        <h3>Why Your Scores Are Different</h3>
                        
                        <h4>Common Scenario:</h4>
                        <p>Accessibility Score: 66.2% | Compliance Score: 30.8%</p>
                        
                        <h4>What This Means:</h4>
                        <ul>
                            <li>Most of your checks (66.2%) are passing</li>
                            <li>But only 30.8% of pages/components are fully compliant</li>
                            <li>You're making good progress but still have critical issues</li>
                        </ul>
                        
                        <h4>Real Example:</h4>
                        <div class="example-box">
                            <p><strong>Form Test Results:</strong></p>
                            <ul>
                                <li>10 form fields tested</li>
                                <li>9 fields have proper labels ✓</li>
                                <li>1 field missing label ✗</li>
                            </ul>
                            <p><strong>Impact on Scores:</strong></p>
                            <ul>
                                <li>Accessibility: +90% (9/10 passed)</li>
                                <li>Compliance: 0% (test has violations)</li>
                            </ul>
                        </div>
                        
                        <h4>Which Score Matters?</h4>
                        <ul>
                            <li><strong>For Development:</strong> Use accessibility score to track progress</li>
                            <li><strong>For Legal/Compliance:</strong> Use compliance score</li>
                            <li><strong>For Users:</strong> Both matter - aim for 100% compliance</li>
                        </ul>
                    `
                }
            },
            wcag: {
                levels: {
                    title: "WCAG Conformance Levels",
                    brief: "Understanding A, AA, and AAA standards",
                    detailed: `
                        <h3>WCAG Conformance Levels</h3>
                        
                        <h4>Level A (Minimum)</h4>
                        <ul>
                            <li>Basic accessibility features</li>
                            <li>Essential for any public website</li>
                            <li>Examples: Images have alt text, pages have titles</li>
                        </ul>
                        
                        <h4>Level AA (Recommended)</h4>
                        <ul>
                            <li>Removes major barriers</li>
                            <li>Legal standard in many countries</li>
                            <li>Examples: Color contrast 4.5:1, captions for videos</li>
                        </ul>
                        
                        <h4>Level AAA (Enhanced)</h4>
                        <ul>
                            <li>Highest level of accessibility</li>
                            <li>Not required for entire sites</li>
                            <li>Examples: Color contrast 7:1, sign language for videos</li>
                        </ul>
                    `
                }
            },
            issues: {
                impact_levels: {
                    title: "Issue Impact Levels",
                    brief: "Understanding Critical, High, Medium, and Low impacts",
                    detailed: `
                        <h3>Issue Impact Levels</h3>
                        
                        <h4>🔴 Critical/High Impact</h4>
                        <ul>
                            <li>Completely blocks access for some users</li>
                            <li>Examples: Missing alt text, no keyboard access</li>
                            <li>Must fix immediately</li>
                        </ul>
                        
                        <h4>🟡 Medium Impact</h4>
                        <ul>
                            <li>Significantly degrades experience</li>
                            <li>Examples: Poor color contrast, missing landmarks</li>
                            <li>Fix as soon as possible</li>
                        </ul>
                        
                        <h4>🟢 Low Impact</h4>
                        <ul>
                            <li>Minor inconvenience</li>
                            <li>Examples: Redundant alt text, decorative issues</li>
                            <li>Fix when convenient</li>
                        </ul>
                        
                        <h4>ℹ️ Info/Discovery</h4>
                        <ul>
                            <li>Best practices and recommendations</li>
                            <li>Not counted in scoring</li>
                            <li>Review for improvement opportunities</li>
                        </ul>
                    `
                }
            },
            testing: {
                applicability: {
                    title: "Test Applicability",
                    brief: "Why some tests show as 'Not Applicable'",
                    detailed: `
                        <h3>Understanding Test Applicability</h3>
                        
                        <p>Tests are marked "Not Applicable" when there are no relevant elements to test on the page.</p>
                        
                        <h4>Examples:</h4>
                        <ul>
                            <li><strong>Images test:</strong> N/A if page has no images</li>
                            <li><strong>Forms test:</strong> N/A if page has no form elements</li>
                            <li><strong>Video test:</strong> N/A if page has no media</li>
                        </ul>
                        
                        <h4>Why This Matters:</h4>
                        <ul>
                            <li>You're not penalized for missing elements</li>
                            <li>Scores reflect only what's actually on the page</li>
                            <li>More accurate assessment of real issues</li>
                        </ul>
                        
                        <h4>Impact on Scoring:</h4>
                        <p>Not applicable tests don't affect your score. A page with just text can still achieve 100% if the text is accessible.</p>
                    `
                }
            }
        };
        
        this.init();
    }
    
    init() {
        this.createHelpModal();
        this.attachEventListeners();
        this.initTooltips();
    }
    
    createHelpModal() {
        const modal = document.createElement('div');
        modal.id = 'help-modal';
        modal.className = 'help-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'help-modal-title');
        modal.innerHTML = `
            <div class="help-modal-content">
                <div class="help-modal-header">
                    <h2 id="help-modal-title">Help</h2>
                    <button class="help-modal-close" aria-label="Close help">&times;</button>
                </div>
                <div class="help-modal-body" id="help-modal-body">
                </div>
                <div class="help-modal-footer">
                    <button class="btn btn-primary help-modal-close">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    showHelp(topicPath) {
        const topics = topicPath.split('.');
        let content = this.helpContent;

        for (const topic of topics) {
            if (content[topic]) {
                content = content[topic];
            } else {
                return;
            }
        }

        const modal = document.getElementById('help-modal');
        const title = document.getElementById('help-modal-title');
        const body = document.getElementById('help-modal-body');

        // Save the element that triggered the modal
        this.previousFocus = document.activeElement;

        title.textContent = content.title || 'Help';
        body.innerHTML = content.detailed || content.brief || 'No help available for this topic.';

        modal.classList.add('show');

        // Focus the first close button inside the modal
        var closeBtn = modal.querySelector('.help-modal-close');
        if (closeBtn) {
            closeBtn.focus();
        }

        // Add focus trap
        this._trapFocus = this._createFocusTrap(modal);
        modal.addEventListener('keydown', this._trapFocus);
    }
    
    hideHelp() {
        const modal = document.getElementById('help-modal');
        modal.classList.remove('show');

        // Remove focus trap
        if (this._trapFocus) {
            modal.removeEventListener('keydown', this._trapFocus);
            this._trapFocus = null;
        }

        // Return focus to the trigger element
        if (this.previousFocus && this.previousFocus.focus) {
            this.previousFocus.focus();
        }
    }

    _createFocusTrap(container) {
        return function(e) {
            if (e.key !== 'Tab') return;

            var focusable = container.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (focusable.length === 0) return;

            var first = focusable[0];
            var last = focusable[focusable.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                }
            } else {
                if (document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        };
    }

    attachEventListeners() {
        // Close modal handlers
        document.querySelectorAll('.help-modal-close').forEach(btn => {
            btn.addEventListener('click', () => this.hideHelp());
        });
        
        // Close on backdrop click
        const modal = document.getElementById('help-modal');
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideHelp();
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.hideHelp();
            }
        });
        
        // Help button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-help]')) {
                e.preventDefault();
                const topic = e.target.getAttribute('data-help');
                this.showHelp(topic);
            }
        });
    }
    
    initTooltips() {
        // Add tooltips to elements with data-tooltip
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            const tooltip = document.createElement('div');
            tooltip.className = 'help-tooltip';
            tooltip.textContent = element.getAttribute('data-tooltip');
            tooltip.style.display = 'none';
            document.body.appendChild(tooltip);
            
            element.addEventListener('mouseenter', (e) => {
                const rect = e.target.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) + 'px';
                tooltip.style.top = rect.top - 35 + 'px';
                tooltip.style.display = 'block';
            });
            
            element.addEventListener('mouseleave', () => {
                tooltip.style.display = 'none';
            });
        });
    }
    
    // Create inline help icon
    createHelpIcon(topic, text = '?') {
        return `<button class="help-icon" data-help="${topic}" aria-label="Get help about ${topic}" title="Click for help">${text}</button>`;
    }
}

// Initialize help system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.helpSystem = new HelpSystem();
    });
} else {
    window.helpSystem = new HelpSystem();
}