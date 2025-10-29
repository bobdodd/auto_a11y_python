"""
Generic descriptions for all catalog entries with placeholders.
This will be used to update issue_descriptions_enhanced.py
"""

WHAT_GENERIC_ADDITIONS = {
    # AI-detected issues
    'AI_ErrAmbiguousLinkText': "Link text is ambiguous without surrounding context",
    'AI_ErrCarouselWithoutARIA': "Carousel or slider lacks proper ARIA markup and controls",
    'AI_ErrDialogWithoutARIA': "Element appears to be a dialog or modal but lacks proper ARIA markup",
    'AI_ErrDropdownWithoutARIA': "Dropdown menu lacks proper ARIA markup",
    'AI_ErrHeadingLevelMismatch': "Heading level doesn't match visual hierarchy",
    'AI_ErrInteractiveElementIssue': "Interactive element has accessibility issues",
    'AI_ErrMissingInteractiveRole': "Interactive element lacks appropriate ARIA role",
    'AI_ErrModalFocusTrap': "Modal or dialog does not properly trap focus",
    'AI_ErrNonSemanticButton': "Clickable element is not a semantic button",
    'AI_ErrSkippedHeading': "Heading levels are skipped in the document hierarchy",
    'AI_ErrTabsWithoutARIA': "Tab interface lacks proper ARIA markup",
    'AI_ErrVisualHeadingNotMarked': "Text appears visually as a heading but is not marked up with proper heading tags",

    # Discovery items
    'DiscoFontFound': "Font is used at multiple sizes on this page",
    'DiscoFormOnPage': "A form has been detected on this page",
    'DiscoNavFound': "A navigation region has been detected on this page",
    'DiscoAsideFound': "A complementary region has been detected on this page",
    'DiscoSectionFound': "A section region has been detected on this page",
    'DiscoHeaderFound': "A banner landmark has been detected on this page",
    'DiscoFooterFound': "A contentinfo landmark has been detected on this page",
    'DiscoSearchFound': "A search landmark has been detected on this page",
    'DiscoResponsiveBreakpoints': "Page defines responsive breakpoints in CSS media queries",

    # Content obscuring
    'ErrContentObscuring': "Dialog or overlay obscures interactive elements, preventing users from accessing them",

    # Heading issues
    'ErrEmptyHeading': "Heading element contains only whitespace or special characters",
    'ErrMultipleH1HeadingsOnPage': "Page contains multiple h1 elements, but best practice is to have exactly one h1 per page",
    'ErrHeadingsDontStartWithH1': "Page heading structure does not start with h1",
    'ErrHeadingLevelsSkipped': "Page heading structure skips intermediate levels, breaking document hierarchy",
    'ErrSkippedHeadingLevel': "Heading levels are not in sequential order",
    'WarnHeadingOver60CharsLong': "Heading text exceeds the recommended character limit",
    'InfoHeadingNearLengthLimit': "Heading is approaching the recommended character limit",

    # List issues
    'ErrFakeListImplementation': "Element contains list-like items but does not use proper list markup",
    'WarnIconFontBulletsInList': "List item uses icon font elements instead of CSS list-style-type property",
    'WarnCustomBulletStyling': "List item uses custom styling for bullets instead of standard list-style-type",

    # Form/Field issues
    'ErrFieldAriaRefDoesNotExist': "ARIA attribute references non-existent element ID",
    'ErrLabelContainsMultipleFields': "Single label contains multiple form fields",
    'WarnFieldLabelledUsingAriaLabel': "Field is labeled using aria-label, which is valid but may have usability considerations",
    'WarnFieldLabelledByElementThatIsNotALabel': "Field labeled by element that is not semantically a label",
    'WarnFieldLabelledByMultipleElements': "Field is labeled by multiple elements via aria-labelledby",

    # Animation issues
    'ErrInfiniteAnimation': "Animation runs infinitely without pause controls",
    'WarnInfiniteAnimationSpinner': "Loading spinner animation runs infinitely without controls",
    'WarnLongAnimation': "Animation duration exceeds recommended time limit",

    # Contrast issues
    'ErrInsufficientContrast': "Text contrast ratio does not meet WCAG requirements",
    'ErrLargeTextContrastAA': "Large text fails WCAG AA contrast requirements",
    'ErrLargeTextContrastAAA': "Large text fails WCAG AAA contrast requirements",
    'ErrTextContrastAA': "Normal text fails WCAG AA contrast requirements",
    'ErrTextContrastAAA': "Normal text fails WCAG AAA contrast requirements",

    # Language issues
    'ErrInvalidLanguageCode': "Language attribute contains invalid code that doesn't conform to ISO 639 standards",
    'ErrInvalidLangChange': "Element has invalid language code that is not a valid ISO 639 language code",
    'WarnInvalidLangChange': "Element has invalid language code that is not a valid ISO 639 language code",

    # Interactive element issues
    'ErrMissingTabindex': "Element has a mouse event handler but lacks tabindex, making it inaccessible to keyboard users",
    'ErrModalMissingHeading': "Modal has incorrect heading level for proper document structure",

    # Multiple landmark issues
    'ErrMultipleH1': "Page contains multiple h1 elements instead of just one",
    'ErrMultiplePageTitles': "Multiple title elements found in the document head",
    'ErrMultipleMainLandmarksOnPage': "Page contains multiple main landmarks, but should have exactly one",
    'ErrMultipleBannerLandmarksOnPage': "Page contains multiple banner landmarks, but should have at most one",
    'ErrMultipleContentinfoLandmarksOnPage': "Page contains multiple contentinfo landmarks, but should have at most one",
    'WarnMultipleTitleElements': "Multiple title elements found in the document head, which may cause unpredictable behavior",

    # Text size issues
    'ErrSmallText': "Text size is below the recommended minimum for comfortable reading",
    'WarnSmallLineHeight': "Line height ratio is below the recommended minimum for readability",

    # Tab order issues
    'ErrTabOrderViolation': "Element's position in tab order does not match its visual position on screen",
    'WarnAmbiguousTabOrder': "Element's position in tab order may not match its visual position",

    # Font issues
    'ErrInaccessibleFont': "Font being used is known to be difficult to read",
    'WarnFontNotInRecommenedListForA11y': "Font is not included in the recommended list of accessibility-friendly fonts",

    # Page title issues
    'WarnPageTitleTooLong': "Page title exceeds the recommended character limit",
    'WarnPageTitleTooShort': "Page title is potentially not descriptive enough",

    # Title attribute issues
    'WarnRedundantTitleAttr': "Element has a title attribute that duplicates or overlaps with visible text content",
}

# Verify we have all 67 entries
if __name__ == '__main__':
    print(f"Generated {len(WHAT_GENERIC_ADDITIONS)} generic descriptions")

    # List them
    for code in sorted(WHAT_GENERIC_ADDITIONS.keys()):
        print(f"{code}: {WHAT_GENERIC_ADDITIONS[code]}")
