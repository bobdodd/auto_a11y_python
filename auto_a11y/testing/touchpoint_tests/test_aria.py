"""
ARIA touchpoint test module
Tests for proper ARIA attribute usage and accessibility.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "ARIA Accessibility Test",
    "touchpoint": "aria",
    "description": "Tests for proper ARIA attribute usage, focusing on voice control compatibility and ensuring aria-label includes visible text per WCAG 2.5.3 Label in Name.",
    "version": "1.0.0",
    "wcagCriteria": ["2.5.3"],
    "tests": [
        {
            "id": "aria-label-voice-control",
            "name": "ARIA Label Voice Control Compatibility",
            "description": "Checks if aria-label includes the visible text so voice control users can activate elements by saying the visible text.",
            "impact": "medium",
            "wcagCriteria": ["2.5.3"],
        }
    ]
}

async def test_aria(page) -> Dict[str, Any]:
    """
    Test ARIA attributes for accessibility issues

    Specifically checks for WCAG 2.5.3 Label in Name violation where
    aria-label doesn't include the visible text, preventing voice control
    users from activating the element.

    Args:
        page: Pyppeteer page object

    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze ARIA label usage
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
                    test_name: 'aria',
                    checks: []
                };

                // Helper function to safely get className as string (handles SVG elements)
                function getClassName(element) {
                    if (!element.className) return '';
                    // SVG elements have className as SVGAnimatedString object
                    return typeof element.className === 'string'
                        ? element.className
                        : (element.className.baseVal || '');
                }

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

                // Get all potentially relevant elements
                const allElements = Array.from(document.querySelectorAll('*'));

                // Track counts for each test
                let checksRun = 0;

                // Test 1: ErrAriaLabelMayNotBeFoundByVoiceControl (existing test)
                const elementsWithAriaLabel = allElements.filter(el => el.hasAttribute('aria-label'));
                checksRun += elementsWithAriaLabel.length;

                elementsWithAriaLabel.forEach(element => {
                    const ariaLabel = element.getAttribute('aria-label').trim();
                    const tag = element.tagName.toLowerCase();
                    const visibleText = element.textContent.trim();

                    if (visibleText && visibleText.length > 0) {
                        const ariaLabelLower = ariaLabel.toLowerCase();
                        const visibleTextLower = visibleText.toLowerCase();

                        if (!ariaLabelLower.includes(visibleTextLower)) {
                            results.errors.push({
                                err: 'ErrAriaLabelMayNotBeFoundByVoiceControl',
                                type: 'err',
                                cat: 'aria',
                                element: tag,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: `aria-label does not include visible text - voice control users cannot activate by saying "${visibleText}"`,
                                ariaLabel: ariaLabel,
                                visibleText: visibleText,
                                wcag: '2.5.3'
                            });
                            results.elements_failed++;
                        } else {
                            results.elements_passed++;
                        }
                    }
                });

                // Test 2: ErrAccordionWithoutARIA
                // Look for accordion patterns: elements that toggle content
                // This includes buttons with toggle functions AND divs/h3 with accordion-header class
                const accordionTriggers = allElements.filter(el => {
                    const tag = el.tagName.toLowerCase();
                    const onclick = el.getAttribute('onclick') || '';
                    const classes = getClassName(el);

                    // Pattern 1: Button elements with toggle/accordion functionality
                    const isToggleButton = tag === 'button' &&
                           (onclick.includes('toggle') || onclick.includes('Accordion') ||
                            classes.includes('accordion'));

                    // Pattern 2: Non-button elements with accordion-header class and onclick
                    const isAccordionHeader = (tag === 'div' || tag === 'h3' || tag === 'h2') &&
                           classes.includes('accordion-header') &&
                           onclick.includes('toggle');

                    return isToggleButton || isAccordionHeader;
                });

                checksRun += accordionTriggers.length;
                accordionTriggers.forEach(trigger => {
                    const hasAriaExpanded = trigger.hasAttribute('aria-expanded');

                    if (!hasAriaExpanded) {
                        results.errors.push({
                            err: 'ErrAccordionWithoutARIA',
                            type: 'err',
                            cat: 'aria',
                            element: trigger.tagName.toLowerCase(),
                            xpath: getFullXPath(trigger),
                            html: trigger.outerHTML.substring(0, 200),
                            description: 'Accordion trigger lacks aria-expanded attribute to indicate state',
                            wcag: '1.3.1, 4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 3: ErrDialogMissingRole
                // Look for dialog/modal patterns: elements with "dialog" or "modal" in class/id
                const potentialDialogs = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    const id = (el.id || '').toLowerCase();
                    return (classes.includes('dialog') || classes.includes('modal') ||
                            id.includes('dialog') || id.includes('modal')) &&
                           el.hasAttribute('aria-labelledby');
                });

                checksRun += potentialDialogs.length;
                potentialDialogs.forEach(dialog => {
                    const role = dialog.getAttribute('role');

                    if (!role || (role !== 'dialog' && role !== 'alertdialog')) {
                        results.errors.push({
                            err: 'ErrDialogMissingRole',
                            type: 'err',
                            cat: 'aria',
                            element: dialog.tagName.toLowerCase(),
                            xpath: getFullXPath(dialog),
                            html: dialog.outerHTML.substring(0, 200),
                            description: 'Dialog element lacks role="dialog" or role="alertdialog"',
                            wcag: '4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 4: ErrMenuWithoutARIA
                // Look for menu patterns: elements with "menubar" or containers with menu items
                const potentialMenus = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    const hasMenubarClass = classes.includes('menubar');
                    const hasMenuClass = classes.split(' ').includes('menu') && !classes.includes('menu-');
                    return (hasMenubarClass || hasMenuClass) && el.tagName.toLowerCase() === 'div';
                });

                checksRun += potentialMenus.length;
                potentialMenus.forEach(menu => {
                    const role = menu.getAttribute('role');
                    const classes = getClassName(menu).toLowerCase();
                    const hasMenuItems = menu.querySelectorAll('[class*="menu-item"]').length > 0;

                    // Only check if it has menu items (it's an actual menu pattern)
                    if (hasMenuItems) {
                        const expectedRoles = ['menubar', 'menu'];
                        if (!role || !expectedRoles.includes(role)) {
                            results.errors.push({
                                err: 'ErrMenuWithoutARIA',
                                type: 'err',
                                cat: 'aria',
                                element: menu.tagName.toLowerCase(),
                                xpath: getFullXPath(menu),
                                html: menu.outerHTML.substring(0, 200),
                                description: 'Menu pattern lacks proper ARIA attributes (role="menubar" or role="menu")',
                                wcag: '4.1.2'
                            });
                            results.elements_failed++;
                        } else {
                            results.elements_passed++;
                        }
                    }
                });

                // Test 5: ErrInteractiveElementIssue
                // Look for divs/spans with onclick but no role
                const interactiveNonSemantics = allElements.filter(el => {
                    const tag = el.tagName.toLowerCase();
                    return (tag === 'div' || tag === 'span' || tag === 'img') &&
                           (el.hasAttribute('onclick') || el.hasAttribute('ng-click') || el.hasAttribute('@click'));
                });

                checksRun += interactiveNonSemantics.length;
                interactiveNonSemantics.forEach(el => {
                    const role = el.getAttribute('role');
                    const tabindex = el.getAttribute('tabindex');

                    if (!role || parseInt(tabindex) < 0) {
                        results.errors.push({
                            err: 'ErrInteractiveElementIssue',
                            type: 'err',
                            cat: 'aria',
                            element: el.tagName.toLowerCase(),
                            xpath: getFullXPath(el),
                            html: el.outerHTML.substring(0, 200),
                            description: `${el.tagName} used as interactive element without proper role or keyboard accessibility`,
                            wcag: '2.1.1, 4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 6: ErrMissingInteractiveRole
                // Look for custom controls (checkbox, radio, switch, slider patterns) without roles
                const customControls = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    return (classes.includes('custom-checkbox') || classes.includes('custom-radio') ||
                            classes.includes('custom-switch') || classes.includes('custom-slider')) &&
                           el.hasAttribute('tabindex');
                });

                checksRun += customControls.length;
                customControls.forEach(control => {
                    const role = control.getAttribute('role');
                    const classes = getClassName(control).toLowerCase();

                    let expectedRole = '';
                    if (classes.includes('checkbox')) expectedRole = 'checkbox';
                    else if (classes.includes('radio')) expectedRole = 'radio';
                    else if (classes.includes('switch')) expectedRole = 'switch';
                    else if (classes.includes('slider')) expectedRole = 'slider';

                    if (!role || role !== expectedRole) {
                        results.errors.push({
                            err: 'ErrMissingInteractiveRole',
                            type: 'err',
                            cat: 'aria',
                            element: control.tagName.toLowerCase(),
                            xpath: getFullXPath(control),
                            html: control.outerHTML.substring(0, 200),
                            description: `Custom interactive control lacks proper role="${expectedRole}"`,
                            wcag: '4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 7: ErrTabpanelWithoutARIA
                // Look for tab patterns: buttons with "tab" class without proper ARIA
                const tabContainers = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    const children = el.querySelectorAll('[class*="tab"]');
                    return classes.includes('tabs') && children.length > 1;
                });

                checksRun += tabContainers.length;
                tabContainers.forEach(container => {
                    const role = container.getAttribute('role');
                    const tabs = container.querySelectorAll('[class*="tab"]:not([class*="panel"])');
                    let hasProperTabRoles = false;

                    tabs.forEach(tab => {
                        if (tab.getAttribute('role') === 'tab') {
                            hasProperTabRoles = true;
                        }
                    });

                    if (!role || role !== 'tablist' || !hasProperTabRoles) {
                        results.errors.push({
                            err: 'ErrTabpanelWithoutARIA',
                            type: 'err',
                            cat: 'aria',
                            element: container.tagName.toLowerCase(),
                            xpath: getFullXPath(container),
                            html: container.outerHTML.substring(0, 200),
                            description: 'Tab interface lacks proper ARIA attributes (role="tablist" on container, role="tab" on tabs)',
                            wcag: '1.3.1, 4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 8: ErrTooltipWithoutARIA
                // Look for tooltip patterns: elements with "tooltip" in class
                const tooltipTriggers = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    return classes.includes('tooltip-trigger') ||
                           (el.querySelector('[class*="tooltip"]') && !el.querySelector('[role="tooltip"]'));
                });

                checksRun += tooltipTriggers.length;
                tooltipTriggers.forEach(trigger => {
                    const hasAriaDescribedby = trigger.hasAttribute('aria-describedby');
                    const tooltip = trigger.querySelector('[class*="tooltip"]');
                    const tooltipHasRole = tooltip && tooltip.getAttribute('role') === 'tooltip';

                    if (!hasAriaDescribedby || !tooltipHasRole) {
                        results.errors.push({
                            err: 'ErrTooltipWithoutARIA',
                            type: 'err',
                            cat: 'aria',
                            element: trigger.tagName.toLowerCase(),
                            xpath: getFullXPath(trigger),
                            html: trigger.outerHTML.substring(0, 200),
                            description: 'Tooltip pattern lacks proper ARIA attributes (aria-describedby on trigger, role="tooltip" on tooltip)',
                            wcag: '4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 9: WarnSliderWithoutARIA (Warning, not error)
                const sliderElements = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    return (classes.includes('slider-track') || classes.includes('slider-container')) &&
                           !el.closest('[role="slider"]');
                });

                checksRun += sliderElements.length;
                sliderElements.forEach(slider => {
                    const hasSliderRole = slider.querySelector('[role="slider"]') !== null;

                    if (!hasSliderRole) {
                        results.warnings.push({
                            err: 'WarnSliderWithoutARIA',
                            type: 'warn',
                            cat: 'aria',
                            element: slider.tagName.toLowerCase(),
                            xpath: getFullXPath(slider),
                            html: slider.outerHTML.substring(0, 200),
                            description: 'Custom slider control should have role="slider" with aria-valuenow, aria-valuemin, and aria-valuemax',
                            wcag: '1.3.1, 4.1.2'
                        });
                    }
                });

                // Test 10: WarnSwitchWithoutARIA (Warning, not error)
                // Look for the main switch control element (not subparts like switch-track, switch-thumb)
                const switchElements = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    const classList = classes.split(' ');
                    // Only match elements with exactly "switch" class or "switch " (with space after)
                    // This excludes switch-track, switch-thumb, switch-label, etc.
                    return (classList.includes('switch') || classes === 'switch') &&
                           !classes.includes('switch-') &&
                           el.tagName.toLowerCase() !== 'label';
                });

                checksRun += switchElements.length;
                switchElements.forEach(switchEl => {
                    const role = switchEl.getAttribute('role');
                    const hasAriaChecked = switchEl.hasAttribute('aria-checked');

                    // Only warn if it doesn't have proper ARIA
                    if (role !== 'switch' || !hasAriaChecked) {
                        results.warnings.push({
                            err: 'WarnSwitchWithoutARIA',
                            type: 'warn',
                            cat: 'aria',
                            element: switchEl.tagName.toLowerCase(),
                            xpath: getFullXPath(switchEl),
                            html: switchEl.outerHTML.substring(0, 200),
                            description: 'Custom toggle switch should have role="switch" and aria-checked attribute',
                            wcag: '1.3.1, 4.1.2'
                        });
                    }
                });

                // Test 11: WarnTreeviewWithoutARIA (Warning, not error)
                const treeContainers = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    return classes.includes('tree') && el.tagName.toLowerCase() === 'ul';
                });

                checksRun += treeContainers.length;
                treeContainers.forEach(tree => {
                    const role = tree.getAttribute('role');
                    const hasTreeitems = tree.querySelectorAll('[class*="tree-item"]').length > 0;

                    if (hasTreeitems && role !== 'tree') {
                        results.warnings.push({
                            err: 'WarnTreeviewWithoutARIA',
                            type: 'warn',
                            cat: 'aria',
                            element: tree.tagName.toLowerCase(),
                            xpath: getFullXPath(tree),
                            html: tree.outerHTML.substring(0, 200),
                            description: 'Tree view navigation should have role="tree" with role="treeitem" on items and aria-expanded on parent nodes',
                            wcag: '1.3.1, 4.1.2'
                        });
                    }
                });

                // Test 12: ErrCarouselWithoutARIA
                // Look for carousel patterns: elements with carousel/slider classes and navigation controls
                const carousels = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    const hasCarouselClass = classes.includes('carousel') || classes.includes('slider');
                    const hasSlides = el.querySelectorAll('[class*="slide"]').length > 1 ||
                                     el.querySelectorAll('[class*="carousel-item"]').length > 1;
                    const hasControls = el.querySelectorAll('button[class*="prev"], button[class*="next"]').length > 0 ||
                                       el.querySelector('[class*="carousel-button"]') !== null;
                    return hasCarouselClass && (hasSlides || hasControls);
                });

                checksRun += carousels.length;
                carousels.forEach(carousel => {
                    const role = carousel.getAttribute('role');
                    const ariaLabel = carousel.getAttribute('aria-label');
                    const ariaLive = carousel.querySelector('[aria-live]');

                    if (!role || role !== 'region' || !ariaLabel) {
                        results.errors.push({
                            err: 'ErrCarouselWithoutARIA',
                            type: 'err',
                            cat: 'aria',
                            element: carousel.tagName.toLowerCase(),
                            xpath: getFullXPath(carousel),
                            html: carousel.outerHTML.substring(0, 200),
                            description: 'Carousel lacks proper ARIA attributes (role="region", aria-label, and aria-live for slide changes)',
                            wcag: '1.3.1, 2.1.1, 4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                // Test 13: ErrClickableWithoutKeyboard
                // Look for clickable elements without keyboard support (non-semantic clickable with no tabindex/role)
                const clickableWithoutKeyboard = allElements.filter(el => {
                    const tag = el.tagName.toLowerCase();
                    const isNonSemantic = (tag === 'div' || tag === 'span' || tag === 'p' || tag === 'img');
                    const hasClickHandler = el.hasAttribute('onclick') || el.hasAttribute('ng-click') || el.hasAttribute('@click');
                    const cursor = window.getComputedStyle(el).cursor;
                    const hasPointerCursor = cursor === 'pointer';

                    return isNonSemantic && (hasClickHandler || hasPointerCursor);
                });

                checksRun += clickableWithoutKeyboard.length;
                clickableWithoutKeyboard.forEach(el => {
                    const role = el.getAttribute('role');
                    const tabindex = el.getAttribute('tabindex');
                    const hasKeyboardHandler = el.hasAttribute('onkeydown') || el.hasAttribute('onkeypress');

                    // Missing both role and proper keyboard accessibility
                    if (!role && (!tabindex || parseInt(tabindex) < 0) && !hasKeyboardHandler) {
                        results.errors.push({
                            err: 'ErrClickableWithoutKeyboard',
                            type: 'err',
                            cat: 'aria',
                            element: el.tagName.toLowerCase(),
                            xpath: getFullXPath(el),
                            html: el.outerHTML.substring(0, 200),
                            description: 'Clickable element lacks keyboard support (needs role="button" and tabindex="0" or keyboard event handlers)',
                            wcag: '2.1.1, 4.1.2'
                        });
                        results.elements_failed++;
                    } else if (role || (tabindex && parseInt(tabindex) >= 0) || hasKeyboardHandler) {
                        results.elements_passed++;
                    }
                });

                // Test 14: ErrDropdownWithoutARIA
                // Look for dropdown/combobox patterns: select-like elements, dropdowns with class names
                const dropdowns = allElements.filter(el => {
                    const classes = getClassName(el).toLowerCase();
                    const hasDropdownClass = classes.includes('dropdown') || classes.includes('select') ||
                                            classes.includes('combobox');

                    // Exclude child elements like dropdown-menu, dropdown-item, etc.
                    const isChildElement = classes.includes('dropdown-menu') || classes.includes('dropdown-item') ||
                                          classes.includes('dropdown-content') || classes.includes('select-options');

                    const hasOptions = el.querySelectorAll('[class*="option"], [class*="item"]').length > 0;
                    const hasToggle = el.querySelector('[class*="toggle"], button') !== null;

                    return (hasDropdownClass && !isChildElement && (hasOptions || hasToggle)) && el.tagName.toLowerCase() !== 'select';
                });

                checksRun += dropdowns.length;
                dropdowns.forEach(dropdown => {
                    const role = dropdown.getAttribute('role');
                    const ariaExpanded = dropdown.hasAttribute('aria-expanded') ||
                                        dropdown.querySelector('[aria-expanded]') !== null;
                    const hasProperRole = role === 'combobox' || role === 'listbox';

                    // Check for menu pattern (button with aria-haspopup and child with role=menu)
                    const hasMenuPattern = dropdown.querySelector('[role="menu"]') !== null &&
                                          dropdown.querySelector('[aria-haspopup]') !== null;

                    // Valid if: has proper combobox/listbox role with aria-expanded, OR uses menu pattern
                    const isAccessible = (hasProperRole && ariaExpanded) || hasMenuPattern;

                    if (!isAccessible) {
                        results.errors.push({
                            err: 'ErrDropdownWithoutARIA',
                            type: 'err',
                            cat: 'aria',
                            element: dropdown.tagName.toLowerCase(),
                            xpath: getFullXPath(dropdown),
                            html: dropdown.outerHTML.substring(0, 200),
                            description: 'Custom dropdown lacks proper ARIA attributes (role="combobox/listbox" with aria-expanded, or role="menu" with aria-haspopup)',
                            wcag: '1.3.1, 4.1.2'
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                });

                results.elements_tested = checksRun;

                if (checksRun === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No ARIA-related patterns found on the page';
                }

                // Add check information for reporting
                results.checks.push({
                    description: 'ARIA patterns and attributes',
                    wcag: ['1.3.1', '2.1.1', '2.5.3', '4.1.2'],
                    total: checksRun,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });

                return results;
            }
        ''')

        return results

    except Exception as e:
        logger.error(f"Error in test_aria: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }
