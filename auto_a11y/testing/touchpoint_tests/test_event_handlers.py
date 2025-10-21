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

                // DISCOVERY: Report each script element and inline event handler individually
                const scriptElements = Array.from(document.querySelectorAll('script[src], script:not([src])'));
                scriptElements.forEach(script => {
                    const src = script.getAttribute('src');
                    const isInline = !src;
                    const scriptContent = isInline ? script.textContent.substring(0, 100) : '';

                    results.warnings.push({
                        err: 'DiscoFoundJS',
                        type: 'disco',
                        cat: 'event_handlers',
                        element: 'script',
                        xpath: getFullXPath(script),
                        html: script.outerHTML.substring(0, 200),
                        description: isInline
                            ? `Inline <script> tag detected - ensure progressive enhancement and that functionality works without JavaScript`
                            : `External script "${src}" detected - ensure progressive enhancement and that functionality works without JavaScript`,
                        scriptType: isInline ? 'inline' : 'external',
                        src: src || null
                    });
                });

                // DISCOVERY: Report elements with inline event handler attributes
                const elementsWithHandlers = Array.from(document.querySelectorAll('*'))
                    .filter(el => Array.from(el.attributes).some(attr => attr.name.startsWith('on')));

                elementsWithHandlers.forEach(element => {
                    const handlers = Array.from(element.attributes)
                        .filter(attr => attr.name.startsWith('on'))
                        .map(attr => attr.name)
                        .join(', ');

                    results.warnings.push({
                        err: 'DiscoFoundJS',
                        type: 'disco',
                        cat: 'event_handlers',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element has inline event handler attributes (${handlers}) - ensure keyboard accessibility and progressive enhancement`,
                        eventHandlers: handlers
                    });
                });

                return results;
            }
        ''')

        # Additional check: Focus indicators for interactive elements (tabindex/event handlers)
        # Extract elements with tabindex or inline event handlers and check their focus styles
        focus_elements = await page.evaluate('''
            () => {
                const elements = [];

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

                // Helper to parse color values to RGBA
                function parseColor(colorStr) {
                    if (!colorStr || colorStr === 'transparent') {
                        return { r: 0, g: 0, b: 0, a: 0 };
                    }
                    const rgbaMatch = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
                    if (rgbaMatch) {
                        return {
                            r: parseInt(rgbaMatch[1]),
                            g: parseInt(rgbaMatch[2]),
                            b: parseInt(rgbaMatch[3]),
                            a: rgbaMatch[4] !== undefined ? parseFloat(rgbaMatch[4]) : 1
                        };
                    }
                    const hexMatch = colorStr.match(/^#([0-9a-f]{6})$/i);
                    if (hexMatch) {
                        const hex = hexMatch[1];
                        return {
                            r: parseInt(hex.substr(0, 2), 16),
                            g: parseInt(hex.substr(2, 2), 16),
                            b: parseInt(hex.substr(4, 2), 16),
                            a: 1
                        };
                    }
                    return { r: 0, g: 0, b: 0, a: 1 };
                }

                // Calculate relative luminance
                function getLuminance(color) {
                    const rsRGB = color.r / 255;
                    const gsRGB = color.g / 255;
                    const bsRGB = color.b / 255;
                    const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
                    const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
                    const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);
                    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
                }

                // Interactive tags to exclude (already natively interactive)
                const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'summary', 'details'];
                const interactiveRoles = [
                    'button', 'link', 'checkbox', 'radio', 'tab', 'menuitem',
                    'menuitemcheckbox', 'menuitemradio', 'option', 'switch',
                    'textbox', 'searchbox', 'slider', 'spinbutton', 'combobox',
                    'scrollbar', 'gridcell', 'treeitem'
                ];

                // Find all elements with tabindex >= -1
                const allElements = document.querySelectorAll('[tabindex]');
                allElements.forEach((element) => {
                    const tabindex = parseInt(element.getAttribute('tabindex'));
                    if (tabindex < -1) return; // Skip non-focusable

                    const tagName = element.tagName.toLowerCase();
                    const role = element.getAttribute('role');

                    // Skip semantic interactive elements
                    if (interactiveTags.includes(tagName)) return;
                    if (role && interactiveRoles.includes(role)) return;

                    // Extract styles
                    const computed = window.getComputedStyle(element);

                    // Extract :focus styles from stylesheets
                    let focusOutlineStyle = null;
                    let focusOutlineWidth = null;
                    let focusOutlineColor = null;
                    let focusBoxShadow = null;
                    let focusBorderWidth = null;
                    let focusBackgroundColor = null;

                    try {
                        for (let sheet of document.styleSheets) {
                            try {
                                const rules = sheet.cssRules || sheet.rules;
                                if (!rules) continue;

                                for (let rule of rules) {
                                    if (!rule.selectorText || !rule.selectorText.includes(':focus')) continue;

                                    const testSelector = rule.selectorText.replace(/:focus.*?(?=[,\\s]|$)/g, '').trim();
                                    if (!testSelector) continue;

                                    try {
                                        if (element.matches(testSelector)) {
                                            if (rule.style.outlineStyle !== undefined && rule.style.outlineStyle !== '') {
                                                focusOutlineStyle = rule.style.outlineStyle;
                                            }
                                            if (rule.style.outlineWidth !== undefined && rule.style.outlineWidth !== '') {
                                                focusOutlineWidth = rule.style.outlineWidth;
                                            }
                                            if (rule.style.outlineColor !== undefined && rule.style.outlineColor !== '') {
                                                focusOutlineColor = rule.style.outlineColor;
                                            }
                                            if (rule.style.outline !== undefined && rule.style.outline !== '') {
                                                const outlineValue = rule.style.outline;
                                                if (outlineValue === 'none' || outlineValue === '0') {
                                                    focusOutlineStyle = 'none';
                                                    focusOutlineWidth = '0px';
                                                } else {
                                                    const parts = outlineValue.split(' ');
                                                    for (let part of parts) {
                                                        if (part.includes('px') || part.includes('em') || part.includes('rem')) {
                                                            focusOutlineWidth = part;
                                                        } else if (['solid', 'dotted', 'dashed', 'double'].includes(part)) {
                                                            focusOutlineStyle = part;
                                                        }
                                                    }
                                                    const colorParts = parts.filter(p =>
                                                        !p.match(/^\\d+(\\.\\d+)?(px|em|rem)$/) &&
                                                        !['solid', 'dotted', 'dashed', 'double'].includes(p)
                                                    );
                                                    if (colorParts.length > 0) {
                                                        focusOutlineColor = colorParts.join(' ');
                                                    }
                                                }
                                            }
                                            if (rule.style.boxShadow !== undefined && rule.style.boxShadow !== '') {
                                                focusBoxShadow = rule.style.boxShadow;
                                            }
                                            if (rule.style.borderWidth !== undefined && rule.style.borderWidth !== '') {
                                                focusBorderWidth = rule.style.borderWidth;
                                            }
                                            if (rule.style.backgroundColor !== undefined && rule.style.backgroundColor !== '') {
                                                focusBackgroundColor = rule.style.backgroundColor;
                                            }
                                        }
                                    } catch (e) {
                                        // Invalid selector
                                    }
                                }
                            } catch (e) {
                                // Cross-origin stylesheet
                            }
                        }
                    } catch (e) {
                        // Error accessing stylesheets
                    }

                    // Check for inline event handlers
                    const eventAttrs = ['onclick', 'onkeydown', 'onkeyup', 'onkeypress', 'onmousedown', 'onmouseup'];
                    const hasInlineHandler = eventAttrs.some(attr => element.hasAttribute(attr));

                    // Check if parent is an interactive element (for detecting redundant focusable children)
                    let parentIsInteractive = false;
                    let parentTag = '';
                    if (element.parentElement) {
                        const parent = element.parentElement;
                        parentTag = parent.tagName.toLowerCase();
                        const parentTabindex = parseInt(parent.getAttribute('tabindex') || '-1');
                        const interactiveTags = ['button', 'a', 'summary'];
                        parentIsInteractive = interactiveTags.includes(parentTag) || parentTabindex >= 0;
                    }

                    // Check for aria-hidden
                    const ariaHidden = element.getAttribute('aria-hidden');

                    elements.push({
                        tag: tagName,
                        id: element.id || '',
                        className: element.className || '',
                        tabindex: tabindex,
                        role: role || '',
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 300),  // Capture HTML snippet for display
                        hasInlineHandler: hasInlineHandler,
                        parentTag: parentTag,
                        parentIsInteractive: parentIsInteractive,
                        ariaHidden: ariaHidden,
                        normalOutlineStyle: computed.outlineStyle,
                        normalOutlineWidth: computed.outlineWidth,
                        normalBorderWidth: computed.borderWidth,
                        normalBoxShadow: computed.boxShadow,
                        backgroundColor: computed.backgroundColor,
                        backgroundImage: computed.backgroundImage,
                        focusOutlineStyle,
                        focusOutlineWidth,
                        focusOutlineColor,
                        focusBoxShadow,
                        focusBorderWidth,
                        focusBackgroundColor
                    });
                });

                return elements;
            }
        ''')

        # Process focus indicator data in Python
        if focus_elements:
            import re

            def parse_px(value):
                """Parse pixel value from CSS string"""
                if not value:
                    return 0
                try:
                    if isinstance(value, str):
                        return float(value.replace('px', '').replace('em', '').replace('rem', '').strip())
                    return float(value)
                except:
                    return 0

            def parse_color(color_str):
                """Parse CSS color to RGBA dict"""
                if not color_str or color_str == 'transparent' or color_str == 'initial':
                    return {'r': 0, 'g': 0, 'b': 0, 'a': 0}
                match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
                if match:
                    return {
                        'r': int(match.group(1)),
                        'g': int(match.group(2)),
                        'b': int(match.group(3)),
                        'a': float(match.group(4)) if match.group(4) else 1.0
                    }
                match = re.match(r'#([0-9a-fA-F]{6})', color_str)
                if match:
                    hex_val = match.group(1)
                    return {
                        'r': int(hex_val[0:2], 16),
                        'g': int(hex_val[2:4], 16),
                        'b': int(hex_val[4:6], 16),
                        'a': 1.0
                    }
                return {'r': 0, 'g': 0, 'b': 0, 'a': 1}

            def get_luminance(color):
                """Calculate relative luminance"""
                r = color['r'] / 255.0
                g = color['g'] / 255.0
                b = color['b'] / 255.0
                r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
                g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
                b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
                return 0.2126 * r + 0.7152 * g + 0.0722 * b

            def get_contrast_ratio(color1, color2):
                """Calculate contrast ratio between two colors"""
                l1 = get_luminance(color1)
                l2 = get_luminance(color2)
                lighter = max(l1, l2)
                darker = min(l1, l2)
                return (lighter + 0.05) / (darker + 0.05)

            # Process each element
            for elem in focus_elements:
                element_id = f"#{elem.get('id')}" if elem.get('id') else f"{elem['tag']}.{elem.get('className', '')}"
                elem_type = 'tabindex' if elem.get('tabindex') is not None else 'handler'

                # Determine error code prefix
                code_prefix = 'ErrTabindex' if elem_type == 'tabindex' else 'ErrHandler'
                warn_prefix = 'WarnTabindex' if elem_type == 'tabindex' else 'WarnHandler'

                # Parse focus styles
                focus_outline_style = elem.get('focusOutlineStyle')
                focus_outline_width = parse_px(elem.get('focusOutlineWidth'))
                focus_outline_color = elem.get('focusOutlineColor')
                focus_box_shadow = elem.get('focusBoxShadow')

                # Check if gradient background
                bg_image = elem.get('backgroundImage', 'none')
                has_gradient = bg_image and 'gradient' in bg_image

                # Determine if element has custom focus styles
                outline_is_none = focus_outline_style == 'none'
                has_outline = focus_outline_style and focus_outline_style not in ['none', 'initial', ''] and focus_outline_width > 0
                box_shadow_changed = focus_box_shadow and focus_box_shadow not in ['none', 'initial', '']

                # Check for border/bg changes
                normal_border_width = parse_px(elem.get('normalBorderWidth', '0px'))
                focus_border_width = parse_px(elem.get('focusBorderWidth')) if elem.get('focusBorderWidth') else normal_border_width
                border_width_changed = abs(focus_border_width - normal_border_width) > 0.5

                normal_bg_color = elem.get('backgroundColor')
                focus_bg_color = elem.get('focusBackgroundColor')
                bg_color_changed = focus_bg_color and focus_bg_color not in ['', 'initial'] and focus_bg_color != normal_bg_color

                # Run all checks independently
                issues_found = []

                # Check 0: Focusable child inside interactive parent
                if elem.get('parentIsInteractive', False):
                    parent_tag = elem.get('parentTag', 'unknown')
                    desc = f"Child element with tabindex={elem.get('tabindex')} inside interactive <{parent_tag}> parent"
                    issues_found.append((f'{code_prefix}ChildOfInteractive', desc))

                # Check 0b: aria-hidden on focusable element
                aria_hidden = elem.get('ariaHidden', '')
                if aria_hidden == 'true':
                    desc = f"Element with {'tabindex' if elem_type == 'tabindex' else 'event handler'} has aria-hidden='true', which is invalid"
                    issues_found.append((f'{code_prefix}AriaHiddenFocusable', desc))

                # Check 1: No visible focus indicator
                if not has_outline and not box_shadow_changed and not border_width_changed and not bg_color_changed:
                    desc = f"Element with {'tabindex' if elem_type == 'tabindex' else 'event handler'} has no visible focus indicator"
                    issues_found.append((f'{code_prefix}NoVisibleFocus', desc))

                # Check 2: outline:none without alternative
                if outline_is_none and not box_shadow_changed and not border_width_changed and not bg_color_changed:
                    desc = f"Element sets outline:none without alternative focus indicator"
                    issues_found.append((f'{code_prefix}OutlineNoneNoBoxShadow', desc))

                # Check 3: Color-only change
                if bg_color_changed and not has_outline and not box_shadow_changed and not border_width_changed:
                    desc = f"Element focus relies solely on color change (violates WCAG 1.4.1)"
                    issues_found.append((f'{code_prefix}ColorChangeOnly', desc))

                # Check 4: Single-sided box-shadow
                if box_shadow_changed and focus_box_shadow and focus_box_shadow != 'none':
                    shadow_str = re.sub(r'rgba?\([^)]+\)', '', focus_box_shadow)
                    shadow_str = re.sub(r'#[0-9a-fA-F]{3,6}', '', shadow_str)
                    shadow_values = shadow_str.strip().split()
                    if len(shadow_values) >= 2:
                        try:
                            h_offset = parse_px(shadow_values[0])
                            v_offset = parse_px(shadow_values[1])
                            if (h_offset != 0 and v_offset == 0) or (h_offset == 0 and v_offset != 0):
                                desc = f"Element uses single-sided box-shadow for focus (violates CR 5.2.4)"
                                issues_found.append((f'{code_prefix}SingleSideBoxShadow', desc))
                        except:
                            pass

                # Check 5: Outline width insufficient (AAA)
                if has_outline and focus_outline_width < 2.0:
                    desc = f"Element focus outline is {focus_outline_width:.1f}px (WCAG 2.4.11 recommends ≥2px)"
                    issues_found.append((f'{code_prefix}OutlineWidthInsufficient', desc))

                # Check 6: Contrast and transparency checks
                if not has_gradient:
                    bg_color = parse_color(elem.get('backgroundColor'))

                    if has_outline and focus_outline_color:
                        outline_color = parse_color(focus_outline_color)

                        # Check transparency
                        if outline_color['a'] < 0.5:
                            desc = f"Element focus outline is semi-transparent (alpha={outline_color['a']:.2f})"
                            issues_found.append((f'{code_prefix}TransparentOutline', desc))

                        # Check contrast
                        contrast = get_contrast_ratio(outline_color, bg_color)
                        if contrast < 3.0:
                            desc = f"Element focus outline has insufficient contrast ({contrast:.2f}:1, needs ≥3:1)"
                            issues_found.append((f'{code_prefix}FocusContrastFail', desc))

                    elif box_shadow_changed and focus_box_shadow:
                        shadow_color_match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)', focus_box_shadow)
                        if shadow_color_match:
                            shadow_color = {
                                'r': int(shadow_color_match.group(1)),
                                'g': int(shadow_color_match.group(2)),
                                'b': int(shadow_color_match.group(3)),
                                'a': float(shadow_color_match.group(4)) if shadow_color_match.group(4) else 1.0
                            }

                            # Check transparency
                            if shadow_color['a'] < 0.5:
                                desc = f"Element focus box-shadow is semi-transparent (alpha={shadow_color['a']:.2f})"
                                issues_found.append((f'{code_prefix}TransparentOutline', desc))

                            # Check contrast
                            contrast = get_contrast_ratio(shadow_color, bg_color)
                            if contrast < 3.0:
                                desc = f"Element focus box-shadow has insufficient contrast ({contrast:.2f}:1)"
                                issues_found.append((f'{code_prefix}FocusContrastFail', desc))

                # Check 7: Default browser focus (no custom styles)
                if not has_outline and not outline_is_none and not box_shadow_changed and not border_width_changed and not bg_color_changed:
                    desc = f"Element relies on default browser focus styles (inconsistent across browsers)"
                    issues_found.append((f'{warn_prefix}DefaultFocus', desc))

                # Check 8: Outline-only (screen magnifier concern)
                if has_outline and not box_shadow_changed and not border_width_changed and not bg_color_changed:
                    desc = f"Element uses outline-only focus (screen magnifier users may not see it when zoomed)"
                    issues_found.append((f'{warn_prefix}NoBorderOutline', desc))

                # Report all issues found for this element
                for error_code, violation_reason in issues_found:
                    result_type = 'warn' if error_code.startswith('Warn') else 'err'
                    result_list = results['warnings'] if result_type == 'warn' else results['errors']
                    result_list.append({
                        'err': error_code,
                        'type': result_type,
                        'cat': 'event_handlers',
                        'element': elem['tag'],
                        'xpath': elem.get('xpath', ''),
                        'html': elem.get('html', ''),  # Include HTML snippet for code display
                        'selector': element_id,
                        'metadata': {
                            'what': violation_reason,
                            'element_type': f"{elem['tag']}[tabindex='{elem.get('tabindex')}']" if elem_type == 'tabindex' else f"{elem['tag']}[event]",
                            'identifier': element_id,
                            'has_inline_handler': elem.get('hasInlineHandler', False)
                        }
                    })

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