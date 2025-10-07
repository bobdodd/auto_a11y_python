function languageScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];
    
    // Language is always applicable - all pages need language declaration
    let langCheck = initializeCheck('page_language', 'Page has language declaration', ['3.1.1']);
    
    const htmlElement = document.querySelector('html');
    langCheck.total = 1;
    
    if (!htmlElement || !htmlElement.hasAttribute('lang')) {
        langCheck.failed = 1;
        // Capture the opening tag of the html element
        const htmlTag = htmlElement ? htmlElement.outerHTML.split('>')[0] + '>' : '<html>';
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'language',
            err: 'ErrNoPageLanguage',
            xpath: '/html',
            html: htmlTag,
            fpTempId: '0'
        });
    } else {
        const lang = htmlElement.getAttribute('lang');
        
        // Check if language code is valid (basic check for format)
        if (!lang || lang.trim() === '') {
            langCheck.failed = 1;
            const htmlTag = htmlElement.outerHTML.split('>')[0] + '>';
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'language',
                err: 'ErrEmptyLanguageAttribute',
                xpath: '/html',
                html: htmlTag,
                fpTempId: '0'
            });
        } else if (!/^[a-z]{2}(-[A-Z]{2})?$/.test(lang)) {
            langCheck.failed = 1;
            const htmlTag = htmlElement.outerHTML.split('>')[0] + '>';
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'language',
                err: 'ErrInvalidLanguageCode',
                found: lang,
                xpath: '/html',
                html: htmlTag,
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
}