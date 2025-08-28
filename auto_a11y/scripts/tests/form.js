function formScrape() {

    let errorList = [];

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
            err: 'DiscoFormPage',
            xpath: formXpath
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
                xpath: formXpath
            });
        }

        if (element.childNodes.length === 0) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'form',
                err: 'ErrFormEmptyHasNoChildNodes',
                xpath: formXpath
            });
        }

        let labelList = [];
        const labels = element.querySelectorAll('label');
        labels.forEach(label => {

            const labelXpath = Elements.DOMPath.xPath(element, true);

            const lan = getAccessibleName(label);
            const labelText = label.textContent;

            if (lan.trim() !== labelText.trim()) {
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'form',
                    err: 'ErrLabelMismatchOfAccessibleNameAndLabelText',
                    acessibleName: lan,
                    text: labelText,
                    xpath: labelXpath
                });
            }

            // Deal with labels can contain fields
            let fieldCt = 0;
            let childrenOfLabelNode = []
            label.childNodes.forEach(childOfLabel => {
                if (htmlInteractiveElements.includes(childOfLabel.tagName.toLowerCase()) || (childOfLabel.hasAttribute('role') & ariaWidgetRoles.includes(childOfLabel.getAttribute('role')))) {
                    // interactive field is a child of label
                    ++fieldCt
                    childrenOfLabelNode.push(childOfLabel);
                }
            });


            if (childrenOfLabelNode.length > 1) {
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'form',
                    err: 'ErrLabelContainsMultipleFields',
                    found: childrenOfLabelNode.length,
                    xpath: labelXpath
                });
            }
            else if (childrenOfLabelNode.length === 1) {
                // field labelled by containing label
                const labelChildXpath = Elements.DOMPath.xPath(childrenOfLabelNode[0], true);
                labelList.push({ label: labelXpath, labelChildXpath, labelUsed: true, labelEnc: true });
            }
            else {
                // Label does not contain field, so it must be referened by it

                // Label must have an id to reference, othewise it is an orphan label
                if (label.id === '' || label.id === null) {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'form',
                        err: 'ErrOrphanLabelWithNoId',
                        xpath: labelXpath
                    });
                }
                else {
                    // Add to list as an unused label to test against later
                    const labelChildXpath = Elements.DOMPath.xPath(childrenOfLabelNode[0], true);
                    labelList.push({ label: labelXpath, labelChildXpath, labelUsed: false, labelEnc: false });
                }
            }
        });

        let interactiveCt = 0;
        element.childNodes.forEach(n => {
            if (n.nodeType === 1) {

                const childNodeXpath = Elements.DOMPath.xPath(n, true);

                if (htmlInteractiveElements.includes(n.tagName.toLowerCase()) || (n.hasAttribute('role') & ariaWidgetRoles.includes(n.getAttribute('role')))) {
                    // we have an interactive element

                    ++interactiveCt;

                    if (n.hasAttribute('tabindex') && n.getAttribute('tabindex') !== 0) {
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'form',
                            err: 'ErrWrongTabindexForInteractiveElement',
                            found: n.getAttribute('tabindex'),
                            xpath: childNodeXpath
                        });
                    }

                    // Must have a label, check first if it is enclosed by a label
                    let isEnc = false;
                    for (let i = 0; i < labelList.length; ++i) {
                        const labelXpath = Elements.DOMPath.xPath(labelList[i].label, true);
                        if (labelList[i].labelChildXpath === childNodeXpath) {
                            if (labelList[i].labelEnc) {
                                isEnc = true;
                                break;
                            }
                        }
                    }

                    if (!isEnc) {
                        // Not enclosed, so must get its label from aria-label or aria-labelledBy
                        if (!(n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledBy'))) {
                            errorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'form',
                                err: 'ErrUnlabelledField',
                                xpath: childNodeXpath
                            });
                        }
                        else {
                            // test for aria-label
                            if (n.hasAttribute('aria-label')) {

                                errorList.push({
                                    url: window.location.href,
                                    type: 'err',
                                    cat: 'form',
                                    err: 'ErrAriaLabelMayNotBeFoundByVoiceControl',
                                    xpath: childNodeXpath
                                });

                                // empty aria-label
                                const aLabel = n.getAttribute('aria-label').trim();
                                if (aLabel === '' || aLabel === null) {
                                    errorList.push({
                                        url: window.location.href,
                                        type: 'err',
                                        cat: 'form',
                                        err: 'ErrEmptyAriaLabelOnField',
                                        xpath: childNodeXpath
                                    });
                                }
                            }
                            else {
                                // test for empty aria-labelledby

                                const aLabel = n.getAttribute('aria-labelledby').trim();
                                if (aLabel === '' || aLabel === null) {
                                    errorList.push({
                                        url: window.location.href,
                                        type: 'err',
                                        cat: 'form',
                                        err: 'ErrEmptyAriaLabelledByOnField',
                                        xpath: childNodeXpath
                                    });
                                }

                                // Must be labelled by exactly one label

                                const aLabels = aLabel.split(' ');
                                if (aLabels.length > 1) {
                                    errorList.push({
                                        url: window.location.href,
                                        type: 'warn',
                                        cat: 'form',
                                        err: 'WarnFieldLabelledByMulitpleElements', // could confuse voice control
                                        xpath: childNodeXpath
                                    });
                                }
                                else {

                                    // referenced item must exist
                                    const refItem = document.querySelector(aLabel);
                                    if (refItem === null) {
                                        errorList.push({
                                            url: window.location.href,
                                            type: 'err',
                                            cat: 'form',
                                            err: 'ErrFieldReferenceDoesNotExist',
                                            xpath: childNodeXpath
                                        });
                                    }
                                    else {
                                        // Referenced item must be a label
                                        if (refItem.tagName !== 'LABEL') {
                                            errorList.push({
                                                url: window.location.href,
                                                type: 'err',
                                                cat: 'form',
                                                err: 'ErrFielLabelledBySomethingNotALabel',
                                                refId: aLabel,
                                                xpath: childNodeXpath
                                            });
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        });

        if (interactiveCt === 0) {
            errorList.push({
                url: window.location.href,
                type: 'Err',
                cat: 'form',
                err: 'ErrFormEmptyHasNoInteractiveElements',
                xpath: xpath
            });
        }

    });


    return { errors: errorList };
}
