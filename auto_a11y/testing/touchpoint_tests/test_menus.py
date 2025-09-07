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
                const invalidMenuRoles = Array.from(document.querySelectorAll('[role="menu"], [role="menuitem"]'));
                
                invalidMenuRoles.forEach(element => {
                    results.errors.push({
                        err: 'ErrInappropriateMenuRole',
                        type: 'err',
                        cat: 'menus',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element uses role="${element.getAttribute('role')}" which is inappropriate for website navigation`,
                        role: element.getAttribute('role')
                    });
                    results.elements_failed++;
                });
                
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
                    
                    accessibleNames.push(accessibleName);
                    
                    // Check for missing accessible name
                    if (!accessibleName) {
                        results.errors.push({
                            err: 'ErrNavMissingAccessibleName',
                            type: 'err',
                            cat: 'menus',
                            element: nav.tagName.toLowerCase(),
                            xpath: getFullXPath(nav),
                            html: nav.outerHTML.substring(0, 200),
                            description: 'Navigation element needs an accessible name via aria-label or aria-labelledby',
                            itemCount: items.length
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for missing aria-current (warning, not error)
                    if (!hasCurrentItem && items.length > 0) {
                        results.warnings.push({
                            err: 'WarnNoCurrentPageIndicator',
                            type: 'warn',
                            cat: 'menus',
                            element: nav.tagName.toLowerCase(),
                            xpath: getFullXPath(nav),
                            html: nav.outerHTML.substring(0, 200),
                            description: 'Navigation lacks current page indicator (aria-current attribute)',
                            accessibleName: accessibleName,
                            itemCount: items.length
                        });
                    }
                });
                
                // Check for duplicate accessible names
                const duplicateNames = accessibleNames
                    .filter(name => name) // Only non-empty names
                    .filter((name, index, arr) => arr.indexOf(name) !== index);
                
                if (duplicateNames.length > 0) {
                    const uniqueDuplicates = [...new Set(duplicateNames)];
                    uniqueDuplicates.forEach(name => {
                        results.errors.push({
                            err: 'ErrDuplicateNavNames',
                            type: 'err',
                            cat: 'menus',
                            element: 'navigation',
                            xpath: '/html',
                            html: '<multiple elements>',
                            description: `Multiple navigation elements share the same accessible name: "${name}"`,
                            duplicateName: name
                        });
                        results.elements_failed++;
                    });
                }
                
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