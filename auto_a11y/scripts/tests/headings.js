function headingsScrape() {

    let headingCount = 0;
    let h1Count = 0;
    let currentHeadingLevel = 0;
    let errorList = [];
    const elements = document.querySelectorAll("*");
    elements.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);

            if (element.tagName === 'H1' || element.tagName === 'H2' || element.tagName === 'H3' || element.tagName === 'H4' || element.tagName === 'H5' || element.tagName === 'H6'
                || (element.hasAttribute("role") && element.getAttribute('role').toLowerCase() == 'heading' && element.hasAttribute("aria-level") && element.getAttribute('aria-level') < 7)
            ) {
                // We know we have a valid heading level


                const hiddenElement = (element.offsetParent === null);

                if (!hiddenElement) {
                    // only inc the count if the heading is not display:none
                    ++headingCount;
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

                const res = computeTextAlternative(element);
                const trimmed = res.name.trim();

                if (element.textContent.trim() != trimmed) {
                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'heading',
                        err: 'VisibleHeadingDoesNotMatchA11yName',
                        visibleText: element.textContent,
                        a11yName: res.name,
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });
                }

                if (trimmed === "" || trimmed === null) {
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
                }

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

                let newHeadingLevel = 0;
                let hLevel = false;
                if (element.tagName === 'H1') { hLevel = true; newHeadingLevel = 1; ++h1Count }
                if (element.tagName === 'H2') { hLevel = true; newHeadingLevel = 2; }
                if (element.tagName === 'H3') { hLevel = true; newHeadingLevel = 3; }
                if (element.tagName === 'H4') { hLevel = true; newHeadingLevel = 4; }
                if (element.tagName === 'H5') { hLevel = true; newHeadingLevel = 5; }
                if (element.tagName === 'H6') { hLevel = true; newHeadingLevel = 6; }

                if (!hLevel) {
                    // Must be a role, look at aria-level
                    newHeadingLevel = element.getAttribute('aria-level');
                }

                if (newHeadingLevel > (currentHeadingLevel + 1)) {
                    // We have skipped a heading level

                    if (!hiddenElement) {

                        if (currentHeadingLevel === 0) {
                            errorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'heading',
                                err: 'ErrHeadingsDontStartWithH1',
                                firstHeadingLevel: currentHeadingLevel,
                                xpath: xpath,
                                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                                fpTempId: element.getAttribute('a11y-fpId')      
                            });
                        }
                        else {
                            errorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'heading',
                                err: 'ErrHeadingLevelsSkipped',
                                from: currentHeadingLevel,
                                to: newHeadingLevel,
                                xpath: xpath,
                                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                                fpTempId: element.getAttribute('a11y-fpId')      
                            });
                        }
                    }
                }

                currentHeadingLevel = newHeadingLevel;
            }

            else {

                if (element.hasAttribute("role") && element.getAttribute('role').toLowerCase() === 'heading' && !element.hasAttribute("aria-level")) {
                    // Has role of heading but no level defined
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'heading',
                        err: 'ErrRoleOfHeadingButNoLevelGiven',
                        element: element.tagName,
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')      
                    });

                }

                else if (element.hasAttribute("role") && element.getAttribute('role').toLowerCase() == 'heading' && element.hasAttribute("aria-level") && element.getAttribute('aria-level') > 6) {
                    // Has role of heading but invalid aria-level
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'heading',
                        err: 'ErrInvalidAriaLevel',
                        found: element.getAttribute('aria-level'),
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')     
                    });
                }

                else if (element.hasAttribute("role") && element.getAttribute('role').toLowerCase() !== 'heading' && element.hasAttribute("aria-level")) {
                    // Role defined that is not heading but an aria-level is provided
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'heading',
                        err: 'ErrFoundAriaLevelButRoleIsNotHeading',
                        level: element.getAttribute('aria-level'),
                        role: element.getAttribute('role'),
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });
                }

                else if (!element.hasAttribute("role") && element.hasAttribute("aria-level")) {
                    // No role declared but does have an aria-level
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'heading',
                        err: 'ErrFoundAriaLevelButNoRoleAppliedAtAll',
                        level:  element.getAttribute('aria-level'),
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

    if (headingCount === 0) {
        //alert('No heading levels');
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'heading',
            err: 'ErrNoHeadingsOnPage',
            fpTempId: '0'  
        });
    }
    else if (h1Count === 0) {
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'heading',
            err: 'ErrNoH1OnPage',
            fpTempId: '0'
        });
    }
    else if (h1Count > 1) {
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'heading',
            err: 'ErrMultipleH1HeadingsOnPage',
            found: h1Count,
            fpTempId: '0'
        });
    }

    ////// Would be good to test here for (searchCt === 0) and if so, 
    ////// look for input fields that might indicate they are search

    return { numHeadings: headingCount, errors: errorList };

}
