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

                // If no breakpoints found in CSS, test at current viewport only
                if (breakpoints.size === 0) {
                    return [window.innerWidth];
                }

                // Return only the breakpoints declared in the page's CSS
                return Array.from(breakpoints).sort((a, b) => a - b);
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
                function getHeadingInfo(dialog) {
                    const heading = dialog.querySelector('h1, h2, h3, h4, h5, h6');
                    if (heading) {
                        return {
                            level: parseInt(heading.tagName.substring(1)),
                            text: heading.textContent.trim().substring(0, 100)
                        };
                    }
                    
                    const ariaLevel = dialog.querySelector('[role="heading"]');
                    if (ariaLevel) {
                        return {
                            level: parseInt(ariaLevel.getAttribute('aria-level') || '1'),
                            text: ariaLevel.textContent.trim().substring(0, 100)
                        };
                    }
                    
                    return null;
                }
                
                // Check for close button or dismiss mechanism
                function hasCloseButton(dialog) {
                    // Find potential close buttons using multiple selectors
                    const closeButtons = dialog.querySelectorAll([
                        // Semantic buttons with close labels (exclude "disclosure" false positives)
                        'button[aria-label*="close" i]',
                        'button[title*="close" i]',
                        'button[aria-label*="dismiss" i]',

                        // Role=button with close labels
                        '[role="button"][aria-label*="close" i]',
                        '[role="button"][title*="close" i]',
                        '[role="button"][aria-label*="dismiss" i]',

                        // Common close button classes
                        'button.close',
                        'button.btn-close',
                        '.close-button',
                        '.modal-close',

                        // Data attributes (Bootstrap, Material UI, etc.)
                        'button[data-dismiss="modal"]',
                        'button[data-bs-dismiss="modal"]',
                        '[data-dialog-close]',
                    ].join(', '));

                    // Filter to only visible, non-disabled buttons
                    const visibleButtons = Array.from(closeButtons).filter(btn => {
                        const style = window.getComputedStyle(btn);
                        const isDisplayed = style.display !== 'none' &&
                                          style.visibility !== 'hidden' &&
                                          style.opacity !== '0';
                        const isEnabled = !btn.disabled && !btn.hasAttribute('disabled');

                        return isDisplayed && isEnabled;
                    });

                    // Also check for aria-label containing "close" after filtering out "disclosure"
                    const filteredButtons = visibleButtons.filter(btn => {
                        const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                        if (label.includes('close')) {
                            return !label.includes('disclosure') && !label.includes('enclose');
                        }
                        return true;
                    });

                    if (filteredButtons.length > 0) {
                        return true;
                    }
                    
                    // Check for single-button dialogs (like cookie consent with just "OK")
                    // These are valid because the single button serves as the dismiss mechanism
                    const allButtons = dialog.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"]');
                    const visibleActionButtons = Array.from(allButtons).filter(btn => {
                        const style = window.getComputedStyle(btn);
                        const isDisplayed = style.display !== 'none' &&
                                          style.visibility !== 'hidden' &&
                                          style.opacity !== '0';
                        const isEnabled = !btn.disabled && !btn.hasAttribute('disabled');
                        return isDisplayed && isEnabled;
                    });
                    
                    // If there's exactly one button, it serves as the dismiss mechanism
                    // Common for cookie notices, alerts, confirmations
                    if (visibleActionButtons.length === 1) {
                        return true;
                    }
                    
                    // Also check for buttons with accept/acknowledge/ok/confirm text
                    // These are valid dismiss mechanisms for consent dialogs
                    const dismissActionButtons = Array.from(allButtons).filter(btn => {
                        const style = window.getComputedStyle(btn);
                        const isDisplayed = style.display !== 'none' &&
                                          style.visibility !== 'hidden' &&
                                          style.opacity !== '0';
                        const isEnabled = !btn.disabled && !btn.hasAttribute('disabled');
                        if (!isDisplayed || !isEnabled) return false;
                        
                        const text = (btn.textContent || '').toLowerCase().trim();
                        const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                        const title = (btn.getAttribute('title') || '').toLowerCase();
                        const combined = text + ' ' + label + ' ' + title;
                        
                        // Accept these as valid dismiss mechanisms
                        const dismissPatterns = ['ok', 'accept', 'agree', 'confirm', 'got it', 'acknowledge', 'understood', 'i understand', 'continue', 'proceed'];
                        return dismissPatterns.some(pattern => combined.includes(pattern));
                    });
                    
                    return dismissActionButtons.length > 0;
                }
                
                // Check for content overlap
                function checkContentOverlap(dialog) {
                    const dialogRect = dialog.getBoundingClientRect();
                    const dialogStyle = window.getComputedStyle(dialog);
                    const allElements = Array.from(document.body.querySelectorAll('*'));
                    const overlappingInteractive = [];
                    
                    // For fixed-position elements, we need to check what they WOULD cover
                    // when user scrolls to different parts of the page
                    const isFixedDialog = dialogStyle.position === 'fixed';
                    const viewportHeight = window.innerHeight;
                    const viewportWidth = window.innerWidth;

                    allElements.forEach(element => {
                        if (element !== dialog && !dialog.contains(element)) {
                            // Skip elements inside the dialog
                            if (dialog.contains(element)) return;
                            
                            const elementRect = element.getBoundingClientRect();
                            let overlaps = false;
                            
                            if (isFixedDialog) {
                                // For fixed dialogs (like cookie banners at bottom),
                                // check if element's horizontal position overlaps
                                // and if the element exists in the area the dialog covers
                                const horizontalOverlap = !(elementRect.right < dialogRect.left ||
                                                          elementRect.left > dialogRect.right);
                                
                                // For fixed bottom dialogs, any element at the bottom of its 
                                // scroll position would be covered when scrolled into view
                                // Check if this element's document position would put it under the dialog
                                const elementDocTop = elementRect.top + window.scrollY;
                                const elementDocBottom = elementRect.bottom + window.scrollY;
                                const docHeight = document.documentElement.scrollHeight;
                                
                                // Element would be covered if when scrolled to show it at bottom of viewport,
                                // it would be behind the fixed dialog
                                // This happens if the element is within dialogRect.height of the bottom of content
                                const dialogHeight = dialogRect.height;
                                const distanceFromDocBottom = docHeight - elementDocBottom;
                                
                                // If element is close enough to bottom that scrolling to it 
                                // would place it behind the fixed bottom dialog
                                const wouldBeCovered = distanceFromDocBottom < dialogHeight && horizontalOverlap;
                                
                                // Also check current viewport overlap
                                const currentOverlap = !(elementRect.right < dialogRect.left ||
                                                        elementRect.left > dialogRect.right ||
                                                        elementRect.bottom < dialogRect.top ||
                                                        elementRect.top > dialogRect.bottom);
                                
                                overlaps = wouldBeCovered || currentOverlap;
                            } else {
                                // Standard overlap check for non-fixed dialogs
                                overlaps = !(elementRect.right < dialogRect.left ||
                                            elementRect.left > dialogRect.right ||
                                            elementRect.bottom < dialogRect.top ||
                                            elementRect.top > dialogRect.bottom);
                            }

                            if (overlaps && isVisible(element) && isInteractive(element)) {
                                overlappingInteractive.push({
                                    element: element.tagName.toLowerCase(),
                                    xpath: getFullXPath(element),
                                    text: element.textContent.trim().substring(0, 50)
                                });
                            }
                        }
                    });

                    return overlappingInteractive;
                }
                
                // Find all potential dialogs using semantic selectors first
                const semanticDialogs = [
                    ...Array.from(document.querySelectorAll('dialog')),
                    ...Array.from(document.querySelectorAll('[role="dialog"]')),
                    ...Array.from(document.querySelectorAll('[role="alertdialog"]')),
                    ...Array.from(document.querySelectorAll('[aria-modal="true"]')),
                ];

                // Find heuristic-based floating elements (dialogs, banners, notices, etc.)
                const heuristicDialogs = Array.from(document.querySelectorAll('div'))
                    .filter(div => {
                        const style = window.getComputedStyle(div);
                        const classes = (div.className || '').toLowerCase();
                        const id = (div.id || '').toLowerCase();

                        // Must have high z-index
                        if (style.zIndex === 'auto' || parseInt(style.zIndex) <= 100) {
                            return false;
                        }
                        
                        // Must be fixed or absolute positioned (floating)
                        if (style.position !== 'fixed' && style.position !== 'absolute') {
                            return false;
                        }

                        // Exclude common false positives by class name
                        const excludePatterns = [
                            'backdrop', 'overlay', 'mask', 'shade',
                            'dropdown', 'tooltip', 'popover', 'menu',
                            'nav', 'header', 'footer', 'sidebar'
                        ];

                        for (const pattern of excludePatterns) {
                            if (classes.includes(pattern)) {
                                return false;
                            }
                        }

                        // Include if class/id suggests it's a modal, dialog, banner, notice, etc.
                        const includePatterns = [
                            'modal', 'dialog', 'alert', 'banner', 'notice', 
                            'cookie', 'consent', 'popup', 'lightbox', 'toast',
                            'notification', 'snackbar', 'floating'
                        ];
                        
                        for (const pattern of includePatterns) {
                            if (classes.includes(pattern) || id.includes(pattern)) {
                                return true;
                            }
                        }
                        
                        return false;
                    });

                // Combine all candidates
                const allCandidates = [...semanticDialogs, ...heuristicDialogs];

                // Deduplicate
                const uniqueDialogs = Array.from(new Set(allCandidates));

                // Filter out backdrops and false positives based on content
                const contentDialogs = uniqueDialogs.filter(dialog => {
                    const classes = (dialog.className || '').toLowerCase();
                    const hasContent = dialog.textContent.trim().length > 0;
                    const hasInteractive = dialog.querySelectorAll('button, a, input, select, textarea, [tabindex]').length > 0;
                    const hasHeading = dialog.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]').length > 0;

                    // Exclude if class name explicitly indicates backdrop/overlay
                    if (classes.includes('backdrop') ||
                        classes.includes('overlay') ||
                        classes.includes('mask') ||
                        classes.includes('shade')) {
                        return false;
                    }

                    // Exclude if it has no meaningful content (likely a backdrop)
                    if (!hasContent && !hasInteractive && !hasHeading) {
                        return false;
                    }

                    // Exclude if it's too small (likely a tooltip/dropdown)
                    const rect = dialog.getBoundingClientRect();
                    if (rect.width < 200 && rect.height < 100) {
                        return false;
                    }

                    return true;
                });

                // Filter out nested dialogs - only keep outermost
                const dialogs = contentDialogs.filter(dialog => {
                    return !contentDialogs.some(otherDialog =>
                        otherDialog !== dialog && otherDialog.contains(dialog)
                    );
                });

                // Filter for visible dialogs
                const visibleDialogs = dialogs.filter(isVisible);
                
                // Debug info
                results._debug = {
                    semanticDialogsCount: semanticDialogs.length,
                    heuristicDialogsCount: heuristicDialogs.length,
                    uniqueDialogsCount: uniqueDialogs.length,
                    contentDialogsCount: contentDialogs.length,
                    visibleDialogsCount: visibleDialogs.length,
                    visibleDialogs: visibleDialogs.map(d => ({
                        tag: d.tagName,
                        id: d.id,
                        class: d.className,
                        ariaModal: d.getAttribute('aria-modal'),
                        role: d.getAttribute('role')
                    }))
                };
                
                if (visibleDialogs.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No visible dialogs found on the page';
                    return results;
                }
                
                results.elements_tested = visibleDialogs.length;
                
                // Test each dialog
                visibleDialogs.forEach(dialog => {
                    const headingInfo = getHeadingInfo(dialog);
                    const headingLevel = headingInfo ? headingInfo.level : null;
                    const headingText = headingInfo ? headingInfo.text : '';
                    const hasClose = hasCloseButton(dialog);
                    const overlappingElements = checkContentOverlap(dialog);
                    
                    // Check heading structure - dialogs should have H2 headings
                    if (!headingLevel) {
                        // No heading at all
                        results.errors.push({
                            err: 'ErrModalNoHeading',
                            type: 'err',
                            cat: 'dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: 'Modal or dialog has no heading to identify its purpose'
                        });
                        results.elements_failed++;
                    } else if (headingLevel !== 2 && headingLevel !== 1) {
                        // Has heading but wrong level (not h1 or h2)
                        results.errors.push({
                            err: 'ErrModalMissingHeading',
                            type: 'err',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: `Dialog has h${headingLevel} heading but should use h2 (or h1)`,
                            foundLevel: headingLevel,
                            headingText: headingText
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
                    // Modal dialogs (aria-modal="true") are EXPECTED to obscure content - that's their purpose
                    // They trap focus and prevent interaction with background content by design
                    // Only flag non-modal floating elements that obscure content unexpectedly
                    const isModal = dialog.getAttribute('aria-modal') === 'true' || 
                                   dialog.tagName.toLowerCase() === 'dialog' ||
                                   dialog.getAttribute('role') === 'alertdialog';
                    
                    // Add per-dialog debug info
                    if (!results._dialogDebug) results._dialogDebug = [];
                    results._dialogDebug.push({
                        id: dialog.id,
                        class: dialog.className,
                        isModal: isModal,
                        headingLevel: headingLevel,
                        headingText: headingText,
                        hasClose: hasClose,
                        overlappingCount: overlappingElements.length,
                        overlapping: overlappingElements.slice(0, 5)
                    });
                    
                    if (overlappingElements.length > 0 && !isModal) {
                        // This is a non-modal floating element obscuring content - problematic
                        results.errors.push({
                            err: 'ErrContentObscuring',
                            type: 'err',
                            cat: 'floating_dialogs',
                            element: dialog.tagName,
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: `Non-modal floating element obscures ${overlappingElements.length} interactive element(s) at ${breakpointWidth}px viewport. Unlike modal dialogs, this element does not trap focus, so users may try to interact with obscured content.`,
                            metadata: {
                                obscuredCount: overlappingElements.length,
                                obscuredElements: overlappingElements,
                                dialogXpath: getFullXPath(dialog),
                                breakpoint: breakpointWidth
                            }
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

            # Log debug info for troubleshooting
            if results.get('_debug'):
                logger.warning(f"DEBUG floating_dialogs at {breakpoint_width}px: {results['_debug']}")
            if results.get('_dialogDebug'):
                logger.warning(f"DEBUG dialog details at {breakpoint_width}px: {results['_dialogDebug']}")
            if results.get('errors'):
                error_codes = [e.get('err') for e in results['errors']]
                logger.warning(f"DEBUG floating_dialogs errors at {breakpoint_width}px: {error_codes}")

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