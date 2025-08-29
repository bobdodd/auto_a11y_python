# Accessibility Issue Catalog - Complete List for Review

## Instructions
Please review and edit the descriptions, WCAG mappings, impact levels, and user groups affected for each issue. The format for each entry is:

```
ID: [Issue identifier from code]
Type: [Error|Warning|Info|Discovery]
Impact: [High|Medium|Low]
WCAG: [List of WCAG success criteria, e.g., 1.1.1, 1.3.1]
Category: [images|forms|headings|landmarks|color|language|focus|etc.]
Description: [What the issue is]
Why it matters: [Why this is important for accessibility]
Who it affects: [Which user groups are impacted]
How to fix: [Remediation guidance]
```

---

## 1. IMAGES (img, svg)

### 1.1 Missing Alt Text
```
ID: ErrImageWithNoAlt
Type: Error
Impact: High
WCAG: 1.1.1
Category: images
Description: Image is missing alt attribute
Why it matters: Screen readers cannot convey the meaning of the image to blind users
Who it affects: Blind and low vision users using screen readers
How to fix: Add an alt attribute with descriptive text, or alt="" for decorative images
```

### 1.2 Empty Alt Text
```
ID: ErrImageWithEmptyAlt
Type: Error
Impact: Medium
WCAG: 1.1.1
Category: images
Description: Image has empty alt attribute but may be informative
Why it matters: Informative images need descriptions for screen reader users
Who it affects: Blind and low vision users
How to fix: Add descriptive alt text for informative images, keep alt="" only for decorative images
```

### 1.3 Alt Text is Image Filename
```
ID: ErrImageWithImgFileExtensionAlt
Type: Error
Impact: High
WCAG: 1.1.1
Category: images
Description: Alt text contains image file extension (e.g., "photo.jpg")
Why it matters: File names don't provide meaningful information about image content
Who it affects: Blind and low vision users
How to fix: Replace filename with descriptive text about the image content
```

### 1.4 Alt on Non-Image Element
```
ID: ErrAltOnElementThatDoesntTakeIt
Type: Error
Impact: Low
WCAG: 1.1.1
Category: images
Description: Alt attribute found on element that doesn't support it
Why it matters: Alt attributes only work on img elements, not divs or other elements
Who it affects: Screen reader users may miss important information
How to fix: Remove alt from non-img elements, use appropriate alternatives like aria-label
```

### 1.5 SVG Discovery
```
ID: DiscoFoundInlineSvg
Type: Discovery
Impact: N/A
WCAG: 1.1.1
Category: images
Description: Inline SVG found - needs manual review for accessibility
Why it matters: SVGs need proper titles and descriptions for accessibility
Who it affects: Screen reader users
How to fix: Add <title> and <desc> elements inside SVG, or role="img" with aria-label
```

```
ID: DiscoFoundSvgImage
Type: Discovery
Impact: N/A
WCAG: 1.1.1
Category: images
Description: SVG image found - needs manual review
Why it matters: SVG images may need alternative text
Who it affects: Screen reader users
How to fix: Ensure SVG has appropriate text alternatives
```

---

## 2. FORMS

### 2.1 Missing Labels
```
ID: ErrUnlabelledField
Type: Error
Impact: High
WCAG: 1.3.1, 3.3.2, 4.1.2
Category: forms
Description: Form input is missing a label
Why it matters: Users don't know what information to enter in the field
Who it affects: Screen reader users, users with cognitive disabilities
How to fix: Add a <label> element with for attribute, or use aria-label
```

```
ID: forms_ErrInputMissingLabel
Type: Error
Impact: High
WCAG: 1.3.1, 3.3.2, 4.1.2
Category: forms
Description: Form input element is missing an associated label
Why it matters: Users cannot determine the purpose of the input field
Who it affects: Screen reader users, voice control users, users with cognitive disabilities
How to fix: Add a <label> element with matching for/id attributes
```

### 2.2 Empty Labels
```
ID: ErrEmptyAriaLabelOnField
Type: Error
Impact: High
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Form field has empty aria-label attribute
Why it matters: Empty labels provide no information about the field
Who it affects: Screen reader users
How to fix: Add descriptive text to aria-label or use visible label
```

