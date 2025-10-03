"""
Modals touchpoint test module
Evaluates modal dialogs for proper accessibility implementation.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Modal Dialog Accessibility Analysis",
    "touchpoint": "modals",
    "description": "Evaluates modal dialogs for proper accessibility implementation, including focus management, proper heading structure, and close mechanisms. This test identifies modals that don't follow best practices for keyboard and screen reader accessibility.",
    "version": "1.0.0",
    "wcagCriteria": ["1.3.1", "2.4.6", "4.1.2", "2.1.2", "2.4.3", "2.4.7"],
    "tests": [
        {
            "id": "dialog-heading",
            "name": "Dialog Heading Structure",
            "description": "Checks if modal dialogs begin with a proper heading element (H1 or H2) to identify their purpose.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.6"],
        },
        {
            "id": "dialog-trigger",
            "name": "Dialog Trigger Elements",
            "description": "Identifies whether each modal dialog has associated trigger elements that open it.",
            "impact": "medium",
            "wcagCriteria": ["4.1.2"],
        },
        {
            "id": "dialog-close",
            "name": "Dialog Close Mechanism",
            "description": "Checks if modal dialogs provide a clear mechanism to close them.",
            "impact": "high",
            "wcagCriteria": ["2.1.2"],
        },
        {
            "id": "focus-management",
            "name": "Dialog Focus Management",
            "description": "Evaluates if modal dialogs properly manage keyboard focus when opened and closed.",
            "impact": "high",
            "wcagCriteria": ["2.4.3", "2.4.7"],
        }
    ]
}

async def test_modals(page) -> Dict[str, Any]:
    """
    Test modal dialogs for accessibility requirements including proper headings

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze modals
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'modals',
                    checks: [],
                    debug: []  // Add debug info
                };

                // Function to generate XPath for elements
                function getFullXPath(element) {
                    if (!element) return '';
                    
                    function getElementIdx(el) {
                        let count = 1;
                        for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                            if (sib.nodeType === 1 && sib.tagName === el.tagName) {
                                count++;
                            }
                        }
                        return count;
                    }
                    
                    let path = '';
                    while (element && element.nodeType === 1) {
                        const idx = getElementIdx(element);
                        const tagName = element.tagName.toLowerCase();
                        path = `/${tagName}[${idx}]${path}`;
                        element = element.parentNode;
                    }
                    return path;
                }
                
                // Find modal elements
                function findModals() {
                    const dialogElements = Array.from(document.querySelectorAll('dialog'));
                    const roleDialogs = Array.from(document.querySelectorAll('[role="dialog"]'));
                    const modalDivs = Array.from(document.querySelectorAll('div[class*="modal" i]'));

                    // Combine all candidates and deduplicate
                    const allModals = [...dialogElements, ...roleDialogs, ...modalDivs];
                    const uniqueModals = Array.from(new Set(allModals));

                    // Filter out nested modals - only keep outermost
                    return uniqueModals.filter(modal => {
                        return !uniqueModals.some(otherModal =>
                            otherModal !== modal && otherModal.contains(modal)
                        );
                    });
                }
                
                // Check dialog heading structure
                function checkDialogHeading(modal) {
                    // Look for first heading anywhere in modal (not just direct children)
                    const firstHeading = modal.querySelector('h1, h2, h3, h4, h5, h6');

                    results.debug.push({
                        modal: modal.id || modal.className,
                        foundHeading: firstHeading ? firstHeading.tagName : 'none',
                        headingText: firstHeading ? firstHeading.textContent.trim() : null
                    });

                    if (!firstHeading) {
                        return {
                            hasProperHeading: false,
                            hasHeading: false,
                            foundLevel: null
                        };
                    }

                    const level = parseInt(firstHeading.tagName.substring(1));
                    const headingText = firstHeading.textContent.trim();

                    // Modal should start with h2 (or h1 if it's the page's main h1)
                    if (level > 2) {
                        return {
                            hasProperHeading: false,
                            hasHeading: true,
                            foundLevel: level,
                            headingText: headingText
                        };
                    }

                    return {
                        hasProperHeading: true,
                        heading: {
                            level: firstHeading.tagName.toLowerCase(),
                            text: headingText
                        }
                    };
                }
                
                // Find close elements
                function findCloseElements(modal) {
                    const closeElements = [];
                    const inaccessibleCloseElements = [];

                    // First check for properly interactive close elements
                    const interactiveElements = modal.querySelectorAll(
                        'button, a, [role="button"], [tabindex]'
                    );

                    interactiveElements.forEach(element => {
                        const text = element.textContent.trim().toLowerCase();
                        const ariaLabel = element.getAttribute('aria-label')?.toLowerCase();
                        const title = element.getAttribute('title')?.toLowerCase();

                        if ((text && text.includes('close')) ||
                            (ariaLabel && ariaLabel.includes('close')) ||
                            (title && title.includes('close')) ||
                            element.className.toLowerCase().includes('close') ||
                            element.id.toLowerCase().includes('close')) {

                            closeElements.push({
                                element: element.tagName.toLowerCase(),
                                id: element.id || null,
                                text: text,
                                ariaLabel: ariaLabel,
                                title: title
                            });
                        }
                    });

                    // If no accessible close elements found, check for inaccessible ones
                    if (closeElements.length === 0) {
                        const allElements = modal.querySelectorAll('span, div, i, svg');

                        allElements.forEach(element => {
                            const text = element.textContent.trim().toLowerCase();
                            const ariaLabel = element.getAttribute('aria-label')?.toLowerCase();
                            const title = element.getAttribute('title')?.toLowerCase();
                            const className = element.className.toLowerCase();
                            const id = element.id.toLowerCase();

                            // Check for close-related patterns
                            const hasCloseText = text === 'close' || text === 'x' || text === '×' || text === '✕';
                            const hasCloseClass = className.includes('close') || className.includes('dismiss');
                            const hasCloseId = id.includes('close') || id.includes('dismiss');
                            const hasCloseLabel = (ariaLabel && ariaLabel.includes('close')) ||
                                                 (title && title.includes('close'));
                            const hasIconClass = className.includes('icon-close') ||
                                               className.includes('icon-x') ||
                                               className.includes('fa-times') ||
                                               className.includes('fa-close');

                            if (hasCloseText || hasCloseClass || hasCloseId || hasCloseLabel || hasIconClass) {
                                inaccessibleCloseElements.push({
                                    element: element.tagName.toLowerCase(),
                                    id: element.id || null,
                                    text: text,
                                    className: element.className,
                                    reason: 'Missing role="button" and tabindex'
                                });
                            }
                        });
                    }

                    return { closeElements, inaccessibleCloseElements };
                }
                
                // Check focus management
                function checkFocusManagement(modal) {
                    const focusableElements = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    
                    return {
                        hasFocusableElements: focusableElements.length > 0,
                        firstFocusable: focusableElements.length > 0 ? {
                            element: focusableElements[0].tagName.toLowerCase(),
                            id: focusableElements[0].id || null,
                            text: focusableElements[0].textContent.trim()
                        } : null,
                        totalFocusable: focusableElements.length
                    };
                }
                
                const modals = findModals();
                
                if (modals.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No modal dialogs found on the page';
                    return results;
                }
                
                results.elements_tested = modals.length;
                
                let modalsWithoutHeading = 0;
                let modalsWithoutClose = 0;
                let modalsWithoutFocusManagement = 0;
                
                modals.forEach(modal => {
                    const headingInfo = checkDialogHeading(modal);
                    const closeInfo = findCloseElements(modal);
                    const focusInfo = checkFocusManagement(modal);

                    let hasViolation = false;

                    // Check for proper heading
                    if (!headingInfo.hasProperHeading) {
                        modalsWithoutHeading++;

                        let description = 'Modal dialog lacks a heading to identify its purpose';
                        let foundLevel = null;
                        let headingText = null;

                        if (headingInfo.hasHeading) {
                            // Has heading but wrong level
                            description = `Modal has h${headingInfo.foundLevel} heading ("${headingInfo.headingText}") but should use h2 (or h1) for proper document structure`;
                            foundLevel = headingInfo.foundLevel;
                            headingText = headingInfo.headingText;
                        }

                        results.errors.push({
                            err: 'ErrModalMissingHeading',
                            type: 'err',
                            cat: 'modals',
                            element: modal.tagName.toLowerCase(),
                            xpath: getFullXPath(modal),
                            html: modal.outerHTML.substring(0, 200),
                            description: description,
                            foundLevel: foundLevel,
                            headingText: headingText
                        });
                        hasViolation = true;
                    }

                    // Check for close mechanism
                    if (closeInfo.closeElements.length === 0) {
                        modalsWithoutClose++;

                        let description = 'Modal dialog has no identifiable close mechanism';
                        let inaccessibleElements = null;

                        // If we found inaccessible close elements, note them
                        if (closeInfo.inaccessibleCloseElements.length > 0) {
                            const inaccessible = closeInfo.inaccessibleCloseElements[0];
                            description = `Modal has close element (<${inaccessible.element}${inaccessible.id ? ' id="' + inaccessible.id + '"' : ''}${inaccessible.className ? ' class="' + inaccessible.className + '"' : ''}>) but it lacks role="button" and tabindex, making it inaccessible to keyboard users`;
                            inaccessibleElements = closeInfo.inaccessibleCloseElements;
                        }

                        results.errors.push({
                            err: 'ErrModalMissingClose',
                            type: 'err',
                            cat: 'modals',
                            element: modal.tagName.toLowerCase(),
                            xpath: getFullXPath(modal),
                            html: modal.outerHTML.substring(0, 200),
                            description: description,
                            inaccessibleCloseElements: inaccessibleElements
                        });
                        hasViolation = true;
                    }
                    
                    // Check for focus management issues
                    if (!focusInfo.hasFocusableElements) {
                        modalsWithoutFocusManagement++;
                        results.warnings.push({
                            err: 'WarnModalNoFocusableElements',
                            type: 'warn',
                            cat: 'modals',
                            element: modal.tagName.toLowerCase(),
                            xpath: getFullXPath(modal),
                            html: modal.outerHTML.substring(0, 200),
                            description: 'Modal dialog contains no focusable elements'
                        });
                    }
                    
                    // Check for ARIA attributes
                    const ariaModal = modal.getAttribute('aria-modal');
                    const ariaLabelledby = modal.getAttribute('aria-labelledby');
                    
                    if (ariaModal !== 'true') {
                        results.warnings.push({
                            err: 'WarnModalMissingAriaModal',
                            type: 'warn',
                            cat: 'modals',
                            element: modal.tagName.toLowerCase(),
                            xpath: getFullXPath(modal),
                            html: modal.outerHTML.substring(0, 200),
                            description: 'Modal dialog should have aria-modal="true" attribute'
                        });
                    }
                    
                    if (!ariaLabelledby) {
                        results.warnings.push({
                            err: 'WarnModalMissingAriaLabelledby',
                            type: 'warn',
                            cat: 'modals',
                            element: modal.tagName.toLowerCase(),
                            xpath: getFullXPath(modal),
                            html: modal.outerHTML.substring(0, 200),
                            description: 'Modal dialog should have aria-labelledby attribute referencing its heading'
                        });
                    }
                    
                    if (!hasViolation) {
                        results.elements_passed++;
                    } else {
                        results.elements_failed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Modal dialog structure',
                    wcag: ['1.3.1', '2.4.6'],
                    total: modals.length,
                    passed: modals.length - modalsWithoutHeading,
                    failed: modalsWithoutHeading
                });
                
                results.checks.push({
                    description: 'Modal close mechanisms',
                    wcag: ['2.1.2'],
                    total: modals.length,
                    passed: modals.length - modalsWithoutClose,
                    failed: modalsWithoutClose
                });
                
                if (modalsWithoutFocusManagement > 0) {
                    results.checks.push({
                        description: 'Modal focus management',
                        wcag: ['2.4.3', '2.4.7'],
                        total: modals.length,
                        passed: modals.length - modalsWithoutFocusManagement,
                        failed: modalsWithoutFocusManagement
                    });
                }
                
                return results;
            }
        ''')

        # Log debug info
        if 'debug' in results and results['debug']:
            logger.warning(f"MODAL DEBUG: {results['debug']}")

        # Log errors for debugging
        if 'errors' in results:
            for error in results['errors']:
                if error.get('err') == 'ErrModalMissingHeading':
                    logger.warning(f"MODAL HEADING ERROR: desc='{error.get('description')}' foundLevel={error.get('foundLevel')} headingText='{error.get('headingText')}'")

        return results
        
    except Exception as e:
        logger.error(f"Error in test_modals: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }