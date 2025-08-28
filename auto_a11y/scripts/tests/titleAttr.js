function titleAttrScrape() {

    let errorList = [];

    let elements = document.querySelectorAll("[title]");
    elements.forEach(element => {

        const xpath = Elements.DOMPath.xPath(element, true);

        if (element.tagName !== 'IFRAME') {

            const title = element.getAttribute('title');
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'titleAttr',
                err: 'ErrTitleAttrFound',
                title: title,
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')      
            });

        }
    });

    elements = document.querySelectorAll("iframe");
    elements.forEach(element => {

        const xpath = Elements.DOMPath.xPath(element, true);

        if (!element.hasAttribute('title')) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'titleAttr',
                err: 'ErrIframeWithNoTitleAttr',
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }
        else if(element.getAttribute('title').trim() === '') {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'titleAttr',
                err: 'ErrErrEmptyTitleAttr',
                xpath: xpath,
                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                fpTempId: element.getAttribute('a11y-fpId')     
            });
        }
    });

    /*
    const body = document.querySelector('body');
    //const col =  translateColorToRGB('blue');
    const col = testContrast('#dddddd','#ffffff', body);
    errorList.push({
        url: window.location.href,
        type: 'DEBUG',
        cat: 'color',
        fg: col.fgHex,
        bg: col.bgHex,
        fontSize: col.fontSize,
        ratio: col.ratio,
        isAA: col.isAA
    });

    */

    return { errors: errorList };

}