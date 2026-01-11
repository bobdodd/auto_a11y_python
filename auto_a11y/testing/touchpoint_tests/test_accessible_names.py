"""
Accessible Names touchpoint test module
Analyzes all interactive elements for proper accessible names using the W3C accessible name computation algorithm.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Accessible Names Analysis",
    "touchpoint": "accessible_names",
    "description": "Analyzes all interactive elements for proper accessible names using the W3C accessible name computation algorithm. This test ensures that elements like buttons, links, form controls, and images have appropriate text alternatives for screen reader users.",
    "version": "1.2.0",
    "wcagCriteria": ["1.1.1", "1.3.1", "2.4.4", "2.4.6", "2.4.9", "3.3.2"],
    "tests": [
        {
            "id": "accessible-names-images",
            "name": "Image Accessible Names",
            "description": "Checks whether images have appropriate alt text providing meaningful descriptions of the image content.",
            "impact": "high",
            "wcagCriteria": ["1.1.1"],
        },
        {
            "id": "accessible-names-inputs",
            "name": "Form Control Labels",
            "description": "Checks whether form controls like inputs, textareas, and selects have proper labels.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "2.4.6", "3.3.2"],
        },
        {
            "id": "accessible-names-buttons",
            "name": "Button Accessible Names",
            "description": "Checks whether buttons have clear, descriptive text that explains their purpose.",
            "impact": "high",
            "wcagCriteria": ["2.4.4", "2.4.9"],
        },
        {
            "id": "accessible-names-links",
            "name": "Link Text Quality",
            "description": "Checks whether links have descriptive text that explains their purpose or destination.",
            "impact": "high",
            "wcagCriteria": ["2.4.4", "2.4.9"],
        },
        {
            "id": "accessible-names-iframe",
            "name": "IFrame Titles",
            "description": "Checks whether iframes have title attributes to describe their purpose or content.",
            "impact": "medium",
            "wcagCriteria": ["2.4.1"],
        }
    ]
}

async def test_accessible_names(page) -> Dict[str, Any]:
    """
    Test accessible names for all visible elements, ensuring they have appropriate labels.
    Uses the W3C accessible name computation algorithm.
    
    Args:
        page: Playwright Page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze accessible names
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
                    test_name: 'accessible_names',
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
                
                // Check if element should have an accessible name
                function shouldHaveAccessibleName(element) {
                    const tag = element.tagName.toLowerCase();

                    // Check for ARIA roles that require names FIRST
                    // (takes precedence over native element behavior)
                    const role = element.getAttribute('role');
                    const requiresNameRoles = [
                        // Standalone widget roles (ARIA 1.2)
                        'button', 'checkbox', 'radio', 'switch', 'slider', 'spinbutton',
                        'textbox', 'searchbox', 'combobox', 'link',
                        'menuitem', 'menuitemcheckbox', 'menuitemradio', 'option',
                        'tab', 'treeitem',
                        // Composite widget roles that need names
                        'tabpanel', 'toolbar', 'tree', 'grid', 'listbox', 'menu',
                        'menubar', 'heading'
                    ];

                    if (role && requiresNameRoles.includes(role)) {
                        return true;
                    }

                    // Elements that can have empty accessible names (if no requiring role)
                    const canBeEmpty = ['div', 'span', 'br', 'p'];
                    if (canBeEmpty.includes(tag)) {
                        return false;
                    }

                    // Special case for anchors - only need names if they're interactive (have href)
                    if (tag === 'a') {
                        return element.hasAttribute('href');
                    }

                    // Elements that must have non-empty accessible names
                    const requiresName = [
                        'button', 'input', 'textarea', 'select', 'img',
                        'iframe', 'area', 'dialog', 'form'
                    ];

                    return requiresName.includes(tag);
                }
                
                // Accessible name computation following W3C algorithm
                function computeAccessibleName(element) {
                    // Check aria-label first
                    const ariaLabel = element.getAttribute('aria-label');
                    if (ariaLabel && ariaLabel.trim()) {
                        return ariaLabel.trim();
                    }

                    // Check aria-labelledby
                    const ariaLabelledby = element.getAttribute('aria-labelledby');
                    if (ariaLabelledby) {
                        const labelElement = document.getElementById(ariaLabelledby);
                        if (labelElement) {
                            return labelElement.textContent.trim();
                        }
                    }

                    const tag = element.tagName.toLowerCase();

                    // Handle images
                    if (tag === 'img') {
                        const alt = element.getAttribute('alt');
                        return alt !== null ? alt : '';
                    }

                    // Handle area elements (image maps)
                    if (tag === 'area') {
                        const alt = element.getAttribute('alt');
                        return alt !== null ? alt : '';
                    }

                    // Handle form controls
                    if (['input', 'textarea', 'select'].includes(tag)) {
                        // Special case: input type="image" uses alt attribute
                        if (tag === 'input' && element.getAttribute('type') === 'image') {
                            const alt = element.getAttribute('alt');
                            return alt !== null ? alt : '';
                        }

                        // Check for associated label
                        if (element.id) {
                            const label = document.querySelector(`label[for="${element.id}"]`);
                            if (label) {
                                return label.textContent.trim();
                            }
                        }

                        // Check for wrapping label
                        const parentLabel = element.closest('label');
                        if (parentLabel) {
                            const clone = parentLabel.cloneNode(true);
                            const inputInClone = clone.querySelector('input, textarea, select');
                            if (inputInClone) {
                                inputInClone.remove();
                            }
                            return clone.textContent.trim();
                        }

                        // For input type=submit/reset/button, use value
                        if (tag === 'input') {
                            const type = element.getAttribute('type');
                            if (['submit', 'reset', 'button'].includes(type)) {
                                return element.value || (type === 'submit' ? 'Submit' : type === 'reset' ? 'Reset' : '');
                            }
                        }
                    }

                    // Handle iframes
                    if (tag === 'iframe') {
                        return element.title || '';
                    }

                    // Handle buttons and links - compute name from contents
                    if (['button', 'a'].includes(tag)) {
                        // First try direct text content (for simple text links/buttons)
                        const directText = Array.from(element.childNodes)
                            .filter(node => node.nodeType === Node.TEXT_NODE)
                            .map(node => node.textContent.trim())
                            .join(' ');

                        if (directText) {
                            return directText;
                        }

                        // Check for child images with alt text
                        const img = element.querySelector('img');
                        if (img) {
                            const alt = img.getAttribute('alt');
                            if (alt !== null) {
                                return alt;
                            }
                        }

                        // Check for child SVG with title
                        const svg = element.querySelector('svg');
                        if (svg) {
                            const title = svg.querySelector('title');
                            if (title) {
                                return title.textContent.trim();
                            }
                        }

                        // Fall back to all text content (includes nested elements)
                        return element.textContent.trim();
                    }

                    // Handle title attribute as fallback
                    const title = element.title;
                    if (title && title.trim()) {
                        return title.trim();
                    }

                    return element.textContent ? element.textContent.trim() : '';
                }
                
                // Get all elements
                const elements = Array.from(document.body.getElementsByTagName('*'))
                    .filter(element => {
                        const style = window.getComputedStyle(element);
                        const isHidden = element.getAttribute('aria-hidden') === 'true' ||
                                       style.display === 'none' ||
                                       style.visibility === 'hidden';
                        return !isHidden && element.tagName.toLowerCase() !== 'script' && element.tagName.toLowerCase() !== 'style';
                    });
                    
                if (elements.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No elements found on the page';
                    return results;
                }
                
                results.elements_tested = elements.length;
                
                let elementsRequiringNames = 0;
                let elementsMissingNames = 0;
                
                elements.forEach(element => {
                    const tag = element.tagName.toLowerCase();
                    const needsName = shouldHaveAccessibleName(element);
                    
                    if (needsName) {
                        elementsRequiringNames++;
                        const accessibleName = computeAccessibleName(element);
                        
                        if (!accessibleName || accessibleName.length === 0) {
                            // Special case: img with empty alt is valid for decorative images
                            if (tag === 'img' && element.getAttribute('alt') === '') {
                                results.elements_passed++;
                                return;
                            }
                            
                            elementsMissingNames++;
                            results.errors.push({
                                err: 'ErrMissingAccessibleName',
                                type: 'err',
                                cat: 'accessible_names',
                                element: tag.toUpperCase(),
                                xpath: getFullXPath(element),
                                html: element.outerHTML.substring(0, 200),
                                description: `${tag} element is missing an accessible name`,
                                role: element.getAttribute('role')
                            });
                            results.elements_failed++;
                        } else {
                            results.elements_passed++;
                            
                            // Check for generic or poor quality names
                            const lowerName = accessibleName.toLowerCase();
                            if (['click here', 'read more', 'more', 'link', 'button', 'image'].includes(lowerName)) {
                                results.warnings.push({
                                    err: 'WarnGenericAccessibleName',
                                    type: 'warn',
                                    cat: 'accessible_names',
                                    element: tag.toUpperCase(),
                                    xpath: getFullXPath(element),
                                    html: element.outerHTML.substring(0, 200),
                                    description: `${tag} has generic accessible name: "${accessibleName}"`,
                                    accessibleName: accessibleName
                                });
                            }
                        }
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Elements with required accessible names',
                    wcag: ['1.1.1', '1.3.1', '2.4.4', '2.4.6', '2.4.9', '3.3.2'],
                    total: elementsRequiringNames,
                    passed: elementsRequiringNames - elementsMissingNames,
                    failed: elementsMissingNames
                });
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_accessible_names: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }