function jsScrape() {

    let errorList = [];

    const scriptTags = document.querySelectorAll('script');

    scriptTags.forEach(tag => {

        //const xpath = Elements.DOMPath.xPath(tag, true);

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'js',
            err: 'DiscoFoundJS',
            src: tag.textContent,
            //xpath: xpath,
            fpTempId: '0'
        });

    });

    return { errors: errorList };


}

function jsMatchElements(elements) {

    const elementList = JSON.parse(elements);
    for (let element of elementList.elements) {
        element.xpaths = new Array();
        const selector = element.selector;
        const refs = document.querySelectorAll(selector);
        refs.forEach(ref => {
            if (ref.tagName != 'BUTTON' && ref.tagName != 'button' && ref.tagName != 'A' && ref.tagName != 'a') {
                const xpath = Elements.DOMPath.xPath(ref, true);
                element.xpaths.push(xpath);
            }
        })
    }
    const result = JSON.stringify(elementList);

    return result;
}