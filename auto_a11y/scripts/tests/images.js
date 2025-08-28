function imagesScrape() {

    let errorList = [];

    ///////////////////////////////////////
    // Images with no ALT attribute
    ///////////////////////////////////////
    const imagesWithNoAltAttr = document.querySelectorAll('img:not([alt]');
    imagesWithNoAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);

            let src = 'none';
            if (element.hasAttribute('src')) {
                src = element.getAttribute('src');
            }

            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'img',
                err: 'ErrImageWithNoAlt',
                src: src,
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')    
            });

        }
    });

    ///////////////////////////////////////
    // Images with empty ALT attribute
    ///////////////////////////////////////
    const imagesWithEmptyAltAttr = document.querySelectorAll('img[alt]');
    imagesWithEmptyAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);

            const txt = element.getAttribute('alt');
            if (txt !== '' && txt.trim() === '') {
                let src = 'none';
                if (element.hasAttribute('src')) {
                    src = element.getAttribute('src');
                }
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'img',
                    err: 'ErrImageWithEmptyAlt',
                    src: src,
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')      
                });
            }
        }
    });

    ///////////////////////////////////////////////////////////////
    // Images with  ALT attribute that starts with http: or https:
    ////////////////////////////////////////////////////////////////
    const imagesWithLinkAltAttr = document.querySelectorAll('img[alt]');
    imagesWithLinkAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);

            const txt = element.getAttribute('alt').trim();
            if (txt.startsWith('http:') || txt.startsWith('https:')) {
                let src = 'none';
                if (element.hasAttribute('src')) {
                    src = element.getAttribute('src');
                }
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'img',
                    err: 'ErrImageWithEmptyAlt',
                    src: src,
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')   
                });
            }
        }
    });

    ///////////////////////////////////////////////////////////////
    // Images with  ALT attribute that ends withan image extension
    ////////////////////////////////////////////////////////////////
    const imagesWithImgFileExtensionAltAttr = document.querySelectorAll('img[alt]');
    imagesWithImgFileExtensionAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);

            const txt = element.getAttribute('alt').trim();
            if (txt.endsWith('.png') || txt.includes('.png?') ||
                txt.endsWith('.jpg') || txt.includes('.jpg?') ||
                txt.endsWith('.webp') || txt.includes('.webp?') ||
                txt.endsWith('.svg') || txt.includes('.svg?')
            ) {
                let src = 'none';
                if (element.hasAttribute('src')) {
                    src = element.getAttribute('src');
                }
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'img',
                    err: 'ErrImageWithImgFileExtensionAlt',
                    src: src,
                    xpath: xpath,
                    parentLandmark: element.getAttribute('a11y-parentLandmark'),
                    parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                    parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                    fpTempId: element.getAttribute('a11y-fpId')    
                });
            }
        }
    });

    ///////////////////////////////////////////////////////////////
    // Illegal ALT attribute
    ////////////////////////////////////////////////////////////////
    const illagealAltAttr = document.querySelectorAll('[alt]');
    illagealAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);

            if ((element.tagName !== 'IMG' && element.tagName !== 'AREA') || (element.tagName === 'INPUT' & element.hasAttribute('type') && element.getAttribute('type') !== 'image')) {

                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'img',
                    err: 'ErrAltOnElementThatDoesntTakeIt',
                    tag: element.tagName,
                    alt: element.getAttribute('alt'),
                    xpath: xpath,
                    fpTempId: element.getAttribute('a11y-fpId')
                });
           
            }

        }
    });


    return { errors: errorList };


}
