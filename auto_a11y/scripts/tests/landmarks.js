// Counters & containers

let landmarksErrorList = [];
let landmarksList = [];

// the tem id used to identify faiure points beofre the database id is known
// Starts at 1 (preincrement) becuse 0 page
let tempIdCt = 0; 

let mainCt = 0;
let complementaryCt = 0;
let navigationCt = 0;
let regionCt = 0;
let bannerCt = 0;


let complementaryLabels = new Array();
let navigationLabels = new Array();
let regionLabels = new Array();
let bannerLabels = new Array();


let landmarkStack = new Array();
let idCount = 0;

let complementaryHasNoLabel = false;
let nodes = new Array();

let navigationHasNoLabel = false;
let headingFound = false;

let regionHasNoLabel = false;

let bannerHasNoLabel = false;

let firstHeader = document.querySelector('header:first-of-type');
let lastFooter = document.querySelector('footer:last-of-type');
let bannerFound = false;
let contentInfoFound = false;

let contentInfoCt = 0;
let contentInfoLabels = new Array();
let contentInfoHasNoLabel = false;

let formCt = 0;
let formLabels = new Array();
let formHasNoLabel = false;

let searchCt = 0;
let searchLabels = new Array();
let searchHasNoLabel = false;

// Node used to bould mode of DOM
class NodeUnderTest {
    constructor(id, parentId, nodeName, role, pr, accessibleName) {
        this.id = id;
        this.nodeName = nodeName;
        this.parentId = parentId;
        this.declaredRole = role;
        this.isPresentational = pr;
        this.accessibleName = accessibleName;
    }
}

