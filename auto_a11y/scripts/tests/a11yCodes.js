const ERR = 0;
const WARN = 1;

class A11yCodes {
    static Headings = {
        HEADINGS_DONT_START_WITH_H1: { code:ERR, txt:"Heading levels do not start with an H1"},
        HEADING_LEVELS_SKIPPED: { code:ERR, txt:"Heading level skipped"},
        EMPTY_HEADING: { code:ERR, txt:"Empty heading"},
        HEADING_QUITE_LONG: { code:WARN, txt:'Heading is quite long'},
        VISIBLE_HEADING_DOESNT_MATCH_A11Y_NAME: { code:ERR, txt:"Visible heading does not match accessible name"},
        ROLE_OF_HEADING_BUT_NO_LEVEL: { code:ERR, txt:'Role of "heading" found but no aria-level attribute provided'},
        INVALID_ARIA_LEVEL: { code:ERR, txt:"Invalid aria-level"},
        LEVEL_ATTR_BUT_ROLE_NOT_HEADING: { code:ERR, txt:"aria-level attribute found but role is not heading"},
        LEVEL_ATTR_BUT_ROLE_NO_ROLE_APPLIED_AT_ALL: { code:ERR, txt:"aria-level attribute found but role is not applied at all"},
        NO_HEADINGS_ON_PAGE: { code:ERR, txt: 'No Heading levels found on page'},
        NO_H1_ON_PAGE: { code:ERR, txt:"No H1 heading on page"},
        MULTIPLE_H1_ON_PAGE: { code:ERR, txt:"Multiple H1 headings on page"},
        DISPLAY_NONE_HEADING_FOUND_MAY_BE_IN_MODAL: { code:WARN, txt:"A heading that is currently display:none found. May be in a modal"}
    }

    static Text = {
        NO_PRIMARY_LANG_ATTR: { code:ERR, txt:"No primary language attribute for page"},
        PRIMARY_LANG_UNRECOGNIZED: { code:ERR, txt:"Primary language of page is unrecognized"},
        PRIMARY_XML_LANG_UNRECOGNIZED: { code:ERR, txt:"Primary XML language of page is unrecognized"},
        PRIMARY_LANG_AND_XML_LANG_DONT_MATCH: { code:ERR, txt:"Primary lang and XML lang don't match"},
        REGION_QUALIFIFIER_FOR_PRIMARY_LANG_NOT_RECOGNIZED: { code:ERR, txt:"Region qualifier for primary lang not recognized"},
        REGION_QUALIFIFIER_FOR_PRIMARY_XML_LANG_NOT_RECOGNIZED: { code:ERR, txt:"Region qualifier for primary  xml lang not recognized"},
        EMPTY_LANG_ATTR: { code:ERR, txt:"Empty lang attribute"},
        EMPTY_XML_LANG_ATTR: { code:ERR, txt:"Empty xml:lang attribute"},
        INCORRECTLY_FORMATTED_PRIMARY_LANG: { code:ERR, txt:"Incorrectly formatted primary lang"},

        ELEMENT_PRIMARY_LANG_NOT_RECOGNIZED: { code:ERR, txt:"Element primary lang attribute unrecognized"},
        ELEMENT_LANG_EMPTY: { code:ERR, txt:"Element lang attribute is empty"},
        ELEMENT_REGION_QUALIFIER_NOT_RECOGNIZED: { code:ERR, txt:"Region qualifier for element lang attribute not recognized"},

        PRIMARY_HREFLANG_NOT_RECOGNIZED: { code:ERR, txt:"Primary hreflang not recognized"},
        HREF_LANG_ATTR_EMPTY: { code:ERR, txt:"hreflang attr is empty"},
        REGION_QUALIFIER_FOR_HREFLANG_NOT_RECOGNIZED: { code:ERR, txt:"Region qualifier for hreflang not recognized"},
        HREFLANG_NOT_ON_A_LINK: { code:ERR, txt:"The hreflang is not on a link"}
    }
}