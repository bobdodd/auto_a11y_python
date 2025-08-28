const recommendedFonts = [
    'Aphont',
    'Arial',
    'Arvo',
    'Bebas Neue',
    'Book Antiqua',
    'Calibri',
    'Comic Sans',
    'Georgia',
    'Helvetica',
    'Lavanderia',
    'Lucida Sans',
    'Museo Slab',
    'Palatino',
    'Rockwell',
    'Tahoma',
    'Verdana',
];

function fontsScrape() {

    let errorList = [];

    /////////////////////////////////////////////////////
    // Test every visible text element for font size
    /////////////////////////////////////////////////////

    // Location head
    let elements = document.querySelectorAll("head *");
    elements.forEach(element => {

        if (!(element.offsetParent === null)) {
            // Element not hidden

            const text = element.textContent;
            if (text !== null || text.trim() != '') {
                // Only check content that actually has text

                const xpath = Elements.DOMPath.xPath(element, true);
                const fontSize = parseFloat(getComputedStyle(element)["font-size"]);

                let fontFace;
                fontFamily = getComputedStyle(element)["font-family"];
                if (fontFamily === null || fontFamily === '') fontFamily = 'default';

                const fontList = fontFamily.split(',');
                fontList.forEach(font => {

                    // Strip quotes if any
                    if (font.startsWith('"')) {
                        font = font.splice(1);
                    }
                    if (font.endsWith('"')) {
                        font = font.splice(0,-1);
                    }

                    errorList.push({
                        url: window.location.href,
                        type: 'disco',
                        cat: 'fonts',
                        err: 'DiscoFontFound',
                        found: font,
                        xpath: xpath,
                        location: 'head',
                        fpTempId: element.getAttribute('a11y-fpId')
                    });


                    if (!(font in recommendedFonts)) {

                        errorList.push({
                            url: window.location.href,
                            type: 'warn',
                            cat: 'fonts',
                            err: 'WarnFontNotInRecommenedListForA11y',
                            found: font,
                            xpath: xpath,
                            location: "head",
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    }

                })


                if (fontSize < 16.0) {

                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'fonts',
                        err: 'WarnFontsizeIsBelow16px',
                        fontSize: fontSize,
                        xpath: xpath,
                        location: "head",
                        fpTempId: element.getAttribute('a11y-fpId')
                    });

                }

            }
        }
    });


    // Location body
    elements = document.querySelectorAll("body *");
    elements.forEach(element => {

        if (!(element.offsetParent === null)) {
            // Element not hidden

            const text = element.textContent;
            if (text !== null || text.trim() != '') {
                // Only check content that actually has text

                const xpath = Elements.DOMPath.xPath(element, true);
                const fontSize = parseFloat(getComputedStyle(element)["font-size"]);

                let fontFamily;
                fontFamily = getComputedStyle(element)["font-family"];
                if (fontFamily === null || fontFamily === '') fontFamily = 'default';

                fontList = fontFamily.split(',');
                fontList.forEach(font => {

                    if (font.startsWith('"')) font = fontFamily.slice(1);
                    if (font.endsWith('"')) font = fontFamily.slice(0, -1);

                    errorList.push({
                        url: window.location.href,
                        type: 'disco',
                        cat: 'fonts',
                        err: 'DiscoFontFound',
                        found: font,
                        xpath: xpath,
                        location: 'body',
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });


                    if (!(font in recommendedFonts)) {

                        errorList.push({
                            url: window.location.href,
                            type: 'warn',
                            cat: 'fonts',
                            err: 'WarnFontNotInRecommenedListForA11y',
                            found: font,
                            xpath: xpath,
                            location: "body",
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    }

                })


                if (fontSize < 16.0) {

                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'fonts',
                        err: 'WarnFontsizeIsBelow16px',
                        fontSize: fontSize,
                        xpath: xpath,
                        location: "body",
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });

                }

            }
        }
    });

    return { errors: errorList };

}