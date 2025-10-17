"""
Menus touchpoint test module
Evaluates website navigation menus and landmarks for proper semantic structure and ARIA attributes.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Navigation Menu Analysis",
    "touchpoint": "menus",
    "description": "Evaluates website navigation menus and landmarks for proper semantic structure and ARIA attributes. This test identifies navigation elements without accessible names, current page indicators, and inappropriate menu role usage.",
    "version": "1.0.0",
    "wcagCriteria": ["1.3.1", "2.4.1", "2.4.8", "4.1.2"],
    "tests": [
        {
            "id": "nav-accessible-name",
            "name": "Navigation Accessible Name",
            "description": "Checks if navigation elements have accessible names to distinguish them from each other.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.1"],
        },
        {
            "id": "duplicate-menu-names",
            "name": "Duplicate Navigation Names",
            "description": "Identifies navigation elements that share the same accessible name.",
            "impact": "medium",
            "wcagCriteria": ["2.4.1"],
        },
        {
            "id": "current-page-indicator",
            "name": "Current Page Indicator",
            "description": "Checks if navigation menus indicate the current page or section.",
            "impact": "medium",
            "wcagCriteria": ["2.4.8"],
        },
        {
            "id": "inappropriate-menu-roles",
            "name": "Inappropriate Menu Roles",
            "description": "Identifies improper use of menu roles for site navigation.",
            "impact": "high",
            "wcagCriteria": ["4.1.2"],
        }
    ]
}

async def test_menus(page) -> Dict[str, Any]:
    """
    Test proper implementation of menus and navigation
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze menus and navigation
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
                    test_name: 'menus',
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
                
                // Get accessible name following ARIA naming precedence
                function getAccessibleName(element) {
                    if (element.getAttribute('aria-labelledby')) {
                        const labelledBy = element.getAttribute('aria-labelledby')
                            .split(' ')
                            .map(id => document.getElementById(id)?.textContent || '')
                            .join(' ');
                        if (labelledBy.trim()) return labelledBy;
                    }
                    
                    if (element.getAttribute('aria-label')) {
                        return element.getAttribute('aria-label');
                    }
                    
                    if (element.getAttribute('title')) {
                        return element.getAttribute('title');
                    }
                    
                    return '';
                }
                
                // Check for invalid menu roles (should not be used for website navigation)
                // Only report on parent menu elements, not individual menuitems
                const invalidMenus = Array.from(document.querySelectorAll('[role="menu"]'));

                invalidMenus.forEach(element => {
                    results.errors.push({
                        err: 'ErrInappropriateMenuRole',
                        type: 'err',
                        cat: 'navigation',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element uses role="menu" which is inappropriate for website navigation`,
                        role: 'menu',
                        menuitemCount: element.querySelectorAll('[role="menuitem"]').length
                    });
                    results.elements_failed++;
                });

                // Check for orphaned menuitems (outside of a menu container)
                const allMenuitems = Array.from(document.querySelectorAll('[role="menuitem"]'));
                const orphanedMenuitems = allMenuitems.filter(item => {
                    // Check if this menuitem has a parent with role="menu"
                    let parent = item.parentElement;
                    while (parent) {
                        if (parent.getAttribute('role') === 'menu') {
                            return false; // Has a menu parent, not orphaned
                        }
                        parent = parent.parentElement;
                    }
                    return true; // No menu parent found, this is orphaned
                });

                orphanedMenuitems.forEach(element => {
                    results.errors.push({
                        err: 'ErrOrphanedMenuitem',
                        type: 'err',
                        cat: 'navigation',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element has role="menuitem" but is not inside a parent with role="menu"`,
                        role: 'menuitem'
                    });
                    results.elements_failed++;
                });

                const invalidMenuRoles = [...invalidMenus, ...orphanedMenuitems];
                
                // Analyze navigation elements
                const navElements = [
                    ...Array.from(document.querySelectorAll('nav')),
                    ...Array.from(document.querySelectorAll('[role="navigation"]'))
                ];
                
                if (navElements.length === 0 && invalidMenuRoles.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No navigation elements found on the page';
                    return results;
                }
                
                results.elements_tested = navElements.length + invalidMenuRoles.length;
                
                const accessibleNames = [];
                
                navElements.forEach(nav => {
                    const accessibleName = getAccessibleName(nav);
                    const items = Array.from(nav.querySelectorAll('a, button'));
                    const hasCurrentItem = items.some(item => item.hasAttribute('aria-current'));

                    accessibleNames.push({
                        name: accessibleName,
                        element: nav,
                        xpath: getFullXPath(nav),
                        html: nav.outerHTML.substring(0, 200)
                    });

                    // Check for missing accessible name
                    // Only error if multiple nav elements exist; warning if only one
                    if (!accessibleName) {
                        if (navElements.length > 1) {
                            // Multiple navigation elements - this is an error
                            results.errors.push({
                                err: 'ErrNavMissingAccessibleName',
                                type: 'err',
                                cat: 'navigation',
                                element: nav.tagName.toLowerCase(),
                                xpath: getFullXPath(nav),
                                html: nav.outerHTML.substring(0, 200),
                                description: 'Navigation element lacks accessible name to distinguish it',
                                itemCount: items.length,
                                totalNavElements: navElements.length
                            });
                            results.elements_failed++;
                        } else {
                            // Single navigation element - this is a warning
                            results.warnings.push({
                                err: 'WarnNavMissingAccessibleName',
                                type: 'warn',
                                cat: 'navigation',
                                element: nav.tagName.toLowerCase(),
                                xpath: getFullXPath(nav),
                                html: nav.outerHTML.substring(0, 200),
                                description: 'Navigation element should have an accessible name via aria-label or aria-labelledby',
                                itemCount: items.length,
                                totalNavElements: navElements.length
                            });
                        }
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for missing aria-current and visual indicators (now errors, not warnings)
                    if (items.length > 0) {
                        // Error: Missing aria-current="page" (screen reader issue - WCAG 5.2.4)
                        if (!hasCurrentItem) {
                            results.errors.push({
                                err: 'ErrNoCurrentPageIndicatorScreenReader',
                                type: 'err',
                                cat: 'navigation',
                                element: nav.tagName.toLowerCase(),
                                xpath: getFullXPath(nav),
                                html: nav.outerHTML.substring(0, 200),
                                description: 'Navigation lacks aria-current="page" indicator, forcing screen reader users through entire menu to discover current location',
                                accessibleName: accessibleName,
                                itemCount: items.length
                            });
                            results.elements_failed++;
                        }

                        // Error: Check for missing visual styling on current page link (magnification issue - WCAG 1.4.13, 2.4.8)
                        // This checks if the current page link has distinct visual styling compared to other links
                        const hasVisualIndicator = (function() {
                            // First check: do any links have common "current" class indicators?
                            if (items.some(link =>
                                link.classList.contains('current') ||
                                link.classList.contains('active') ||
                                link.classList.contains('current-page') ||
                                link.classList.contains('is-active')
                            )) {
                                return true;
                            }

                            // Second check: Compare styling between links with aria-current and those without
                            // Collect links with and without aria-current
                            const currentLinks = items.filter(link => link.hasAttribute('aria-current'));
                            const otherLinks = items.filter(link => !link.hasAttribute('aria-current'));

                            // If no current link or no other links to compare, we can't determine
                            if (currentLinks.length === 0 || otherLinks.length === 0) {
                                return false;
                            }

                            // Compare styles of first current link vs first other link
                            try {
                                const currentComputed = window.getComputedStyle(currentLinks[0]);
                                const otherComputed = window.getComputedStyle(otherLinks[0]);

                                // Check for distinct inline styles on current link
                                const inlineStyle = currentLinks[0].getAttribute('style');
                                if (inlineStyle && (
                                    inlineStyle.includes('font-weight') ||
                                    inlineStyle.includes('background') ||
                                    inlineStyle.includes('border') ||
                                    inlineStyle.includes('text-decoration')
                                )) {
                                    return true;
                                }

                                // Compare computed styles - current link should be different from others
                                // Check font weight difference
                                const currentWeight = parseInt(currentComputed.fontWeight);
                                const otherWeight = parseInt(otherComputed.fontWeight);
                                if (Math.abs(currentWeight - otherWeight) >= 200) {
                                    return true;
                                }

                                // Check text decoration difference
                                if (currentComputed.textDecoration !== otherComputed.textDecoration) {
                                    return true;
                                }

                                // Check background color difference
                                if (currentComputed.backgroundColor !== otherComputed.backgroundColor &&
                                    currentComputed.backgroundColor !== 'rgba(0, 0, 0, 0)' &&
                                    currentComputed.backgroundColor !== 'transparent') {
                                    return true;
                                }

                                // Check border difference
                                if (currentComputed.borderStyle !== otherComputed.borderStyle ||
                                    currentComputed.borderWidth !== otherComputed.borderWidth ||
                                    currentComputed.borderColor !== otherComputed.borderColor) {
                                    return true;
                                }

                                // Check color difference
                                if (currentComputed.color !== otherComputed.color) {
                                    return true;
                                }
                            } catch (e) {
                                // If we can't check styles, assume no indicator
                            }

                            return false;
                        })();

                        if (!hasVisualIndicator) {
                            results.errors.push({
                                err: 'ErrNoCurrentPageIndicatorMagnification',
                                type: 'err',
                                cat: 'navigation',
                                element: nav.tagName.toLowerCase(),
                                xpath: getFullXPath(nav),
                                html: nav.outerHTML.substring(0, 200),
                                description: 'Navigation lacks visual current page indicator, preventing screen magnifier users from knowing their location without panning',
                                accessibleName: accessibleName,
                                itemCount: items.length
                            });
                            results.elements_failed++;
                        }
                    }
                });
                
                // Check for duplicate accessible names
                // Process elements sequentially, removing used ones from consideration
                const processedIndices = new Set();

                accessibleNames.forEach((navInfo, currentIndex) => {
                    // Skip if already processed or no name
                    if (processedIndices.has(currentIndex) || !navInfo.name) {
                        return;
                    }

                    // Find all elements with the same accessible name
                    const duplicates = [];
                    accessibleNames.forEach((otherNav, otherIndex) => {
                        if (otherNav.name === navInfo.name && !processedIndices.has(otherIndex)) {
                            duplicates.push({
                                index: duplicates.length + 1,
                                html: otherNav.html,
                                xpath: otherNav.xpath,
                                name: otherNav.name,
                                originalIndex: otherIndex
                            });
                        }
                    });

                    // If duplicates found (more than one element with this name)
                    if (duplicates.length > 1) {
                        // Create ONE error for this duplicate name group
                        results.errors.push({
                            err: 'ErrDuplicateNavNames',
                            type: 'err',
                            cat: 'navigation',
                            element: 'nav',
                            xpath: duplicates[0].xpath,
                            html: duplicates[0].html,
                            description: `Found ${duplicates.length} navigation elements with the same accessible name: "${navInfo.name}"`,
                            duplicateName: navInfo.name,
                            totalCount: duplicates.length,
                            allInstances: duplicates.map(d => ({
                                index: d.index,
                                html: d.html,
                                xpath: d.xpath,
                                name: d.name
                            }))
                        });

                        // Mark all elements in this group as processed and failed
                        duplicates.forEach(d => {
                            processedIndices.add(d.originalIndex);
                        });
                        results.elements_failed += duplicates.length;
                    } else {
                        // Mark as processed (no duplicates)
                        processedIndices.add(currentIndex);
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Navigation accessibility',
                    wcag: ['1.3.1', '2.4.1'],
                    total: navElements.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed - invalidMenuRoles.length
                });
                
                if (invalidMenuRoles.length > 0) {
                    results.checks.push({
                        description: 'Inappropriate menu roles',
                        wcag: ['4.1.2'],
                        total: invalidMenuRoles.length,
                        passed: 0,
                        failed: invalidMenuRoles.length
                    });
                }
                
                const navigationsWithoutCurrent = navElements.filter(nav => {
                    const items = Array.from(nav.querySelectorAll('a, button'));
                    return items.length > 0 && !items.some(item => item.hasAttribute('aria-current'));
                }).length;
                
                if (navigationsWithoutCurrent > 0) {
                    results.checks.push({
                        description: 'Current page indicators',
                        wcag: ['2.4.8'],
                        total: navElements.length,
                        passed: navElements.length - navigationsWithoutCurrent,
                        failed: navigationsWithoutCurrent
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_menus: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }