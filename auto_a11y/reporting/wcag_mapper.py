"""
WCAG Success Criteria Mapper
Maps issue codes to specific WCAG success criteria
"""

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
    'ErrEmptyHeading': ['1.3.1 Info and Relationships', '2.4.6 Headings and Labels'],
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
    'ErrUnlabelledField': ['1.3.1 Info and Relationships', '3.3.2 Labels or Instructions'],
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
    'InfoFieldLabelledUsingAriaLabel': [],  # Info only
    'DiscoFormOnPage': [],  # Discovery
    
    # Landmark Issues
    'ErrNoMainLandmark': ['1.3.1 Info and Relationships', '2.4.1 Bypass Blocks'],
    'ErrMultipleBanners': ['1.3.1 Info and Relationships'],
    'ErrMultipleBannerLandmarks': ['1.3.1 Info and Relationships'],
    'ErrMultipleContentinfo': ['1.3.1 Info and Relationships'],
    'ErrMultipleContentinfoLandmarks': ['1.3.1 Info and Relationships'],
    'ErrMultipleMainLandmarksOnPage': ['1.3.1 Info and Relationships'],
    'ErrNoNavLandmark': ['1.3.1 Info and Relationships', '2.4.1 Bypass Blocks'],
    'WarnMultipleNavNeedsLabel': ['1.3.1 Info and Relationships'],
    'DiscoLandmarkStructure': [],  # Discovery
    
    # Color/Contrast Issues
    'ErrTextContrast': ['1.4.3 Contrast (Minimum)'],
    'ErrInsufficientContrast': ['1.4.3 Contrast (Minimum)'],
    'ErrLinkContrast': ['1.4.3 Contrast (Minimum)', '1.4.1 Use of Color'],
    'ErrColorStyleDefinedExplicitlyInElement': ['1.4.1 Use of Color'],
    'ErrColorStyleDefinedExplicitlyInStyleTag': ['1.4.1 Use of Color'],
    'WarnColorRelatedStyleDefinedExplicitlyInElement': ['1.4.1 Use of Color'],
    'WarnColorRelatedStyleDefinedExplicitlyInStyleTag': ['1.4.1 Use of Color'],
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
    'DiscoFoundSvgImage': [],  # Discovery
    'DiscoFoundInlineSvg': [],  # Discovery
    
    # Iframe Issues
    'ErrIframeWithNoTitleAttr': ['2.4.1 Bypass Blocks', '4.1.2 Name, Role, Value'],
    'ErrEmptyTitleAttr': ['2.4.1 Bypass Blocks', '4.1.2 Name, Role, Value'],
    'WarnIframeTitleNotDescriptive': ['2.4.1 Bypass Blocks'],
    
    # Font/Text Issues
    'ErrFontSizeTooSmall': ['1.4.4 Resize Text'],
    'WarnFontSizeSmall': ['1.4.4 Resize Text'],
    
    # PDF Issues
    'WarnPdfLinkFound': ['1.1.1 Non-text Content'],
    
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

def format_wcag_link(criterion: str) -> str:
    """
    Generate a W3C link for a WCAG criterion
    
    Args:
        criterion: WCAG criterion string (e.g., "1.4.3 Contrast (Minimum)")
        
    Returns:
        URL to the WCAG understanding document
    """
    # Extract the number (e.g., "1.4.3")
    parts = criterion.split(' ', 1)
    if len(parts) > 0:
        number = parts[0]
        # Convert to URL format (e.g., "contrast-minimum")
        if len(parts) > 1 and '(' in parts[1]:
            # Extract text between parentheses
            name_part = parts[1].split('(')[1].rstrip(')')
            slug = name_part.lower().replace(' ', '-')
        else:
            # Fallback to using the number
            slug = f"sc-{number.replace('.', '')}"
        
        return f"https://www.w3.org/WAI/WCAG21/Understanding/{slug}.html"
    
    return "https://www.w3.org/WAI/WCAG21/quickref/"

def enrich_wcag_criteria(criteria_list: list) -> list:
    """
    Enrich a list of WCAG criteria with full names
    
    Args:
        criteria_list: List of criterion numbers or full strings
        
    Returns:
        List of enriched criterion strings
    """
    # Map of common criterion numbers to full names
    criterion_names = {
        '1.1.1': '1.1.1 Non-text Content',
        '1.3.1': '1.3.1 Info and Relationships',
        '1.4.1': '1.4.1 Use of Color',
        '1.4.3': '1.4.3 Contrast (Minimum)',
        '1.4.4': '1.4.4 Resize Text',
        '1.4.6': '1.4.6 Contrast (Enhanced)',
        '1.4.11': '1.4.11 Non-text Contrast',
        '2.1.1': '2.1.1 Keyboard',
        '2.4.1': '2.4.1 Bypass Blocks',
        '2.4.2': '2.4.2 Page Titled',
        '2.4.3': '2.4.3 Focus Order',
        '2.4.6': '2.4.6 Headings and Labels',
        '2.4.7': '2.4.7 Focus Visible',
        '2.5.3': '2.5.3 Label in Name',
        '3.1.1': '3.1.1 Language of Page',
        '3.1.2': '3.1.2 Language of Parts',
        '3.3.2': '3.3.2 Labels or Instructions',
        '3.3.5': '3.3.5 Help',
        '4.1.1': '4.1.1 Parsing',
        '4.1.2': '4.1.2 Name, Role, Value',
    }
    
    enriched = []
    for criterion in criteria_list:
        if criterion in criterion_names:
            enriched.append(criterion_names[criterion])
        elif ' ' not in criterion and '.' in criterion:
            # It's just a number, try to enrich it
            enriched.append(criterion_names.get(criterion, criterion))
        else:
            # Already enriched or unknown
            enriched.append(criterion)
    
    return enriched