function walkDOMandFlatten(n, parentId, isPresentational) {

    var numtags = 0;
    if (n.nodeType == 1)
        numtags++;
    var children = n.childNodes;

    ///////////////////////
    // Hande current node
    ///////////////////////

    // give this node an id if it doesn't have one
    if (n.id === undefined || n.id.trim() == "") {
        // Comment out for now
        //n.id = "a11y-" + idCount++;
    }

    let nodeType = n.nodeType;
    let elementRole;

    if (nodeType === 1 && n.hasAttribute('role')) {
        elementRole = n.getAttribute('role');
    }

    //////////////////////////////////
    // Create node
    //////////////////////////////////

    let declaredRole = null;
    if (n.nodeType === 1 && n.hasAttribute('role')) {
        declaredRole = n.getAttribute('role');
    }

    let pr = isPresentational;
    if (declaredRole === 'presentation') {
        pr = true;
    }

    /////////////////////////////////////////
    // Look for landmarks
    /////////////////////////////////////////


    if (nodeType === 1) {

        const xpath = Elements.DOMPath.xPath(n, true);
        const an = computeTextAlternative(n).name; // get a11y name
        nodes[n.id] = new NodeUnderTest(n.id, parentId, n.nodeName, declaredRole, pr, an);


        //////////////////////////////////////
        // Annotate node with parent landmark
        //////////////////////////////////////

        if (landmarkStack.length === 0) {
            // Special case of not in a landmark at all
            n.setAttribute('a11y-parentLandmark', 'none');
            n.setAttribute('a11y-fpId', '0');

        }
        else {
            // We are in a landmark

            let parentLandmark = landmarkStack.at(-1);
            n.setAttribute('a11y-fpId', parentLandmark.tempId);

            if (parentLandmark.name === 'navigation' ||
                parentLandmark.name === 'search' ||
                parentLandmark.name === 'form' ||
                parentLandmark.name === 'region'
            ) {

                // we really want to know what the top-level andmark is
                if (landmarkStack.length > 1) {
                    parentLandmark = landmarkStack[landmarkStack.length - 2];
                    const secondaryLandmark = landmarkStack.at(-1);
                    n.setAttribute('a11y-2ndParentLandmark', secondaryLandmark.name);
                    n.setAttribute('a11y-2NdParentLandmark.xpath', secondaryLandmark.xpath);
                    n.setAttribute('a11y-2ndParentLandmark.an', secondaryLandmark.an);
                }

            }

            n.setAttribute('a11y-parentLandmark', parentLandmark.name);
            n.setAttribute('a11y-parentLandmark.xpath', parentLandmark.xpath);
            n.setAttribute('a11y-parentLandmark.an', parentLandmark.an);
        }

        /////////////////////////////
        // Search for Main Landmark
        /////////////////////////////

        if (n.tagName === 'MAIN' || (n.hasAttribute('role') && n.getAttribute('role') === 'main')) {

            ++mainCt;

            if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {

                // Page - Landmarks - Main Landmark Multiply Labelled
                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'main',
                    err: 'ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                    ariaLabel: n.getAttribute('aria-label'),
                    ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (landmarkStack.length !== 0) {

                // Page - Landmarks - Main Landmark - Main Landmark cannot be nested
                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'main',
                    err: 'ErrMainLandmarkMayNotbeChildOfAnotherLandmark',
                    inside: landmarkStack.at(-1).name,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (n.hasAttribute('tabindex') && n.getAttribute('tabindex') === '0') {

                // Page - Landmarks - Main landmark has tabindex of 0
                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'main',
                    err: 'ErrMainLandmarkHasTabindexOfZeroCanOnlyHaveMinusOneAtMost',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (isHidden(n, getDefaultContext())) {

                // Landmarks - Main landmark is hidden
                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'main',
                    err: 'ErrMainLandmarkIsHidden',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }

            // Add the landmark to the stack and landmarks list
            // We have to create the object twice as push pushes a ref, not a copy)
            landmarkStack.push({ name: 'Main', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Main', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }

        //////////////////////////////////////
        // Search for Complementary Landmark
        //////////////////////////////////////

        else if (n.tagName === 'ASIDE' || (n.hasAttribute('role') && n.getAttribute('role') === 'complementary')) {
            ++complementaryCt;

            // See if the accessible name is a duplicate for other complementary landmarks
            let dup = false;
            for (let i = 0; i < complementaryLabels.length; ++i) {

                if (an.trim() == complementaryLabels[i].trim()) {

                    // duplicate label
                    dup = true;

                    // Page - Landmarks - Duplicate label for complementary landmarks
                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'complementary',
                        err: 'ErrDuplicateLabelForComplementaryLandmark',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                    break;
                }

            }

            if (!dup) {
                complementaryLabels.push(an);
            }

            if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {
q                      
                // Page - Landmarks - Complementary landmark multiply labelled                  
                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'complementary',
                    err: 'ErrComplementaryLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                    ariaLabel: n.getAttribute('aria-label'),
                    ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (landmarkStack.length !== 0) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'complementary',
                    err: 'ErrComplementaryLandmarkMayNotBeChildOfAnotherLandmark',
                    inside: landmarkStack.at(-1).name,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }
            if (!(n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby'))) {
                complementaryHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'complementary',
                    err: 'WarnComplementaryLandmarkHasNoLabel',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }
            if ((n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby')) && (an === '' || an === null || an === undefined)) {
                complementaryHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'complementary',
                    err: 'ErrComplementaryLandmarkAccessibleNameIsBlank',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (an.toLowerCase().includes('complementary')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'complementary',
                    err: 'WarnComplementaryLandmarkAccessibleNameUsesComplementary',
                    name: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }

            landmarkStack.push({ name: 'Complementary', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Complementary', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }

        //////////////////////////////////////
        // Search for Navigation Landmark
        //////////////////////////////////////

        else if (n.tagName === 'NAV' || (n.hasAttribute('role') && n.getAttribute('role') === 'navigation')) {
            ++navigationCt;

            let dup = false;
            for (let i = 0; i < navigationLabels.length; ++i) {

                if (an.trim() == navigationLabels[i].trim()) {

                    // duplicate label
                    dup = true;

                    ///////////////////////////////////////////////////////////////////
                    // MORE WORK NEEDED
                    // You can have multiple navs with the same name, 
                    // so long as they contain the same content.
                    // One eample is pagination at the top and bottom of search results
                    ////////////////////////////////////////////////////////////////////

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'navigation',
                        err: 'ErrDuplicateLabelForNavLandmark',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                    break;
                }
            }
            if (!dup) {
                navigationLabels.push(an);
            }

            if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'navigation',
                    err: 'ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                    ariaLabel: n.getAttribute('aria-label'),
                    ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (!(n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby'))) {
                navigationHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'navigation',
                    err: 'WarnNavLandmarkHasNoLabel',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if ((n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby')) && (an === '' || an === null || an === undefined)) {
                navigationHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'navigation',
                    err: 'ErrNavLandmarkAccessibleNameIsBlank',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (an.toLowerCase().includes('navigation')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'navigation',
                    err: 'WarnNavLandmarkAccessibleNameUsesNavigation',
                    name: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (n.childNodes.length == 0) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'navigation',
                    err: 'ErrCompletelyEmptyNavLandmark',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            } else if (n.textContent.trim() == '') {

                let hasElements = false;
                [...n.childNodes].forEach(node => {
                    if (n.nodeType === 1) hasElements = true;
                });
                if (!hasElements) {
                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'navigation',
                        err: 'ErrNavLandmarkContainsOnlyWhiteSpace',
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });
                }
            }

            let nestedNav = false;
            for (i = 0; i < landmarkStack.length; ++i) {

                if (landmarkStack[i].name.toLowerCase() === 'navigation') {
                    nestedNav = true;
                    break;
                }
            }
            if (nestedNav) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'navigation',
                    err: 'ErrNestedNavLandmarks',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            // Get the interactive signature of the nav element
            // Used to prove that there is interaction in the <nav>
            // Used when duplicate labels on <nav>. Identical sigs allow for this, 
            // otherwide fail.
            // TBD
            /*
            const sig = walkContainerAnfReturnInteractiveSignature(n, "");
            const children = [...n.children];
            console.log('num children: ' + children.length);
            */

            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }

            landmarkStack.push({ name: 'Navigation', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Navigation', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }
            
            landmarkStack.pop();
            headingFound = false;

        }

        //////////////////////////////////////
        // Search for Region Landmark
        //////////////////////////////////////

        else if ((n.tagName === 'SECTION' && (n.hasAttribute('aria-label') || n.hasAttribute('arial-labelledby'))) || (n.hasAttribute('role') && n.getAttribute('role') === 'region')) {
            ++regionCt;

            let dup = false;
            for (let i = 0; i < regionLabels.length; ++i) {

                if (an.trim() == regionLabels[i].trim()) {

                    // duplicate label
                    dup = true;

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'region',
                        err: 'ErrDuplicateLabelForRegionLandmark',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                    break;
                }
            }

            if (!dup) {
                regionLabels.push(an);
            }

            if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'region',
                    err: 'ErrRegionLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                    ariaLabel: n.getAttribute('aria-label'),
                    ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (!(n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby'))) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'region',
                    err: 'WarnRegionLandmarkHasNoLabelSoIsNotConsideredALandmark',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if ((n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby')) && (an.trim() === '' || an.trim() === null || an.trim() === undefined)) {
                regionHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'region',
                    err: 'RegionLandmarkAccessibleNameIsBlank',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (an.toLowerCase().includes('region')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'region',
                    err: 'WarnRegionLandmarkAccessibleNameUsesNavigation',
                    name: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }

            landmarkStack.push({ name: 'Region', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Region', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }


        //////////////////////////////////////
        // Search for Banner Landmark
        //////////////////////////////////////

        else if ((n.tagName === 'HEADER' && landmarkStack.length === 0) || (n.hasAttribute('role') && n.getAttribute('role') === 'banner')) {

            // If this is <header> then check if it is a descendant

            ++bannerCt;

            let dup = false;
            for (let i = 0; i < bannerLabels.length; ++i) {

                if (an.trim() == bannerLabels[i].trim()) {

                    // duplicate label
                    dup = true;

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'banner',
                        err: 'ErrDuplicateLabelForBannerLandmark',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                    break;
                }

            }

            if (!dup) {
                bannerLabels.push(an);
            }

            if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'banner',
                    err: 'ErrBannerLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                    ariaLabel: n.getAttribute('aria-label'),
                    ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (landmarkStack.length !== 0) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'banner',
                    err: 'ErrBannerLandmarkMayNotBeChildOfAnotherLandmark',
                    inside: landmarkStack.at(-1).name,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if ((n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby')) && (an === '' || an === null || an === undefined)) {
                bannerHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'banner',
                    err: 'ErrBannerLandmarkAccessibleNameIsBlank',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (an.toLowerCase().includes('banner')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'banner',
                    err: 'WarnBannerLandmarkAccessibleNameUsesBanner',
                    name: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }


            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }

            landmarkStack.push({ name: 'Banner', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Banner', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length
                ; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }

        // FOOTER

        else if ((n.tagName === 'FOOTER' && landmarkStack.length === 0) || (n.hasAttribute('role') && n.getAttribute('role') === 'contentinfo')) {
            ++contentInfoCt;

            let dup = false;
            for (let i = 0; i < contentInfoLabels.length; ++i) {

                if (an.trim() == contentInfoLabels[i].trim()) {

                    // duplicate label
                    dup = true;

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'contentinfo',
                        err: 'ErrDuplicateLabelForContentinfoLandmark',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                    break;
                }

            }

            if (!dup) {
                contentInfoLabels.push(an);
            }

            if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'contentinfo',
                    err: 'ErrContentInfoLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                    ariaLabel: n.getAttribute('aria-label'),
                    ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (landmarkStack.length !== 0) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'contentinfo',
                    err: 'ErrContentinfoLandmarkMayNotBeChildOfAnotherLandmark',
                    inside: landmarkStack.at(-1).name,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });
            }

            if (!(n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby'))) {
                contentInfoHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'contentinfo',
                    err: 'WarnContentInfoLandmarkHasNoLabel',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if ((n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby')) && (an === '' || an === null || an === undefined)) {
                contentInfoHasNoLabel = true;

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    landmark: 'contentinfo',
                    err: 'ErrContentInfoLandmarkAccessibleNameIsBlank',
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }

            if (an.includes('contentinfo')) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'contentinfo',
                    err: 'WarnContentinfoLandmarkAccessibleNameUsesContentinfo',
                    name: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }


            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }

            landmarkStack.push({ name: 'ContentInfo', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'ContentInfo', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }

        //// FORM

        else if ((n.tagName === 'FORM') || (n.hasAttribute('role') && n.getAttribute('role') === 'form')) {
            ++formCt;

            // Not technically a landmark if it doesn't have a label
            if (!(n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby') || n.hasAttribute('title'))) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'warn',
                    cat: 'landmark',
                    landmark: 'form',
                    err: 'WarnFormHasNoLabelSoIsNotLandmark',
                    name: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                });

            }
            else {
                // Form has a label and can be classified as a landmark

                let dup = false;
                for (let i = 0; i < formLabels.length; ++i) {

                    if (an.trim() == formLabels[i].trim()) {

                        // duplicate label
                        dup = true;

                        landmarksErrorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'landmark',
                            landmark: 'form',
                            err: 'ErrDuplicateLabelForFormLandmark',
                            found: an,
                            xpath: xpath,
                            fpTempId: n.getAttribute('a11y-fpId')
                        });

                        break;
                    }
                }

                if (!dup) {
                    formLabels.push(an);
                }

                // ARIA Authorin Practices reques not only that the form is labelled, but that the label is available to everyone i.e. H1-H6 only
                if (n.hasAttribute('aria-label')) {

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'form',
                        err: 'ErrFormUsesAriaLabelInsteadOfVisibleElement',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                }

                if (n.hasAttribute('title')) {

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'form',
                        err: 'ErrFormUsesTitleAttribute',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });
                }

                if (n.hasAttribute('aria-labelledby')) {
                    // test if it is labelled by a (visible) headig
                    let labelId = n.getAttribute('aria-labelledby');

                    if (labelId === '' || labelId === null || labelId === undefined) {

                        landmarksErrorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'landmark',
                            landmark: 'form',
                            err: 'ErrFormAriaLabelledByIsBlank',
                            found: an,
                            xpath: xpath,
                            fpTempId: n.getAttribute('a11y-fpId')
                        });

                    }
                    else {
                        // we have a label Id, but is it to a heading?
                        let referencedNode = document.querySelector('#' + labelId);

                        if (referencedNode === null) {


                            landmarksErrorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'landmark',
                                landmark: 'form',
                                err: 'ErrFormAriaLabelledByReferenceDoesNotExist',
                                referenced: labelId,
                                xpath: xpath,
                                fpTempId: n.getAttribute('a11y-fpId')
                            });

                        }
                        else {
                            // Valid ref, but what is it?)
                            if (!(referencedNode.tagName === 'H1' || referencedNode.tagName === 'H2' || referencedNode.tagName === 'H3' || referencedNode.tagName === 'H4' || referencedNode.tagName === 'H5' || referencedNode.tagName === 'H6'
                                || (referencedNode.hasAttribute("role") && referencedNode.getAttribute('role') === 'heading'))) {

                                landmarksErrorList.push({
                                    url: window.location.href,
                                    type: 'err',
                                    cat: 'landmark',
                                    landmark: 'form',
                                    err: 'ErrFormAriaLabelledByReferenceDoesNotReferenceAHeading',
                                    referenced: labelId,
                                    xpath: xpath,
                                    fpTempId: n.getAttribute('a11y-fpId')
                                });

                            }
                            else {
                                // We have a heading but is it visible?
                                if (isHidden(referencedNode)) {

                                    landmarksErrorList.push({
                                        url: window.location.href,
                                        type: 'err',
                                        cat: 'landmark',
                                        landmark: 'form',
                                        err: 'ErrFormAriaLabelledByReferenceDIsHidden',
                                        referenced: labelId,
                                        xpath: xpath,
                                        fpTempId: n.getAttribute('a11y-fpId')
                                    });

                                }
                            }
                        }
                    }
                }

                if (n.hasAttribute('aria-label') && n.hasAttribute('aria-labelledby')) {

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'form',
                        err: 'ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs',
                        ariaLabel: n.getAttribute('aria-label'),
                        ariaLabelledBy: n.getAttribute('aria-labelledBy'),
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                }

                if ((n.hasAttribute('aria-label') || n.hasAttribute('aria-labelledby')) && (an === '' || an === null || an === undefined)) {
                    formHasNoLabel = true;

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'form',
                        err: 'ErrFormLandmarkAccessibleNameIsBlank',
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                }

                if (an.includes('form')) {

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'landmark',
                        landmark: 'form',
                        err: 'WarnFormLandmarkAccessibleNameUsesForm',
                        name: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                }
            }

            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }
            landmarkStack.push({ name: 'Form', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Form', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });
           
            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }


        ///////// SEARCH ////////////////
        else if ((n.tagName === 'SEARCH') || (n.hasAttribute('role') && n.getAttribute('role') === 'search')) {
            ++searchCt;

            let dup = false;
            for (let i = 0; i < searchLabels.length; ++i) {

                if (an.trim() == searchLabels[i].trim()) {

                    // duplicate label
                    dup = true;

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'landmark',
                        landmark: 'form',
                        err: 'ErrDuplicateLabelForSearchLandmark',
                        found: an,
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                    break;
                }

            }

            if (!dup) {
                searchLabels.push(an);
            }

            let noLabelledBy = false;
            let labelledBy = '';
            if (n.hasAttribute('aria-labelledby')) {
                noLabelledBy = false;
                labelledBy = n.getAttribute('aria-labelledby');
            }
            else {
                noLabelledBy = true;
            }
            landmarkStack.push({ name: 'Search', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: ++tempIdCt });
            landmarksList.push({ name: 'Search', parentLandmark: 'n/a', an: an, xpath: xpath, node: n, noLabelledBy: noLabelledBy, labelledBy: labelledBy, tempId: tempIdCt });

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

            landmarkStack.pop();
            headingFound = false;

        }

        else {

            ///////////////////////////
            // Not a landmark
            ///////////////////////////

            // All content should be inside landmarks
            if (landmarkStack.length === 0) {

                landmarksErrorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'landmark',
                    err: 'ErrElementNotContainedInALandmark',
                    tagName: n.tagName,
                    an: an,
                    xpath: xpath,
                    fpTempId: n.getAttribute('a11y-fpId')
                })
            }

            const myChildren = n.childNodes;
            for (var i = 0; i < myChildren.length; i++) {
                numtags += walkDOMandFlatten(myChildren[i], n.id, pr);
            }

        }

        if (n.tagName === 'H1' || n.tagName === 'H2' || n.tagName === 'H3' || n.tagName === 'H4' || n.tagName === 'H5' || n.tagName === 'H6'
            || (n.hasAttribute("role") && n.getAttribute('role') === 'heading')) {

            if (!headingFound && landmarkStack.length !== 0) {
                headingFound = true;

                let currentLandmark = landmarkStack.at(-1);
                if (currentLandmark.noLabelledBy && currentLandmark.name.toLowerCase() !== 'main') {
                    // Note, we dont bother to announce this for <main> as it is not usual to label main

                    landmarksErrorList.push({
                        url: window.location.href,
                        type: 'warn',
                        cat: 'landmark',
                        landmark: currentLandmark.name,
                        err: 'WarnHeadingFoundInsideLandmarkButDoesntLabelLandmark',
                        found: an,
                        noLabelledBy: currentLandmark.noLabelledBy,
                        labelledBy: currentLandmark.labelledBy,
                        currentName: currentLandmark.name.toLowerCase(),
                        xpath: xpath,
                        fpTempId: n.getAttribute('a11y-fpId')
                    });

                }

                else if (currentLandmark.labelledBy !== '') {

                    let headingId = n.id;
                    if (currentLandmark.labelledBy !== n.id) {

                        landmarksErrorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'landmark',
                            landmark: currentLandmark.name,
                            err: 'WarnHeadingFoundInLandmarkButIsLabelledByAnAriaLabelledBy',
                            labelRef: currentLandmark.labelledBy,
                            found: an,
                            xpath: xpath,
                            fpTempId: n.getAttribute('a11y-fpId')
                        });
                    }
                }
            }
        }


    }


    ////////////////////////////////////////
    // Continue to walk DOM
    ////////////////////////////////////////

    /*
    for (var i = 0; i < children.length; i++) {
        numtags += walkDOMandFlatten(children[i], n.id, pr);
    }
    */

    // reset current landmark before moving to sibling/parent
    /*
    if (nodeType === 1) {
        landmarkStack.pop();
        headingFound = false;
    }
     */

}



function landmarksScrape() {

    walkDOMandFlatten(document.querySelector('body:first-of-type'), null, false);

    /*
    const topNodes = document.querySelectorAll('body');
    topNodes.forEach(node => {
        walkDOMandFlatten(node, null, false);
    });
    */

    ////////////////////////////////////////////////////////
    // Report final landmark tickets (based on counters)
    ////////////////////////////////////////////////////////

    if (mainCt < 1) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            landmark: 'main',
            err: 'ErrNoMainLandmarkOnPage',
            fpTempId: '0'
        });

    } else if (mainCt > 1) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            landmark: 'main',
            err: 'ErrMultipleMainLandmarksOnPage',
            found: mainCt,
            fpTempId: '0'
        });

    }

    if (complementaryCt > 1 && complementaryHasNoLabel) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'complementary',
            err: 'WarnMultipleComplementaryLandmarksButNotAllHaveLabels',
            fpTempId: '0'
        });

    }

    if (navigationCt > 1 && navigationHasNoLabel) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'navigation',
            err: 'WarnMultipleNavLandmarksButNotAllHaveLabels',
            fpTempId: '0'
        });

    }

    if (regionCt > 1 && regionHasNoLabel) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'region',
            err: 'WarnMultipleRegionLandmarksButNotAllHaveLabels',
            fpTempId: '0'
        });

    }


    if (navigationCt < 1) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'navigation',
            err: 'WarnNoNavLandmarksOnPage',
            fpTempId: '0'
        });

    }

    if (bannerCt == 0) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            landmark: 'banner',
            err: 'ErrNoBannerLandmarkOnPage',
            fpTempId: '0'
        });

    } else if (bannerCt > 1) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            landmark: 'banner',
            err: 'ErrMultipleBannerLandmarksOnPage',
            found: bannerCt,
            fpTempId: '0'
        });

    }

    if (bannerCt > 1 && bannerHasNoLabel) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'banner',
            err: 'WarnMultipleBannerLandmarksButNotAllHaveLabels',
            fpTempId: '0'
        });

    }

    if (contentInfoCt == 0) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'contentinfo',
            err: 'WarnNoContentinfoLandmarkOnPage',
            fpTempId: '0'
        });

    } else if (contentInfoCt > 1) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'landmark',
            landmark: 'contentinfo',
            err: 'ErrMultipleContentinfoLandmarksOnPage',
            found: contentInfoCt,
            fpTempId: '0'
        });

    }

    if (contentInfoCt > 1 && contentInfoHasNoLabel) {

        landmarksErrorList.push({
            url: window.location.href,
            type: 'warn',
            cat: 'landmark',
            landmark: 'contentinfo',
            err: 'WarnMultipleContentInfoLandmarksButNotAllHaveLabels',
            fpTempId: '0'
        });
    }

    return { errors: landmarksErrorList, landmarksList: landmarksList };

}

function walkContainerAndReturnInteractiveSignature(node, currentSignature) {

}