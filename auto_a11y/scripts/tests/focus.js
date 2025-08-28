function focusScrape() {

    let errorList = [];

    let elements = document.querySelectorAll("body *");
    elements.forEach(element => {

        const xpath = Elements.DOMPath.xPath(element, true);

        const style = window.getComputedStyle(element);


        ///////////////////////////////////////////////////////////
        // Test if focus outline is none on an interactive element
        ///////////////////////////////////////////////////////////

        if (htmlInteractiveElements.includes(element.tagName.toLowerCase()) || (element.hasAttribute('role') & ariaWidgetRoles.includes(element.getAttribute('role')))) {
            // We have an interactive element

            if (style.hasOwnProperty('outline-style')) { 
                if (style['outline-style'] === 'none') {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'focus',
                        err: 'ErrOutlineIsNoneOnInteractiveElement',
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')           
                    });
                }
            }

            if (style.hasOwnProperty('outline-offset')) { 

                if (style['outline-offset'] === '0px') {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'focus',
                        err: 'ErrZeroOutlineOffset',
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')        
                    });
                }
            }
            else {
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'focus',
                    err: 'ErrNoOutlineOffsetDefined',
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')    
                });
            }

        }

    });


    return { errors: errorList };

}
