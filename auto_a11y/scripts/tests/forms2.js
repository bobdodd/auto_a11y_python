function walkDomToFindInteractiveNodes(n, nodeList) {

    if (n.nodeType == 1) {
        if (htmlInteractiveElements.includes(n.tagName.toLowerCase()) || (n.hasAttribute('role') & ariaWidgetRoles.includes(n.getAttribute('role')))) {
            nodeList.push(n);

        }

        n.childNodes.forEach(child => {
            walkDomToFindInteractiveNodes(child, nodeList);
        })
    }

    return nodeList;
}

function formScrape() {

    let errorList = [];

    let fieldsList = [];
    let labelsList = [];

    const elements = document.querySelectorAll('form');
    elements.forEach(element => {

        const formXpath = Elements.DOMPath.xPath(element, true);

        //////////////////////////////////////
        // Report a form on the page
        //////////////////////////////////////

        errorList.push({
            url: window.location.href,
            type: 'disco',
            cat: 'form',
            err: 'DiscoFormOnPage',
            xpath: formXpath,
            fpTempId: '0'
        });

        ///////////////////////////////////////
        // Form has no label
        ///////////////////////////////////////
        if (!(element.hasAttribute('aria-label') || element.hasAttribute('aria-labelledby'))) {

            errorList.push({
                url: window.location.href,
                type: 'warn',
                cat: 'form',
                err: 'WarnFormHasNoLabel',
                xpath: formXpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }

        if (element.childNodes.length === 0) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'form',
                err: 'ErrFormEmptyHasNoChildNodes',
                xpath: formXpath,
                fpTempId: element.getAttribute('a11y-fpId')
            });
        }

        ///////////////////////////////////////////////
        // Deal with labels and how they map to fields
        ///////////////////////////////////////////////

        const fieldsList = walkDomToFindInteractiveNodes(element, []);
        const labelsList = element.querySelectorAll('label');

        let utilizedLabels = [];
        let utilizedFields = [];

        // We now have a list of fields and labels
        // See which fields are labelled

        // By aria-label
        fieldsList.forEach(field => {
            const fieldXpath = Elements.DOMPath.xPath(field, true);

            if (field.hasAttribute('aria-label') || field.hasAttribute('aria-labelledby')) {
                // we say field is lebelled, even if the label is broken
                utilizedFields.push(field);

                if (field.hasAttribute('aria-label')) {

                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'form',
                        err: 'ErrFieldLabelledUsinAriaLabel',
                        xpath: fieldXpath,
                        found: field.getAttribute('aria-label'),
                        fpTempId: field.getAttribute('a11y-fpId')
                    });
                }

                else if (field.hasAttribute('aria-labelledby')) {

                    const refId = field.getAttribute('aria-labelledby');
                    const refElement = document.getElementById(refId);

                    if (refElement === null) {

                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'form',
                            err: 'ErrFieldAriaRefDoesNotExist',
                            xpath: fieldXpath,
                            found: refId,
                            fpTempId: field.getAttribute('a11y-fpId')
                        });

                    }
                    else {

                        if (refElement.tagName !== 'LABEL') {

                            errorList.push({
                                url: window.location.href,
                                type: 'warn',
                                cat: 'form',
                                err: 'WarnFieldLabelledByElementThatIsNotALabel',
                                xpath: fieldXpath,
                                found: refId,
                                tag: refElement.tagName,
                                fpTempId: field.getAttribute('a11y-fpId')
                            });

                        }
                        else {
                            utilizedLabels.push(refElement);
                        }
                    }

                }

            }
        });

        // By containment in label
        labelsList.forEach(label => {
            label.childNodes.forEach(childOfLabel => {
                if (childOfLabel.nodeType === 1) {
                    
                    if (htmlInteractiveElements.includes(childOfLabel.tagName.toLowerCase()) || (childOfLabel.hasAttribute('role') & ariaWidgetRoles.includes(childOfLabel.getAttribute('role')))) {
                        // Is interacive node           

                        const fieldXpath = Elements.DOMPath.xPath(childOfLabel, true);
                        for (let i = 0; i < fieldsList.length; ++i) {
                            const fieldsListXpath = Elements.DOMPath.xPath(fieldsList[i], true);
                            if (fieldXpath === fieldsListXpath) {
                                utilizedFields.push(childOfLabel);
                                if (!utilizedLabels.includes(label)) {
                                    utilizedLabels.push(label);
                                }
                                break;
                            }
                        }
                        
                    }
                    
                }
            });
        });


        // By reference from a label
        const references = document.querySelectorAll('label[for]');
        references.forEach(ref => {
            const refId = ref.getAttribute('for');
            const referredField = document.getElementById(ref);
        
            if (referredField !== null) {
                // refs a valid element

                const refFieldXpath = elements.DOMPath.xPath(referredField, true);

                for (let i = 0; i < fieldsList.length; ++i) {
                    const fieldsListXpath = elements.DOMPath.xPath(fieldsList[i], true);
                    if (refFieldXpath === fieldsListXpath) {
                        utilizedFields.push(referredField);
                        if (!utilizedLabels.includes(label)) {
                            utilizedLabels.push(label);
                        }
                        break;
                    }
                }
            }
        });


        // Find unlabelled fields
        fieldsList.forEach(field=>{
            if (!(field in utilizedFields)) {

                const fieldXpth = Elements.DOMPath.xPath(field, true);

                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'form',
                    err: 'ErrUnlabelledField',
                    xpath: fieldXpth,
                    fpTempId: field.getAttribute('a11y-fpId')
                });
        
            }
        })

    });


    return { errors: errorList };
}
