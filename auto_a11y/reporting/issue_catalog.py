"""
Accessibility Issue Catalog
Generated from ISSUE_CATALOG_TEMPLATE.md
Contains enriched descriptions for all accessibility issues
"""

from typing import Dict, List, Any
from .issue_descriptions_enhanced import get_detailed_issue_description


class IssueCatalog:
    """Catalog of all accessibility issues with enriched descriptions"""
    
    # Issue data dictionary
    ISSUES: Dict[str, Dict[str, Any]] = {
        "ErrImageWithNoAlt": {
            "id": "ErrImageWithNoAlt",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "Images are missing alternative text attributes, preventing assistive technologies from conveying their content or purpose to users",
            "why_it_matters": "Screen readers cannot describe image content to users who are blind or have low vision, creating information barriers that may prevent understanding of essential content, navigation, or task completion. This also affects users with cognitive disabilities who benefit from text alternatives and users on slow connections where images fail to load.",
            "who_it_affects": "Blind users using screen readers, users with low vision using screen readers with magnification, users with cognitive disabilities who rely on text alternatives, voice control users who need text labels to reference elements, and users on slow internet connections",
            "how_to_fix": "Add descriptive alt attributes for informative images (alt=\"Sales chart showing 40% increase\"), use empty alt attributes for decorative images (alt=\"\"), describe the function for interactive images (alt=\"Search\" not alt=\"magnifying glass icon\"), and provide detailed descriptions via aria-describedby for complex images like charts or diagrams."
        },
        "ErrImageWithEmptyAlt": {
            "id": "ErrImageWithEmptyAlt",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "Image alt attribute contains only whitespace characters (spaces, tabs, line breaks), providing no accessible name",
            "why_it_matters": "Whitespace-only alt attributes fail to provide any accessible name for the image, causing screen readers to announce unhelpful fallback information like the image filename or \"unlabeled graphic\". Unlike properly empty alt=\"\" which signals decorative content, whitespace alt text creates ambiguity - users cannot determine if they're missing important information or if the image is decorative.",
            "who_it_affects": "Blind and low vision users relying on screen readers who cannot determine the image's purpose or content, users with cognitive disabilities who depend on clear labeling to understand page content, and users of voice control software who cannot reference images without accessible names",
            "how_to_fix": "Determine the image's purpose and apply appropriate alt text - for informative images add descriptive alternative text that conveys the same information, for decorative images use alt=\"\" (no spaces) to properly mark them as decorative, for functional images describe the action or destination not the appearance, and remove any whitespace-only alt attributes that serve as ineffective placeholders"
        },
        "ErrImageWithImgFileExtensionAlt": {
            "id": "ErrImageWithImgFileExtensionAlt",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "Alt text contains image filename with file extension (e.g., \"photo.jpg\", \"IMG_1234.png\", \"banner.gif\"), providing no meaningful description of the image content",
            "why_it_matters": "Filenames rarely describe image content meaningfully and often contain technical identifiers, underscores, hyphens, or numbers that create a poor listening experience when announced by screen readers. Users hear cryptic strings like \"DSC underscore zero zero four two dot jay peg\" instead of learning what the image actually shows, forcing them to guess at important visual information or miss it entirely.",
            "who_it_affects": "Blind and low vision users using screen readers who need meaningful descriptions to understand visual content, users with cognitive disabilities who rely on clear, descriptive text to process information, users in low-bandwidth situations where images don't load and only alt text is displayed, and search engine users who rely on descriptive alt text for finding relevant content",
            "how_to_fix": "Replace the filename with descriptive text that conveys the image's information or purpose (change alt=\"hero-banner-2.jpg\" to alt=\"Students collaborating in the campus library\"), focus on what the image communicates rather than technical details, ensure the description makes sense when read in context with surrounding content, and avoid including file extensions or technical metadata in alt attributes"
        },
        "ErrAltOnElementThatDoesntTakeIt": {
            "id": "ErrAltOnElementThatDoesntTakeIt",
            "type": "Error",
            "impact": "Low",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "Alt attribute placed on HTML elements that don't support it (such as div, span, p, or other non-image elements), making the alternative text inaccessible to assistive technologies",
            "why_it_matters": "The alt attribute is only valid on specific elements (<img>, <area>, <input type=\"image\">) and is ignored when placed on other elements. Screen readers will not announce this misplaced alt text, meaning any important information it contains is completely lost to users who rely on assistive technologies. This often occurs when developers attempt to add accessibility features but use incorrect techniques.",
            "who_it_affects": "Blind and low vision users using screen readers who cannot access the alternative text content placed in invalid locations, users with cognitive disabilities who may be missing explanatory text, keyboard users who may not receive important contextual information, and users of assistive technologies that rely on proper semantic HTML markup",
            "how_to_fix": "Remove alt attributes from non-supporting elements and use appropriate alternatives - for background images in CSS use role=\"img\" with aria-label, for clickable elements use aria-label or visually hidden text, for decorative elements ensure they're properly hidden with aria-hidden=\"true\", and verify that actual <img> elements are used for content images that need alternative text"
        },
        "DiscoFoundInlineSvg": {
            "id": "DiscoFoundInlineSvg",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "svg",
            "description": "Inline SVG element detected that requires manual review to determine appropriate accessibility implementation based on its purpose and complexity",
            "why_it_matters": "SVG elements serve diverse purposes from simple icons to complex interactive visualizations, each requiring different accessibility approaches. A decorative border needs different treatment than a data chart, which differs from an interactive map or scientific simulation. Automated tools cannot determine SVG purpose, whether it's decorative or informative, static or interactive, or if existing accessibility features adequately support user needs.",
            "who_it_affects": "Blind and low vision users using screen readers who need text alternatives for graphics or keyboard access to interactive elements, users with motor disabilities who require keyboard navigation for interactive SVG controls, users with cognitive disabilities who benefit from clear labeling and predictable interaction patterns, and users of various assistive technologies that may interpret SVG content differently",
            "how_to_fix": "Evaluate the SVG's purpose and complexity - for simple images add <title> with aria-labelledby or role=\"img\" with aria-label, for decorative graphics use aria-hidden=\"true\", for data visualizations provide <title> and <desc> plus consider adjacent detailed text alternatives, for interactive content ensure all controls are keyboard accessible with proper ARIA labels and focus management, for complex simulations provide instructions and state changes announcements, and test with screen readers to verify the experience matches visual functionality"
        },
        "DiscoFoundSvgImage": {
            "id": "DiscoFoundSvgImage",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "SVG element with role=\"img\" detected that requires manual review to verify appropriate text alternatives are provided",
            "why_it_matters": "SVG elements with role=\"img\" are explicitly marked as images and treated as a single graphic by assistive technologies, requiring appropriate text alternatives. While the role=\"img\" indicates developer awareness of accessibility needs, manual review is needed to verify that any aria-label, aria-labelledby, or internal <title> elements adequately describe the image's content or function, and that the description is appropriate for the SVG's context and purpose.",
            "who_it_affects": "Blind and low vision users using screen readers who depend on text alternatives to understand image content, users with cognitive disabilities who benefit from clear, concise descriptions of visual information, keyboard users who may encounter the SVG in their navigation flow, and users of assistive technologies that treat role=\"img\" SVGs as atomic image elements",
            "how_to_fix": "Verify the SVG with role=\"img\" has appropriate accessible names through aria-label or aria-labelledby attributes, ensure any <title> or <desc> elements inside the SVG are properly referenced if used for labeling, confirm decorative SVGs are hidden with aria-hidden=\"true\" rather than given role=\"img\", check that the text alternative accurately describes the SVG's meaning in context, and test with screen readers to ensure the image is announced with meaningful information"
        },
        "ErrImageWithURLAsAlt": {
            "id": "ErrImageWithURLAsAlt",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "Alt attribute contains a URL (starting with http://, https://, www., or file://) instead of descriptive text about the image content",
            "why_it_matters": "URLs provide no meaningful information about what an image shows or its purpose on the page. Screen reader users hear lengthy, difficult-to-parse web addresses being spelled out character by character or in chunks like \"h-t-t-p-colon-slash-slash-w-w-w-dot\", creating a frustrating experience that conveys nothing about the actual image content. This often happens when image source URLs are mistakenly copied into alt attributes.",
            "who_it_affects": "Blind and low vision users using screen readers who need meaningful descriptions instead of technical URLs, users with cognitive disabilities who cannot process or remember long URL strings to understand image content, users in low-bandwidth situations where only alt text displays when images fail to load, and voice control users who cannot effectively reference images labeled with URLs",
            "how_to_fix": "Replace the URL with descriptive text that conveys what the image shows or its function (change alt=\"https://example.com/images/team-photo.jpg\" to alt=\"Marketing team at annual conference\"), focus on describing the image content rather than its location or technical details, ensure the description makes sense in the page context, and never use the image's web address as its alternative text"
        },
        "ErrImageAltContainsHTML": {
            "id": "ErrImageAltContainsHTML",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.1.1"],
            "wcag_full": "1.1.1 Non-text Content (Level A)",
            "category": "Images",
            "description": "Image's alternative text contains HTML markup tags",
            "why_it_matters": "HTML in alt text is not parsed, so screen readers will read the HTML markup as literal characters. Users will hear angle brackets announced as \"less than\" or \"greater than\" and tag names spelled out, creating a confusing experience. For example, alt=\"<b>Team Photo</b>\" would be read as \"less than b greater than Team Photo less than slash b greater than\".",
            "who_it_affects": "Blind and low vision users using screen readers who will hear nonsense characters and words interspersed with the actual alt text, making it difficult or impossible to understand the image content",
            "how_to_fix": "Remove all HTML markup from alt attributes and use only plain text. If formatting or structure is important to convey, describe it in words rather than using markup (e.g., instead of \"<em>Important</em>\" use \"Important, emphasized\")."
        },
        "forms_ErrInputMissingLabel": {
            "id": "forms_ErrInputMissingLabel",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "3.3.2", "4.1.2"],
            "wcag_full": "1.3.1, 3.3.2, 4.1.2",
            "category": "forms",
            "description": "Form input element is missing an associated label",
            "why_it_matters": "Users cannot determine the purpose of the input field",
            "who_it_affects": "Screen reader users, voice control users, users with cognitive disabilities",
            "how_to_fix": "Add a <label> element with matching for/id attributes"
        },
        "ErrEmptyAriaLabelOnField": {
            "id": "ErrEmptyAriaLabelOnField",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "3.3.2"],
            "wcag_full": "1.3.1, 3.3.2",
            "category": "forms",
            "description": "Form field has empty aria-label attribute",
            "why_it_matters": "Empty labels provide no information about the field",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add descriptive text to aria-label or use visible label"
        },
        "ErrEmptyAriaLabelledByOnField": {
            "id": "ErrEmptyAriaLabelledByOnField",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "3.3.2"],
            "wcag_full": "1.3.1, 3.3.2",
            "category": "forms",
            "description": "Form field has empty aria-labelledby attribute",
            "why_it_matters": "Empty labelledby provides no field description",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Reference valid element IDs or use direct labeling"
        },
        "ErrFieldAriaRefDoesNotExist": {
            "id": "ErrFieldAriaRefDoesNotExist",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "forms",
            "description": "aria-labelledby references non-existent element",
            "why_it_matters": "Broken reference means no label for screen readers",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Fix the ID reference or use a different labeling method"
        },
        "ErrFieldReferenceDoesNotExist": {
            "id": "ErrFieldReferenceDoesNotExist",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "forms",
            "description": "Label for attribute references non-existent field",
            "why_it_matters": "Label is not associated with any form field",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Fix the for/id relationship"
        },
        "ErrLabelContainsMultipleFields": {
            "id": "ErrLabelContainsMultipleFields",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "3.3.2"],
            "wcag_full": "1.3.1, 3.3.2",
            "category": "forms",
            "description": "Single label contains multiple form fields",
            "why_it_matters": "Unclear which field the label describes",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use separate labels for each field"
        },
        "ErrOrphanLabelWithNoId": {
            "id": "ErrOrphanLabelWithNoId",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "forms",
            "description": "Label element exists but has no for attribute",
            "why_it_matters": "Label is not programmatically associated with any field",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add for attribute pointing to field ID"
        },
        "WarnFormHasNoLabel": {
            "id": "WarnFormHasNoLabel",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.6 Headings and Labels",
            "category": "forms",
            "description": "Form element has no accessible name to describe its purpose",
            "why_it_matters": "When a form lacks an accessible name, screen reader users hear only \"form\" without knowing what the form does - is it a search form, login form, contact form, or something else? Users navigating by landmarks or forms need to understand each form's purpose to decide whether to interact with it. This is especially important on pages with multiple forms. Without proper labeling, users might fill out the wrong form, skip important forms, or waste time exploring forms to understand their purpose.",
            "who_it_affects": "Screen reader users navigating by forms or landmarks who need to identify form purposes, users with cognitive disabilities who need clear labels to understand what each form does, and keyboard users who tab through forms and need context about what they're interacting with",
            "how_to_fix": "Add an accessible name to the form element using aria-label (e.g., aria-label=\"Contact form\") or aria-labelledby to reference a visible heading. If the form has a visible heading immediately before it, use aria-labelledby to point to that heading's ID. For search forms, \"Search\" is usually sufficient. The label should clearly indicate the form's purpose and be unique if there are multiple forms on the page."
        },
        "forms_WarnRequiredNotIndicated": {
            "id": "forms_WarnRequiredNotIndicated",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["3.3.2"],
            "wcag_full": "3.3.2",
            "category": "forms",
            "description": "Required field not clearly indicated",
            "why_it_matters": "Users don't know which fields are mandatory",
            "who_it_affects": "All users, especially those with cognitive disabilities",
            "how_to_fix": "Add required attribute and visual indication"
        },
        "ErrInputNoVisibleFocus": {
            "id": "ErrInputNoVisibleFocus",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "forms",
            "description": "Text input field has no visible focus indicator (outline:none, no border change, no box-shadow)",
            "why_it_matters": "WCAG 2.4.7 Focus Visible (Level AA) requires that keyboard focus indicators are visible. When an input field removes the outline without providing an alternative focus indicator (border change, box-shadow, or custom outline), keyboard users cannot determine which field has focus. This forces users to type blind, not knowing if they're entering data into the correct field. For users completing complex forms, this creates an impossible situation - they might skip required fields, enter data in the wrong place, or become completely lost in the form structure. Input fields MUST have visible focus indicators because users need to know where their keyboard input will be directed.",
            "who_it_affects": "Keyboard-only users who cannot see which field has focus, screen magnifier users who need clear indicators to track focus, users with attention or memory issues who lose track of their position in forms, users with low vision who cannot perceive subtle focus changes, and motor impairment users who navigate slowly and need clear feedback about current focus position",
            "how_to_fix": "Remove outline:none or outline:0 from focus styles. If custom styling is needed, provide a visible alternative: (1) Add a clear outline using outline: 2px solid color with sufficient contrast, (2) Increase border width by ≥1px on focus, (3) Add box-shadow with ≥3:1 contrast, or (4) Combine border color change with border thickening or outline. Best practice: use a separate outline (outline: 2px solid) as it doesn't affect layout and is clearest for screen magnifier users who may only see one field at a time."
        },
        "ErrInputColorChangeOnly": {
            "id": "ErrInputColorChangeOnly",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.1"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.1 Use of Color (Level A)",
            "category": "forms",
            "description": "Input field focus indicator relies solely on border color change without structural change",
            "why_it_matters": "WCAG 1.4.1 Use of Color (Level A) explicitly prohibits using color as the only visual means of conveying information. When an input field changes only its border color on focus (e.g., gray → blue) without adding an outline, thickening the border, or adding box-shadow, users with color blindness cannot perceive the focus indicator. Approximately 8% of men and 0.5% of women have some form of color vision deficiency - for them, the focused and unfocused states look identical. This is especially problematic in forms where users must navigate between multiple fields. Color-only indicators also fail on monochrome displays, in high-contrast mode, and for users who cannot distinguish subtle color differences.",
            "who_it_affects": "Users with color blindness (protanopia, deuteranopia, tritanopia - affecting ~8% of men), users with low vision who cannot perceive color differences, users on monochrome displays or e-ink screens, users in bright sunlight where colors wash out, users with high-contrast mode enabled, and users with cognitive disabilities who rely on shape and structure over color",
            "how_to_fix": "Add a structural change in addition to any color change. Options: (1) Add an outline (outline: 2px solid colorName) - RECOMMENDED, (2) Increase border width by ≥1px (e.g., border: 1px → 2px solid), (3) Add box-shadow (box-shadow: 0 0 0 2px colorName), or (4) Combine border color change with border thickening. The structural change must be perceivable without color - test in grayscale to verify."
        },
        "ErrInputFocusContrastFail": {
            "id": "ErrInputFocusContrastFail",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast (Level AA)",
            "category": "forms",
            "description": "Input field focus indicator has insufficient color contrast (< 3:1) against background",
            "why_it_matters": "WCAG 1.4.11 Non-text Contrast requires focus indicators to have a contrast ratio of at least 3:1 against adjacent colors. When an input field's outline, border, or box-shadow has insufficient contrast, users with low vision cannot perceive it. A blue outline (rgb(0,102,204)) on a light blue background (rgb(200,220,255)) might have only 1.5:1 contrast - essentially invisible to users with low vision. This is common when designers match focus colors to brand colors without checking contrast. Low-contrast indicators also fail in bright lighting, on low-quality displays, for users with cataracts or age-related vision loss, and when viewed through screen magnifiers at high zoom.",
            "who_it_affects": "Users with low vision who cannot perceive low-contrast indicators, older users with age-related vision changes, users with cataracts or other vision conditions that reduce contrast sensitivity, users viewing in bright ambient lighting, users on low-quality or poorly calibrated displays, and screen magnifier users who need high contrast to track focus",
            "how_to_fix": "Choose focus indicator colors with ≥3:1 contrast against the input field's background. For fields on white backgrounds (rgb(255,255,255)), use dark colors like: dark blue (#003366, 6.5:1), black (#000000, 21:1), or dark gray (#666666, 5.7:1). For fields on dark backgrounds, use light colors. Use online contrast checkers (WebAIM, Colour Contrast Analyser) to verify. Test against all background colors that may appear behind the field. If the background is dynamic, test all states. For fields on gradient or image backgrounds, ensure contrast with both lightest and darkest areas."
        },
        "ErrInputSingleSideBoxShadow": {
            "id": "ErrInputSingleSideBoxShadow",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible, Conformance Requirement 5.2.4 (all levels)",
            "category": "forms",
            "description": "Input field uses single-sided box-shadow for focus indicator (does not follow field shape)",
            "why_it_matters": "WCAG Conformance Requirement 5.2.4 states that when components have a visible boundary, changes to contrast must apply to all parts of the boundary. A single-sided box-shadow (e.g., box-shadow: 0 2px 0 0 blue - bottom only, or box-shadow: 2px 0 0 0 blue - right only) does not follow the input field's rectangular shape. This creates ambiguity about whether the indicator belongs to the focused field or an adjacent element. For screen magnifier users viewing only part of the field, a bottom-only shadow might appear to be an underline on the field below. For users with cognitive disabilities, partial indicators create confusion about which element actually has focus. The indicator must clearly and completely identify the focused element.",
            "who_it_affects": "Screen magnifier users who may only see part of the field and cannot determine if a partial shadow belongs to it, users with cognitive disabilities who are confused by partial indicators, users with attention difficulties who need clear visual boundaries, keyboard users who need unambiguous feedback about focus location, and users with low vision who may not perceive partial shadows as belonging to the field",
            "how_to_fix": "Use box-shadow on all sides: box-shadow: 0 0 0 2px colorName (creates outline effect around entire field). Alternatively, use a proper outline: outline: 2px solid colorName which automatically follows the element shape. If design requires shadow for depth, combine a full box-shadow with offset: box-shadow: 0 0 0 2px blue, 0 4px 6px rgba(0,0,0,0.1). Never use single-sided shadows as the only focus indicator. Test that the indicator is clearly visible from all edges of the field."
        },
        "ErrInputBorderChangeInsufficient": {
            "id": "ErrInputBorderChangeInsufficient",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "forms",
            "description": "Input field border thickens on focus but change is less than 1px (not manifest)",
            "why_it_matters": "When an input field's border thickness increases by less than 1px on focus (e.g., 1px → 1.5px, or 1.5px → 2px), the change is not manifest enough for many users to perceive. WCAG 2.4.7 requires focus indicators to be visible, which means users must actually be able to SEE the change. A 0.5px border increase might be technically measurable but is imperceptible to users with low vision, on many displays, or at typical viewing distances. This is especially problematic because the developer believes they've added a focus indicator, but users experience the same issue as if there were no indicator at all. Border thickness changes must be substantial - at least 1 full pixel increase - to be reliably visible.",
            "who_it_affects": "Users with low vision who cannot perceive sub-pixel or half-pixel changes, users on lower resolution displays where fractional pixels may not render, users viewing at typical distances where fine details are not visible, screen magnifier users who need clear indicators, older users with reduced visual acuity, and keyboard users who depend on obvious focus changes to navigate forms",
            "how_to_fix": "Increase border width by at least 1 full pixel on focus. Examples: border: 1px → 2px solid (1px increase - good), border: 2px → 3px solid (1px increase - good), border: 1px → 3px solid (2px increase - excellent). If keeping borders thin is important for design, consider adding an outline instead: outline: 2px solid colorName which won't affect layout. Or combine a minimal border increase with a color change AND an outline. Test at typical viewing distances to ensure the change is obvious. Best practice: use outline: 2px solid for clarity and consistency."
        },
        "ErrInputOutlineWidthInsufficient": {
            "id": "ErrInputOutlineWidthInsufficient",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.7", "2.4.11"],
            "wcag_full": "2.4.7 Focus Visible (Level AA), 2.4.11 Focus Appearance (Level AAA)",
            "category": "forms",
            "description": "Input field focus outline is less than 2px wide",
            "why_it_matters": "WCAG 2.4.11 Focus Appearance (Level AAA) specifies that focus indicators should be at least 2 CSS pixels thick or have equivalent area. While this is AAA (aspirational) rather than AA (required), there are strong practical reasons for the 2px minimum. A 1px outline can be difficult to see for users with low vision, on high-DPI displays (where CSS pixels don't match physical pixels), for users viewing from a distance, in bright lighting, or on lower quality displays. Screen magnifier users especially benefit from thicker outlines as they're easier to track when zoomed in. Though not a strict AA failure, 1px outlines are on the borderline of visibility - going to 2px provides much better usability for minimal visual impact.",
            "who_it_affects": "Users with low vision who struggle to see thin 1px outlines, users on high-DPI displays (retina, 4K) where 1px appears thinner, screen magnifier users who need clear indicators when zoomed, older users with reduced visual acuity, users in bright ambient lighting where thin lines wash out, and keyboard users who benefit from prominent focus indicators",
            "how_to_fix": "Increase outline width to 2px: outline: 2px solid colorName. This is a simple change that significantly improves visibility. For even better visibility, consider 3px. Ensure the outline color has ≥3:1 contrast with the background. If a 2px outline looks too heavy in your design, verify that your current design has been tested with actual users with low vision - you may be optimizing for aesthetic preferences over accessibility needs. Remember that 2px is the MINIMUM for AAA compliance and is considered best practice for AA as well."
        },
        "WarnInputNoBorderOutline": {
            "id": "WarnInputNoBorderOutline",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "forms",
            "description": "Input field uses border/box-shadow changes but no separate outline for focus indicator",
            "why_it_matters": "While border changes and box-shadows can serve as valid focus indicators, they have a significant limitation for screen magnifier users: these users often zoom in to 200-400% and may only see ONE input field at a time. When the only focus indicator is a border color change or thickness change, magnifier users cannot see other fields to compare against - they cannot tell if the field they're viewing is focused or not because they don't have a reference point. A separate outline (outline: 2px solid) provides an ABSOLUTE indicator - its presence clearly shows focus, its absence shows no focus, without needing to compare to other fields. This is why outlines are the gold standard for focus indicators. This is a warning, not an error, because the current implementation does meet WCAG AA, but it's not optimal for all users.",
            "who_it_affects": "Screen magnifier users who may only see one field at a time and cannot compare visual states, users who zoom browser to 200-400% to read content, users with tunnel vision who see only a small area of the screen, users with attention difficulties who focus on one element at a time and cannot make comparisons, and users switching between applications who return to find focus but cannot determine which field has it without tabbing",
            "how_to_fix": "Add a separate outline in addition to any border or box-shadow changes: outline: 2px solid colorName. This provides both an absolute indicator (outline presence/absence) and a relative indicator (border/shadow changes). The outline should have ≥3:1 contrast with the background. If outline affects layout undesirably, use outline-offset: 1px to add space. Example: input:focus { outline: 2px solid #0066cc; outline-offset: 1px; border-color: #0066cc; border-width: 2px; } - this provides multiple reinforcing indicators."
        },
        "WarnInputDefaultFocus": {
            "id": "WarnInputDefaultFocus",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "forms",
            "description": "Input field relies on default browser focus styles which vary across browsers and platforms",
            "why_it_matters": "Default browser focus indicators vary significantly: Chrome uses a 2px blue outline (rgb(0,103,244)), Firefox uses a 1px dotted black outline, Safari uses a 3px blue outline with subtle glow, and older browsers use different styles. These styles also differ between Windows, macOS, and Linux. Some defaults are excellent (Safari), while others are barely visible (Firefox's 1px dotted on some backgrounds). By relying on browser defaults, you lose control over the user experience and cannot guarantee that focus will be clearly visible in all contexts. Additionally, default focus styles often clash with brand design, leading developers to remove them with outline:none without replacement. Custom focus indicators ensure consistent, predictable, and well-tested focus visibility across all browsers and platforms.",
            "who_it_affects": "All keyboard users whose experience varies by browser, users on older browsers with poor default focus indicators, users on platforms with different default styles (Windows vs Mac), developers who might remove default styles if they clash with design without adding replacements, and QA teams who must test across many browser combinations",
            "how_to_fix": "Define custom focus styles that work consistently across all browsers: input:focus { outline: 2px solid #0066cc; outline-offset: 1px; }. Choose colors with ≥3:1 contrast against your input backgrounds. Test in Chrome, Firefox, Safari, and Edge. Test on both light and dark backgrounds if your site supports themes. Document your focus indicator standards in your design system. Use CSS custom properties to maintain consistency: --focus-outline: 2px solid var(--focus-color). Custom styles also allow you to match your brand while ensuring excellent accessibility."
        },
        "WarnInputFocusGradientBackground": {
            "id": "WarnInputFocusGradientBackground",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast (Level AA)",
            "category": "forms",
            "description": "Input field has gradient background - focus indicator contrast cannot be automatically verified",
            "why_it_matters": "When an input field has a gradient background (linear-gradient, radial-gradient, etc.), automated tools cannot determine the contrast ratio between the focus indicator and the background because the background color varies across the field. A focus outline might have 4:1 contrast against the light end of the gradient but only 1.5:1 against the dark end. Gradients are especially problematic for box-shadow focus indicators that appear at the field edges - the shadow might be visible on one side and invisible on the other. While this warning doesn't indicate a definite failure, it flags inputs that require manual inspection. Visual gradients on form fields are generally poor practice as they make focus indicators, placeholder text, and input text harder to perceive consistently.",
            "who_it_affects": "Users with low vision who may not see focus indicators against certain parts of the gradient, automated testing tools that cannot verify compliance, users with color vision deficiencies for whom gradients may appear differently, QA teams who must manually test these fields, and users on displays with poor color reproduction where gradients may appear banded or distorted",
            "how_to_fix": "Best solution: use solid background colors for input fields (background-color: #ffffff). If gradients are required for design: (1) Use a very subtle gradient (e.g., #f8f8f8 to #ffffff) and ensure focus outline has ≥3:1 against the darkest color, (2) Add a solid-color inner border or inset box-shadow to provide a consistent background immediately behind the focus indicator, (3) Use a thick outline (3-4px) that remains visible against all gradient colors, (4) Manually test focus visibility across the entire gradient range. Verify in grayscale to ensure contrast doesn't rely on hue."
        },
        "WarnInputTransparentFocus": {
            "id": "WarnInputTransparentFocus",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast (Level AA)",
            "category": "forms",
            "description": "Input field focus indicator is semi-transparent (alpha < 0.5) which may not provide sufficient visibility",
            "why_it_matters": "Semi-transparent focus indicators (using rgba or hsla with alpha < 0.5) create unpredictable contrast ratios that vary based on what's behind the input field. An outline with rgba(0,102,204,0.3) appears differently against white, gray, or patterned backgrounds - the effective color and contrast constantly change. As users scroll, animations play, or modals open, the background behind the field may change, causing the focus indicator to become invisible at certain times. Alpha values below 0.5 mean the outline is more than 50% transparent - essentially blending into the background on many color combinations. WCAG requires consistent accessibility - an indicator that works sometimes but fails in other contexts is not reliable. For users with low vision, a barely-visible transparent indicator is functionally equivalent to no indicator.",
            "who_it_affects": "Users with low vision who cannot perceive subtle transparent indicators, users viewing in bright lighting where transparent colors wash out further, users with color vision deficiencies for whom transparent colors may be especially hard to perceive, screen magnifier users who need clear indicators, users on displays with poor contrast ratios, and users with cognitive disabilities who need obvious, unambiguous focus indicators",
            "how_to_fix": "Use fully opaque colors for focus indicators: rgba(0,102,204,1.0) or simply rgb(0,102,204) or #0066cc. If you want a lighter or more subtle color, choose a different HUE rather than making it transparent - use #66b3ff (light opaque blue) instead of rgba(0,102,204,0.3) (transparent blue). Calculate and verify ≥3:1 contrast against all possible backgrounds. If you must use transparency for specific design reasons, ensure alpha ≥ 0.5 and manually test against all backgrounds in all states. Test in grayscale to verify the indicator is visible without relying on color. Remember: opacity reduces both color vibrancy AND contrast."
        },
        "forms_WarnGenericButtonText": {
            "id": "forms_WarnGenericButtonText",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "forms",
            "description": "Button has generic text like \"Submit\" or \"Click here\"",
            "why_it_matters": "Button purpose is unclear out of context",
            "who_it_affects": "Screen reader users navigating by buttons",
            "how_to_fix": "Use descriptive button text like \"Submit registration\""
        },
        "forms_WarnNoFieldset": {
            "id": "forms_WarnNoFieldset",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "3.3.2"],
            "wcag_full": "1.3.1, 3.3.2",
            "category": "forms",
            "description": "Radio/checkbox group lacks fieldset and legend",
            "why_it_matters": "Group relationship is not clear",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Wrap related inputs in fieldset with legend"
        },
        "DiscoFormOnPage": {
            "id": "DiscoFormOnPage",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": [],
            "wcag_full": "N/A",
            "category": "forms",
            "description": "Form detected on page - needs manual testing",
            "why_it_matters": "Forms need comprehensive accessibility testing",
            "who_it_affects": "All users with disabilities",
            "how_to_fix": "Manually test form with keyboard and screen reader"
        },
        "forms_DiscoNoSubmitButton": {
            "id": "forms_DiscoNoSubmitButton",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": ["3.3.2"],
            "wcag_full": "3.3.2",
            "category": "forms",
            "description": "Form may lack clear submit button",
            "why_it_matters": "Users may not know how to submit the form",
            "who_it_affects": "Users with cognitive disabilities, keyboard users",
            "how_to_fix": "Ensure form has clear submit mechanism"
        },
        "forms_DiscoPlaceholderAsLabel": {
            "id": "forms_DiscoPlaceholderAsLabel",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": ["3.3.2"],
            "wcag_full": "3.3.2",
            "category": "forms",
            "description": "Placeholder may be used instead of label",
            "why_it_matters": "Placeholder text disappears when typing",
            "who_it_affects": "Users with memory/cognitive issues, screen reader users",
            "how_to_fix": "Use proper labels, placeholder for examples only"
        },
        "ErrFormEmptyHasNoChildNodes": {
            "id": "ErrFormEmptyHasNoChildNodes",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "forms",
            "description": "Form element is completely empty with no child nodes",
            "why_it_matters": "Empty forms serve no purpose and confuse assistive technology users",
            "who_it_affects": "Screen reader users, keyboard users",
            "how_to_fix": "Remove empty form elements or add appropriate form controls"
        },
        "ErrFormEmptyHasNoInteractiveElements": {
            "id": "ErrFormEmptyHasNoInteractiveElements",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "forms",
            "description": "Form has content but no interactive elements",
            "why_it_matters": "Forms without inputs cannot be used for their intended purpose",
            "who_it_affects": "All users",
            "how_to_fix": "Add appropriate input fields, buttons, or other form controls"
        },
        "ErrFieldLabelledUsinAriaLabel": {
            "id": "ErrFieldLabelledUsinAriaLabel",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.3.2"],
            "wcag_full": "3.3.2",
            "category": "forms",
            "description": "Field labeled using aria-label instead of visible label",
            "why_it_matters": "Visible labels benefit all users, not just screen reader users",
            "who_it_affects": "Users with cognitive disabilities, all users",
            "how_to_fix": "Use visible <label> elements instead of aria-label when possible"
        },
        "ErrFielLabelledBySomethingNotALabel": {
            "id": "ErrFielLabelledBySomethingNotALabel",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "3.3.2"],
            "wcag_full": "1.3.1, 3.3.2",
            "category": "forms",
            "description": "Field is labeled by an element that is not a proper label",
            "why_it_matters": "Non-label elements may not provide appropriate semantic relationships",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use proper <label> elements or appropriate ARIA labeling"
        },
        "WarnFieldLabelledByMulitpleElements": {
            "id": "WarnFieldLabelledByMulitpleElements",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["3.3.2"],
            "wcag_full": "3.3.2",
            "category": "forms",
            "description": "Field is labeled by multiple elements via aria-labelledby",
            "why_it_matters": "Multiple labels may be confusing or incorrectly concatenated",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Ensure multiple labels make sense when read together"
        },
        "WarnFieldLabelledByElementThatIsNotALabel": {
            "id": "WarnFieldLabelledByElementThatIsNotALabel",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "3.3.2"],
            "wcag_full": "1.3.1, 3.3.2",
            "category": "forms",
            "description": "Field labeled by element that is not semantically a label",
            "why_it_matters": "Non-label elements may not convey proper semantic meaning",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use proper label elements or ensure aria-labelledby references appropriate content"
        },
        "forms_ErrNoButtonText": {
            "id": "forms_ErrNoButtonText",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.6", "4.1.2"],
            "wcag_full": "2.4.6, 4.1.2",
            "category": "forms",
            "description": "Button has no accessible text",
            "why_it_matters": "Users cannot determine button purpose",
            "who_it_affects": "Screen reader users, voice control users",
            "how_to_fix": "Add text content, aria-label, or aria-labelledby to button"
        },
        "ErrNoHeadingsOnPage": {
            "id": "ErrNoHeadingsOnPage",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.6 Headings and Labels",
            "category": "headings",
            "description": "No heading elements (h1-h6) found anywhere on the page",
            "why_it_matters": "Headings create the structural outline of your content, like a table of contents. They allow users to understand how information is organized and navigate directly to sections of interest. Without any headings, screen reader users cannot use heading navigation shortcuts (one of their primary navigation methods) and must read through all content linearly. This is like forcing someone to read an entire book without chapter titles or section breaks. Users cannot skim content, jump to relevant sections, or understand the information hierarchy. For users with cognitive disabilities, the lack of visual structure makes content overwhelming and hard to process.",
            "who_it_affects": "Screen reader users who lose a critical navigation method and cannot understand content structure, users with cognitive disabilities who need clear visual organization to process information, users with attention disorders who rely on headings to focus on relevant sections, and users with reading disabilities who use headings to break content into manageable chunks",
            "how_to_fix": "Add semantic heading elements (h1-h6) to structure your content. Start with one h1 that describes the main page topic. Use h2 for major sections, h3 for subsections, and so on. Don't skip levels (e.g., h1 to h3). Ensure headings describe the content that follows them. Never use headings just for visual styling - they must represent actual content structure. If you need large text without semantic meaning, use CSS instead."
        },
        "ErrNoH1OnPage": {
            "id": "ErrNoH1OnPage",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.6 Headings and Labels",
            "category": "headings",
            "description": "Page is missing an h1 element to identify the main topic",
            "why_it_matters": "The h1 is the most important heading on a page - it tells users what the page is about, similar to a chapter title in a book. Screen reader users often navigate directly to the h1 first to understand the page purpose. Without it, users must guess the page topic from other cues like the title or URL. The h1 also establishes the starting point for the heading hierarchy. Search engines use the h1 to understand page content, and browser extensions that generate page outlines will be missing the top level. Think of the h1 as answering \"What is this page about?\" - without it, users lack this fundamental context.",
            "who_it_affects": "Screen reader users who jump to the h1 to understand page purpose, users with cognitive disabilities who need clear indication of page topic, SEO and users finding your content through search engines, users of browser tools that generate page outlines or tables of contents",
            "how_to_fix": "Add exactly one h1 element that describes the main topic or purpose of the page. It should be unique to that page (not the same site-wide). Place it at the beginning of your main content, typically inside the main landmark. The h1 text should make sense if read in isolation and match user expectations based on how they arrived at the page. Don't use the site name as the h1 - use the specific page topic."
        },
        "ErrEmptyHeading": {
            "id": "ErrEmptyHeading",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.6 Headings and Labels",
            "category": "headings",
            "description": "Heading element (h1-h6) contains no text content or only whitespace",
            "why_it_matters": "Empty headings disrupt document structure and navigation. Screen reader users rely on headings to understand page organization and navigate efficiently using heading shortcuts. An empty heading creates a navigation point with no information, confusing users about the page structure. It may indicate missing content or poor markup practices that affect the overall accessibility of the page.",
            "who_it_affects": "Screen reader users who navigate by headings and cannot determine what section the empty heading represents, users with cognitive disabilities who rely on clear structure to understand content organization, and users of browser plugins or assistive technologies that generate page outlines",
            "how_to_fix": "Either add meaningful text content to the heading that describes the section it introduces, or remove the empty heading element entirely if it serves no structural purpose. Never use headings for visual spacing - use CSS margin/padding instead. Ensure all headings have descriptive text that helps users understand the content structure."
        },
        "ErrHeadingLevelsSkipped": {
            "id": "ErrHeadingLevelsSkipped",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1 Info and Relationships",
            "category": "headings",
            "description": "Heading levels are not in sequential order - one or more levels are skipped (e.g., h1 followed by h3 with no h2)",
            "why_it_matters": "Heading levels create a hierarchical outline of your content, like nested bullet points. When you skip levels (jump from h1 to h3), you break this logical structure. It's like having chapter 1, then jumping to section 1.1.1 without section 1.1. Screen reader users navigating by headings will be confused about the relationship between sections - is the h3 a subsection of something that's missing? This broken hierarchy makes it hard to understand how content is organized and can cause users to think content is missing or that they've accidentally skipped something.",
            "who_it_affects": "Screen reader users navigating by heading structure who rely on levels to understand content relationships, users with cognitive disabilities who need logical, predictable content organization, users of assistive technology that generates document outlines, and developers or content authors maintaining the page who need to understand the intended structure",
            "how_to_fix": "Always use heading levels sequentially. After h1, use h2 for the next level, then h3, and so on. Don't skip levels when going down (h1→h2→h3, not h1→h3). You can skip levels going back up (h3 can be followed by h2 for a new section). If you need a heading to look smaller visually, use CSS to style it rather than choosing a lower heading level. The heading level should reflect the content's logical structure, not its visual appearance."
        },
        "ErrHeadingOrder": {
            "id": "ErrHeadingOrder",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1 Info and Relationships",
            "category": "headings",
            "description": "Headings appear in illogical order - high-level headings (H1, H2) appear after lower-level headings (H3, H4, H5, H6)",
            "why_it_matters": "Document structure should be logical and predictable. When high-level headings like H1 or H2 appear after lower-level headings, it creates a backwards or inverted hierarchy. This is like reading a book where chapter titles appear after section headings, or where the main title appears at the end. Screen reader users navigating by headings expect the most important headings first, followed by progressively more detailed subsections. When headings appear out of logical order, users cannot understand the content structure, may miss important navigation landmarks, and cannot build an accurate mental model of how the page is organized.",
            "who_it_affects": "Screen reader users who rely on heading navigation and expect logical document structure, users with cognitive disabilities who need predictable content organization, users who generate document outlines from headings, and users who navigate by heading levels to understand content hierarchy",
            "how_to_fix": "Restructure your content so that high-level headings (H1, H2) appear before lower-level headings. Start with H1 for the main page title, then H2 for major sections, then H3 for subsections within those. Headings should appear in a logical, top-down hierarchy that matches how users would naturally read and understand the content structure."
        },
        "ErrHeadingsDontStartWithH1": {
            "id": "ErrHeadingsDontStartWithH1",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "headings",
            "description": "First heading on page is not h1",
            "why_it_matters": "Document structure should start with h1",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Start heading hierarchy with h1"
        },
        "ErrMultipleH1HeadingsOnPage": {
            "id": "ErrMultipleH1HeadingsOnPage",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "headings",
            "description": "Multiple h1 elements found on page",
            "why_it_matters": "Unclear main topic of page",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one h1 per page"
        },
        "ErrFoundAriaLevelButNoRoleAppliedAtAll": {
            "id": "ErrFoundAriaLevelButNoRoleAppliedAtAll",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "headings",
            "description": "aria-level attribute without role=\"heading\"",
            "why_it_matters": "aria-level only works with heading role",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add role=\"heading\" or use native heading element"
        },
        "ErrFoundAriaLevelButRoleIsNotHeading": {
            "id": "ErrFoundAriaLevelButRoleIsNotHeading",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "headings",
            "description": "aria-level on element without heading role",
            "why_it_matters": "aria-level requires heading role to work",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add role=\"heading\" or remove aria-level"
        },
        "ErrInvalidAriaLevel": {
            "id": "ErrInvalidAriaLevel",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "headings",
            "description": "Invalid aria-level value (not 1-6)",
            "why_it_matters": "Invalid levels break heading hierarchy",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use aria-level values 1 through 6 only"
        },
        "ErrRoleOfHeadingButNoLevelGiven": {
            "id": "ErrRoleOfHeadingButNoLevelGiven",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "headings",
            "description": "role=\"heading\" without aria-level",
            "why_it_matters": "Heading level is undefined",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add aria-level attribute with value 1-6"
        },
        "WarnHeadingOver60CharsLong": {
            "id": "WarnHeadingOver60CharsLong",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "headings",
            "description": "Heading text exceeds 60 characters",
            "why_it_matters": "Long headings are hard to scan and understand",
            "who_it_affects": "Users with cognitive disabilities, screen reader users",
            "how_to_fix": "Use concise heading text"
        },
        "WarnHeadingInsideDisplayNone": {
            "id": "WarnHeadingInsideDisplayNone",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "headings",
            "description": "Heading is hidden with display:none",
            "why_it_matters": "Hidden headings may affect document structure",
            "who_it_affects": "Screen reader users (varies by implementation)",
            "how_to_fix": "Remove unused headings or make them visible"
        },
        "ErrHeadingAccessibleNameMismatch": {
            "id": "ErrHeadingAccessibleNameMismatch",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.5.3"],
            "wcag_full": "2.5.3",
            "category": "headings",
            "description": "Visible heading text doesn't match its accessible name",
            "why_it_matters": "Voice control users may not be able to reference the heading by its visible text",
            "who_it_affects": "Voice control users, screen reader users",
            "how_to_fix": "Ensure visible text starts the accessible name (e.g., visible 'Support' should be at the start of aria-label, like 'Support: Customer Service')"
        },
        "ErrNoMainLandmarkOnPage": {
            "id": "ErrNoMainLandmarkOnPage",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "2.4.1"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.1 Bypass Blocks",
            "category": "landmarks",
            "description": "Page is missing a main landmark region to identify the primary content area",
            "why_it_matters": "Screen reader users rely on landmarks to understand page layout and quickly navigate to important sections. The main landmark allows users to skip repeated content like headers and navigation to jump directly to the unique page content. Without it, users must navigate through all repeated elements on every page, which is time-consuming and frustrating. The main landmark should contain all content that is unique to the page, including the h1 heading.",
            "who_it_affects": "Blind and low vision users using screen readers who navigate by landmarks, users with motor disabilities who need efficient keyboard navigation to skip repeated content, and users with cognitive disabilities who benefit from clear page structure",
            "how_to_fix": "Add a <main> element around the primary content area, or use role=\"main\" on an appropriate container element. Ensure there is only one main landmark per page, position it as a top-level landmark (not nested inside other landmarks), and include all unique page content within it, including the h1 heading. The main landmark should not include repeated content like site headers, navigation, or footers."
        },
        "ErrNoBannerLandmarkOnPage": {
            "id": "ErrNoBannerLandmarkOnPage",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.1"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.1 Bypass Blocks",
            "category": "landmarks",
            "description": "Page is missing a banner landmark to identify the site header region",
            "why_it_matters": "The banner landmark identifies the site header which typically contains the site logo, main navigation, and search functionality. This content appears consistently across pages and users expect to find it at the top. Without proper banner markup, screen reader users cannot quickly jump to the header area using landmark navigation shortcuts. They must instead navigate through all content linearly or guess where the header content begins and ends. This makes it difficult to access primary navigation or return to the site homepage via the logo link, tasks that sighted users can do instantly by looking at the top of the page.",
            "who_it_affects": "Screen reader users who use landmark navigation to quickly access site navigation and branding, keyboard users who want to efficiently navigate to header elements, users with cognitive disabilities who rely on consistent page structure to orient themselves, and users with low vision using screen magnifiers who need to quickly locate navigation elements",
            "how_to_fix": "Use the HTML5 <header> element for your site header (it has an implicit role of banner when it's not nested inside article, aside, main, nav, or section elements). Alternatively, add role=\"banner\" to the container holding your header content. There should typically be only one banner landmark per page at the top level. Include site-wide content like logo, primary navigation, and site search within the banner landmark."
        },
        "WarnNoContentinfoLandmarkOnPage": {
            "id": "WarnNoContentinfoLandmarkOnPage",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1", "2.4.1"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.1 Bypass Blocks",
            "category": "landmarks",
            "description": "Page is missing a contentinfo landmark to identify the footer region",
            "why_it_matters": "The contentinfo landmark (typically a footer) contains important information about the page or site such as copyright notices, privacy policies, contact information, and site maps. Screen reader users rely on landmarks to quickly navigate to these common elements without having to read through the entire page. When the footer lacks proper landmark markup, users must search manually through the content to find this information, which is inefficient and may cause them to miss important legal notices or helpful links. The contentinfo landmark provides a consistent, predictable way to access this supplementary information across all pages.",
            "who_it_affects": "Screen reader users who navigate by landmarks to quickly find footer information, keyboard users who want to efficiently skip to footer content, users with cognitive disabilities who rely on consistent page structure, and users who need to frequently access footer links like privacy policies or contact information",
            "how_to_fix": "Use the HTML5 <footer> element for your page footer (it has an implicit role of contentinfo when it's not nested inside article, aside, main, nav, or section elements). Alternatively, add role=\"contentinfo\" to the container holding your footer content. Ensure there's only one contentinfo landmark per page at the top level. The footer should contain information about the page or site, not primary content."
        },
        "WarnNoNavLandmarksOnPage": {
            "id": "WarnNoNavLandmarksOnPage",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1", "2.4.1"],
            "wcag_full": "1.3.1 Info and Relationships, 2.4.1 Bypass Blocks",
            "category": "landmarks",
            "description": "Page has no navigation landmarks to identify navigation regions",
            "why_it_matters": "Navigation landmarks identify areas containing navigation links, allowing users to quickly jump to menus without reading through other content. Most web pages have multiple navigation areas (main menu, footer links, sidebar navigation, breadcrumbs) but without proper markup, these are just lists of links mixed with other content. Screen reader users must hunt for navigation areas or listen to all links to find what they need. Navigation landmarks make these areas immediately discoverable and allow users to skip between different navigation regions efficiently.",
            "who_it_affects": "Screen reader users who use landmarks to find navigation menus quickly, keyboard users navigating complex sites with multiple menus, users with cognitive disabilities who need clear identification of navigation areas, and users with motor disabilities who need to minimize unnecessary navigation",
            "how_to_fix": "Wrap navigation areas in <nav> elements or add role=\"navigation\" to containers with navigation links. If you have multiple navigation areas, label each one with aria-label to distinguish them (e.g., aria-label=\"Main navigation\", aria-label=\"Footer links\", aria-label=\"Breadcrumb\"). Not every group of links needs to be a navigation landmark - use it for major navigation blocks that users would want to find quickly."
        },
        "ErrMultipleMainLandmarksOnPage": {
            "id": "ErrMultipleMainLandmarksOnPage",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1 Info and Relationships",
            "category": "landmarks",
            "description": "Multiple main landmark regions found on the page",
            "why_it_matters": "The main landmark should contain THE primary content of the page - having multiple main landmarks is like having multiple \"Chapter 1\" sections in a book. It confuses the page structure and defeats the purpose of landmarks. Screen reader users expecting to jump to the main content won't know which landmark contains the actual primary content. They might land in the wrong section, miss important content, or have to check multiple \"main\" areas. This ambiguity makes the landmark system unreliable and forces users back to linear navigation.",
            "who_it_affects": "Screen reader users relying on the main landmark to skip to primary content, keyboard users using landmark navigation extensions, users with cognitive disabilities who need clear, unambiguous page structure, and developers trying to understand the intended page structure",
            "how_to_fix": "Use only one <main> element or role=\"main\" per page. Identify which content is truly the primary, unique content for that page and wrap only that in the main landmark. If you have multiple important sections, use other appropriate landmarks (article, section) or headings to structure them within the single main landmark. The main should contain all unique page content but exclude repeated elements like headers, navigation, and footers."
        },
        "ErrMultipleBannerLandmarksOnPage": {
            "id": "ErrMultipleBannerLandmarksOnPage",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Multiple banner landmarks found",
            "why_it_matters": "Multiple headers confuse page structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one banner landmark"
        },
        "ErrMultipleContentinfoLandmarksOnPage": {
            "id": "ErrMultipleContentinfoLandmarksOnPage",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Multiple contentinfo landmarks found",
            "why_it_matters": "Multiple footers confuse page structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one contentinfo landmark"
        },
        "ErrBannerLandmarkAccessibleNameIsBlank": {
            "id": "ErrBannerLandmarkAccessibleNameIsBlank",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Banner landmark has blank accessible name",
            "why_it_matters": "Multiple banners need labels to distinguish them",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add aria-label or aria-labelledby"
        },
        "ErrNavLandmarkAccessibleNameIsBlank": {
            "id": "ErrNavLandmarkAccessibleNameIsBlank",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Navigation landmark has blank accessible name",
            "why_it_matters": "Multiple nav areas need labels",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add aria-label like \"Main navigation\" or \"Footer navigation\""
        },
        "WarnNavLandmarkHasNoLabel": {
            "id": "WarnNavLandmarkHasNoLabel",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Navigation landmark lacks label",
            "why_it_matters": "Hard to distinguish multiple navigation areas",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add descriptive aria-label"
        },
        "ErrMainLandmarkMayNotbeChildOfAnotherLandmark": {
            "id": "ErrMainLandmarkMayNotbeChildOfAnotherLandmark",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Main landmark nested inside another landmark",
            "why_it_matters": "Invalid landmark nesting breaks structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Move main outside of other landmarks"
        },
        "ErrBannerLandmarkMayNotBeChildOfAnotherLandmark": {
            "id": "ErrBannerLandmarkMayNotBeChildOfAnotherLandmark",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Banner landmark nested inside another landmark",
            "why_it_matters": "Invalid nesting breaks page structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Move banner to top level"
        },
        "ErrNestedNavLandmarks": {
            "id": "ErrNestedNavLandmarks",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Navigation landmarks are nested",
            "why_it_matters": "Confusing navigation structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Flatten navigation structure"
        },
        "ErrElementNotContainedInALandmark": {
            "id": "ErrElementNotContainedInALandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Content exists outside of any landmark",
            "why_it_matters": "Content may be missed when navigating by landmarks",
            "who_it_affects": "Screen reader users using landmark navigation",
            "how_to_fix": "Ensure all content is within appropriate landmarks"
        },
        "ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Main landmark has both aria-label and aria-labelledby attributes",
            "why_it_matters": "Conflicting labeling methods may cause confusion",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method - either aria-label or aria-labelledby"
        },
        "ErrMainLandmarkHasTabindexOfZeroCanOnlyHaveMinusOneAtMost": {
            "id": "ErrMainLandmarkHasTabindexOfZeroCanOnlyHaveMinusOneAtMost",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3",
            "category": "landmarks",
            "description": "Main landmark has tabindex=\"0\" which is inappropriate",
            "why_it_matters": "Landmarks should not be in the tab order",
            "who_it_affects": "Keyboard users",
            "how_to_fix": "Remove tabindex or use tabindex=\"-1\" if programmatic focus is needed"
        },
        "ErrMainLandmarkIsHidden": {
            "id": "ErrMainLandmarkIsHidden",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Main landmark is hidden from view",
            "why_it_matters": "Hidden main content defeats the purpose of the landmark",
            "who_it_affects": "All users",
            "how_to_fix": "Ensure main landmark is visible or remove if not needed"
        },
        "ErrDuplicateLabelForComplementaryLandmark": {
            "id": "ErrDuplicateLabelForComplementaryLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple complementary landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different complementary sections",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Provide unique labels for each complementary landmark"
        },
        "ErrComplementaryLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrComplementaryLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Complementary landmark has both aria-label and aria-labelledby",
            "why_it_matters": "Conflicting labeling methods may cause confusion",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method"
        },
        "ErrComplementaryLandmarkMayNotBeChildOfAnotherLandmark": {
            "id": "ErrComplementaryLandmarkMayNotBeChildOfAnotherLandmark",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Complementary landmark is nested inside another landmark",
            "why_it_matters": "Invalid nesting breaks landmark structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Move complementary landmark outside of other landmarks"
        },
        "WarnComplementaryLandmarkHasNoLabel": {
            "id": "WarnComplementaryLandmarkHasNoLabel",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Complementary landmark lacks a label",
            "why_it_matters": "Hard to distinguish multiple complementary sections",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add aria-label or aria-labelledby to identify the purpose"
        },
        "ErrComplementaryLandmarkAccessibleNameIsBlank": {
            "id": "ErrComplementaryLandmarkAccessibleNameIsBlank",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Complementary landmark has blank accessible name",
            "why_it_matters": "Empty labels provide no information",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add meaningful label text"
        },
        "WarnComplementaryLandmarkAccessibleNameUsesComplementary": {
            "id": "WarnComplementaryLandmarkAccessibleNameUsesComplementary",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "landmarks",
            "description": "Complementary landmark label uses generic term \"complementary\"",
            "why_it_matters": "Generic labels don't describe specific content",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use descriptive labels like \"Related articles\" or \"Sidebar\""
        },
        "ErrDuplicateLabelForNavLandmark": {
            "id": "ErrDuplicateLabelForNavLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple navigation landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different navigation areas",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Provide unique labels like \"Main navigation\" and \"Footer navigation\""
        },
        "ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Navigation landmark has both aria-label and aria-labelledby",
            "why_it_matters": "Conflicting labeling methods",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method"
        },
        "WarnNavLandmarkAccessibleNameUsesNavigation": {
            "id": "WarnNavLandmarkAccessibleNameUsesNavigation",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "landmarks",
            "description": "Navigation landmark uses generic term \"navigation\" in label",
            "why_it_matters": "Generic labels don't describe specific purpose",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use more descriptive labels like \"Product categories\" or \"User account menu\""
        },
        "ErrCompletelyEmptyNavLandmark": {
            "id": "ErrCompletelyEmptyNavLandmark",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Navigation landmark contains no content",
            "why_it_matters": "Empty navigation serves no purpose",
            "who_it_affects": "All users",
            "how_to_fix": "Add navigation content or remove empty landmark"
        },
        "ErrNavLandmarkContainsOnlyWhiteSpace": {
            "id": "ErrNavLandmarkContainsOnlyWhiteSpace",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Navigation landmark contains only whitespace",
            "why_it_matters": "Whitespace-only navigation is not functional",
            "who_it_affects": "All users",
            "how_to_fix": "Add navigation links or remove the landmark"
        },
        "ErrDuplicateLabelForRegionLandmark": {
            "id": "ErrDuplicateLabelForRegionLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple region landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different regions",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Provide unique labels for each region"
        },
        "ErrRegionLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrRegionLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Region landmark has both aria-label and aria-labelledby",
            "why_it_matters": "Conflicting labeling methods",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method"
        },
        "WarnRegionLandmarkHasNoLabelSoIsNotConsideredALandmark": {
            "id": "WarnRegionLandmarkHasNoLabelSoIsNotConsideredALandmark",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Region landmark lacks required label to be considered a landmark",
            "why_it_matters": "Regions without labels are not exposed as landmarks",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add aria-label or aria-labelledby, or use a different landmark type"
        },
        "RegionLandmarkAccessibleNameIsBlank": {
            "id": "RegionLandmarkAccessibleNameIsBlank",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Region landmark has blank accessible name",
            "why_it_matters": "Blank labels provide no information",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add meaningful label text"
        },
        "WarnRegionLandmarkAccessibleNameUsesNavigation": {
            "id": "WarnRegionLandmarkAccessibleNameUsesNavigation",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "landmarks",
            "description": "Region landmark incorrectly uses \"navigation\" in its label",
            "why_it_matters": "Confusing landmark type and purpose",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use appropriate label or change to nav landmark"
        },
        "ErrDuplicateLabelForBannerLandmark": {
            "id": "ErrDuplicateLabelForBannerLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple banner landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different banners",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Only one banner should typically exist per page"
        },
        "ErrBannerLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrBannerLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Banner landmark has both aria-label and aria-labelledby",
            "why_it_matters": "Conflicting labeling methods",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method"
        },
        "WarnBannerLandmarkAccessibleNameUsesBanner": {
            "id": "WarnBannerLandmarkAccessibleNameUsesBanner",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "landmarks",
            "description": "Banner landmark uses generic term \"banner\" in label",
            "why_it_matters": "Redundant labeling",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use descriptive label or rely on implicit role"
        },
        "WarnMultipleBannerLandmarksButNotAllHaveLabels": {
            "id": "WarnMultipleBannerLandmarksButNotAllHaveLabels",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple banner landmarks exist but not all have labels",
            "why_it_matters": "Inconsistent labeling makes navigation difficult",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Ensure all banner landmarks have labels or reduce to single banner"
        },
        "ErrDuplicateLabelForContentinfoLandmark": {
            "id": "ErrDuplicateLabelForContentinfoLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple contentinfo landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different footer areas",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Typically only one contentinfo should exist per page"
        },
        "ErrContentInfoLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrContentInfoLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Contentinfo landmark has both aria-label and aria-labelledby",
            "why_it_matters": "Conflicting labeling methods",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method"
        },
        "ErrContentinfoLandmarkMayNotBeChildOfAnotherLandmark": {
            "id": "ErrContentinfoLandmarkMayNotBeChildOfAnotherLandmark",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Contentinfo landmark is nested inside another landmark",
            "why_it_matters": "Invalid nesting breaks landmark structure",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Move contentinfo to top level"
        },
        "WarnContentInfoLandmarkHasNoLabel": {
            "id": "WarnContentInfoLandmarkHasNoLabel",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Contentinfo landmark lacks a label",
            "why_it_matters": "May be harder to identify purpose",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add descriptive label if multiple contentinfo exist"
        },
        "ErrContentInfoLandmarkAccessibleNameIsBlank": {
            "id": "ErrContentInfoLandmarkAccessibleNameIsBlank",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Contentinfo landmark has blank accessible name",
            "why_it_matters": "Blank labels provide no information",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add meaningful label text"
        },
        "WarnContentinfoLandmarkAccessibleNameUsesContentinfo": {
            "id": "WarnContentinfoLandmarkAccessibleNameUsesContentinfo",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "landmarks",
            "description": "Contentinfo landmark uses generic term \"contentinfo\" in label",
            "why_it_matters": "Redundant labeling",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use descriptive label or rely on implicit role"
        },
        "WarnMultipleContentInfoLandmarksButNotAllHaveLabels": {
            "id": "WarnMultipleContentInfoLandmarksButNotAllHaveLabels",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple contentinfo landmarks exist but not all have labels",
            "why_it_matters": "Inconsistent labeling makes navigation difficult",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Ensure all contentinfo landmarks have labels or reduce to single contentinfo"
        },
        "WarnFormHasNoLabelSoIsNotLandmark": {
            "id": "WarnFormHasNoLabelSoIsNotLandmark",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Form element lacks label so is not exposed as landmark",
            "why_it_matters": "Forms without accessible names are not landmarks",
            "who_it_affects": "Screen reader users navigating by landmarks",
            "how_to_fix": "Add aria-label or aria-labelledby to make it a landmark"
        },
        "ErrDuplicateLabelForFormLandmark": {
            "id": "ErrDuplicateLabelForFormLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple form landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different forms",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Provide unique labels for each form"
        },
        "ErrFormUsesAriaLabelInsteadOfVisibleElement": {
            "id": "ErrFormUsesAriaLabelInsteadOfVisibleElement",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.5.3", "3.3.2"],
            "wcag_full": "2.5.3, 3.3.2",
            "category": "landmarks",
            "description": "Form uses aria-label instead of visible heading or label",
            "why_it_matters": "Visible labels benefit all users",
            "who_it_affects": "All users, especially those with cognitive disabilities",
            "how_to_fix": "Use visible heading with aria-labelledby"
        },
        "ErrFormUsesTitleAttribute": {
            "id": "ErrFormUsesTitleAttribute",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Form uses title attribute for labeling",
            "why_it_matters": "Title attributes are not reliably accessible",
            "who_it_affects": "Screen reader users, mobile users",
            "how_to_fix": "Use aria-label or aria-labelledby instead"
        },
        "ErrFormAriaLabelledByIsBlank": {
            "id": "ErrFormAriaLabelledByIsBlank",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "landmarks",
            "description": "Form aria-labelledby references blank or empty element",
            "why_it_matters": "No accessible name is provided",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Reference element with actual text content"
        },
        "ErrFormAriaLabelledByReferenceDoesNotExist": {
            "id": "ErrFormAriaLabelledByReferenceDoesNotExist",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "landmarks",
            "description": "Form aria-labelledby references non-existent element",
            "why_it_matters": "Broken reference provides no accessible name",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Fix ID reference or use different labeling method"
        },
        "ErrFormAriaLabelledByReferenceDoesNotReferenceAHeading": {
            "id": "ErrFormAriaLabelledByReferenceDoesNotReferenceAHeading",
            "type": "Error",
            "impact": "Low",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Form aria-labelledby doesn't reference a heading element",
            "why_it_matters": "Best practice is to reference headings for form landmarks",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Reference a heading element when possible"
        },
        "ErrFormAriaLabelledByReferenceDIsHidden": {
            "id": "ErrFormAriaLabelledByReferenceDIsHidden",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "4.1.2"],
            "wcag_full": "1.3.1, 4.1.2",
            "category": "landmarks",
            "description": "Form aria-labelledby references hidden element",
            "why_it_matters": "Hidden elements may not provide accessible names",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Reference visible elements only"
        },
        "ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs": {
            "id": "ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "landmarks",
            "description": "Form landmark has both aria-label and aria-labelledby",
            "why_it_matters": "Conflicting labeling methods",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use only one labeling method"
        },
        "ErrFormLandmarkAccessibleNameIsBlank": {
            "id": "ErrFormLandmarkAccessibleNameIsBlank",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Form landmark has blank accessible name",
            "why_it_matters": "Forms need clear identification",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Add meaningful label describing form purpose"
        },
        "WarnFormLandmarkAccessibleNameUsesForm": {
            "id": "WarnFormLandmarkAccessibleNameUsesForm",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6",
            "category": "landmarks",
            "description": "Form landmark uses generic term \"form\" in label",
            "why_it_matters": "Generic labels don't describe purpose",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use descriptive labels like \"Contact form\" or \"Search form\""
        },
        "ErrDuplicateLabelForSearchLandmark": {
            "id": "ErrDuplicateLabelForSearchLandmark",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple search landmarks have the same label",
            "why_it_matters": "Users cannot distinguish between different search areas",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Provide unique labels for each search landmark"
        },
        "WarnHeadingFoundInsideLandmarkButDoesntLabelLandmark": {
            "id": "WarnHeadingFoundInsideLandmarkButDoesntLabelLandmark",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Heading inside landmark doesn't label the landmark",
            "why_it_matters": "Missed opportunity for clear landmark labeling",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Consider using heading as landmark label via aria-labelledby"
        },
        "WarnHeadingFoundInLandmarkButIsLabelledByAnAriaLabelledBy": {
            "id": "WarnHeadingFoundInLandmarkButIsLabelledByAnAriaLabelledBy",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1",
            "category": "landmarks",
            "description": "Landmark has heading but uses different element for label",
            "why_it_matters": "Confusing when heading doesn't match landmark label",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use the heading as the landmark label"
        },
        "WarnMultipleComplementaryLandmarksButNotAllHaveLabels": {
            "id": "WarnMultipleComplementaryLandmarksButNotAllHaveLabels",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple complementary landmarks but not all labeled",
            "why_it_matters": "Inconsistent labeling makes navigation difficult",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Ensure all complementary landmarks have unique labels"
        },
        "WarnMultipleNavLandmarksButNotAllHaveLabels": {
            "id": "WarnMultipleNavLandmarksButNotAllHaveLabels",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple navigation landmarks but not all labeled",
            "why_it_matters": "Users cannot distinguish between navigation areas",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Label all navigation landmarks uniquely"
        },
        "WarnMultipleRegionLandmarksButNotAllHaveLabels": {
            "id": "WarnMultipleRegionLandmarksButNotAllHaveLabels",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.3.1", "2.4.6"],
            "wcag_full": "1.3.1, 2.4.6",
            "category": "landmarks",
            "description": "Multiple region landmarks but not all labeled",
            "why_it_matters": "Regions without labels are not exposed as landmarks",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Ensure all regions have labels or use different elements"
        },
        "ErrTextContrast": {
            "id": "ErrTextContrast",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.3", "1.4.6"],
            "wcag_full": "1.4.3 Contrast (Minimum), 1.4.6 Contrast (Enhanced)",
            "category": "color",
            "description": "Text color has insufficient contrast ratio with its background color",
            "why_it_matters": "Users with low vision, color blindness, or who are viewing content in bright sunlight may not be able to read text that doesn't have sufficient contrast with its background. This creates barriers to accessing information and can make content completely unreadable. Insufficient contrast is one of the most common accessibility issues and affects a large number of users.",
            "who_it_affects": "Users with low vision who need higher contrast to distinguish text, users with color blindness who may have difficulty distinguishing certain color combinations, older users experiencing age-related vision changes, and any user viewing content in bright sunlight or on low-quality displays",
            "how_to_fix": "Ensure text has a contrast ratio of at least 4.5:1 with its background for normal text, or 3:1 for large text (18pt or 14pt bold). For enhanced accessibility (Level AAA), use 7:1 for normal text and 4.5:1 for large text. Use a contrast checking tool to verify ratios and test with actual users when possible. Consider providing a high contrast mode option."
        },
        "ErrColorStyleDefinedExplicitlyInElement": {
            "id": "ErrColorStyleDefinedExplicitlyInElement",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.4.3"],
            "wcag_full": "1.4.3",
            "category": "color",
            "description": "Color defined inline on element",
            "why_it_matters": "Inline styles are harder to maintain and override",
            "who_it_affects": "Users who need custom color schemes",
            "how_to_fix": "Move color definitions to CSS classes"
        },
        "ErrColorStyleDefinedExplicitlyInStyleTag": {
            "id": "ErrColorStyleDefinedExplicitlyInStyleTag",
            "type": "Error",
            "impact": "Low",
            "wcag": ["1.4.3"],
            "wcag_full": "1.4.3",
            "category": "color",
            "description": "Color defined in style tag",
            "why_it_matters": "Embedded styles harder to override",
            "who_it_affects": "Users with custom stylesheets",
            "how_to_fix": "Use external stylesheets"
        },
        "ErrColorRelatedStyleDefinedExplicitlyInElement": {
            "id": "ErrColorRelatedStyleDefinedExplicitlyInElement",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.4.3"],
            "wcag_full": "1.4.3",
            "category": "color",
            "description": "Color-related styles defined inline",
            "why_it_matters": "Harder to maintain consistent color scheme",
            "who_it_affects": "Users needing high contrast modes",
            "how_to_fix": "Use CSS classes instead of inline styles"
        },
        "ErrColorRelatedStyleDefinedExplicitlyInStyleTag": {
            "id": "ErrColorRelatedStyleDefinedExplicitlyInStyleTag",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.4.3"],
            "wcag_full": "1.4.3",
            "category": "color",
            "description": "Color-related styles defined in style tag",
            "why_it_matters": "Embedded color styles harder to override for user preferences",
            "who_it_affects": "Users with custom stylesheets, high contrast mode users",
            "how_to_fix": "Use external stylesheets for better maintainability"
        },
        "ErrPrimaryLangUnrecognized": {
            "id": "ErrPrimaryLangUnrecognized",
            "type": "Error",
            "impact": "High",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "Language code not recognized",
            "why_it_matters": "Invalid language codes prevent proper pronunciation",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use valid ISO 639-1 language codes"
        },
        "ErrIncorrectlyFormattedPrimaryLang": {
            "id": "ErrIncorrectlyFormattedPrimaryLang",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "Language code incorrectly formatted",
            "why_it_matters": "Malformed codes may not work properly",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use correct format: \"en-US\" or \"en\""
        },
        "ErrElementPrimaryLangNotRecognized": {
            "id": "ErrElementPrimaryLangNotRecognized",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.1.1", "3.1.2"],
            "wcag_full": "3.1.1, 3.1.2",
            "category": "language",
            "description": "Element has unrecognized language code",
            "why_it_matters": "Language changes won't be announced properly",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use valid language codes"
        },
        "ErrPrimaryLangAndXmlLangMismatch": {
            "id": "ErrPrimaryLangAndXmlLangMismatch",
            "type": "Error",
            "impact": "Low",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "lang and xml:lang attributes don't match",
            "why_it_matters": "Conflicting language information",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Ensure both attributes have same value"
        },
        "ErrHreflangNotOnLink": {
            "id": "ErrHreflangNotOnLink",
            "type": "Error",
            "impact": "Low",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "hreflang attribute on non-link element",
            "why_it_matters": "hreflang only works on links",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Move hreflang to anchor elements only"
        },
        "ErrRegionQualifierForPrimaryLangNotRecognized": {
            "id": "ErrRegionQualifierForPrimaryLangNotRecognized",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "Region qualifier in primary language code not recognized (e.g., \"en-XY\")",
            "why_it_matters": "Invalid region codes may cause incorrect pronunciation",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use valid ISO 3166-1 region codes like \"en-US\", \"en-GB\""
        },
        "ErrEmptyXmlLangAttr": {
            "id": "ErrEmptyXmlLangAttr",
            "type": "Error",
            "impact": "High",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "xml:lang attribute is empty",
            "why_it_matters": "Empty xml:lang provides no language information",
            "who_it_affects": "Screen reader users using XML/XHTML parsers",
            "how_to_fix": "Add valid language code to xml:lang attribute"
        },
        "ErrPrimaryXmlLangUnrecognized": {
            "id": "ErrPrimaryXmlLangUnrecognized",
            "type": "Error",
            "impact": "High",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "xml:lang language code not recognized",
            "why_it_matters": "Invalid xml:lang codes prevent proper pronunciation",
            "who_it_affects": "Screen reader users in XML/XHTML contexts",
            "how_to_fix": "Use valid ISO 639-1 language codes"
        },
        "ErrRegionQualifierForPrimaryXmlLangNotRecognized": {
            "id": "ErrRegionQualifierForPrimaryXmlLangNotRecognized",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "Region qualifier in xml:lang not recognized",
            "why_it_matters": "Invalid region codes in xml:lang may cause issues",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use valid ISO 3166-1 region codes"
        },
        "ErrElementRegionQualifierNotRecognized": {
            "id": "ErrElementRegionQualifierNotRecognized",
            "type": "Error",
            "impact": "Low",
            "wcag": ["3.1.2"],
            "wcag_full": "3.1.2",
            "category": "language",
            "description": "Element lang attribute has unrecognized region qualifier",
            "why_it_matters": "Invalid region codes may affect pronunciation",
            "who_it_affects": "Screen reader users",
            "how_to_fix": "Use valid ISO 3166-1 region codes"
        },
        "ErrEmptyLanguageAttribute": {
            "id": "ErrEmptyLanguageAttribute",
            "type": "Error",
            "impact": "High",
            "wcag": ["3.1.2"],
            "wcag_full": "3.1.2 Language of Parts (Level AA)",
            "category": "language",
            "description": "Element (non-HTML) has a lang attribute present but with no value (lang=\"\"), preventing screen readers from determining language changes",
            "why_it_matters": "An empty lang attribute on elements prevents screen readers from properly switching pronunciation rules for content in different languages",
            "who_it_affects": "Screen reader users, multilingual users, users with reading disabilities",
            "how_to_fix": "Add a valid language code to the lang attribute (e.g., lang=\"fr\" for French). Use ISO 639-1 two-letter codes. Remove the attribute if language matches page language."
        },
        "ErrHreflangAttrEmpty": {
            "id": "ErrHreflangAttrEmpty",
            "type": "Error",
            "impact": "Low",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "hreflang attribute is empty on link",
            "why_it_matters": "Empty hreflang provides no language information for the linked resource",
            "who_it_affects": "Screen reader users, search engines",
            "how_to_fix": "Add valid language code or remove empty hreflang attribute"
        },
        "ErrPrimaryHrefLangNotRecognized": {
            "id": "ErrPrimaryHrefLangNotRecognized",
            "type": "Error",
            "impact": "Low",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "hreflang language code not recognized",
            "why_it_matters": "Invalid hreflang codes provide incorrect information about linked resources",
            "who_it_affects": "Screen reader users, search engines",
            "how_to_fix": "Use valid ISO 639-1 language codes"
        },
        "ErrRegionQualifierForHreflangUnrecognized": {
            "id": "ErrRegionQualifierForHreflangUnrecognized",
            "type": "Error",
            "impact": "Low",
            "wcag": ["3.1.1"],
            "wcag_full": "3.1.1",
            "category": "language",
            "description": "hreflang region qualifier not recognized",
            "why_it_matters": "Invalid region codes in hreflang attributes",
            "who_it_affects": "Screen reader users, search engines",
            "how_to_fix": "Use valid ISO 3166-1 region codes"
        },
        "ErrOutlineIsNoneOnInteractiveElement": {
            "id": "ErrOutlineIsNoneOnInteractiveElement",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "focus",
            "description": "Interactive element has CSS outline:none removing the default focus indicator",
            "why_it_matters": "People with mobility disabilities use keyboard or keyboard-alternate devices to navigate rather than a mouse. Visible focus indicators are essential as they perform the same function as a mouse cursor. Without focus indicators, users cannot tell where they are on the page or when interactive elements are focused. This makes keyboard navigation impossible and can completely prevent access to functionality.",
            "who_it_affects": "Sighted users with motor disabilities navigating with keyboard or keyboard-alternate devices, users who prefer keyboard navigation for efficiency, users with temporary injuries preventing mouse use, and users of assistive technologies that rely on keyboard navigation",
            "how_to_fix": "Never use outline:none without providing an alternative visible focus indicator. The focus indicator must be clearly visible with at least 3:1 contrast ratio with the background, be at least 2 pixels thick, and ideally be offset from the element to maximize visibility. Consider using CSS :focus-visible for better control over when focus indicators appear."
        },
        "ErrNoOutlineOffsetDefined": {
            "id": "ErrNoOutlineOffsetDefined",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7",
            "category": "focus",
            "description": "No outline offset defined for focus",
            "why_it_matters": "Focus indicator may be hard to see",
            "who_it_affects": "Keyboard users",
            "how_to_fix": "Add outline-offset for better visibility"
        },
        "ErrZeroOutlineOffset": {
            "id": "ErrZeroOutlineOffset",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7",
            "category": "focus",
            "description": "Outline offset is set to zero",
            "why_it_matters": "Focus indicator touches element edge",
            "who_it_affects": "Keyboard users with low vision",
            "how_to_fix": "Use positive outline-offset value"
        },
        "ErrPositiveTabIndex": {
            "id": "ErrPositiveTabIndex",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3 Focus Order",
            "category": "focus",
            "description": "Element uses a positive tabindex value (greater than 0)",
            "why_it_matters": "Positive tabindex values override the natural tab order of the page, creating an unpredictable navigation experience. When you use tabindex=\"1\" or higher, that element jumps to the front of the tab order, regardless of where it appears visually. This breaks the expected top-to-bottom, left-to-right flow that keyboard users rely on. Users might tab from the header straight to a random form field in the middle of the page, then jump to the footer, then back to the navigation. This confusing order makes it easy to miss content, difficult to predict where focus will go next, and nearly impossible to maintain as the page evolves.",
            "who_it_affects": "Keyboard users who expect logical, predictable navigation order, screen reader users who rely on consistent focus flow, users with motor disabilities who need efficient keyboard navigation, users with cognitive disabilities who are confused by unpredictable focus movement, and developers maintaining the code who must manage complex tabindex values",
            "how_to_fix": "Remove positive tabindex values and use only tabindex=\"0\" (adds element to natural tab order) or tabindex=\"-1\" (removes from tab order but allows programmatic focus). Let the DOM order determine tab order - if elements need to be reached in a different order, rearrange them in the HTML. If visual order must differ from DOM order for design reasons, consider using CSS Grid or Flexbox with the order property, but be cautious as this can still cause accessibility issues."
        },
        "ErrNegativeTabIndex": {
            "id": "ErrNegativeTabIndex",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3",
            "category": "focus",
            "description": "Negative tabindex on interactive element",
            "why_it_matters": "Element removed from tab order",
            "who_it_affects": "Keyboard users",
            "how_to_fix": "Use tabindex=\"0\" for interactive elements"
        },
        "ErrTabindexOfZeroOnNonInteractiveElement": {
            "id": "ErrTabindexOfZeroOnNonInteractiveElement",
            "type": "Error",
            "impact": "Low",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3",
            "category": "focus",
            "description": "tabindex=\"0\" on non-interactive element",
            "why_it_matters": "Non-interactive elements in tab order",
            "who_it_affects": "Keyboard users",
            "how_to_fix": "Remove tabindex from non-interactive elements"
        },
        "ErrWrongTabindexForInteractiveElement": {
            "id": "ErrWrongTabindexForInteractiveElement",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3",
            "category": "focus",
            "description": "Inappropriate tabindex on interactive element",
            "why_it_matters": "Tab order doesn't match visual order",
            "who_it_affects": "Keyboard users",
            "how_to_fix": "Let natural tab order work, avoid tabindex"
        },
        "ErrTTabindexOnNonInteractiveElement": {
            "id": "ErrTTabindexOnNonInteractiveElement",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3",
            "category": "focus",
            "description": "Tabindex attribute on non-interactive element",
            "why_it_matters": "Non-interactive elements should not be in tab order unless they serve a specific purpose",
            "who_it_affects": "Keyboard users",
            "how_to_fix": "Remove tabindex from non-interactive elements or make them properly interactive"
        },
        "WarnFontNotInRecommenedListForA11y": {
            "id": "WarnFontNotInRecommenedListForA11y",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.4.8"],
            "wcag_full": "1.4.8",
            "category": "fonts",
            "description": "Font not in recommended accessibility list",
            "why_it_matters": "Some fonts are harder to read",
            "who_it_affects": "Users with dyslexia, low vision",
            "how_to_fix": "Use clear, simple fonts like Arial, Verdana"
        },
        "DiscoFontFound": {
            "id": "DiscoFontFound",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": [],
            "wcag_full": "N/A",
            "category": "fonts",
            "description": "Font usage detected for review",
            "why_it_matters": "Some fonts may have readability issues",
            "who_it_affects": "Users with reading disabilities",
            "how_to_fix": "Review font choices for readability"
        },
        "ErrTitleAttrFound": {
            "id": "ErrTitleAttrFound",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["5.2.4", "4.1.2"],
            "wcag_full": "5.2.4 Accessible Documentation (Conformance Requirement), 4.1.2 Name, Role, Value (Level A)",
            "category": "title",
            "description": "Title attribute used - fundamentally inaccessible to assistive technology",
            "why_it_matters": "Title attributes fail WCAG Conformance requirement 5.2.4. For screen magnifier users at high magnification, tooltip content goes off-screen and disappears when mouse moves, making content completely inaccessible",
            "who_it_affects": "Screen magnifier users, mobile and touch screen users, keyboard-only users, screen reader users, users with motor or cognitive disabilities",
            "how_to_fix": "Never use title attributes. Use visible text, proper <label> elements for forms, aria-label for icons, or visible helper text"
        },
        "ErrEmptyTitleAttr": {
            "id": "ErrEmptyTitleAttr",
            "type": "Error",
            "impact": "Low",
            "wcag": ["4.1.2"],
            "wcag_full": "4.1.2",
            "category": "title",
            "description": "Empty title attribute",
            "why_it_matters": "Empty titles provide no information and add unnecessary markup",
            "who_it_affects": "Users expecting tooltip information",
            "how_to_fix": "Remove empty title attributes or provide meaningful descriptive text"
        },
        "ErrImproperTitleAttribute": {
            "id": "ErrImproperTitleAttribute",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["5.2.4", "3.3.2"],
            "wcag_full": "5.2.4 Accessible Documentation (Conformance Requirement), 3.3.2 Labels or Instructions (Level A)",
            "category": "title",
            "description": "Title attribute used in particularly problematic patterns (on non-focusable elements or duplicating visible text)",
            "why_it_matters": "Title attributes fail WCAG 5.2.4 - screen magnifier users at high magnification cannot read tooltips as content goes off-screen. This flags especially bad patterns: titles on non-focusable elements where users can't even trigger the tooltip, and redundant titles that provide no value",
            "who_it_affects": "Screen magnifier users, mobile users, keyboard-only users, users with motor disabilities",
            "how_to_fix": "Never use title attributes on body elements. Remove titles from non-focusable containers (div, span). Remove redundant titles. Use visible text, proper labels, or visible helper text instead"
        },
        "WarnVagueTitleAttribute": {
            "id": "WarnVagueTitleAttribute",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["5.2.4", "3.3.2"],
            "wcag_full": "5.2.4 Accessible Documentation (Conformance Requirement), 3.3.2 Labels or Instructions (Level A)",
            "category": "title",
            "description": "Title attribute contains vague or generic text that provides no useful information",
            "why_it_matters": "Title attributes fundamentally fail WCAG 5.2.4 - screen magnifier users cannot read tooltips as content goes off-screen. Vague titles like 'Click here', 'Link', 'Button' compound the problem by providing no value even for users who can access them",
            "who_it_affects": "Screen magnifier users (fundamental inaccessibility), mobile users, keyboard users, all users who would benefit from clear information",
            "how_to_fix": "Never use title attributes (they fail WCAG 5.2.4). Remove title entirely and use visible text, proper labels, aria-label, or visible helper text instead"
        },
        "ErrIframeWithNoTitleAttr": {
            "id": "ErrIframeWithNoTitleAttr",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.1", "4.1.2"],
            "wcag_full": "2.4.1 Bypass Blocks, 4.1.2 Name, Role, Value",
            "category": "title",
            "description": "Iframe element is missing the required title attribute",
            "why_it_matters": "Iframes embed external content like videos, maps, or forms within your page. Without a title attribute, screen reader users hear only \"iframe\" with no indication of what content it contains. This is like having a door with no label - users don't know what's behind it. They must enter the iframe and explore its content to understand its purpose, which is time-consuming and may be confusing if the iframe content lacks context. For pages with multiple iframes, users cannot distinguish between them or decide which ones are worth exploring.",
            "who_it_affects": "Screen reader users who need to understand what each iframe contains before deciding whether to interact with it, keyboard users navigating through iframes who need context about embedded content, users with cognitive disabilities who need clear labeling of all page regions, and users on slow connections who may experience delays loading iframe content",
            "how_to_fix": "Add a title attribute to every iframe that concisely describes its content or purpose (e.g., title=\"YouTube video: Product demonstration\", title=\"Google Maps: Office location\", title=\"Payment form\"). The title should be unique if there are multiple iframes. Keep it brief but descriptive enough that users understand what the iframe contains without having to enter it. For decorative iframes (rare), you can use title=\"\" and add tabindex=\"-1\" to remove it from tab order."
        },
        "ErrAriaLabelMayNotBeFoundByVoiceControl": {
            "id": "ErrAriaLabelMayNotBeFoundByVoiceControl",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.5.3"],
            "wcag_full": "2.5.3",
            "category": "aria",
            "description": "aria-label doesn't match visible text",
            "why_it_matters": "Voice control users can't activate element",
            "who_it_affects": "Voice control users",
            "how_to_fix": "Ensure aria-label includes visible text"
        },
        "ErrLabelMismatchOfAccessibleNameAndLabelText": {
            "id": "ErrLabelMismatchOfAccessibleNameAndLabelText",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.5.3"],
            "wcag_full": "2.5.3",
            "category": "aria",
            "description": "Accessible name doesn't match visible label",
            "why_it_matters": "Confusing for voice control users",
            "who_it_affects": "Voice control users",
            "how_to_fix": "Make accessible name match visible text"
        },
        "DiscoStyleAttrOnElements": {
            "id": "DiscoStyleAttrOnElements",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": [],
            "wcag_full": "N/A",
            "category": "style",
            "description": "Inline styles detected",
            "why_it_matters": "May affect responsive design and user customization",
            "who_it_affects": "Users with custom stylesheets",
            "how_to_fix": "Consider moving to CSS classes"
        },
        "DiscoStyleElementOnPage": {
            "id": "DiscoStyleElementOnPage",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": [],
            "wcag_full": "N/A",
            "category": "style",
            "description": "Style element found in page",
            "why_it_matters": "Embedded styles harder to override",
            "who_it_affects": "Users needing custom styles",
            "how_to_fix": "Consider external stylesheets"
        },
        "DiscoResponsiveBreakpoints": {
            "id": "DiscoResponsiveBreakpoints",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": ["1.4.10", "2.4.3"],
            "wcag_full": "1.4.10 Reflow (AA), 2.4.3 Focus Order (A)",
            "category": "responsive",
            "description": "Responsive breakpoints detected on page",
            "why_it_matters": "Layout changes at different viewport widths may affect accessibility",
            "who_it_affects": "Mobile and tablet users, users who zoom content",
            "how_to_fix": "Test accessibility at each defined breakpoint"
        },
        "DiscoFoundJS": {
            "id": "DiscoFoundJS",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": [],
            "wcag_full": "N/A",
            "category": "javascript",
            "description": "JavaScript detected on page",
            "why_it_matters": "Functionality should work without JavaScript",
            "who_it_affects": "Users with JavaScript disabled",
            "how_to_fix": "Ensure progressive enhancement"
        },
        "ErrButtonTextLowContrast": {
            "id": "ErrButtonTextLowContrast",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.3"],
            "wcag_full": "1.4.3 Contrast (Minimum)",
            "category": "buttons",
            "description": "Button text has insufficient color contrast with button background",
            "why_it_matters": "Users with low vision, color blindness, or viewing the page in bright sunlight may not be able to read button labels if contrast is insufficient. This prevents users from understanding button purpose and can make critical functions inaccessible. Buttons are action triggers, so being unable to read them can prevent task completion.",
            "who_it_affects": "Users with low vision, color blindness, age-related vision changes, and anyone viewing content in poor lighting conditions or on low-quality displays",
            "how_to_fix": "Ensure button text has at least 4.5:1 contrast ratio with the button background for normal text, or 3:1 for large text (18pt or 14pt bold). For Level AAA compliance, use 7:1 for normal text. Test in different states (hover, focus, active) as contrast requirements apply to all states. Avoid using color alone to indicate button state."
        },
        "ErrButtonOutlineNoneNoBoxShadow": {
            "id": "ErrButtonOutlineNoneNoBoxShadow",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.1"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.1 Use of Color",
            "category": "buttons",
            "description": "Button has outline:none on focus with no box-shadow, relying only on color change which fails WCAG 1.4.1",
            "why_it_matters": "Relying solely on color change for focus indication fails WCAG 1.4.1 Use of Color. Users with color blindness, low vision, or monochrome displays cannot perceive focus state. Box-shadow or outline is required to provide a non-color visual indicator that wraps the element.",
            "who_it_affects": "Users with color blindness (8% of males, 0.5% of females), users with low vision, users on monochrome displays, keyboard navigation users",
            "how_to_fix": "Add a box-shadow focus indicator (e.g., box-shadow: 0 0 0 3px rgba(0,102,204,0.5)) or use an outline with outline-offset of at least 2px. Do not rely on color change alone."
        },
        "ErrButtonFocusContrastFail": {
            "id": "ErrButtonFocusContrastFail",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "buttons",
            "description": "Button focus outline has insufficient contrast (less than 3:1) against the button's current background color",
            "why_it_matters": "Focus indicators must have at least 3:1 contrast ratio against adjacent colors per WCAG 1.4.11. Without sufficient contrast, keyboard users cannot see which button has focus, making the interface unusable for keyboard navigation.",
            "who_it_affects": "Users with low vision, users with color vision deficiencies, keyboard navigation users, users in bright lighting conditions",
            "how_to_fix": "Choose an outline color with at least 3:1 contrast against the button background. Test against all button states (default, hover, active). Consider using a high-contrast color like dark blue (#0066cc) on light buttons or white on dark buttons."
        },
        "ErrButtonOutlineWidthInsufficient": {
            "id": "ErrButtonOutlineWidthInsufficient",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "2.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 2.4.11 Focus Appearance",
            "category": "buttons",
            "description": "Button focus outline has outline-width less than 2px, making it too thin to be clearly visible",
            "why_it_matters": "Focus indicators must be thick enough to be clearly visible to keyboard users. Outlines thinner than 2px can be difficult or impossible to see, especially for users with low vision or on high-resolution displays. WCAG 2.4.11 Level AAA requires focus indicators to be at least 2 CSS pixels thick.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users on high-DPI displays, users with cognitive disabilities",
            "how_to_fix": "Set outline-width to at least 2px (e.g., outline: 2px solid #0066cc). For better visibility, consider 3px width. Test on various screen sizes and resolutions to ensure visibility."
        },
        "ErrButtonOutlineOffsetInsufficient": {
            "id": "ErrButtonOutlineOffsetInsufficient",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "buttons",
            "description": "Button focus outline has outline-offset less than 2px, causing the outline to be lost within the button element",
            "why_it_matters": "When outline-offset is less than 2px, the focus outline sits too close to or inside the button border, making it difficult or impossible to see, especially on colored or image buttons. The outline can blend with the button's edge, defeating its purpose.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users with cognitive disabilities who rely on clear visual cues",
            "how_to_fix": "Set outline-offset to at least 2px (e.g., outline-offset: 2px) to create clear space between the button and its focus indicator. This ensures the outline is visible regardless of button styling."
        },
        "ErrButtonFocusObscured": {
            "id": "ErrButtonFocusObscured",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "buttons",
            "description": "Button focus indicator is partially or fully obscured by other elements due to z-index stacking",
            "why_it_matters": "If the focus indicator is hidden behind other elements, keyboard users cannot see which button has focus. This completely breaks keyboard navigation and makes the interface unusable for non-mouse users.",
            "who_it_affects": "Keyboard navigation users, screen magnifier users, users with motor disabilities, power users",
            "how_to_fix": "Review z-index values and stacking contexts. Ensure focused buttons have appropriate z-index to keep focus indicators visible. Use isolation or adjust parent stacking contexts if needed. Test with actual keyboard navigation."
        },
        "WarnButtonOutlineNoneWithBoxShadow": {
            "id": "WarnButtonOutlineNoneWithBoxShadow",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "buttons",
            "description": "Button uses outline:none with box-shadow for focus, which may not provide clear indication on all sides",
            "why_it_matters": "While box-shadow provides a focus indicator, it may not be visible on all sides of the button depending on shadow direction and spread. A clear outline on all four sides is preferred for maximum clarity. Box-shadow can also be harder to see in certain contexts.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users with cognitive disabilities",
            "how_to_fix": "Replace box-shadow with outline and outline-offset (e.g., outline: 2px solid #0066cc; outline-offset: 2px) to ensure a clear border on all sides of the focused button."
        },
        "WarnButtonDefaultFocus": {
            "id": "WarnButtonDefaultFocus",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "buttons",
            "description": "Button uses browser default focus outline which may not meet contrast requirements on all backgrounds",
            "why_it_matters": "Browser default outlines (typically thin blue or dotted lines) often fail to meet 3:1 contrast requirements depending on the background. Different browsers use different default styles, leading to inconsistent and potentially inaccessible experiences.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users on different browsers and operating systems",
            "how_to_fix": "Define explicit focus styles with outline and outline-offset that meet 3:1 contrast ratio. Example: button:focus { outline: 2px solid #0066cc; outline-offset: 2px; }"
        },
        "WarnButtonFocusGradientBackground": {
            "id": "WarnButtonFocusGradientBackground",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "buttons",
            "description": "Button with gradient background has focus outline - contrast cannot be automatically verified against gradient",
            "why_it_matters": "CSS gradients have varying colors across the button, making it impossible to programmatically verify that the focus outline meets 3:1 contrast against all parts of the gradient. The outline may meet contrast at some points but fail at others.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users with color vision deficiencies",
            "how_to_fix": "Manually verify focus outline has at least 3:1 contrast against the lightest AND darkest colors in the gradient. Consider using a solid background color, or add outline-offset to separate the outline from the gradient. Use tools like WebAIM Contrast Checker for verification."
        },
        "WarnButtonFocusImageBackground": {
            "id": "WarnButtonFocusImageBackground",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "buttons",
            "description": "Button with background image has focus outline - contrast cannot be automatically verified against image",
            "why_it_matters": "Background images have varying colors and patterns, making it impossible to programmatically verify focus outline contrast. The outline may be invisible against certain parts of the image, creating unusable focus indicators for keyboard users.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users with color vision deficiencies",
            "how_to_fix": "Manually test focus visibility against all parts of the background image. Consider adding a semi-transparent overlay behind the outline, using outline-offset for separation, or avoiding background images on focusable buttons. Test with multiple users if possible."
        },
        "ErrButtonSingleSideBoxShadow": {
            "id": "ErrButtonSingleSideBoxShadow",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "buttons",
            "description": "Button uses outline:none with box-shadow that only appears on one side (directional shadow with offset)",
            "why_it_matters": "A focus indicator must be visible from all angles. Single-side box-shadows (with x or y offset) only show on one edge of the button, making focus invisible or ambiguous from other directions. Keyboard users cannot reliably determine focus state, especially with complex layouts or when buttons are near other elements.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users with cognitive disabilities who rely on clear visual focus cues",
            "how_to_fix": "Replace single-side box-shadow with outline and outline-offset (e.g., outline: 2px solid #0066cc; outline-offset: 2px), or use box-shadow with zero x/y offset and spread value (e.g., box-shadow: 0 0 0 3px rgba(0,102,204,0.5)) to create an all-around border effect."
        },
        "ErrButtonClipPathWithOutline": {
            "id": "ErrButtonClipPathWithOutline",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible, WCAG Conformance Requirement 5.2.4",
            "category": "buttons",
            "description": "Button with non-rectangular clip-path uses outline for focus indicator - outline draws rectangular box not following clipped shape",
            "why_it_matters": "CSS outline property always draws a rectangular box, even when the button is clipped to a circle, polygon, or other shape. This creates 'ears' or gaps where the outline appears far from the button edge. Users with high magnification (WCAG Conformance 5.2.4) may see only the outline without the button, creating confusion about what is focused. This is a failure of Conformance Requirement 5.2.4 which states that assistive technologies must be able to determine the focus location - a disconnected rectangular outline on a circular button makes this impossible. Failing Conformance Requirement 5.2.4 means the page fails WCAG conformance at ALL levels (A, AA, AAA).",
            "who_it_affects": "Screen magnifier users at high zoom levels (400%+), users with low vision who may only see portions of the interface, keyboard navigation users who need to understand focus location",
            "how_to_fix": "For non-rectangular buttons, use box-shadow or border instead of outline, as these follow the element's shape. Alternatively, consider using rectangular buttons with border-radius for rounded corners, which outline handles better. Test at 400% zoom to ensure focus indicator stays visually connected to the button."
        },
        "ErrButtonTransparentOutline": {
            "id": "ErrButtonTransparentOutline",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "buttons",
            "description": "Button focus outline uses semi-transparent color (alpha < 0.5) which cannot guarantee sufficient visibility",
            "why_it_matters": "Semi-transparent outlines blend with backgrounds, making it impossible to guarantee they meet the 3:1 contrast requirement in all contexts. The effective contrast varies based on background color. When transparency is involved, the outline may achieve sufficient contrast in some positions but fail in others as the page scrolls, during animations, or when overlays appear. Since WCAG requires consistent accessibility, an outline that may or may not be visible depending on context is a failure.",
            "who_it_affects": "Keyboard navigation users, users with low vision, users with color vision deficiencies, users viewing in bright lighting conditions",
            "how_to_fix": "Use fully opaque colors for focus outlines (alpha = 1.0). If subtle styling is desired, use a lighter or darker shade of a fully opaque color. Calculate and verify the outline has 3:1 contrast against all possible backgrounds. For dynamic contexts, test the outline in all states (default, hover, scrolled, with overlays, etc.)."
        },
        "WarnButtonGenericText": {
            "id": "WarnButtonGenericText",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.6"],
            "wcag_full": "2.4.6 Headings and Labels",
            "category": "buttons",
            "description": "Button uses generic text like \"Click here\", \"Submit\", or \"OK\" without context",
            "why_it_matters": "Screen reader users often navigate by pulling up a list of all buttons on a page. Generic button text provides no information about what the button does when heard out of context. Users cannot determine the button's purpose without additional exploration, slowing navigation and potentially causing errors.",
            "who_it_affects": "Screen reader users navigating by buttons list, users with cognitive disabilities who need clear labels, and screen magnifier users who may not see surrounding context",
            "how_to_fix": "Use descriptive button text that explains the action (e.g., \"Submit registration form\" instead of \"Submit\", \"Download PDF report\" instead of \"Download\"). The button text should make sense when read in isolation. If visual design constraints require short text, use aria-label to provide a more descriptive accessible name."
        },
        "ErrLinkTextNotDescriptive": {
            "id": "ErrLinkTextNotDescriptive",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.4"],
            "wcag_full": "2.4.4 Link Purpose (In Context)",
            "category": "links",
            "description": "Link text does not adequately describe the link's destination or purpose",
            "why_it_matters": "Users need to understand where a link will take them before activating it. Vague link text like \"click here\" or \"read more\" provides no information about the destination. Screen reader users often navigate by pulling up a list of all links, where non-descriptive text becomes meaningless out of context.",
            "who_it_affects": "Screen reader users navigating by links list, users with cognitive disabilities who need clear navigation cues, and users with motor disabilities who need to make informed decisions before activating links",
            "how_to_fix": "Write link text that describes the destination or action (e.g., \"Download 2024 annual report\" instead of \"Download\"). Avoid generic phrases. If design constraints require short link text, provide additional context through aria-label or aria-describedby, or ensure surrounding text provides context."
        },
        "ErrLinkOpensNewWindowNoWarning": {
            "id": "ErrLinkOpensNewWindowNoWarning",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.2.2"],
            "wcag_full": "3.2.2 On Input",
            "category": "links",
            "description": "Link opens in new window/tab without warning users",
            "why_it_matters": "Unexpectedly opening new windows can disorient users, especially those using screen readers or magnification. Users may not realize a new window opened and become confused when the back button doesn't work. This is particularly problematic for users with cognitive disabilities or those unfamiliar with browser behaviors.",
            "who_it_affects": "Screen reader users who may not notice the context change, users with cognitive disabilities who may become disoriented, users with motor disabilities who have difficulty managing multiple windows, and novice computer users",
            "how_to_fix": "Add visible text or an icon indicating the link opens in a new window. Include this information in the accessible name (e.g., \"Annual report (opens in new window)\"). Consider whether opening in a new window is necessary - often it's better to open in the same window and let users control this behavior."
        },
        "ErrAnchorTargetTabindex": {
            "id": "ErrAnchorTargetTabindex",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.3"],
            "wcag_full": "2.4.3 Focus Order (Level A)",
            "category": "links",
            "description": "In-page link target (element with id referenced by href=\"#id\") is not keyboard accessible - non-interactive element needs tabindex=\"-1\"",
            "why_it_matters": "When users click an in-page anchor link (like \"Jump to Section 2\"), the browser scrolls to the target element. However, if the target is a non-interactive element (div, section, h2, etc.) without tabindex=\"-1\", keyboard users and screen reader users won't receive focus at the destination. This means they don't know where they've jumped to, and keyboard navigation doesn't continue from that point. The jump appears to do nothing for keyboard users, breaking the expected behavior and making in-page navigation inaccessible.",
            "who_it_affects": "Keyboard-only users who cannot determine where in-page links navigated to, screen reader users who need focus to move to the destination for proper announcement, users with motor disabilities using keyboard navigation, users with cognitive disabilities who need clear feedback about navigation actions, and speech input users who rely on programmatic focus",
            "how_to_fix": "Add tabindex=\"-1\" to the target element of in-page anchor links. For example, if you have <a href=\"#section2\">Jump to Section 2</a>, ensure the target has <div id=\"section2\" tabindex=\"-1\">. The tabindex=\"-1\" makes the element programmatically focusable without adding it to the normal tab order, allowing the browser to move focus there when the link is activated. Already-interactive elements (a, button, input, select, textarea) don't need this as they're naturally focusable."
        },
        "WarnColorOnlyLink": {
            "id": "WarnColorOnlyLink",
            "type": "Warning",
            "impact": "High",
            "wcag": ["1.4.1"],
            "wcag_full": "1.4.1 Use of Color (Level A)",
            "category": "links",
            "description": "Link in flowing text is distinguished from surrounding text only by color, without underline, border, or other non-color visual indicator",
            "why_it_matters": "WCAG 1.4.1 requires that color is not the only visual means of conveying information or distinguishing elements. Links that rely solely on color cannot be perceived by users with color blindness (affecting ~8% of men and ~0.5% of women), users viewing in monochrome, users with low vision, or users who have customized their color schemes. Without additional visual indicators like underlines or borders, these users cannot identify which text is clickable. Note: This applies to links within flowing text (paragraphs), not navigation menus where context makes link purpose clear.",
            "who_it_affects": "Users with color blindness (protanopia, deuteranopia, tritanopia) who cannot distinguish color differences, users with low vision using high contrast modes that override colors, users with monochrome displays, users who have customized system colors for readability, users viewing in bright sunlight where color distinction is reduced, and users with cognitive disabilities who benefit from multiple visual cues",
            "how_to_fix": "Add a non-color visual indicator to links in flowing text. Best practice: keep the default underline (text-decoration: underline). Alternatives include: adding a border (border-bottom: 2px solid), adding an outline, using icons before/after the link, or ensuring sufficient font-weight difference. Note: font-weight, bold, and text-shadow alone are considered weak indicators and will generate a separate warning - prefer underline or border for clarity."
        },
        "WarnColorOnlyLinkWeakIndicator": {
            "id": "WarnColorOnlyLinkWeakIndicator",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["1.4.1"],
            "wcag_full": "1.4.1 Use of Color (Level A)",
            "category": "links",
            "description": "Link in flowing text uses only subtle visual indicators (font-weight, bold, or text-shadow) in addition to color - these can be difficult for users to recognize as links",
            "why_it_matters": "While font-weight changes, bold text, or text-shadows technically satisfy the 'non-color indicator' requirement, they are often too subtle for users to recognize as link indicators, especially in flowing text. Users with low vision may not notice these subtle differences, and many users simply don't associate bold text or shadows with clickability. Underlines and borders are universally recognized as link indicators, while font-weight and shadows require users to scan and compare text weights across the page.",
            "who_it_affects": "Users with low vision who may not perceive subtle font-weight differences, users with cognitive disabilities who rely on familiar link conventions, novice computer users who expect traditional underlines, users scanning pages quickly who miss subtle indicators, and older users familiar with standard web conventions",
            "how_to_fix": "Use stronger visual indicators that are universally recognized: add underline (text-decoration: underline), add border-bottom (border-bottom: 2px solid), or use a combination of indicators. If design constraints require removing underlines, consider adding them on hover/focus at minimum, or use a prominent border style. Font-weight changes should be supplementary to, not replacements for, underlines or borders."
        },
        "WarnLinkLooksLikeButton": {
            "id": "WarnLinkLooksLikeButton",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.3.1"],
            "wcag_full": "1.3.1 Info and Relationships",
            "category": "links",
            "description": "Link is styled to look like a button but uses anchor element",
            "why_it_matters": "Links and buttons have different behaviors - links navigate to new locations while buttons trigger actions. When links look like buttons, users may have incorrect expectations about what will happen. Keyboard users expect Space key to activate buttons but it doesn't work on links.",
            "who_it_affects": "Keyboard users who expect button behavior, screen reader users who hear it announced as a link but see it as a button, and users with cognitive disabilities who rely on consistent interactions",
            "how_to_fix": "If the element performs an action (submit form, open dialog), use a button element. If it navigates to a new URL, keep it as a link but consider whether button styling is appropriate. Ensure keyboard behavior matches the element type."
        },
        "ErrLinkButtonMissingSpaceHandler": {
            "id": "ErrLinkButtonMissingSpaceHandler",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.1.1", "4.1.2"],
            "wcag_full": "2.1.1 Keyboard (Level A), 4.1.2 Name, Role, Value (Level A)",
            "category": "links",
            "description": "Link is styled to look like a button but lacks Space key handler - keyboard users expect Space key to activate button-like elements",
            "why_it_matters": "When a link is visually styled to look like a button, users expect button keyboard behavior. Buttons are activated by both Enter AND Space keys, while links only respond to Enter. Keyboard users who see a button-styled element will naturally press Space to activate it, but on links this will scroll the page instead - a confusing and broken experience. This violates WCAG 2.1.1 (Keyboard) because the expected keyboard functionality doesn't work, and WCAG 4.1.2 (Name, Role, Value) because the visual presentation (button) conflicts with the programmatic role (link). Users with motor disabilities who rely on keyboard navigation are particularly impacted as they cannot efficiently activate these elements.",
            "who_it_affects": "Keyboard-only users who cannot activate button-styled links with Space key, users with motor disabilities using keyboard navigation, users with cognitive disabilities who rely on consistent interaction patterns, speech input users who say 'press space' expecting button behavior, and screen reader users who expect Space key to work on button-looking elements",
            "how_to_fix": "Best solution: Use semantic HTML - if it performs an action, use <button>; if it navigates, use <a> with link styling. If you must style a link as a button, add a keydown event handler that listens for Space key (keyCode 32 or key ' ') and prevents default scroll behavior while triggering the link's action: element.addEventListener('keydown', (e) => { if (e.key === ' ' || e.keyCode === 32) { e.preventDefault(); element.click(); } }). However, this is a workaround - proper semantic HTML is always preferred."
        },
        "ErrLinkFocusContrastFail": {
            "id": "ErrLinkFocusContrastFail",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "links",
            "description": "Link focus indicator (outline, border, or underline) has contrast ratio < 3:1 against the background",
            "why_it_matters": "WCAG 1.4.11 requires all UI components, including focus indicators, to have at least 3:1 contrast ratio against adjacent colors. Low contrast focus indicators are invisible to users with low vision, color vision deficiencies, or anyone viewing the page in bright lighting conditions. A focus indicator that cannot be seen provides no benefit - it fails its entire purpose of showing where keyboard focus is located. This is particularly critical for links, as users need to clearly see which link they're about to activate.",
            "who_it_affects": "Users with low vision, users with color vision deficiencies (8% of males, 0.5% of females), older users with reduced contrast sensitivity, users viewing screens in bright lighting, and users on low-quality displays",
            "how_to_fix": "Choose a focus indicator color that has at least 3:1 contrast ratio against the link's background. Use a contrast checker tool to verify. For light backgrounds, use dark colors (e.g., #0066cc, #000000). For dark backgrounds, use light colors (e.g., #ffffff, #66b3ff). If the background color varies, choose an indicator color that works in all contexts, or use a high-contrast color like black or white with guaranteed visibility."
        },
        "ErrLinkOutlineWidthInsufficient": {
            "id": "ErrLinkOutlineWidthInsufficient",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "2.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 2.4.11 Focus Appearance (Level AAA)",
            "category": "links",
            "description": "Link focus outline width is less than 2px",
            "why_it_matters": "WCAG 2.4.11 (Level AAA) requires focus indicators to be at least 2 CSS pixels thick to ensure adequate visibility. Thin outlines (1px or less) are difficult to see, especially on high-DPI displays, for users with low vision, or in bright lighting conditions. While 2.4.11 is Level AAA, the principle applies to Level AA conformance under 2.4.7 - the focus must be visible enough to be useful. A 1px outline may technically be 'visible' but practically invisible to many users.",
            "who_it_affects": "Users with low vision, older users with reduced visual acuity, users viewing on high-resolution displays where 1px is very small, users viewing in bright lighting, and users with attention deficits who need clear visual cues",
            "how_to_fix": "Set outline-width to at least 2px (outline: 2px solid #color). For even better visibility, consider 3px. The outline should be thick enough to be easily spotted in peripheral vision when tabbing through the page. If using em or rem units, ensure they resolve to at least 2px (e.g., 0.125em when font-size is 16px). Test on various devices including high-DPI displays."
        },
        "ErrLinkImageNoFocusIndicator": {
            "id": "ErrLinkImageNoFocusIndicator",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "links",
            "description": "Image link has no visible focus indicator (no outline, border, or box-shadow)",
            "why_it_matters": "Image links cannot use underline as a focus indicator since there is no text to underline. They must use a structural indicator like outline, border, or box-shadow. Without any of these, keyboard users cannot tell when an image link has focus, making it impossible to navigate effectively. This is especially problematic for icon links, logo links, and thumbnail galleries where multiple images are interactive. Users cannot determine which image they're about to click without a visible focus indicator.",
            "who_it_affects": "Keyboard-only users, switch device users, screen magnifier users tracking focus, users with motor disabilities, and users with cognitive disabilities who need clear visual feedback",
            "how_to_fix": "Add an outline, border, or box-shadow to image links on :focus. Recommended: outline: 2px solid #color with outline-offset: 2px to create clear separation from the image. Alternatively, use border: 2px solid #color or box-shadow: 0 0 0 2px #color. Ensure the indicator color has at least 3:1 contrast against both the image and the page background. Test with actual images to verify the indicator is clearly visible."
        },
        "ErrLinkColorChangeOnly": {
            "id": "ErrLinkColorChangeOnly",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7", "1.4.1"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.1 Use of Color (Level A)",
            "category": "links",
            "description": "Link focus indicator relies solely on color change without outline, border, box-shadow, or underline",
            "why_it_matters": "WCAG 1.4.1 Use of Color (Level A) explicitly prohibits using color as the only visual means of conveying information. When a link's focus state changes only the text color or background color without adding a structural indicator (outline, border, box-shadow, underline), users with color blindness cannot perceive the focus. Approximately 8% of males and 0.5% of females have some form of color vision deficiency. Additionally, users on monochrome displays, users with reduced color contrast settings, or users viewing in bright sunlight may not perceive subtle color changes. Color alone is never sufficient.",
            "who_it_affects": "Users with color blindness (protanopia, deuteranopia, tritanopia), users on monochrome displays, users with custom color schemes for medical reasons, users in bright lighting conditions, and users with older or low-quality displays",
            "how_to_fix": "Add a structural indicator in addition to any color change. For text links: add underline (text-decoration: underline) or outline (outline: 2px solid #color; outline-offset: 2px). For image links: add outline, border, or box-shadow. You can keep the color change for additional reinforcement, but it must not be the only indicator. Test by viewing the page in grayscale mode to verify focus is still visible without color."
        },
        "WarnLinkOutlineOffsetTooLarge": {
            "id": "WarnLinkOutlineOffsetTooLarge",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "links",
            "description": "Link has both underline and outline with outline-offset > 1px, creating confusing visual gap",
            "why_it_matters": "When a link has an underline (either as default link styling or added on :focus) and also has an outline with large offset (> 1px), there is a visible gap between the underlined text and the outline. This creates visual confusion - users see two separate indicators with empty space between them, making it unclear which element actually has focus. The gap is particularly confusing for users with cognitive disabilities, attention deficits, or those using screen magnification who may only see part of the indicator. For text links with underline, the outline should be close to the text (0-1px offset) to create a cohesive visual unit.",
            "who_it_affects": "Screen magnifier users who may only see part of the indicator, users with cognitive disabilities who are confused by disconnected visual elements, users with attention deficits, and users with low vision tracking focus location",
            "how_to_fix": "When using both underline and outline on text links, set outline-offset to 0px or 1px to keep the outline close to the underlined text. Alternatively, choose one indicator: either use underline alone (sufficient for text links) or use outline alone (remove the underline). If you need visual separation, keep outline-offset ≤ 1px for text links with underline. Test by tabbing through links to verify the focus indicator appears as a single cohesive visual unit."
        },
        "WarnLinkDefaultFocus": {
            "id": "WarnLinkDefaultFocus",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible",
            "category": "links",
            "description": "Link uses browser default focus styles which vary across browsers and may fail contrast requirements",
            "why_it_matters": "Browser default focus indicators vary significantly: Chrome uses a thin blue outline, Firefox uses a dotted outline, Safari uses a blue glow. These defaults may not meet 3:1 contrast requirements on all backgrounds, especially on blue backgrounds where blue outlines disappear. Relying on browser defaults creates an inconsistent user experience and may fail accessibility requirements in some browsers. The default styles were designed for general use, not optimized for your specific color scheme, and often appear too thin or too light. Defining explicit focus styles ensures consistent, accessible focus indication across all browsers.",
            "who_it_affects": "Users on different browsers see different focus indicators, users with low vision may find default indicators too subtle, users on certain backgrounds (especially blue) where default blue outlines are invisible",
            "how_to_fix": "Define explicit :focus styles for all links. For text links: a:focus { outline: 2px solid #0066cc; outline-offset: 2px; } or a:focus { text-decoration: underline; }. For image links: a:focus img { outline: 2px solid #0066cc; outline-offset: 2px; }. Choose colors that have 3:1 contrast against your specific backgrounds. Test in multiple browsers to ensure consistency. Consider using :focus-visible to show focus only for keyboard users."
        },
        "WarnLinkFocusGradientBackground": {
            "id": "WarnLinkFocusGradientBackground",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "links",
            "description": "Link has gradient background - focus indicator contrast cannot be automatically verified and requires manual testing",
            "why_it_matters": "When a link has a gradient background (linear-gradient, radial-gradient, conic-gradient), the background color varies across the link. An outline or border that has sufficient 3:1 contrast against the lightest part of the gradient may fail contrast requirements against the darkest part (or vice versa). Automated tools cannot reliably calculate contrast against gradients because the contrast ratio varies by position. The focus indicator might be clearly visible at the top of the link but invisible at the bottom. This requires manual verification by checking contrast at multiple points across the gradient, particularly at the lightest and darkest stops.",
            "who_it_affects": "Users with low vision who cannot see low-contrast portions of the focus indicator, users with color vision deficiencies where partial visibility is problematic, users viewing in bright lighting conditions",
            "how_to_fix": "Manually verify focus indicator contrast against ALL parts of the gradient, especially the lightest and darkest colors. Use a contrast checker to test the indicator color against: (1) the lightest gradient stop color, (2) the darkest gradient stop color, and (3) any mid-tones. Ensure 3:1 contrast at all points. Better solution: avoid gradient backgrounds on focusable links, or choose an indicator color (like pure black or pure white) that has guaranteed high contrast against all gradient stops. Consider using a solid background for links to simplify accessibility."
        },
        "WarnLinkTransparentOutline": {
            "id": "WarnLinkTransparentOutline",
            "type": "Warning",
            "impact": "Medium",
            "wcag": ["2.4.7", "1.4.11"],
            "wcag_full": "2.4.7 Focus Visible, 1.4.11 Non-text Contrast",
            "category": "links",
            "description": "Link focus outline or border uses semi-transparent color (alpha < 0.5) which cannot guarantee sufficient contrast",
            "why_it_matters": "Semi-transparent outlines/borders blend with the background, making it impossible to guarantee they meet 3:1 contrast in all contexts. The effective color and contrast ratio change based on the background color beneath the transparent outline. An outline with rgba(0,102,204,0.3) appears differently on white vs gray vs black backgrounds. As the page scrolls, animations run, or overlays appear, the background beneath the link may change, causing the focus indicator to become invisible at certain times. WCAG requires consistent accessibility - an indicator that works sometimes but fails other times is not reliable. For alpha values < 0.5, the outline is so transparent it essentially disappears on many backgrounds.",
            "who_it_affects": "Users with low vision who cannot perceive subtle transparent indicators, users viewing in bright lighting, users with color vision deficiencies, screen magnifier users who may see the indicator against unexpected backgrounds",
            "how_to_fix": "Use fully opaque colors for focus outlines/borders (alpha = 1.0). If subtle styling is desired, choose a lighter or darker shade of a fully opaque color. For example, instead of rgba(0,102,204,0.3), use a lighter opaque blue like #66b3ff. Calculate and verify contrast against all possible backgrounds. If you must use transparency for design reasons, ensure alpha ≥ 0.5 and manually test against all backgrounds in all states (scrolled, hovered, overlaid)."
        },
        "DiscoPDFLinksFound": {
            "id": "DiscoPDFLinksFound",
            "type": "Discovery",
            "impact": "N/A",
            "wcag": ["1.1.1", "1.3.1", "2.1.1", "2.4.1"],
            "wcag_full": "1.1.1, 1.3.1, 2.1.1, 2.4.1",
            "category": "pdf",
            "description": "Links to PDF documents detected on page",
            "why_it_matters": "PDF documents often have accessibility issues and may not be accessible to all users",
            "who_it_affects": "Screen reader users, users with disabilities who have difficulty with PDF formats",
            "how_to_fix": "Ensure PDFs are accessible (tagged, structured, with text content) or provide HTML alternatives"
        },
        "ErrDocumentLinkMissingFileType": {
            "id": "ErrDocumentLinkMissingFileType",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.4"],
            "wcag_full": "2.4.4 Link Purpose (In Context) (Level A)",
            "category": "links",
            "description": "Link to downloadable document (PDF, Word, Excel, PowerPoint, etc.) does not indicate the file type in its accessible name",
            "why_it_matters": "Users need to know they're about to download a file and what type of file it is before activating the link. Without file type indication, users may experience unexpected downloads, particularly problematic for mobile users with limited data plans or users on screen readers who cannot see file icons. Knowing the file type helps users decide if they have appropriate software to open it, if they want to download it on their current device, and how much bandwidth it will consume. This is especially critical for users who cannot easily perceive visual file type indicators like icons or extensions.",
            "who_it_affects": "Screen reader users who cannot see file type icons, mobile users who need to manage downloads and data usage, users with cognitive disabilities who benefit from explicit warnings about downloads, users on metered connections who need to know file sizes, users without appropriate software who need to know file types before downloading, and users with slow connections who cannot afford unexpected large downloads",
            "how_to_fix": "Include the file type in the link text (e.g., \"Annual Report (PDF)\" or \"Budget Spreadsheet (Excel)\"), or use aria-label to provide this information (e.g., aria-label=\"Annual Report PDF document\"). The file type should be part of the accessible name that screen readers announce. Common patterns: \"Download [Document Name] ([FILE TYPE])\" or \"[Document Name] - [FILE TYPE] format\". Ensure the file type is announced to screen readers, not just shown visually as an icon or file extension in the URL."
        },
        "ErrDocumentLinkWrongLanguage": {
            "id": "ErrDocumentLinkWrongLanguage",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["3.1.2"],
            "wcag_full": "3.1.2 Language of Parts (Level AA)",
            "category": "links",
            "description": "Link to a downloadable document in a different language than the page language lacks lang attribute or language indication",
            "why_it_matters": "When a page links to a document in a different language, screen reader users need advance warning so they can switch to the appropriate voice or pronunciation engine. Without language indication, screen readers attempt to read foreign language content with the wrong pronunciation rules, making documents unintelligible. Users with cognitive disabilities benefit from knowing a document is in a different language before opening it, allowing them to prepare translation tools or decide not to access content they cannot understand. This also helps all users make informed decisions about whether to download documents they may not be able to read.",
            "who_it_affects": "Screen reader users who need to switch voice engines for different languages, multilingual users who need to know which language a document is in, users with cognitive disabilities who need preparation for language changes, users who rely on automatic translation tools, users with limited language proficiency who need advance warning, and international users navigating multilingual websites",
            "how_to_fix": "Add a lang attribute to links pointing to documents in different languages (e.g., <a href=\"report.pdf\" lang=\"fr\">Rapport Annuel</a> on an English page). Alternatively or additionally, indicate the language in the link text (e.g., \"Annual Report (PDF, French)\" or \"Rapport Annuel (PDF, en français)\"). For hreflang, use it for alternate language versions of the same content. The lang attribute ensures screen readers use correct pronunciation. Always include both visual and programmatic language indication for maximum accessibility."
        },
        "WarnMissingDocumentMetadata": {
            "id": "WarnMissingDocumentMetadata",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.4"],
            "wcag_full": "2.4.4 Link Purpose (In Context) (Level A)",
            "category": "links",
            "description": "Link to downloadable document does not provide additional metadata such as file size or page count",
            "why_it_matters": "Beyond file type, users benefit from knowing file size (e.g., \"3.2 MB\") to make informed decisions about downloading, especially on mobile devices or metered connections. Page count or document length helps users understand time commitment. This metadata helps users avoid downloading unexpectedly large files, plan for download times, and determine if they have sufficient storage space.",
            "who_it_affects": "Mobile users on limited data plans, users with slow internet connections, users with limited device storage, users with cognitive disabilities who benefit from clear expectations, and users who need to plan time for reviewing documents",
            "how_to_fix": "Include file size and optionally page count or document length in the link text or nearby (e.g., \"Annual Report (PDF, 3.2 MB, 48 pages)\"). This can be in the link text itself, in aria-describedby content, or in immediately adjacent text. Ensure this metadata is accessible to screen readers."
        },
        "ErrMissingDocumentType": {
            "id": "ErrMissingDocumentType",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["4.1.1"],
            "wcag_full": "4.1.1 Parsing (Level A)",
            "category": "page",
            "description": "HTML document is missing the DOCTYPE declaration (<!DOCTYPE html>) at the beginning of the file",
            "why_it_matters": "The DOCTYPE declaration tells browsers how to parse and render the page. Without it, browsers render in \"quirks mode\" which uses outdated parsing rules for backward compatibility with 1990s websites. Quirks mode causes unpredictable rendering behavior, CSS inconsistencies, JavaScript issues, and can break assistive technology compatibility. Modern assistive technologies expect standards-compliant HTML parsing. Missing DOCTYPE violates WCAG 4.1.1 Parsing which requires properly formed HTML. Quirks mode may cause form controls, focus indicators, ARIA attributes, and other accessibility features to behave incorrectly.",
            "who_it_affects": "All users due to unpredictable rendering behavior, assistive technology users whose tools may not parse the page correctly, screen reader users who may experience navigation issues, keyboard users whose focus indicators may not display correctly, and users with cognitive disabilities who are confused by inconsistent behavior across browsers",
            "how_to_fix": "Add <!DOCTYPE html> as the very first line of every HTML document, before the <html> tag. This is the HTML5 DOCTYPE and works for all modern HTML. Never omit this declaration. Ensure there are no characters (including spaces or byte-order marks) before the DOCTYPE. The declaration is case-insensitive but <!DOCTYPE html> is standard. Example: <!DOCTYPE html>\\n<html lang=\"en\">\\n<head>..."
        },
        "ErrNoPageTitle": {
            "id": "ErrNoPageTitle",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.2"],
            "wcag_full": "2.4.2 Page Titled",
            "category": "page",
            "description": "Page has no <title> element in the document head",
            "why_it_matters": "The page title is the first thing screen reader users hear when a page loads, and it appears in browser tabs, bookmarks, and search results. Without a title, users cannot identify the page in their browser history, distinguish between multiple open tabs, or understand what page they're on when arriving from a link. Screen reader users announcing \"Untitled document\" have no context about where they are. This is like opening a book with no title on the cover or spine - you don't know what you're reading until you dive into the content. The title is critical for orientation and navigation.",
            "who_it_affects": "Screen reader users who rely on titles for page identification and orientation, users with cognitive disabilities who need clear page identification, users managing multiple browser tabs who need to distinguish between pages, users with memory issues using browser history to return to pages, and all users when bookmarking or sharing pages",
            "how_to_fix": "Add a <title> element within the <head> section of your HTML. Create descriptive, unique titles that identify both the page content and the site. Use a consistent pattern like \"Page Topic - Site Name\". Put the unique page information first since it's most important. Keep titles concise (under 60 characters) but descriptive. Avoid generic titles like \"Home\" or \"Page 1\". The title should make sense when read out of context in a list of bookmarks or search results."
        },
        "ErrEmptyPageTitle": {
            "id": "ErrEmptyPageTitle",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.2"],
            "wcag_full": "2.4.2",
            "category": "page",
            "description": "Page title element is empty",
            "why_it_matters": "Empty titles provide no information about page content",
            "who_it_affects": "Screen reader users, users with cognitive disabilities",
            "how_to_fix": "Add descriptive text to title element"
        },
        "ErrMultiplePageTitles": {
            "id": "ErrMultiplePageTitles",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.2"],
            "wcag_full": "2.4.2 Page Titled (A)",
            "category": "page",
            "description": "Multiple title elements found in document head causing unpredictable behavior",
            "why_it_matters": "Browsers and assistive technologies choose unpredictably between multiple titles, creating inconsistent experience",
            "who_it_affects": "All users, screen reader users, search engine users",
            "how_to_fix": "Remove all but one title element from document head"
        },
        "ErrStyleAttrColorFont": {
            "id": "ErrStyleAttrColorFont",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.3", "1.4.8", "1.4.12"],
            "wcag_full": "1.4.3 Contrast (Minimum) (Level AA), 1.4.8 Visual Presentation (Level AAA), 1.4.12 Text Spacing (Level AA)",
            "category": "styles",
            "description": "Inline style attributes define color or font properties directly on HTML elements, overriding user stylesheets and preventing users from customizing visual presentation",
            "why_it_matters": "When colors and fonts are hard-coded in inline style attributes, CSS specificity rules make them extremely difficult for users to override with their own stylesheets. Users with low vision who need specific color schemes (high contrast, inverted colors, custom color combinations), users with dyslexia who need particular fonts, and users who need custom text spacing cannot apply their accessibility preferences. Inline styles essentially lock visual presentation, forcing all users to view content exactly as designed regardless of their needs.",
            "who_it_affects": "Users with low vision who require custom color schemes or high contrast settings, users with dyslexia or reading disabilities who need specific fonts like OpenDyslexic or Comic Sans, users with light sensitivity who need dark mode or specific color combinations, users with cognitive disabilities who need customized text presentation, elderly users who need larger text with specific spacing, and users with color blindness who need adjusted color palettes",
            "how_to_fix": "Move all color and font declarations from inline style attributes to external CSS files or <style> blocks with lower specificity, use CSS classes instead of inline styles (replace style=\"color: red; font-size: 18px;\" with class=\"error-text\"), ensure user stylesheets can override your styles by avoiding !important declarations, test that users can apply custom stylesheets successfully, and reserve inline styles only for layout properties like positioning or dimensions when absolutely necessary"
        },
        "WarnStyleAttrOther": {
            "id": "WarnStyleAttrOther",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.4.8"],
            "wcag_full": "1.4.8 Visual Presentation (Level AAA)",
            "category": "styles",
            "description": "Inline style attributes define layout properties (margin, padding, width, display) directly on HTML elements instead of using CSS classes",
            "why_it_matters": "While layout-related inline styles are less problematic for accessibility than color/font styles, they still reduce maintainability, make responsive design harder to implement, and can interfere with user zoom and customization. Inline layout styles scatter presentation logic throughout HTML making it difficult to create consistent designs or implement site-wide changes. They also make it harder for users with custom stylesheets to adjust spacing or layout for their needs.",
            "who_it_affects": "Users who need custom stylesheets to adjust layout for readability, users who zoom content and need flexible layouts that adapt properly, developers maintaining the codebase who cannot easily update or debug scattered inline styles, and users with cognitive disabilities who benefit from consistent, predictable layouts",
            "how_to_fix": "Move layout properties to CSS classes or external stylesheets for better maintainability (replace style=\"margin: 20px; padding: 10px;\" with appropriate CSS classes), use semantic HTML with CSS for layout rather than inline positioning, create reusable utility classes for common spacing patterns, ensure responsive design works properly without inline dimension declarations, and document any truly necessary inline layout styles with comments explaining why they cannot be moved to stylesheets"
        },
        "ErrStyleTagColorFont": {
            "id": "ErrStyleTagColorFont",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.3", "1.4.8", "1.4.12"],
            "wcag_full": "1.4.3 Contrast (Minimum) (Level AA), 1.4.8 Visual Presentation (Level AAA), 1.4.12 Text Spacing (Level AA)",
            "category": "styles",
            "description": "Style tags in HTML document define color or font properties, making it harder for users to override with custom stylesheets due to specificity and source order",
            "why_it_matters": "Embedded <style> tags create specificity and cascade issues that can prevent users from successfully applying their own stylesheets for accessibility needs. Colors and fonts defined in <style> tags appear later in the cascade than external stylesheets, often requiring users to add !important to every custom rule or fight complex specificity battles. This creates significant barriers for users who depend on custom styling - those with low vision needing high contrast, users with dyslexia needing specific fonts, or users with light sensitivity needing dark themes. External CSS files load first and are easier to override with user stylesheets.",
            "who_it_affects": "Users with low vision who need custom color schemes that may be overridden by embedded styles, users with dyslexia or reading disabilities who cannot reliably apply their preferred fonts, users with photosensitivity who need consistent dark mode implementations, users with cognitive disabilities requiring specific visual customizations, and users relying on browser extensions or assistive technology that inject custom CSS which may be defeated by embedded styles",
            "how_to_fix": "Move all color and font definitions from <style> tags to external CSS files that load early in the document head, use external stylesheets with link elements instead of embedded styles (replace <style> with <link rel=\"stylesheet\" href=\"styles.css\">), ensure external stylesheets are loaded before any embedded styles if you must use both, avoid using overly specific selectors or !important that make user overrides difficult, test that user stylesheets successfully override your color and font choices, and reserve <style> tags for critical layout CSS only when external files would cause flash of unstyled content"
        },
        "WarnStyleTagOther": {
            "id": "WarnStyleTagOther",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["1.4.8"],
            "wcag_full": "1.4.8 Visual Presentation (Level AAA)",
            "category": "styles",
            "description": "Style tags in HTML document define layout properties, which should preferably be in external CSS files for better maintainability and performance",
            "why_it_matters": "While layout CSS in <style> tags is less problematic than inline styles, using external CSS files provides better caching, allows CSS to be shared across pages, makes maintenance easier, enables better testing, and improves page load performance. Embedded <style> blocks increase HTML file size, prevent browser caching of styles, make it harder to implement site-wide design changes, and can create flash of unstyled content issues. External CSS also makes it easier to implement responsive design and media queries consistently.",
            "who_it_affects": "All users benefit from faster page loads through CSS caching, users on slow connections who download unnecessary CSS with every page, users who zoom or need responsive layouts that should be managed centrally, developers maintaining scattered style blocks across multiple pages, and users whose custom stylesheets work more predictably when site styles are in external files",
            "how_to_fix": "Move layout CSS from <style> tags to external CSS files loaded via <link> elements, combine styles from multiple pages into shared stylesheets to improve caching, use CSS modules or build tools to manage styles systematically, keep <style> tags only for critical above-the-fold CSS if optimizing initial paint time, document any remaining embedded styles with comments explaining why external CSS isn't suitable, and ensure responsive design and media queries are managed in external files where they can be easily updated"
        },

        # ============================================================================
        # Tabindex Interactive Element Focus Indicators
        # ============================================================================
        "ErrTabindexNoVisibleFocus": {
            "id": "ErrTabindexNoVisibleFocus",
            "title": "Element with tabindex has no visible focus indicator",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Non-interactive element made focusable with tabindex attribute lacks a visible focus indicator",
            "why_it_matters": "When elements are made keyboard-focusable using tabindex, keyboard users must be able to see where focus is located. Without a visible focus indicator, keyboard-only users cannot determine which element has focus, making navigation impossible. This is especially critical for elements that aren't natively interactive, as users won't expect them to be focusable.",
            "who_it_affects": "Keyboard-only users who cannot use a mouse, users with motor disabilities who rely on keyboard navigation, screen magnifier users who need to see focus location, users with attention disorders who track focus visually, and users navigating with assistive technologies that follow keyboard focus",
            "how_to_fix": "Add a :focus style with a visible indicator such as outline (e.g., 'outline: 2px solid #0066cc'), box-shadow (e.g., 'box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.5)'), or border change. Ensure the indicator has at least 3:1 contrast ratio with adjacent colors. For elements with tabindex, treat them like buttons and provide clear visual feedback when focused."
        },
        "ErrTabindexChildOfInteractive": {
            "id": "ErrTabindexChildOfInteractive",
            "title": "Focusable child element inside interactive parent",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Child element has tabindex making it focusable when it is already inside an interactive parent element (button, link, etc.)",
            "why_it_matters": "When a child element (like an SVG or span) inside an interactive parent (like a button) has its own tabindex, it creates a redundant tab stop and relies on the parent's focus indicator. Screen magnifier users at high zoom levels may only see the child element without its parent context. If the child element lacks its own visible focus indicator, these users cannot determine when the element has focus. Even if the parent button changes color on focus, magnified users viewing only the SVG won't see this change. The child element needs either its own focus indicator or should not be independently focusable.",
            "who_it_affects": "Screen magnifier users at 200%+ zoom who may only see the child element, users with tunnel vision or reduced peripheral vision, keyboard-only users who get confused by redundant tab stops, users with cognitive disabilities who may be confused by nested focusable elements, and users relying on focus indicators to track their position",
            "how_to_fix": "Remove the tabindex attribute from the child element - the parent interactive element already provides keyboard access. If the child must be independently focusable (rare), add a distinct visible focus indicator directly to the child element using outline or box-shadow that is visible even when viewing only that element in isolation. In most cases, removing tabindex from children of buttons, links, and other interactive elements is the correct solution."
        },
        "ErrTabindexFocusContrastFail": {
            "id": "ErrTabindexFocusContrastFail",
            "title": "Focus indicator on tabindex element has insufficient contrast",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.11", "2.4.7"],
            "wcag_full": "1.4.11 Non-text Contrast (Level AA), 2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Focus indicator on element with tabindex has less than 3:1 contrast ratio with adjacent colors",
            "why_it_matters": "Low contrast focus indicators are difficult or impossible to see for users with low vision, color blindness, or in bright lighting conditions. A 3:1 contrast ratio is the minimum required by WCAG 2.1 for non-text elements including focus indicators. Users with mild vision impairments, older users, and users in sub-optimal viewing conditions rely on adequate contrast to see where keyboard focus is located.",
            "who_it_affects": "Users with low vision who cannot perceive low-contrast indicators, users with color blindness who may not distinguish certain color combinations, older users experiencing age-related vision decline, users viewing screens in bright sunlight or poor lighting, and keyboard users who need to track focus visually",
            "how_to_fix": "Increase the contrast of the focus indicator to at least 3:1 against adjacent colors. Use tools like the WebAIM Contrast Checker to verify contrast ratios. Consider using high-contrast colors like dark blue (#0066cc) on white backgrounds. Ensure the focus indicator color contrasts with both the element background and surrounding content. Test with multiple background colors if the element appears in different contexts."
        },
        "ErrTabindexOutlineNoneNoBoxShadow": {
            "id": "ErrTabindexOutlineNoneNoBoxShadow",
            "title": "Tabindex element sets outline:none without alternative indicator",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with tabindex removes default outline with 'outline:none' but provides no alternative focus indicator",
            "why_it_matters": "Removing the browser's default focus outline without providing an alternative completely eliminates the focus indicator, making keyboard navigation impossible. This is a critical accessibility failure that prevents keyboard users from knowing where they are on the page. The default outline exists specifically to provide keyboard accessibility - removing it requires providing an equally visible alternative.",
            "who_it_affects": "All keyboard-only users who cannot navigate without visible focus, users with motor disabilities using alternative input devices, screen magnifier users tracking focus location, users with attention disorders following focus visually, and assistive technology users whose tools follow keyboard focus",
            "how_to_fix": "If outline:none is used, always provide an alternative focus indicator using box-shadow, border changes, or background color changes. For example: 'button:focus { outline: none; box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.5); }'. Better yet, keep the outline and enhance it: 'button:focus { outline: 2px solid #0066cc; outline-offset: 2px; }'. Never remove focus indicators without replacement."
        },
        "ErrTabindexSingleSideBoxShadow": {
            "id": "ErrTabindexSingleSideBoxShadow",
            "title": "Tabindex element uses single-sided box-shadow for focus",
            "type": "Error",
            "impact": "High",
            "wcag": ["CR 5.2.4"],
            "wcag_full": "WCAG 2.2 Conformance Requirement 5.2.4 - Focus Appearance (Minimum)",
            "category": "event_handling",
            "description": "Element with tabindex uses box-shadow on only one side (top, right, bottom, or left) for focus indicator",
            "why_it_matters": "Single-sided focus indicators violate WCAG 2.2's Conformance Requirement 5.2.4 which requires focus indicators to have sufficient area. A focus indicator appearing on only one edge may not meet the minimum 2 CSS pixel area requirement relative to the element's perimeter. Users may miss single-sided indicators, especially when scanning quickly or when the indicator side is outside their field of view in screen magnifiers.",
            "who_it_affects": "Screen magnifier users who may not see the indicator side when zoomed in, users with tunnel vision or reduced peripheral vision, users scanning pages quickly who miss partial indicators, keyboard users who need obvious focus cues, and users with attention disorders who benefit from complete visual boundaries",
            "how_to_fix": "Use box-shadow that appears on all sides: 'box-shadow: 0 0 0 3px #0066cc' (uniform around element) instead of offset shadows like 'box-shadow: 3px 0 0 #0066cc' (single side). Alternatively, use outline which automatically appears on all sides. If design requires directional emphasis, combine it with a full-perimeter indicator."
        },
        "ErrTabindexOutlineWidthInsufficient": {
            "id": "ErrTabindexOutlineWidthInsufficient",
            "title": "Focus outline on tabindex element is thinner than 2 pixels",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.11"],
            "wcag_full": "2.4.11 Focus Appearance (Level AAA)",
            "category": "event_handling",
            "description": "Element with tabindex has a focus outline less than 2 CSS pixels thick",
            "why_it_matters": "WCAG 2.2 Success Criterion 2.4.11 (Level AAA) recommends focus indicators be at least 2 pixels thick to ensure visibility. Thin outlines (1px) can be difficult to see, especially at distance, in bright conditions, or for users with mild vision impairments. While Level AAA is not always required, thicker focus indicators significantly improve usability for a broader range of users with minimal design impact.",
            "who_it_affects": "Users with mild to moderate vision impairments, older users with age-related vision changes, users viewing screens at non-optimal distances or angles, users in bright environments where thin lines are hard to see, and users with attention disorders who benefit from more prominent visual cues",
            "how_to_fix": "Increase outline width to at least 2px: 'outline: 2px solid #0066cc' instead of '1px'. Consider 3px for even better visibility. Use outline-offset to add space between the element and outline for better visibility: 'outline-offset: 2px'. For box-shadow alternatives, use at least 2px spread: 'box-shadow: 0 0 0 2px #0066cc'."
        },
        "ErrTabindexColorChangeOnly": {
            "id": "ErrTabindexColorChangeOnly",
            "title": "Focus on tabindex element relies solely on color change",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.1"],
            "wcag_full": "1.4.1 Use of Color (Level A)",
            "category": "event_handling",
            "description": "Element with tabindex indicates focus only through color change without structural change (outline, border, shape)",
            "why_it_matters": "WCAG 1.4.1 requires that color is not the only visual means of conveying information. Users with color blindness (affecting ~8% of men and 0.5% of women) may not perceive color-only changes. Users with monochrome displays, users who override colors for readability, and users in poor lighting conditions also cannot rely on color alone. Focus indicators must include structural changes like outlines, borders, underlines, or shapes.",
            "who_it_affects": "Users with color blindness (protanopia, deuteranopia, tritanopia), users with low vision using high contrast modes, users with monochrome displays, users who have customized system colors for readability, users in bright sunlight where color distinction is reduced, and users with cognitive disabilities who rely on multiple visual cues",
            "how_to_fix": "Add a structural change in addition to color: use outline ('outline: 2px solid color'), add border ('border: 2px solid color'), add box-shadow ('box-shadow: 0 0 0 3px color'), add underline for text elements, or change shape/size. Ensure the structural change is visible independent of color perception. Test by viewing in grayscale mode."
        },
        "ErrTabindexTransparentOutline": {
            "id": "ErrTabindexTransparentOutline",
            "title": "Focus outline on tabindex element is semi-transparent",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.4.11", "2.4.7"],
            "wcag_full": "1.4.11 Non-text Contrast (Level AA), 2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with tabindex uses semi-transparent (alpha < 0.5) focus outline or box-shadow",
            "why_it_matters": "Semi-transparent focus indicators have reduced visibility and may fail to meet the 3:1 contrast requirement depending on what content appears behind them. Transparency makes contrast unpredictable - an indicator might pass on one background but fail on another. Users with low vision need consistent, high-visibility focus indicators that don't vary based on background content. Fully opaque indicators ensure reliable visibility.",
            "who_it_affects": "Users with low vision who need high-visibility focus indicators, users with color blindness who may not perceive subtle transparent overlays, users in bright viewing conditions where transparency reduces visibility further, screen magnifier users tracking focus location, and keyboard users who depend on obvious focus cues",
            "how_to_fix": "Use fully opaque colors (alpha = 1.0) for focus indicators: 'outline: 2px solid rgb(0, 102, 204)' instead of 'rgba(0, 102, 204, 0.3)'. If transparency is desired for aesthetic reasons, keep it above 0.8 alpha and verify 3:1 contrast on all possible backgrounds. Test with various background colors and images. Consider using solid colors with outline-offset for spacing rather than transparency for softness."
        },
        "WarnTabindexDefaultFocus": {
            "id": "WarnTabindexDefaultFocus",
            "title": "Tabindex element relies on default browser focus styles",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with tabindex has no custom focus styles and relies on browser default focus indicator",
            "why_it_matters": "Default browser focus styles vary significantly across browsers (Chrome: blue outline, Firefox: dotted outline, Safari: blue ring) and may not match your site's design or branding. While technically WCAG compliant, inconsistent focus indicators across browsers can confuse users and appear unprofessional. Custom focus styles ensure consistent user experience and can be optimized for your site's color scheme and contrast requirements.",
            "who_it_affects": "All users benefit from consistent focus indicators across browsers, users who switch between browsers and expect consistent interfaces, users of specific browsers with less visible default focus styles, branding-conscious users who notice inconsistent design, and developers maintaining consistent user experience standards",
            "how_to_fix": "Define custom :focus styles that match your site's design: 'element:focus { outline: 2px solid #your-brand-color; outline-offset: 2px; }'. Ensure custom styles meet 3:1 contrast requirements. Test across all major browsers (Chrome, Firefox, Safari, Edge). Document focus style standards in your design system. Consider using CSS custom properties for focus colors to maintain consistency."
        },
        "WarnTabindexNoBorderOutline": {
            "id": "WarnTabindexNoBorderOutline",
            "title": "Tabindex element uses outline-only focus (screen magnifier concern)",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with tabindex uses only CSS outline for focus with no border or size change",
            "why_it_matters": "Screen magnifier users zoomed to 200-400% may not see CSS outline which appears outside the element boundaries. When magnified, the outline may fall outside the visible viewport while the element itself remains visible. Combining outline with border changes or size changes ensures focus is visible even when the element edges are at the viewport boundary. This is a best practice to improve focus visibility for magnified views.",
            "who_it_affects": "Screen magnifier users zoomed to 200%+ who may have element visible but outline outside viewport, users with low vision using browser zoom at high levels, users with tunnel vision who focus on element center, mobile users in zoomed mode, and users with cognitive disabilities who benefit from multiple focus indicators",
            "how_to_fix": "Combine outline with visible changes inside element boundaries: add border thickness change ('border: 3px solid color' on focus vs 1px normal), add padding adjustment to prevent layout shift, add background color change, or add inner box-shadow ('box-shadow: inset 0 0 0 2px color'). Use outline-offset with positive value to keep outline closer to element. Test with browser zoom at 200%+ to verify visibility."
        },

        # ============================================================================
        # Event Handler Interactive Element Focus Indicators
        # ============================================================================
        "ErrHandlerNoVisibleFocus": {
            "id": "ErrHandlerNoVisibleFocus",
            "title": "Element with event handler has no visible focus indicator",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Non-interactive element with event handler (onclick, etc.) lacks a visible focus indicator",
            "why_it_matters": "When elements have event handlers but no visible focus indicator, keyboard users cannot determine which element has focus or know the element is interactive. This is especially problematic for click handlers on <div> or <span> elements that appear interactive but lack focus indicators. Without visible focus, keyboard navigation becomes impossible and users may not realize the element is clickable.",
            "who_it_affects": "Keyboard-only users who cannot use a mouse, users with motor disabilities relying on keyboard navigation, screen magnifier users tracking focus location, users with attention disorders following focus visually, and assistive technology users whose tools follow keyboard focus",
            "how_to_fix": "Add tabindex='0' to make the element keyboard-focusable, then add :focus styles with visible indicators: outline, box-shadow, or border changes. Better yet, use semantic HTML elements (<button>, <a>) which are natively keyboard-accessible. If using div/span for interactive elements, add role='button' and handle keyboard events (Enter/Space). Ensure focus indicator has 3:1 contrast."
        },
        "ErrHandlerFocusContrastFail": {
            "id": "ErrHandlerFocusContrastFail",
            "title": "Focus indicator on event handler element has insufficient contrast",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.11", "2.4.7"],
            "wcag_full": "1.4.11 Non-text Contrast (Level AA), 2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Focus indicator on element with event handler has less than 3:1 contrast ratio with adjacent colors",
            "why_it_matters": "Low contrast focus indicators are difficult or impossible to see for users with low vision, color blindness, or in bright lighting conditions. For elements made interactive with event handlers, visible focus is even more critical since users may not expect the element to be interactive. A 3:1 contrast ratio is the minimum required by WCAG 2.1 for non-text elements including focus indicators.",
            "who_it_affects": "Users with low vision who cannot perceive low-contrast indicators, users with color blindness who may not distinguish certain color combinations, older users experiencing age-related vision decline, users viewing screens in bright sunlight or poor lighting, and keyboard users who need to track focus visually",
            "how_to_fix": "Increase focus indicator contrast to at least 3:1 against adjacent colors. Use contrast checking tools to verify. Consider high-contrast color combinations like dark blue (#0066cc) on white, or white/yellow on dark backgrounds. Test with various background colors if the element appears in different contexts. Ensure the indicator contrasts with both the element background and surrounding content."
        },
        "ErrHandlerOutlineNoneNoBoxShadow": {
            "id": "ErrHandlerOutlineNoneNoBoxShadow",
            "title": "Event handler element sets outline:none without alternative indicator",
            "type": "Error",
            "impact": "High",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with event handler removes default outline with 'outline:none' but provides no alternative focus indicator",
            "why_it_matters": "Removing the browser's default focus outline without providing an alternative completely eliminates the focus indicator, making keyboard navigation impossible. This is especially problematic for elements made interactive with event handlers, as they may not have had focus indicators originally. Users cannot tell if these elements have focus or are even interactive without a visible indicator.",
            "who_it_affects": "All keyboard-only users who cannot navigate without visible focus, users with motor disabilities using alternative input devices, screen magnifier users tracking focus location, users with attention disorders following focus visually, and assistive technology users whose tools follow keyboard focus",
            "how_to_fix": "Never use outline:none without providing an alternative. Add box-shadow ('box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.5)'), border changes, or background color changes when removing outline. Better yet, keep and enhance the outline: 'outline: 2px solid #0066cc; outline-offset: 2px'. Ensure any alternative indicator is clearly visible and meets contrast requirements."
        },
        "ErrHandlerSingleSideBoxShadow": {
            "id": "ErrHandlerSingleSideBoxShadow",
            "title": "Event handler element uses single-sided box-shadow for focus",
            "type": "Error",
            "impact": "High",
            "wcag": ["CR 5.2.4"],
            "wcag_full": "WCAG 2.2 Conformance Requirement 5.2.4 - Focus Appearance (Minimum)",
            "category": "event_handling",
            "description": "Element with event handler uses box-shadow on only one side for focus indicator",
            "why_it_matters": "Single-sided focus indicators violate WCAG 2.2's Conformance Requirement 5.2.4 which requires focus indicators to have sufficient area. A focus indicator appearing on only one edge may not meet the minimum 2 CSS pixel area requirement. For elements made interactive with event handlers, clear focus indicators are critical since users may not expect them to be focusable.",
            "who_it_affects": "Screen magnifier users who may not see the indicator side when zoomed in, users with tunnel vision or reduced peripheral vision, users scanning pages quickly who miss partial indicators, keyboard users who need obvious focus cues, and users with attention disorders who benefit from complete visual boundaries",
            "how_to_fix": "Use box-shadow that appears on all sides: 'box-shadow: 0 0 0 3px #0066cc' instead of offset shadows like 'box-shadow: 3px 0 0 #0066cc'. Alternatively, use outline which automatically appears on all sides. If design requires directional emphasis, combine it with a full-perimeter indicator. Test with screen magnifiers to verify visibility at high zoom levels."
        },
        "ErrHandlerOutlineWidthInsufficient": {
            "id": "ErrHandlerOutlineWidthInsufficient",
            "title": "Focus outline on event handler element is thinner than 2 pixels",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["2.4.11"],
            "wcag_full": "2.4.11 Focus Appearance (Level AAA)",
            "category": "event_handling",
            "description": "Element with event handler has a focus outline less than 2 CSS pixels thick",
            "why_it_matters": "WCAG 2.2 Success Criterion 2.4.11 (Level AAA) recommends focus indicators be at least 2 pixels thick. Thin outlines (1px) can be difficult to see, especially for elements that users don't expect to be interactive. For event handler elements, prominent focus indicators help users understand the element is focusable and interactive.",
            "who_it_affects": "Users with mild to moderate vision impairments, older users with age-related vision changes, users viewing screens at non-optimal distances or angles, users in bright environments where thin lines are hard to see, and users with attention disorders who benefit from more prominent visual cues",
            "how_to_fix": "Increase outline width to at least 2px: 'outline: 2px solid #0066cc'. Consider 3px for better visibility on interactive elements. Use outline-offset to add space: 'outline-offset: 2px'. For box-shadow alternatives, use at least 2px spread: 'box-shadow: 0 0 0 2px #0066cc'. Test visibility at various screen sizes and zoom levels."
        },
        "ErrHandlerColorChangeOnly": {
            "id": "ErrHandlerColorChangeOnly",
            "title": "Focus on event handler element relies solely on color change",
            "type": "Error",
            "impact": "High",
            "wcag": ["1.4.1"],
            "wcag_full": "1.4.1 Use of Color (Level A)",
            "category": "event_handling",
            "description": "Element with event handler indicates focus only through color change without structural change",
            "why_it_matters": "WCAG 1.4.1 requires that color is not the only visual means of conveying information. Users with color blindness cannot perceive color-only changes. For elements made interactive with event handlers, relying solely on color changes makes it impossible for color-blind users to see focus or understand that the element is interactive.",
            "who_it_affects": "Users with color blindness (affecting ~8% of men and 0.5% of women), users with low vision using high contrast modes, users with monochrome displays, users who have customized system colors, users in bright sunlight where color distinction is reduced, and users with cognitive disabilities who rely on multiple visual cues",
            "how_to_fix": "Add structural changes in addition to color: use outline, add border, add box-shadow, add underline for text, or change shape/size. Ensure the structural change is visible independent of color perception. Test by viewing in grayscale mode. For example: 'element:focus { outline: 2px solid #0066cc; background-color: #f0f0f0; }' provides both structural (outline) and color changes."
        },
        "ErrHandlerTransparentOutline": {
            "id": "ErrHandlerTransparentOutline",
            "title": "Focus outline on event handler element is semi-transparent",
            "type": "Error",
            "impact": "Medium",
            "wcag": ["1.4.11", "2.4.7"],
            "wcag_full": "1.4.11 Non-text Contrast (Level AA), 2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with event handler uses semi-transparent (alpha < 0.5) focus outline or box-shadow",
            "why_it_matters": "Semi-transparent focus indicators have reduced visibility and may fail contrast requirements depending on background content. For elements made interactive with event handlers, users may not expect them to be focusable - a clear, opaque focus indicator helps users understand the element is interactive. Transparency makes contrast unpredictable and unreliable.",
            "who_it_affects": "Users with low vision who need high-visibility focus indicators, users with color blindness who may not perceive subtle transparent overlays, users in bright viewing conditions, screen magnifier users tracking focus location, and keyboard users who depend on obvious focus cues",
            "how_to_fix": "Use fully opaque colors (alpha = 1.0) for focus indicators: 'outline: 2px solid rgb(0, 102, 204)' instead of 'rgba(0, 102, 204, 0.3)'. If transparency is desired, keep it above 0.8 alpha and verify 3:1 contrast on all possible backgrounds. Use solid colors with outline-offset for spacing rather than transparency. Test with various backgrounds."
        },
        "WarnHandlerDefaultFocus": {
            "id": "WarnHandlerDefaultFocus",
            "title": "Event handler element relies on default browser focus styles",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with event handler has no custom focus styles and relies on browser default focus indicator",
            "why_it_matters": "Default browser focus styles vary across browsers and may not make it obvious that non-standard elements (like divs with click handlers) are interactive. Custom focus styles ensure consistent user experience and can be designed to clearly indicate interactivity. Users may not expect divs/spans to be clickable without clear custom styling.",
            "who_it_affects": "All users benefit from consistent focus indicators, users who switch between browsers, users of browsers with less visible default focus styles, users with cognitive disabilities who need clear affordances for interactive elements, and developers maintaining consistent user experience",
            "how_to_fix": "Define custom :focus styles that clearly indicate interactivity: 'element:focus { outline: 2px solid #your-brand-color; outline-offset: 2px; background-color: #f0f0f0; }'. Make focus styles more prominent than typical elements since users don't expect these elements to be interactive. Ensure 3:1 contrast. Test across browsers. Consider using semantic HTML (<button>) instead."
        },
        "WarnHandlerNoBorderOutline": {
            "id": "WarnHandlerNoBorderOutline",
            "title": "Event handler element uses outline-only focus (screen magnifier concern)",
            "type": "Warning",
            "impact": "Low",
            "wcag": ["2.4.7"],
            "wcag_full": "2.4.7 Focus Visible (Level AA)",
            "category": "event_handling",
            "description": "Element with event handler uses only CSS outline for focus with no border or size change",
            "why_it_matters": "Screen magnifier users zoomed to 200-400% may not see CSS outline which appears outside element boundaries. For elements made interactive with event handlers, this is especially problematic as users may not know these elements are focusable. Combining outline with border or size changes ensures focus is visible even when magnified.",
            "who_it_affects": "Screen magnifier users zoomed to 200%+ who may have element visible but outline outside viewport, users with low vision using browser zoom at high levels, users with tunnel vision who focus on element center, mobile users in zoomed mode, and users who need multiple visual cues to identify interactive elements",
            "how_to_fix": "Combine outline with visible changes inside element boundaries: add border thickness change, add padding adjustment, add background color change, or add inner box-shadow. Use outline-offset with positive value to keep outline closer. For event handler elements, consider more prominent focus styles than typical interactive elements to compensate for unexpected interactivity. Test with browser zoom at 200%+."
        },
    }
    
    @classmethod
    def get_issue(cls, issue_id: str) -> Dict[str, Any]:
        """
        Get issue details by ID
        
        Args:
            issue_id: The issue identifier
            
        Returns:
            Dictionary with issue details or default if not found
        """
        # First try to get enhanced description
        try:
            enhanced = get_detailed_issue_description(issue_id)
            if enhanced and enhanced.get('title') != f"Issue {issue_id} needs documentation":
                # Convert enhanced format to catalog format
                return {
                    "id": issue_id,
                    "type": "Error" if "Err" in issue_id else "Warning" if "Warn" in issue_id else "Info",
                    "impact": enhanced.get('impact', 'Medium'),
                    "wcag": enhanced.get('wcag', []),
                    "wcag_full": ", ".join(enhanced.get('wcag', [])) if enhanced.get('wcag') else "",
                    "category": "unknown",  # Enhanced descriptions don't have categories
                    "description": enhanced.get('what', enhanced.get('title', '')),
                    "why_it_matters": enhanced.get('why', ''),
                    "who_it_affects": enhanced.get('who', ''),
                    "how_to_fix": enhanced.get('remediation', enhanced.get('how', '')),
                    # Include enhanced metadata for template use
                    "title": enhanced.get('title', ''),
                    "what": enhanced.get('what', ''),
                    "why": enhanced.get('why', ''),
                    "who": enhanced.get('who', ''),
                    "full_remediation": enhanced.get('remediation', '')
                }
        except Exception:
            pass  # Fall through to original catalog
        
        # Fall back to original ISSUES dictionary
        return cls.ISSUES.get(issue_id, cls._get_default_issue(issue_id))
    
    @classmethod
    def _get_default_issue(cls, issue_id: str) -> Dict[str, Any]:
        """Return default issue data when specific issue not found"""
        return {
            "id": issue_id,
            "type": "Error",
            "impact": "Medium",
            "wcag": [],
            "wcag_full": "WCAG criteria not specified",
            "category": "general",
            "description": f"Accessibility issue: {issue_id}",
            "why_it_matters": "This issue may create barriers for users with disabilities. Specific impact details are not available for this issue type.",
            "who_it_affects": "Users with disabilities who rely on assistive technologies or accessible interfaces",
            "how_to_fix": "Review the specific issue details and apply appropriate accessibility fixes. Consult WCAG guidelines for more information."
        }
    
    @classmethod
    def get_all_issues(cls) -> Dict[str, Dict[str, Any]]:
        """Get all issues in the catalog"""
        return cls.ISSUES
    
    @classmethod
    def get_issues_by_category(cls, category: str) -> List[Dict[str, Any]]:
        """Get all issues in a specific category"""
        return [
            issue for issue in cls.ISSUES.values()
            if issue['category'].lower() == category.lower()
        ]
    
    @classmethod
    def get_issues_by_impact(cls, impact: str) -> List[Dict[str, Any]]:
        """Get all issues with a specific impact level"""
        return [
            issue for issue in cls.ISSUES.values()
            if issue['impact'].lower() == impact.lower()
        ]
    
    @classmethod
    def get_issues_by_wcag(cls, wcag_criterion: str) -> List[Dict[str, Any]]:
        """Get all issues related to a specific WCAG criterion"""
        return [
            issue for issue in cls.ISSUES.values()
            if wcag_criterion in issue['wcag']
        ]
    
    @classmethod
    def enrich_issue(cls, issue_dict: dict) -> dict:
        """
        Enrich a basic issue dictionary with full catalog information
        
        Args:
            issue_dict: Basic issue with at least an 'id' field
            
        Returns:
            Enriched issue dictionary
        """
        issue_id = issue_dict.get('id', issue_dict.get('err', ''))
        catalog_data = cls.get_issue(issue_id)
        
        # Merge catalog data with existing issue data
        enriched = issue_dict.copy()
        
        # Add enriched fields if not present
        if 'description_full' not in enriched:
            enriched['description_full'] = catalog_data['description']
        if 'why_it_matters' not in enriched:
            enriched['why_it_matters'] = catalog_data['why_it_matters']
        if 'who_it_affects' not in enriched:
            enriched['who_it_affects'] = catalog_data['who_it_affects']
        if 'how_to_fix' not in enriched:
            enriched['how_to_fix'] = catalog_data['how_to_fix']
        if 'wcag_full' not in enriched:
            enriched['wcag_full'] = catalog_data['wcag_full']
        if 'impact' not in enriched:
            enriched['impact'] = catalog_data['impact']
            
        return enriched
