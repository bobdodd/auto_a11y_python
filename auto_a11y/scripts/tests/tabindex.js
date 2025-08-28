function tabindexScrape() {

    let errorList = [];

    const elements = document.querySelectorAll('[tabindex]');
    elements.forEach(element => {

        const xpath = Elements.DOMPath.xPath(element, true);
        const tabindex = element.getAttribute('tabindex');

        if (tabindex < -1) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'tabindex',
                err: 'ErrNegativeTabIndex',
                found: tabindex,
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')     
            });
        }

        else if (tabindex > 0) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'tabindex',
                err: 'ErrPositiveTabIndex',
                found: tabindex,
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')   
            });
        }

        else {

            // we have either 0 or -1

            if (!htmlInteractiveElements.includes(element.tagName.toLowerCase())) {

                // Not an interactive HTML element
                if (!element.hasAttribute('role') && tabindex === 0) {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'tabindex',
                        err: 'ErrTabindexOfZeroOnNonInteractiveElement',
                        found: tabindex,
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')           
                    });
                }
                else if (element.hasAttribute('role')) {

                    const role = element.getAttribute('role');
                    if (!ariaWidgetRoles.toLowerCase().includes(role)) {
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'tabindex',
                            err: 'ErrTTabindexOnNonInteractiveElement',
                            found: tabindex,
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')              
                        });
                    }
                }

            }

        }

    });


    return { errors: errorList };

}