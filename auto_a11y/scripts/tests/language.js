const LANGUAGE_CODES = {
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'an': 'Aragonese',
    'ar': 'Arabic (Standard)',
    'ar-DZ': 'Arabic (Algeria)',
    'ar-BH': 'Arabic (Bahrain)',
    'ar-EG': 'Arabic (Egypt)',
    'ar-IQ': 'Arabic (Iraq)',
    'ar-JO': 'Arabic (Jordan)',
    'ar-KW': 'Arabic (Kuwait)',
    'ar-LB': 'Arabic (Lebanon)',
    'ar-LY': 'Arabic (Libya)',
    'ar-MA': 'Arabic (Morocco)',
    'ar-OM': 'Arabic (Oman)',
    'ar-QA': 'Arabic (Qatar)',
    'ar-SA': 'Arabic (Saudi Arabia)',
    'ar-SY': 'Arabic (Syria)',
    'ar-TN': 'Arabic (Tunisia)',
    'ar-AE': 'Arabic (U.A.E.)',
    'ar-YE': 'Arabic (Yemen)',
    'hy': 'Armenian',
    'as': 'Assamese',
    'ast': 'Asturian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'br': 'Breton',
    'bg': 'Bulgarian',
    'my': 'Burmese',
    'ca': 'Catalan',
    'ch': 'Chamorro',
    'ce': 'Chechen',
    'zh': 'Chinese',
    'zh-HK': 'Chinese (Hong Kong)',
    'zh-CN': 'Chinese (PRC)',
    'zh-SG': 'Chinese (Singapore)',
    'zh-TW': 'Chinese (Taiwan)',
    'cv': 'Chuvash',
    'co': 'Corsican',
    'cr': 'Cree',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch (Standard)',
    'nl-BE': 'Dutch (Belgian)',
    'en': 'English',
    'en-AU': 'English (Australia)',
    'en-BZ': 'English (Belize)',
    'en-CA': 'English (Canada)',
    'en-IE': 'English (Ireland)',
    'en-JM': 'English (Jamaica)',
    'en-NZ': 'English (New Zealand)',
    'en-PH': 'English (Philippines)',
    'en-ZA': 'English (South Africa)',
    'en-TT': 'English (Trinidad & Tobago)',
    'en-GB': 'English (United Kingdom)',
    'en-US': 'English (United States)',
    'en-ZW': 'English (Zimbabwe)',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'fo': 'Faeroese',
    'fj': 'Fijian',
    'fi': 'Finnish',
    'fr': 'French (Standard)',
    'fr-BE': 'French (Belgium)',
    'fr-CA': 'French (Canada)',
    'fr-FR': 'French (France)',
    'fr-LU': 'French (Luxembourg)',
    'fr-MC': 'French (Monaco)',
    'fr-CH': 'French (Switzerland)',
    'fy': 'Frisian',
    'fur': 'Friulian',
    'gd': 'Gaelic (Scots)',
    'gd-ie': 'Gaelic (Irish)',
    'gl': 'Galacian',
    'ka': 'Georgian',
    'de': 'German (Standard)',
    'de-AT': 'German (Austria)',
    'de-DE': 'German (Germany)',
    'de-LI': 'German (Liechtenstein)',
    'de-LU': 'German (Luxembourg)',
    'de-CH': 'German (Switzerland)',
    'el': 'Greek',
    'gu': 'Gujurati',
    'ht': 'Haitian',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'id': 'Indonesian',
    'iu': 'Inuktitut',
    'ga': 'Irish',
    'it': 'Italian (Standard)',
    'it-CH': 'Italian (Switzerland)',
    'ja': 'Japanese',
    'kn': 'Kannada',
    'ks': 'Kashmiri',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'ky': 'Kirghiz',
    'tlh': 'Klingon',
    'ko': 'Korean',
    'ko-KP': 'Korean (North Korea)',
    'ko-KR': 'Korean (South Korea)',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'FYRO Macedonian',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mo': 'Moldavian',
    'nv': 'Navajo',
    'ng': 'Ndonga',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'nb': 'Norwegian (Bokmal)',
    'nn': 'Norwegian (Nynorsk)',
    'oc': 'Occitan',
    'or': 'Oriya',
    'om': 'Oromo',
    'fa': 'Persian',
    'fa-IR': 'Persian/Iran',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pt-BR': 'Portuguese (Brazil)',
    'pa': 'Punjabi',
    'pa-IN': 'Punjabi (India)',
    'pa-PK': 'Punjabi (Pakistan)',
    'qu': 'Quechua',
    'rm': 'Rhaeto-Romanic',
    'ro': 'Romanian',
    'ro-MO': 'Romanian (Moldavia)',
    'ru': 'Russian',
    'ru-MO': 'Russian (Moldavia)',
    'sz': 'Sami (Lappish)',
    'sg': 'Sango',
    'sa': 'Sanskrit',
    'sc': 'Sardinian',
    'sd': 'Sindhi',
    'si': 'Singhalese',
    'sr': 'Serbian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somani',
    'sb': 'Sorbian',
    'es': 'Spanish',
    'es-AR': 'Spanish (Argentina)',
    'es-BO': 'Spanish (Bolivia)',
    'es-CL': 'Spanish (Chile)',
    'es-CO': 'Spanish (Colombia)',
    'es-CR': 'Spanish (Costa Rica)',
    'es-DO': 'Spanish (Dominican Republic)',
    'es-EC': 'Spanish (Ecuador)',
    'es-SV': 'Spanish (El Salvador)',
    'es-GT': 'Spanish (Guatemala)',
    'es-HM': 'Spanish (Honduras)',
    'es-MX': 'Spanish (Mexico)',
    'es-NI': 'Spanish (Nicaragua)',
    'es-PA': 'Spanish (Panama)',
    'es-PY': 'Spanish (Paraguay)',
    'es-PE': 'Spanish (Peru)',
    'es-PR': 'Spanish (Puerto Rico)',
    'es-ES': 'Spanish (Spain)',
    'es-UY': 'Spanish (Uruguay)',
    'es-VE': 'Spanish (Venezuela)',
    'sx': 'Sutu',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'sv-FI': 'Swedish (Finland)',
    'sv-SV': 'Swedish (Sweden)',
    'ta': 'Tamil',
    'tt': 'Tatar',
    'te': 'Teluga',
    'th': 'Thai',
    'tig': 'Tigre',
    'ts': 'Tsonga',
    'tn': 'Tswana',
    'tr': 'Turkish',
    'tk': 'Turkmen',
    'uk': 'Ukrainian',
    'hsb': 'Upper Sorbian',
    'ur': 'Urdu',
    've': 'Venda',
    'vi': 'Vietnamese',
    'vo': 'Volapuk',
    'wa': 'Walloon',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'ji': 'Yiddish',
    'zu': 'Zulu',
};
// Tested according to https://www.w3.org/WAI/WCAG21/Understanding/language-of-page.html#test-rules

