function headingsScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Check applicability - are there any headings?
    const allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]');
    
    if (allHeadings.length === 0) {
        return createNotApplicableResult('headings', 'No headings found on page', [
            {
                id: 'heading_hierarchy',
                description: 'Headings follow proper hierarchy',
                wcag: ['1.3.1']
            },
            {
                id: 'heading_content',
                description: 'Headings have content',
                wcag: ['2.4.6']
            }
        ]);
    }
    
    // Initialize checks
    let hierarchyCheck = initializeCheck('heading_hierarchy', 'Headings follow proper hierarchy', ['1.3.1']);
    let contentCheck = initializeCheck('heading_content', 'Headings have content', ['2.4.6']);
    let h1Check = initializeCheck('single_h1', 'Page has single H1', ['1.3.1']);
    
    let headingCount = 0;
    let h1Count = 0;
    let currentHeadingLevel = 0;
    let headingLevels = [];
    
    const elements = document.querySelectorAll("*");
    elements.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {
            const xpath = Elements.DOMPath.xPath(element, true);
            
            if (element.tagName === 'H1' || element.tagName === 'H2' || element.tagName === 'H3' || 
                element.tagName === 'H4' || element.tagName === 'H5' || element.tagName === 'H6' ||
                (element.hasAttribute("role") && element.getAttribute('role').toLowerCase() == 'heading' && 
                 element.hasAttribute("aria-level") && element.getAttribute('aria-level') < 7)) {
                
                const hiddenElement = (element.offsetParent === null);
                
                if (!hiddenElement) {
                    ++headingCount;
                    hierarchyCheck.total++;
                    contentCheck.total++;
                    
                    // Check content
                    const res = computeTextAlternative(element);
                    const trimmed = res.name.trim();
                    
                    if (trimmed === "" || trimmed === null) {
                        contentCheck.failed++;
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'heading',
                            err: 'ErrEmptyHeading',
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    } else {
                        contentCheck.passed++;
                        passList.push({
                            check: 'heading_has_content',
                            element: element.tagName,
                            text: trimmed.substring(0, 50),
                            xpath: xpath,
                            wcag: ['2.4.6'],
                            reason: 'Heading has text content'
                        });
                    }
                    
                    // Check for overly long headings
                    if (trimmed.length > 60) {
                        errorList.push({
                            url: window.location.href,
                            type: 'warn',
                            cat: 'heading',
                            err: 'WarnHeadingOver60CharsLong',
                            headingText: trimmed,
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    }
                    
                    // Track heading levels
                    let newHeadingLevel = 0;
                    if (element.tagName === 'H1') { newHeadingLevel = 1; ++h1Count; }
                    if (element.tagName === 'H2') { newHeadingLevel = 2; }
                    if (element.tagName === 'H3') { newHeadingLevel = 3; }
                    if (element.tagName === 'H4') { newHeadingLevel = 4; }
                    if (element.tagName === 'H5') { newHeadingLevel = 5; }
                    if (element.tagName === 'H6') { newHeadingLevel = 6; }
                    
                    if (newHeadingLevel === 0 && element.hasAttribute('aria-level')) {
                        newHeadingLevel = parseInt(element.getAttribute('aria-level'));
                    }
                    
                    headingLevels.push({level: newHeadingLevel, element: element, xpath: xpath});
                    
                } else {
                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'heading',
                        err: 'WarnHeadingInsideDisplayNone',
                        element: element.tagName,
                        headingText: element.textContent,
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });
                }
            }
        }
    });
    
    // Check heading hierarchy
    let lastLevel = 0;
    let hierarchyPasses = 0;
    let hierarchyFails = 0;
    
    for (let i = 0; i < headingLevels.length; i++) {
        const heading = headingLevels[i];
        
        if (lastLevel > 0 && heading.level > lastLevel + 1) {
            hierarchyFails++;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'heading',
                err: 'ErrSkippedHeadingLevel',
                skippedFrom: lastLevel,
                skippedTo: heading.level,
                xpath: heading.xpath,
                fpTempId: heading.element.getAttribute('a11y-fpId')
            });
        } else {
            hierarchyPasses++;
            passList.push({
                check: 'heading_hierarchy',
                level: heading.level,
                xpath: heading.xpath,
                wcag: ['1.3.1'],
                reason: 'Heading level follows proper hierarchy'
            });
        }
        lastLevel = heading.level;
    }
    
    hierarchyCheck.passed = hierarchyPasses;
    hierarchyCheck.failed = hierarchyFails;
    
    // Check H1 count
    h1Check.total = 1;
    if (h1Count === 1) {
        h1Check.passed = 1;
        passList.push({
            check: 'single_h1',
            wcag: ['1.3.1'],
            reason: 'Page has exactly one H1'
        });
    } else if (h1Count > 1) {
        h1Check.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'heading',
            err: 'ErrMultipleH1',
            count: h1Count,
            fpTempId: '0'
        });
    } else {
        h1Check.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'heading',
            err: 'WarnNoH1',
            fpTempId: '0'
        });
    }
    
    // Add checks to results
    checks.push(hierarchyCheck);
    checks.push(contentCheck);
    checks.push(h1Check);
    
    return createApplicableResult('headings', headingCount, 
        hierarchyCheck.passed + contentCheck.passed + h1Check.passed,
        hierarchyCheck.failed + contentCheck.failed + h1Check.failed,
        errorList, passList, checks);
}