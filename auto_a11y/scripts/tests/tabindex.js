function tabindexScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Check applicability - are there any elements with tabindex?
    const tabindexElements = document.querySelectorAll('[tabindex]');
    
    if (tabindexElements.length === 0) {
        return createNotApplicableResult('tabindex', 'No elements with tabindex found', [
            {
                id: 'valid_tabindex',
                description: 'Tabindex values are appropriate',
                wcag: ['2.4.3']
            }
        ]);
    }
    
    // Initialize check
    let tabindexCheck = initializeCheck('valid_tabindex', 'Tabindex values are appropriate', ['2.4.3']);
    
    tabindexElements.forEach(element => {
        tabindexCheck.total++;
        const xpath = Elements.DOMPath.xPath(element, true);
        const tabindexValue = element.getAttribute('tabindex');
        const tabindexNum = parseInt(tabindexValue);
        
        if (tabindexValue === '0' || tabindexValue === '-1') {
            // Valid values
            tabindexCheck.passed++;
            passList.push({
                check: 'valid_tabindex',
                element: element.tagName,
                value: tabindexValue,
                xpath: xpath,
                wcag: ['2.4.3'],
                reason: tabindexValue === '0' ? 'Element in natural tab order' : 'Element removed from tab order'
            });
        } else if (tabindexNum > 0) {
            // Positive tabindex - usually problematic
            tabindexCheck.failed++;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'focus',
                err: 'ErrPositiveTabindex',
                element: element.tagName,
                value: tabindexValue,
                xpath: xpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        } else if (isNaN(tabindexNum)) {
            // Invalid tabindex value
            tabindexCheck.failed++;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'focus',
                err: 'ErrInvalidTabindex',
                element: element.tagName,
                value: tabindexValue,
                xpath: xpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }
    });
    
    // Add check to results
    checks.push(tabindexCheck);
    
    return createApplicableResult('tabindex', tabindexElements.length, tabindexCheck.passed, tabindexCheck.failed, errorList, passList, checks);
}