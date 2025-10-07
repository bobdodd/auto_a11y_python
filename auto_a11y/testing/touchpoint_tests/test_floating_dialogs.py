"""
Floating Dialogs touchpoint test module
Evaluates floating dialogs and modal windows for accessibility compliance.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Floating Dialog Accessibility Analysis",
    "touchpoint": "floating_dialogs",
    "description": "Evaluates floating dialogs and modal windows for accessibility compliance. This test helps ensure that dialogs are properly structured, keyboard accessible, and don't obscure important content.",
    "version": "2.0.0",
    "wcagCriteria": ["4.1.2", "2.4.6", "2.1.1", "2.1.2", "1.4.13"],
    "tests": [
        {
            "id": "dialog-heading-structure",
            "name": "Dialog Heading Structure",
            "description": "Checks if dialogs have proper heading structure, typically starting with a level 2 heading (h2). This helps screen reader users understand the organization and purpose of dialog content.",
            "impact": "high",
            "wcagCriteria": ["4.1.2", "2.4.6"],
        },
        {
            "id": "dialog-close-button",
            "name": "Dialog Close Mechanism",
            "description": "Verifies that dialogs have accessible close buttons that are properly labeled and can be activated by keyboard. Without a clear close mechanism, keyboard-only users may become trapped in dialogs.",
            "impact": "critical",
            "wcagCriteria": ["2.1.1", "2.1.2"],
        },
        {
            "id": "dialog-focus-management",
            "name": "Focus Management",
            "description": "Evaluates whether dialog close mechanisms properly manage keyboard focus, returning it to an appropriate location when the dialog is dismissed.",
            "impact": "high",
            "wcagCriteria": ["2.4.3", "2.4.7"],
        },
        {
            "id": "dialog-content-obscuring",
            "name": "Content Obscuring",
            "description": "Identifies cases where floating dialogs obscure interactive page content, making it inaccessible to users.",
            "impact": "critical",
            "wcagCriteria": ["2.1.1", "1.4.13"],
        }
    ]
}

async def test_floating_dialogs(page) -> Dict[str, Any]:
    """
    Test floating dialogs for proper implementation and content obscuring
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # First, extract breakpoints from stylesheets
        breakpoints = await page.evaluate(r'''
            () => {
                const breakpoints = new Set();

                // Parse all stylesheets for media queries
                for (const sheet of document.styleSheets) {
                    try {
                        if (sheet.cssRules) {
                            for (const rule of sheet.cssRules) {
                                if (rule instanceof CSSMediaRule) {
                                    // Extract width values from media query
                                    const media = rule.media.mediaText;
                                    const widthMatches = media.match(/(?:min-width|max-width):\s*(\d+)px/g);
                                    if (widthMatches) {
                                        widthMatches.forEach(match => {
                                            const value = parseInt(match.match(/(\d+)px/)[1]);
                                            breakpoints.add(value);
                                        });
                                    }
                                }
                            }
                        }
                    } catch (e) {
                        // Skip stylesheets we can't access (CORS)
                    }
                }

                // Add common breakpoints if none found
                if (breakpoints.size === 0) {
                    return [320, 768, 1024, 1440];
                }

                // Convert to array and sort, add mobile if not present
                const bpArray = Array.from(breakpoints).sort((a, b) => a - b);
                if (!bpArray.includes(320)) {
                    bpArray.unshift(320);
                }
                // Add desktop width if largest is small
                if (bpArray[bpArray.length - 1] < 1200) {
                    bpArray.push(1440);
                }

                return bpArray;
            }
        ''')

        logger.info(f"Testing dialogs at breakpoints: {breakpoints}")

        # Store original viewport (page.viewport is a property, not a method)
        original_viewport = page.viewport

        # Collect all errors/warnings/passes across all breakpoints
        all_errors = []
        all_warnings = []
        all_passes = []
        total_elements_tested = 0
        total_elements_passed = 0
        total_elements_failed = 0
        test_applicable = False
        not_applicable_reason = ''

        # Test at each breakpoint
        for breakpoint_width in breakpoints:
            # Set viewport to breakpoint
            await page.setViewport({
                'width': breakpoint_width,
                'height': original_viewport.get('height', 1080) if original_viewport else 1080
            })

            # Wait a moment for layout to settle
            await page.evaluate('() => new Promise(resolve => setTimeout(resolve, 300))')

            # Execute JavaScript to analyze floating dialogs at this breakpoint
            # Build the JavaScript code with breakpoint_width injected
            js_code = '''
                () => {
                    const breakpointWidth = ''' + str(breakpoint_width) + ''';
                    const results = {
                        applicable: true,
                        errors: [],
                        warnings: [],
                        passes: [],
                        elements_tested: 0,
                        elements_passed: 0,
                        elements_failed: 0,
                        test_name: 'floating_dialogs',
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
                
                // Check if element is visible
                function isVisible(element) {
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           style.opacity !== '0';
                }
                
                // Check if element is interactive
                function isInteractive(element) {
                    const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'details'];
                    const interactiveRoles = ['button', 'checkbox', 'combobox', 'link', 'menuitem', 'option', 'radio', 'switch', 'tab', 'textbox'];
                    
                    if (interactiveTags.includes(element.tagName.toLowerCase())) {
                        return true;
                    }
                    
                    const role = element.getAttribute('role');
                    if (role && interactiveRoles.includes(role)) {
                        return true;
                    }
                    
                    return element.hasAttribute('tabindex') || 
                           element.hasAttribute('onclick') || 
                           element.hasAttribute('onkeydown');
                }
                
                // Get heading level of dialog
                function getHeadingLevel(dialog) {
                    const heading = dialog.querySelector('h1, h2, h3, h4, h5, h6');
                    if (heading) {
                        return parseInt(heading.tagName.substring(1));
                    }
                    
                    const ariaLevel = dialog.querySelector('[role="heading"]');
                    if (ariaLevel) {
                        return parseInt(ariaLevel.getAttribute('aria-level') || '1');
                    }
                    
                    return null;
                }
                
                // Check for close button
                function hasCloseButton(dialog) {
                    const closeButtons = dialog.querySelectorAll(
                        'button[aria-label*="close" i], button[title*="close" i], ' +
                        '[role="button"][aria-label*="close" i], [role="button"][title*="close" i], ' +
                        'button.close, .close-button, .btn-close'
                    );
                    
                    return closeButtons.length > 0;
                }
                
                // Check for content overlap
                function checkContentOverlap(dialog) {
                    const dialogRect = dialog.getBoundingClientRect();
                    const allElements = Array.from(document.body.querySelectorAll('*'));
                    const overlappingInteractive = [];

                    allElements.forEach(element => {
                        if (element !== dialog && !dialog.contains(element)) {
                            const elementRect = element.getBoundingClientRect();

                            // Check if elements overlap
                            if (!(elementRect.right < dialogRect.left ||
                                  elementRect.left > dialogRect.right ||
                                  elementRect.bottom < dialogRect.top ||
                                  elementRect.top > dialogRect.bottom)) {

                                // Only include visible interactive elements
                                if (isVisible(element) && isInteractive(element)) {
                                    overlappingInteractive.push({
                                        element: element.tagName.toLowerCase(),
                                        xpath: getFullXPath(element),
                                        text: element.textContent.trim().substring(0, 50)
                                    });
                                }
                            }
                        }
                    });

                    return overlappingInteractive;
                }
                
                // Find all potential dialogs
                const dialogCandidates = [
                    ...Array.from(document.querySelectorAll('dialog')),
                    ...Array.from(document.querySelectorAll('[role="dialog"]')),
                    ...Array.from(document.querySelectorAll('[class*="modal"]')),
                    ...Array.from(document.querySelectorAll('div'))
                        .filter(div => {
                            const style = window.getComputedStyle(div);
                            return style.zIndex !== 'auto' && parseInt(style.zIndex) > 100;
                        })
                ];

                // Deduplicate
                const uniqueDialogs = Array.from(new Set(dialogCandidates));

                // Filter out nested dialogs - only keep outermost
                const dialogs = uniqueDialogs.filter(dialog => {
                    return !uniqueDialogs.some(otherDialog =>
                        otherDialog !== dialog && otherDialog.contains(dialog)
                    );
                });

                // Filter for visible dialogs
                const visibleDialogs = dialogs.filter(isVisible);
                
                if (visibleDialogs.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No visible dialogs found on the page';
                    return results;
                }
                
                results.elements_tested = visibleDialogs.length;
                
                // Test each dialog
                visibleDialogs.forEach(dialog => {
                    const headingLevel = getHeadingLevel(dialog);
                    const hasClose = hasCloseButton(dialog);
                    const overlappingElements = checkContentOverlap(dialog);
                    
                    // Check heading structure
                    if (!headingLevel || headingLevel !== 2) {
                        results.errors.push({
                            err: 'ErrIncorrectHeadingLevel',
                            type: 'err',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: `Dialog should have h2 heading, found: ${headingLevel ? 'h' + headingLevel : 'none'}`,
                            currentLevel: headingLevel
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check close button
                    if (!hasClose) {
                        results.errors.push({
                            err: 'ErrMissingCloseButton',
                            type: 'err',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: 'Dialog is missing an accessible close button'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for content obscuring
                    if (overlappingElements.length > 0) {
                        results.errors.push({
                            err: 'ErrContentObscuring',
                            type: 'err',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: `Dialog obscures ${overlappingElements.length} interactive element(s) at ${breakpointWidth}px viewport`,
                            obscuredCount: overlappingElements.length,
                            obscuredElements: overlappingElements,
                            dialogXpath: getFullXPath(dialog),
                            breakpoint: breakpointWidth
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for proper ARIA attributes
                    const ariaModal = dialog.getAttribute('aria-modal');
                    const ariaLabelledby = dialog.getAttribute('aria-labelledby');
                    const ariaDescribedby = dialog.getAttribute('aria-describedby');
                    
                    if (ariaModal !== 'true') {
                        results.warnings.push({
                            err: 'WarnMissingAriaModal',
                            type: 'warn',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: 'Dialog should have aria-modal="true" attribute'
                        });
                    }
                    
                    if (!ariaLabelledby) {
                        results.warnings.push({
                            err: 'WarnMissingAriaLabelledby',
                            type: 'warn',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: 'Dialog should have aria-labelledby attribute referencing its heading'
                        });
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Dialog accessibility',
                    wcag: ['4.1.2', '2.4.6', '2.1.1', '2.1.2'],
                    total: visibleDialogs.length * 3, // 3 main checks per dialog
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });

                return results;
                }
            '''

            results = await page.evaluate(js_code)

            # Aggregate results from this breakpoint
            if results['applicable']:
                test_applicable = True

            # Deduplicate errors by signature (xpath + error type, but keep breakpoint-specific ones)
            for error in results.get('errors', []):
                # Check if we already have this error at a different breakpoint
                signature = f"{error.get('err')}:{error.get('xpath')}"
                existing = next((e for e in all_errors if f"{e.get('err')}:{e.get('xpath')}" == signature), None)

                if not existing:
                    all_errors.append(error)
                elif error.get('err') == 'ErrContentObscuring':
                    # For content obscuring, we want to keep all breakpoint-specific instances
                    all_errors.append(error)

            all_warnings.extend(results.get('warnings', []))
            all_passes.extend(results.get('passes', []))
            total_elements_tested += results.get('elements_tested', 0)
            total_elements_passed += results.get('elements_passed', 0)
            total_elements_failed += results.get('elements_failed', 0)

            if not results['applicable'] and not not_applicable_reason:
                not_applicable_reason = results.get('not_applicable_reason', '')

        # Restore original viewport
        if original_viewport:
            await page.setViewport(original_viewport)

        # Return aggregated results
        final_results = {
            'applicable': test_applicable,
            'not_applicable_reason': not_applicable_reason if not test_applicable else '',
            'errors': all_errors,
            'warnings': all_warnings,
            'passes': all_passes,
            'elements_tested': total_elements_tested,
            'elements_passed': total_elements_passed,
            'elements_failed': total_elements_failed,
            'test_name': 'floating_dialogs',
            'checks': []
        }

        if test_applicable and total_elements_tested > 0:
            final_results['checks'].append({
                'description': 'Dialog accessibility',
                'wcag': ['4.1.2', '2.4.6', '2.1.1', '2.1.2'],
                'total': total_elements_tested * 3,
                'passed': total_elements_passed,
                'failed': total_elements_failed
            })

        return final_results
        
    except Exception as e:
        logger.error(f"Error in test_floating_dialogs: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }