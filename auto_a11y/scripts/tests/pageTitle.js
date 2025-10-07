function pageTitleScrape() {
    let errorList = [];
    let passList = [];
    let checks = [];

    // Get title length limit from config, default to 60
    const titleLengthLimit = (window.a11yConfig && window.a11yConfig.titleLengthLimit) || 60;

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
        } else if (titleText.length > titleLengthLimit) {
            titleCheck.passed = 1; // Still passes but with warning
            errorList.push({
                url: window.location.href,
                type: 'warn',
                cat: 'page',
                err: 'WarnPageTitleTooLong',
                found: titleText,
                length: titleText.length,
                limit: titleLengthLimit,
                xpath: '/html/head/title',
                fpTempId: '0'
            });
            passList.push({
                check: 'page_title',
                title: titleText.substring(0, titleLengthLimit) + '...',
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
}