"""
Forms touchpoint test module
Evaluates web forms for accessibility requirements including proper labeling, structure, and contrast.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

TEST_DOCUMENTATION = {
    "testName": "Form Accessibility Analysis",
    "touchpoint": "forms",
    "description": "Evaluates web forms for accessibility requirements including proper labeling, structure, layout, and contrast.",
    "version": "1.0.0",
    "wcagCriteria": ["1.3.1", "3.3.2", "4.1.2", "1.4.3"],
    "tests": [
        {
            "id": "form-input-labels",
            "name": "Input Field Labeling",
            "description": "Verifies that all form inputs have properly associated labels.",
            "impact": "critical",
            "wcagCriteria": ["1.3.1", "3.3.2", "4.1.2"],
        },
        {
            "id": "form-placeholder-misuse",
            "name": "Placeholder Text Misuse",
            "description": "Identifies form fields that use placeholder text as a substitute for proper labels.",
            "impact": "high",
            "wcagCriteria": ["1.3.1", "3.3.2"],
        },
        {
            "id": "form-fieldset",
            "name": "Fieldset and Legend",
            "description": "Checks that radio buttons and checkboxes are properly grouped.",
            "impact": "medium",
            "wcagCriteria": ["1.3.1"],
        },
        {
            "id": "form-required",
            "name": "Required Field Indication",
            "description": "Verifies that required fields are properly indicated.",
            "impact": "medium",
            "wcagCriteria": ["3.3.2"],
        },
    ]
}

async def test_forms(page) -> Dict[str, Any]:
    """
    Test forms for accessibility requirements
    
    Args:
        page: Pyppeteer page object
        
    Returns:
        Dictionary containing test results with errors and warnings
    """
    try:
        # Execute JavaScript to analyze forms
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
                    test_name: 'forms',
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
                
                // Get all form inputs
                const inputs = Array.from(document.querySelectorAll('input:not([type="hidden"]), select, textarea'));
                const radioButtons = Array.from(document.querySelectorAll('input[type="radio"]'));
                const checkboxes = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                
                if (inputs.length === 0) {
                    results.applicable = false;
                    results.not_applicable_reason = 'No form inputs found on the page';
                    return results;
                }
                
                results.elements_tested = inputs.length;
                
                // Check each input for labels
                inputs.forEach(input => {
                    const inputType = input.type || 'text';
                    const inputName = input.name || '';
                    const inputId = input.id || '';
                    
                    // Skip submit/reset/button inputs as they don't need labels
                    if (['submit', 'reset', 'button'].includes(inputType)) {
                        results.elements_passed++;
                        return;
                    }
                    
                    // Check for associated label
                    let hasLabel = false;
                    let labelText = '';
                    
                    // Method 1: Check for label with for attribute
                    if (inputId) {
                        const label = document.querySelector(`label[for="${inputId}"]`);
                        if (label) {
                            hasLabel = true;
                            labelText = label.textContent.trim();
                        }
                    }
                    
                    // Method 2: Check if input is inside a label
                    if (!hasLabel) {
                        const parentLabel = input.closest('label');
                        if (parentLabel) {
                            hasLabel = true;
                            labelText = parentLabel.textContent.trim();
                        }
                    }
                    
                    // Method 3: Check for aria-label or aria-labelledby
                    const ariaLabel = input.getAttribute('aria-label');
                    const ariaLabelledby = input.getAttribute('aria-labelledby');
                    
                    if (ariaLabel) {
                        hasLabel = true;
                        labelText = ariaLabel;
                    } else if (ariaLabelledby) {
                        const labelElement = document.getElementById(ariaLabelledby);
                        if (labelElement) {
                            hasLabel = true;
                            labelText = labelElement.textContent.trim();
                        }
                    }
                    
                    // Check for placeholder misuse
                    const placeholder = input.getAttribute('placeholder');
                    const hasPlaceholder = placeholder && placeholder.trim().length > 0;
                    
                    if (!hasLabel) {
                        // Check if only using placeholder
                        if (hasPlaceholder) {
                            results.errors.push({
                                err: 'ErrPlaceholderAsLabel',
                                type: 'err',
                                cat: 'forms',
                                element: input.tagName,
                                xpath: getFullXPath(input),
                                html: input.outerHTML.substring(0, 200),
                                description: `Form input relies on placeholder text instead of proper label`,
                                inputType: inputType,
                                placeholder: placeholder
                            });
                            results.elements_failed++;
                        } else {
                            results.errors.push({
                                err: 'ErrNoLabel',
                                type: 'err',
                                cat: 'forms',
                                element: input.tagName,
                                xpath: getFullXPath(input),
                                html: input.outerHTML.substring(0, 200),
                                description: 'Form input is missing a label',
                                inputType: inputType,
                                inputName: inputName
                            });
                            results.elements_failed++;
                        }
                    } else if (!labelText || labelText.trim() === '') {
                        results.errors.push({
                            err: 'ErrEmptyLabel',
                            type: 'err',
                            cat: 'forms',
                            element: input.tagName,
                            xpath: getFullXPath(input),
                            html: input.outerHTML.substring(0, 200),
                            description: 'Form label exists but is empty',
                            inputType: inputType
                        });
                        results.elements_failed++;
                    } else {
                        results.elements_passed++;
                        
                        // Check for required field indication
                        if (input.hasAttribute('required') || input.getAttribute('aria-required') === 'true') {
                            // Check if the label indicates it's required
                            if (!labelText.includes('*') && !labelText.toLowerCase().includes('required')) {
                                results.warnings.push({
                                    err: 'WarnMissingRequiredIndication',
                                    type: 'warn',
                                    cat: 'forms',
                                    element: input.tagName,
                                    xpath: getFullXPath(input),
                                    html: input.outerHTML.substring(0, 200),
                                    description: 'Required field not clearly indicated in label',
                                    label: labelText
                                });
                            }
                        }
                    }
                });
                
                // Check for fieldset/legend for radio and checkbox groups
                const radioGroups = {};
                const checkboxGroups = {};
                
                // Group radio buttons by name
                radioButtons.forEach(radio => {
                    const name = radio.name;
                    if (name) {
                        if (!radioGroups[name]) {
                            radioGroups[name] = [];
                        }
                        radioGroups[name].push(radio);
                    }
                });
                
                // Check each radio group for fieldset
                Object.entries(radioGroups).forEach(([name, radios]) => {
                    if (radios.length > 1) {
                        const firstRadio = radios[0];
                        const fieldset = firstRadio.closest('fieldset');
                        
                        if (!fieldset) {
                            results.warnings.push({
                                err: 'WarnNoFieldset',
                                type: 'warn',
                                cat: 'forms',
                                element: 'RADIO_GROUP',
                                xpath: getFullXPath(firstRadio),
                                html: firstRadio.outerHTML.substring(0, 200),
                                description: `Radio button group "${name}" should be wrapped in a fieldset with legend`,
                                groupName: name,
                                groupSize: radios.length
                            });
                        } else {
                            const legend = fieldset.querySelector('legend');
                            if (!legend || !legend.textContent.trim()) {
                                results.warnings.push({
                                    err: 'WarnNoLegend',
                                    type: 'warn',
                                    cat: 'forms',
                                    element: 'FIELDSET',
                                    xpath: getFullXPath(fieldset),
                                    html: fieldset.outerHTML.substring(0, 200),
                                    description: 'Fieldset is missing a legend element',
                                    groupName: name
                                });
                            }
                        }
                    }
                });
                
                // Add check information for reporting
                results.checks.push({
                    description: 'Form input labeling',
                    wcag: ['1.3.1', '3.3.2', '4.1.2'],
                    total: inputs.length,
                    passed: results.elements_passed,
                    failed: results.elements_failed
                });
                
                if (Object.keys(radioGroups).length > 0) {
                    const groupsWithFieldset = Object.values(radioGroups).filter(radios => 
                        radios.length > 1 && radios[0].closest('fieldset')
                    ).length;
                    const totalGroups = Object.values(radioGroups).filter(radios => radios.length > 1).length;
                    
                    results.checks.push({
                        description: 'Radio button grouping',
                        wcag: ['1.3.1'],
                        total: totalGroups,
                        passed: groupsWithFieldset,
                        failed: totalGroups - groupsWithFieldset
                    });
                }
                
                return results;
            }
        ''')
        
        return results
        
    except Exception as e:
        logger.error(f"Error in test_forms: {e}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }