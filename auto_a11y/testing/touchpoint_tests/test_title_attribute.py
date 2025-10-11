"""
Title Attribute touchpoint test module
Tests for proper usage of the title attribute on HTML elements.
"""

from typing import Dict, Any
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
        # Extract all title attribute data from the page
        title_data = await page.evaluate('''
            () => {
                // Simple XPath generator
                function getXPath(element) {
                    if (element.id) {
                        return `//*[@id="${element.id}"]`;
                    }
                    if (element === document.body) {
                        return '/html/body';
                    }
                    let ix = 0;
                    const siblings = element.parentNode ? element.parentNode.childNodes : [];
                    for (let i = 0; i < siblings.length; i++) {
                        const sibling = siblings[i];
                        if (sibling === element) {
                            return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                        }
                        if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                            ix++;
                        }
                    }
                }

                // Get all iframes (with or without title)
                const allIframes = Array.from(document.querySelectorAll('iframe')).map(iframe => ({
                    tagName: iframe.tagName,
                    hasTitle: iframe.hasAttribute('title'),
                    titleValue: iframe.getAttribute('title'),
                    src: iframe.getAttribute('src') || '(no src)',
                    xpath: getXPath(iframe),
                    html: iframe.outerHTML.substring(0, 200)
                }));

                // Get all elements WITH title attribute
                const elementsWithTitle = Array.from(document.querySelectorAll('[title]')).map(el => {
                    const titleValue = el.getAttribute('title');
                    const visibleText = (el.textContent || '').trim();

                    // Check if it's a form field
                    const isFormField = ['INPUT', 'SELECT', 'TEXTAREA'].includes(el.tagName);

                    // Get associated label for form fields
                    let hasLabel = false;
                    if (isFormField && el.id) {
                        hasLabel = document.querySelector(`label[for="${el.id}"]`) !== null;
                    }
                    // Check if wrapped in label
                    if (isFormField && !hasLabel) {
                        let parent = el.parentElement;
                        while (parent && parent !== document.body) {
                            if (parent.tagName === 'LABEL') {
                                hasLabel = true;
                                break;
                            }
                            parent = parent.parentElement;
                        }
                    }

                    return {
                        tagName: el.tagName,
                        titleValue: titleValue,
                        visibleText: visibleText,
                        isFormField: isFormField,
                        hasLabel: hasLabel,
                        hasAriaLabel: el.hasAttribute('aria-label'),
                        hasAriaLabelledby: el.hasAttribute('aria-labelledby'),
                        xpath: getXPath(el),
                        html: el.outerHTML.substring(0, 200)
                    };
                });

                return {
                    allIframes: allIframes,
                    elementsWithTitle: elementsWithTitle
                };
            }
        ''')

        results = {
            'applicable': True,
            'errors': [],
            'warnings': [],
            'passes': [],
            'elements_tested': 0,
            'elements_passed': 0,
            'elements_failed': 0,
            'test_name': 'title_attribute',
            'checks': []
        }

        # Check if test is applicable
        if len(title_data['elementsWithTitle']) == 0 and len(title_data['allIframes']) == 0:
            results['applicable'] = False
            results['not_applicable_reason'] = 'No elements with title attributes and no iframes found on the page'
            return results

        results['elements_tested'] = len(title_data['elementsWithTitle']) + len(title_data['allIframes'])

        # Test 1: Check iframes for missing title attributes (ErrIframeWithNoTitleAttr)
        for iframe in title_data['allIframes']:
            if not iframe['hasTitle']:
                results['errors'].append({
                    'err': 'ErrIframeWithNoTitleAttr',
                    'type': 'err',
                    'cat': 'title',
                    'element': 'iframe',
                    'xpath': iframe['xpath'],
                    'html': iframe['html'],
                    'description': 'Iframe element is missing the required title attribute',
                    'src': iframe['src']
                })
                results['elements_failed'] += 1

        # Test 2: Check all elements WITH title attributes
        for element in title_data['elementsWithTitle']:
            title_value = element['titleValue'].strip() if element['titleValue'] else ''
            tag = element['tagName'].lower()

            # ErrEmptyTitleAttr: Empty title attribute (applies to ALL elements)
            if title_value == '':
                results['errors'].append({
                    'err': 'ErrEmptyTitleAttr',
                    'type': 'err',
                    'cat': 'title',
                    'element': tag,
                    'xpath': element['xpath'],
                    'html': element['html'],
                    'description': 'Element has empty title attribute providing no information. Remove the empty title attribute entirely or provide meaningful descriptive text'
                })
                results['elements_failed'] += 1
                continue  # Skip further checks for this element

            # Handle iframes with title (already checked for missing titles above)
            if tag == 'iframe':
                results['elements_passed'] += 1

                # Check for generic/non-descriptive iframe titles
                title_lower = title_value.lower()
                generic_titles = [
                    'iframe', 'frame', 'embedded', 'embed', 'content',
                    'video', 'widget', 'player', 'media', 'box',
                    'container', 'element', 'component', 'module'
                ]

                if len(title_value) < 3:
                    results['warnings'].append({
                        'err': 'WarnVagueTitleAttribute',
                        'type': 'warn',
                        'cat': 'title',
                        'element': tag,
                        'xpath': element['xpath'],
                        'html': element['html'],
                        'description': 'Iframe title attribute should be more descriptive',
                        'titleValue': title_value
                    })
                elif title_lower in generic_titles:
                    results['warnings'].append({
                        'err': 'WarnIframeTitleNotDescriptive',
                        'type': 'warn',
                        'cat': 'title',
                        'element': tag,
                        'xpath': element['xpath'],
                        'html': element['html'],
                        'description': 'Iframe has a generic or non-descriptive title attribute',
                        'titleValue': title_value,
                        'suggestion': 'Replace with a descriptive title that explains the iframe content or purpose'
                    })
                continue

            # Handle non-iframe elements with title attributes

            # ErrTitleAsOnlyLabel: Form field with ONLY title as label (kept for backward compatibility)
            if element['isFormField'] and not element['hasLabel'] and not element['hasAriaLabel'] and not element['hasAriaLabelledby']:
                results['errors'].append({
                    'err': 'ErrTitleAsOnlyLabel',
                    'type': 'err',
                    'cat': 'title',
                    'element': tag,
                    'xpath': element['xpath'],
                    'html': element['html'],
                    'description': 'Form element is using title attribute as its only accessible label',
                    'titleValue': title_value
                })
                results['elements_failed'] += 1
                continue

            # ErrTitleAttrFound: Title attribute used - fundamentally inaccessible
            # Fails WCAG Conformance requirement 5.2.4 - not accessible to screen magnifier users
            # At high magnification, tooltip content goes off-screen and disappears when mouse moves
            results['errors'].append({
                'err': 'ErrTitleAttrFound',
                'type': 'err',
                'cat': 'title',
                'element': tag,
                'xpath': element['xpath'],
                'html': element['html'],
                'description': 'Title attribute is fundamentally inaccessible to screen magnifier users and fails WCAG Conformance 5.2.4. Use visible text or proper labels instead',
                'titleValue': title_value,
                'visibleText': element['visibleText'][:100] if element['visibleText'] else None
            })
            results['elements_failed'] += 1

        # Add check information for reporting
        results['checks'].append({
            'description': 'Title attribute usage',
            'wcag': ['2.4.1', '2.4.2', '4.1.2'],
            'total': results['elements_tested'],
            'passed': results['elements_passed'],
            'failed': results['elements_failed']
        })

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
