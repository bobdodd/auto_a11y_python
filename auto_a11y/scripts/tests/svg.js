function svgScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Check applicability - are there any SVG elements?
    const allSvg = document.querySelectorAll('svg');
    
    if (allSvg.length === 0) {
        return createNotApplicableResult('svg', 'No SVG elements found on page', [
            {
                id: 'svg_accessibility',
                description: 'SVG elements are accessible',
                wcag: ['1.1.1']
            }
        ]);
    }
    
    // Initialize check
    let svgCheck = initializeCheck('svg_accessibility', 'SVG elements are accessible', ['1.1.1']);
    
    const svgImage = document.querySelectorAll('svg[role="image"]');
    const svgInline = document.querySelectorAll('svg:not([role="image"])');
    
    // Check SVG images
    svgImage.forEach(img => {
        svgCheck.total++;
        const xpath = Elements.DOMPath.xPath(img, true);
        
        // Check if has title or aria-label
        const hasTitle = img.querySelector('title');
        const hasAriaLabel = img.hasAttribute('aria-label');
        const hasAriaLabelledby = img.hasAttribute('aria-labelledby');
        
        if (hasTitle || hasAriaLabel || hasAriaLabelledby) {
            svgCheck.passed++;
            passList.push({
                check: 'svg_image_labeled',
                element: 'SVG',
                xpath: xpath,
                wcag: ['1.1.1'],
                reason: 'SVG image has accessible name'
            });
        } else {
            svgCheck.failed++;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'svg',
                err: 'ErrSvgImageNoLabel',
                xpath: xpath,
                fpTempId: img.getAttribute('a11y-fpId')
            });
        }
        
        // Discovery for manual review (not counted in pass/fail)
        // Note: Discovery items are pushed to errorList but marked with type: 'disco'
        // The result processor will categorize them separately
        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'svg',
            err: 'DiscoFoundSvgImage',
            xpath: xpath,
            fpTempId: '0'
        });
    });
    
    // Check inline SVG
    svgInline.forEach(svg => {
        svgCheck.total++;
        const xpath = Elements.DOMPath.xPath(svg, true);
        
        // For inline SVG, check if it's decorative or has proper labeling
        const isHidden = svg.getAttribute('aria-hidden') === 'true';
        const hasRole = svg.hasAttribute('role');
        
        if (isHidden) {
            svgCheck.passed++;
            passList.push({
                check: 'svg_decorative',
                element: 'SVG',
                xpath: xpath,
                wcag: ['1.1.1'],
                reason: 'SVG marked as decorative'
            });
        } else if (!hasRole) {
            // Inline SVG without role - needs manual review
            svgCheck.passed++; // Don't fail, but flag for review
        }
        
        // Discovery for manual review (not counted in pass/fail)
        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'svg',
            err: 'DiscoFoundInlineSvg',
            xpath: xpath,
            fpTempId: '0'
        });
    });
    
    // Add check to results
    checks.push(svgCheck);
    
    return createApplicableResult('svg', allSvg.length, svgCheck.passed, svgCheck.failed, errorList, passList, checks);
}