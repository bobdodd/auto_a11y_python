function titleAttrScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Check for elements with title attributes (generally problematic except for iframes)
    const elementsWithTitle = document.querySelectorAll('[title]');
    const iframes = document.querySelectorAll('iframe');
    const allElementsChecked = elementsWithTitle.length + iframes.length;
    
    // Check applicability - are there any elements to check?
    if (allElementsChecked === 0) {
        return {
            test_name: 'titleAttr',
            applicable: false,
            not_applicable_reason: 'No elements with title attributes or iframes found',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'title_attribute_usage',
                description: 'Title attributes used appropriately',
                wcag: ['2.4.6', '3.3.2'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }
    
    // Initialize checks
    let titleAttrCheck = {
        id: 'title_attribute_usage',
        description: 'Title attributes used appropriately',
        wcag: ['2.4.6', '3.3.2'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    let iframeTitleCheck = {
        id: 'iframe_titles',
        description: 'Iframes have descriptive titles',
        wcag: ['2.4.1', '4.1.2'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    // Check elements with title attributes (excluding iframes)
    elementsWithTitle.forEach(element => {
        if (element.tagName === 'IFRAME') {
            return; // Handle iframes separately
        }
        
        titleAttrCheck.total++;
        const xpath = Elements.DOMPath.xPath(element, true);
        const title = element.getAttribute('title');
        
        // Title attributes on most elements are problematic for accessibility
        // They don't work well with touch devices, screen readers inconsistently announce them,
        // and they create dependency on hover which excludes keyboard users
        titleAttrCheck.failed++;
        
        // Determine severity based on context
        let errorType = 'warn';
        let errorCode = 'WarnTitleAttrFound';
        
        // Check if element has accessible name from other sources
        const hasAriaLabel = element.hasAttribute('aria-label');
        const hasAriaLabelledby = element.hasAttribute('aria-labelledby');
        const isLabelable = ['INPUT', 'SELECT', 'TEXTAREA', 'BUTTON'].includes(element.tagName);
        
        if (isLabelable && !hasAriaLabel && !hasAriaLabelledby) {
            // More serious if title is the only labeling mechanism
            errorType = 'err';
            errorCode = 'ErrTitleAsOnlyLabel';
        }
        
        errorList.push({
            url: window.location.href,
            type: errorType,
            cat: 'titleAttr',
            err: errorCode,
            element: element.tagName.toLowerCase(),
            title: title,
            xpath: xpath,
            parentLandmark: element.getAttribute('a11y-parentLandmark'),
            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
            fpTempId: element.getAttribute('a11y-fpId')
        });
    });
    
    // Check iframes
    iframes.forEach(element => {
        iframeTitleCheck.total++;
        const xpath = Elements.DOMPath.xPath(element, true);
        
        if (!element.hasAttribute('title')) {
            // Missing title on iframe
            iframeTitleCheck.failed++;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'titleAttr',
                err: 'ErrIframeWithNoTitleAttr',
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')
            });
        } else {
            const titleValue = element.getAttribute('title').trim();
            
            if (titleValue === '') {
                // Empty title on iframe
                iframeTitleCheck.failed++;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'titleAttr',
                    err: 'ErrEmptyTitleAttr',
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')
                });
            } else {
                // Iframe has proper title - this is good!
                iframeTitleCheck.passed++;
                passList.push({
                    check: 'iframe_has_title',
                    element: 'IFRAME',
                    title: titleValue,
                    xpath: xpath,
                    wcag: ['2.4.1', '4.1.2'],
                    reason: 'Iframe has descriptive title attribute'
                });
                
                // Also check if title is descriptive
                if (titleValue.length < 3 || 
                    titleValue.toLowerCase() === 'iframe' || 
                    titleValue.toLowerCase() === 'frame') {
                    // Title exists but isn't descriptive
                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'titleAttr',
                        err: 'WarnIframeTitleNotDescriptive',
                        title: titleValue,
                        xpath: xpath,
                        fpTempId: element.getAttribute('a11y-fpId')
                    });
                }
            }
        }
    });
    
    // Add checks to results
    if (titleAttrCheck.total > 0) {
        checks.push(titleAttrCheck);
    }
    if (iframeTitleCheck.total > 0) {
        checks.push(iframeTitleCheck);
    }
    
    // Calculate totals
    const totalTested = titleAttrCheck.total + iframeTitleCheck.total;
    const totalPassed = titleAttrCheck.passed + iframeTitleCheck.passed;
    const totalFailed = titleAttrCheck.failed + iframeTitleCheck.failed;
    
    // Return new format with pass tracking
    return {
        test_name: 'titleAttr',
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