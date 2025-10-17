"""
Accessibility Touchpoints System

This module defines the accessibility touchpoints that organize all tests 
(both JavaScript DOM tests and AI visual analysis) into logical categories
that represent different aspects of web accessibility.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


class TouchpointID(Enum):
    """Enumeration of all accessibility touchpoints"""
    ACCESSIBLE_NAMES = "accessible_names"
    ANIMATION = "animation"
    BUTTONS = "buttons"
    COLORS = "colors"
    DIALOGS = "dialogs"
    ELECTRONIC_DOCUMENTS = "electronic_documents"
    EVENT_HANDLING = "event_handling"
    FLOATING_CONTENT = "floating_content"
    FOCUS_MANAGEMENT = "focus_management"
    FONTS = "fonts"
    FORMS = "forms"
    STYLES = "styles"
    HEADINGS = "headings"
    IMAGES = "images"
    LANDMARKS = "landmarks"
    LANGUAGE = "language"
    LINKS = "links"
    LISTS = "lists"
    MAPS = "maps"
    NAVIGATION = "navigation"
    PAGE = "page"
    READ_MORE_LINKS = "read_more_links"
    TABINDEX = "tabindex"
    TITLE_ATTRIBUTES = "title_attributes"
    TABLES = "tables"
    TIMERS = "timers"
    VIDEOS = "videos"


@dataclass
class Touchpoint:
    """Definition of an accessibility touchpoint"""
    id: TouchpointID
    name: str
    description: str
    js_tests: List[str]  # JavaScript test files that belong to this touchpoint
    ai_tests: List[str]  # AI analysis types that belong to this touchpoint
    wcag_criteria: List[str]  # Related WCAG success criteria
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert touchpoint to dictionary"""
        return {
            'id': self.id.value,
            'name': self.name,
            'description': self.description,
            'js_tests': self.js_tests,
            'ai_tests': self.ai_tests,
            'wcag_criteria': self.wcag_criteria
        }


# Define all touchpoints with their associated tests
TOUCHPOINTS = {
    TouchpointID.ACCESSIBLE_NAMES: Touchpoint(
        id=TouchpointID.ACCESSIBLE_NAMES,
        name="Accessible Names",
        description="Ensures all interactive elements have appropriate accessible names for assistive technology",
        js_tests=["accessibleName.js", "ariaRoles.js"],
        ai_tests=["accessible_name_visual"],
        wcag_criteria=["4.1.2", "2.4.4", "1.1.1", "3.3.2"]
    ),
    
    TouchpointID.ANIMATION: Touchpoint(
        id=TouchpointID.ANIMATION,
        name="Animation",
        description="Detects and evaluates animations, auto-playing content, and motion that may cause issues",
        js_tests=[],  # No direct JS tests for animation
        ai_tests=["animation_detection", "auto_play_content", "parallax_scrolling"],
        wcag_criteria=["2.2.2", "2.3.1", "2.3.3"]
    ),

    TouchpointID.BUTTONS: Touchpoint(
        id=TouchpointID.BUTTONS,
        name="Buttons",
        description="Evaluates button focus indicators and keyboard accessibility",
        js_tests=["buttons.js"],
        ai_tests=[],
        wcag_criteria=["2.4.7"]
    ),
    
    TouchpointID.COLORS: Touchpoint(
        id=TouchpointID.COLORS,
        name="Colors and Contrast",
        description="Verifies text and UI components meet WCAG color contrast requirements and ensures color is not the only means of conveying information",
        js_tests=["colorContrast.js", "color.js"],
        ai_tests=["contrast_visual_check", "color_only_information"],
        wcag_criteria=["1.4.1", "1.4.3", "1.4.6", "1.4.11"]
    ),
    
    TouchpointID.DIALOGS: Touchpoint(
        id=TouchpointID.DIALOGS,
        name="Dialogs",
        description="Evaluates modal dialogs, pop-ups, and overlay accessibility",
        js_tests=[],  # Will be detected through ARIA roles
        ai_tests=["modal_accessibility", "dialog_focus_trap"],
        wcag_criteria=["2.1.2", "2.4.3", "1.3.1"]
    ),
    
    TouchpointID.ELECTRONIC_DOCUMENTS: Touchpoint(
        id=TouchpointID.ELECTRONIC_DOCUMENTS,
        name="Electronic Documents",
        description="Checks accessibility of PDFs, Word docs, and other downloadable documents",
        js_tests=["pdf.js"],
        ai_tests=["document_accessibility"],
        wcag_criteria=["1.1.1", "1.3.1", "2.4.2"]
    ),
    
    TouchpointID.EVENT_HANDLING: Touchpoint(
        id=TouchpointID.EVENT_HANDLING,
        name="Event Handling",
        description="Verifies keyboard and mouse event handling for interactive elements",
        js_tests=[],  # Covered by focus and forms tests
        ai_tests=["event_handler_detection"],
        wcag_criteria=["2.1.1", "2.1.3", "2.5.1"]
    ),
    
    TouchpointID.FLOATING_CONTENT: Touchpoint(
        id=TouchpointID.FLOATING_CONTENT,
        name="Floating Content",
        description="Evaluates sticky headers, floating buttons, and fixed position elements",
        js_tests=[],  # No direct JS test
        ai_tests=["floating_element_detection", "sticky_content_analysis"],
        wcag_criteria=["2.4.1", "1.4.10", "2.5.5"]
    ),
    
    TouchpointID.FOCUS_MANAGEMENT: Touchpoint(
        id=TouchpointID.FOCUS_MANAGEMENT,
        name="Focus Management",
        description="Ensures proper focus indicators, tab order, and keyboard navigation",
        js_tests=["focus.js", "tabindex.js"],
        ai_tests=["focus_order_visual", "focus_indicator_visibility"],
        wcag_criteria=["2.4.3", "2.4.7", "2.1.1", "2.1.2"]
    ),
    
    TouchpointID.FONTS: Touchpoint(
        id=TouchpointID.FONTS,
        name="Fonts",
        description="Evaluates font readability, size, and icon fonts accessibility",
        js_tests=["fonts.js"],
        ai_tests=["font_readability", "icon_font_detection"],
        wcag_criteria=["1.4.4", "1.4.12"]
    ),

    TouchpointID.STYLES: Touchpoint(
        id=TouchpointID.STYLES,
        name="Inline Styles",
        description="Evaluates inline style attributes for proper separation of presentation from content",
        js_tests=[],
        ai_tests=[],
        wcag_criteria=["1.4.3", "1.4.8", "1.4.12"]
    ),

    TouchpointID.FORMS: Touchpoint(
        id=TouchpointID.FORMS,
        name="Forms",
        description="Comprehensive form accessibility including labels, errors, and validation",
        js_tests=["forms2.js", "forms_enhanced.js"],
        ai_tests=["form_visual_labels", "error_identification"],
        wcag_criteria=["3.3.1", "3.3.2", "3.3.3", "3.3.4", "1.3.1", "4.1.2"]
    ),
    
    TouchpointID.HEADINGS: Touchpoint(
        id=TouchpointID.HEADINGS,
        name="Headings",
        description="Validates heading hierarchy, structure, and visual headings",
        js_tests=["headings.js"],
        ai_tests=["visual_heading_detection", "heading_hierarchy"],
        wcag_criteria=["1.3.1", "2.4.6"]
    ),
    
    TouchpointID.IMAGES: Touchpoint(
        id=TouchpointID.IMAGES,
        name="Images",
        description="Checks image alt text, decorative images, and complex graphics",
        js_tests=["images.js", "svg.js"],
        ai_tests=["image_text_detection", "complex_image_analysis"],
        wcag_criteria=["1.1.1", "1.4.5", "1.4.9"]
    ),
    
    TouchpointID.LANDMARKS: Touchpoint(
        id=TouchpointID.LANDMARKS,
        name="Landmarks",
        description="Evaluates ARIA landmarks and page regions",
        js_tests=["landmarks.js"],
        ai_tests=["landmark_visual_mapping"],
        wcag_criteria=["1.3.1", "2.4.1", "4.1.2"]
    ),
    
    TouchpointID.LANGUAGE: Touchpoint(
        id=TouchpointID.LANGUAGE,
        name="Language",
        description="Verifies language declarations and changes",
        js_tests=["language.js"],
        ai_tests=["language_change_detection"],
        wcag_criteria=["3.1.1", "3.1.2"]
    ),
    
    TouchpointID.LISTS: Touchpoint(
        id=TouchpointID.LISTS,
        name="Lists",
        description="Validates list structure and semantics",
        js_tests=[],  # Will add list.js
        ai_tests=["visual_list_detection"],
        wcag_criteria=["1.3.1"]
    ),
    
    TouchpointID.MAPS: Touchpoint(
        id=TouchpointID.MAPS,
        name="Maps",
        description="Evaluates interactive maps and geographic content accessibility",
        js_tests=[],  # No direct JS test
        ai_tests=["map_accessibility", "map_alternative_text"],
        wcag_criteria=["1.1.1", "2.1.1", "1.4.1"]
    ),

    TouchpointID.PAGE: Touchpoint(
        id=TouchpointID.PAGE,
        name="Page",
        description="Validates page-level structure including page title element and document metadata",
        js_tests=["pageTitle.js"],
        ai_tests=[],
        wcag_criteria=["2.4.2"]
    ),

    TouchpointID.READ_MORE_LINKS: Touchpoint(
        id=TouchpointID.READ_MORE_LINKS,
        name="Read More Links",
        description="Identifies and evaluates ambiguous link text",
        js_tests=[],  # Covered in accessible names
        ai_tests=["ambiguous_link_detection"],
        wcag_criteria=["2.4.4", "2.4.9"]
    ),

    TouchpointID.LINKS: Touchpoint(
        id=TouchpointID.LINKS,
        name="Links",
        description="Evaluates link accessibility including focus indicators, descriptive text, keyboard support, and document links",
        js_tests=["links.js"],
        ai_tests=[],
        wcag_criteria=["2.4.4", "2.4.9", "3.1.2", "3.2.4"]
    ),

    TouchpointID.NAVIGATION: Touchpoint(
        id=TouchpointID.NAVIGATION,
        name="Navigation",
        description="Evaluates navigation menus, landmarks, and accessible names for navigation elements",
        js_tests=["navigation.js"],
        ai_tests=[],
        wcag_criteria=["2.4.1", "4.1.2"]
    ),

    TouchpointID.TABINDEX: Touchpoint(
        id=TouchpointID.TABINDEX,
        name="Tabindex",
        description="Validates tabindex usage and keyboard navigation order",
        js_tests=["tabindex.js"],
        ai_tests=["tab_order_visual"],
        wcag_criteria=["2.4.3", "2.1.1"]
    ),
    
    TouchpointID.TITLE_ATTRIBUTES: Touchpoint(
        id=TouchpointID.TITLE_ATTRIBUTES,
        name="Title Attributes",
        description="Evaluates proper use of HTML title attributes for tooltips and supplementary information",
        js_tests=["titleAttr.js"],
        ai_tests=[],
        wcag_criteria=["3.3.2"]
    ),
    
    TouchpointID.TABLES: Touchpoint(
        id=TouchpointID.TABLES,
        name="Tables",
        description="Validates data table structure, headers, and relationships",
        js_tests=[],  # Will add tables.js
        ai_tests=["table_structure_analysis", "table_header_detection"],
        wcag_criteria=["1.3.1", "1.3.2"]
    ),
    
    TouchpointID.TIMERS: Touchpoint(
        id=TouchpointID.TIMERS,
        name="Timers",
        description="Detects and evaluates time limits and session timeouts",
        js_tests=[],  # No direct JS test
        ai_tests=["timer_detection", "timeout_warning"],
        wcag_criteria=["2.2.1", "2.2.3", "2.2.6"]
    ),
    
    TouchpointID.VIDEOS: Touchpoint(
        id=TouchpointID.VIDEOS,
        name="Videos",
        description="Checks video accessibility including captions, controls, and audio descriptions",
        js_tests=[],  # Will add video.js
        ai_tests=["video_caption_detection", "video_control_accessibility"],
        wcag_criteria=["1.2.1", "1.2.2", "1.2.3", "1.2.5", "1.4.2"]
    )
}


class TouchpointMapper:
    """Maps test results to touchpoints"""
    
    # Mapping from old categories to new touchpoints
    CATEGORY_TO_TOUCHPOINT = {
        # Old category -> New touchpoint
        'heading': TouchpointID.HEADINGS,
        'headings': TouchpointID.HEADINGS,
        'image': TouchpointID.IMAGES,
        'images': TouchpointID.IMAGES,
        'form': TouchpointID.FORMS,
        'forms': TouchpointID.FORMS,
        'landmark': TouchpointID.LANDMARKS,
        'landmarks': TouchpointID.LANDMARKS,
        'color': TouchpointID.COLORS,
        'colors': TouchpointID.COLORS,
        'color_use': TouchpointID.COLORS,
        'contrast': TouchpointID.COLORS,
        'color_contrast': TouchpointID.COLORS,
        'colorcontrast': TouchpointID.COLORS,
        'colorsandcontrast': TouchpointID.COLORS,
        'focus': TouchpointID.FOCUS_MANAGEMENT,
        'focus_management': TouchpointID.FOCUS_MANAGEMENT,
        'language': TouchpointID.LANGUAGE,
        'lang': TouchpointID.LANGUAGE,
        'button': TouchpointID.FORMS,  # Buttons are part of forms
        'buttons': TouchpointID.FORMS,
        'link': TouchpointID.LINKS,
        'links': TouchpointID.LINKS,
        'page': TouchpointID.PAGE,
        'title': TouchpointID.TITLE_ATTRIBUTES,
        'title_attribute': TouchpointID.TITLE_ATTRIBUTES,
        'title_attributes': TouchpointID.TITLE_ATTRIBUTES,
        'titleattr': TouchpointID.TITLE_ATTRIBUTES,
        'tabindex': TouchpointID.TABINDEX,
        'aria': TouchpointID.ACCESSIBLE_NAMES,  # ARIA is about accessible names
        'svg': TouchpointID.IMAGES,
        'pdf': TouchpointID.ELECTRONIC_DOCUMENTS,
        'font': TouchpointID.FONTS,
        'fonts': TouchpointID.FONTS,
        'javascript': TouchpointID.EVENT_HANDLING,
        'event_handling': TouchpointID.EVENT_HANDLING,
        'event_handlers': TouchpointID.EVENT_HANDLING,
        'style': TouchpointID.STYLES,
        'styles': TouchpointID.STYLES,
        'navigation': TouchpointID.NAVIGATION,
        'modal': TouchpointID.DIALOGS,
        'dialog': TouchpointID.DIALOGS,
        'animation': TouchpointID.ANIMATION,
        'timer': TouchpointID.TIMERS,
        'video': TouchpointID.VIDEOS,
        'table': TouchpointID.TABLES,
        'list': TouchpointID.LISTS,
        'map': TouchpointID.MAPS,
        'other': TouchpointID.ACCESSIBLE_NAMES,  # Default fallback
    }
    
    # Mapping from error codes to touchpoints
    ERROR_CODE_TO_TOUCHPOINT = {
        # Heading errors
        'ErrEmptyHeading': TouchpointID.HEADINGS,
        'ErrHeadingOrder': TouchpointID.HEADINGS,
        'ErrH1Missing': TouchpointID.HEADINGS,
        'ErrMultipleH1': TouchpointID.HEADINGS,
        'ErrSkippedHeadingLevel': TouchpointID.HEADINGS,
        'ErrNoH1': TouchpointID.HEADINGS,
        'ErrIncorrectHeadingLevel': TouchpointID.HEADINGS,
        'ErrModalMissingHeading': TouchpointID.DIALOGS,  # Modal-specific heading issue
        'WarnHeadingInsideDisplayNone': TouchpointID.HEADINGS,
        'WarnHeadingOver60CharsLong': TouchpointID.HEADINGS,
        'WarnVisualHierarchy': TouchpointID.HEADINGS,
        'InfoHeadingNearLengthLimit': TouchpointID.HEADINGS,
        'DiscoHeadingWithID': TouchpointID.HEADINGS,
        
        # Image errors  
        'ErrNoAlt': TouchpointID.IMAGES,
        'ErrImageWithNoAlt': TouchpointID.IMAGES,
        'ErrImageWithEmptyAlt': TouchpointID.IMAGES,
        'ErrAltTooLong': TouchpointID.IMAGES,
        'ErrRedundantAlt': TouchpointID.IMAGES,
        'ErrImageAltContainsHTML': TouchpointID.IMAGES,
        'ErrImageWithImgFileExtensionAlt': TouchpointID.IMAGES,
        'ErrImageWithURLAsAlt': TouchpointID.IMAGES,
        'ErrAltOnElementThatDoesntTakeIt': TouchpointID.IMAGES,
        'ErrSVGNoAccessibleName': TouchpointID.IMAGES,
        'WarnSVGNoRole': TouchpointID.IMAGES,
        'WarnSvgPositiveTabindex': TouchpointID.IMAGES,
        'DiscoFoundInlineSvg': TouchpointID.IMAGES,
        'DiscoFoundSvgImage': TouchpointID.IMAGES,
        
        # Form errors
        'ErrNoLabel': TouchpointID.FORMS,
        'ErrEmptyLabel': TouchpointID.FORMS,
        'ErrPlaceholderAsLabel': TouchpointID.FORMS,
        'ErrUnlabelledField': TouchpointID.FORMS,
        'ErrButtonEmpty': TouchpointID.ACCESSIBLE_NAMES,  # Buttons need accessible names
        'ErrButtonNoText': TouchpointID.ACCESSIBLE_NAMES,  # Buttons need text for accessibility
        'ErrButtonOutlineNoneNoBoxShadow': TouchpointID.BUTTONS,  # Button focus indicators
        'ErrButtonFocusContrastFail': TouchpointID.BUTTONS,  # Button focus indicators
        'ErrButtonOutlineWidthInsufficient': TouchpointID.BUTTONS,  # Button focus indicators
        'ErrButtonOutlineOffsetInsufficient': TouchpointID.BUTTONS,  # Button focus indicators
        'ErrButtonFocusObscured': TouchpointID.BUTTONS,  # Button focus indicators
        'WarnButtonOutlineNoneWithBoxShadow': TouchpointID.BUTTONS,  # Button focus indicators
        'WarnButtonDefaultFocus': TouchpointID.BUTTONS,  # Button focus indicators
        'WarnButtonFocusGradientBackground': TouchpointID.BUTTONS,  # Button focus indicators
        'WarnButtonFocusImageBackground': TouchpointID.BUTTONS,  # Button focus indicators
        'ErrMissingCloseButton': TouchpointID.DIALOGS,  # Close button is for dialogs
        'WarnButtonTextInsufficient': TouchpointID.ACCESSIBLE_NAMES,  # Button text quality is about naming
        'WarnMissingRequiredIndication': TouchpointID.FORMS,
        'WarnNoFieldset': TouchpointID.FORMS,
        'WarnNoLegend': TouchpointID.FORMS,
        'WarnUnlabelledForm': TouchpointID.FORMS,  # Deprecated, kept for backwards compatibility
        'ErrFormLandmarkMustHaveAccessibleName': TouchpointID.LANDMARKS,  # Forms without names aren't landmarks
        'WarnUnlabelledRegion': TouchpointID.LANDMARKS,  # Regions are landmarks
        'WarnMissingAriaLabelledby': TouchpointID.FORMS,
        'DiscoFormOnPage': TouchpointID.FORMS,
        'DiscoNavFound': TouchpointID.LANDMARKS,  # Navigation is a landmark
        'DiscoAsideFound': TouchpointID.LANDMARKS,  # Complementary is a landmark
        'DiscoSectionFound': TouchpointID.LANDMARKS,  # Section (region) is a landmark
        'DiscoHeaderFound': TouchpointID.LANDMARKS,  # Banner is a landmark
        'DiscoFooterFound': TouchpointID.LANDMARKS,  # Contentinfo is a landmark
        'DiscoSearchFound': TouchpointID.LANDMARKS,  # Search is a landmark
        'forms_DiscoNoSubmitButton': TouchpointID.FORMS,
        'forms_DiscoPlaceholderAsLabel': TouchpointID.FORMS,
        
        # Color/contrast errors
        'ErrInsufficientContrast': TouchpointID.COLORS,
        'ErrTextContrastAA': TouchpointID.COLORS,
        'ErrLargeTextContrastAA': TouchpointID.COLORS,
        'ErrTextContrastAAA': TouchpointID.COLORS,
        'ErrLargeTextContrastAAA': TouchpointID.COLORS,
        'WarnNoColorSchemeSupport': TouchpointID.COLORS,
        'WarnNoContrastSupport': TouchpointID.COLORS,
        'WarnColorOnlyLink': TouchpointID.COLORS,

        # Font/typography errors
        'ErrSmallText': TouchpointID.FONTS,
        'WarnSmallLineHeight': TouchpointID.FONTS,
        'WarnItalicText': TouchpointID.FONTS,
        'WarnJustifiedText': TouchpointID.FONTS,
        'WarnRightAlignedText': TouchpointID.FONTS,
        'WarnVisualHierarchy': TouchpointID.FONTS,
        
        # Focus errors
        'ErrNoFocusIndicator': TouchpointID.FOCUS_MANAGEMENT,
        'ErrContentObscuring': TouchpointID.FOCUS_MANAGEMENT,
        'ErrNoOutlineOffsetDefined': TouchpointID.FOCUS_MANAGEMENT,
        'ErrOutlineIsNoneOnInteractiveElement': TouchpointID.FOCUS_MANAGEMENT,
        'WarnZeroOutlineOffset': TouchpointID.FOCUS_MANAGEMENT,
        
        # Tabindex errors
        'ErrPositiveTabindex': TouchpointID.TABINDEX,
        'ErrTabOrderViolation': TouchpointID.TABINDEX,
        'ErrMissingTabindex': TouchpointID.TABINDEX,
        'ErrNonInteractiveZeroTabindex': TouchpointID.TABINDEX,
        'WarnHighTabindex': TouchpointID.TABINDEX,
        'WarnNegativeTabindex': TouchpointID.TABINDEX,
        'WarnMissingNegativeTabindex': TouchpointID.TABINDEX,
        
        # Accessible name errors
        'ErrMissingAccessibleName': TouchpointID.ACCESSIBLE_NAMES,
        'WarnGenericAccessibleName': TouchpointID.ACCESSIBLE_NAMES,
        'ErrInvalidGenericLinkName': TouchpointID.ACCESSIBLE_NAMES,
        'WarnGenericLinkNoImprovement': TouchpointID.ACCESSIBLE_NAMES,
        
        # Language errors
        'ErrNoDocumentLanguage': TouchpointID.LANGUAGE,
        'ErrIncorrectlyFormattedPrimaryLang': TouchpointID.LANGUAGE,
        'ErrHreflangNotOnLink': TouchpointID.LANGUAGE,
        'ErrHreflangAttrEmpty': TouchpointID.LANGUAGE,
        
        # Page title errors (page <title> element)
        'ErrNoPageTitle': TouchpointID.PAGE,
        'ErrEmptyPageTitle': TouchpointID.PAGE,
        'ErrMultiplePageTitles': TouchpointID.PAGE,
        'WarnPageTitleTooShort': TouchpointID.PAGE,
        'WarnPageTitleTooLong': TouchpointID.PAGE,
        'ErrImproperTitleAttribute': TouchpointID.TITLE_ATTRIBUTES,
        'ErrEmptyTitleAttr': TouchpointID.TITLE_ATTRIBUTES,
        'ErrTitleAsOnlyLabel': TouchpointID.TITLE_ATTRIBUTES,
        'ErrTitleAttrFound': TouchpointID.TITLE_ATTRIBUTES,
        'WarnRedundantTitleAttr': TouchpointID.TITLE_ATTRIBUTES,
        'WarnVagueTitleAttribute': TouchpointID.TITLE_ATTRIBUTES,

        # Landmark errors
        'ErrMissingMainLandmark': TouchpointID.LANDMARKS,
        'ErrDuplicateLandmarkWithoutName': TouchpointID.LANDMARKS,
        'WarnMissingBannerLandmark': TouchpointID.LANDMARKS,
        'WarnMissingContentinfoLandmark': TouchpointID.LANDMARKS,
        'WarnContentOutsideLandmarks': TouchpointID.LANDMARKS,
        
        # Document link errors (for downloadable documents)
        'DiscoPDFLinksFound': TouchpointID.ELECTRONIC_DOCUMENTS,
        'WarnGenericDocumentLinkText': TouchpointID.ELECTRONIC_DOCUMENTS,
        'ErrDocumentLinkMissingFileType': TouchpointID.ELECTRONIC_DOCUMENTS,
        'ErrDocumentLinkWrongLanguage': TouchpointID.ELECTRONIC_DOCUMENTS,
        'WarnMissingDocumentMetadata': TouchpointID.ELECTRONIC_DOCUMENTS,

        # Link errors
        'ErrAnchorTargetTabindex': TouchpointID.LINKS,
        'ErrLinkButtonMissingSpaceHandler': TouchpointID.LINKS,
        'ErrLinkColorChangeOnly': TouchpointID.LINKS,
        'ErrLinkFocusContrastFail': TouchpointID.LINKS,
        'ErrLinkImageNoFocusIndicator': TouchpointID.LINKS,
        'ErrLinkOpensNewWindowNoWarning': TouchpointID.LINKS,
        'ErrLinkOutlineWidthInsufficient': TouchpointID.LINKS,
        'ErrLinkTextNotDescriptive': TouchpointID.LINKS,
        'WarnColorOnlyLinkWeakIndicator': TouchpointID.LINKS,
        'WarnLinkDefaultFocus': TouchpointID.LINKS,
        'WarnLinkFocusGradientBackground': TouchpointID.LINKS,
        'WarnLinkLooksLikeButton': TouchpointID.LINKS,
        'WarnLinkOutlineOffsetTooLarge': TouchpointID.LINKS,
        'WarnLinkTransparentOutline': TouchpointID.LINKS,

        # Navigation errors
        'AI_ErrAccordionWithoutARIA': TouchpointID.NAVIGATION,
        'AI_ErrCarouselWithoutARIA': TouchpointID.NAVIGATION,
        'AI_ErrDropdownWithoutARIA': TouchpointID.NAVIGATION,
        'ErrNavMissingAccessibleName': TouchpointID.NAVIGATION,
        'WarnNavMissingAccessibleName': TouchpointID.NAVIGATION,
        'ErrInappropriateMenuRole': TouchpointID.NAVIGATION,

        # Semantic structure errors (for HTML DOCTYPE) - use PAGE for document-level structure
        'ErrMissingDocumentType': TouchpointID.PAGE,
        
        # Modal/Dialog errors
        'ErrModalMissingClose': TouchpointID.DIALOGS,
        'ErrModalWithoutEscape': TouchpointID.DIALOGS,
        'WarnMissingAriaModal': TouchpointID.DIALOGS,
        'WarnModalMissingAriaLabelledby': TouchpointID.DIALOGS,
        'WarnModalMissingAriaModal': TouchpointID.DIALOGS,
        'WarnModalNoFocusableElements': TouchpointID.DIALOGS,
        
        # Animation/Timer errors
        'ErrAutoStartTimers': TouchpointID.TIMERS,
        'ErrTimersWithoutControls': TouchpointID.TIMERS,
        'WarnFastInterval': TouchpointID.TIMERS,
        'ErrInfiniteAnimation': TouchpointID.ANIMATION,
        'ErrNoReducedMotionSupport': TouchpointID.ANIMATION,
        'WarnLongAnimation': TouchpointID.ANIMATION,
        
        # Event handling errors
        'ErrMouseOnlyHandler': TouchpointID.EVENT_HANDLING,
        
        # Font errors
        'DiscoFontFound': TouchpointID.FONTS,
        'WarnItalicText': TouchpointID.FONTS,
        'WarnJustifiedText': TouchpointID.FONTS,
        'WarnRightAlignedText': TouchpointID.FONTS,
        'WarnSmallLineHeight': TouchpointID.FONTS,
        
        # Table errors
        'ErrHeaderMissingScope': TouchpointID.TABLES,
        'ErrTableMissingCaption': TouchpointID.TABLES,
        'ErrTableNoColumnHeaders': TouchpointID.TABLES,
        'WarnTableMissingThead': TouchpointID.TABLES,
        
        # List errors
        'ErrEmptyList': TouchpointID.LISTS,
        'ErrFakeListImplementation': TouchpointID.LISTS,
        'WarnCustomBulletStyling': TouchpointID.LISTS,
        'WarnDeepListNesting': TouchpointID.LISTS,
        
        # Map errors
        'ErrMapMissingTitle': TouchpointID.MAPS,
        'ErrDivMapMissingAttributes': TouchpointID.MAPS,
        
        # Video/Media errors
        'ErrVideoIframeMissingTitle': TouchpointID.VIDEOS,
        'ErrNativeVideoMissingControls': TouchpointID.VIDEOS,
        'WarnVideoAutoplay': TouchpointID.VIDEOS,

        # Navigation-related errors mapped to LANDMARKS
        'ErrDuplicateNavNames': TouchpointID.LANDMARKS,  # This is about duplicate landmark names
        'WarnNoCurrentPageIndicator': TouchpointID.LANDMARKS,  # Current page indicator is navigation structure

        # Link-specific errors for accessible names and readability
        'WarnAnchorTargetTabindex': TouchpointID.TABINDEX,  # This is about tabindex, not names
        'ErrEmptyLink': TouchpointID.ACCESSIBLE_NAMES,  # Links need accessible text
        'WarnAmbiguousLinkText': TouchpointID.READ_MORE_LINKS,  # Ambiguous link text issue

        # ARIA errors (map to appropriate touchpoints based on context)
        'AI_ErrMissingInteractiveRole': TouchpointID.ACCESSIBLE_NAMES,
        'ErrAriaLabelMayNotBeFoundByVoiceControl': TouchpointID.ACCESSIBLE_NAMES,  # WCAG 2.5.3 Label in Name
        'ErrMapAriaHidden': TouchpointID.MAPS,  # This is specifically about maps
        
        # AI-detected content order/reading issues
        'AI_InfoContentOrder': TouchpointID.HEADINGS,
        'AI_WarnPossibleReadingOrderIssue': TouchpointID.HEADINGS,
        
        # Style errors and warnings
        'ErrStyleAttrColorFont': TouchpointID.STYLES,
        'WarnStyleAttrOther': TouchpointID.STYLES,
        'ErrStyleTagColorFont': TouchpointID.STYLES,
        'WarnStyleTagOther': TouchpointID.STYLES,

        # Style/JavaScript discovery items (these are just discoveries, not specific issues)
        'DiscoFoundJS': TouchpointID.EVENT_HANDLING,
        'DiscoStyleAttrOnElements': TouchpointID.STYLES,  # Old code, moved to styles touchpoint
        'DiscoStyleElementOnPage': TouchpointID.STYLES,  # Moved from colors to styles
        'DiscoResponsiveBreakpoints': TouchpointID.PAGE,  # Responsive breakpoints discovery

        # Additional mappings for completeness
        'ErrMissingRole': TouchpointID.ACCESSIBLE_NAMES,  # Missing ARIA role
        'ErrInvalidRole': TouchpointID.ACCESSIBLE_NAMES,  # Invalid ARIA role
        'WarnRedundantRole': TouchpointID.ACCESSIBLE_NAMES,  # Redundant ARIA role
        'ErrAriaHidden': TouchpointID.ACCESSIBLE_NAMES,  # Inappropriate aria-hidden usage
        'WarnPresentationalRole': TouchpointID.ACCESSIBLE_NAMES,  # Role=presentation issues
        'ErrSkipLinkMissing': TouchpointID.LANDMARKS,  # Skip navigation link missing
        'WarnSkipLinkHidden': TouchpointID.LANDMARKS,  # Skip link not visible
        'ErrEmptyParagraph': TouchpointID.HEADINGS,  # Empty content structure
        'WarnLongParagraph': TouchpointID.HEADINGS,  # Content structure issues
        'ErrBrokenSkipLink': TouchpointID.LANDMARKS,  # Skip link doesn't work
        'InfoInteractiveElement': TouchpointID.EVENT_HANDLING,  # Interactive element discovered
        'DiscoScriptElement': TouchpointID.EVENT_HANDLING,  # Script element found
    }
    
    # AI finding types to touchpoints
    AI_TYPE_TO_TOUCHPOINT = {
        'visual_heading': TouchpointID.HEADINGS,
        'heading_mismatch': TouchpointID.HEADINGS,
        'reading_order': TouchpointID.HEADINGS,
        'modal_issue': TouchpointID.DIALOGS,
        'animation_detected': TouchpointID.ANIMATION,
        'contrast_issue': TouchpointID.COLORS,
        'focus_issue': TouchpointID.FOCUS_MANAGEMENT,
        'form_issue': TouchpointID.FORMS,
        'language_change': TouchpointID.LANGUAGE,
        'floating_element': TouchpointID.FLOATING_CONTENT,
        'timer_detected': TouchpointID.TIMERS,
        'video_issue': TouchpointID.VIDEOS,
        'map_issue': TouchpointID.MAPS,
        'table_issue': TouchpointID.TABLES,
        'list_issue': TouchpointID.LISTS,
    }
    
    @classmethod
    def get_touchpoint_for_category(cls, category: str) -> TouchpointID:
        """
        Get touchpoint ID for a given category

        Args:
            category: Old category name

        Returns:
            TouchpointID for the category

        Raises:
            ValueError: If category is not mapped to a touchpoint
        """
        category_lower = category.lower() if category else 'other'
        touchpoint = cls.CATEGORY_TO_TOUCHPOINT.get(category_lower)
        if touchpoint is None:
            raise ValueError(
                f"Category '{category}' is not mapped to a touchpoint. "
                f"Add mapping in TouchpointManager.CATEGORY_TO_TOUCHPOINT. "
                f"Available categories: {list(cls.CATEGORY_TO_TOUCHPOINT.keys())}"
            )
        return touchpoint
    
    @classmethod
    def get_touchpoint_for_error_code(cls, error_code: str) -> Optional[TouchpointID]:
        """
        Get touchpoint ID for a specific error code
        
        Args:
            error_code: Error code (e.g., 'ErrEmptyHeading')
            
        Returns:
            TouchpointID for the error code, or None if not mapped
        """
        return cls.ERROR_CODE_TO_TOUCHPOINT.get(error_code)
    
    @classmethod
    def get_touchpoint_for_ai_type(cls, ai_type: str) -> TouchpointID:
        """
        Get touchpoint ID for an AI finding type
        
        Args:
            ai_type: AI finding type
            
        Returns:
            TouchpointID for the AI finding
        """
        return cls.AI_TYPE_TO_TOUCHPOINT.get(
            ai_type,
            TouchpointID.ACCESSIBLE_NAMES  # Default
        )
    
    @classmethod
    def map_violation_to_touchpoint(cls, violation: Dict[str, Any]) -> TouchpointID:
        """
        Map a violation to its appropriate touchpoint
        
        Args:
            violation: Violation dictionary
            
        Returns:
            TouchpointID for the violation
        """
        # First try to map by error code if available
        if 'id' in violation:
            touchpoint = cls.get_touchpoint_for_error_code(violation['id'])
            if touchpoint:
                return touchpoint
        
        # Fall back to category mapping
        category = violation.get('category', 'other')
        return cls.get_touchpoint_for_category(category)
    
    @classmethod
    def map_ai_finding_to_touchpoint(cls, ai_finding: Dict[str, Any]) -> TouchpointID:
        """
        Map an AI finding to its appropriate touchpoint
        
        Args:
            ai_finding: AI finding dictionary
            
        Returns:
            TouchpointID for the AI finding
        """
        ai_type = ai_finding.get('type', '')
        return cls.get_touchpoint_for_ai_type(ai_type)


def get_touchpoint(touchpoint_id: TouchpointID) -> Touchpoint:
    """
    Get a touchpoint by its ID
    
    Args:
        touchpoint_id: TouchpointID enum value
        
    Returns:
        Touchpoint instance
    """
    return TOUCHPOINTS.get(touchpoint_id)


def get_all_touchpoints() -> List[Touchpoint]:
    """
    Get all touchpoints
    
    Returns:
        List of all touchpoint instances
    """
    return list(TOUCHPOINTS.values())


def get_touchpoints_for_js_test(js_test_file: str) -> List[TouchpointID]:
    """
    Get touchpoints that include a specific JavaScript test
    
    Args:
        js_test_file: JavaScript test filename
        
    Returns:
        List of TouchpointIDs that include this test
    """
    touchpoints = []
    for touchpoint_id, touchpoint in TOUCHPOINTS.items():
        if js_test_file in touchpoint.js_tests:
            touchpoints.append(touchpoint_id)
    return touchpoints


def get_touchpoints_for_ai_test(ai_test_type: str) -> List[TouchpointID]:
    """
    Get touchpoints that include a specific AI test type
    
    Args:
        ai_test_type: AI test type identifier
        
    Returns:
        List of TouchpointIDs that include this test
    """
    touchpoints = []
    for touchpoint_id, touchpoint in TOUCHPOINTS.items():
        if ai_test_type in touchpoint.ai_tests:
            touchpoints.append(touchpoint_id)
    return touchpoints