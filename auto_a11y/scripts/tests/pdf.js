function pdfScrape() {

    let pdfList = [];

    let elements = document.querySelectorAll("a[href]");
    elements.forEach(element=>{
        const href = element.getAttribute('href');
        if (href.endsWith('.pdf')) {
            pdfList.push(href);
        }
    });

    return { pdfList: pdfList };
}
