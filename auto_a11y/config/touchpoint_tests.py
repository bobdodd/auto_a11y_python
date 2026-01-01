"""
Mapping of individual tests to touchpoints
Generated from ISSUE_CATALOG_BY_TOUCHPOINT.md
"""

# Complete mapping of all test IDs to their touchpoints
TOUCHPOINT_TEST_MAPPING = {
    'headings': [
        'DiscoHeadingWithID',
        'ErrEmptyHeading', 
        'ErrHeadingEmpty',
        'ErrHeadingOrder',
        'ErrMultipleH1',
        'ErrNoH1',
        'ErrSkippedHeadingLevel',
        'InfoHeadingNearLengthLimit',
        'WarnHeadingInsideDisplayNone',
        'WarnHeadingOver60CharsLong',
        'WarnVisualHierarchy',
    ],
    
    'images': [
        'DiscoFoundInlineSvg',
        'DiscoFoundSvgImage',
        'ErrAltOnElementThatDoesntTakeIt',
        'ErrAltTooLong',
        'ErrImageAltContainsHTML',
        'ErrImageWithEmptyAlt',
        'ErrImageWithImgFileExtensionAlt',
        'ErrImageWithURLAsAlt',
        'ErrNoAlt',
        'ErrRedundantAlt',
        'ErrSVGNoAccessibleName',
        'WarnSvgPositiveTabindex',
    ],
    
    'forms': [
        'ErrEmptyLabel',
        'ErrFielLabelledBySomethingNotALabel',
        'ErrFieldAriaRefDoesNotExist',
        'ErrFieldLabelledUsingAriaLabel',
        'ErrFieldReferenceDoesNotExist',
        'ErrFormAriaLabelledByIsBlank',
        'ErrFormAriaLabelledByReferenceDIsHidden',
        'ErrFormAriaLabelledByReferenceDoesNotExist',
        'ErrFormEmptyHasNoChildNodes',
        'ErrFormEmptyHasNoInteractiveElements',
        'ErrFormLandmarkAccessibleNameIsBlank',
        'ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs',
        'ErrFormUsesAriaLabelInsteadOfVisibleElement',
        'ErrFormUsesTitleAttribute',
        'ErrLabelContainsMultipleFields',
        'ErrLabelMismatchOfAccessibleNameAndLabelText',
        'ErrNoLabel',
        'ErrOrphanLabelWithNoId',
        'ErrPlaceholderAsLabel',
        'ErrTitleAsOnlyLabel',
        'InfoFieldLabelledUsingAriaLabel',
        'WarnMissingRequiredIndication',
        'WarnModalMissingAriaLabelledby',
        'WarnNoFieldset',
        'WarnNoLegend',
        'ErrFormLandmarkMustHaveAccessibleName',
        'DiscoNoSubmitButton',
        'WarnGenericButtonText',
        'WarnRequiredNotIndicated',
    ],
    
    'buttons': [
        'ErrButtonEmpty',
        'ErrButtonNoText',
        'ErrButtonNoVisibleFocusRelyingOnColorOnly',
        'ErrButtonFocusContrastFail',
        'ErrButtonOutlineWidthInsufficient',
        'ErrButtonOutlineOffsetInsufficient',
        'ErrButtonFocusObscured',
        'WarnButtonOutlineNoneWithBoxShadow',
        'WarnButtonDefaultFocus',
        'WarnButtonFocusGradientBackground',
        'WarnButtonFocusImageBackground',
        'WarnButtonTextInsufficient',
    ],

    'links': [
        'ErrAnchorTargetTabindex',
        'ErrDocumentLinkMissingFileType',
        'ErrDocumentLinkWrongLanguage',
        'ErrLinkButtonMissingSpaceHandler',
        'ErrLinkColorChangeOnly',
        'ErrLinkFocusContrastFail',
        'ErrLinkImageNoFocusIndicator',
        'ErrLinkOutlineWidthInsufficient',
        'WarnColorOnlyLink',
        'WarnColorOnlyLinkWeakIndicator',
        'WarnGenericDocumentLinkText',
        'WarnLinkDefaultFocus',
        'WarnLinkFocusGradientBackground',
        'WarnLinkLooksLikeButton',
        'WarnLinkOutlineOffsetTooLarge',
        'WarnLinkTransparentOutline',
        'WarnMissingDocumentMetadata',
    ],
    
    'navigation': [
        'ErrDuplicateNavNames',
        'ErrInappropriateMenuRole',
        'ErrNavMissingAccessibleName',
        'WarnNavMissingAccessibleName',
        'ErrNoCurrentPageIndicatorScreenReader',
        'ErrNoCurrentPageIndicatorMagnification',
        'WarnNoCurrentPageIndicator',  # Deprecated
    ],
    
    'colors_contrast': [
        'ErrTextContrastAA',
        'ErrLargeTextContrastAA',
        'ErrTextContrastAAA',
        'ErrLargeTextContrastAAA',
        'WarnTextContrastCannotCalculate',
        'WarnNoColorSchemeSupport',
        'WarnNoContrastSupport',
        'WarnColorOnlyLink',
    ],
    
    'keyboard_navigation': [
        'ErrMissingTabindex',
        'ErrNonInteractiveZeroTabindex',
        'ErrNoFocusIndicator',
        'ErrPositiveTabindex',
        'ErrTabOrderViolation',
        'WarnHighTabindex',
        'WarnModalNoFocusableElements',
        'WarnNegativeTabindex',
    ],
    
    'landmarks': [
        'ErrDuplicateLandmarkWithoutName',
        'ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs',
        'ErrMissingMainLandmark',
        'ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs',
        'WarnContentOutsideLandmarks',
        'WarnMissingBannerLandmark',
        'WarnMissingContentinfoLandmark',
        'WarnUnlabelledRegion',
    ],
    
    'language': [
        'ErrDocumentLinkWrongLanguage',
        'ErrHreflangAttrEmpty',
        'ErrHreflangNotOnLink',
        'ErrIncorrectlyFormattedPrimaryLang',
        'ErrNoDocumentLanguage',
    ],
    
    'tables': [
        'ErrHeaderMissingScope',
        'ErrTableMissingCaption',
        'ErrTableNoColumnHeaders',
        'WarnTableMissingThead',
    ],
    
    'lists': [
        'ErrEmptyList',
        'ErrListitemEmpty',
        'ErrFakeListImplementation',
        'WarnCustomBulletStyling',
        'WarnDeepListNesting',
    ],
    
    'media': [
        'ErrAutoplayWithoutControls',
        'ErrNativeVideoMissingControls',
        'ErrVideoIframeMissingTitle',
        'WarnVideoAutoplay',
        'WarnVideoMutedAutoplay',
    ],
    
    'dialogs': [
        'ErrMissingCloseButton',
        'ErrModalMissingClose',
        'ErrModalNoHeading',
        'ErrModalMissingHeading',
        'ErrModalWithoutEscape',
        'WarnMissingAriaLabelledby',
        'WarnMissingAriaModal',
    ],
    
    'animation': [
        'ErrInfiniteAnimation',
        'ErrNoReducedMotionSupport',
        'WarnLongAnimation',
    ],

    'timers': [
        'ErrTimersWithoutControls',
        'WarnAutoStartTimers',
        'WarnFastInterval',
    ],
    
    'fonts': [
        'DiscoFontFound',
        'ErrSmallText',
        'ErrInaccessibleFont',
        'WarnItalicText',
        'WarnJustifiedText',
        'WarnRightAlignedText',
        'WarnSmallLineHeight',
    ],

    'semantic_structure': [
        'ErrHeaderMissingScope',
        'ErrInvalidTabindex',
        'ErrMissingDocumentType',
        'WarnVisualHierarchy',
    ],
    
    'aria': [
        'ErrAccordionWithoutARIA',
        'ErrCarouselWithoutARIA',
        'ErrClickableWithoutKeyboard',
        'ErrDialogMissingRole',
        'ErrDropdownWithoutARIA',
        'ErrInteractiveElementIssue',
        'ErrMenuWithoutARIA',
        'ErrMissingInteractiveRole',
        'ErrTabpanelWithoutARIA',
        'ErrTooltipWithoutARIA',
        'ErrAriaLabelMayNotBeFoundByVoiceControl',
        'ErrFoundAriaLevelButNoRoleAppliedAtAll',
        'WarnMissingAriaModal',
        'WarnSliderWithoutARIA',
        'WarnSwitchWithoutARIA',
        'WarnTreeviewWithoutARIA',
    ],
    
    'focus_management': [
        'ErrContentObscuring',
        'ErrNoFocusIndicator',
        'ErrNoOutlineOffsetDefined',
        'ErrOutlineIsNoneOnInteractiveElement',
        'WarnZeroOutlineOffset',
    ],
    
    'reading_order': [
        'AI_InfoContentOrder',
        'AI_WarnPossibleReadingOrderIssue',
    ],
    
    'event_handling': [
        'ErrMouseOnlyHandler',
        'ErrTabindexNoVisibleFocus',
        'ErrTabindexChildOfInteractive',
        'ErrTabindexAriaHiddenFocusable',
        'ErrTabindexFocusContrastFail',
        'ErrTabindexOutlineNoneNoBoxShadow',
        'ErrTabindexSingleSideBoxShadow',
        'ErrTabindexOutlineWidthInsufficient',
        'ErrTabindexColorChangeOnly',
        'ErrTabindexTransparentOutline',
        'WarnTabindexDefaultFocus',
        'WarnTabindexNoBorderOutline',
    ],
    
    'accessible_names': [
        'ErrMissingAccessibleName',
        'WarnGenericAccessibleName',
    ],
    
    'maps': [
        'DiscoMapFound',
        'ErrDivMapMissingAttributes',
        'ErrDivMapMissingStructure',
        'ErrMapAriaHidden',
        'ErrMapGenericName',
        'ErrMapMissingTitle',
        'ErrMapRolePresentation',
        'ErrSvgMapMissingName',
        'WarnDivMapNoLandmark',
        'WarnMapPotentialContentHiding',
    ],
    
    'documents': [
        'DiscoPDFLinksFound',
        'ErrDocumentLinkMissingFileType',
        'ErrDocumentLinkWrongLanguage',
        'ErrMissingDocumentType',
        'WarnGenericDocumentLinkText',
        'WarnMissingDocumentMetadata',
    ],
    
    'touch_mobile': [
        # No specific tests mapped yet
    ],
    
    'iframes': [
        'ErrVideoIframeMissingTitle',
    ],

    'page': [
        'DiscoResponsiveBreakpoints',
        'ErrEmptyPageTitle',
        'ErrMultiplePageTitles',
        'ErrNoPageTitle',
        'WarnMultipleTitleElements',  # Deprecated - use ErrMultiplePageTitles
        'WarnPageTitleTooLong',
        'WarnPageTitleTooShort',
    ],

    'title_attributes': [
        'ErrEmptyTitleAttr',
        'ErrImproperTitleAttribute',
        'ErrTitleAttrFound',
        'WarnRedundantTitleAttr',
        'WarnVagueTitleAttribute',
    ],
}

def get_tests_for_touchpoint(touchpoint_id: str) -> list:
    """Get all test IDs for a given touchpoint"""
    return TOUCHPOINT_TEST_MAPPING.get(touchpoint_id, [])

def get_touchpoint_for_test(test_id: str) -> str:
    """Find which touchpoint a test belongs to"""
    for touchpoint, tests in TOUCHPOINT_TEST_MAPPING.items():
        if test_id in tests:
            return touchpoint
    return 'general'

def get_all_test_ids() -> set:
    """Get all unique test IDs across all touchpoints"""
    all_tests = set()
    for tests in TOUCHPOINT_TEST_MAPPING.values():
        all_tests.update(tests)
    return all_tests