/**
 * Enhanced Forms Accessibility Test
 * Tracks passes, failures, and applicability
 */

function formsEnhancedScrape() {
    // Initialize result structure
    let result = {
        test_name: 'forms',
        test_version: '2.0',
        applicable: false,
        not_applicable_reason: null,
        elements_found: 0,
        elements_tested: 0,
        elements_passed: 0,
        elements_failed: 0,
        errors: [],
        warnings: [],
        passes: [],
        info: [],
        discovery: [],
        checks: []
    };

    // Helper function to check if element has associated label
    function hasAssociatedLabel(element) {
        // Check for explicit label
        if (element.id) {
            const label = document.querySelector(`label[for="${element.id}"]`);
            if (label && label.textContent.trim()) {
                return { type: 'explicit', label: label };
            }
        }
        
        // Check for implicit label (wrapped)
        const parentLabel = element.closest('label');
        if (parentLabel && parentLabel.textContent.trim()) {
            return { type: 'implicit', label: parentLabel };
        }
        
        // Check for aria-label
        if (element.getAttribute('aria-label')) {
            return { type: 'aria-label', label: element.getAttribute('aria-label') };
        }
        
        // Check for aria-labelledby
        if (element.getAttribute('aria-labelledby')) {
            const labelledBy = element.getAttribute('aria-labelledby');
            const labelElement = document.getElementById(labelledBy);
            if (labelElement) {
                return { type: 'aria-labelledby', label: labelElement };
            }
        }
        
        // Check for title attribute (not ideal but acceptable)
        if (element.getAttribute('title')) {
            return { type: 'title', label: element.getAttribute('title') };
        }
        
        return false;
    }

    // Find all form-related elements (excluding hidden inputs)
    const formInputs = document.querySelectorAll(`
        input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]),
        select,
        textarea
    `);
    
    const allButtons = document.querySelectorAll(`
        button,
        input[type="submit"],
        input[type="button"],
        input[type="reset"]
    `);
    
    const allForms = document.querySelectorAll('form');
    
    // Check if test is applicable
    if (formInputs.length === 0 && allButtons.length === 0) {
        result.applicable = false;
        result.not_applicable_reason = 'No form elements found on page';
        
        // Still record that we checked
        result.checks.push({
            id: 'form_labels',
            description: 'All form inputs have labels',
            wcag: ['1.3.1', '3.3.2', '4.1.2'],
            level: 'A',
            applicable: false,
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0
        });
        
        return result;
    }
    
    // Test IS applicable
    result.applicable = true;
    result.elements_found = formInputs.length + allButtons.length;
    
    // Check 1: Form Input Labels
    let labelCheck = {
        id: 'form_labels',
        description: 'All form inputs have labels',
        wcag: ['1.3.1', '3.3.2', '4.1.2'],
        level: 'A',
        applicable: formInputs.length > 0,
        elements_found: formInputs.length,
        elements_tested: 0,
        elements_passed: 0,
        elements_failed: 0
    };
    
    formInputs.forEach(element => {
        labelCheck.elements_tested++;
        result.elements_tested++;
        
        const xpath = Elements.DOMPath.xPath(element, true);
        const labelInfo = hasAssociatedLabel(element);
        
        if (labelInfo) {
            // PASS - has label
            labelCheck.elements_passed++;
            result.elements_passed++;
            
            result.passes.push({
                check_id: 'form_label',
                check_name: 'Form input has label',
                element: element.tagName.toLowerCase(),
                input_type: element.type || 'text',
                label_type: labelInfo.type,
                xpath: xpath,
                wcag: ['1.3.1', '3.3.2'],
                message: `${element.type || element.tagName} input properly labeled via ${labelInfo.type}`
            });
        } else {
            // FAIL - no label
            labelCheck.elements_failed++;
            result.elements_failed++;
            
            result.errors.push({
                err: 'forms_ErrInputMissingLabel',
                cat: 'forms',
                element: element.tagName.toLowerCase(),
                input_type: element.type || 'text',
                name: element.name || '',
                xpath: xpath,
                html: element.outerHTML.substring(0, 200),
                wcag: ['1.3.1', '3.3.2'],
                impact: 'high',
                message: `${element.type || element.tagName} input is missing a label`
            });
        }
    });
    
    if (labelCheck.applicable) {
        result.checks.push(labelCheck);
    }
    
    // Check 2: Required Fields Indication
    let requiredCheck = {
        id: 'required_fields',
        description: 'Required fields are properly indicated',
        wcag: ['3.3.2'],
        level: 'A',
        applicable: false,
        elements_found: 0,
        elements_tested: 0,
        elements_passed: 0,
        elements_failed: 0
    };
    
    const requiredInputs = document.querySelectorAll('[required], [aria-required="true"]');
    if (requiredInputs.length > 0) {
        requiredCheck.applicable = true;
        requiredCheck.elements_found = requiredInputs.length;
        
        requiredInputs.forEach(element => {
            requiredCheck.elements_tested++;
            const labelInfo = hasAssociatedLabel(element);
            
            if (labelInfo) {
                // Check if required status is indicated in label
                const labelText = labelInfo.label.textContent || labelInfo.label;
                const hasRequiredIndication = 
                    labelText.includes('*') || 
                    labelText.toLowerCase().includes('required') ||
                    element.getAttribute('aria-required') === 'true';
                
                if (hasRequiredIndication) {
                    requiredCheck.elements_passed++;
                    result.passes.push({
                        check_id: 'required_field_indication',
                        element: element.tagName.toLowerCase(),
                        xpath: Elements.DOMPath.xPath(element, true),
                        message: 'Required field is properly indicated'
                    });
                } else {
                    requiredCheck.elements_failed++;
                    result.warnings.push({
                        err: 'forms_WarnRequiredNotIndicated',
                        cat: 'forms',
                        element: element.tagName.toLowerCase(),
                        xpath: Elements.DOMPath.xPath(element, true),
                        message: 'Required field may not be clearly indicated to users'
                    });
                }
            }
        });
        
        result.checks.push(requiredCheck);
    }
    
    // Check 3: Fieldset/Legend for Radio/Checkbox Groups
    let fieldsetCheck = {
        id: 'fieldset_legend',
        description: 'Radio/checkbox groups have fieldset and legend',
        wcag: ['1.3.1', '3.3.2'],
        level: 'A',
        applicable: false,
        elements_found: 0,
        elements_tested: 0,
        elements_passed: 0,
        elements_failed: 0
    };
    
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    if (radioButtons.length > 0 || checkboxes.length > 0) {
        fieldsetCheck.applicable = true;
        
        // Group radio buttons by name
        const radioGroups = {};
        radioButtons.forEach(radio => {
            const name = radio.name;
            if (name) {
                if (!radioGroups[name]) radioGroups[name] = [];
                radioGroups[name].push(radio);
            }
        });
        
        // Check each radio group
        Object.entries(radioGroups).forEach(([name, radios]) => {
            if (radios.length > 1) {  // Only check groups with multiple options
                fieldsetCheck.elements_tested++;
                
                const inFieldset = radios[0].closest('fieldset');
                const hasLegend = inFieldset && inFieldset.querySelector('legend');
                
                if (hasLegend) {
                    fieldsetCheck.elements_passed++;
                    result.passes.push({
                        check_id: 'radio_group_fieldset',
                        group_name: name,
                        message: `Radio group "${name}" properly grouped with fieldset/legend`
                    });
                } else {
                    fieldsetCheck.elements_failed++;
                    result.warnings.push({
                        err: 'forms_WarnNoFieldset',
                        cat: 'forms',
                        group_name: name,
                        message: `Radio group "${name}" should be grouped with fieldset/legend`
                    });
                }
            }
        });
        
        result.checks.push(fieldsetCheck);
    }
    
    // Check 4: Button Text
    let buttonCheck = {
        id: 'button_text',
        description: 'Buttons have descriptive text',
        wcag: ['2.4.6', '4.1.2'],
        level: 'AA',
        applicable: allButtons.length > 0,
        elements_found: allButtons.length,
        elements_tested: 0,
        elements_passed: 0,
        elements_failed: 0
    };
    
    if (buttonCheck.applicable) {
        allButtons.forEach(button => {
            buttonCheck.elements_tested++;
            result.elements_tested++;
            
            const buttonText = button.textContent.trim() || 
                             button.value || 
                             button.getAttribute('aria-label') || 
                             button.getAttribute('title');
            
            if (buttonText && buttonText.length > 0) {
                buttonCheck.elements_passed++;
                result.elements_passed++;
                
                // Check for generic button text
                const genericTexts = ['click here', 'submit', 'button', 'ok'];
                if (genericTexts.includes(buttonText.toLowerCase())) {
                    result.warnings.push({
                        err: 'forms_WarnGenericButtonText',
                        cat: 'forms',
                        text: buttonText,
                        xpath: Elements.DOMPath.xPath(button, true),
                        message: `Button has generic text: "${buttonText}"`
                    });
                } else {
                    result.passes.push({
                        check_id: 'button_text',
                        text: buttonText,
                        message: `Button has descriptive text: "${buttonText}"`
                    });
                }
            } else {
                buttonCheck.elements_failed++;
                result.elements_failed++;
                
                result.errors.push({
                    err: 'forms_ErrNoButtonText',
                    cat: 'forms',
                    xpath: Elements.DOMPath.xPath(button, true),
                    html: button.outerHTML.substring(0, 200),
                    message: 'Button has no accessible text'
                });
            }
        });
        
        result.checks.push(buttonCheck);
    }
    
    // Discovery: Form without submit button
    allForms.forEach(form => {
        const hasSubmit = form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
        if (!hasSubmit) {
            result.discovery.push({
                err: 'forms_DiscoNoSubmitButton',
                cat: 'forms',
                xpath: Elements.DOMPath.xPath(form, true),
                message: 'Form may lack a clear submit button - manual review recommended'
            });
        }
    });
    
    // Discovery: Placeholder used as label
    const inputsWithPlaceholder = document.querySelectorAll('[placeholder]');
    inputsWithPlaceholder.forEach(element => {
        const hasLabel = hasAssociatedLabel(element);
        if (!hasLabel) {
            result.discovery.push({
                err: 'forms_DiscoPlaceholderAsLabel',
                cat: 'forms',
                placeholder: element.getAttribute('placeholder'),
                xpath: Elements.DOMPath.xPath(element, true),
                message: 'Placeholder appears to be used instead of label - manual review recommended'
            });
        }
    });
    
    // Calculate overall compliance for forms
    if (result.elements_tested > 0) {
        result.compliance_rate = (result.elements_passed / result.elements_tested) * 100;
    }
    
    return result;
}