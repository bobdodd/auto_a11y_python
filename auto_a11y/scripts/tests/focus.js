function focusScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Get all interactive elements - using a simpler, safer approach
    const interactiveElements = [];
    
    // Find standard interactive HTML elements
    const standardInteractive = document.querySelectorAll(
        'a[href], button, input:not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    // Find ARIA widget role elements
    const ariaInteractive = document.querySelectorAll(
        '[role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], ' +
        '[role="menuitem"], [role="option"], [role="switch"], [role="textbox"], [role="searchbox"], ' +
        '[role="combobox"], [role="slider"], [role="spinbutton"]'
    );
    
    // Combine both sets (avoiding duplicates)
    const seenElements = new Set();
    standardInteractive.forEach(el => {
        if (!seenElements.has(el)) {
            interactiveElements.push(el);
            seenElements.add(el);
        }
    });
    ariaInteractive.forEach(el => {
        if (!seenElements.has(el)) {
            interactiveElements.push(el);
            seenElements.add(el);
        }
    });
    
    // Check applicability - are there any interactive elements?
    if (interactiveElements.length === 0) {
        return {
            test_name: 'focus',
            applicable: false,
            not_applicable_reason: 'No interactive elements found on page',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'focus_indicators',
                description: 'Interactive elements have visible focus indicators',
                wcag: ['2.4.7'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }
    
    // Initialize check
    let focusIndicatorCheck = {
        id: 'focus_indicators',
        description: 'Interactive elements have visible focus indicators',
        wcag: ['2.4.7'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    // Check each interactive element - simplified to avoid crashes
    interactiveElements.forEach(element => {
        focusIndicatorCheck.total++;
        const xpath = Elements.DOMPath.xPath(element, true);
        
        // Get computed styles safely
        let style = null;
        try {
            style = window.getComputedStyle(element);
        } catch (e) {
            // Skip if we can't get styles
            return;
        }
        
        // Check focus outline properties
        const outlineStyle = style.getPropertyValue('outline-style') || 'none';
        const outlineWidth = style.getPropertyValue('outline-width') || '0px';
        const outlineColor = style.getPropertyValue('outline-color') || '';
        
        // Parse outline width to check if it's effectively zero
        const widthValue = parseFloat(outlineWidth);
        const hasOutline = outlineStyle !== 'none' && widthValue > 0;
        
        if (!hasOutline) {
            // Check for alternative focus indicators
            const boxShadow = style.getPropertyValue('box-shadow') || 'none';
            const border = style.getPropertyValue('border-style') || 'none';
            
            // Check if there's any visible alternative
            const hasBoxShadow = boxShadow !== 'none' && boxShadow !== '';
            const hasBorder = border !== 'none' && border !== '';
            
            if (!hasBoxShadow && !hasBorder) {
                // No visible focus indicator detected
                focusIndicatorCheck.failed++;
                
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'focus',
                    err: 'ErrNoFocusIndicator',
                    element: element.tagName,
                    outlineStyle: outlineStyle,
                    outlineWidth: outlineWidth,
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')
                });
            } else {
                // Has alternative focus indicator
                focusIndicatorCheck.passed++;
                passList.push({
                    check: 'alternative_focus_indicator',
                    element: element.tagName,
                    xpath: xpath,
                    wcag: ['2.4.7'],
                    reason: hasBoxShadow ? 'Element has box-shadow for focus' : 'Element has border for focus'
                });
            }
        } else {
            // Has outline focus indicator
            focusIndicatorCheck.passed++;
            
            // Check for transparent or effectively invisible outline
            if (outlineColor === 'transparent' || 
                outlineColor === 'rgba(0, 0, 0, 0)' || 
                outlineColor === 'rgba(255, 255, 255, 0)') {
                // Outline exists but is transparent
                focusIndicatorCheck.failed++;
                focusIndicatorCheck.passed--; // Correct the count
                
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'focus',
                    err: 'ErrTransparentFocusIndicator',
                    element: element.tagName,
                    outlineColor: outlineColor,
                    xpath: xpath,
                    fpTempId: element.getAttribute('a11y-fpId')
                });
            } else {
                // Check outline offset for warning
                const outlineOffset = style.getPropertyValue('outline-offset') || '0px';
                
                if (outlineOffset === '0px' || parseFloat(outlineOffset) < 0) {
                    // Outline may be too close or overlapping content
                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'focus',
                        err: 'WarnZeroOutlineOffset',
                        element: element.tagName,
                        outlineOffset: outlineOffset,
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });
                }
                
                passList.push({
                    check: 'visible_focus_indicator',
                    element: element.tagName,
                    xpath: xpath,
                    wcag: ['2.4.7'],
                    reason: 'Element has visible outline focus indicator'
                });
            }
        }
    });
    
    // Add check to results
    checks.push(focusIndicatorCheck);
    
    // Calculate totals
    const totalTested = focusIndicatorCheck.total;
    const totalPassed = focusIndicatorCheck.passed;
    const totalFailed = focusIndicatorCheck.failed;
    
    return {
        test_name: 'focus',
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