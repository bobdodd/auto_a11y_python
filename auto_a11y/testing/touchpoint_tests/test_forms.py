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
                    discovery: [],
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
                    let hasVisibleLabel = false;

                    // Method 1: Check for label with for attribute
                    if (inputId) {
                        const label = document.querySelector(`label[for="${inputId}"]`);
                        if (label) {
                            hasLabel = true;
                            hasVisibleLabel = true;
                            labelText = label.textContent.trim();
                        }
                    }

                    // Method 2: Check if input is inside a label
                    if (!hasLabel) {
                        const parentLabel = input.closest('label');
                        if (parentLabel) {
                            hasLabel = true;
                            hasVisibleLabel = true;
                            labelText = parentLabel.textContent.trim();
                        }
                    }

                    // Method 3: Check for aria-label or aria-labelledby
                    const ariaLabel = input.getAttribute('aria-label');
                    const ariaLabelledby = input.getAttribute('aria-labelledby');

                    if (ariaLabel !== null) {
                        // Check if aria-label is empty
                        const ariaLabelTrimmed = ariaLabel.trim();
                        if (ariaLabelTrimmed === '') {
                            // Empty aria-label - raise specific error
                            results.errors.push({
                                err: 'ErrEmptyAriaLabelOnField',
                                type: 'err',
                                cat: 'forms',
                                element: input.tagName,
                                xpath: getFullXPath(input),
                                html: input.outerHTML.substring(0, 200),
                                description: 'Form field has empty aria-label attribute',
                                inputType: inputType
                            });
                            results.elements_failed++;
                            return; // Skip further processing for this field
                        }
                        hasLabel = true;
                        labelText = ariaLabelTrimmed;
                    } else if (ariaLabelledby !== null) {
                        // Check if aria-labelledby is empty
                        const ariaLabelledbyTrimmed = ariaLabelledby.trim();
                        if (ariaLabelledbyTrimmed === '') {
                            // Empty aria-labelledby - raise specific error
                            results.errors.push({
                                err: 'ErrEmptyAriaLabelledByOnField',
                                type: 'err',
                                cat: 'forms',
                                element: input.tagName,
                                xpath: getFullXPath(input),
                                html: input.outerHTML.substring(0, 200),
                                description: 'Form field has empty aria-labelledby attribute',
                                inputType: inputType
                            });
                            results.elements_failed++;
                            return; // Skip further processing for this field
                        }

                        // aria-labelledby can reference multiple IDs (space-separated)
                        const refIds = ariaLabelledbyTrimmed.split(/\s+/);
                        let labelTexts = [];

                        refIds.forEach(refId => {
                            const labelElement = document.getElementById(refId);
                            if (labelElement) {
                                hasLabel = true;
                                labelTexts.push(labelElement.textContent.trim());

                                // Error if the referenced element is not a <label> element
                                if (labelElement.tagName !== 'LABEL') {
                                    results.errors.push({
                                        err: 'ErrFielLabelledBySomethingNotALabel',
                                        type: 'err',
                                        cat: 'forms',
                                        element: input.tagName,
                                        xpath: getFullXPath(input),
                                        html: input.outerHTML.substring(0, 200),
                                        description: `Form field uses aria-labelledby to reference ${labelElement.tagName} (id="${refId}") instead of LABEL element`,
                                        inputType: inputType,
                                        referencedTag: labelElement.tagName,
                                        referencedId: refId
                                    });
                                    results.elements_failed++;
                                }
                            } else {
                                // Error: referenced element does not exist
                                results.errors.push({
                                    err: 'ErrFieldAriaRefDoesNotExist',
                                    type: 'err',
                                    cat: 'forms',
                                    element: input.tagName,
                                    xpath: getFullXPath(input),
                                    html: input.outerHTML.substring(0, 200),
                                    description: `Form field has aria-labelledby referencing non-existent ID: "${refId}"`,
                                    inputType: inputType,
                                    missingId: refId
                                });
                                results.elements_failed++;
                            }
                        });

                        if (labelTexts.length > 0) {
                            labelText = labelTexts.join(' ');
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

                        // ERROR: Check if using aria-label without visible label
                        if (ariaLabel && !hasVisibleLabel) {
                            results.errors.push({
                                err: 'ErrFieldLabelledUsingAriaLabel',
                                type: 'err',
                                cat: 'forms',
                                element: input.tagName,
                                xpath: getFullXPath(input),
                                html: input.outerHTML.substring(0, 200),
                                description: `Field uses aria-label="${ariaLabel}" without visible label`,
                                ariaLabel: ariaLabel,
                                inputType: inputType
                            });
                            results.elements_failed++;
                        }

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

                // ERROR: Check for labels with for attribute referencing non-existent fields
                const allLabels = Array.from(document.querySelectorAll('label[for]'));
                allLabels.forEach(label => {
                    const forId = label.getAttribute('for');
                    if (forId) {
                        const referencedField = document.getElementById(forId);
                        if (!referencedField) {
                            results.errors.push({
                                err: 'ErrFieldReferenceDoesNotExist',
                                type: 'err',
                                cat: 'forms',
                                element: 'LABEL',
                                xpath: getFullXPath(label),
                                html: label.outerHTML.substring(0, 200),
                                description: `Label for attribute references non-existent field ID: "${forId}"`,
                                forId: forId,
                                labelText: label.textContent.trim()
                            });
                            results.elements_failed++;
                        }
                    }
                });

                // DISCOVERY: Report all forms on the page for manual review
                const allForms = Array.from(document.querySelectorAll('form'));
                allForms.forEach(form => {
                    // Generate a content-based signature for the form
                    // This allows identifying the same form across different pages/xpaths
                    const formSignatureData = [];

                    // Include form attributes
                    const action = form.getAttribute('action') || '';
                    const method = (form.getAttribute('method') || 'get').toLowerCase();
                    formSignatureData.push(`action:${action}`);
                    formSignatureData.push(`method:${method}`);

                    // Include form field structure (type and name of each input)
                    const formFields = Array.from(form.querySelectorAll('input, select, textarea, button'))
                        .map(field => {
                            const type = field.type || field.tagName.toLowerCase();
                            const name = field.name || field.id || '';
                            return `${type}:${name}`;
                        })
                        .sort(); // Sort for consistency

                    formSignatureData.push(...formFields);

                    // Create signature string and generate simple hash (CRC-like)
                    const signatureString = formSignatureData.join('|');

                    // Simple hash function (similar to CRC concept)
                    let hash = 0;
                    for (let i = 0; i < signatureString.length; i++) {
                        const char = signatureString.charCodeAt(i);
                        hash = ((hash << 5) - hash) + char;
                        hash = hash & hash; // Convert to 32bit integer
                    }
                    const formSignature = Math.abs(hash).toString(16).padStart(8, '0');

                    // Check if form has search role or is contained within search landmark
                    const formRole = form.getAttribute('role');
                    const isSearchRole = formRole === 'search';
                    const searchContainer = form.closest('[role="search"]');
                    const isWithinSearch = searchContainer !== null && searchContainer !== form;
                    const isSearchForm = isSearchRole || isWithinSearch;

                    // Count form fields by type
                    const fieldCounts = {};
                    Array.from(form.querySelectorAll('input, select, textarea')).forEach(field => {
                        const type = field.type || field.tagName.toLowerCase();
                        fieldCounts[type] = (fieldCounts[type] || 0) + 1;
                    });

                    const fieldSummary = Object.entries(fieldCounts)
                        .map(([type, count]) => `${count} ${type}`)
                        .join(', ');

                    // Build description with search context
                    let description = `Form detected (signature: ${formSignature})`;
                    if (isSearchRole) {
                        description += ` with role="search"`;
                    } else if (isWithinSearch) {
                        description += ` contained within search landmark`;
                    }
                    description += ` with ${fieldSummary || 'no fields'} - requires manual accessibility review`;

                    results.warnings.push({
                        err: 'DiscoFormOnPage',
                        type: 'disco',
                        cat: 'forms',
                        element: 'form',
                        xpath: getFullXPath(form),
                        html: form.outerHTML.substring(0, 200),
                        description: description,
                        formSignature: formSignature,
                        formAction: action,
                        formMethod: method,
                        fieldCount: Object.values(fieldCounts).reduce((a, b) => a + b, 0),
                        fieldTypes: fieldCounts,
                        isSearchForm: isSearchForm,
                        searchContext: isSearchRole ? 'has role="search"' : (isWithinSearch ? 'within search landmark' : 'not a search form')
                    });
                });

                return results;
            }
        ''')

        # TEST INPUT FIELD FOCUS INDICATORS
        # Extract focus styles from stylesheets for text input fields
        input_styles = await page.evaluate('''
            () => {
                const inputs = [];
                const fields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="search"], input[type="tel"], input[type="url"], input[type="number"], textarea, input:not([type])');

                function getFullXPath(element) {
                    if (!element) return '';
                    function getElementIdx(el) {
                        let count = 1;
                        for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                            if (sib.nodeType === 1 && sib.tagName === el.tagName) count++;
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

                function getComputedStyleValue(element, property) {
                    try {
                        return window.getComputedStyle(element).getPropertyValue(property);
                    } catch (e) {
                        return '';
                    }
                }

                fields.forEach((field, index) => {
                    const normalStyle = window.getComputedStyle(field);

                    // Extract focus styles from stylesheets (don't actually focus!)
                    let focusOutlineStyle = null;
                    let focusOutlineWidth = null;
                    let focusOutlineColor = null;
                    let focusOutlineOffset = null;
                    let focusBorderWidth = null;
                    let focusBorderTopWidth = null;
                    let focusBorderRightWidth = null;
                    let focusBorderBottomWidth = null;
                    let focusBorderLeftWidth = null;
                    let focusBorderColor = null;
                    let focusBorderTopColor = null;
                    let focusBoxShadow = null;

                    // Check all stylesheets for :focus rules
                    const sheets = Array.from(document.styleSheets);
                    for (const sheet of sheets) {
                        try {
                            const rules = Array.from(sheet.cssRules || sheet.rules || []);
                            for (const rule of rules) {
                                if (rule.selectorText && rule.selectorText.includes(':focus')) {
                                    const selector = rule.selectorText.replace(':focus', '');
                                    try {
                                        if (field.matches(selector)) {
                                            if (rule.style.outlineStyle !== undefined && rule.style.outlineStyle !== '') {
                                                focusOutlineStyle = rule.style.outlineStyle;
                                            }
                                            if (rule.style.outlineWidth !== undefined && rule.style.outlineWidth !== '') {
                                                focusOutlineWidth = rule.style.outlineWidth;
                                            }
                                            if (rule.style.outlineColor !== undefined && rule.style.outlineColor !== '') {
                                                focusOutlineColor = rule.style.outlineColor;
                                            }
                                            if (rule.style.outlineOffset !== undefined && rule.style.outlineOffset !== '') {
                                                focusOutlineOffset = rule.style.outlineOffset;
                                            }
                                            if (rule.style.outline !== undefined && rule.style.outline !== '') {
                                                const outlineValue = rule.style.outline;
                                                if (outlineValue === 'none' || outlineValue === '0') {
                                                    focusOutlineStyle = 'none';
                                                    focusOutlineWidth = '0px';
                                                } else {
                                                    // Parse outline shorthand: "2px solid #0066cc" or "3px solid rgba(0, 102, 204, 0.3)"
                                                    // Note: Browser may return it in different orders like "rgba(...) solid 3px"
                                                    const parts = outlineValue.split(' ');

                                                    // Try to find width, style, and color from any position
                                                    for (let part of parts) {
                                                        if (part.includes('px') || part.includes('em') || part.includes('rem')) {
                                                            focusOutlineWidth = part;
                                                        } else if (['solid', 'dotted', 'dashed', 'double'].includes(part)) {
                                                            focusOutlineStyle = part;
                                                        }
                                                    }

                                                    // Everything that's not width or style is probably color (may have commas/spaces)
                                                    // Get the full color by filtering out width and style
                                                    const colorParts = parts.filter(p =>
                                                        !p.match(/^\d+(\.\d+)?(px|em|rem)$/) &&
                                                        !['solid', 'dotted', 'dashed', 'double'].includes(p)
                                                    );
                                                    if (colorParts.length > 0) {
                                                        focusOutlineColor = colorParts.join(' ');
                                                    }
                                                }
                                            }
                                            if (rule.style.borderWidth !== undefined && rule.style.borderWidth !== '') {
                                                focusBorderWidth = rule.style.borderWidth;
                                            }
                                            if (rule.style.borderTopWidth !== undefined && rule.style.borderTopWidth !== '') {
                                                focusBorderTopWidth = rule.style.borderTopWidth;
                                            }
                                            if (rule.style.borderRightWidth !== undefined && rule.style.borderRightWidth !== '') {
                                                focusBorderRightWidth = rule.style.borderRightWidth;
                                            }
                                            if (rule.style.borderBottomWidth !== undefined && rule.style.borderBottomWidth !== '') {
                                                focusBorderBottomWidth = rule.style.borderBottomWidth;
                                            }
                                            if (rule.style.borderLeftWidth !== undefined && rule.style.borderLeftWidth !== '') {
                                                focusBorderLeftWidth = rule.style.borderLeftWidth;
                                            }
                                            if (rule.style.borderColor !== undefined && rule.style.borderColor !== '') {
                                                focusBorderColor = rule.style.borderColor;
                                            }
                                            if (rule.style.borderTopColor !== undefined && rule.style.borderTopColor !== '') {
                                                focusBorderTopColor = rule.style.borderTopColor;
                                            }
                                            if (rule.style.boxShadow !== undefined && rule.style.boxShadow !== '') {
                                                focusBoxShadow = rule.style.boxShadow;
                                            }
                                            if (rule.style.border !== undefined && rule.style.border !== '') {
                                                const borderValue = rule.style.border;
                                                const parts = borderValue.split(' ');
                                                if (parts.length >= 1) focusBorderWidth = parts[0];
                                                if (parts.length >= 3) focusBorderColor = parts[2];
                                            }
                                        }
                                    } catch (e) {
                                        // Selector might not be valid
                                    }
                                }
                            }
                        } catch (e) {
                            // Cross-origin stylesheet
                        }
                    }

                    inputs.push({
                        index,
                        tag: field.tagName.toLowerCase(),
                        type: field.type || 'text',
                        id: field.id || '',
                        className: field.className || '',
                        name: field.name || '',
                        xpath: getFullXPath(field),
                        html: field.outerHTML.substring(0, 200),
                        normalOutlineStyle: normalStyle.outlineStyle,
                        normalOutlineWidth: normalStyle.outlineWidth,
                        normalOutlineColor: normalStyle.outlineColor,
                        normalBorderWidth: normalStyle.borderWidth,
                        normalBorderTopWidth: normalStyle.borderTopWidth,
                        normalBorderRightWidth: normalStyle.borderRightWidth,
                        normalBorderBottomWidth: normalStyle.borderBottomWidth,
                        normalBorderLeftWidth: normalStyle.borderLeftWidth,
                        normalBorderColor: normalStyle.borderColor,
                        normalBorderTopColor: normalStyle.borderTopColor,
                        normalBoxShadow: normalStyle.boxShadow,
                        backgroundColor: normalStyle.backgroundColor,
                        backgroundImage: normalStyle.backgroundImage,
                        focusOutlineStyle,
                        focusOutlineWidth,
                        focusOutlineColor,
                        focusOutlineOffset,
                        focusBorderWidth,
                        focusBorderTopWidth,
                        focusBorderRightWidth,
                        focusBorderBottomWidth,
                        focusBorderLeftWidth,
                        focusBorderColor,
                        focusBorderTopColor,
                        focusBoxShadow
                    });
                });

                return inputs;
            }
        ''')

        # Process input focus indicators (Python logic)
        if input_styles:
            import re

            def parse_px(value):
                if not value or value == 'auto': return 0
                try:
                    if 'em' in value:
                        return float(value.replace('em', '').replace('rem', '')) * 16
                    return float(value.replace('px', ''))
                except: return 0

            def parse_color(color_str):
                if not color_str: return {'r': 0, 'g': 0, 'b': 0, 'a': 1}
                rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
                if rgba_match:
                    return {'r': int(rgba_match.group(1)), 'g': int(rgba_match.group(2)),
                            'b': int(rgba_match.group(3)),
                            'a': float(rgba_match.group(4)) if rgba_match.group(4) else 1.0}
                return {'r': 0, 'g': 0, 'b': 0, 'a': 1}

            def get_contrast_ratio(color1, color2):
                def luminance(c):
                    def adjust(val):
                        val = val / 255.0
                        return val / 12.92 if val <= 0.03928 else ((val + 0.055) / 1.055) ** 2.4
                    return 0.2126 * adjust(c['r']) + 0.7152 * adjust(c['g']) + 0.0722 * adjust(c['b'])
                l1 = luminance(color1)
                l2 = luminance(color2)
                return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

            for field in input_styles:
                error_code = None
                violation_reason = None

                element_id = f"#{field['id']}" if field.get('id') else (
                    f".{field.get('className', '').split()[0]}" if field.get('className') and field.get('className').strip() else
                    f"[name='{field.get('name', '')}']" if field.get('name') else
                    f"{field.get('tag', 'input')}[{field.get('index', 0)}]"
                )

                has_gradient = 'gradient' in field.get('backgroundImage', '').lower()

                # Check if focus outline is explicitly disabled (outline:none or 0)
                outline_is_none = (
                    field.get('focusOutlineStyle') == 'none' or
                    field.get('focusOutlineWidth') == '0px'
                )

                normal_border_top = parse_px(field['normalBorderTopWidth'])
                normal_border_right = parse_px(field['normalBorderRightWidth'])
                normal_border_bottom = parse_px(field['normalBorderBottomWidth'])
                normal_border_left = parse_px(field['normalBorderLeftWidth'])

                focus_border_top = parse_px(field['focusBorderTopWidth'])
                focus_border_right = parse_px(field['focusBorderRightWidth'])
                focus_border_bottom = parse_px(field['focusBorderBottomWidth'])
                focus_border_left = parse_px(field['focusBorderLeftWidth'])

                max_border_change = max(
                    focus_border_top - normal_border_top,
                    focus_border_right - normal_border_right,
                    focus_border_bottom - normal_border_bottom,
                    focus_border_left - normal_border_left
                )

                normal_border_color = field['normalBorderColor'] or field['normalBorderTopColor']
                focus_border_color = field['focusBorderColor'] or field['focusBorderTopColor']
                # If focus border color is None, it means no change (use normal color)
                if focus_border_color is None:
                    focus_border_color = normal_border_color
                border_color_changed = normal_border_color != focus_border_color

                normal_box_shadow = field['normalBoxShadow']
                focus_box_shadow = field['focusBoxShadow']
                # If focus box shadow is None, it means no change (use normal shadow)
                if focus_box_shadow is None:
                    focus_box_shadow = normal_box_shadow
                box_shadow_changed = normal_box_shadow != focus_box_shadow and focus_box_shadow != 'none'

                is_single_side_shadow = False
                if box_shadow_changed and focus_box_shadow and focus_box_shadow != 'none':
                    # Parse box-shadow - browser may return: "rgb(r, g, b) h v blur spread" or "h v blur spread rgb(r, g, b)"
                    # Remove the color part entirely
                    shadow_str = re.sub(r'rgba?\([^)]+\)', '', focus_box_shadow)  # Remove rgb() or rgba()
                    shadow_str = re.sub(r'#[0-9a-fA-F]{3,6}', '', shadow_str)  # Remove hex colors
                    shadow_values = shadow_str.strip().split()
                    if len(shadow_values) >= 2:
                        try:
                            h_offset = parse_px(shadow_values[0])
                            v_offset = parse_px(shadow_values[1])
                            is_single_side_shadow = (h_offset != 0 and v_offset == 0) or (h_offset == 0 and v_offset != 0)
                        except Exception as e:
                            is_single_side_shadow = False

                has_outline = (
                    field['focusOutlineStyle'] not in ['none', 'hidden'] and
                    field['focusOutlineWidth'] != '0px' and
                    parse_px(field['focusOutlineWidth']) > 0
                )
                outline_width = parse_px(field['focusOutlineWidth']) if has_outline else 0

                # DETECTION LOGIC - Check all conditions independently
                issues_found = []

                # Check 1: Single-sided box-shadow (highest priority error)
                if is_single_side_shadow:
                    issues_found.append(('ErrInputSingleSideBoxShadow', 'Input field uses single-sided box-shadow for focus (violates CR 5.2.4)'))

                # Check 2: No visible focus indicator at all
                if outline_is_none and not border_color_changed and max_border_change <= 0 and not box_shadow_changed:
                    issues_found.append(('ErrInputNoVisibleFocus', 'Input field has no visible focus indicator (violates WCAG 2.4.7)'))

                # Check 3: Color-only change (no structural change)
                if outline_is_none and border_color_changed and max_border_change <= 0 and not box_shadow_changed:
                    issues_found.append(('ErrInputColorChangeOnly', 'Input field focus relies solely on border color change (violates WCAG 1.4.1)'))

                # Check 4: Border change too small
                if max_border_change > 0 and max_border_change < 1.0 and not has_outline and not box_shadow_changed:
                    issues_found.append(('ErrInputBorderChangeInsufficient', f'Input border thickens by only {max_border_change:.2f}px (needs ≥1px)'))

                # Check 5: Outline width too thin (AAA recommendation)
                if has_outline and outline_width < 2.0:
                    issues_found.append(('ErrInputOutlineWidthInsufficient', f'Input focus outline is {outline_width:.2f}px (WCAG 2.4.11 recommends ≥2px)'))

                # Check 6: Contrast and transparency checks
                if not has_gradient:
                    bg_color = parse_color(field['backgroundColor'])
                    if has_outline:
                        outline_color = parse_color(field['focusOutlineColor'])
                        # Check transparency
                        if outline_color['a'] < 0.5:
                            issues_found.append(('WarnInputTransparentFocus', f'Input focus outline is semi-transparent (alpha={outline_color["a"]:.2f})'))
                        # Check contrast
                        contrast = get_contrast_ratio(outline_color, bg_color)
                        if contrast < 3.0:
                            issues_found.append(('ErrInputFocusContrastFail', f'Input focus outline has insufficient contrast ({contrast:.2f}:1, needs ≥3:1)'))
                        # Check outline-only warning
                        if not border_color_changed and max_border_change <= 0 and not box_shadow_changed:
                            issues_found.append(('WarnInputNoBorderOutline', 'Input uses outline but screen magnifier users may not see comparison'))
                    elif box_shadow_changed and focus_box_shadow:
                        # Check box-shadow contrast AND transparency
                        # Try to match rgba first, then rgb
                        shadow_color_match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([0-9.]+))?\)', focus_box_shadow)
                        if shadow_color_match:
                            shadow_color = {'r': int(shadow_color_match.group(1)),
                                          'g': int(shadow_color_match.group(2)),
                                          'b': int(shadow_color_match.group(3)),
                                          'a': float(shadow_color_match.group(4)) if shadow_color_match.group(4) else 1.0}
                            # Check transparency
                            if shadow_color['a'] < 0.5:
                                issues_found.append(('WarnInputTransparentFocus', f'Input focus box-shadow is semi-transparent (alpha={shadow_color["a"]:.2f})'))
                            # Check contrast
                            contrast = get_contrast_ratio(shadow_color, bg_color)
                            if contrast < 3.0:
                                issues_found.append(('ErrInputFocusContrastFail', f'Input focus box-shadow has insufficient contrast ({contrast:.2f}:1)'))
                else:
                    # Check 7: Gradient background warning
                    issues_found.append(('WarnInputFocusGradientBackground', 'Input has gradient background - contrast cannot be automatically verified'))

                # Check 8: Default browser focus
                # Warn if NO custom focus styles are defined (relying on browser defaults)
                # has_outline=False means no custom :focus outline/border/box-shadow rules found
                if not has_outline and not outline_is_none and not border_color_changed and not box_shadow_changed:
                    issues_found.append(('WarnInputDefaultFocus', 'Input relies on default browser focus styles (inconsistent across browsers)'))

                # Report all issues found for this field
                for error_code, violation_reason in issues_found:
                    result_type = 'warn' if error_code.startswith('Warn') else 'err'
                    result_list = results['warnings'] if result_type == 'warn' else results['errors']
                    result_list.append({
                        'err': error_code,
                        'type': result_type,
                        'cat': 'forms',
                        'element': field['tag'],
                        'xpath': field.get('xpath', ''),
                        'html': field.get('html', ''),
                        'description': violation_reason,
                        'selector': element_id,
                        'metadata': {
                            'what': violation_reason,
                            'element_type': f"{field['tag']}[type='{field['type']}']",
                            'identifier': element_id
                        }
                    })

        return results
        
    except Exception as e:
        import traceback
        logger.error(f"Error in test_forms: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'error': str(e),
            'applicable': False,
            'errors': [],
            'warnings': [],
            'passes': []
        }