"""
Semantic Structure touchpoint test module
Tests HTML document structure including DOCTYPE declaration
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Semantic Structure Tests",
    "touchpoint": "semantic_structure",
    "description": "Tests HTML document semantic structure including DOCTYPE declaration and proper HTML parsing",
    "version": "1.0.0",
    "wcagCriteria": ["4.1.1"],
    "tests": [
        {
            "id": "doctype-declaration",
            "name": "DOCTYPE Declaration",
            "description": "Checks if HTML document starts with <!DOCTYPE html> declaration to prevent quirks mode rendering",
            "impact": "medium",
            "wcagCriteria": ["4.1.1"],
        }
    ]
}

async def test_semantic_structure(page) -> Dict[str, Any]:
    """
    Test HTML document semantic structure

    Checks:
    - DOCTYPE declaration presence
    - Future: Other semantic structure issues

    Args:
        page: Playwright Page object

    Returns:
        Dictionary containing test results
    """
    try:
        # Execute JavaScript to check DOCTYPE
        results = await page.evaluate('''
            () => {
                const results = {
                    applicable: true,
                    errors: [],
                    warnings: [],
                    discovery: [],
                    passes: [],
                    elements_tested: 1,
                    elements_passed: 0,
                    elements_failed: 0,
                    test_name: 'semantic_structure',
                    checks: []
                };

                // Check for DOCTYPE declaration
                const doctype = document.doctype;

                if (!doctype) {
                    // No DOCTYPE at all
                    results.errors.push({
                        err: 'ErrMissingDocumentType',
                        type: 'err',
                        cat: 'page',
                        element: 'HTML',
                        xpath: '/html',
                        html: '<html>',
                        description: 'HTML document is missing DOCTYPE declaration - browsers will render in quirks mode',
                        compatMode: document.compatMode || 'unknown',
                        recommendation: 'Add <!DOCTYPE html> as the very first line of the HTML document'
                    });
                    results.elements_failed++;
                } else if (doctype.name !== 'html' || doctype.publicId || doctype.systemId) {
                    // DOCTYPE exists but is not HTML5
                    results.errors.push({
                        err: 'ErrMissingDocumentType',
                        type: 'err',
                        cat: 'page',
                        element: 'HTML',
                        xpath: '/html',
                        html: '<!DOCTYPE ' + doctype.name + '>',
                        description: 'HTML document has incorrect DOCTYPE - should be <!DOCTYPE html> for HTML5',
                        doctypeName: doctype.name,
                        doctypePublicId: doctype.publicId || '',
                        doctypeSystemId: doctype.systemId || '',
                        compatMode: document.compatMode || 'unknown',
                        recommendation: 'Replace with <!DOCTYPE html> for HTML5 standards mode'
                    });
                    results.elements_failed++;
                } else {
                    // Correct DOCTYPE
                    results.passes.push({
                        test: 'doctype',
                        element: 'HTML',
                        description: 'Document has correct HTML5 DOCTYPE declaration',
                        compatMode: document.compatMode || 'unknown'
                    });
                    results.elements_passed++;
                }

                // Add compat mode to results for debugging
                results.compatMode = document.compatMode;

                return results;
            }
        ''')

        logger.debug(f"DOCTYPE check complete: {results['elements_tested']} tested, "
                    f"{results['elements_passed']} passed, {results['elements_failed']} failed, "
                    f"compat mode: {results.get('compatMode', 'unknown')}")

        return results

    except Exception as e:
        logger.error(f"Error in DOCTYPE check: {str(e)}", exc_info=True)
        return {
            'applicable': False,
            'errors': [],
            'warnings': [],
            'discovery': [],
            'passes': [],
            'elements_tested': 0,
            'elements_passed': 0,
            'elements_failed': 0,
            'test_name': 'semantic_structure',
            'checks': [],
            'error': str(e)
        }