```
ID: ErrEmptyAriaLabelledByOnField
Type: Error
Impact: High
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Form field has empty aria-labelledby attribute
Why it matters: Empty labelledby provides no field description
Who it affects: Screen reader users
How to fix: Reference valid element IDs or use direct labeling
```

### 2.3 Label Issues
```
ID: ErrFieldAriaRefDoesNotExist
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: forms
Description: aria-labelledby references non-existent element
Why it matters: Broken reference means no label for screen readers
Who it affects: Screen reader users
How to fix: Fix the ID reference or use a different labeling method
```

```
ID: ErrFieldReferenceDoesNotExist
Type: Error
Impact: High
WCAG: 1.3.1
Category: forms
Description: Label for attribute references non-existent field
Why it matters: Label is not associated with any form field
Who it affects: Screen reader users
How to fix: Fix the for/id relationship
```

```
ID: ErrLabelContainsMultipleFields
Type: Error
Impact: Medium
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Single label contains multiple form fields
Why it matters: Unclear which field the label describes
Who it affects: Screen reader users
How to fix: Use separate labels for each field
```

```
ID: ErrOrphanLabelWithNoId
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: forms
Description: Label element exists but has no for attribute
Why it matters: Label is not programmatically associated with any field
Who it affects: Screen reader users
How to fix: Add for attribute pointing to field ID
```

### 2.4 Form Warnings
```
ID: WarnFormHasNoLabel
Type: Warning
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: forms
Description: Form element has no accessible name
Why it matters: Form purpose may be unclear
Who it affects: Screen reader users
How to fix: Add aria-label or aria-labelledby to form element
```

```
ID: forms_WarnRequiredNotIndicated
Type: Warning
Impact: Medium
WCAG: 3.3.2
Category: forms
Description: Required field not clearly indicated
Why it matters: Users don't know which fields are mandatory
Who it affects: All users, especially those with cognitive disabilities
How to fix: Add required attribute and visual indication
```

```
ID: forms_WarnGenericButtonText
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: forms
Description: Button has generic text like "Submit" or "Click here"
Why it matters: Button purpose is unclear out of context
Who it affects: Screen reader users navigating by buttons
How to fix: Use descriptive button text like "Submit registration"
```

```
ID: forms_WarnNoFieldset
Type: Warning
Impact: Medium
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Radio/checkbox group lacks fieldset and legend
Why it matters: Group relationship is not clear
Who it affects: Screen reader users
How to fix: Wrap related inputs in fieldset with legend
```

### 2.5 Form Discovery
```
ID: DiscoFormOnPage
Type: Discovery
Impact: N/A
WCAG: N/A
Category: forms
Description: Form detected on page - needs manual testing
Why it matters: Forms need comprehensive accessibility testing
Who it affects: All users with disabilities
How to fix: Manually test form with keyboard and screen reader
```

```
ID: forms_DiscoNoSubmitButton
Type: Discovery
Impact: N/A
WCAG: 3.3.2
Category: forms
Description: Form may lack clear submit button
Why it matters: Users may not know how to submit the form
Who it affects: Users with cognitive disabilities, keyboard users
How to fix: Ensure form has clear submit mechanism
```

```
ID: forms_DiscoPlaceholderAsLabel
Type: Discovery
Impact: N/A
WCAG: 3.3.2
Category: forms
Description: Placeholder may be used instead of label
Why it matters: Placeholder text disappears when typing
Who it affects: Users with memory/cognitive issues, screen reader users
How to fix: Use proper labels, placeholder for examples only
```

---

## 3. HEADINGS

### 3.1 Missing Headings
```
ID: ErrNoHeadingsOnPage
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.6
Category: headings
Description: No heading elements found on page
Why it matters: Headings provide page structure and navigation
Who it affects: Screen reader users, users with cognitive disabilities
How to fix: Add appropriate heading hierarchy starting with h1
```

```
ID: ErrNoH1OnPage
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.6
Category: headings
Description: Page is missing an h1 element
Why it matters: H1 provides the main topic of the page
Who it affects: Screen reader users navigating by headings
How to fix: Add one h1 element describing the main page content
```

### 3.2 Empty Headings
```
ID: ErrEmptyHeading
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.6
Category: headings
Description: Heading element contains no text
Why it matters: Empty headings break navigation and structure
Who it affects: Screen reader users
How to fix: Add text content or remove empty heading
```

### 3.3 Heading Hierarchy
```
ID: ErrHeadingLevelsSkipped
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: headings
Description: Heading levels are not in sequential order (e.g., h1 to h3)
Why it matters: Skipped levels confuse document structure
Who it affects: Screen reader users, users with cognitive disabilities
How to fix: Use sequential heading levels without skipping
```

```
ID: ErrHeadingsDontStartWithH1
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: headings
Description: First heading on page is not h1
Why it matters: Document structure should start with h1
Who it affects: Screen reader users
How to fix: Start heading hierarchy with h1
```

```
ID: ErrMultipleH1HeadingsOnPage
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: headings
Description: Multiple h1 elements found on page
Why it matters: Unclear main topic of page
Who it affects: Screen reader users
How to fix: Use only one h1 per page
```

### 3.4 ARIA Heading Issues
```
ID: ErrFoundAriaLevelButNoRoleAppliedAtAll
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: headings
Description: aria-level attribute without role="heading"
Why it matters: aria-level only works with heading role
Who it affects: Screen reader users
How to fix: Add role="heading" or use native heading element
```

```
ID: ErrFoundAriaLevelButRoleIsNotHeading
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: headings
Description: aria-level on element without heading role
Why it matters: aria-level requires heading role to work
Who it affects: Screen reader users
How to fix: Add role="heading" or remove aria-level
```

```
ID: ErrInvalidAriaLevel
Type: Error
Impact: Medium
WCAG: 1.3.1, 4.1.2
Category: headings
Description: Invalid aria-level value (not 1-6)
Why it matters: Invalid levels break heading hierarchy
Who it affects: Screen reader users
How to fix: Use aria-level values 1 through 6 only
```

```
ID: ErrRoleOfHeadingButNoLevelGiven
Type: Error
Impact: Medium
WCAG: 1.3.1, 4.1.2
Category: headings
Description: role="heading" without aria-level
Why it matters: Heading level is undefined
Who it affects: Screen reader users
How to fix: Add aria-level attribute with value 1-6
```

### 3.5 Heading Warnings
```
ID: WarnHeadingOver60CharsLong
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: headings
Description: Heading text exceeds 60 characters
Why it matters: Long headings are hard to scan and understand
Who it affects: Users with cognitive disabilities, screen reader users
How to fix: Use concise heading text
```

```
ID: WarnHeadingInsideDisplayNone
Type: Warning
Impact: Low
WCAG: 1.3.1
Category: headings
Description: Heading is hidden with display:none
Why it matters: Hidden headings may affect document structure
Who it affects: Screen reader users (varies by implementation)
How to fix: Remove unused headings or make them visible
```

---

## 4. LANDMARKS

### 4.1 Missing Landmarks
```
ID: ErrNoMainLandmarkOnPage
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.1
Category: landmarks
Description: Page is missing main landmark
Why it matters: Main landmark identifies primary content area
Who it affects: Screen reader users navigating by landmarks
How to fix: Add <main> element or role="main" to primary content
```

```
ID: ErrNoBannerLandmarkOnPage
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.1
Category: landmarks
Description: Page is missing banner landmark (header)
Why it matters: Banner provides consistent navigation area
Who it affects: Screen reader users
How to fix: Add <header> element or role="banner"
```

```
ID: WarnNoContentinfoLandmarkOnPage
Type: Warning
Impact: Low
WCAG: 1.3.1, 2.4.1
Category: landmarks
Description: Page is missing contentinfo landmark (footer)
Why it matters: Footer provides consistent supplementary information
Who it affects: Screen reader users
How to fix: Add <footer> element or role="contentinfo"
```

```
ID: WarnNoNavLandmarksOnPage
Type: Warning
Impact: Low
WCAG: 1.3.1, 2.4.1
Category: landmarks
Description: Page has no navigation landmarks
Why it matters: Navigation areas should be marked as such
Who it affects: Screen reader users
How to fix: Add <nav> element or role="navigation"
```

### 4.2 Multiple Landmarks
```
ID: ErrMultipleMainLandmarksOnPage
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Multiple main landmarks found
Why it matters: Unclear which is the primary content
Who it affects: Screen reader users
How to fix: Use only one main landmark per page
```

```
ID: ErrMultipleBannerLandmarksOnPage
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Multiple banner landmarks found
Why it matters: Multiple headers confuse page structure
Who it affects: Screen reader users
How to fix: Use only one banner landmark
```

```
ID: ErrMultipleContentinfoLandmarksOnPage
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Multiple contentinfo landmarks found
Why it matters: Multiple footers confuse page structure
Who it affects: Screen reader users
How to fix: Use only one contentinfo landmark
```

### 4.3 Landmark Labels
```
ID: ErrBannerLandmarkAccessibleNameIsBlank
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Banner landmark has blank accessible name
Why it matters: Multiple banners need labels to distinguish them
Who it affects: Screen reader users
How to fix: Add aria-label or aria-labelledby
```

```
ID: ErrNavLandmarkAccessibleNameIsBlank
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Navigation landmark has blank accessible name
Why it matters: Multiple nav areas need labels
Who it affects: Screen reader users
How to fix: Add aria-label like "Main navigation" or "Footer navigation"
```

```
ID: WarnNavLandmarkHasNoLabel
Type: Warning
Impact: Low
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Navigation landmark lacks label
Why it matters: Hard to distinguish multiple navigation areas
Who it affects: Screen reader users
How to fix: Add descriptive aria-label
```

### 4.4 Landmark Nesting
```
ID: ErrMainLandmarkMayNotbeChildOfAnotherLandmark
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Main landmark nested inside another landmark
Why it matters: Invalid landmark nesting breaks structure
Who it affects: Screen reader users
How to fix: Move main outside of other landmarks
```

```
ID: ErrBannerLandmarkMayNotBeChildOfAnotherLandmark
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Banner landmark nested inside another landmark
Why it matters: Invalid nesting breaks page structure
Who it affects: Screen reader users
How to fix: Move banner to top level
```

```
ID: ErrNestedNavLandmarks
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Navigation landmarks are nested
Why it matters: Confusing navigation structure
Who it affects: Screen reader users
How to fix: Flatten navigation structure
```

### 4.5 Content Outside Landmarks
```
ID: ErrElementNotContainedInALandmark
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Content exists outside of any landmark
Why it matters: Content may be missed when navigating by landmarks
Who it affects: Screen reader users using landmark navigation
How to fix: Ensure all content is within appropriate landmarks
```

---

## 5. COLOR & CONTRAST

### 5.1 Contrast Errors
```
ID: ErrTextContrast
Type: Error
Impact: High
WCAG: 1.4.3, 1.4.6
Category: color
Description: Text has insufficient color contrast
Why it matters: Text is difficult or impossible to read
Who it affects: Users with low vision, color blindness, older users
How to fix: Increase contrast ratio to 4.5:1 for normal text, 3:1 for large text
```

### 5.2 Color Style Issues
```
ID: ErrColorStyleDefinedExplicitlyInElement
Type: Error
Impact: Medium
WCAG: 1.4.3
Category: color
Description: Color defined inline on element
Why it matters: Inline styles are harder to maintain and override
Who it affects: Users who need custom color schemes
How to fix: Move color definitions to CSS classes
```

```
ID: ErrColorStyleDefinedExplicitlyInStyleTag
Type: Error
Impact: Low
WCAG: 1.4.3
Category: color
Description: Color defined in style tag
Why it matters: Embedded styles harder to override
Who it affects: Users with custom stylesheets
How to fix: Use external stylesheets
```

```
ID: ErrColorRelatedStyleDefinedExplicitlyInElement
Type: Error
Impact: Low
WCAG: 1.4.3
Category: color
Description: Color-related styles defined inline
Why it matters: Harder to maintain consistent color scheme
Who it affects: Users needing high contrast modes
How to fix: Use CSS classes instead of inline styles
```

---

## 6. LANGUAGE

### 6.1 Missing Language
```
ID: ErrNoPrimaryLangAttr
Type: Error
Impact: High
WCAG: 3.1.1
Category: language
Description: HTML element missing lang attribute
Why it matters: Screen readers don't know which language to use
Who it affects: Screen reader users
How to fix: Add lang="en" (or appropriate language code) to html element
```

```
ID: ErrEmptyLangAttr
Type: Error
Impact: High
WCAG: 3.1.1
Category: language
Description: Lang attribute is empty
Why it matters: Empty lang provides no language information
Who it affects: Screen reader users
How to fix: Add valid language code to lang attribute
```

### 6.2 Invalid Language
```
ID: ErrPrimaryLangUnrecognized
Type: Error
Impact: High
WCAG: 3.1.1
Category: language
Description: Language code not recognized
Why it matters: Invalid language codes prevent proper pronunciation
Who it affects: Screen reader users
How to fix: Use valid ISO 639-1 language codes
```

```
ID: ErrIncorrectlyFormattedPrimaryLang
Type: Error
Impact: Medium
WCAG: 3.1.1
Category: language
Description: Language code incorrectly formatted
Why it matters: Malformed codes may not work properly
Who it affects: Screen reader users
How to fix: Use correct format: "en-US" or "en"
```

```
ID: ErrElementPrimaryLangNotRecognized
Type: Error
Impact: Medium
WCAG: 3.1.1, 3.1.2
Category: language
Description: Element has unrecognized language code
Why it matters: Language changes won't be announced properly
Who it affects: Screen reader users
How to fix: Use valid language codes
```

### 6.3 Language Mismatches
```
ID: ErrPrimaryLangAndXmlLangMismatch
Type: Error
Impact: Low
WCAG: 3.1.1
Category: language
Description: lang and xml:lang attributes don't match
Why it matters: Conflicting language information
Who it affects: Screen reader users
How to fix: Ensure both attributes have same value
```

### 6.4 Hreflang Issues
```
ID: ErrHreflangNotOnLink
Type: Error
Impact: Low
WCAG: 3.1.1
Category: language
Description: hreflang attribute on non-link element
Why it matters: hreflang only works on links
Who it affects: Screen reader users
How to fix: Move hreflang to anchor elements only
```

---

## 7. FOCUS & KEYBOARD

### 7.1 Focus Indicators
```
ID: ErrOutlineIsNoneOnInteractiveElement
Type: Error
Impact: High
WCAG: 2.4.7
Category: focus
Description: Interactive element has outline:none
Why it matters: No visible focus indicator for keyboard users
Who it affects: Keyboard users, users with motor disabilities
How to fix: Provide visible focus indicator, don't remove outline
```

```
ID: ErrNoOutlineOffsetDefined
Type: Error
Impact: Medium
WCAG: 2.4.7
Category: focus
Description: No outline offset defined for focus
Why it matters: Focus indicator may be hard to see
Who it affects: Keyboard users
How to fix: Add outline-offset for better visibility
```

```
ID: ErrZeroOutlineOffset
Type: Error
Impact: Medium
WCAG: 2.4.7
Category: focus
Description: Outline offset is set to zero
Why it matters: Focus indicator touches element edge
Who it affects: Keyboard users with low vision
How to fix: Use positive outline-offset value
```

### 7.2 Tab Order
```
ID: ErrPositiveTabIndex
Type: Error
Impact: High
WCAG: 2.4.3
Category: focus
Description: Positive tabindex value used
Why it matters: Disrupts natural tab order
Who it affects: Keyboard users
How to fix: Use tabindex="0" or "-1" only
```

```
ID: ErrNegativeTabIndex
Type: Error
Impact: Medium
WCAG: 2.4.3
Category: focus
Description: Negative tabindex on interactive element
Why it matters: Element removed from tab order
Who it affects: Keyboard users
How to fix: Use tabindex="0" for interactive elements
```

```
ID: ErrTabindexOfZeroOnNonInteractiveElement
Type: Error
Impact: Low
WCAG: 2.4.3
Category: focus
Description: tabindex="0" on non-interactive element
Why it matters: Non-interactive elements in tab order
Who it affects: Keyboard users
How to fix: Remove tabindex from non-interactive elements
```

```
ID: ErrWrongTabindexForInteractiveElement
Type: Error
Impact: Medium
WCAG: 2.4.3
Category: focus
Description: Inappropriate tabindex on interactive element
Why it matters: Tab order doesn't match visual order
Who it affects: Keyboard users
How to fix: Let natural tab order work, avoid tabindex
```

---

## 8. FONTS

### 8.1 Font Warnings
```
ID: WarnFontNotInRecommenedListForA11y
Type: Warning
Impact: Low
WCAG: 1.4.8
Category: fonts
Description: Font not in recommended accessibility list
Why it matters: Some fonts are harder to read
Who it affects: Users with dyslexia, low vision
How to fix: Use clear, simple fonts like Arial, Verdana
```

