const cssColorProps = [

    'accent-color:',
    'background-attachment:',
    'background-blend-mode:',
    'background-clip:',
    'background-color:',
    'background-image:',
    'background-image:',
    'background-origin:',
    'background-position:',
    'background-repeat:',
    'background-size',
    'border-block-color:',
    'border-block-end-color:',
    'border-block-start-color:',
    'border-bottom-color:',
    'border-color:',
    'border-image:',
    'border-image-repeat:',
    'border-image-slice:',
    'border-image-source:',
    'border-image-width',
    'border-inline-color:',
    'border-inline-end-color:',
    'border-inline-start-color:',
    'border-right-color',
    'border-top-color:',
    'caret-color:',
    'clip-path:',
    'color:',
    'color-adjust:',
    'color-interpolation-filters:',
    'color-scheme:',
    'fill-color:',
    'fill-image:',
    'fill-opacity',
    'fill-origin:',
    'fill-position:',
    'fill-repeat:',
    'fill-rule:',
    'fill-size',
    'filter:',
    'flood-color:',
    'flood-opacity:',
    'font-palette:',
    'font-weight:',
    'forced-color-adjust:',
    'image-orientation:',
    'lighting-color:',
    'opacity:',
    'outline-color:',
    'print-color-adjust:',
    'scrollbar-color:',
    'stroke-color',
    'text-decoration-color:',
    'text-emphasis-color:',

];

const cssColorImpactProps = [
    'background:',
    'border:',
    'border-bottom:',
    'border-block:',
    'border-inline:',
    'border-inline-end:',
    'border-inline-start:',
    'border-left:',
    'border-right:',
    'border-top:',
    'caret:',
    'clip:',
    'content:',
    'content-visibility:',
    'fill:',
    'outline:',
    'text-decoration:',

];

function colorScrape() {

    let errorList = [];


    /////////////////////////////////////////////////////
    // Test every visible text element for color contrast
    // In the case of <input> then also paceholder contrast
    /////////////////////////////////////////////////////

    let elements = document.querySelectorAll("*");
    elements.forEach(element => {

        if (!(element.offsetParent === null)) {
            // Element not hidden

            const text = element.textContent;
            if (text !== null || text.trim() != '') {
                // Only check content that actually has text

                const xpath = Elements.DOMPath.xPath(element, true);

                const fgColor = getComputedStyle(element)["color"];
                const bgColor = getComputedStyle(element)["background-color"];

                const col = testContrast(fgColor, bgColor, element);

                if (!col.isAA) {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'color',
                        err: 'ErrTextContrast',
                        fg: col.fgHex,
                        bg: col.bgHex,
                        ratio: col.ratio,
                        fontSize: col.fontSize,
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

    //////////////////////////////////////////////////////////
    // Test if color is hard coded to an element with style:
    //  color
    //  background-color
    //  border-color
    //  outline-color
    /////////////////////////////////////////////////////////

    elements = document.querySelectorAll("body[style], body *[style]");
    elements.forEach(element => {

        const style = element.getAttribute('style');

        const xpath = Elements.DOMPath.xPath(element, true);

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'css',
            err: 'DiscoStyleAttrOnElements',
            style: style,
            xpath: xpath,
            parentLandmark: element.getAttribute('a11y-parentLandmark'),
            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
            fpTempId: element.getAttribute('a11y-fpId')
        });

        cssColorProps.forEach(prop => {
            if (style.includes(prop)) {
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'color',
                    err: 'ErrColorStyleDefinedExplicitlyInElement',
                    prop: prop.slice(0, -1),
                    style: style,
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId') 
                });
            }
        });

        cssColorImpactProps.forEach(prop => {
            if (style.includes(prop)) {
            
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'color',
                    err: 'ErrColorRelatedStyleDefinedExplicitlyInElement',
                    prop: prop.slice(0, -1),
                    style: style,
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')      
                });
            }
        });
    });


    ///////////////////////////////////////////////////////////////
    // Test if color is hard coded into a style block on the page
    //  color
    //  background-color
    //  border-color
    //  outline-color
    ///////////////////////////////////////////////////////////////

    // style inside the head
    styleElements = document.querySelectorAll("head style");
    styleElements.forEach(element => {

        const style = element.textContent;
        const xpath = Elements.DOMPath.xPath(element, true);

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'css',
            err: 'DiscoStyleElementOnPage',
            location: 'head',
            xpath: xpath,
            fpTempId: element.getAttribute('a11y-fpId')
         });

    });


    // styles inside the body
    styleElements = document.querySelectorAll("body style");
    styleElements.forEach(element => {

        const style = element.textContent;
        const xpath = Elements.DOMPath.xPath(element, true);

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'css',
            err: 'DiscoStyleElementOnPage',
            loation: 'body',
            xpath: xpath,
            parentLandmark: element.getAttribute('a11y-parentLandmark'),
            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
            fpTempId: element.getAttribute('a11y-fpId')     
        });

        cssColorProps.forEach(prop => {

            if (style.includes(prop)) {
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'color',
                    err: 'ErrColorStyleDefinedExplicitlyInStyleTag',
                    prop: prop.slice(0, -1),
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')      
                });
            }
        });

        cssColorImpactProps.forEach(prop => {
            if (style.includes(prop)) {
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'color',
                    err: 'ErrColorRelatedStyleDefinedExplicitlyInStyleTag',
                    prop: prop.slice(0, -1),
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')    
                });
            }
        });

    });

    //////////////////////////////////////////////////////////////
    // Warn if an element has an opacity of less than 1
    //   - we may ned to manually test for color contrast
    //////////////////////////////////////////////////////////////



    ///////////////////////////////////////////////////////////////////
    // Get hover, focus state colors to build a color model of the site
    ///////////////////////////////////////////////////////////////////


    //////////////////////////////////////////////////////////////
    // Test non-text contrast
    //////////////////////////////////////////////////////////////


    ///////////////////////////////////////////////////////////////////////////////////
    // Test links in paragraphs, divs and spans for use of color as sole discriminator
    ///////////////////////////////////////////////////////////////////////////////////


    return { errors: errorList };

}
