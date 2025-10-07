"""
Lists touchpoint test module
Evaluates the implementation and styling of HTML lists to ensure proper semantic structure.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "List Structure Analysis",
    "touchpoint": "lists",
    "description": "Evaluates the implementation and styling of HTML lists to ensure proper semantic structure for screen reader users. This test identifies improper list implementations, excessive nesting, empty lists, and custom bullet styling that may impact accessibility.",
    "version": "1.0.0",
    "wcagCriteria": ["1.3.1", "4.1.1", "2.4.10"],
    "tests": [
        {
            "id": "fake-lists",
            "name": "Fake List Detection",
            "description": "Identifies elements that visually appear as lists but don't use proper list markup (ul/ol and li elements).",
            "impact": "high",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "empty-lists",
            "name": "Empty List Detection",
            "description": "Identifies list elements (ul/ol) that contain no list items.",
            "impact": "medium",
            "wcagCriteria": ["4.1.1"],
        },
        {
            "id": "deep-nesting",
            "name": "Excessive List Nesting",
            "description": "Identifies lists with excessive nesting depth that may cause navigation difficulties.",
            "impact": "medium",
            "wcagCriteria": ["2.4.10"],
        },
        {
            "id": "custom-bullets",
            "name": "Custom Bullet Styling",
            "description": "Identifies lists with custom bullet styling that may impact screen reader announcements.",
            "impact": "low",
            "wcagCriteria": ["1.3.1"],
        }
    ]
}

async def test_lists(page) -> Dict[str, Any]:
    """
    Test proper implementation of lists and their styling
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze lists
        results = await page.evaluate(r'''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    passes: [],
                    elements_tested: 0,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'lists',
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
                
                // Calculate list nesting depth
                function calculateListDepth(element) {
                    let depth = 0;
                    let current = element;
                    
                    while (current.parentElement) {
                        if (current.parentElement.tagName.match(/^(UL|OL)$/)) {
                            depth++;
                        }
                        current = current.parentElement;
                    }
                    
                    return depth;
                }
                
                // Check for fake lists (elements styled as lists but not using ul/ol)
                const potentialFakeLists = Array.from(document.querySelectorAll('div, span, p'))
                    .filter(el => {
                        const style = window.getComputedStyle(el);
                        const text = el.textContent;
                        const html = el.innerHTML;

                        // Check various fake list patterns
                        return style.display === 'list-item' ||
                               html.includes('•') || html.includes('·') || html.includes('‣') ||
                               html.includes('◦') || html.includes('▪') || html.includes('▫') ||
                               text.match(/^\s*[-–—*]\s/) ||  // Lines starting with dash/hyphen/asterisk
                               (html.match(/<br\s*\/?>/gi) || []).length > 2 ||  // Multiple br tags
                               el.querySelector('[class*="bullet"], [class*="list"]');
                    });

                potentialFakeLists.forEach(element => {
                    const style = window.getComputedStyle(element);
                    const html = element.innerHTML;
                    const text = element.textContent;

                    // Determine what pattern makes this look like a fake list
                    let pattern = 'unknown';
                    let detectedBullets = [];

                    if (style.display === 'list-item') {
                        pattern = 'CSS list-item display';
                    } else if (html.includes('•')) {
                        pattern = 'bullet character (•)';
                        detectedBullets = text.split('•').map(item => item.trim()).filter(item => item.length > 0);
                    } else if (html.includes('·')) {
                        pattern = 'middot character (·)';
                        detectedBullets = text.split('·').map(item => item.trim()).filter(item => item.length > 0);
                    } else if (html.includes('‣')) {
                        pattern = 'triangular bullet (‣)';
                        detectedBullets = text.split('‣').map(item => item.trim()).filter(item => item.length > 0);
                    } else if (html.includes('◦') || html.includes('▪') || html.includes('▫')) {
                        pattern = 'geometric bullet characters';
                        const bullets = ['◦', '▪', '▫'];
                        for (const bullet of bullets) {
                            if (html.includes(bullet)) {
                                detectedBullets = text.split(bullet).map(item => item.trim()).filter(item => item.length > 0);
                                break;
                            }
                        }
                    } else if (text.match(/^\s*[-–—*]\s/)) {
                        pattern = 'dash or asterisk bullets';
                        detectedBullets = text.split(/\n/).map(line => line.replace(/^\s*[-–—*]\s*/, '').trim()).filter(item => item.length > 0);
                    } else if ((html.match(/<br\s*\/?>/gi) || []).length > 2) {
                        pattern = 'multiple <br> tags';
                        detectedBullets = html.split(/<br\s*\/?>/gi).map(item => item.replace(/<[^>]*>/g, '').trim()).filter(item => item.length > 0);
                    } else if (element.querySelector('[class*="bullet"], [class*="list"]')) {
                        pattern = 'class names suggesting list/bullets';
                    }

                    // Get sample items (max 5)
                    const sampleItems = detectedBullets.slice(0, 5).map((item, idx) => ({
                        index: idx + 1,
                        text: item.substring(0, 100)
                    }));

                    results.errors.push({
                        err: 'ErrFakeListImplementation',
                        type: 'err',
                        cat: 'lists',
                        element: element.tagName.toLowerCase(),
                        xpath: getFullXPath(element),
                        html: element.outerHTML.substring(0, 200),
                        description: `Element appears to be a list using ${pattern} but does not use proper list markup`,
                        pattern: pattern,
                        itemCount: detectedBullets.length,
                        sampleItems: sampleItems,
                        innerHTML: element.innerHTML.substring(0, 100)
                    });
                    results.elements_failed++;
                });
                
                // Find all proper lists
                const allLists = Array.from(document.querySelectorAll('ul, ol'));
                
                if (allLists.length === 0 && potentialFakeLists.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No lists found on the page';
                    return results;
                }
                
                results.elements_tested = allLists.length + potentialFakeLists.length;
                
                allLists.forEach(list => {
                    const items = list.querySelectorAll('li');
                    const depth = calculateListDepth(list);
                    
                    // Check for empty lists
                    if (items.length === 0) {
                        results.errors.push({
                            err: 'ErrEmptyList',
                            type: 'err',
                            cat: 'lists',
                            element: list.tagName.toLowerCase(),
                            xpath: getFullXPath(list),
                            html: list.outerHTML.substring(0, 200),
                            description: 'List element contains no list items',
                            listType: list.tagName.toLowerCase()
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                    }
                    
                    // Check for excessive nesting (more than 3 levels)
                    if (depth > 3) {
                        results.warnings.push({
                            err: 'WarnDeepListNesting',
                            type: 'warn',
                            cat: 'lists',
                            element: list.tagName.toLowerCase(),
                            xpath: getFullXPath(list),
                            html: list.outerHTML.substring(0, 200),
                            description: `List is nested ${depth} levels deep (recommended max: 3)`,
                            depth: depth
                        });
                    }
                    
                    // Check styling of list items for custom bullets
                    items.forEach(item => {
                        const style = window.getComputedStyle(item);
                        const beforePseudo = window.getComputedStyle(item, '::before');
                        
                        const hasCustomBullet = beforePseudo.getPropertyValue('content') !== 'none' &&
                                              beforePseudo.getPropertyValue('content') !== '""' &&
                                              beforePseudo.getPropertyValue('content') !== 'normal';
                        
                        const hasIconFont = beforePseudo.getPropertyValue('font-family').includes('icon') ||
                                          beforePseudo.getPropertyValue('content').match(/[^\\u0000-\\u007F]/);
                        
                        const hasImage = beforePseudo.getPropertyValue('background-image') !== 'none' ||
                                       item.querySelector('img, svg');
                        
                        if (hasCustomBullet || hasIconFont || hasImage) {
                            results.warnings.push({
                                err: 'WarnCustomBulletStyling',
                                type: 'warn',
                                cat: 'lists',
                                element: item.tagName.toLowerCase(),
                                xpath: getFullXPath(item),
                                html: item.outerHTML.substring(0, 200),
                                description: 'List item uses custom bullet styling that may affect screen reader announcements',
                                styleType: style.getPropertyValue('list-style-type')
                            });
                        }
                    });
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'List structure integrity',
                    wcag: ['1.3.1', '4.1.1'],
                    total: allLists.length + potentialFakeLists.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed + potentialFakeLists.length
                });
                
                const deepNestingCount = allLists.filter(list => calculateListDepth(list) > 3).length;
                if (deepNestingCount > 0) {
                    results.checks.push({
                        description: 'List nesting depth',
                        wcag: ['2.4.10'],
                        total: allLists.length,
                        passed: allLists.length - deepNestingCount,
                        failed: deepNestingCount
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_lists: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }