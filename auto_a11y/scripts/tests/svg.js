function svgScrape() {

    let errorList = [];


    const svgImage = document.querySelectorAll('svg[role="image"]');
    const svgInline = document.querySelectorAll('svg[not(role="image")]');

    svgImage.forEach(img=>{

        const xpath = Elements.DOMPath.xPath(svgImage, true);

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'svg',
            err: 'DiscoFoundSvgImage',
            xpath: xpath,
            fpTempId: '0'
        });

    });


    svgImage.forEach(img=>{

        const xpath = Elements.DOMPath.xPath(svgImage, true);

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'svg',
            err: 'DiscoFoundInlineSvg',
            xpath: xpath,
            fpTempId: '0'
        });
        
    });


    return { errors: errorList };


}