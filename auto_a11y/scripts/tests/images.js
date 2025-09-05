function imagesScrape() {

    let errorList = [];
    let passList = [];
    let checks = [];

    // Check applicability - are there any images?
    const allImages = document.querySelectorAll('img');
    
    if (allImages.length === 0) {
        // No images on page - test is not applicable
        return {
            test_name: 'images',
            applicable: false,
            not_applicable_reason: 'No images found on page',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'image_alt_text',
                description: 'All images have appropriate alt text',
                wcag: ['1.1.1'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }

    // Initialize check tracking
    let altTextCheck = {
        id: 'image_alt_text',
        description: 'All images have appropriate alt text',
        wcag: ['1.1.1'],
        applicable: true,
        total: allImages.length,
        passed: 0,
        failed: 0
    };

    // Track which images we've already processed
    let processedImages = new Set();

    ///////////////////////////////////////
    // Images with no ALT attribute
    ///////////////////////////////////////
    const imagesWithNoAltAttr = document.querySelectorAll('img:not([alt])');
    imagesWithNoAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);
            processedImages.add(xpath);
            altTextCheck.failed++;

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
            
            // Skip if already processed
            if (processedImages.has(xpath)) {
                return;
            }

            const txt = element.getAttribute('alt');
            
            // Check for empty or whitespace-only alt
            if (txt !== '' && txt.trim() === '') {
                processedImages.add(xpath);
                altTextCheck.failed++;
                
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
            
            // Skip if already processed
            if (processedImages.has(xpath)) {
                return;
            }

            const txt = element.getAttribute('alt').trim();
            if (txt.startsWith('http:') || txt.startsWith('https:') || txt.startsWith('www.')) {
                processedImages.add(xpath);
                altTextCheck.failed++;
                
                let src = 'none';
                if (element.hasAttribute('src')) {
                    src = element.getAttribute('src');
                }
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'img',
                    err: 'ErrImageWithURLAsAlt',
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
    // Images with  ALT attribute that ends with an image extension
    ////////////////////////////////////////////////////////////////
    const imagesWithImgFileExtensionAltAttr = document.querySelectorAll('img[alt]');
    imagesWithImgFileExtensionAltAttr.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            const xpath = Elements.DOMPath.xPath(element, true);
            
            // Skip if already processed
            if (processedImages.has(xpath)) {
                return;
            }

            const txt = element.getAttribute('alt').trim();
            if (txt.endsWith('.png') || txt.includes('.png?') ||
                txt.endsWith('.jpg') || txt.includes('.jpg?') ||
                txt.endsWith('.webp') || txt.includes('.webp?') ||
                txt.endsWith('.svg') || txt.includes('.svg?')
            ) {
                processedImages.add(xpath);
                altTextCheck.failed++;
                
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
    const illegalAltAttr = document.querySelectorAll('[alt]');
    illegalAltAttr.forEach(element => {
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

    // Process all images to find passes
    allImages.forEach(element => {
        const xpath = Elements.DOMPath.xPath(element, true);
        
        // If not in processed (failed) set, it passed
        if (!processedImages.has(xpath)) {
            const altText = element.getAttribute('alt');
            
            // Has alt attribute and it's not problematic
            if (element.hasAttribute('alt') && altText !== null) {
                altTextCheck.passed++;
                
                let src = 'none';
                if (element.hasAttribute('src')) {
                    src = element.getAttribute('src');
                }
                
                passList.push({
                    check: 'image_has_alt',
                    element: 'IMG',
                    src: src,
                    alt: altText,
                    xpath: xpath,
                    wcag: ['1.1.1'],
                    reason: altText === '' ? 'Decorative image with empty alt' : 'Image has descriptive alt text'
                });
            }
        }
    });

    // Add check to results
    checks.push(altTextCheck);

    return {
        test_name: 'images',
        applicable: true,
        elements_found: allImages.length,
        elements_tested: allImages.length,
        elements_passed: altTextCheck.passed,
        elements_failed: altTextCheck.failed,
        errors: errorList,
        passes: passList,
        checks: checks
    };
}