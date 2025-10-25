"""
WCAG Success Criteria Mapper
Maps issue codes to specific WCAG success criteria
"""

# WCAG 2.2 URL Slug Mapping - maps criterion numbers to Understanding page slugs
WCAG_CRITERION_SLUGS = {
    '1.1.1': 'non-text-content',
    '1.2.1': 'audio-only-and-video-only-prerecorded',
    '1.2.2': 'captions-prerecorded',
    '1.2.3': 'audio-description-or-media-alternative-prerecorded',
    '1.2.4': 'captions-live',
    '1.2.5': 'audio-description-prerecorded',
    '1.3.1': 'info-and-relationships',
    '1.3.2': 'meaningful-sequence',
    '1.3.3': 'sensory-characteristics',
    '1.3.4': 'orientation',
    '1.3.5': 'identify-input-purpose',
    '1.4.1': 'use-of-color',
    '1.4.2': 'audio-control',
    '1.4.3': 'contrast-minimum',
    '1.4.4': 'resize-text',
    '1.4.5': 'images-of-text',
    '1.4.6': 'contrast-enhanced',
    '1.4.8': 'visual-presentation',
    '1.4.10': 'reflow',
    '1.4.11': 'non-text-contrast',
    '1.4.12': 'text-spacing',
    '1.4.13': 'content-on-hover-or-focus',
    '2.1.1': 'keyboard',
    '2.1.2': 'no-keyboard-trap',
    '2.1.3': 'keyboard-no-exception',
    '2.1.4': 'character-key-shortcuts',
    '2.2.1': 'timing-adjustable',
    '2.2.2': 'pause-stop-hide',
    '2.2.6': 'timeouts',
    '2.3.1': 'three-flashes-or-below-threshold',
    '2.3.3': 'animation-from-interactions',
    '2.4.1': 'bypass-blocks',
    '2.4.2': 'page-titled',
    '2.4.3': 'focus-order',
    '2.4.4': 'link-purpose-in-context',
    '2.4.5': 'multiple-ways',
    '2.4.6': 'headings-and-labels',
    '2.4.7': 'focus-visible',
    '2.4.8': 'location',
    '2.4.11': 'focus-not-obscured-minimum',
    '2.4.13': 'focus-appearance',
    '2.5.1': 'pointer-gestures',
    '2.5.2': 'pointer-cancellation',
    '2.5.3': 'label-in-name',
    '2.5.4': 'motion-actuation',
    '2.5.7': 'dragging-movements',
    '2.5.8': 'target-size-minimum',
    '3.1.1': 'language-of-page',
    '3.1.2': 'language-of-parts',
    '3.2.1': 'on-focus',
    '3.2.2': 'on-input',
    '3.2.3': 'consistent-navigation',
    '3.2.4': 'consistent-identification',
    '3.2.6': 'consistent-help',
    '3.3.1': 'error-identification',
    '3.3.2': 'labels-or-instructions',
    '3.3.3': 'error-suggestion',
    '3.3.4': 'error-prevention-legal-financial-data',
    '3.3.7': 'redundant-entry',
    '3.3.8': 'accessible-authentication-minimum',
    '4.1.2': 'name-role-value',
    '4.1.3': 'status-messages',
    '5.2.4': 'accessibility-supported',
}

