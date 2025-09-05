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
    let passList = [];
    let checks = [];
    
    // Initialize checks
    let contrastCheck = {
        id: 'text_contrast',
        description: 'Text has sufficient color contrast',
        wcag: ['1.4.3', '1.4.6'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    let inlineStyleCheck = {
        id: 'inline_styles',
        description: 'Avoid inline color styles',
        wcag: ['1.4.1'],
        applicable: true,
        total: 0,
        passed: 0,
        failed: 0
    };
    
    /////////////////////////////////////////////////////
    // Test every visible text element for color contrast
    /////////////////////////////////////////////////////
    
    // Get text elements more efficiently
    const textElements = [];
    const allElements = document.querySelectorAll("*");
    
    allElements.forEach(element => {
        // Skip hidden elements
        if (element.offsetParent === null) {
            return;
        }
        
        // Check if element has actual text content (not just whitespace)
        const hasDirectText = element.childNodes && Array.from(element.childNodes).some(
            node => node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 0
        );
        
        if (hasDirectText) {
            textElements.push(element);
        }
    });
    
    // Check applicability
    if (textElements.length === 0 && document.querySelectorAll('[style]').length === 0) {
        return {
            test_name: 'color',
            applicable: false,
            not_applicable_reason: 'No visible text elements or styled elements found',
            elements_found: 0,
            elements_tested: 0,
            elements_passed: 0,
            elements_failed: 0,
            errors: [],
            passes: [],
            checks: [{
                id: 'text_contrast',
                description: 'Text has sufficient color contrast',
                wcag: ['1.4.3', '1.4.6'],
                applicable: false,
                total: 0,
                passed: 0,
                failed: 0
            }]
        };
    }
    
    // Test contrast for text elements
    textElements.forEach(element => {
        contrastCheck.total++;
        const xpath = Elements.DOMPath.xPath(element, true);
        
        try {
            const fgColor = getComputedStyle(element)["color"];
            const bgColor = getComputedStyle(element)["background-color"];
            
            // Skip if colors can't be determined
            if (!fgColor || !bgColor || fgColor === 'transparent' || bgColor === 'transparent') {
                // Can't determine contrast - skip but don't fail
                contrastCheck.total--;
                return;
            }
            
            const col = testContrast(fgColor, bgColor, element);
            
            if (!col.isAA) {
                contrastCheck.failed++;
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
            } else {
                contrastCheck.passed++;
                
                // Record pass with details
                passList.push({
                    check: 'text_contrast',
                    element: element.tagName,
                    xpath: xpath,
                    wcag: col.isAAA ? ['1.4.3', '1.4.6'] : ['1.4.3'],
                    reason: `Contrast ratio ${col.ratio.toFixed(2)}:1 ${col.isAAA ? '(AAA)' : '(AA)'}`,
                    details: {
                        foreground: col.fgHex,
                        background: col.bgHex,
                        ratio: col.ratio,
                        fontSize: col.fontSize
                    }
                });
            }
        } catch (e) {
            // Error getting styles - skip this element
            contrastCheck.total--;
        }
    });
    
    //////////////////////////////////////////////////////////
    // Test if color is hard coded to an element with style attribute
    /////////////////////////////////////////////////////////
    
    const styledElements = document.querySelectorAll("body[style], body *[style]");
    styledElements.forEach(element => {
        const style = element.getAttribute('style');
        const xpath = Elements.DOMPath.xPath(element, true);
        
        // Discovery item for style attribute (not counted in pass/fail)
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
        
        // Check for color-related properties
        let hasColorStyle = false;
        
        cssColorProps.forEach(prop => {
            if (style.includes(prop)) {
                hasColorStyle = true;
                inlineStyleCheck.total++;
                inlineStyleCheck.failed++;
                
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
                if (!hasColorStyle) {
                    inlineStyleCheck.total++;
                    inlineStyleCheck.failed++;
                }
                
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'color',
                    err: 'WarnColorRelatedStyleDefinedExplicitlyInElement',
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
        
        // If element has style but no color-related properties, it passes
        if (!hasColorStyle && style.trim().length > 0) {
            inlineStyleCheck.total++;
            inlineStyleCheck.passed++;
            passList.push({
                check: 'no_inline_color_styles',
                element: element.tagName,
                xpath: xpath,
                wcag: ['1.4.1'],
                reason: 'Element has inline styles but no color-related properties'
            });
        }
    });
    
    ///////////////////////////////////////////////////////////////
    // Test if color is hard coded into a style block on the page
    ///////////////////////////////////////////////////////////////
    
    // Style elements in head
    const headStyles = document.querySelectorAll("head style");
    headStyles.forEach(element => {
        const style = element.textContent;
        const xpath = Elements.DOMPath.xPath(element, true);
        
        // Discovery item (not counted in pass/fail)
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
    
    // Style elements in body
    const bodyStyles = document.querySelectorAll("body style");
    bodyStyles.forEach(element => {
        const style = element.textContent;
        const xpath = Elements.DOMPath.xPath(element, true);
        
        // Discovery item (not counted in pass/fail)
        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'css',
            err: 'DiscoStyleElementOnPage',
            location: 'body',
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
                    err: 'WarnColorRelatedStyleDefinedExplicitlyInStyleTag',
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
    
    // Add checks to results
    if (contrastCheck.total > 0) {
        checks.push(contrastCheck);
    }
    if (inlineStyleCheck.total > 0) {
        checks.push(inlineStyleCheck);
    }
    
    // Calculate totals
    const totalTested = contrastCheck.total + inlineStyleCheck.total;
    const totalPassed = contrastCheck.passed + inlineStyleCheck.passed;
    const totalFailed = contrastCheck.failed + inlineStyleCheck.failed;
    
    return {
        test_name: 'color',
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