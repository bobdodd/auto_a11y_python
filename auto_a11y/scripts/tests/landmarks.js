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

            // DISCOVERY: Report each navigation element for tracking across pages
            const navXPath = Elements.DOMPath.xPath(nav, true);
            const navHTML = nav.outerHTML.substring(0, 500); // First 500 chars for signature

            // Count links in this navigation
            const links = nav.querySelectorAll('a');
            const linkCount = links.length;

            // Get accessible name if present
            let navLabel = '';
            if (nav.hasAttribute('aria-label')) {
                navLabel = nav.getAttribute('aria-label');
            } else if (nav.hasAttribute('aria-labelledby')) {
                const labelId = nav.getAttribute('aria-labelledby');
                const labelEl = document.getElementById(labelId);
                if (labelEl) {
                    navLabel = labelEl.textContent.trim();
                }
            }

            // Generate signature from nav structure (similar to forms)
            // Use the nav's link text to create a signature
            const navStructure = Array.from(links).map(link => link.textContent.trim()).join('|');
            const signatureString = navStructure + '|' + navXPath;

            // Simple hash function (same as forms)
            let hash = 0;
            for (let i = 0; i < signatureString.length; i++) {
                const char = signatureString.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convert to 32bit integer
            }
            const navSignature = Math.abs(hash).toString(16).padStart(8, '0');

            errorList.push({
                url: window.location.href,
                type: 'disco',
                cat: 'landmarks',
                err: 'DiscoNavFound',
                xpath: navXPath,
                element: nav.tagName.toLowerCase(),
                html: navHTML,
                navSignature: navSignature,
                linkCount: linkCount,
                navLabel: navLabel,
                fpTempId: nav.getAttribute('a11y-fpId')
            });
        });
    }

    // DISCOVERY: Report each <aside> or role="complementary" for tracking across pages
    {
        const asideElements = document.querySelectorAll('aside, [role="complementary"]');
        asideElements.forEach(aside => {
            const asideXPath = Elements.DOMPath.xPath(aside, true);
            const asideHTML = aside.outerHTML.substring(0, 500);

            let asideLabel = '';
            const ariaLabel = aside.getAttribute('aria-label');
            if (ariaLabel) {
                asideLabel = ariaLabel.trim();
            } else {
                const labelledBy = aside.getAttribute('aria-labelledby');
                if (labelledBy) {
                    const labelEl = document.getElementById(labelledBy);
                    if (labelEl) asideLabel = labelEl.textContent.trim();
                }
            }

            // Generate signature based on text content structure
            const textContent = aside.textContent.trim().substring(0, 200);
            const signatureString = textContent + '|' + asideXPath;

            // Simple hash function
            let hash = 0;
            for (let i = 0; i < signatureString.length; i++) {
                const char = signatureString.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash;
            }
            const asideSignature = Math.abs(hash).toString(16).padStart(8, '0');

            errorList.push({
                url: window.location.href,
                type: 'disco',
                cat: 'landmarks',
                err: 'DiscoAsideFound',
                xpath: asideXPath,
                element: aside.tagName.toLowerCase(),
                html: asideHTML,
                asideSignature: asideSignature,
                asideLabel: asideLabel,
                fpTempId: aside.getAttribute('a11y-fpId')
            });
        });
    }

    // DISCOVERY: Report each <section> with role="region" or explicit aria-label/labelledby
    {
        const sectionElements = document.querySelectorAll('section[role="region"], section[aria-label], section[aria-labelledby]');
        sectionElements.forEach(section => {
            const sectionXPath = Elements.DOMPath.xPath(section, true);
            const sectionHTML = section.outerHTML.substring(0, 500);

            let sectionLabel = '';
            const ariaLabel = section.getAttribute('aria-label');
            if (ariaLabel) {
                sectionLabel = ariaLabel.trim();
            } else {
                const labelledBy = section.getAttribute('aria-labelledby');
                if (labelledBy) {
                    const labelEl = document.getElementById(labelledBy);
                    if (labelEl) sectionLabel = labelEl.textContent.trim();
                }
            }

            // Generate signature based on text content structure
            const textContent = section.textContent.trim().substring(0, 200);
            const signatureString = textContent + '|' + sectionLabel + '|' + sectionXPath;

            // Simple hash function
            let hash = 0;
            for (let i = 0; i < signatureString.length; i++) {
                const char = signatureString.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash;
            }
            const sectionSignature = Math.abs(hash).toString(16).padStart(8, '0');

            errorList.push({
                url: window.location.href,
                type: 'disco',
                cat: 'landmarks',
                err: 'DiscoSectionFound',
                xpath: sectionXPath,
                element: section.tagName.toLowerCase(),
                html: sectionHTML,
                sectionSignature: sectionSignature,
                sectionLabel: sectionLabel,
                fpTempId: section.getAttribute('a11y-fpId')
            });
        });
    }

    // DISCOVERY: Report each <header> at top level or role="banner"
    {
        const headerElements = document.querySelectorAll('header, [role="banner"]');
        headerElements.forEach(header => {
            // Only report top-level headers (not nested in article/section) or explicit role="banner"
            const hasExplicitRole = header.getAttribute('role') === 'banner';
            const isTopLevel = !header.closest('article, section, aside, nav, main');

            if (hasExplicitRole || isTopLevel) {
                const headerXPath = Elements.DOMPath.xPath(header, true);
                const headerHTML = header.outerHTML.substring(0, 500);

                let headerLabel = '';
                const ariaLabel = header.getAttribute('aria-label');
                if (ariaLabel) {
                    headerLabel = ariaLabel.trim();
                } else {
                    const labelledBy = header.getAttribute('aria-labelledby');
                    if (labelledBy) {
                        const labelEl = document.getElementById(labelledBy);
                        if (labelEl) headerLabel = labelEl.textContent.trim();
                    }
                }

                // Generate signature based on text content structure
                const textContent = header.textContent.trim().substring(0, 200);
                const signatureString = textContent + '|' + headerXPath;

                // Simple hash function
                let hash = 0;
                for (let i = 0; i < signatureString.length; i++) {
                    const char = signatureString.charCodeAt(i);
                    hash = ((hash << 5) - hash) + char;
                    hash = hash & hash;
                }
                const headerSignature = Math.abs(hash).toString(16).padStart(8, '0');

                errorList.push({
                    url: window.location.href,
                    type: 'disco',
                    cat: 'landmarks',
                    err: 'DiscoHeaderFound',
                    xpath: headerXPath,
                    element: header.tagName.toLowerCase(),
                    html: headerHTML,
                    headerSignature: headerSignature,
                    headerLabel: headerLabel,
                    fpTempId: header.getAttribute('a11y-fpId')
                });
            }
        });
    }

    // DISCOVERY: Report each <footer> at top level or role="contentinfo"
    {
        const footerElements = document.querySelectorAll('footer, [role="contentinfo"]');
        footerElements.forEach(footer => {
            // Only report top-level footers (not nested in article/section) or explicit role="contentinfo"
            const hasExplicitRole = footer.getAttribute('role') === 'contentinfo';
            const isTopLevel = !footer.closest('article, section, aside, nav, main');

            if (hasExplicitRole || isTopLevel) {
                const footerXPath = Elements.DOMPath.xPath(footer, true);
                const footerHTML = footer.outerHTML.substring(0, 500);

                let footerLabel = '';
                const ariaLabel = footer.getAttribute('aria-label');
                if (ariaLabel) {
                    footerLabel = ariaLabel.trim();
                } else {
                    const labelledBy = footer.getAttribute('aria-labelledby');
                    if (labelledBy) {
                        const labelEl = document.getElementById(labelledBy);
                        if (labelEl) footerLabel = labelEl.textContent.trim();
                    }
                }

                // Generate signature based on text content structure
                const textContent = footer.textContent.trim().substring(0, 200);
                const signatureString = textContent + '|' + footerXPath;

                // Simple hash function
                let hash = 0;
                for (let i = 0; i < signatureString.length; i++) {
                    const char = signatureString.charCodeAt(i);
                    hash = ((hash << 5) - hash) + char;
                    hash = hash & hash;
                }
                const footerSignature = Math.abs(hash).toString(16).padStart(8, '0');

                errorList.push({
                    url: window.location.href,
                    type: 'disco',
                    cat: 'landmarks',
                    err: 'DiscoFooterFound',
                    xpath: footerXPath,
                    element: footer.tagName.toLowerCase(),
                    html: footerHTML,
                    footerSignature: footerSignature,
                    footerLabel: footerLabel,
                    fpTempId: footer.getAttribute('a11y-fpId')
                });
            }
        });
    }

    // DISCOVERY: Report each <search> or role="search"
    {
        const searchElements = document.querySelectorAll('search, [role="search"]');
        searchElements.forEach(search => {
            const searchXPath = Elements.DOMPath.xPath(search, true);
            const searchHTML = search.outerHTML.substring(0, 500);

            let searchLabel = '';
            const ariaLabel = search.getAttribute('aria-label');
            if (ariaLabel) {
                searchLabel = ariaLabel.trim();
            } else {
                const labelledBy = search.getAttribute('aria-labelledby');
                if (labelledBy) {
                    const labelEl = document.getElementById(labelledBy);
                    if (labelEl) searchLabel = labelEl.textContent.trim();
                }
            }

            // Generate signature based on text content structure
            const textContent = search.textContent.trim().substring(0, 200);
            const signatureString = textContent + '|' + searchLabel + '|' + searchXPath;

            // Simple hash function
            let hash = 0;
            for (let i = 0; i < signatureString.length; i++) {
                const char = signatureString.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash;
            }
            const searchSignature = Math.abs(hash).toString(16).padStart(8, '0');

            errorList.push({
                url: window.location.href,
                type: 'disco',
                cat: 'landmarks',
                err: 'DiscoSearchFound',
                xpath: searchXPath,
                element: search.tagName.toLowerCase(),
                html: searchHTML,
                searchSignature: searchSignature,
                searchLabel: searchLabel,
                fpTempId: search.getAttribute('a11y-fpId')
            });
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