# Comprehensive WCAG mapping for all known issue types
WCAG_MAPPINGS = {
    # Image Issues
    'ErrImageWithNoAlt': ['1.1.1 Non-text Content'],
    'ErrEmptyAltText': ['1.1.1 Non-text Content'],
    'ErrAltTooLong': ['1.1.1 Non-text Content'],
    'ErrRedundantAlt': ['1.1.1 Non-text Content'],
    'ErrNoAlt': ['1.1.1 Non-text Content'],
    'WarnAltTextTooLong': ['1.1.1 Non-text Content'],
    'WarnAltTextRedundant': ['1.1.1 Non-text Content'],
    'DiscoImageOnPage': [],  # Discovery - no WCAG criteria

    # Heading Issues
    'ErrEmptyHeading': ['2.4.6 Headings and Labels'],
    'ErrSkippedHeadingLevel': ['1.3.1 Info and Relationships'],
    'ErrMultipleH1': ['1.3.1 Info and Relationships'],
    'ErrMultipleH1HeadingsOnPage': ['1.3.1 Info and Relationships'],
    'ErrNoH1OnPage': ['1.3.1 Info and Relationships', '2.4.6 Headings and Labels'],
    'WarnHeadingInsideDisplayNone': ['1.3.1 Info and Relationships'],
    'WarnHeadingOver60CharsLong': ['2.4.6 Headings and Labels'],
    'DiscoHeadingHierarchy': [],  # Discovery
    
    # Form Issues  
    'ErrNoLabel': ['1.3.1 Info and Relationships', '3.3.2 Labels or Instructions', '4.1.2 Name, Role, Value'],
    'ErrEmptyLabel': ['3.3.2 Labels or Instructions'],
    'ErrNoFieldset': ['1.3.1 Info and Relationships'],
    'ErrMissingRequired': ['3.3.2 Labels or Instructions', '3.3.5 Help'],
    'ErrPlaceholderAsLabel': ['3.3.2 Labels or Instructions'],
    'ErrOrphanLabelWithNoId': ['1.3.1 Info and Relationships'],
    'ErrLabelContainsMultipleFields': ['1.3.1 Info and Relationships', '3.3.2 Labels or Instructions'],
    'ErrLabelMismatchOfAccessibleNameAndLabelText': ['2.5.3 Label in Name'],
    'ErrEmptyAriaLabelOnField': ['4.1.2 Name, Role, Value'],
    'ErrEmptyAriaLabelledByOnField': ['4.1.2 Name, Role, Value'],
    'ErrFieldAriaRefDoesNotExist': ['4.1.2 Name, Role, Value'],
    'ErrFormEmptyHasNoChildNodes': ['1.3.1 Info and Relationships'],
    'ErrFormEmptyHasNoInteractiveElements': ['1.3.1 Info and Relationships'],
    'ErrWrongTabindexForInteractiveElement': ['2.4.3 Focus Order'],
    'ErrAriaLabelMayNotBeFoundByVoiceControl': ['2.5.3 Label in Name'],
    'ErrTitleAsOnlyLabel': ['3.3.2 Labels or Instructions', '4.1.2 Name, Role, Value'],
    'WarnFormHasNoLabel': ['1.3.1 Info and Relationships'],
    'WarnFieldLabelledByMultipleElements': ['1.3.1 Info and Relationships'],
    'WarnFieldLabelledByElementThatIsNotALabel': ['1.3.1 Info and Relationships'],
    'WarnFieldLabelledUsingAriaLabel': ['3.3.2 Labels or Instructions'],  # Warning about usability concerns
    'DiscoFormOnPage': [],  # Discovery

    # Form Input Focus Issues
    'ErrInputNoVisibleFocus': ['2.4.7 Focus Visible'],
    'ErrInputColorChangeOnly': ['2.4.7 Focus Visible', '1.4.1 Use of Color'],
    'ErrInputFocusContrastFail': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'ErrInputSingleSideBoxShadow': ['2.4.7 Focus Visible'],
    'ErrInputBorderChangeInsufficient': ['2.4.7 Focus Visible'],
    'ErrInputOutlineWidthInsufficient': ['2.4.7 Focus Visible', '2.4.11 Focus Appearance'],
    'WarnInputNoBorderOutline': ['2.4.7 Focus Visible'],
    'WarnInputDefaultFocus': ['2.4.7 Focus Visible'],
    'WarnInputFocusGradientBackground': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'WarnInputTransparentFocus': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],

    # Landmark Issues
    'ErrNoMainLandmark': ['1.3.1 Info and Relationships', '2.4.1 Bypass Blocks'],
    'ErrMultipleBanners': ['1.3.1 Info and Relationships'],
    'ErrMultipleBannerLandmarks': ['1.3.1 Info and Relationships'],
    'ErrMultipleContentinfo': ['1.3.1 Info and Relationships'],
    'ErrMultipleContentinfoLandmarks': ['1.3.1 Info and Relationships'],
    'ErrMultipleMainLandmarksOnPage': ['1.3.1 Info and Relationships'],
    'ErrNoNavLandmark': ['1.3.1 Info and Relationships', '2.4.1 Bypass Blocks'],
    'WarnMultipleNavNeedsLabel': ['1.3.1 Info and Relationships'],
    'ErrFormLandmarkMustHaveAccessibleName': ['5.2.4'],
    'ErrContentOutsideLandmarks': ['5.2.4'],
    'WarnContentOutsideLandmarks': ['1.3.1 Info and Relationships'],  # Deprecated - use ErrContentOutsideLandmarks
    'WarnUnlabelledForm': ['1.3.1 Info and Relationships', '4.1.2 Name, Role, Value'],  # Deprecated
    'DiscoLandmarkStructure': [],  # Discovery

    # Navigation/Current Page Issues
    'ErrNoCurrentPageIndicatorScreenReader': ['5.2.4'],
    'ErrNoCurrentPageIndicatorMagnification': ['2.4.8 Location', '5.2.4 Accessibility Supported'],
    'WarnNoCurrentPageIndicator': ['2.4.8 Location'],  # Deprecated
    
    # Color/Contrast Issues
    'ErrTextContrast': ['1.4.3 Contrast (Minimum)'],
    'ErrInsufficientContrast': ['1.4.3 Contrast (Minimum)'],
    'ErrLinkContrast': ['1.4.3 Contrast (Minimum)', '1.4.1 Use of Color'],
    'WarnColorRelatedStyleDefinedExplicitlyInElement': ['1.4.1 Use of Color'],
    'WarnColorRelatedStyleDefinedExplicitlyInStyleTag': ['1.4.1 Use of Color'],
    'WarnNoColorSchemeSupport': ['1.4.3 Contrast (Minimum)', '5.2.4 Accessibility Supported'],
    'WarnNoContrastSupport': ['1.4.3 Contrast (Minimum)', '5.2.4 Accessibility Supported'],
    'DiscoStyleAttrOnElements': [],  # Discovery
    'DiscoStyleElementOnPage': [],  # Discovery
    
    # Focus Issues
    'ErrNoFocusIndicator': ['2.4.7 Focus Visible'],
    'ErrOutlineIsNoneOnInteractiveElement': ['2.4.7 Focus Visible'],
    'ErrTransparentFocusIndicator': ['2.4.7 Focus Visible'],
    'ErrZeroOutlineOffset': ['2.4.7 Focus Visible'],
    'ErrNoOutlineOffsetDefined': ['2.4.7 Focus Visible'],
    'ErrInvalidTabindex': ['2.4.3 Focus Order'],
    'ErrPositiveTabindex': ['2.4.3 Focus Order'],
    'WarnZeroOutlineOffset': ['2.4.7 Focus Visible'],

    # Button Focus Issues
    'ErrButtonOutlineNoneNoBoxShadow': ['2.4.7 Focus Visible', '1.4.1 Use of Color'],
    'ErrButtonFocusContrastFail': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'ErrButtonOutlineWidthInsufficient': ['2.4.7 Focus Visible', '2.4.11 Focus Appearance'],
    'ErrButtonOutlineOffsetInsufficient': ['2.4.7 Focus Visible'],
    'ErrButtonFocusObscured': ['2.4.7 Focus Visible'],
    'ErrButtonSingleSideBoxShadow': ['2.4.7 Focus Visible', '1.4.1 Use of Color'],
    'ErrButtonClipPathWithOutline': ['2.4.7 Focus Visible'],
    'ErrButtonTransparentOutline': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'WarnButtonOutlineNoneWithBoxShadow': ['2.4.7 Focus Visible'],
    'WarnButtonDefaultFocus': ['2.4.7 Focus Visible'],
    'WarnButtonFocusGradientBackground': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'WarnButtonFocusImageBackground': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],

    # Link Focus Issues
    'ErrLinkFocusContrastFail': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'ErrLinkOutlineWidthInsufficient': ['2.4.7 Focus Visible', '2.4.11 Focus Appearance'],
    'ErrLinkImageNoFocusIndicator': ['2.4.7 Focus Visible'],
    'ErrLinkColorChangeOnly': ['2.4.7 Focus Visible', '1.4.1 Use of Color'],
    'WarnLinkOutlineOffsetTooLarge': ['2.4.7 Focus Visible'],
    'WarnLinkDefaultFocus': ['2.4.7 Focus Visible'],
    'WarnLinkFocusGradientBackground': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'WarnLinkTransparentOutline': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],

    # Tabindex Interactive Element Focus Issues
    'ErrTabindexNoVisibleFocus': ['2.4.7 Focus Visible'],
    'ErrTabindexChildOfInteractive': ['1.3.1 Info and Relationships'],
    'ErrTabindexAriaHiddenFocusable': ['4.1.2 Name, Role, Value'],
    'ErrTabindexFocusContrastFail': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'ErrTabindexOutlineNoneNoBoxShadow': ['2.4.7 Focus Visible'],
    'ErrTabindexSingleSideBoxShadow': ['2.4.7 Focus Visible'],
    'ErrTabindexOutlineWidthInsufficient': ['2.4.7 Focus Visible', '2.4.11 Focus Appearance'],
    'ErrTabindexColorChangeOnly': ['2.4.7 Focus Visible', '1.4.1 Use of Color'],
    'ErrTabindexTransparentOutline': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'WarnTabindexDefaultFocus': ['2.4.7 Focus Visible'],
    'WarnTabindexNoBorderOutline': ['2.4.7 Focus Visible'],

    # Event Handler Interactive Element Focus Issues
    'ErrHandlerNoVisibleFocus': ['2.4.7 Focus Visible'],
    'ErrHandlerFocusContrastFail': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'ErrHandlerOutlineNoneNoBoxShadow': ['2.4.7 Focus Visible'],
    'ErrHandlerSingleSideBoxShadow': ['2.4.7 Focus Visible'],
    'ErrHandlerOutlineWidthInsufficient': ['2.4.7 Focus Visible', '2.4.11 Focus Appearance'],
    'ErrHandlerColorChangeOnly': ['2.4.7 Focus Visible', '1.4.1 Use of Color'],
    'ErrHandlerTransparentOutline': ['2.4.7 Focus Visible', '1.4.11 Non-text Contrast'],
    'WarnHandlerDefaultFocus': ['2.4.7 Focus Visible'],
    'WarnHandlerNoBorderOutline': ['2.4.7 Focus Visible'],

    # Language Issues
    'ErrNoPageLanguage': ['3.1.1 Language of Page'],
    'ErrInvalidLanguageCode': ['3.1.1 Language of Page'],
    'ErrEmptyLanguageCode': ['3.1.1 Language of Page'],
    
    # Page Title Issues
    'ErrNoPageTitle': ['2.4.2 Page Titled'],
    'ErrEmptyPageTitle': ['2.4.2 Page Titled'],
    'ErrPageTitleTooLong': ['2.4.2 Page Titled'],
    'ErrPageTitleTooShort': ['2.4.2 Page Titled'],
    'ErrMultiplePageTitles': ['2.4.2 Page Titled'],
    'WarnMultipleTitleElements': ['2.4.2 Page Titled'],  # Deprecated - use ErrMultiplePageTitles
    
    # SVG Issues
    'ErrSvgImageNoLabel': ['1.1.1 Non-text Content'],
    'ErrSvgStaticWithoutRole': ['1.1.1 Non-text Content', '4.1.2 Name, Role, Value'],
    'DiscoInteractiveSvg': [],  # Discovery - manual review required
    'DiscoFoundSvgImage': [],  # Discovery
    'DiscoFoundInlineSvg': [],  # Discovery - deprecated, replaced by ErrSvgStaticWithoutRole and DiscoInteractiveSvg
    
    # Iframe Issues
    'ErrIframeWithNoTitleAttr': ['4.1.2 Name, Role, Value'],
    'ErrEmptyTitleAttr': ['4.1.2 Name, Role, Value'],
    'WarnIframeTitleNotDescriptive': ['4.1.2 Name, Role, Value'],
    
    # Font/Text Issues
    'ErrFontSizeTooSmall': ['1.4.4 Resize Text'],
    'WarnFontSizeSmall': ['1.4.4 Resize Text'],

    # PDF Issues
    'WarnPdfLinkFound': ['1.1.1 Non-text Content'],

    # Document Link Issues
    'ErrDocumentLinkMissingFileType': ['2.4.4 Link Purpose (In Context)'],
    'WarnMissingDocumentMetadata': ['2.4.4 Link Purpose (In Context)'],

    # Semantic Structure Issues
    'ErrMissingDocumentType': ['4.1.1 Parsing'],

    # Generic/Other Issues
    'ErrTitleAttrFound': ['3.3.2 Labels or Instructions'],
    'ErrElementHasNoText': ['1.3.1 Info and Relationships'],
    'DiscoElementFound': [],  # Discovery
    
    # Tabindex Issues
    'ErrInvalidTabindex': ['2.4.3 Focus Order'],
    'ErrPositiveTabindex': ['2.4.3 Focus Order'],
}

