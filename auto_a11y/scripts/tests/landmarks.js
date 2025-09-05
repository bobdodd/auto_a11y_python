function landmarksScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Landmarks are always applicable - all pages should have proper structure
    let mainCheck = initializeCheck('main_landmark', 'Page has main landmark', ['1.3.1', '2.4.1']);
    let bannerCheck = initializeCheck('banner_landmark', 'Page has appropriate banner', ['1.3.1']);
    let contentInfoCheck = initializeCheck('contentinfo_landmark', 'Page has appropriate contentinfo', ['1.3.1']);
    let navigationCheck = initializeCheck('navigation_landmark', 'Navigation areas properly marked', ['1.3.1']);
    
    // Check for main landmark
    const mainElements = document.querySelectorAll('main, [role="main"]');
    mainCheck.total = 1;
    
    if (mainElements.length === 0) {
        mainCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            err: 'ErrNoMainLandmark',
            xpath: '/html/body',
            fpTempId: '0'
        });
    } else if (mainElements.length === 1) {
        mainCheck.passed = 1;
        passList.push({
            check: 'main_landmark',
            element: mainElements[0].tagName,
            xpath: Elements.DOMPath.xPath(mainElements[0], true),
            wcag: ['1.3.1', '2.4.1'],
            reason: 'Page has main landmark'
        });
    } else {
        mainCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            err: 'ErrMultipleMainLandmarks',
            count: mainElements.length,
            xpath: '/html/body',
            fpTempId: '0'
        });
    }
    
    // Check for banner (header)
    const bannerElements = document.querySelectorAll('header:not([role]), [role="banner"]');
    bannerCheck.total = 1;
    
    if (bannerElements.length === 0) {
        bannerCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            err: 'WarnNoBannerLandmark',
            xpath: '/html/body',
            fpTempId: '0'
        });
    } else if (bannerElements.length === 1) {
        bannerCheck.passed = 1;
        passList.push({
            check: 'banner_landmark',
            element: bannerElements[0].tagName,
            xpath: Elements.DOMPath.xPath(bannerElements[0], true),
            wcag: ['1.3.1'],
            reason: 'Page has banner landmark'
        });
    } else {
        bannerCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            err: 'ErrMultipleBannerLandmarks',
            count: bannerElements.length,
            xpath: '/html/body',
            fpTempId: '0'
        });
    }
    
    // Check for contentinfo (footer)
    const footerElements = document.querySelectorAll('footer:not([role]), [role="contentinfo"]');
    contentInfoCheck.total = 1;
    
    if (footerElements.length === 0) {
        contentInfoCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            err: 'WarnNoContentinfoLandmark',
            xpath: '/html/body',
            fpTempId: '0'
        });
    } else if (footerElements.length === 1) {
        contentInfoCheck.passed = 1;
        passList.push({
            check: 'contentinfo_landmark',
            element: footerElements[0].tagName,
            xpath: Elements.DOMPath.xPath(footerElements[0], true),
            wcag: ['1.3.1'],
            reason: 'Page has contentinfo landmark'
        });
    } else {
        contentInfoCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            err: 'ErrMultipleContentinfoLandmarks',
            count: footerElements.length,
            xpath: '/html/body',
            fpTempId: '0'
        });
    }
    
    // Check navigation landmarks
    const navElements = document.querySelectorAll('nav, [role="navigation"]');
    navigationCheck.total = navElements.length || 1;
    
    if (navElements.length === 0) {
        navigationCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            err: 'WarnNoNavigationLandmark',
            xpath: '/html/body',
            fpTempId: '0'
        });
    } else {
        navElements.forEach(nav => {
            const hasLabel = nav.hasAttribute('aria-label') || nav.hasAttribute('aria-labelledby');
            if (navElements.length > 1 && !hasLabel) {
                navigationCheck.failed++;
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    err: 'WarnMultipleNavNeedsLabel',
                    xpath: Elements.DOMPath.xPath(nav, true),
                    fpTempId: nav.getAttribute('a11y-fpId')
                });
            } else {
                navigationCheck.passed++;
                passList.push({
                    check: 'navigation_landmark',
                    element: nav.tagName,
                    xpath: Elements.DOMPath.xPath(nav, true),
                    wcag: ['1.3.1'],
                    reason: hasLabel ? 'Navigation has label' : 'Navigation properly marked'
                });
            }
        });
    }
    
    // Check for elements not in landmarks
    const contentElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, a, button, input, select, textarea, img');
    let elementsNotInLandmarks = 0;
    
    contentElements.forEach(element => {
        const inLandmark = element.closest('main, [role="main"], header, [role="banner"], footer, [role="contentinfo"], nav, [role="navigation"], aside, [role="complementary"]');
        if (!inLandmark && element.offsetParent !== null) {
            elementsNotInLandmarks++;
            errorList.push({
                url: window.location.href,
                type: 'warn',
                cat: 'landmark',
                err: 'WarnElementNotInLandmark',
                element: element.tagName,
                xpath: Elements.DOMPath.xPath(element, true),
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }
    });
    
    // Add checks to results
    checks.push(mainCheck);
    checks.push(bannerCheck);
    checks.push(contentInfoCheck);
    checks.push(navigationCheck);
    
    const totalPassed = mainCheck.passed + bannerCheck.passed + contentInfoCheck.passed + navigationCheck.passed;
    const totalFailed = mainCheck.failed + bannerCheck.failed + contentInfoCheck.failed + navigationCheck.failed;
    
    return createApplicableResult('landmarks', 4, totalPassed, totalFailed, errorList, passList, checks);
}