```
ID: WarnFontsizeIsBelow16px
Type: Warning
Impact: Medium
WCAG: 1.4.4
Category: fonts
Description: Font size below 16px
Why it matters: Small text is hard to read
Who it affects: Users with low vision, older users
How to fix: Use minimum 16px for body text
```

### 8.2 Font Discovery
```
ID: DiscoFontFound
Type: Discovery
Impact: N/A
WCAG: N/A
Category: fonts
Description: Font usage detected for review
Why it matters: Some fonts may have readability issues
Who it affects: Users with reading disabilities
How to fix: Review font choices for readability
```

---

## 9. TITLE & ARIA

### 9.1 Title Issues
```
ID: ErrTitleAttrFound
Type: Error
Impact: Low
WCAG: 3.3.2, 4.1.2
Category: title
Description: Title attribute used for important information
Why it matters: Title attributes are not reliably accessible
Who it affects: Mobile users, keyboard users, some screen readers
How to fix: Use visible text or proper labels instead
```

```
ID: ErrErrEmptyTitleAttr
Type: Error
Impact: Low
WCAG: 3.3.2
Category: title
Description: Empty title attribute
Why it matters: Empty titles provide no information
Who it affects: Users expecting tooltip information
How to fix: Remove empty title attributes
```

```
ID: ErrIframeWithNoTitleAttr
Type: Error
Impact: High
WCAG: 2.4.1, 4.1.2
Category: title
Description: Iframe missing title attribute
Why it matters: Screen readers can't describe iframe content
Who it affects: Screen reader users
How to fix: Add descriptive title to iframe
```

### 9.2 ARIA Issues
```
ID: ErrAriaLabelMayNotBeFoundByVoiceControl
Type: Error
Impact: Medium
WCAG: 2.5.3
Category: aria
Description: aria-label doesn't match visible text
Why it matters: Voice control users can't activate element
Who it affects: Voice control users
How to fix: Ensure aria-label includes visible text
```

```
ID: ErrLabelMismatchOfAccessibleNameAndLabelText
Type: Error
Impact: Medium
WCAG: 2.5.3
Category: aria
Description: Accessible name doesn't match visible label
Why it matters: Confusing for voice control users
Who it affects: Voice control users
How to fix: Make accessible name match visible text
```

---

## 10. STYLE & JAVASCRIPT

### 10.1 Style Discovery
```
ID: DiscoStyleAttrOnElements
Type: Discovery
Impact: N/A
WCAG: N/A
Category: style
Description: Inline styles detected
Why it matters: May affect responsive design and user customization
Who it affects: Users with custom stylesheets
How to fix: Consider moving to CSS classes
```

```
ID: DiscoStyleElementOnPage
Type: Discovery
Impact: N/A
WCAG: N/A
Category: style
Description: Style element found in page
Why it matters: Embedded styles harder to override
Who it affects: Users needing custom styles
How to fix: Consider external stylesheets
```

### 10.2 JavaScript Discovery
```
ID: DiscoFoundJS
Type: Discovery
Impact: N/A
WCAG: N/A
Category: javascript
Description: JavaScript detected on page
Why it matters: Functionality should work without JavaScript
Who it affects: Users with JavaScript disabled
How to fix: Ensure progressive enhancement
```

---

## Additional Notes for Editor

Please review each issue and:

1. **Verify WCAG Mappings**: Ensure the WCAG success criteria are accurate
2. **Adjust Impact Levels**: Change High/Medium/Low based on actual user impact
3. **Enhance Descriptions**: Make descriptions clearer and more specific
4. **Improve Remediation**: Provide more detailed fix instructions
5. **Add Missing Issues**: If you notice any issues not listed, please add them
6. **Categorize Properly**: Ensure each issue is in the right category
7. **User Groups**: Specify which disability groups are affected:
   - Vision (blind, low vision, color blind)
   - Hearing (deaf, hard of hearing)
   - Motor (limited mobility, tremors)
   - Cognitive (dyslexia, ADHD, memory issues)
   - Seizure (photosensitive epilepsy)

## Format for New Issues

If adding new issues, please use this format:

```
ID: [unique_identifier]
Type: [Error|Warning|Info|Discovery]
Impact: [High|Medium|Low|N/A]
WCAG: [comma-separated list]
Category: [category_name]
Description: [what the issue is]
Why it matters: [accessibility impact]
Who it affects: [affected user groups]
How to fix: [remediation steps]
```