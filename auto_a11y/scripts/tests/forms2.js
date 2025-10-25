function walkDomToFindInteractiveNodes(n, nodeList) {

    if (n.nodeType == 1) {
        if (htmlInteractiveElements.includes(n.tagName.toLowerCase()) || (n.hasAttribute('role') & ariaWidgetRoles.includes(n.getAttribute('role')))) {
            nodeList.push(n);
        }

        n.childNodes.forEach(child => {
            walkDomToFindInteractiveNodes(child, nodeList);
        })
    }

    return nodeList;
}

function forms2Scrape() {

    let errorList = [];
    let passList = [];
    let checks = [];

    const elements = document.querySelectorAll('form');
    
    // Check applicability - are there any form elements?
    const allFormElements = document.querySelectorAll('input:not([type="hidden"]), select, textarea, button[type="submit"], button[type="button"], [role="textbox"], [role="combobox"], [role="checkbox"], [role="radio"]');
    
    if (elements.length === 0 && allFormElements.length === 0) {
        // No form elements on page - test is not applicable
        return {
            test_name: 'forms2',
            applicable: false,
            not_applicable_reason: 'No form elements found on page',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'form_labels',
                description: 'All form inputs have labels',
                wcag: ['1.3.1', '3.3.2'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }
    
    // Initialize check tracking
    let labelCheck = {
        id: 'form_labels',
        description: 'All form inputs have labels',
        wcag: ['1.3.1', '3.3.2'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    let formLabelCheck = {
        id: 'form_has_label',
        description: 'Forms have descriptive labels',
        wcag: ['1.3.1'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    let labelQualityCheck = {
        id: 'label_quality',
        description: 'Labels are properly associated and clear',
        wcag: ['2.4.6', '3.3.2'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    let tabindexCheck = {
        id: 'form_tabindex',
        description: 'Form fields have appropriate tabindex',
        wcag: ['2.4.3'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    let voiceControlCheck = {
        id: 'voice_control_compatibility',
        description: 'Form fields work with voice control',
        wcag: ['2.5.3'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };

    elements.forEach(element => {

        const formXpath = Elements.DOMPath.xPath(element, true);

        //////////////////////////////////////
        // Report a form on the page (Discovery - not counted in pass/fail)
        //////////////////////////////////////
        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'form',
            err: 'DiscoFormOnPage',
            xpath: formXpath,
            fpTempId: '0'
        });

        ///////////////////////////////////////
        // Form has no label
        ///////////////////////////////////////
        formLabelCheck.total++;
        if (!(element.hasAttribute('aria-label') || element.hasAttribute('aria-labelledby'))) {
            formLabelCheck.failed++;
            errorList.push({
                url: window.location.href,
                type: 'warn',
                cat: 'form',
                err: 'WarnFormHasNoLabel',
                xpath: formXpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        } else {
            formLabelCheck.passed++;
            passList.push({
                check: 'form_has_label',
                element: 'FORM',
                xpath: formXpath,
                wcag: ['1.3.1'],
                reason: 'Form has aria-label or aria-labelledby'
            });
        }

        ///////////////////////////////////////
        // Check for empty forms
        ///////////////////////////////////////
        if (element.childNodes.length === 0) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'form',
                err: 'ErrFormEmptyHasNoChildNodes',
                xpath: formXpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }
        
        // Check for forms with no interactive elements
        const interactiveNodes = walkDomToFindInteractiveNodes(element, []);
        if (element.childNodes.length > 0 && interactiveNodes.length === 0) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'form',
                err: 'ErrFormEmptyHasNoInteractiveElements',
                xpath: formXpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }

        ///////////////////////////////////////////////
        // Deal with labels and how they map to fields
        ///////////////////////////////////////////////
        const fieldsList = interactiveNodes;
        const labelsList = element.querySelectorAll('label');

        let utilizedLabels = [];
        let utilizedFields = [];
        
        // Check for orphan labels
        labelsList.forEach(label => {
            labelQualityCheck.total++;
            
            // Check for orphan labels without for attribute or contained field
            if (!label.hasAttribute('for') && !label.querySelector('input, select, textarea')) {
                labelQualityCheck.failed++;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'form',
                    err: 'ErrOrphanLabelWithNoId',
                    xpath: Elements.DOMPath.xPath(label, true),
                    fpTempId: label.getAttribute('a11y-fpId')
                });
            } else {
                // Check if label contains multiple fields (bad practice)
                const containedFields = label.querySelectorAll('input, select, textarea');
                if (containedFields.length > 1) {
                    labelQualityCheck.failed++;
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'form',
                        err: 'ErrLabelContainsMultipleFields',
                        count: containedFields.length,
                        xpath: Elements.DOMPath.xPath(label, true),
                        fpTempId: label.getAttribute('a11y-fpId')
                    });
                } else {
                    labelQualityCheck.passed++;
                }
            }
            
            // Check label text vs accessible name mismatch
            const res = computeTextAlternative(label);
            if (label.textContent.trim() !== res.name.trim() && res.name.trim() !== '') {
                labelQualityCheck.failed++;
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'form',
                    err: 'ErrLabelMismatchOfAccessibleNameAndLabelText',
                    visibleText: label.textContent.trim(),
                    accessibleName: res.name.trim(),
                    xpath: Elements.DOMPath.xPath(label, true),
                    fpTempId: label.getAttribute('a11y-fpId')
                });
            }
        });

        // Check each field for proper labeling
        fieldsList.forEach(field => {
            const fieldXpath = Elements.DOMPath.xPath(field, true);
            labelCheck.total++;
            
            // Check tabindex
            if (field.hasAttribute('tabindex')) {
                tabindexCheck.total++;
                const tabindexValue = parseInt(field.getAttribute('tabindex'));
                if (tabindexValue > 0) {
                    tabindexCheck.failed++;
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'form',
                        err: 'ErrWrongTabindexForInteractiveElement',
                        element: field.tagName,
                        value: tabindexValue,
                        xpath: fieldXpath,
                        fpTempId: field.getAttribute('a11y-fpId')
                    });
                } else {
                    tabindexCheck.passed++;
                }
            }

            // Check various labeling methods
            if (field.hasAttribute('aria-label')) {
                utilizedFields.push(field);
                
                const ariaLabel = field.getAttribute('aria-label').trim();
                
                // Check for empty aria-label
                if (ariaLabel === '') {
                    labelCheck.failed++;
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'form',
                        err: 'ErrEmptyAriaLabelOnField',
                        element: field.tagName,
                        xpath: fieldXpath,
                        fpTempId: field.getAttribute('a11y-fpId')
                    });
                } else {
                    labelCheck.passed++;
                    
                    // Check for voice control compatibility
                    voiceControlCheck.total++;
                    const visibleText = field.value || field.textContent || '';
                    if (visibleText && !ariaLabel.toLowerCase().includes(visibleText.toLowerCase().substring(0, 3))) {
                        voiceControlCheck.failed++;
                        errorList.push({
                            url: window.location.href,
                            type: 'warn',
                            cat: 'form',
                            err: 'ErrAriaLabelMayNotBeFoundByVoiceControl',
                            ariaLabel: ariaLabel,
                            visibleText: visibleText,
                            xpath: fieldXpath,
                            fpTempId: field.getAttribute('a11y-fpId')
                        });
                    } else {
                        voiceControlCheck.passed++;
                    }
                    
                    passList.push({
                        check: 'field_has_label',
                        element: field.tagName,
                        type: field.type || 'N/A',
                        xpath: fieldXpath,
                        wcag: ['1.3.1', '3.3.2'],
                        reason: 'Field has aria-label'
                    });
                }
                
                // Warn about aria-label usage (best practice is to use visible labels)
                errorList.push({
                    url: window.location.href,
                    type: 'info',
                    cat: 'form',
                    err: 'InfoFieldLabelledUsingAriaLabel',
                    xpath: fieldXpath,
                    found: ariaLabel,
                    fpTempId: field.getAttribute('a11y-fpId')
                });
            } else if (field.hasAttribute('aria-labelledby')) {
                const refIds = field.getAttribute('aria-labelledby').trim().split(/\s+/);
                
                // Check for empty aria-labelledby
                if (refIds.length === 0 || refIds[0] === '') {
                    labelCheck.failed++;
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'form',
                        err: 'ErrEmptyAriaLabelledByOnField',
                        element: field.tagName,
                        xpath: fieldXpath,
                        fpTempId: field.getAttribute('a11y-fpId')
                    });
                } else {
                    let allRefsValid = true;
                    let hasLabelElement = false;
                    
                    // Note: Multiple labels pointing to same field is now handled by
                    // the error code implementation in test_forms.py

                    // Check each reference
                    refIds.forEach(refId => {
                        const refElement = document.getElementById(refId);
                        
                        if (refElement === null) {
                            allRefsValid = false;
                            errorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'form',
                                err: 'ErrFieldAriaRefDoesNotExist',
                                xpath: fieldXpath,
                                found: refId,
                                fpTempId: field.getAttribute('a11y-fpId')
                            });
                        } else {
                            if (refElement.tagName === 'LABEL') {
                                hasLabelElement = true;
                                utilizedLabels.push(refElement);
                            }
                            // Note: Non-label elements in aria-labelledby are now caught by
                            // ErrFielLabelledBySomethingNotALabel in test_forms.py
                        }
                    });
                    
                    if (allRefsValid) {
                        utilizedFields.push(field);
                        labelCheck.passed++;
                        passList.push({
                            check: 'field_has_label',
                            element: field.tagName,
                            type: field.type || 'N/A',
                            xpath: fieldXpath,
                            wcag: ['1.3.1', '3.3.2'],
                            reason: 'Field has aria-labelledby'
                        });
                    } else {
                        labelCheck.failed++;
                    }
                }
            } else {
                // Check if field is wrapped in a label
                const parentLabel = field.closest('label');
                if (parentLabel) {
                    utilizedFields.push(field);
                    utilizedLabels.push(parentLabel);
                    labelCheck.passed++;
                    passList.push({
                        check: 'field_wrapped_in_label',
                        element: field.tagName,
                        type: field.type || 'N/A',
                        xpath: fieldXpath,
                        wcag: ['1.3.1', '3.3.2'],
                        reason: 'Field is wrapped in label element'
                    });
                } else {
                    // Check for label with for attribute
                    const labelFor = document.querySelector(`label[for="${field.id}"]`);
                    if (labelFor && field.id) {
                        utilizedFields.push(field);
                        utilizedLabels.push(labelFor);
                        labelCheck.passed++;
                        passList.push({
                            check: 'field_referenced_by_label',
                            element: field.tagName,
                            type: field.type || 'N/A',
                            xpath: fieldXpath,
                            wcag: ['1.3.1', '3.3.2'],
                            reason: 'Field is referenced by label with for attribute'
                        });
                    } else {
                        // Field has no label at all
                        labelCheck.failed++;
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'form',
                            err: 'ErrNoLabel',
                            element: field.tagName,
                            type: field.type || 'N/A',
                            xpath: fieldXpath,
                            fpTempId: field.getAttribute('a11y-fpId')
                        });
                    }
                }
            }
        });
    });

    // Add checks to results
    if (labelCheck.total > 0) {
        checks.push(labelCheck);
    }
    if (formLabelCheck.total > 0) {
        checks.push(formLabelCheck);
    }
    if (labelQualityCheck.total > 0) {
        checks.push(labelQualityCheck);
    }
    if (tabindexCheck.total > 0) {
        checks.push(tabindexCheck);
    }
    if (voiceControlCheck.total > 0) {
        checks.push(voiceControlCheck);
    }

    // Calculate totals
    const totalTested = labelCheck.total + formLabelCheck.total + labelQualityCheck.total + 
                       tabindexCheck.total + voiceControlCheck.total;
    const totalPassed = labelCheck.passed + formLabelCheck.passed + labelQualityCheck.passed + 
                       tabindexCheck.passed + voiceControlCheck.passed;
    const totalFailed = labelCheck.failed + formLabelCheck.failed + labelQualityCheck.failed + 
                       tabindexCheck.failed + voiceControlCheck.failed;

    return {
        test_name: 'forms2',
        applicable: true,
        elements_found: totalTested,
        elements_tested: totalTested,
        elements_passed: totalPassed,
        elements_failed: totalFailed,
        errors: errorList,
        passes: passList,
        checks: checks
    };
}