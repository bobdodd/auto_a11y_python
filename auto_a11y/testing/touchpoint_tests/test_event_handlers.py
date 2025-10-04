"""
Event Handlers touchpoint test module
Analyzes page for event handling accessibility issues and keyboard navigation patterns.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Event Handler Accessibility Tests",
    "touchpoint": "event_handlers",
    "description": "Analyzes page for event handling accessibility issues and keyboard navigation patterns. Checks for proper implementation of keyboard access for interactive elements, correct tab order, and escape key functionality for modal dialogs.",
    "version": "1.0.0",
    "wcagCriteria": ["2.1.1", "2.1.2", "2.1.3", "2.4.3"],
    "tests": [
        {
            "id": "missing-tabindex",
            "name": "Non-interactive Elements with Event Handlers Missing Tabindex",
            "description": "Tests for non-interactive elements (div, span, etc.) that have event handlers but no tabindex attribute. These elements must have tabindex to be keyboard accessible.",
            "impact": "critical",
            "wcagCriteria": ["2.1.1", "2.1.3"],
        },
        {
            "id": "mouse-only",
            "name": "Elements with Mouse Events but no Keyboard Events",
            "description": "Identifies elements that respond to mouse events (click, hover) but have no keyboard event handlers, making them inaccessible to keyboard users",
            "impact": "high",
            "wcagCriteria": ["2.1.1", "2.1.3"],
        },
        {
            "id": "modal-without-escape",
            "name": "Modal Dialogs without Keyboard Escape",
            "description": "Checks if modal dialogs provide keyboard escape functionality (ESC key)",
            "impact": "high",
            "wcagCriteria": ["2.1.2"],
        },
        {
            "id": "visual-order",
            "name": "Tab Order Doesn't Follow Visual Layout",
            "description": "Checks if the tab order of interactive elements follows their visual arrangement",
            "impact": "medium", 
            "wcagCriteria": ["2.4.3"],
        },
        {
            "id": "negative-tabindex",
            "name": "Elements with Negative Tabindex",
            "description": "Identifies elements using negative tabindex which removes them from the natural tab order but keeps them focusable programmatically",
            "impact": "medium",
            "wcagCriteria": ["2.4.3"],
        },
        {
            "id": "high-tabindex",
            "name": "Elements with Unusually High Tabindex",
            "description": "Identifies elements with tabindex values > 10, which is a poor practice that can create maintenance issues",
            "impact": "low",
            "wcagCriteria": ["2.4.3"],
        }
    ]
}

async def test_event_handlers(page) -> Dict[str, Any]:
    """
    Test event handlers and tab order accessibility requirements
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze event handlers
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    discovery: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'event_handlers',
                    checks: []
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
                
                // Check if element is intrinsically interactive
                function isIntrinsicInteractive(element) {
                    const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'details', 'summary'];
                    const interactiveRoles = ['button', 'link', 'menuitem', 'tab', 'checkbox', 'radio', 'switch'];
                    
                    return interactiveTags.includes(element.tagName.toLowerCase()) ||
                           (element.getAttribute('role') && 
                            interactiveRoles.includes(element.getAttribute('role')));
                }
                
                // Find all focusable elements
                const focusableElements = Array.from(document.querySelectorAll(
                    'a, button, input, select, textarea, [tabindex], [contentEditable=true], audio[controls], video[controls]'
                )).filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                });
                
                results.elements_tested = focusableElements.length;
                
                if (focusableElements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No focusable elements found on the page';
                    return results;
                }
                
                // Check tab order
                let tabOrderViolations = 0;
                let previousRect = null;
                
                focusableElements.forEach((element, index) => {
                    const rect = element.getBoundingClientRect();
                    const tabindex = element.getAttribute('tabindex');
                    const tabindexValue = tabindex ? parseInt(tabindex) : 0;
                    
                    // Check for negative tabindex
                    if (tabindexValue < 0) {
                        results.warnings.push({
                            err: 'WarnNegativeTabindex',
                            type: 'warn',
                            cat: 'event_handlers',
                            element: element.tagName,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Element has negative tabindex, removing it from tab order',
                            tabindex: tabindexValue
                        });
                    }
                    
                    // Check for high tabindex values
                    if (tabindexValue > 10) {
                        results.warnings.push({
                            err: 'WarnHighTabindex',
                            type: 'warn',
                            cat: 'event_handlers',
                            element: element.tagName,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `Element has unusually high tabindex (${tabindexValue}), which may cause navigation issues`,
                            tabindex: tabindexValue
                        });
                    }
                    
                    // Check visual tab order
                    if (previousRect && index > 0) {
                        const previousElement = focusableElements[index - 1];
                        const previousElementRect = previousElement.getBoundingClientRect();

                        // Calculate vertical alignment
                        const verticalDiff = Math.abs(rect.top - previousElementRect.top);
                        const clearlyDifferentRows = verticalDiff > 10;
                        const definitelySameRow = verticalDiff <= 5;
                        const ambiguousOverlap = verticalDiff > 5 && verticalDiff <= 10;

                        // Only check left/right position if there's potential for same-row issue
                        if (!clearlyDifferentRows && rect.left < previousElementRect.left - 50) {
                            // Get readable descriptions of both elements
                            const currentDesc = element.tagName.toLowerCase() +
                                (element.id ? `#${element.id}` : '') +
                                (element.textContent ? ` ("${element.textContent.trim().substring(0, 30)}")` : '');
                            const previousDesc = previousElement.tagName.toLowerCase() +
                                (previousElement.id ? `#${previousElement.id}` : '') +
                                (previousElement.textContent ? ` ("${previousElement.textContent.trim().substring(0, 30)}")` : '');

                            const sharedData = {
                                cat: 'event_handlers',
                                element: element.tagName.toLowerCase(),
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                currentElement: {
                                    tag: element.tagName.toLowerCase(),
                                    id: element.id || null,
                                    text: element.textContent.trim().substring(0, 50),
                                    position: { x: Math.round(rect.left), y: Math.round(rect.top) },
                                    tabIndex: index + 1
                                },
                                previousElement: {
                                    tag: previousElement.tagName.toLowerCase(),
                                    id: previousElement.id || null,
                                    text: previousElement.textContent.trim().substring(0, 50),
                                    html: previousElement.outerHTML.substring(0, 200),
                                    xpath: getFullXPath(previousElement),
                                    position: { x: Math.round(previousElementRect.left), y: Math.round(previousElementRect.top) },
                                    tabIndex: index
                                },
                                verticalDiff: Math.round(verticalDiff)
                            };

                            if (definitelySameRow) {
                                // Clear same-row violation - this is an ERROR
                                tabOrderViolations++;
                                results.errors.push({
                                    err: 'ErrTabOrderViolation',
                                    type: 'err',
                                    description: `Tab order diverges from visual layout: ${currentDesc} appears visually left of ${previousDesc} but comes after it in tab order`,
                                    ...sharedData
                                });
                                results.elements_failed++;
                            } else if (ambiguousOverlap) {
                                // Ambiguous overlap - this is a WARNING
                                results.warnings.push({
                                    err: 'WarnAmbiguousTabOrder',
                                    type: 'warn',
                                    description: `Possible tab order issue: ${currentDesc} appears left of ${previousDesc} but comes after it. Elements overlap vertically (${Math.round(verticalDiff)}px difference) - verify visual layout matches intended tab order`,
                                    ...sharedData
                                });
                            }
                        } else {
                            results.elements_passed++;
                        }
                    }
                    
                    previousRect = rect;
                });
                
                // Check for elements with event handlers but no tabindex
                const allElements = Array.from(document.querySelectorAll('*'));
                allElements.forEach(element => {
                    let hasEventHandler = false;
                    let hasKeyboardHandler = false;
                    
                    // Check for inline event handlers
                    Array.from(element.attributes).forEach(attr => {
                        if (attr.name.startsWith('on')) {
                            hasEventHandler = true;
                            const eventType = attr.name.slice(2);
                            if (['keydown', 'keyup', 'keypress'].includes(eventType)) {
                                hasKeyboardHandler = true;
                            }
                        }
                    });
                    
                    // Check for class-based event handlers (common pattern)
                    const classAndData = element.className + ' ' + 
                        Array.from(element.attributes)
                            .map(attr => attr.name + ' ' + attr.value)
                            .join(' ');
                            
                    if (classAndData.toLowerCase().includes('click') ||
                        classAndData.toLowerCase().includes('button') ||
                        classAndData.toLowerCase().includes('trigger')) {
                        hasEventHandler = true;
                    }
                    
                    if (hasEventHandler && !isIntrinsicInteractive(element) && !element.hasAttribute('tabindex')) {
                        const tagName = element.tagName.toLowerCase();
                        const hasOnclick = element.hasAttribute('onclick');
                        const hasOtherHandlers = element.hasAttribute('onmousedown') ||
                                                 element.hasAttribute('onmouseup') ||
                                                 element.hasAttribute('ondblclick');

                        results.errors.push({
                            err: 'ErrMissingTabindex',
                            type: 'err',
                            cat: 'event_handlers',
                            element: tagName,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: `<${tagName}> with event handler is not keyboard accessible - missing tabindex`,
                            elementTag: tagName,
                            hasOnclick: hasOnclick,
                            hasOtherHandlers: hasOtherHandlers
                        });
                        results.elements_failed++;
                    }
                    
                    // Check for mouse-only handlers
                    if (hasEventHandler && !hasKeyboardHandler && !isIntrinsicInteractive(element)) {
                        results.errors.push({
                            err: 'ErrMouseOnlyHandler',
                            type: 'err',
                            cat: 'event_handlers',
                            element: element.tagName,
                            xpath: getFullXPath(element),
                            html: element.outerHTML.substring(0, 200),
                            description: 'Element has mouse handler but no keyboard handler'
                        });
                        results.elements_failed++;
                    }
                });
                
                // Check for modals without escape handlers
                const modals = Array.from(document.querySelectorAll('dialog, [role="dialog"], [class*="modal"]'))
                    .filter(modal => {
                        // Exclude nested modal content containers - only check outermost modal
                        const hasModalAncestor = Array.from(document.querySelectorAll('dialog, [role="dialog"], [class*="modal"]'))
                            .some(otherModal => otherModal !== modal && otherModal.contains(modal));
                        return !hasModalAncestor;
                    });

                modals.forEach(modal => {
                    const onkeydown = modal.getAttribute('onkeydown');
                    const hasEscapeHandler = onkeydown &&
                                           (onkeydown.includes('Escape') ||
                                            onkeydown.includes('Esc') ||
                                            onkeydown.includes('27'));

                    if (!hasEscapeHandler) {
                        results.errors.push({
                            err: 'ErrModalWithoutEscape',
                            type: 'err',
                            cat: 'event_handlers',
                            element: modal.tagName,
                            xpath: getFullXPath(modal),
                            html: modal.outerHTML.substring(0, 200),
                            description: 'Modal element without keyboard escape handler'
                        });
                        results.elements_failed++;
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Interactive elements accessibility',
                    wcag: ['2.1.1', '2.1.3'],
                    total: focusableElements.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                if (tabOrderViolations > 0) {
                    results.checks.push({
                        description: 'Tab order violations',
                        wcag: ['2.4.3'],
                        total: focusableElements.length,
                        passed: focusableElements.length - tabOrderViolations,
                        failed: tabOrderViolations
                    });
                }

                // DISCOVERY: Report presence of JavaScript on the page
                const scriptElements = Array.from(document.querySelectorAll('script[src], script:not([src])'));
                if (scriptElements.length > 0) {
                    results.warnings.push({
                        err: 'DiscoFoundJS',
                        type: 'disco',
                        cat: 'event_handlers',
                        element: 'script',
                        xpath: '/html[1]',
                        html: `<meta>Found ${scriptElements.length} script elements</meta>`,
                        description: `${scriptElements.length} JavaScript elements detected - ensure progressive enhancement`,
                        count: scriptElements.length
                    });
                }

                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_event_handlers: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }