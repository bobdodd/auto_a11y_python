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
        'ErrIncorrectHeadingLevel',
        'ErrModalMissingHeading',
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
        'ErrImageWithNoAlt',
        'ErrImageWithURLAsAlt',
        'ErrNoAlt',
        'ErrRedundantAlt',
        'ErrSVGNoAccessibleName',
        'ErrSvgImageNoLabel',
        'WarnSVGNoRole',
        'WarnSvgPositiveTabindex',
    ],
    
    'forms': [
        'ErrEmptyLabel',
        'ErrFielLabelledBySomethingNotALabel',
        'ErrFieldAriaRefDoesNotExist',
        'ErrFieldLabelledUsinAriaLabel',
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
        'ErrUnlabelledField',
        'InfoFieldLabelledUsingAriaLabel',
        'WarnMissingAriaLabelledby',
        'WarnMissingRequiredIndication',
        'WarnModalMissingAriaLabelledby',
        'WarnNoFieldset',
        'WarnNoLegend',
        'WarnUnlabelledForm',
        'WarnUnlabelledRegion',
        'forms_ErrNoButtonText',
    ],
    
    'buttons': [
        'ErrButtonEmpty',
        'ErrButtonNoText',
        'ErrMissingCloseButton',
        'WarnButtonTextInsufficient',
        'WarnLinkLooksLikeButton',
    ],
    
    'links': [
        'ErrInvalidGenericLinkName',
        'WarnAnchorTargetTabindex',
        'WarnColorOnlyLink',
        'WarnGenericDocumentLinkText',
        'WarnGenericLinkNoImprovement',
    ],
    
    'navigation': [
        'AI_ErrAccordionWithoutARIA',
        'AI_ErrCarouselWithoutARIA',
        'AI_ErrDropdownWithoutARIA',
        'ErrDuplicateNavNames',
        'ErrInappropriateMenuRole',
        'ErrNavMissingAccessibleName',
        'WarnNavMissingAccessibleName',
        'WarnNoCurrentPageIndicator',
    ],
    
    'colors_contrast': [
        'ErrInsufficientContrast',
        'InfoNoColorSchemeSupport',
        'InfoNoContrastSupport',
        'WarnColorOnlyLink',
    ],
    
    'keyboard_navigation': [
        'ErrMissingTabindex',
        'ErrNonInteractiveZeroTabindex',
        'ErrNoFocusIndicator',
        'ErrPositiveTabindex',
        'ErrTabOrderViolation',
        'WarnHighTabindex',
        'WarnMissingNegativeTabindex',
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
    ],
    
    'language': [
        'ErrHreflangAttrEmpty',
        'ErrHreflangNotOnLink',
        'ErrIncorrectlyFormattedPrimaryLang',
        'ErrNoDocumentLanguage',
        'WarnMissingDocumentMetadata',
    ],
    
    'tables': [
        'ErrHeaderMissingScope',
        'ErrTableMissingCaption',
        'ErrTableNoColumnHeaders',
        'WarnTableMissingThead',
    ],
    
    'lists': [
        'ErrEmptyList',
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
        'ErrModalMissingClose',
        'ErrModalMissingHeading',
        'ErrModalWithoutEscape',
        'WarnMissingAriaModal',
        'WarnModalMissingAriaModal',
    ],
    
    'animation': [
        'ErrAutoStartTimers',
        'ErrInfiniteAnimation',
        'ErrNoReducedMotionSupport',
        'WarnFastInterval',
        'WarnLongAnimation',
    ],
    
    'timing': [
        'ErrTimersWithoutControls',
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
        'ErrImproperTitleAttribute',
        'ErrMissingDocumentType',
        'WarnVisualHierarchy',
    ],
    
    'aria': [
        'AI_ErrMissingInteractiveRole',
        'ErrFoundAriaLevelButNoRoleAppliedAtAll',
        'ErrMapAriaHidden',
        'WarnMissingAriaModal',
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
    ],
    
    'accessible_names': [
        'ErrMissingAccessibleName',
        'WarnGenericAccessibleName',
    ],
    
    'maps': [
        'ErrDivMapMissingAttributes',
        'ErrMapMissingTitle',
    ],
    
    'documents': [
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