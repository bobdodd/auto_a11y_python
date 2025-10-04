"""
Title Attribute touchpoint test module
Tests for proper usage of the title attribute on HTML elements.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Title Attribute Test",
    "touchpoint": "title_attribute",
    "description": "Tests for proper usage of the title attribute on HTML elements. According to accessibility guidelines, the title attribute should primarily be used on iframe elements to provide descriptive labels. Using title attributes on other elements can create issues for screen reader users and is generally not recommended.",
    "version": "1.0.0",
    "wcagCriteria": ["2.4.1", "2.4.2", "4.1.2"],
    "tests": [
        {
            "id": "title-attribute-usage",
            "name": "Title Attribute Usage",
            "description": "Checks if title attributes are used properly (only on iframe elements)",
            "impact": "medium",
            "wcagCriteria": ["2.4.1", "2.4.2", "4.1.2"],
        }
    ]
}

async def test_title_attribute(page) -> Dict[str, Any]:
    """
    Test proper usage of title attribute - should only be used on iframes
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze title attribute usage
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
                    test_name: 'title_attribute',
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
                
                // Find all elements with title attributes
                const elementsWithTitle = Array.from(document.querySelectorAll('[title]'));
                
                if (elementsWithTitle.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No elements with title attributes found on the page';
                    return results;
                }
                
                results.elements_tested = elementsWithTitle.length;
                
                let improperUseCount = 0;
                let properUseCount = 0;
                
                elementsWithTitle.forEach(element => {
                    const titleValue = element.getAttribute('title').trim();
                    const tag = element.tagName.toLowerCase();

                    if (tag !== 'iframe') {
                        // Check if element has visible text content
                        const visibleText = (element.textContent || '').trim();
                        const hasVisibleText = visibleText.length > 0;

                        // Check if element has accessible name from other sources
                        const hasAriaLabel = element.hasAttribute('aria-label');
                        const hasAriaLabelledby = element.hasAttribute('aria-labelledby');
                        const isFormField = ['input', 'select', 'textarea'].includes(tag);

                        // Get associated label for form fields
                        let hasLabel = false;
                        if (isFormField) {
                            const id = element.id;
                            if (id) {
                                hasLabel = document.querySelector(`label[for="${id}"]`) !== null;
                            }
                            // Check if wrapped in label
                            if (!hasLabel) {
                                let parent = element.parentElement;
                                while (parent && parent !== document.body) {
                                    if (parent.tagName === 'LABEL') {
                                        hasLabel = true;
                                        break;
                                    }
                                    parent = parent.parentElement;
                                }
                            }
                        }

                        // Determine error type and severity
                        if (isFormField && !hasLabel && !hasAriaLabel && !hasAriaLabelledby) {
                            // Form field with ONLY title attribute as label - this is HIGH severity
                            improperUseCount++;
                            results.errors.push({
                                err: 'ErrTitleAsOnlyLabel',
                                type: 'err',
                                cat: 'title_attributes',
                                element: tag,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: 'Form element is using title attribute as its only accessible label',
                                titleValue: titleValue
                            });
                            results.elements_failed++;
                        } else if (hasVisibleText) {
                            // Element has visible text - check if title is redundant
                            const titleLower = titleValue.toLowerCase();
                            const textLower = visibleText.toLowerCase();

                            if (titleLower === textLower || textLower.includes(titleLower) || titleLower.includes(textLower)) {
                                // Redundant title - WARNING
                                improperUseCount++;
                                results.warnings.push({
                                    err: 'WarnRedundantTitleAttr',
                                    type: 'warn',
                                    cat: 'title_attributes',
                                    element: tag,
                                    xpath: getFullXPath(element),
                                    html: element.outerHTML.substring(0, 200),
                                    description: 'Title attribute duplicates visible text, creating inaccessible tooltip',
                                    titleValue: titleValue,
                                    visibleText: visibleText.substring(0, 100)
                                });
                                results.elements_failed++;
                            } else {
                                // Title adds different info - still problematic but less severe
                                improperUseCount++;
                                results.warnings.push({
                                    err: 'WarnTitleAttrFound',
                                    type: 'warn',
                                    cat: 'title_attributes',
                                    element: tag,
                                    xpath: getFullXPath(element),
                                    html: element.outerHTML.substring(0, 200),
                                    description: 'Title attribute has accessibility limitations',
                                    titleValue: titleValue,
                                    visibleText: visibleText.substring(0, 100)
                                });
                                results.elements_failed++;
                            }
                        } else {
                            // General case - title on element without visible text
                            improperUseCount++;
                            results.warnings.push({
                                err: 'WarnTitleAttrFound',
                                type: 'warn',
                                cat: 'title_attributes',
                                element: tag,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: 'Title attribute has accessibility limitations',
                                titleValue: titleValue
                            });
                            results.elements_failed++;
                        }
                    } else {
                        // Iframe - title is appropriate here
                        properUseCount++;
                        results.elements_passed++;

                        // Check if iframe title is descriptive
                        if (!titleValue.trim() || titleValue.trim().length < 3) {
                            results.warnings.push({
                                err: 'WarnVagueTitleAttribute',
                                type: 'warn',
                                cat: 'title_attributes',
                                element: tag,
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: 'Iframe title attribute should be more descriptive',
                                titleValue: titleValue
                            });
                        }
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Title attribute usage',
                    wcag: ['2.4.1', '2.4.2', '4.1.2'],
                    total: elementsWithTitle.length,
                    passed: properUseCount,
                    failed: improperUseCount
                });
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_title_attribute: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }