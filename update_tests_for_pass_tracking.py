#!/usr/bin/env python3
"""
Update remaining JavaScript test files to include pass tracking and applicability
"""

import os
import re

def update_headings_js():
    """Update headings.js with pass tracking"""
    content = '''function headingsScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Check applicability - are there any headings?
    const allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]');
    
    if (allHeadings.length === 0) {
        return createNotApplicableResult('headings', 'No headings found on page', [
            {
                id: 'heading_hierarchy',
                description: 'Headings follow proper hierarchy',
                wcag: ['1.3.1']
            },
            {
                id: 'heading_content',
                description: 'Headings have content',
                wcag: ['2.4.6']
            }
        ]);
    }
    
    // Initialize checks
    let hierarchyCheck = initializeCheck('heading_hierarchy', 'Headings follow proper hierarchy', ['1.3.1']);
    let contentCheck = initializeCheck('heading_content', 'Headings have content', ['2.4.6']);
    let h1Check = initializeCheck('single_h1', 'Page has single H1', ['1.3.1']);
    
    let headingCount = 0;
    let h1Count = 0;
    let currentHeadingLevel = 0;
    let headingLevels = [];
    
    const elements = document.querySelectorAll("*");
    elements.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {
            const xpath = Elements.DOMPath.xPath(element, true);
            
            if (element.tagName === 'H1' || element.tagName === 'H2' || element.tagName === 'H3' || 
                element.tagName === 'H4' || element.tagName === 'H5' || element.tagName === 'H6' ||
                (element.hasAttribute("role") && element.getAttribute('role').toLowerCase() == 'heading' && 
                 element.hasAttribute("aria-level") && element.getAttribute('aria-level') < 7)) {
                
                const hiddenElement = (element.offsetParent === null);
                
                if (!hiddenElement) {
                    ++headingCount;
                    hierarchyCheck.total++;
                    contentCheck.total++;
                    
                    // Check content
                    const res = computeTextAlternative(element);
                    const trimmed = res.name.trim();
                    
                    if (trimmed === "" || trimmed === null) {
                        contentCheck.failed++;
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'heading',
                            err: 'ErrEmptyHeading',
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    } else {
                        contentCheck.passed++;
                        passList.push({
                            check: 'heading_has_content',
                            element: element.tagName,
                            text: trimmed.substring(0, 50),
                            xpath: xpath,
                            wcag: ['2.4.6'],
                            reason: 'Heading has text content'
                        });
                    }
                    
                    // Check for overly long headings
                    if (trimmed.length > 60) {
                        errorList.push({
                            url: window.location.href,
                            type: 'warn',
                            cat: 'heading',
                            err: 'WarnHeadingOver60CharsLong',
                            headingText: trimmed,
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    }
                    
                    // Track heading levels
                    let newHeadingLevel = 0;
                    if (element.tagName === 'H1') { newHeadingLevel = 1; ++h1Count; }
                    if (element.tagName === 'H2') { newHeadingLevel = 2; }
                    if (element.tagName === 'H3') { newHeadingLevel = 3; }
                    if (element.tagName === 'H4') { newHeadingLevel = 4; }
                    if (element.tagName === 'H5') { newHeadingLevel = 5; }
                    if (element.tagName === 'H6') { newHeadingLevel = 6; }
                    
                    if (newHeadingLevel === 0 && element.hasAttribute('aria-level')) {
                        newHeadingLevel = parseInt(element.getAttribute('aria-level'));
                    }
                    
                    headingLevels.push({level: newHeadingLevel, element: element, xpath: xpath});
                    
                } else {
                    errorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'heading',
                        err: 'WarnHeadingInsideDisplayNone',
                        element: element.tagName,
                        headingText: element.textContent,
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
    
    // Check heading hierarchy
    let lastLevel = 0;
    let hierarchyPasses = 0;
    let hierarchyFails = 0;
    
    for (let i = 0; i < headingLevels.length; i++) {
        const heading = headingLevels[i];
        
        if (lastLevel > 0 && heading.level > lastLevel + 1) {
            hierarchyFails++;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'heading',
                err: 'ErrSkippedHeadingLevel',
                skippedFrom: lastLevel,
                skippedTo: heading.level,
                xpath: heading.xpath,
                fpTempId: heading.element.getAttribute('a11y-fpId')
            });
        } else {
            hierarchyPasses++;
            passList.push({
                check: 'heading_hierarchy',
                level: heading.level,
                xpath: heading.xpath,
                wcag: ['1.3.1'],
                reason: 'Heading level follows proper hierarchy'
            });
        }
        lastLevel = heading.level;
    }
    
    hierarchyCheck.passed = hierarchyPasses;
    hierarchyCheck.failed = hierarchyFails;
    
    // Check H1 count
    h1Check.total = 1;
    if (h1Count === 1) {
        h1Check.passed = 1;
        passList.push({
            check: 'single_h1',
            wcag: ['1.3.1'],
            reason: 'Page has exactly one H1'
        });
    } else if (h1Count > 1) {
        h1Check.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'heading',
            err: 'ErrMultipleH1',
            count: h1Count,
            fpTempId: '0'
        });
    } else {
        h1Check.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'heading',
            err: 'WarnNoH1',
            fpTempId: '0'
        });
    }
    
    // Add checks to results
    checks.push(hierarchyCheck);
    checks.push(contentCheck);
    checks.push(h1Check);
    
    return createApplicableResult('headings', headingCount, 
        hierarchyCheck.passed + contentCheck.passed + h1Check.passed,
        hierarchyCheck.failed + contentCheck.failed + h1Check.failed,
        errorList, passList, checks);
}'''
    
    with open('auto_a11y/scripts/tests/headings.js', 'w') as f:
        f.write(content)
    print("✅ Updated headings.js")

def update_landmarks_js():
    """Update landmarks.js with pass tracking"""
    content = '''function landmarksScrape() {
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
}'''
    
    with open('auto_a11y/scripts/tests/landmarks.js', 'w') as f:
        f.write(content)
    print("✅ Updated landmarks.js")

def update_language_js():
    """Update language.js with pass tracking"""
    content = '''function languageScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Language is always applicable - all pages need language declaration
    let langCheck = initializeCheck('page_language', 'Page has language declaration', ['3.1.1']);
    
    const htmlElement = document.querySelector('html');
    langCheck.total = 1;
    
    if (!htmlElement || !htmlElement.hasAttribute('lang')) {
        langCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'language',
            err: 'ErrNoPageLanguage',
            xpath: '/html',
            fpTempId: '0'
        });
    } else {
        const lang = htmlElement.getAttribute('lang');
        
        // Check if language code is valid (basic check for format)
        if (!lang || lang.trim() === '') {
            langCheck.failed = 1;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'language',
                err: 'ErrEmptyLanguageAttribute',
                xpath: '/html',
                fpTempId: '0'
            });
        } else if (!/^[a-z]{2}(-[A-Z]{2})?$/.test(lang)) {
            langCheck.failed = 1;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'language',
                err: 'ErrInvalidLanguageCode',
                found: lang,
                xpath: '/html',
                fpTempId: '0'
            });
        } else {
            langCheck.passed = 1;
            passList.push({
                check: 'page_language',
                language: lang,
                xpath: '/html',
                wcag: ['3.1.1'],
                reason: 'Page has valid language declaration'
            });
        }
    }
    
    // Check for lang changes in the document
    const elementsWithLang = document.querySelectorAll('[lang]');
    let langChangeCheck = initializeCheck('language_changes', 'Language changes properly marked', ['3.1.2']);
    
    elementsWithLang.forEach(element => {
        if (element !== htmlElement) {
            langChangeCheck.total++;
            const lang = element.getAttribute('lang');
            
            if (!lang || lang.trim() === '') {
                langChangeCheck.failed++;
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'language',
                    err: 'WarnEmptyLangAttribute',
                    element: element.tagName,
                    xpath: Elements.DOMPath.xPath(element, true),
                    fpTempId: element.getAttribute('a11y-fpId')
                });
            } else if (!/^[a-z]{2}(-[A-Z]{2})?$/.test(lang)) {
                langChangeCheck.failed++;
                errorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'language',
                    err: 'WarnInvalidLangChange',
                    element: element.tagName,
                    found: lang,
                    xpath: Elements.DOMPath.xPath(element, true),
                    fpTempId: element.getAttribute('a11y-fpId')
                });
            } else {
                langChangeCheck.passed++;
                passList.push({
                    check: 'language_change',
                    element: element.tagName,
                    language: lang,
                    xpath: Elements.DOMPath.xPath(element, true),
                    wcag: ['3.1.2'],
                    reason: 'Language change properly marked'
                });
            }
        }
    });
    
    // Add checks to results
    checks.push(langCheck);
    if (langChangeCheck.total > 0) {
        checks.push(langChangeCheck);
    }
    
    const totalPassed = langCheck.passed + langChangeCheck.passed;
    const totalFailed = langCheck.failed + langChangeCheck.failed;
    const totalChecks = langCheck.total + langChangeCheck.total;
    
    return createApplicableResult('language', totalChecks, totalPassed, totalFailed, errorList, passList, checks);
}'''
    
    with open('auto_a11y/scripts/tests/language.js', 'w') as f:
        f.write(content)
    print("✅ Updated language.js")

def update_pageTitle_js():
    """Update pageTitle.js with pass tracking"""
    content = '''function pageTitleScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Page title is always applicable - all pages need a title
    let titleCheck = initializeCheck('page_title', 'Page has descriptive title', ['2.4.2']);
    
    const titleElement = document.querySelector('title');
    titleCheck.total = 1;
    
    if (!titleElement) {
        titleCheck.failed = 1;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'page',
            err: 'ErrNoPageTitle',
            xpath: '/html/head',
            fpTempId: '0'
        });
    } else {
        const titleText = titleElement.textContent.trim();
        
        if (!titleText || titleText === '') {
            titleCheck.failed = 1;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'page',
                err: 'ErrEmptyPageTitle',
                xpath: '/html/head/title',
                fpTempId: '0'
            });
        } else if (titleText.length < 5) {
            titleCheck.failed = 1;
            errorList.push({
                url: window.location.href,
                type: 'warn',
                cat: 'page',
                err: 'WarnPageTitleTooShort',
                found: titleText,
                length: titleText.length,
                xpath: '/html/head/title',
                fpTempId: '0'
            });
        } else if (titleText.length > 60) {
            titleCheck.passed = 1; // Still passes but with warning
            errorList.push({
                url: window.location.href,
                type: 'warn',
                cat: 'page',
                err: 'WarnPageTitleTooLong',
                found: titleText,
                length: titleText.length,
                xpath: '/html/head/title',
                fpTempId: '0'
            });
            passList.push({
                check: 'page_title',
                title: titleText.substring(0, 60) + '...',
                xpath: '/html/head/title',
                wcag: ['2.4.2'],
                reason: 'Page has title (but too long)'
            });
        } else {
            titleCheck.passed = 1;
            passList.push({
                check: 'page_title',
                title: titleText,
                xpath: '/html/head/title',
                wcag: ['2.4.2'],
                reason: 'Page has descriptive title'
            });
        }
    }
    
    // Check for multiple title elements (shouldn't happen but worth checking)
    const allTitles = document.querySelectorAll('title');
    if (allTitles.length > 1) {
        errorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'page',
            err: 'WarnMultipleTitleElements',
            count: allTitles.length,
            xpath: '/html/head',
            fpTempId: '0'
        });
    }
    
    // Add check to results
    checks.push(titleCheck);
    
    return createApplicableResult('pageTitle', 1, titleCheck.passed, titleCheck.failed, errorList, passList, checks);
}'''
    
    with open('auto_a11y/scripts/tests/pageTitle.js', 'w') as f:
        f.write(content)
    print("✅ Updated pageTitle.js")

# Run all updates
if __name__ == '__main__':
    print("Updating JavaScript test files for pass tracking...")
    print("-" * 50)
    
    update_headings_js()
    update_landmarks_js()
    update_language_js()
    update_pageTitle_js()
    
    print("-" * 50)
    print("✅ All major test files updated!")
    print("\nThe updated tests now:")
    print("1. Check applicability before running")
    print("2. Track passes and failures for each check")
    print("3. Return structured data for accurate scoring")
    print("4. Support the new applicability-aware scoring system")