function languageScrape() {

    let errorList = [];
    let warningList = [];


    /////////////////////////////////////
    // Language of Page
    ////////////////////////////////////

    let lang = null;
    let xmlLang = null;
    let PrimaryLangHasError = false;
    let primaryXmlLangHasError = false;

    const html = document.querySelector('html');
    const xpath = Elements.DOMPath.xPath(html, true);

    
    if (!html.hasAttribute('lang')) {
        PrimaryLangHasError = true;
        errorList.push({
            url: window.location.href,
            type: 'err',
            cat: 'lang',
            err: 'ErrNoPrimaryLangAttr',
            xpath: xpath,
            fpTempId: '0'
        });
    }
    else {
        lang = html.getAttribute('lang').trim();
        if (lang == null || lang === '') {
            PrimaryLangHasError = true;
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'lang',
                err: 'ErrEmptyLangAttr',
                xpath: xpath,
                fpTempId: '0'
            });
        }
        else {
            const langSplit = lang.split('-');
            const htmlPrimaryLang = langSplit[0];

            let htmlQualifierLang;
            if (langSplit.length == 2) {
                htmlQualifierLang = langSplit[1];
            }
            else if (langSplit.length > 2) {
                // we have more thsn one hyphen
                PrimaryLangHasError = true;
                htmlQualifierLang = null;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'lang',
                    err: 'ErrIncorrectlyFormattedPrimaryLang',
                    found: lang,
                    xpath: xpath,
                    fpTempId: '0'
                });
            }

            if (!(htmlPrimaryLang in LANGUAGE_CODES)) {
                PrimaryLangHasError = true;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'lang',
                    err: 'ErrPrimaryLangUnrecognized',
                    found: htmlPrimaryLang,
                    xpath: xpath,
                    fpTempId: '0'
                });
            }

            if (htmlQualifierLang != null && !(lang in LANGUAGE_CODES)) {
                PrimaryLangHasError = true;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'lang',
                    err: 'ErrRegionQualifierForPrimaryLangNotRecognized',
                    found: lang,
                    xpath: xpath,
                    fpTempId: '0'
                });
            }

        }
    }

    if (html.hasAttribute('xml:lang')) {

        xmlLang = html.getAttribute('xml:lang').trim();
        if (xmlLang === null || xmlLang === '') {
            primaryXmlLangHasError = true;
            errorList.push({
                url: window.location.href,
                cat: 'lang',
                type: 'err',
                err: 'ErrEmptyXmlLangAttr',
                xpath: xpath,
                fpTempId: '0'
            });
        }
        else {
            const xmlPrimaryLang = (xmlLang) ? xmlLang.split('-')[0] : "";
            if (!(xmlPrimaryLang in LANGUAGE_CODES)) {
                primaryXmlLangHasError = true;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'lang',
                    err: 'ErrPrimaryXmlLangUnrecognized',
                    found: xmlPrimaryLang,
                    xpath: xpath,
                    fpTempId: '0'
                });
            }
            else if (!(xmlLang in LANGUAGE_CODES)) {
                primaryXmlLangHasError = true;
                errorList.push({
                    url: window.location.href,
                    type: 'err',
                    cat: 'lang',
                    err: 'ErrRegionQualifierForPrimaryXmlLangNotRecognized',
                    found: xmlLang,
                    xpath: xpath,
                    fpTempId: '0'
                });
            }

        }

    }

    if (!PrimaryLangHasError && !primaryXmlLangHasError) {
        if (lang != null && xmlLang != null & lang != xmlLang) {
            errorList.push({
                url: window.location.href,
                type: 'err',
                cat: 'lang',
                err: 'ErrPrimaryLangAndXmlLangMismatch',
                lang: lang,
                xmlLang: xmlLang,
                xpath: xpath,
                fpTempId: '0'
            });
        }
    }


    ////////////////////////////////////////
    // Language of parts
    ////////////////////////////////////////

    const elements = document.querySelectorAll("body, body *");
    elements.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            
            if (element.hasAttribute('lang')) {

                const xpath = Elements.DOMPath.xPath(element, true);

                const eLang = element.getAttribute('lang').trim();
                const eLangSplit = eLang.split('-');
                const primaryELang = eLangSplit[0];

                if (eLang === null || eLang === '') {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'lang',
                        err: 'ErrElementLangEmpty',
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')

                    });
                }

                else {
                    let eLangOk = true;
                    if (!(primaryELang in LANGUAGE_CODES)) {
                        eLangOk = false;
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'lang',
                            err: 'ErrElementPrimaryLangNotRecognized',
                            found: primaryELang,
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')  
                        });
                    }
                    //alert('elang: ' + eLang);
                    //alert('eLangOk: ' + eLangOk);

                    if (eLangOk && eLangSplit.length > 1 && !(eLang in LANGUAGE_CODES)) {
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'lang',
                            err: 'ErrElementRegionQualifierNotRecognized',
                            found: eLang,
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId')
                        });
                    }
                }
            }
        }
    });

    // This time for hreflang
    elements.forEach(element => {
        if (element.nodeType == Node.ELEMENT_NODE) {

            if (element.hasAttribute('hreflang')) {

                const xpath = Elements.DOMPath.xPath(element, true);

                const eLang = element.getAttribute('hreflang').trim();
                const eLangSplit = eLang.split('-');
                const primaryELang = eLangSplit[0];

                // Node needs to be a link
                if (element.tagName.toUpperCase() != 'A') {
                    errorList.push({
                        url: window.location.href,
                        type: 'err',
                        cat: 'lang',
                        err: 'ErrHreflangNotOnLink',
                        xpath: xpath,
                        parentLandmark: element.getAttribute('a11y-parentLandmark'),
                        parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                        parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                        fpTempId: element.getAttribute('a11y-fpId')
                    });
                }
                else {
                    if (eLang === null || eLang === '') {
                        errorList.push({
                            url: window.location.href,
                            type: 'err',
                            cat: 'lang',
                            err: 'ErrHreflangAttrEmpty',
                            xpath: xpath,
                            parentLandmark: element.getAttribute('a11y-parentLandmark'),
                            parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                            parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                            fpTempId: element.getAttribute('a11y-fpId') 
                        });
                    }

                    else {
                        let eLangOk = true;
                        if (!(primaryELang in LANGUAGE_CODES)) {
                            eLangOk = false;
                            errorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'lang',
                                err: 'ErrPrimaryHrefLangNotRecognized',
                                found: primaryELang,
                                xpath: xpath,
                                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                                fpTempId: element.getAttribute('a11y-fpId')       
                            });
                        }

                        if (eLangOk && eLangSplit.length > 1 && !(eLang in LANGUAGE_CODES)) {
                            errorList.push({
                                url: window.location.href,
                                type: 'err',
                                cat: 'lang',
                                err: 'ErrRegionQualifierForHreflangUnrecognized',
                                found: eLang,
                                xpath: xpath,
                                parentLandmark: element.getAttribute('a11y-parentLandmark'),
                                parentLandmarkXpath: element.getAttribute('a11y-parentLandmark.xpath'),
                                parentLandmarkAN: element.getAttribute('a11y-parentLandmark.an'),
                                fpTempId: element.getAttribute('a11y-fpId')      
                            });
                        }
                    }

                }
            }
        }
    });


    return { errors: errorList };

}