def get_wcag_criteria(issue_code: str) -> list:
    """
    Get WCAG success criteria for a given issue code
    
    Args:
        issue_code: The issue code to look up
        
    Returns:
        List of WCAG success criteria strings
    """
    # Direct lookup
    if issue_code in WCAG_MAPPINGS:
        return WCAG_MAPPINGS[issue_code]
    
    # Try removing test prefix if present
    if '_' in issue_code:
        base_code = issue_code.split('_', 1)[1] if issue_code.count('_') > 0 else issue_code
        if base_code in WCAG_MAPPINGS:
            return WCAG_MAPPINGS[base_code]
    
    # Try pattern matching for dynamic issue codes
    patterns = {
        'contrast': ['1.4.3 Contrast (Minimum)'],
        'color': ['1.4.1 Use of Color', '1.4.3 Contrast (Minimum)'],
        'label': ['1.3.1 Info and Relationships', '3.3.2 Labels or Instructions'],
        'heading': ['1.3.1 Info and Relationships', '2.4.6 Headings and Labels'],
        'landmark': ['1.3.1 Info and Relationships', '2.4.1 Bypass Blocks'],
        'focus': ['2.4.7 Focus Visible', '2.4.3 Focus Order'],
        'keyboard': ['2.1.1 Keyboard', '2.4.3 Focus Order'],
        'aria': ['4.1.2 Name, Role, Value', '1.3.1 Info and Relationships'],
        'alt': ['1.1.1 Non-text Content'],
        'language': ['3.1.1 Language of Page'],
        'title': ['2.4.2 Page Titled'],
        'form': ['1.3.1 Info and Relationships', '3.3.2 Labels or Instructions'],
        'tabindex': ['2.4.3 Focus Order'],
        'image': ['1.1.1 Non-text Content'],
        'img': ['1.1.1 Non-text Content'],
        'svg': ['1.1.1 Non-text Content'],
        'iframe': ['2.4.1 Bypass Blocks', '4.1.2 Name, Role, Value'],
    }
    
    issue_lower = issue_code.lower()
    for pattern, criteria in patterns.items():
        if pattern in issue_lower:
            return criteria
    
    # Default fallback - most issues relate to structure or parsing
    return ['1.3.1 Info and Relationships', '4.1.1 Parsing']

def format_wcag_link(criterion: str, link_type: str = 'understanding') -> str:
    """
    Generate a W3C link for a WCAG 2.2 criterion

    Args:
        criterion: WCAG criterion string (e.g., "1.4.3" or "1.4.3 Contrast (Minimum)")
        link_type: Type of link - 'understanding' or 'quickref' (default: 'understanding')

    Returns:
        URL to the WCAG 2.2 understanding or quick reference document
    """
    # Extract the number (e.g., "1.4.3" from "1.4.3 Contrast (Minimum)")
    number = criterion.split()[0] if ' ' in criterion else criterion

    # Special case for 5.2.4 Accessibility Supported (Conformance Requirement)
    # Points to the definition in the main WCAG spec, not an Understanding page
    if number == '5.2.4':
        return "https://www.w3.org/TR/WCAG22/#dfn-accessibility-supported"

    # Get the slug from module-level mapping
    slug = WCAG_CRITERION_SLUGS.get(number)

    if slug:
        if link_type == 'quickref':
            return f"https://www.w3.org/WAI/WCAG22/quickref/#{slug}"
        else:  # understanding
            return f"https://www.w3.org/WAI/WCAG22/Understanding/{slug}"

    # Fallback to generic quickref page
    return "https://www.w3.org/WAI/WCAG22/quickref/"

def enrich_wcag_criteria(criteria_list: list) -> list:
    """
    Enrich a list of WCAG criteria with full names and conformance levels

    Args:
        criteria_list: List of criterion numbers or full strings

    Returns:
        List of enriched criterion strings with format "X.X.X Name (Level XX)"
    """
    # Map of criterion numbers to full names with conformance levels
    # Format: "X.X.X Name (Level XX)"
    criterion_names = {
        '1.1.1': '1.1.1 Non-text Content (Level A)',
        '1.2.1': '1.2.1 Audio-only and Video-only (Prerecorded) (Level A)',
        '1.2.2': '1.2.2 Captions (Prerecorded) (Level A)',
        '1.2.3': '1.2.3 Audio Description or Media Alternative (Prerecorded) (Level A)',
        '1.2.4': '1.2.4 Captions (Live) (Level AA)',
        '1.2.5': '1.2.5 Audio Description (Prerecorded) (Level AA)',
        '1.3.1': '1.3.1 Info and Relationships (Level A)',
        '1.3.2': '1.3.2 Meaningful Sequence (Level A)',
        '1.3.3': '1.3.3 Sensory Characteristics (Level A)',
        '1.3.4': '1.3.4 Orientation (Level AA)',
        '1.3.5': '1.3.5 Identify Input Purpose (Level AA)',
        '1.4.1': '1.4.1 Use of Color (Level A)',
        '1.4.2': '1.4.2 Audio Control (Level A)',
        '1.4.3': '1.4.3 Contrast (Minimum) (Level AA)',
        '1.4.4': '1.4.4 Resize Text (Level AA)',
        '1.4.5': '1.4.5 Images of Text (Level AA)',
        '1.4.6': '1.4.6 Contrast (Enhanced) (Level AAA)',
        '1.4.8': '1.4.8 Visual Presentation (Level AAA)',
        '1.4.10': '1.4.10 Reflow (Level AA)',
        '1.4.11': '1.4.11 Non-text Contrast (Level AA)',
        '1.4.12': '1.4.12 Text Spacing (Level AA)',
        '1.4.13': '1.4.13 Content on Hover or Focus (Level AA)',
        '2.1.1': '2.1.1 Keyboard (Level A)',
        '2.1.2': '2.1.2 No Keyboard Trap (Level A)',
        '2.1.3': '2.1.3 Keyboard (No Exception) (Level AAA)',
        '2.1.4': '2.1.4 Character Key Shortcuts (Level A)',
        '2.2.1': '2.2.1 Timing Adjustable (Level A)',
        '2.2.2': '2.2.2 Pause, Stop, Hide (Level A)',
        '2.3.1': '2.3.1 Three Flashes or Below Threshold (Level A)',
        '2.4.1': '2.4.1 Bypass Blocks (Level A)',
        '2.4.2': '2.4.2 Page Titled (Level A)',
        '2.4.3': '2.4.3 Focus Order (Level A)',
        '2.4.4': '2.4.4 Link Purpose (In Context) (Level A)',
        '2.4.5': '2.4.5 Multiple Ways (Level AA)',
        '2.4.6': '2.4.6 Headings and Labels (Level AA)',
        '2.4.7': '2.4.7 Focus Visible (Level AA)',
        '2.4.8': '2.4.8 Location (Level AAA)',
        '2.4.11': '2.4.11 Focus Appearance (Level AA)',
        '2.5.1': '2.5.1 Pointer Gestures (Level A)',
        '2.5.2': '2.5.2 Pointer Cancellation (Level A)',
        '2.5.3': '2.5.3 Label in Name (Level A)',
        '2.5.4': '2.5.4 Motion Actuation (Level A)',
        '2.5.7': '2.5.7 Dragging Movements (Level AA)',
        '2.5.8': '2.5.8 Target Size (Minimum) (Level AA)',
        '3.1.1': '3.1.1 Language of Page (Level A)',
        '3.1.2': '3.1.2 Language of Parts (Level AA)',
        '3.2.1': '3.2.1 On Focus (Level A)',
        '3.2.2': '3.2.2 On Input (Level A)',
        '3.2.3': '3.2.3 Consistent Navigation (Level AA)',
        '3.2.4': '3.2.4 Consistent Identification (Level AA)',
        '3.2.6': '3.2.6 Consistent Help (Level A)',
        '3.3.1': '3.3.1 Error Identification (Level A)',
        '3.3.2': '3.3.2 Labels or Instructions (Level A)',
        '3.3.3': '3.3.3 Error Suggestion (Level AA)',
        '3.3.4': '3.3.4 Error Prevention (Legal, Financial, Data) (Level AA)',
        '3.3.5': '3.3.5 Help (Level AAA)',
        '3.3.7': '3.3.7 Redundant Entry (Level A)',
        '3.3.8': '3.3.8 Accessible Authentication (Minimum) (Level AA)',
        '4.1.1': '4.1.1 Parsing (Level A)',
        '4.1.2': '4.1.2 Name, Role, Value (Level A)',
        '4.1.3': '4.1.3 Status Messages (Level AA)',
        '5.2.4': '5.2.4 Accessibility Supported',
    }

    enriched = []
    for criterion in criteria_list:
        # Extract just the number part if it already has text
        if ' ' in str(criterion):
            # Extract number from strings like "1.1.1 Non-text Content" or "1.1.1"
            number = criterion.split()[0]
        else:
            number = criterion

        # Check if we have a full entry for this criterion
        if number in criterion_names:
            enriched.append(criterion_names[number])
        else:
            # Keep original if we don't have mapping
            enriched.append(criterion)

    return enriched