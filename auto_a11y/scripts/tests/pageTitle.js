function pageTitleScrape() {


    const pageTitles = document.querySelectorAll('head:first-of-type title');
    let firstTitle = 'none';
    if (pageTitles) {
        if (pageTitles[0]) {
            firstTitle = pageTitles[0].textContent;
        }
    }

    return {numTitles: pageTitles.length, firstTitle: firstTitle };
}