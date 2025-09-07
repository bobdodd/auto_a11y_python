# Accessibility Issue Catalog - Organized by Touchpoint

## Instructions
This catalog organizes all accessibility issues by touchpoint (testing category). Each entry follows this format:

```
ID: [Issue identifier from code]
Type: [Error|Warning|Info|Discovery]
Impact: [High|Medium|Low|N/A]
WCAG: [List of WCAG success criteria, e.g., 1.1.1, 1.3.1]
Description: [What the issue is]
Why it matters: [Why this is important for accessibility]
Who it affects: [Which users are impacted]
How to fix: [Remediation guidance]
```

## Touchpoints

### ARIA

ID:  AI_ErrAccordionWithoutARIA
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2, 1.3.1
Category: navigation
Description: Accordion element "{element_text}" lacks proper ARIA markup
Why it matters: Without aria-expanded and proper roles, users cannot determine if sections are expanded or collapsed
Who it affects: Screen reader users, keyboard users
How to fix: Add button role to headers, aria-expanded to indicate state, and aria-controls to link headers to panels
```

```

---

ID:  AI_ErrCarouselWithoutARIA
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2, 2.2.2
Category: navigation
Description: Carousel/slider "{element_text}" lacks proper ARIA markup and controls
Why it matters: Without proper ARIA and controls, users cannot understand or control the carousel's behavior
Who it affects: Screen reader users, keyboard users, users with motor impairments
How to fix: Add role="region", aria-label, aria-live for updates, and accessible previous/next controls
```

```

---

ID:  AI_ErrDropdownWithoutARIA
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2, 1.3.1
Category: forms
Description: Dropdown menu "{element_text}" lacks proper ARIA markup
Why it matters: Without aria-expanded, aria-haspopup, and proper roles, users cannot understand the dropdown's state or navigate it properly
Who it affects: Screen reader users, keyboard users
How to fix: Add aria-haspopup="true", aria-expanded state, and role="menu" with role="menuitem" for options
```

```

---

ID:  AI_ErrMissingInteractiveRole
Type: Error
Impact: High
WCAG: 4.1.2
Category: forms
Description: Interactive {element_tag} element lacks appropriate ARIA role
Why it matters: Screen readers won't announce this as an interactive control
Who it affects: Screen reader users
How to fix: Add appropriate ARIA role (button, link, checkbox, etc.) to the element
```

```

---

ID:  ErrFoundAriaLevelButNoRoleAppliedAtAll
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

---

ID:  ErrInvalidAriaLevel
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

---

ID: ErrMapAriaHidden
Type: Error
Impact: High
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Map element hidden from assistive technologies with aria-hidden
Why it matters: Hiding maps completely removes access to important geographic or spatial information for screen reader users.
Who it affects: Blind and low vision users who need text alternatives for map information.
How to fix: Remove aria-hidden from maps, provide appropriate text alternatives and accessible controls instead.

---

### Accessible Names

ID: ErrMissingAccessibleName
Type: Error
Impact: High
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Interactive element has no accessible name
Why it matters: Without accessible names, screen reader users cannot identify or interact with controls.
Who it affects: Screen reader users who cannot identify unnamed controls, voice control users who cannot target elements.
How to fix: Add aria-label, aria-labelledby, or visible text labels to all interactive elements.

---

ID: WarnGenericAccessibleName
Type: Warning
Impact: Medium
WCAG: 2.4.6 Headings and Labels (Level AA)
Description: Element has generic accessible name that doesn't describe its purpose
Why it matters: Generic names like "button" or "link" don't help users understand element purpose.
Who it affects: Screen reader users, voice control users.
How to fix: Provide descriptive accessible names that explain the element's specific purpose.

---

### Animation

ID:  AI_WarnProblematicAnimation
Type: Warning
Impact: Medium
WCAG: 2.2.2, 2.3.1
Category: animations
Description: Animation detected that may cause accessibility issues
Why it matters: Animations can trigger seizures or make content difficult to read
Who it affects: Users with vestibular disorders, photosensitive epilepsy, or cognitive disabilities
How to fix: Provide pause/stop controls and respect prefers-reduced-motion preference
```

### Visual Information Issues

```

---

ID: ErrInfiniteAnimation
Type: Error
Impact: High
WCAG: 2.2.2 Pause, Stop, Hide (Level A)
Description: Animation runs infinitely without pause controls
Why it matters: Continuous animations can trigger seizures, cause distraction, and make content unusable for many users.
Who it affects: Users with vestibular disorders, users with ADHD, users with photosensitive epilepsy, users with cognitive disabilities.
How to fix: Provide pause/stop controls for all animations, respect prefers-reduced-motion settings, limit animation duration.

---

ID: ErrNoReducedMotionSupport
Type: Error
Impact: High
WCAG: 2.3.3 Animation from Interactions (Level AAA)
Description: Animations do not respect prefers-reduced-motion setting
Why it matters: Users with vestibular disorders can experience nausea, dizziness, or seizures from motion.
Who it affects: Users with vestibular disorders, users with motion sensitivity, users with ADHD.
How to fix: Use CSS @media (prefers-reduced-motion: reduce) to disable or reduce animations, provide animation toggle controls.

---

ID: WarnLongAnimation
Type: Warning
Impact: Medium
WCAG: 2.2.2 Pause, Stop, Hide (Level A)
Description: Animation duration exceeds 5 seconds
Why it matters: Long animations can be distracting and may need user controls.
Who it affects: Users with attention disorders, users with cognitive disabilities.
How to fix: Shorten animation duration or provide pause/stop controls.

---

### Buttons

ID:  AI_ErrNonSemanticButton
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2
Category: buttons
Description: Clickable {element_tag} element "{element_text}" is not a semantic button
Why it matters: Non-semantic buttons are not keyboard accessible and invisible to screen readers
Who it affects: Keyboard users, screen reader users
How to fix: Replace {element_tag} with <button> element or add role="button" and tabindex="0"
```

```

---

ID:  ErrButtonNoVisibleFocus
Type: Error
Impact: High
WCAG: 2.4.7 Focus Visible
Category: buttons
Description: Button lacks visible focus indicator when focused
Why it matters: Keyboard users need visible focus indicators to know which element is currently selected. Without clear focus indication on buttons, users cannot tell which button will be activated when they press Enter or Space, leading to errors and inability to use the interface effectively.
Who it affects: Users with motor disabilities using keyboard navigation, users who cannot use a mouse, power users who prefer keyboard navigation, and users of assistive technologies
How to fix: Ensure buttons have a clearly visible focus indicator with at least 3:1 contrast against the background. The indicator should be at least 2 pixels thick and not rely on color alone. Never remove focus indicators without providing an alternative. Consider using :focus-visible for refined focus management.
```

```

---

ID:  ErrButtonTextLowContrast
Type: Error
Impact: High
WCAG: 1.4.3 Contrast (Minimum)
Category: buttons
Description: Button text has insufficient color contrast with button background
Why it matters: Users with low vision, color blindness, or viewing the page in bright sunlight may not be able to read button labels if contrast is insufficient. This prevents users from understanding button purpose and can make critical functions inaccessible. Buttons are action triggers, so being unable to read them can prevent task completion.
Who it affects: Users with low vision, color blindness, age-related vision changes, and anyone viewing content in poor lighting conditions or on low-quality displays
How to fix: Ensure button text has at least 4.5:1 contrast ratio with the button background for normal text, or 3:1 for large text (18pt or 14pt bold). For Level AAA compliance, use 7:1 for normal text. Test in different states (hover, focus, active) as contrast requirements apply to all states. Avoid using color alone to indicate button state.
```

```

---

ID: ErrMissingCloseButton
Type: Error
Impact: High
WCAG: 2.1.2 No Keyboard Trap (Level A)
Description: Modal or dialog missing close button
Why it matters: Without a close button, users can become trapped in modals with no way to return to main content.
Who it affects: Keyboard users who cannot use escape key, screen reader users who need explicit close controls.
How to fix: Add visible close button to all modals and dialogs, ensure it's keyboard accessible and properly labeled.

---

ID:  WarnButtonGenericText
Type: Warning
Impact: Medium
WCAG: 2.4.6 Headings and Labels
Category: buttons
Description: Button uses generic text like "Click here", "Submit", or "OK" without context
Why it matters: Screen reader users often navigate by pulling up a list of all buttons on a page. Generic button text provides no information about what the button does when heard out of context. Users cannot determine the button's purpose without additional exploration, slowing navigation and potentially causing errors.
Who it affects: Screen reader users navigating by buttons list, users with cognitive disabilities who need clear labels, and screen magnifier users who may not see surrounding context
How to fix: Use descriptive button text that explains the action (e.g., "Submit registration form" instead of "Submit", "Download PDF report" instead of "Download"). The button text should make sense when read in isolation. If visual design constraints require short text, use aria-label to provide a more descriptive accessible name.
```

## 12. LINKS

### 12.1 Link Purpose
```

---

ID:  WarnLinkLooksLikeButton
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships
Category: links
Description: Link is styled to look like a button but uses anchor element
Why it matters: Links and buttons have different behaviors - links navigate to new locations while buttons trigger actions. When links look like buttons, users may have incorrect expectations about what will happen. Keyboard users expect Space key to activate buttons but it doesn't work on links.
Who it affects: Keyboard users who expect button behavior, screen reader users who hear it announced as a link but see it as a button, and users with cognitive disabilities who rely on consistent interactions
How to fix: If the element performs an action (submit form, open dialog), use a button element. If it navigates to a new URL, keep it as a link but consider whether button styling is appropriate. Ensure keyboard behavior matches the element type.
```

## 13. PDF DOCUMENTS

### 11.1 PDF Discovery
```

---

### Colors and Contrast

ID:  ErrColorStyleDefinedExplicitlyInElement
Type: Error
Impact: Low
WCAG: 1.4.3
Category: color
Description: Color-related styles defined inline
Why it matters: Harder to maintain consistent color scheme
Who it affects: Users needing high contrast modes
How to fix: Use CSS classes instead of inline styles
```

```

---

ID:  ErrColorStyleDefinedExplicitlyInStyleTag
Type: Error
Impact: Low
WCAG: 1.4.3
Category: color
Description: Color-related styles defined in style tag
Why it matters: Embedded color styles harder to override for user preferences
Who it affects: Users with custom stylesheets, high contrast mode users
How to fix: Use external stylesheets for better maintainability
```

```

---

ID: ErrInsufficientContrast
Type: Error
Impact: High
WCAG: 1.4.3 Contrast (Minimum) (Level AA)
Description: Text does not meet WCAG contrast ratio requirements
Why it matters: Insufficient contrast makes text unreadable for users with low vision or in challenging lighting conditions.
Who it affects: Users with low vision, users with color blindness, aging users, all users in bright sunlight or glare.
How to fix: Ensure 4.5:1 contrast ratio for normal text, 3:1 for large text (18pt+), use color contrast analyzers to verify.

---

ID:  ErrLargeTextContrastAA
Type: Error
Impact: High
WCAG: 1.4.3 Contrast (Minimum)
Category: color
Description: Large text fails WCAG AA with contrast ratio of {ratio}:1 (foreground: {fg}, background: {bg})
Why it matters: This large text ({fontSize}px) with a contrast ratio of {ratio}:1 does not meet WCAG Level AA requirements. Large text (24px+ or 18.66px+ bold) requires a minimum contrast ratio of 3:1 to pass Level AA. The foreground color ({fg}) against background ({bg}) doesn't provide enough distinction.
Who it affects: Users with low vision, color blindness, or age-related vision changes who struggle to distinguish text with insufficient contrast, even when the text is larger
How to fix: Current contrast is {ratio}:1, but WCAG Level AA requires at least 3:1 for large text. To fix, adjust the foreground color from {fg} or the background from {bg}. Consider using #949494 or darker on white background for large text.
```

### 5.2 Contrast Errors - Level AAA
```

---

ID:  ErrLargeTextContrastAAA
Type: Error
Impact: High
WCAG: 1.4.6 Contrast (Enhanced)
Category: color
Description: Large text fails WCAG AAA with contrast ratio of {ratio}:1 (foreground: {fg}, background: {bg})
Why it matters: This large text ({fontSize}px) with a contrast ratio of {ratio}:1 does not meet WCAG Level AAA enhanced requirements. Large text (24px+ or 18.66px+ bold) requires a minimum contrast ratio of 4.5:1 to pass Level AAA for enhanced accessibility.
Who it affects: Users with moderate visual impairments who benefit from enhanced contrast even for large text, ensuring optimal readability in all conditions
How to fix: Current contrast is {ratio}:1, but WCAG Level AAA requires at least 4.5:1 for large text. To fix, adjust colors to achieve higher contrast, such as #767676 or darker on white background for large text at Level AAA.
```

### 5.2 Color Style Issues
```

---

ID:  ErrTextContrastAA
Type: Error
Impact: High
WCAG: 1.4.3 Contrast (Minimum)
Category: color
Description: Text fails WCAG AA with contrast ratio of {ratio}:1 (foreground: {fg}, background: {bg})
Why it matters: This text with a contrast ratio of {ratio}:1 does not meet WCAG Level AA requirements. Normal text requires a minimum contrast ratio of 4.5:1 to pass Level AA. The foreground color ({fg}) against the background ({bg}) doesn't provide enough distinction for users with visual impairments.
Who it affects: Users with low vision who need higher contrast to distinguish text, users with color blindness, older users experiencing age-related vision changes, and users viewing content in bright sunlight or on low-quality displays
How to fix: Current contrast is {ratio}:1, but WCAG Level AA requires at least 4.5:1 for normal text ({fontSize}px). To fix, darken the foreground color from {fg} or lighten the background from {bg}. Consider using #595959 or darker on white background, or #FFFFFF on backgrounds darker than #767676.
```

```

---

ID:  ErrTextContrastAAA
Type: Error
Impact: High
WCAG: 1.4.6 Contrast (Enhanced)
Category: color
Description: Text fails WCAG AAA with contrast ratio of {ratio}:1 (foreground: {fg}, background: {bg})
Why it matters: This text with a contrast ratio of {ratio}:1 does not meet WCAG Level AAA enhanced requirements. Normal text requires a minimum contrast ratio of 7:1 to pass Level AAA. The foreground color ({fg}) against the background ({bg}) doesn't provide optimal distinction for maximum accessibility.
Who it affects: Users with moderate visual impairments, including those with low vision, color blindness, or contrast sensitivity who benefit from enhanced contrast for optimal readability
How to fix: Current contrast is {ratio}:1, but WCAG Level AAA requires at least 7:1 for normal text ({fontSize}px). To fix, use high contrast combinations like #333333 or darker on white background, or white text on backgrounds darker than #565656.
```

```

---

ID: InfoNoColorSchemeSupport
Type: Info
Impact: Low
WCAG: 1.4.3 Contrast (Minimum) (Level AA)
Description: Site doesn't support OS color scheme preferences
Why it matters: Supporting user color preferences improves readability and reduces eye strain.
Who it affects: Users who prefer dark mode, users with light sensitivity.
How to fix: Implement CSS prefers-color-scheme media query to support dark/light mode preferences.

---

ID: InfoNoContrastSupport
Type: Info
Impact: Low
WCAG: 1.4.3 Contrast (Minimum) (Level AA)
Description: Site doesn't support high contrast mode
Why it matters: High contrast mode helps users with low vision read content more easily.
Who it affects: Users with low vision, users in bright lighting conditions.
How to fix: Test site in high contrast mode, ensure it remains usable, consider high contrast stylesheet option.

---

ID:  WarnColorRelatedStyleDefinedExplicitlyInElement
Type: Warning
Impact: Low
WCAG: 1.4.3 Contrast (Minimum), 1.4.8 Visual Presentation
Category: color
Description: Color-related CSS properties found in inline style attributes on HTML elements
Why it matters: Inline color styles bypass user stylesheets and browser extensions that help users with visual disabilities customize colors for better readability. Users who need high contrast, inverted colors, or specific color schemes cannot easily override inline styles. This also makes it difficult to implement dark mode, maintain consistent theming, or allow user color preferences.
Who it affects: Users with low vision who need high contrast or specific color combinations, users with color blindness who need to adjust problematic color pairs, users with dyslexia who benefit from specific background colors, users with light sensitivity who need dark themes, and users who rely on browser extensions for color customization
How to fix: Move color-related styles (color, background-color, border-color, etc.) to external CSS files using classes. This allows users to override styles with their own stylesheets, enables easier theme switching, improves maintainability, and supports user preference media queries like prefers-color-scheme. Use CSS custom properties (variables) for colors to make customization even easier.
```

```

---

ID:  WarnColorRelatedStyleDefinedExplicitlyInStyleTag
Type: Warning
Impact: Low
WCAG: 1.4.3 Contrast (Minimum), 1.4.8 Visual Presentation
Category: color
Description: Color-related CSS found in <style> tags within the HTML document instead of external stylesheets
Why it matters: Embedded styles in <style> tags are harder for users to override than external stylesheets and may not be cached efficiently. Users with visual disabilities who need custom color schemes must use more aggressive CSS overrides. This approach also makes it difficult to maintain consistent theming across pages and prevents users from disabling styles entirely if needed.
Who it affects: Users with low vision requiring custom color schemes, users with photosensitivity needing to modify bright colors, users with color blindness who need to adjust color combinations, and users who benefit from consistent, predictable styling across pages
How to fix: Move color styles to external CSS files linked with <link> tags. Organize colors using CSS custom properties for easy theming. Implement user preference support with @media (prefers-color-scheme) and similar queries. Consider providing theme switcher functionality. Ensure your external stylesheets are properly cached for performance.
```

---

## 6. LANGUAGE

### 6.1 Missing Language
```

---

### Dialogs and Modals

ID:  AI_ErrDialogWithoutARIA
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2, 2.4.3
Category: dialogs
Description: {element_tag} element "{element_text}" appears to be a dialog/modal but lacks proper ARIA markup
Why it matters: Without proper ARIA attributes, screen readers cannot announce the dialog's purpose, state, or provide proper navigation
Who it affects: Screen reader users, keyboard users who need focus management
How to fix: Add role="dialog", aria-modal="true", aria-label or aria-labelledby, and implement focus trap
```

```

---

ID: ErrModalMissingClose
Type: Error
Impact: High
WCAG: 2.1.2 No Keyboard Trap (Level A)
Description: Modal dialog has no way to close it
Why it matters: Users become trapped in the modal with no way to return to the main content.
Who it affects: All users, especially keyboard users who cannot click outside to close.
How to fix: Provide at least one clear way to close modals (close button, escape key, cancel button).

---

ID: ErrModalWithoutEscape
Type: Error
Impact: High
WCAG: 2.1.2 No Keyboard Trap (Level A)
Description: Modal cannot be closed using the Escape key
Why it matters: Escape key is the expected keyboard shortcut for closing modals; without it, keyboard users may become trapped.
Who it affects: Keyboard users who expect standard modal behavior, power users who rely on keyboard shortcuts.
How to fix: Implement Escape key handler to close modals, ensure it works even when focus is within modal content.

---

ID: WarnMissingAriaModal
Type: Warning
Impact: Medium
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Modal dialog missing aria-modal="true"
Why it matters: Without aria-modal, screen readers may not properly constrain navigation to the modal.
Who it affects: Screen reader users who may navigate outside the modal accidentally.
How to fix: Add aria-modal="true" to modal containers along with proper focus management.

---

ID: WarnModalMissingAriaModal
Type: Warning
Impact: Medium
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Modal dialog missing aria-modal attribute
Why it matters: aria-modal helps assistive technologies understand modal boundaries.
Who it affects: Screen reader users navigating modal content.
How to fix: Add aria-modal="true" to modal containers.

---

### Documents

ID: ErrMissingDocumentType
Type: Error
Impact: Medium
WCAG: 4.1.1 Parsing (Level A)
Description: HTML document missing DOCTYPE declaration
Why it matters: Missing DOCTYPE can cause browsers to render in quirks mode, leading to unpredictable behavior and accessibility issues.
Who it affects: All users due to potential rendering issues, assistive technology users affected by parsing errors.
How to fix: Add <!DOCTYPE html> as the first line of all HTML documents.

---

ID: WarnMissingDocumentMetadata
Type: Warning
Impact: Low
WCAG: 2.4.2 Page Titled (Level A)
Description: Document links missing metadata about file type or size
Why it matters: Users need to know document details before downloading.
Who it affects: Users on slow connections, mobile users with data limits.
How to fix: Include file type and size in link text or adjacent text.

---

### Event Handling

ID: ErrMouseOnlyHandler
Type: Error
Impact: High
WCAG: 2.1.1 Keyboard (Level A)
Description: Interactive functionality only available through mouse events
Why it matters: Mouse-only interactions exclude users who cannot use a pointing device.
Who it affects: Keyboard users, screen reader users, users with motor disabilities, mobile device users.
How to fix: Provide keyboard equivalents for all mouse interactions, use click events that work with keyboard, add proper keyboard event handlers.

---

### Forms

ID:  AI_WarnModalMissingLabel
Type: Warning
Impact: High
WCAG: 4.1.2
Category: modals
Description: Modal dialog lacks accessible name or description
Why it matters: Screen readers won't announce what the dialog is for
Who it affects: Screen reader users
How to fix: Add aria-label or aria-labelledby to the dialog element
```

### Language Issues

```

---

ID:  DiscoFormOnPage
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

---

ID:  DiscoFormPage
Type: Discovery
Impact: N/A
WCAG: N/A
Category: forms
Description: Page contains forms - needs comprehensive accessibility review
Why it matters: Forms are critical interaction points requiring thorough testing
Who it affects: All users with disabilities
How to fix: Manually test all forms with keyboard and screen reader
```

```

---

ID:  ErrAriaLabelMayNotBeFoundByVoiceControl
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

---

ID:  ErrBannerLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Banner landmark has both aria-label and aria-labelledby
Why it matters: Conflicting labeling methods
Who it affects: Screen reader users
How to fix: Use only one labeling method
```

```

---

ID:  ErrComplementaryLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Complementary landmark has both aria-label and aria-labelledby
Why it matters: Conflicting labeling methods may cause confusion
Who it affects: Screen reader users
How to fix: Use only one labeling method
```

```

---

ID:  ErrContentInfoLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Contentinfo landmark has both aria-label and aria-labelledby
Why it matters: Conflicting labeling methods
Who it affects: Screen reader users
How to fix: Use only one labeling method
```

```

---

ID:  ErrDuplicateLabelForBannerLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple banner landmarks have the same label
Why it matters: Users cannot distinguish between different banners
Who it affects: Screen reader users
How to fix: Only one banner should typically exist per page
```

```

---

ID:  ErrDuplicateLabelForComplementaryLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple complementary landmarks have the same label
Why it matters: Users cannot distinguish between different complementary sections
Who it affects: Screen reader users
How to fix: Provide unique labels for each complementary landmark
```

```

---

ID:  ErrDuplicateLabelForContentinfoLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple contentinfo landmarks have the same label
Why it matters: Users cannot distinguish between different footer areas
Who it affects: Screen reader users
How to fix: Typically only one contentinfo should exist per page
```

```

---

ID:  ErrDuplicateLabelForFormLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple form landmarks have the same label
Why it matters: Users cannot distinguish between different forms
Who it affects: Screen reader users
How to fix: Provide unique labels for each form
```

```

---

ID:  ErrDuplicateLabelForNavLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple navigation landmarks have the same label
Why it matters: Users cannot distinguish between different navigation areas
Who it affects: Screen reader users
How to fix: Provide unique labels like "Main navigation" and "Footer navigation"
```

```

---

ID:  ErrDuplicateLabelForRegionLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple region landmarks have the same label
Why it matters: Users cannot distinguish between different regions
Who it affects: Screen reader users
How to fix: Provide unique labels for each region
```

```

---

ID:  ErrDuplicateLabelForSearchLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple search landmarks have the same label
Why it matters: Users cannot distinguish between different search areas
Who it affects: Screen reader users
How to fix: Provide unique labels for each search landmark
```

#### General Landmark Issues
```

---

ID:  ErrEmptyAriaLabelOnField
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

---

ID:  ErrEmptyAriaLabelledByOnField
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

---

ID: ErrEmptyLabel
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships (Level A), 3.3.2 Labels or Instructions (Level A)
Description: Label element exists but contains no text
Why it matters: Empty labels provide no information about the associated form control, making forms impossible to complete correctly.
Who it affects: Screen reader users who cannot identify form fields, users with cognitive disabilities who need clear labels.
How to fix: Add descriptive text to all label elements that clearly identifies the purpose of the associated form control.

---

ID:  ErrFielLabelledBySomethingNotALabel
Type: Error  
Impact: Medium
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Field is labeled by an element that is not a proper label
Why it matters: Non-label elements may not provide appropriate semantic relationships
Who it affects: Screen reader users
How to fix: Use proper <label> elements or appropriate ARIA labeling
```

```

---

ID:  ErrFieldAriaRefDoesNotExist
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: forms
Description: aria-labelledby references non-existent element ID '{found}'
Why it matters: The aria-labelledby attribute references '{found}' but no element with id="{found}" exists on the page. This broken reference means the field has no accessible label for screen readers.
Who it affects: Screen reader users who receive no label for this field
How to fix: Either create an element with id="{found}" to serve as the label, fix the ID reference to point to an existing element, or use a different labeling method like a <label> element
```

```

---

ID:  ErrFieldLabelledUsinAriaLabel
Type: Error
Impact: Medium
WCAG: 3.3.2
Category: forms
Description: Field labeled using aria-label instead of visible label
Why it matters: Visible labels benefit all users, not just screen reader users
Who it affects: Users with cognitive disabilities, all users
How to fix: Use visible <label> elements instead of aria-label when possible
```

```

---

ID:  ErrFieldReferenceDoesNotExist
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

---

ID:  ErrFormAriaLabelledByIsBlank
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: landmarks
Description: Form aria-labelledby references blank or empty element
Why it matters: No accessible name is provided
Who it affects: Screen reader users
How to fix: Reference element with actual text content
```

```

---

ID:  ErrFormAriaLabelledByReferenceDIsHidden
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: landmarks
Description: Form aria-labelledby references hidden element
Why it matters: Hidden elements may not provide accessible names
Who it affects: Screen reader users
How to fix: Reference visible elements only
```

```

---

ID:  ErrFormAriaLabelledByReferenceDoesNotExist
Type: Error
Impact: High
WCAG: 1.3.1, 4.1.2
Category: landmarks
Description: Form aria-labelledby references non-existent element
Why it matters: Broken reference provides no accessible name
Who it affects: Screen reader users
How to fix: Fix ID reference or use different labeling method
```

```

---

ID:  ErrFormEmptyHasNoChildNodes
Type: Error
Impact: High
WCAG: 1.3.1
Category: forms
Description: Form element is completely empty with no child nodes
Why it matters: Empty forms serve no purpose and confuse assistive technology users
Who it affects: Screen reader users, keyboard users
How to fix: Remove empty form elements or add appropriate form controls
```

```

---

ID:  ErrFormEmptyHasNoInteractiveElements
Type: Error
Impact: High
WCAG: 1.3.1
Category: forms
Description: Form has content but no interactive elements
Why it matters: Forms without inputs cannot be used for their intended purpose
Who it affects: All users
How to fix: Add appropriate input fields, buttons, or other form controls
```

```

---

ID:  ErrFormLandmarkAccessibleNameIsBlank
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Form landmark has blank accessible name
Why it matters: Forms need clear identification
Who it affects: Screen reader users
How to fix: Add meaningful label describing form purpose
```

```

---

ID:  ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Form landmark has both aria-label and aria-labelledby
Why it matters: Conflicting labeling methods
Who it affects: Screen reader users
How to fix: Use only one labeling method
```

```

---

ID:  ErrFormUsesAriaLabelInsteadOfVisibleElement
Type: Error
Impact: Medium
WCAG: 2.5.3, 3.3.2
Category: landmarks
Description: Form uses aria-label instead of visible heading or label
Why it matters: Visible labels benefit all users
Who it affects: All users, especially those with cognitive disabilities
How to fix: Use visible heading with aria-labelledby
```

```

---

ID:  ErrFormUsesTitleAttribute
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Form uses title attribute for labeling
Why it matters: Title attributes are not reliably accessible
Who it affects: Screen reader users, mobile users
How to fix: Use aria-label or aria-labelledby instead
```

```

---

ID:  ErrIncorrectlyFormattedPrimaryLang
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

---

ID:  ErrLabelContainsMultipleFields
Type: Error
Impact: Medium
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Single label contains {count} form fields
Why it matters: A label containing {count} fields creates ambiguity about which field it describes. Screen readers will associate this label with all {count} fields, making it unclear which field is which.
Who it affects: Screen reader users who need clear field identification, users with cognitive disabilities who need simple relationships
How to fix: Split the label so each of the {count} fields has its own dedicated label. Use fieldset and legend for grouped fields if they're related.
```

```

---

ID:  ErrLabelMismatchOfAccessibleNameAndLabelText
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

---

ID:  ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Main landmark has both aria-label and aria-labelledby attributes
Why it matters: Conflicting labeling methods may cause confusion
Who it affects: Screen reader users
How to fix: Use only one labeling method - either aria-label or aria-labelledby
```

```

---

ID:  ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Navigation landmark has both aria-label and aria-labelledby
Why it matters: Conflicting labeling methods
Who it affects: Screen reader users
How to fix: Use only one labeling method
```

```

---

ID: ErrNoLabel
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships (Level A), 3.3.2 Labels or Instructions (Level A)
Description: Form input has no associated label
Why it matters: Without labels, users don't know what information to enter in form fields.
Who it affects: Screen reader users who cannot identify form fields, users with cognitive disabilities.
How to fix: Add label elements with for attribute, or use aria-label/aria-labelledby for each form input.

---

ID:  ErrOrphanLabelWithNoId
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

---

ID: ErrPlaceholderAsLabel
Type: Error
Impact: High
WCAG: 3.3.2 Labels or Instructions (Level A)
Description: Placeholder attribute used as the only label for form field
Why it matters: Placeholder text disappears when users start typing, leaving no persistent label for reference.
Who it affects: Users with cognitive disabilities, users who need to review form data, screen reader users.
How to fix: Add proper label elements or aria-label, use placeholder only for supplementary hints or examples.

---

ID:  ErrRegionLandmarkHasAriaLabelAndAriaLabelledByAttrs
Type: Error
Impact: Medium
WCAG: 4.1.2
Category: landmarks
Description: Region landmark has both aria-label and aria-labelledby
Why it matters: Conflicting labeling methods
Who it affects: Screen reader users
How to fix: Use only one labeling method
```

```

---

ID:  ErrTitleAsOnlyLabel
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A), 1.3.1 Info and Relationships (Level A), 4.1.2 Name, Role, Value (Level A)
Category: title
Description: Form element is using title attribute as its only accessible label, which is insufficient for accessibility
Why it matters: When title is the only labeling mechanism for a form field, many users cannot determine what information to enter. Title attributes are not announced by screen readers when navigating forms in normal mode, don't appear on mobile devices, cannot be accessed by keyboard users, and disappear too quickly for many users to read. This makes the form field essentially unlabeled for a large portion of users, preventing them from completing forms successfully.
Who it affects: Screen reader users who won't hear the field's purpose when navigating the form, mobile users who cannot see title tooltips at all, keyboard users who cannot hover to see the tooltip, users with motor disabilities who struggle with precise hovering, users with cognitive disabilities who need persistent labels as memory aids, and voice control users who cannot reference fields without visible labels
How to fix: Add a proper visible <label> element associated with the form field using the 'for' attribute. If space is limited, use placeholder text in addition to (not instead of) a label. For complex layouts, consider using aria-labelledby to reference existing visible text. If you must use aria-label, ensure it's descriptive and consider adding visible text for sighted users. Never rely solely on title attributes for labeling form fields - they should only supplement proper labels, not replace them.
```

```

---

ID:  ErrUnlabelledField
Type: Error
Impact: High
WCAG: 3.3.2 Labels or Instructions (Level A), 4.1.2 Name, Role, Value (Level A)
Category: forms
Description: Form input element lacks an accessible name through <label>, aria-label, aria-labelledby, or other labeling methods, leaving the field's purpose undefined for assistive technologies
Why it matters: Without labels, users cannot determine what information to enter, leading to form errors, abandoned transactions, and inability to complete critical tasks. Screen readers announce only the field type like "edit" or "combo box" without context, forcing users to guess based on surrounding content that may not be programmatically associated. This creates barriers for independent form completion and may result in users submitting incorrect information or being unable to proceed.
Who it affects: Blind and low vision users using screen readers who hear no field description when navigating forms, users with cognitive disabilities who need clear labels to understand what information is required, users with motor disabilities using voice control who cannot reference unlabeled fields by name, mobile users where placeholder text may disappear on focus, and users who rely on browser autofill features that depend on proper field labeling
How to fix: Add explicit <label> elements with for attribute matching the input's id (preferred method), use aria-label for simple labels when visual text isn't needed, implement aria-labelledby to reference existing visible text, ensure placeholder text is not the only labeling method as it disappears on input, wrap inputs and label text together for implicit association, and verify all form controls including select elements, textareas, and custom widgets have accessible names
```

```

---

ID:  InfoFieldLabelledUsingAriaLabel
Type: Info
Impact: N/A
WCAG: 3.3.2 Labels or Instructions (Level A)
Category: forms
Description: Field is labeled using aria-label="{found}", which is valid but may have usability considerations
Why it matters: While aria-label="{found}" is a valid way to label this form field, it has limitations: the label "{found}" is not visible on screen which can confuse sighted users, voice control users cannot reference the field by the visible text "{found}", the label won't be automatically translated by browser translation tools, and users with cognitive disabilities benefit from visible labels as memory aids.
Who it affects: Sighted users who can't see "{found}" as a label, voice control users who can't say "click {found}", users relying on browser translation, users with cognitive disabilities who benefit from persistent visible labels
How to fix: Consider if a visible label showing "{found}" would better serve all users. If space permits, use a visible <label> element with the text "{found}". If aria-label must be used, ensure "{found}" is clear and descriptive. Consider adding visible helper text or placeholder text to provide visual context.
```

---

## 3. HEADINGS

### 3.1 Missing Headings
```

---

ID:  WarnComplementaryLandmarkHasNoLabel
Type: Warning
Impact: Low
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Complementary landmark lacks a label
Why it matters: Hard to distinguish multiple complementary sections
Who it affects: Screen reader users
How to fix: Add aria-label or aria-labelledby to identify the purpose
```

```

---

ID:  WarnContentInfoLandmarkHasNoLabel
Type: Warning
Impact: Low
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Contentinfo landmark lacks a label
Why it matters: May be harder to identify purpose
Who it affects: Screen reader users
How to fix: Add descriptive label if multiple contentinfo exist
```

```

---

ID:  WarnFieldLabelledByElementThatIsNotALabel
Type: Warning
Impact: Medium
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Field labeled by element '{found}' that is not semantically a label
Why it matters: The element with ID '{found}' is being used as a label but is not a <label> element. While this can work, non-label elements may not convey proper semantic meaning or behave as users expect.
Who it affects: Screen reader users who may not receive proper label semantics
How to fix: Consider using a proper <label> element, or ensure the element '{found}' contains appropriate descriptive text for the field
```

```

---

ID:  WarnFieldLabelledByMultipleElements
Type: Warning
Impact: Low
WCAG: 3.3.2
Category: forms
Description: Field is labeled by {count} elements via aria-labelledby
Why it matters: When {count} elements label a field, they will be concatenated together. The order and combination may not make sense or could be confusing when read as a single label.
Who it affects: Screen reader users who hear all {count} labels concatenated together
How to fix: Review the {count} labeling elements to ensure they make sense when read together in order. Consider if a single, clear label would be better.
```

```

---

ID:  WarnFormHasNoLabel
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships, 2.4.6 Headings and Labels
Category: forms
Description: Form element has no accessible name to describe its purpose
Why it matters: When a form lacks an accessible name, screen reader users hear only "form" without knowing what the form does - is it a search form, login form, contact form, or something else? Users navigating by landmarks or forms need to understand each form's purpose to decide whether to interact with it. This is especially important on pages with multiple forms. Without proper labeling, users might fill out the wrong form, skip important forms, or waste time exploring forms to understand their purpose.
Who it affects: Screen reader users navigating by forms or landmarks who need to identify form purposes, users with cognitive disabilities who need clear labels to understand what each form does, and keyboard users who tab through forms and need context about what they're interacting with
How to fix: Add an accessible name to the form element using aria-label (e.g., aria-label="Contact form") or aria-labelledby to reference a visible heading. If the form has a visible heading immediately before it, use aria-labelledby to point to that heading's ID. For search forms, "Search" is usually sufficient. The label should clearly indicate the form's purpose and be unique if there are multiple forms on the page.
```

```

---

ID:  WarnFormHasNoLabelSoIsNotLandmark
Type: Warning
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Form element lacks label so is not exposed as landmark
Why it matters: Forms without accessible names are not landmarks
Who it affects: Screen reader users navigating by landmarks
How to fix: Add aria-label or aria-labelledby to make it a landmark
```

```

---

ID:  WarnFormLandmarkAccessibleNameUsesForm
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: landmarks
Description: Form landmark uses generic term "form" in label
Why it matters: Generic labels don't describe purpose
Who it affects: Screen reader users
How to fix: Use descriptive labels like "Contact form" or "Search form"
```

#### Search Landmark Issues
```

---

ID: WarnMissingAriaLabelledby
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Form field could benefit from aria-labelledby for complex labeling
Why it matters: Complex forms may need multiple labels or descriptions for clarity.
Who it affects: Screen reader users needing additional context.
How to fix: Use aria-labelledby to associate multiple labels or aria-describedby for help text.

---

ID: WarnModalMissingAriaLabelledby
Type: Warning
Impact: Medium
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Modal lacks aria-labelledby pointing to its heading
Why it matters: Screen readers need to announce the modal's title when it opens.
Who it affects: Screen reader users who need modal context.
How to fix: Add aria-labelledby pointing to the modal's heading element.

---

ID:  WarnMultipleBannerLandmarksButNotAllHaveLabels
Type: Warning
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple banner landmarks exist but not all have labels
Why it matters: Inconsistent labeling makes navigation difficult
Who it affects: Screen reader users
How to fix: Ensure all banner landmarks have labels or reduce to single banner
```

#### Content Info Landmark Issues
```

---

ID:  WarnMultipleComplementaryLandmarksButNotAllHaveLabels
Type: Warning
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple complementary landmarks but not all labeled
Why it matters: Inconsistent labeling makes navigation difficult
Who it affects: Screen reader users
How to fix: Ensure all complementary landmarks have unique labels
```

```

---

ID:  WarnMultipleContentInfoLandmarksButNotAllHaveLabels
Type: Warning
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple contentinfo landmarks exist but not all have labels
Why it matters: Inconsistent labeling makes navigation difficult
Who it affects: Screen reader users
How to fix: Ensure all contentinfo landmarks have labels or reduce to single contentinfo
```

#### Form Landmark Issues
```

---

ID:  WarnMultipleNavLandmarksButNotAllHaveLabels
Type: Warning
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple navigation landmarks but not all labeled
Why it matters: Users cannot distinguish between navigation areas
Who it affects: Screen reader users
How to fix: Label all navigation landmarks uniquely
```

```

---

ID:  WarnMultipleNavNeedsLabel
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Category: landmarks
Description: Multiple navigation landmarks found without distinguishing labels
Why it matters: When a page has multiple navigation areas (main menu, footer links, breadcrumbs, sidebar navigation), users need to distinguish between them. Without unique labels, screen reader users hear "navigation" multiple times with no indication of which navigation area they're entering. This creates confusion about which menu contains the desired links and requires users to explore each navigation to understand its purpose.
Who it affects: Screen reader users who need to distinguish between different navigation areas, keyboard users navigating between multiple menus, users with cognitive disabilities who need clear labeling, and frequent users who want to quickly access specific navigation areas
How to fix: Add unique aria-label attributes to each <nav> element or role="navigation" container. Use descriptive labels like aria-label="Main menu", aria-label="Footer links", aria-label="Breadcrumb", aria-label="Related articles". The labels should clearly indicate the purpose or location of each navigation. Test with screen readers to ensure each navigation is announced with its unique label.
```

### 4.4 Landmark Nesting
```

---

ID:  WarnMultipleRegionLandmarksButNotAllHaveLabels
Type: Warning
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Multiple region landmarks but not all labeled
Why it matters: Regions without labels are not exposed as landmarks
Who it affects: Screen reader users
How to fix: Ensure all regions have labels or use different elements
```

---

## 5. COLOR & CONTRAST

### 5.1 Contrast Errors - Level AA
```

---

ID:  WarnNavLandmarkHasNoLabel
Type: Warning
Impact: Low
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Navigation landmark lacks label
Why it matters: Hard to distinguish multiple navigation areas
Who it affects: Screen reader users
How to fix: Add descriptive aria-label
```

```

---

ID: WarnNoFieldset
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Related form fields not grouped with fieldset
Why it matters: Fieldsets help users understand relationships between form controls.
Who it affects: Screen reader users, users with cognitive disabilities.
How to fix: Use fieldset and legend elements to group related form fields like radio buttons.

---

ID:  WarnRegionLandmarkHasNoLabelSoIsNotConsideredALandmark
Type: Warning
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Region landmark lacks required label to be considered a landmark
Why it matters: Regions without labels are not exposed as landmarks
Who it affects: Screen reader users
How to fix: Add aria-label or aria-labelledby, or use a different landmark type
```

```

---

ID: WarnUnlabelledForm
Type: Warning
Impact: Medium
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Form element lacks accessible name
Why it matters: Forms need names to help users understand their purpose.
Who it affects: Screen reader users.
How to fix: Add aria-label or aria-labelledby to form elements.

---

ID: WarnUnlabelledRegion
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Region landmark lacks accessible name
Why it matters: Named regions help users understand content structure.
Who it affects: Screen reader users navigating by landmarks.
How to fix: Add aria-label or aria-labelledby to region landmarks.

---

ID:  forms_DiscoNoSubmitButton
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

---

ID:  forms_DiscoPlaceholderAsLabel
Type: Discovery
Impact: N/A
WCAG: 3.3.2
Category: forms
Description: Placeholder may be used instead of label
Why it matters: Placeholder text disappears when typing
Who it affects: Users with memory/cognitive issues, screen reader users
How to fix: Use proper labels, placeholder for examples only
```

### 2.6 Additional Form Issues

```

---

ID:  forms_ErrInputMissingLabel
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

---

ID:  forms_ErrNoButtonText
Type: Error
Impact: High
WCAG: 2.4.6, 4.1.2
Category: forms
Description: Button has no accessible text
Why it matters: Users cannot determine button purpose
Who it affects: Screen reader users, voice control users
How to fix: Add text content, aria-label, or aria-labelledby to button
```

### 2.8 Field Labeling Info
```

---

ID:  forms_WarnGenericButtonText
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: forms
Description: Button has generic text "{text}"
Why it matters: The button text "{text}" doesn't describe what the button does. When screen reader users navigate by buttons or hear buttons out of context, "{text}" provides no information about the button's purpose or action.
Who it affects: Screen reader users navigating by buttons who hear "{text}" without context, users with cognitive disabilities who need clear action labels
How to fix: Change "{text}" to describe the specific action, like "Submit registration", "Save changes", or "Search products" instead of just "{text}"
```

```

---

ID:  forms_WarnNoFieldset
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

---

ID:  forms_WarnRequiredNotIndicated
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

---

### General

ID:  AI_InfoVisualCue
Type: Info
Impact: Low
WCAG: 1.3.3, 1.4.1
Category: visual
Description: Information conveyed only through visual cues (color, position, size)
Why it matters: Users who can't perceive visual cues miss important information
Who it affects: Blind users, colorblind users
How to fix: Provide text alternatives or additional cues beyond just visual ones
```

### Missing Interactive Element Issues

```

---

ID:  DiscoFoundJS
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

## 11. BUTTONS

### 11.1 Button Contrast Issues
```

---

ID:  DiscoStyleAttrOnElements
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

---

ID:  DiscoStyleElementOnPage
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

---

ID: ErrContentObscuring
Type: Error  
Impact: High
WCAG: 2.4.3 Focus Order (Level A), 2.1.2 No Keyboard Trap (Level A)
Description: Content is obscured by other elements preventing interaction
Why it matters: When content is covered by other elements, users cannot access or interact with it, creating complete barriers to functionality.
Who it affects: All users, particularly keyboard users who cannot use mouse to work around layout issues, screen reader users who may not know content is obscured.
How to fix: Fix z-index and positioning issues, ensure modals and overlays don't cover content inappropriately, test that all content remains accessible.

---

ID:  ErrEmptyPageTitle
Type: Error
Impact: High
WCAG: 2.4.2
Category: page
Description: Page title element is empty
Why it matters: Empty titles provide no information about page content
Who it affects: Screen reader users, users with cognitive disabilities
How to fix: Add descriptive text to title element
```

```

---

ID:  ErrEmptyTitleAttr
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

---

ID: ErrImproperTitleAttribute
Type: Error
Impact: Low
WCAG: 3.3.2 Labels or Instructions (Level A)
Description: Title attribute used improperly as primary labeling mechanism
Why it matters: Title attributes are not reliably announced by all assistive technologies and should not be the only way to provide essential information.
Who it affects: Screen reader users who may not receive title attribute content, mobile users who cannot hover to see tooltips.
How to fix: Use proper labeling techniques (label elements, aria-label) instead of relying on title attributes for essential information.

---

ID:  ErrMultiplePageTitles
Type: Error
Impact: Low
WCAG: 2.4.2
Category: page
Description: Multiple title elements found in document
Why it matters: Multiple titles may confuse assistive technologies
Who it affects: Screen reader users
How to fix: Use only one title element per page
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

---

ID:  ErrNoOutlineOffsetDefined
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

---

ID:  ErrNoPageTitle
Type: Error
Impact: High
WCAG: 2.4.2 Page Titled
Category: page
Description: Page has no <title> element in the document head
Why it matters: The page title is the first thing screen reader users hear when a page loads, and it appears in browser tabs, bookmarks, and search results. Without a title, users cannot identify the page in their browser history, distinguish between multiple open tabs, or understand what page they're on when arriving from a link. Screen reader users announcing "Untitled document" have no context about where they are. This is like opening a book with no title on the cover or spine - you don't know what you're reading until you dive into the content. The title is critical for orientation and navigation.
Who it affects: Screen reader users who rely on titles for page identification and orientation, users with cognitive disabilities who need clear page identification, users managing multiple browser tabs who need to distinguish between pages, users with memory issues using browser history to return to pages, and all users when bookmarking or sharing pages
How to fix: Add a <title> element within the <head> section of your HTML. Create descriptive, unique titles that identify both the page content and the site. Use a consistent pattern like "Page Topic - Site Name". Put the unique page information first since it's most important. Keep titles concise (under 60 characters) but descriptive. Avoid generic titles like "Home" or "Page 1". The title should make sense when read out of context in a list of bookmarks or search results.
```

```

---

ID:  ErrOutlineIsNoneOnInteractiveElement
Type: Error
Impact: High
WCAG: 2.4.7 Focus Visible
Category: focus
Description: Interactive element has CSS outline:none removing the default focus indicator
Why it matters: People with mobility disabilities use keyboard or keyboard-alternate devices to navigate rather than a mouse. Visible focus indicators are essential as they perform the same function as a mouse cursor. Without focus indicators, users cannot tell where they are on the page or when interactive elements are focused. This makes keyboard navigation impossible and can completely prevent access to functionality.
Who it affects: Sighted users with motor disabilities navigating with keyboard or keyboard-alternate devices, users who prefer keyboard navigation for efficiency, users with temporary injuries preventing mouse use, and users of assistive technologies that rely on keyboard navigation
How to fix: Never use outline:none without providing an alternative visible focus indicator. The focus indicator must be clearly visible with at least 3:1 contrast ratio with the background, be at least 2 pixels thick, and ideally be offset from the element to maximize visibility. Consider using CSS :focus-visible for better control over when focus indicators appear.
```

```

---

ID:  ErrTitleAttrFound
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

---

ID: WarnMissingRequiredIndication
Type: Warning
Impact: Medium
WCAG: 3.3.2 Labels or Instructions (Level A)
Description: Required form fields not clearly indicated
Why it matters: Users need to know which fields are required before submitting forms.
Who it affects: All users, especially those using screen readers.
How to fix: Mark required fields with aria-required="true" and visual indicators.

---

ID:  WarnMultipleTitleElements
Type: Warning
Impact: Medium
WCAG: 2.4.2 Page Titled (Level A)
Category: title
Description: {count} <title> elements found in the document head, which may cause unpredictable behavior
Why it matters: Having {count} title elements causes browsers to choose unpredictably between them, creating inconsistent page identification. Different browsers and assistive technologies may choose different titles from the {count} available, creating an inconsistent experience. SEO is negatively affected as search engines may index the wrong title.
Who it affects: All users seeing inconsistent titles in browser tabs, screen reader users who may hear different titles than what's visually displayed, users bookmarking pages with incorrect titles
How to fix: Remove {count-1} duplicate <title> elements, keeping only one in the document head. Check for scripts that might be adding titles dynamically. Ensure your CMS or framework isn't creating duplicate titles.
```

```

---

ID: WarnNoCurrentPageIndicator
Type: Warning
Impact: Low
WCAG: 2.4.8 Location (Level AAA)
Description: Navigation doesn't indicate current page
Why it matters: Users need to know their current location within the site navigation.
Who it affects: Users with cognitive disabilities, screen reader users.
How to fix: Use aria-current="page" and visual styling to indicate current page in navigation.

---

ID: WarnNoCursorPointer
Type: Warning
Impact: Low
WCAG: 2.1.1 Keyboard (Level A)
Description: Clickable element doesn't show pointer cursor
Why it matters: Cursor changes help users identify interactive elements.
Who it affects: Mouse users who rely on cursor changes.
How to fix: Add cursor: pointer CSS to all clickable elements.

---

ID: WarnNoLegend
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Fieldset missing legend element
Why it matters: Legends provide context for grouped form fields.
Who it affects: Screen reader users who need group labels.
How to fix: Add legend as first child of fieldset to label the group.

---

ID:  WarnPageTitleTooLong
Type: Warning
Impact: Low
WCAG: 2.4.2 Page Titled (Level A)
Category: title
Description: Page title is {length} characters long, exceeding the recommended 60 character limit
Why it matters: The title "{title}" with {length} characters will get cut off in browser tabs (typically around 30 characters) and search engine results (typically 50-60 characters), losing important information. The most important information might be at the end and never seen. Screen reader users have to listen to lengthy titles repeatedly.
Who it affects: Users with multiple tabs open who see truncated titles, users searching for content who can't see full titles in results, screen reader users who must listen to long titles repeatedly, mobile users with even less space for title display
How to fix: Shorten the title from {length} to under 60 characters. Place the most important, unique information first. Remove unnecessary words like "Welcome to" or "This page contains". Test how titles appear in browser tabs and search results to ensure key information is visible.
```

```

---

ID:  WarnPageTitleTooShort
Type: Warning
Impact: Low
WCAG: 2.4.2 Page Titled (Level A)
Category: title
Description: Page title "{found}" is only {length} characters, potentially not descriptive enough
Why it matters: The title "{found}" with only {length} characters doesn't provide enough context, especially when users have multiple tabs open or are browsing history. Users can't distinguish between different sites with the same generic titles. Screen reader users hearing page titles announced need more descriptive information to understand where they are.
Who it affects: Users with multiple browser tabs who need to distinguish between pages, screen reader users who rely on descriptive titles for context, users browsing history or bookmarks, users with cognitive disabilities who need clear page identification
How to fix: Expand "{found}" to be more descriptive by including the site name and page purpose. Aim for 20-60 characters that clearly describe the page content. Ensure each page has a unique, descriptive title that makes sense out of context.
```

```

---

ID:  WarnTitleAttrFound
Type: Warning
Impact: Low
WCAG: 3.3.2 Labels or Instructions (Level A), 4.1.2 Name, Role, Value (Level A)
Category: title
Description: Title attribute is being used on an element, which has significant accessibility limitations
Why it matters: Title attributes are problematic for accessibility: they don't appear on mobile devices or touch screens, keyboard users cannot access them without a mouse, screen readers handle them inconsistently (some ignore them, some read them), they disappear quickly making them hard to read for users with motor or cognitive disabilities, they cannot be styled or resized for users with low vision, and they're not translated by browser translation tools. Using title attributes for important information excludes many users from accessing that content.
Who it affects: Mobile and touch screen users who never see title tooltips, keyboard-only users who cannot hover to trigger tooltips, screen reader users who may not hear title content reliably, users with motor disabilities who cannot hover precisely, users with cognitive disabilities who need more time to read, users with low vision who cannot resize tooltip text, and users relying on translation tools
How to fix: Replace title attributes with visible, persistent text that all users can access. For form fields, use visible <label> elements or aria-label. For links and buttons, ensure the visible text is descriptive. For abbreviations, provide the full text on first use. For supplementary information, use visible helper text, details/summary elements, or clickable info icons. Only use title attributes for progressive enhancement where the information duplicates visible content. Never rely on title alone for important information.
```

```

---

ID: WarnVagueTitleAttribute
Type: Warning
Impact: Low
WCAG: 3.3.2 Labels or Instructions (Level A)
Description: Title attribute contains vague or redundant information
Why it matters: Vague titles don't provide useful supplementary information.
Who it affects: Users who rely on tooltips for additional context.
How to fix: Make title attributes informative or remove if redundant with visible text.

---

ID:  WarnZeroOutlineOffset
Type: Warning
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

---

ID:  [Issue identifier from code]
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

---

### Headings

ID:  AI_ErrEmptyHeading
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.6
Category: headings
Description: Heading element {element_tag} at level {heading_level} is empty or contains no text
Why it matters: Empty headings break document structure and confuse screen reader users who navigate by headings
Who it affects: Screen reader users, users who navigate by headings
How to fix: Remove empty heading or add meaningful text content
```

```

---

ID:  AI_ErrHeadingLevelMismatch
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.1
Category: headings
Description: Heading level {current_level} doesn't match visual hierarchy (should be level {suggested_level})
Why it matters: Incorrect heading levels create confusing document structure for screen reader users
Who it affects: Screen reader users, users who navigate by headings
How to fix: Adjust heading level to match the visual hierarchy of the page
```

### Interactive Element Issues

```

---

ID:  AI_ErrSkippedHeading
Type: Error
Impact: High
WCAG: 1.3.1
Category: headings
Description: Heading level skipped from h{current_level} to h{next_level}
Why it matters: Skipped heading levels break the logical document structure and make navigation difficult
Who it affects: Screen reader users, users who navigate by headings
How to fix: Use sequential heading levels without skipping (h1, h2, h3, not h1, h3)
```

---

ID:  AI_ErrVisualHeadingNotMarked
Type: Error
Impact: High
WCAG: 1.3.1, 2.4.1, 2.4.6
Category: headings
Description: Text "{visual_text}" appears visually as a heading but is not marked up with proper heading tags
Why it matters: Screen reader users won't recognize this text as a heading, breaking navigation and document structure
Who it affects: Screen reader users, users who navigate by headings
How to fix: Use appropriate HTML heading tags (h1-h6) for text that serves as headings
```

```

---

ID: DiscoHeadingWithID
Type: Discovery
Impact: N/A
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Heading element has an ID attribute that may be used for in-page navigation
Why it matters: Headings with IDs are often link targets for navigation, requiring verification that they work correctly and provide meaningful navigation points.
Who it affects: All users who use in-page navigation links, screen reader users who navigate by headings, keyboard users who follow fragment links.
How to fix: Verify the heading ID is referenced by navigation links, ensure the ID is descriptive and stable, check that the heading text provides clear navigation context.

---

ID:  ErrEmptyHeading
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships, 2.4.6 Headings and Labels
Category: headings
Description: Heading element contains only whitespace or special characters: "{text}"
Why it matters: This heading contains only "{text}" which provides no meaningful content. Empty headings disrupt document structure and navigation. Screen reader users rely on headings to understand page organization and navigate efficiently using heading shortcuts. An empty heading creates a navigation point with no information, confusing users about the page structure.
Who it affects: Screen reader users who navigate by headings and find a heading containing only "{text}", users with cognitive disabilities who rely on clear structure to understand content organization, and users of assistive technologies that generate page outlines
How to fix: Either replace "{text}" with meaningful text content that describes the section, or remove the empty heading element entirely if it serves no structural purpose. Never use headings for visual spacing - use CSS margin/padding instead.
```

### 3.3 Heading Hierarchy
```

---

ID:  ErrFormAriaLabelledByReferenceDoesNotReferenceAHeading
Type: Error
Impact: Low
WCAG: 1.3.1
Category: landmarks
Description: Form aria-labelledby doesn't reference a heading element
Why it matters: Best practice is to reference headings for form landmarks
Who it affects: Screen reader users
How to fix: Reference a heading element when possible
```

```

---

ID:  ErrFoundAriaLevelButRoleIsNotHeading
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

---

ID: ErrIncorrectHeadingLevel
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Heading level used incorrectly based on visual appearance rather than document structure
Why it matters: Incorrect heading levels break the document outline and make it difficult to understand content hierarchy.
Who it affects: Screen reader users navigating by headings, users who rely on proper document structure.
How to fix: Use heading levels to convey document structure (h1 > h2 > h3), not for visual styling; use CSS for appearance.

---

ID: ErrModalMissingHeading
Type: Error
Impact: Medium
WCAG: 2.4.6 Headings and Labels (Level AA)
Description: Modal dialog lacks a heading to identify its purpose
Why it matters: Without headings, users don't know the purpose or context of the modal content.
Who it affects: Screen reader users who need to understand modal purpose, users with cognitive disabilities.
How to fix: Add a heading (h1-h6) at the beginning of modal content that clearly identifies its purpose.

---

ID:  ErrMultipleH1
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: headings
Description: Page contains {count} h1 elements instead of just one
Why it matters: Having {count} h1 elements creates confusion about the page's main topic. Each h1 represents a primary heading, and multiple h1s suggest multiple main topics, breaking the document hierarchy. Screen readers users won't know which h1 represents the actual page topic.
Who it affects: Screen reader users who expect a single h1 to identify the page topic, users navigating by headings who see multiple "top level" items, SEO and search engines that look for a single main topic
How to fix: Keep only one h1 that represents the main page topic. Change the other {count-1} h1 elements to h2 or appropriate lower levels based on their relationship to the main topic.
```

### 3.4 ARIA Heading Issues
```

---

ID: ErrNoH1
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Page has no h1 heading
Why it matters: H1 headings identify the main topic of a page and are crucial for document structure.
Who it affects: Screen reader users who navigate by headings, users who rely on document outlines.
How to fix: Add exactly one h1 heading that describes the main content or purpose of the page.

---

ID:  ErrNoHeadingsOnPage
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships, 2.4.6 Headings and Labels
Category: headings
Description: No heading elements (h1-h6) found anywhere on the page
Why it matters: Headings create the structural outline of your content, like a table of contents. They allow users to understand how information is organized and navigate directly to sections of interest. Without any headings, screen reader users cannot use heading navigation shortcuts (one of their primary navigation methods) and must read through all content linearly. This is like forcing someone to read an entire book without chapter titles or section breaks. Users cannot skim content, jump to relevant sections, or understand the information hierarchy. For users with cognitive disabilities, the lack of visual structure makes content overwhelming and hard to process.
Who it affects: Screen reader users who lose a critical navigation method and cannot understand content structure, users with cognitive disabilities who need clear visual organization to process information, users with attention disorders who rely on headings to focus on relevant sections, and users with reading disabilities who use headings to break content into manageable chunks
How to fix: Add semantic heading elements (h1-h6) to structure your content. Start with one h1 that describes the main page topic. Use h2 for major sections, h3 for subsections, and so on. Don't skip levels (e.g., h1 to h3). Ensure headings describe the content that follows them. Never use headings just for visual styling - they must represent actual content structure. If you need large text without semantic meaning, use CSS instead.
```

```

---

ID:  ErrRoleOfHeadingButNoLevelGiven
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

---

ID:  ErrSkippedHeadingLevel
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships
Category: headings
Description: Heading levels are not in sequential order - jumped from h{skippedFrom} to h{skippedTo}, skipping intermediate level(s)
Why it matters: Heading levels create a hierarchical outline of your content, like nested bullet points. Jumping from h{skippedFrom} to h{skippedTo} breaks this logical structure. It's like having chapter {skippedFrom}, then jumping to section {skippedTo} without the intermediate section. Screen reader users navigating by headings will be confused about the relationship between sections - is the h{skippedTo} a subsection of something that's missing? This broken hierarchy makes it hard to understand how content is organized and can cause users to think content is missing or that they've accidentally skipped something.
Who it affects: Screen reader users navigating by heading structure who rely on levels to understand content relationships, users with cognitive disabilities who need logical, predictable content organization, users of assistive technology that generates document outlines, and developers or content authors maintaining the page who need to understand the intended structure
How to fix: Insert an h{expectedLevel} heading between the h{skippedFrom} and h{skippedTo}, or change the h{skippedTo} to h{expectedLevel} to maintain sequential order. After h{skippedFrom}, use h{expectedLevel} for the next level. Don't skip levels when going down the hierarchy. If you need a heading to look smaller visually, use CSS to style it rather than choosing a lower heading level. The heading level should reflect the content's logical structure, not its visual appearance.
```

```

---

ID: InfoHeadingNearLengthLimit
Type: Info
Impact: Low
WCAG: 2.4.6 Headings and Labels (Level AA)
Description: Heading approaching recommended length limit
Why it matters: Very long headings are difficult to scan and understand quickly.
Who it affects: Users with cognitive disabilities, users scanning content.
How to fix: Consider shortening headings to be more concise while maintaining clarity.

---

ID:  VisibleHeadingDoesNotMatchA11yName
Type: Warning
Impact: Medium
WCAG: 2.5.3
Category: headings
Description: Visible heading text doesn't match its accessible name
Why it matters: Voice control users may not be able to reference the heading by its visible text
Who it affects: Voice control users, screen reader users
How to fix: Ensure visible text matches or is contained within the accessible name
```

---

## 4. LANDMARKS

### 4.1 Missing Landmarks
```

---

ID:  WarnHeadingFoundInLandmarkButIsLabelledByAnAriaLabelledBy
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Landmark has heading but uses different element for label
Why it matters: Confusing when heading doesn't match landmark label
Who it affects: Screen reader users
How to fix: Use the heading as the landmark label
```

#### Multiple Landmark Warnings
```

---

ID:  WarnHeadingFoundInsideLandmarkButDoesntLabelLandmark
Type: Warning
Impact: Low
WCAG: 1.3.1
Category: landmarks
Description: Heading inside landmark doesn't label the landmark
Why it matters: Missed opportunity for clear landmark labeling
Who it affects: Screen reader users
How to fix: Consider using heading as landmark label via aria-labelledby
```

```

---

ID:  WarnHeadingInsideDisplayNone
Type: Warning
Impact: Low
WCAG: 1.3.1
Category: headings
Description: Heading is hidden with display:none
Why it matters: Hidden headings may affect document structure
Who it affects: Screen reader users (varies by implementation)
How to fix: Remove unused headings or make them visible
```

```

---

ID:  WarnHeadingOver60CharsLong
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: headings
Description: Heading text is {length} characters long: "{headingText}"
Why it matters: This heading has {length} characters. Long headings are harder to scan quickly, more difficult to understand at a glance, and can overwhelm users. Screen reader users hearing the full heading text may struggle to grasp the main point. Long headings also cause layout issues on mobile devices and in navigation menus.
Who it affects: Users with cognitive disabilities who benefit from concise, clear headings, screen reader users who must listen to the entire heading, users scanning the page quickly for information, and mobile users with limited screen space
How to fix: Shorten the heading to under 60 characters while preserving its meaning. Current: "{headingText}" - Consider breaking into a shorter heading with explanatory text below, or focus on the key message. Use descriptive but concise language.
```

```

---

ID:  WarnNoH1
Type: Warning
Impact: High
WCAG: 1.3.1 Info and Relationships, 2.4.6 Headings and Labels
Category: headings
Description: Page is missing an h1 element to identify the main topic
Why it matters: The h1 is the most important heading on a page - it tells users what the page is about, similar to a chapter title in a book. Screen reader users often navigate directly to the h1 first to understand the page purpose. Without it, users must guess the page topic from other cues like the title or URL. The h1 also establishes the starting point for the heading hierarchy. Search engines use the h1 to understand page content, and browser extensions that generate page outlines will be missing the top level. Think of the h1 as answering "What is this page about?" - without it, users lack this fundamental context.
Who it affects: Screen reader users who jump to the h1 to understand page purpose, users with cognitive disabilities who need clear indication of page topic, SEO and users finding your content through search engines, users of browser tools that generate page outlines or tables of contents
How to fix: Add exactly one h1 element that describes the main topic or purpose of the page. It should be unique to that page (not the same site-wide). Place it at the beginning of your main content, typically inside the main landmark. The h1 text should make sense if read in isolation and match user expectations based on how they arrived at the page. Don't use the site name as the h1 - use the specific page topic.
```

### 3.2 Empty Headings
```

---

### Iframes

ID:  ErrIframeWithNoTitleAttr
Type: Error
Impact: High
WCAG: 2.4.1 Bypass Blocks, 4.1.2 Name, Role, Value
Category: title
Description: Iframe element is missing the required title attribute
Why it matters: Iframes embed external content like videos, maps, or forms within your page. Without a title attribute, screen reader users hear only "iframe" with no indication of what content it contains. This is like having a door with no label - users don't know what's behind it. They must enter the iframe and explore its content to understand its purpose, which is time-consuming and may be confusing if the iframe content lacks context. For pages with multiple iframes, users cannot distinguish between them or decide which ones are worth exploring.
Who it affects: Screen reader users who need to understand what each iframe contains before deciding whether to interact with it, keyboard users navigating through iframes who need context about embedded content, users with cognitive disabilities who need clear labeling of all page regions, and users on slow connections who may experience delays loading iframe content
How to fix: Add a title attribute to every iframe that concisely describes its content or purpose (e.g., title="YouTube video: Product demonstration", title="Google Maps: Office location", title="Payment form"). The title should be unique if there are multiple iframes. Keep it brief but descriptive enough that users understand what the iframe contains without having to enter it. For decorative iframes (rare), you can use title="" and add tabindex="-1" to remove it from tab order.
```

### 9.2 Page Title Issues
```

---

ID:  WarnIframeTitleNotDescriptive
Type: Warning
Impact: Medium
WCAG: 2.4.1 Bypass Blocks (Level A), 4.1.2 Name, Role, Value (Level A)
Category: title
Description: Iframe has a title attribute but it's generic or not descriptive (e.g., "iframe", "frame", "embedded content")
Why it matters: Generic iframe titles like "iframe" or "embedded" provide no useful information about the embedded content. Screen reader users hear these unhelpful titles and must enter the iframe to understand what it contains. With multiple iframes, users cannot distinguish between them or determine which ones are worth exploring. This wastes time and creates confusion, especially if iframes contain important functionality like payment forms or videos.
Who it affects: Screen reader users trying to understand and navigate between multiple iframes, keyboard users who encounter iframes in tab order, users with cognitive disabilities who need clear labeling of all content regions, and users trying to navigate efficiently through complex pages
How to fix: Replace generic titles with descriptive ones that explain the iframe's content or purpose. Use specific descriptions like title="YouTube video: Product demo", title="Customer feedback form", title="Live chat support", or title="Interactive map of office locations". Each iframe title should be unique if there are multiple iframes. Avoid redundant words like "iframe" in the title since the element type is already announced.
```

### 9.3 ARIA Issues
```

---

### Images

ID:  DiscoFoundInlineSvg
Type: Discovery
Impact: N/A
WCAG: 1.1.1 Non-text Content (Level A)
Category: svg
Description: Inline SVG element detected that requires manual review to determine appropriate accessibility implementation based on its purpose and complexity
Why it matters: SVG elements serve diverse purposes from simple icons to complex interactive visualizations, each requiring different accessibility approaches. A decorative border needs different treatment than a data chart, which differs from an interactive map or scientific simulation. Automated tools cannot determine SVG purpose, whether it's decorative or informative, static or interactive, or if existing accessibility features adequately support user needs.
Who it affects: Blind and low vision users using screen readers who need text alternatives for graphics or keyboard access to interactive elements, users with motor disabilities who require keyboard navigation for interactive SVG controls, users with cognitive disabilities who benefit from clear labeling and predictable interaction patterns, and users of various assistive technologies that may interpret SVG content differently
How to fix: Evaluate the SVG's purpose and complexity - for simple images add <title> with aria-labelledby or role="img" with aria-label, for decorative graphics use aria-hidden="true", for data visualizations provide <title> and <desc> plus consider adjacent detailed text alternatives, for interactive content ensure all controls are keyboard accessible with proper ARIA labels and focus management, for complex simulations provide instructions and state changes announcements, and test with screen readers to verify the experience matches visual functionality
```

### 1.6 SVG Image Found

```

---

ID:  DiscoFoundSvgImage
Type: Discovery
Impact: N/A
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: SVG element with role="img" detected that requires manual review to verify appropriate text alternatives are provided
Why it matters: SVG elements with role="img" are explicitly marked as images and treated as a single graphic by assistive technologies, requiring appropriate text alternatives. While the role="img" indicates developer awareness of accessibility needs, manual review is needed to verify that any aria-label, aria-labelledby, or internal <title> elements adequately describe the image's content or function, and that the description is appropriate for the SVG's context and purpose.
Who it affects: Blind and low vision users using screen readers who depend on text alternatives to understand image content, users with cognitive disabilities who benefit from clear, concise descriptions of visual information, keyboard users who may encounter the SVG in their navigation flow, and users of assistive technologies that treat role="img" SVGs as atomic image elements
How to fix: Verify the SVG with role="img" has appropriate accessible names through aria-label or aria-labelledby attributes, ensure any <title> or <desc> elements inside the SVG are properly referenced if used for labeling, confirm decorative SVGs are hidden with aria-hidden="true" rather than given role="img", check that the text alternative accurately describes the SVG's meaning in context, and test with screen readers to ensure the image is announced with meaningful information
```

### 1.7 SVG Missing Label
```

---

ID:  ErrAltOnElementThatDoesntTakeIt
Type: Error
Impact: Low
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: Alt attribute placed on HTML elements that don't support it (such as div, span, p, or other non-image elements), making the alternative text inaccessible to assistive technologies
Why it matters: The alt attribute is only valid on specific elements (<img>, <area>, <input type="image">) and is ignored when placed on other elements. Screen readers will not announce this misplaced alt text, meaning any important information it contains is completely lost to users who rely on assistive technologies. This often occurs when developers attempt to add accessibility features but use incorrect techniques.
Who it affects: Blind and low vision users using screen readers who cannot access the alternative text content placed in invalid locations, users with cognitive disabilities who may be missing explanatory text, keyboard users who may not receive important contextual information, and users of assistive technologies that rely on proper semantic HTML markup
How to fix: Remove alt attributes from non-supporting elements and use appropriate alternatives - for background images in CSS use role="img" with aria-label, for clickable elements use aria-label or visually hidden text, for decorative elements ensure they're properly hidden with aria-hidden="true", and verify that actual <img> elements are used for content images that need alternative text
```

### 1.5 Inline SVG Discovery

```

---

ID: ErrAltTooLong
Type: Error
Impact: Medium
WCAG: 1.1.1 Non-text Content (Level A)
Description: Alt text exceeds 150 characters, making it difficult for screen reader users to process
Why it matters: Excessively long alt text creates a poor listening experience and may indicate that complex information should be presented differently.
Who it affects: Screen reader users who must listen to lengthy descriptions, users with cognitive disabilities who may struggle with verbose content.
How to fix: Limit alt text to 150 characters or less, use longdesc or aria-describedby for complex images, provide detailed descriptions in adjacent text content.

---

ID:  ErrImageAltContainsHTML
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: Image's alternative text contains HTML markup tags
Why it matters: HTML in alt text is not parsed, so screen readers will read the HTML markup as literal characters. Users will hear angle brackets announced as "less than" or "greater than" and tag names spelled out, creating a confusing experience. For example, alt="<b>Team Photo</b>" would be read as "less than b greater than Team Photo less than slash b greater than".
Who it affects: Blind and low vision users using screen readers who will hear nonsense characters and words interspersed with the actual alt text, making it difficult or impossible to understand the image content
How to fix: Remove all HTML markup from alt attributes and use only plain text. If formatting or structure is important to convey, describe it in words rather than using markup (e.g., instead of "<em>Important</em>" use "Important, emphasized").
```

---

## 2. FORMS

### 2.1 Unlabelled field

```

---

ID:  ErrImageWithEmptyAlt
Type: Error
Impact: Medium
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: Image alt attribute contains only whitespace characters (spaces, tabs, line breaks), providing no accessible name
Why it matters: Whitespace-only alt attributes fail to provide any accessible name for the image, causing screen readers to announce unhelpful fallback information like the image filename or "unlabeled graphic". Unlike properly empty alt="" which signals decorative content, whitespace alt text creates ambiguity - users cannot determine if they're missing important information or if the image is decorative.
Who it affects: Blind and low vision users relying on screen readers who cannot determine the image's purpose or content, users with cognitive disabilities who depend on clear labeling to understand page content, and users of voice control software who cannot reference images without accessible names
How to fix: Determine the image's purpose and apply appropriate alt text - for informative images add descriptive alternative text that conveys the same information, for decorative images use alt="" (no spaces) to properly mark them as decorative, for functional images describe the action or destination not the appearance, and remove any whitespace-only alt attributes that serve as ineffective placeholders
```

### 1.3 Alt Text is Image Filename

```

---

ID:  ErrImageWithImgFileExtensionAlt
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: Alt text contains image filename with file extension (e.g., "photo.jpg", "IMG_1234.png", "banner.gif"), providing no meaningful description of the image content
Why it matters: Filenames rarely describe image content meaningfully and often contain technical identifiers, underscores, hyphens, or numbers that create a poor listening experience when announced by screen readers. Users hear cryptic strings like "DSC underscore zero zero four two dot jay peg" instead of learning what the image actually shows, forcing them to guess at important visual information or miss it entirely.
Who it affects: Blind and low vision users using screen readers who need meaningful descriptions to understand visual content, users with cognitive disabilities who rely on clear, descriptive text to process information, users in low-bandwidth situations where images don't load and only alt text is displayed, and search engine users who rely on descriptive alt text for finding relevant content
How to fix: Replace the filename with descriptive text that conveys the image's information or purpose (change alt="hero-banner-2.jpg" to alt="Students collaborating in the campus library"), focus on what the image communicates rather than technical details, ensure the description makes sense when read in context with surrounding content, and avoid including file extensions or technical metadata in alt attributes
```

### 1.4 Alt on Non-Image Element

```

---

ID:  ErrImageWithNoAlt
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: Images are missing alternative text attributes, preventing assistive technologies from conveying their content or purpose to users
Why it matters: Screen readers cannot describe image content to users who are blind or have low vision, creating information barriers that may prevent understanding of essential content, navigation, or task completion. This also affects users with cognitive disabilities who benefit from text alternatives and users on slow connections where images fail to load.
Who it affects: Blind users using screen readers, users with low vision using screen readers with magnification, users with cognitive disabilities who rely on text alternatives, voice control users who need text labels to reference elements, and users on slow internet connections
How to fix: Add descriptive alt attributes for informative images (alt="Sales chart showing 40% increase"), use empty alt attributes for decorative images (alt=""), describe the function for interactive images (alt="Search" not alt="magnifying glass icon"), and provide detailed descriptions via aria-describedby for complex images like charts or diagrams.
```

### 1.2 Empty Alternative Text on Informative Images

```### 1.2 Empty Alternative Text

```

---

ID:  ErrImageWithURLAsAlt
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: Alt attribute contains a URL (starting with http://, https://, www., or file://) instead of descriptive text about the image content
Why it matters: URLs provide no meaningful information about what an image shows or its purpose on the page. Screen reader users hear lengthy, difficult-to-parse web addresses being spelled out character by character or in chunks like "h-t-t-p-colon-slash-slash-w-w-w-dot", creating a frustrating experience that conveys nothing about the actual image content. This often happens when image source URLs are mistakenly copied into alt attributes.
Who it affects: Blind and low vision users using screen readers who need meaningful descriptions instead of technical URLs, users with cognitive disabilities who cannot process or remember long URL strings to understand image content, users in low-bandwidth situations where only alt text displays when images fail to load, and voice control users who cannot effectively reference images labeled with URLs
How to fix: Replace the URL with descriptive text that conveys what the image shows or its function (change alt="https://example.com/images/team-photo.jpg" to alt="Marketing team at annual conference"), focus on describing the image content rather than its location or technical details, ensure the description makes sense in the page context, and never use the image's web address as its alternative text
```

### 1.8 ALT text contains HTML markup

```

---

ID: ErrNoAlt
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Description: Image missing alt attribute entirely
Why it matters: Without alt attributes, screen readers cannot convey any information about images to users.
Who it affects: Blind and low vision users using screen readers, users with images disabled.
How to fix: Add alt attribute to all img elements; use alt="" for decorative images, descriptive text for informative images.

---

ID: ErrRedundantAlt
Type: Error
Impact: Low
WCAG: 1.1.1 Non-text Content (Level A)
Description: Alt text contains redundant words like "image of" or "picture of"
Why it matters: Screen readers already announce images as images, so these phrases create redundant announcements.
Who it affects: Screen reader users who hear repetitive "image image of" announcements.
How to fix: Remove "image of", "picture of", "graphic of" from alt text; describe the content directly.

---

ID: ErrSVGNoAccessibleName
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Description: SVG image lacks accessible name through title, aria-label, or aria-labelledby
Why it matters: Without accessible names, SVG content is invisible to screen reader users.
Who it affects: Blind and low vision users using screen readers.
How to fix: Add <title> element with aria-labelledby, or use role="img" with aria-label for simple SVGs.

---

ID:  ErrSvgImageNoLabel
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: SVG image element lacks accessible text alternatives, making it invisible to screen reader users
Why it matters: SVG images without proper labeling are completely inaccessible to screen reader users - they are either skipped entirely or announced as "graphic" with no indication of what they represent. Unlike HTML img elements that can use alt attributes, SVGs require different techniques for accessibility. Without proper labeling, users miss important visual information, icons, charts, logos, or interactive graphics that may be essential for understanding or using the page.
Who it affects: Blind and low vision users using screen readers who cannot perceive any information about unlabeled SVG content, users with cognitive disabilities who benefit from text descriptions of complex graphics, keyboard users who may encounter interactive SVGs without understanding their purpose, and users of assistive technologies that need text alternatives for all visual content
How to fix: For simple SVGs, add role="img" and aria-label with descriptive text. For complex SVGs, use <title> as the first child element and reference it with aria-labelledby. For decorative SVGs, use aria-hidden="true" to hide from assistive technologies. For inline SVGs containing text, ensure text is in actual text elements not paths. For interactive SVGs, provide appropriate ARIA labels for all interactive elements. Always test with screen readers to verify SVGs are properly announced.
```

### 1.8 URL used as ALT text

```

---

ID: WarnSVGNoRole
Type: Warning
Impact: Low
WCAG: 1.1.1 Non-text Content (Level A)
Description: SVG missing appropriate role attribute
Why it matters: SVGs need proper roles to be correctly interpreted by assistive technologies.
Who it affects: Screen reader users.
How to fix: Add role="img" for informative SVGs, use aria-hidden="true" for decorative ones.

---

ID: WarnSvgPositiveTabindex
Type: Warning
Impact: Medium
WCAG: 2.4.3 Focus Order (Level A)
Description: SVG element has positive tabindex disrupting tab order
Why it matters: SVGs typically shouldn't be in tab order unless interactive.
Who it affects: Keyboard users experiencing confusing navigation.
How to fix: Remove tabindex from non-interactive SVGs, use tabindex="0" only for interactive SVGs.

---

### Keyboard Navigation

ID:  AI_ErrClickableWithoutKeyboard
Type: Error
Impact: High
WCAG: 2.1.1
Category: keyboard
Description: Element with onclick handler is not keyboard accessible
Why it matters: Keyboard users cannot activate this control
Who it affects: Keyboard users, users who cannot use a mouse
How to fix: Add tabindex="0" and implement onkeypress/onkeydown handlers for Enter and Space keys
```

```

---

ID:  AI_ErrMissingFocusIndicator
Type: Error
Impact: High
WCAG: 2.4.7
Category: focus
Description: Interactive element lacks visible focus indicator
Why it matters: Users can't see which element has keyboard focus
Who it affects: Keyboard users, users with attention or memory issues
How to fix: Add CSS :focus styles with visible outline, border, or background change
```

```

---

ID:  AI_ErrModalFocusTrap
Type: Error
Impact: High
WCAG: 2.1.2, 2.4.3
Category: dialogs
Description: Modal/dialog "{element_text}" does not properly trap focus
Why it matters: Without focus trapping, keyboard users can navigate outside the modal while it's open, causing confusion
Who it affects: Keyboard users, screen reader users
How to fix: Implement focus trap to keep focus within modal while open, and return focus to trigger element on close
```

```

---

ID:  AI_ErrTabsWithoutARIA
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2, 1.3.1
Category: navigation
Description: Tab interface "{element_text}" lacks proper ARIA markup
Why it matters: Without role="tablist", role="tab", and aria-selected attributes, screen readers cannot convey tab relationships and states
Who it affects: Screen reader users, keyboard users
How to fix: Add role="tablist" to container, role="tab" to tabs, role="tabpanel" to panels, and manage aria-selected states
```

```

---

ID:  AI_WarnModalWithoutFocusTrap
Type: Warning
Impact: High
WCAG: 2.1.2, 2.4.3
Category: modals
Description: Modal dialog doesn't trap focus within the dialog
Why it matters: Keyboard users can tab out of the modal into the page behind it
Who it affects: Keyboard users, screen reader users
How to fix: Implement focus trap that keeps tab navigation within the modal
```

```

---

ID:  ErrInvalidTabindex
Type: Error
Impact: High
WCAG: 2.4.3 Focus Order (Level A)
Category: focus
Description: Element has a tabindex attribute with an invalid value (non-numeric or decimal)
Why it matters: Invalid tabindex values are ignored by browsers, potentially making interactive elements unreachable by keyboard or creating unpredictable focus behavior. This can completely block keyboard users from accessing functionality. The element might be skipped during tabbing, receive focus unexpectedly, or behave differently across browsers.
Who it affects: Keyboard users who cannot reach or interact with the element, screen reader users who may miss important interactive controls, users with motor disabilities relying on keyboard navigation, and users who cannot use a mouse
How to fix: Use only valid integer values for tabindex: "0" to include in natural tab order, "-1" to remove from tab order but allow programmatic focus, or remove the tabindex attribute entirely if the element shouldn't be focusable. Never use decimal values (1.5), text ("first"), or empty values (tabindex="").
```

### 7.4 Focus Indicators
```

---

ID:  ErrMainLandmarkHasTabindexOfZeroCanOnlyHaveMinusOneAtMost
Type: Error
Impact: Medium
WCAG: 2.4.3
Category: landmarks
Description: Main landmark has tabindex="0" which is inappropriate
Why it matters: Landmarks should not be in the tab order
Who it affects: Keyboard users
How to fix: Remove tabindex or use tabindex="-1" if programmatic focus is needed
```

```

---

ID: ErrMissingTabindex
Type: Error
Impact: High
WCAG: 2.1.1 Keyboard (Level A)
Description: Interactive element not keyboard accessible due to missing tabindex
Why it matters: Elements that should be interactive but lack keyboard access create complete barriers for non-mouse users.
Who it affects: Keyboard users, screen reader users, users with motor disabilities who cannot use a mouse.
How to fix: Add tabindex="0" to custom interactive elements, or use native interactive HTML elements that are keyboard accessible by default.

---

ID:  ErrNegativeTabindex
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

---

ID:  ErrNoFocusIndicator
Type: Error
Impact: High
WCAG: 2.4.7 Focus Visible (Level AA)
Category: focus
Description: Interactive element has no visible focus indicator when focused, making keyboard navigation impossible to track
Why it matters: Focus indicators show keyboard users where they are on the page - without them, it's like navigating in the dark. Users cannot see which element will be activated when they press Enter or Space, making it impossible to navigate confidently. They might activate the wrong control, skip important content, or become completely lost on the page. This is especially critical for forms where activating the wrong button could submit incomplete data or cancel an operation.
Who it affects: Keyboard users who need to see their current position, users with attention or memory disabilities who lose track of focus position, users with low vision who need clear visual indicators, users with motor disabilities who need to carefully track navigation, and any user who temporarily cannot use a mouse
How to fix: Ensure all interactive elements have a visible focus indicator using CSS :focus styles. Add outline, border, background color, or box-shadow changes. Make focus indicators clearly visible with sufficient color contrast (3:1 minimum). Never use outline: none without providing an alternative indicator. Consider using :focus-visible for keyboard-only focus styles. Test by tabbing through your entire page to ensure every interactive element shows focus clearly.
```

```

---

ID: ErrNonInteractiveZeroTabindex
Type: Error
Impact: Medium
WCAG: 2.1.1 Keyboard (Level A)
Description: Non-interactive element has tabindex="0" making it keyboard focusable
Why it matters: Adding keyboard focus to non-interactive elements confuses users and clutters keyboard navigation.
Who it affects: Keyboard users encountering unexpected tab stops, screen reader users hearing non-actionable elements.
How to fix: Remove tabindex="0" from non-interactive elements, only make elements focusable if they have functionality.

---

ID:  ErrPositiveTabindex
Type: Error
Impact: High
WCAG: 2.4.3 Focus Order
Category: focus
Description: Element uses a positive tabindex value (greater than 0)
Why it matters: Positive tabindex values override the natural tab order of the page, creating an unpredictable navigation experience. When you use tabindex="1" or higher, that element jumps to the front of the tab order, regardless of where it appears visually. This breaks the expected top-to-bottom, left-to-right flow that keyboard users rely on. Users might tab from the header straight to a random form field in the middle of the page, then jump to the footer, then back to the navigation. This confusing order makes it easy to miss content, difficult to predict where focus will go next, and nearly impossible to maintain as the page evolves.
Who it affects: Keyboard users who expect logical, predictable navigation order, screen reader users who rely on consistent focus flow, users with motor disabilities who need efficient keyboard navigation, users with cognitive disabilities who are confused by unpredictable focus movement, and developers maintaining the code who must manage complex tabindex values
How to fix: Remove positive tabindex values and use only tabindex="0" (adds element to natural tab order) or tabindex="-1" (removes from tab order but allows programmatic focus). Let the DOM order determine tab order - if elements need to be reached in a different order, rearrange them in the HTML. If visual order must differ from DOM order for design reasons, consider using CSS Grid or Flexbox with the order property, but be cautious as this can still cause accessibility issues.
```

```

---

ID:  ErrTTabindexOnNonInteractiveElement
Type: Error
Impact: Medium
WCAG: 2.4.3
Category: focus
Description: Tabindex attribute on non-interactive element
Why it matters: Non-interactive elements should not be in tab order unless they serve a specific purpose
Who it affects: Keyboard users
How to fix: Remove tabindex from non-interactive elements or make them properly interactive
```

### 7.3 Invalid Tabindex
```

---

ID: ErrTabOrderViolation
Type: Error
Impact: High
WCAG: 2.4.3 Focus Order (Level A)
Description: Tab order does not follow logical reading order
Why it matters: Illogical tab order confuses users and makes interfaces difficult to navigate efficiently.
Who it affects: Keyboard users, screen reader users, users with cognitive disabilities.
How to fix: Ensure DOM order matches visual order, avoid positive tabindex values, test tab order manually.

---

ID:  ErrTabindexOfZeroOnNonInteractiveElement
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

---

ID:  ErrTransparentFocusIndicator
Type: Error
Impact: High
WCAG: 2.4.7 Focus Visible (Level AA)
Category: focus
Description: Focus indicator uses transparent or nearly transparent color, making it effectively invisible
Why it matters: A transparent focus indicator is functionally the same as no focus indicator - users cannot see where keyboard focus is located. This might occur from using rgba with 0 or very low alpha values, setting outline-color to transparent, or using colors that match the background. The focus indicator exists technically but provides no practical benefit to users trying to navigate.
Who it affects: Keyboard users who need visible focus indicators to navigate, users with low vision who need clear visual cues, users with color blindness who may already struggle with certain color combinations, and users with cognitive disabilities who need obvious focus indicators
How to fix: Use opaque colors with sufficient contrast for focus indicators. Replace transparent outlines with visible colors, ensure at least 3:1 contrast ratio between focus indicator and background, use solid colors or high alpha values (0.7 or higher) for rgba colors. Test focus indicators on different backgrounds across your site. Consider using box-shadow or background changes as additional focus indicators.
```

---

## 8. FONTS

### 8.1 Font Warnings
```

---

ID:  ErrWrongTabindexForInteractiveElement
Type: Error
Impact: Medium
WCAG: 2.4.3
Category: focus
Description: Inappropriate tabindex on interactive element
Why it matters: Tab order doesn't match visual order
Who it affects: Keyboard users
How to fix: Let natural tab order work, avoid tabindex
```

```

---

ID: WarnHighTabindex
Type: Warning
Impact: Medium
WCAG: 2.4.3 Focus Order (Level A)
Description: Very high tabindex value used (over 10)
Why it matters: High tabindex values indicate attempts to control tab order that likely create confusing navigation.
Who it affects: Keyboard users experiencing unexpected tab order.
How to fix: Remove positive tabindex values, restructure DOM for natural tab order.

---

ID: WarnMissingNegativeTabindex
Type: Warning
Impact: Low
WCAG: 2.1.1 Keyboard (Level A)
Description: Element that should be removed from tab order lacks negative tabindex
Why it matters: Some elements need to be programmatically focusable but not in tab order.
Who it affects: Keyboard users encountering unnecessary tab stops.
How to fix: Add tabindex="-1" to elements that should be focusable by script but not keyboard.

---

ID: WarnModalNoFocusableElements
Type: Warning
Impact: High
WCAG: 2.1.1 Keyboard (Level A)
Description: Modal has no focusable elements
Why it matters: Modals without focusable elements trap keyboard focus with no actions available.
Who it affects: Keyboard users unable to interact with modal.
How to fix: Ensure modals contain at least one focusable element (close button, form fields, etc.).

---

ID: WarnNegativeTabindex
Type: Warning
Impact: Low
WCAG: 2.1.1 Keyboard (Level A)
Description: Interactive element has negative tabindex
Why it matters: Negative tabindex removes elements from keyboard navigation, potentially making them inaccessible.
Who it affects: Keyboard users who cannot reach the element.
How to fix: Use tabindex="0" for keyboard-accessible elements, only use -1 for programmatic focus.

---

### Landmarks

ID:  ErrBannerLandmarkAccessibleNameIsBlank
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

---

ID:  ErrBannerLandmarkMayNotBeChildOfAnotherLandmark
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

---

ID:  ErrComplementaryLandmarkAccessibleNameIsBlank
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Complementary landmark has blank accessible name
Why it matters: Empty labels provide no information
Who it affects: Screen reader users
How to fix: Add meaningful label text
```

```

---

ID:  ErrComplementaryLandmarkMayNotBeChildOfAnotherLandmark
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Complementary landmark is nested inside another landmark
Why it matters: Invalid nesting breaks landmark structure
Who it affects: Screen reader users
How to fix: Move complementary landmark outside of other landmarks
```

```

---

ID:  ErrContentInfoLandmarkAccessibleNameIsBlank
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Contentinfo landmark has blank accessible name
Why it matters: Blank labels provide no information
Who it affects: Screen reader users
How to fix: Add meaningful label text
```

```

---

ID:  ErrContentinfoLandmarkMayNotBeChildOfAnotherLandmark
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Contentinfo landmark is nested inside another landmark
Why it matters: Invalid nesting breaks landmark structure
Who it affects: Screen reader users
How to fix: Move contentinfo to top level
```

```

---

ID: ErrDuplicateLandmarkWithoutName
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Multiple landmarks of the same type without distinguishing accessible names
Why it matters: When multiple navigation or other landmarks exist without unique names, screen reader users cannot distinguish between them.
Who it affects: Screen reader users who navigate by landmarks, keyboard users who use landmark navigation shortcuts.
How to fix: Add aria-label or aria-labelledby to distinguish multiple landmarks of the same type (e.g., "Main navigation" vs "Footer navigation").

---

ID:  ErrElementNotContainedInALandmark
Type: Error
Impact: Medium
WCAG: 1.3.1
Category: landmarks
Description: Content exists outside of any landmark
Why it matters: Content may be missed when navigating by landmarks
Who it affects: Screen reader users using landmark navigation
How to fix: Ensure all content is within appropriate landmarks
```

### 4.5 Content Outside Landmarks
```

---

ID:  ErrElementRegionQualifierNotRecognized
Type: Error
Impact: Low
WCAG: 3.1.2
Category: language
Description: Element lang attribute has unrecognized region qualifier
Why it matters: Invalid region codes may affect pronunciation
Who it affects: Screen reader users
How to fix: Use valid ISO 3166-1 region codes
```

```

---

ID:  ErrMainLandmarkIsHidden
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Main landmark is hidden from view
Why it matters: Hidden main content defeats the purpose of the landmark
Who it affects: All users
How to fix: Ensure main landmark is visible or remove if not needed
```

#### Complementary Landmark Issues
```

---

ID:  ErrMainLandmarkMayNotbeChildOfAnotherLandmark
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

---

ID: ErrMissingMainLandmark
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Page missing main landmark for primary content
Why it matters: Without a main landmark, screen reader users cannot quickly navigate to the primary content area.
Who it affects: Screen reader users who navigate by landmarks, keyboard users using landmark navigation.
How to fix: Add <main> element or role="main" to identify the primary content area of each page.

---

ID:  ErrMultipleBannerLandmarks
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

---

ID:  ErrMultipleContentinfoLandmarks
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

---

ID:  ErrMultipleMainLandmarks
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships
Category: landmarks
Description: Multiple main landmark regions found on the page
Why it matters: The main landmark should contain THE primary content of the page - having multiple main landmarks is like having multiple "Chapter 1" sections in a book. It confuses the page structure and defeats the purpose of landmarks. Screen reader users expecting to jump to the main content won't know which landmark contains the actual primary content. They might land in the wrong section, miss important content, or have to check multiple "main" areas. This ambiguity makes the landmark system unreliable and forces users back to linear navigation.
Who it affects: Screen reader users relying on the main landmark to skip to primary content, keyboard users using landmark navigation extensions, users with cognitive disabilities who need clear, unambiguous page structure, and developers trying to understand the intended page structure
How to fix: Use only one <main> element or role="main" per page. Identify which content is truly the primary, unique content for that page and wrap only that in the main landmark. If you have multiple important sections, use other appropriate landmarks (article, section) or headings to structure them within the single main landmark. The main should contain all unique page content but exclude repeated elements like headers, navigation, and footers.
```

```

---

ID:  ErrNoBannerLandmarkOnPage
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships, 2.4.1 Bypass Blocks
Category: landmarks
Description: Page is missing a banner landmark to identify the site header region
Why it matters: The banner landmark identifies the site header which typically contains the site logo, main navigation, and search functionality. This content appears consistently across pages and users expect to find it at the top. Without proper banner markup, screen reader users cannot quickly jump to the header area using landmark navigation shortcuts. They must instead navigate through all content linearly or guess where the header content begins and ends. This makes it difficult to access primary navigation or return to the site homepage via the logo link, tasks that sighted users can do instantly by looking at the top of the page.
Who it affects: Screen reader users who use landmark navigation to quickly access site navigation and branding, keyboard users who want to efficiently navigate to header elements, users with cognitive disabilities who rely on consistent page structure to orient themselves, and users with low vision using screen magnifiers who need to quickly locate navigation elements
How to fix: Use the HTML5 <header> element for your site header (it has an implicit role of banner when it's not nested inside article, aside, main, nav, or section elements). Alternatively, add role="banner" to the container holding your header content. There should typically be only one banner landmark per page at the top level. Include site-wide content like logo, primary navigation, and site search within the banner landmark.
```

```

---

ID:  ErrNoMainLandmark
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships, 2.4.1 Bypass Blocks
Category: landmarks
Description: Page is missing a main landmark region to identify the primary content area
Why it matters: Screen reader users rely on landmarks to understand page layout and quickly navigate to important sections. The main landmark allows users to skip repeated content like headers and navigation to jump directly to the unique page content. Without it, users must navigate through all repeated elements on every page, which is time-consuming and frustrating. The main landmark should contain all content that is unique to the page, including the h1 heading.
Who it affects: Blind and low vision users using screen readers who navigate by landmarks, users with motor disabilities who need efficient keyboard navigation to skip repeated content, and users with cognitive disabilities who benefit from clear page structure
How to fix: Add a <main> element around the primary content area, or use role="main" on an appropriate container element. Ensure there is only one main landmark per page, position it as a top-level landmark (not nested inside other landmarks), and include all unique page content within it, including the h1 heading. The main landmark should not include repeated content like site headers, navigation, or footers.
```

```

---

ID:  RegionLandmarkAccessibleNameIsBlank
Type: Error
Impact: Medium
WCAG: 1.3.1, 2.4.6
Category: landmarks
Description: Region landmark has blank accessible name
Why it matters: Blank labels provide no information
Who it affects: Screen reader users
How to fix: Add meaningful label text
```

```

---

ID:  WarnBannerLandmarkAccessibleNameUsesBanner
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: landmarks
Description: Banner landmark uses generic term "banner" in label
Why it matters: Redundant labeling
Who it affects: Screen reader users
How to fix: Use descriptive label or rely on implicit role
```

```

---

ID:  WarnComplementaryLandmarkAccessibleNameUsesComplementary
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: landmarks
Description: Complementary landmark label uses generic term "complementary"
Why it matters: Generic labels don't describe specific content
Who it affects: Screen reader users
How to fix: Use descriptive labels like "Related articles" or "Sidebar"
```

#### Navigation Landmark Issues
```

---

ID: WarnContentOutsideLandmarks
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Content exists outside of landmark regions
Why it matters: Content outside landmarks is harder to find and navigate for screen reader users.
Who it affects: Screen reader users who navigate by landmarks.
How to fix: Ensure all content is within appropriate landmarks (header, nav, main, footer, aside).

---

ID:  WarnContentinfoLandmarkAccessibleNameUsesContentinfo
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: landmarks
Description: Contentinfo landmark uses generic term "contentinfo" in label
Why it matters: Redundant labeling
Who it affects: Screen reader users
How to fix: Use descriptive label or rely on implicit role
```

```

---

ID:  WarnElementNotInLandmark
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Category: landmarks
Description: Important content found outside of any landmark region, making it harder for screen reader users to find and navigate to
Why it matters: Landmarks create a navigable structure for your page, like a table of contents. Content outside landmarks is like having chapters missing from the table of contents - users may never find it when navigating by landmarks. Screen reader users often jump between landmarks to quickly scan page structure, and content outside landmarks requires them to read through the entire page linearly to discover it. This particularly affects users who are familiar with your site and want to quickly navigate to specific content areas.
Who it affects: Screen reader users who navigate by landmarks to efficiently explore pages, keyboard users using browser extensions for landmark navigation, users with cognitive disabilities who rely on consistent page structure, and power users who use landmarks for quick navigation
How to fix: Ensure all meaningful content is contained within appropriate landmark regions. Typically: use <header> or role="banner" for site headers, <nav> or role="navigation" for navigation menus, <main> or role="main" for primary content, <aside> or role="complementary" for sidebar content, <footer> or role="contentinfo" for footers. Decorative content or spacers can remain outside landmarks. Review your page structure to ensure no important content is orphaned outside the landmark structure.
```

### 4.6 Additional Landmark Issues

#### Main Landmark Issues
```

---

ID: WarnMissingBannerLandmark
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Page missing banner landmark for header content
Why it matters: Banner landmark helps users quickly navigate to page header/branding.
Who it affects: Screen reader users navigating by landmarks.
How to fix: Use <header> element or role="banner" for page header content.

---

ID: WarnMissingContentinfoLandmark
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Page missing contentinfo landmark for footer
Why it matters: Contentinfo landmark helps users find footer information like copyright and links.
Who it affects: Screen reader users navigating by landmarks.
How to fix: Use <footer> element or role="contentinfo" for page footer.

---

ID:  WarnNoBannerLandmark
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A), 2.4.1 Bypass Blocks (Level A)
Category: landmarks
Description: Page is missing a banner landmark to identify the header/masthead region
Why it matters: The banner landmark identifies the site header containing the logo, primary navigation, and other site-wide content. Without it, screen reader users cannot quickly jump to the header area using landmark navigation. They must read through content linearly to find navigation and branding elements. This is especially frustrating when users want to access the main navigation or return to the homepage via the logo.
Who it affects: Screen reader users who navigate by landmarks to quickly access header content, keyboard users with assistive technology looking for navigation, users with cognitive disabilities who rely on consistent page structure, and users who frequently need to access header elements like search or main navigation
How to fix: Use the HTML5 <header> element at the page level (not within article, aside, main, nav, or section) as it has an implicit banner role. Alternatively, add role="banner" to your header container. Include site-wide elements like logo, primary navigation, site search, and utility navigation within the banner. Ensure only one banner landmark exists per page at the top level.
```

```

---

ID:  WarnNoContentinfoLandmark
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships, 2.4.1 Bypass Blocks
Category: landmarks
Description: Page is missing a contentinfo landmark to identify the footer region
Why it matters: The contentinfo landmark (typically a footer) contains important information about the page or site such as copyright notices, privacy policies, contact information, and site maps. Screen reader users rely on landmarks to quickly navigate to these common elements without having to read through the entire page. When the footer lacks proper landmark markup, users must search manually through the content to find this information, which is inefficient and may cause them to miss important legal notices or helpful links. The contentinfo landmark provides a consistent, predictable way to access this supplementary information across all pages.
Who it affects: Screen reader users who navigate by landmarks to quickly find footer information, keyboard users who want to efficiently skip to footer content, users with cognitive disabilities who rely on consistent page structure, and users who need to frequently access footer links like privacy policies or contact information
How to fix: Use the HTML5 <footer> element for your page footer (it has an implicit role of contentinfo when it's not nested inside article, aside, main, nav, or section elements). Alternatively, add role="contentinfo" to the container holding your footer content. Ensure there's only one contentinfo landmark per page at the top level. The footer should contain information about the page or site, not primary content.
```

```

---

### Language

ID:  AI_WarnMixedLanguage
Type: Warning
Impact: Medium
WCAG: 3.1.2
Category: language
Description: Mixed language content detected without proper language declarations
Why it matters: Screen readers may pronounce text incorrectly without language declarations
Who it affects: Screen reader users who speak multiple languages
How to fix: Add lang attributes to elements containing different languages
```

### Animation Issues

```

---

ID:  ErrElementLangEmpty
Type: Error
Impact: Medium
WCAG: 3.1.2
Category: language
Description: Element has empty lang attribute
Why it matters: Empty lang on elements provides no language change information
Who it affects: Screen reader users
How to fix: Add valid language code or remove empty lang attribute
```

```

---

ID:  ErrElementPrimaryLangNotRecognized
Type: Error
Impact: Medium
WCAG: 3.1.1, 3.1.2
Category: language
Description: Element has unrecognized language code
Why it matters: Language changes won't be announced properly
Who it affects: Screen reader users
How to fix: Use valid language codes
```

### 6.3 Empty Language Attribute
```

---

ID:  ErrEmptyLangAttr
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

---

ID:  ErrEmptyLanguageAttribute
Type: Error
Impact: High
WCAG: 3.1.1 Language of Page (Level A)
Category: language
Description: HTML element has a lang attribute present but with no value (lang=""), preventing screen readers from determining the page language
Why it matters: An empty lang attribute is worse than no lang attribute because it explicitly tells assistive technologies there's no language specified, potentially causing screen readers to use incorrect pronunciation rules or fail to switch language synthesizers. This can make content completely unintelligible when read aloud.
Who it affects: Blind and low vision users using screen readers who need proper language identification for correct pronunciation, multilingual users who rely on automatic language switching in assistive technologies, users with dyslexia using reading tools that depend on language settings, and users of translation services
How to fix: Add a valid language code to the lang attribute (e.g., lang="en" for English, lang="es" for Spanish, lang="fr" for French). Use the correct ISO 639-1 two-letter code or ISO 639-2 three-letter code. For the HTML element, always specify the primary document language. If the language is truly unknown, remove the lang attribute entirely rather than leaving it empty.
```

### 6.4 Invalid Language Code
```

---

ID:  ErrEmptyXmlLangAttr
Type: Error
Impact: High
WCAG: 3.1.1
Category: language
Description: xml:lang attribute is empty
Why it matters: Empty xml:lang provides no language information
Who it affects: Screen reader users using XML/XHTML parsers
How to fix: Add valid language code to xml:lang attribute
```

```

---

ID:  ErrInvalidLanguageCode
Type: Error
Impact: High
WCAG: 3.1.1 Language of Page (Level A), 3.1.2 Language of Parts (Level AA)
Category: language
Description: Language attribute contains invalid code '{found}' that doesn't conform to ISO 639 standards
Why it matters: The language code '{found}' is not recognized as a valid ISO 639 language code. This prevents assistive technologies from properly processing content, causing screen readers to mispronounce words, use incorrect inflection patterns, or fail to switch language engines. This can make content difficult or impossible to understand when read aloud, especially if the content is in a non-English language but gets read with English pronunciation rules.
Who it affects: Blind and low vision users relying on screen readers for accurate pronunciation, multilingual users who need proper language identification for comprehension, users with reading disabilities using text-to-speech tools, and international users accessing content in multiple languages
How to fix: Replace '{found}' with a valid ISO 639-1 or ISO 639-2 language code. If '{found}' appears to be English, use "en". Common corrections: "english" → "en", "spanish" → "es", "french" → "fr", "deutsch" → "de", "eng" → "en". For regional variants use BCP 47 format (e.g., "en-US", "en-GB", "es-MX"). Check the official ISO 639 registry for the correct code.
```

### 6.5 No Page Language
```

---

ID:  ErrNoPageLanguage
Type: Error
Impact: High
WCAG: 3.1.1 Language of Page (Level A)
Category: language
Description: HTML element is missing the lang attribute, preventing assistive technologies from determining the primary language of the page
Why it matters: Without a declared language, screen readers cannot determine which pronunciation rules and voice synthesizer to use, often defaulting to the user's system language which may be incorrect. This causes mispronunciation, incorrect inflection, and can make content unintelligible, especially for pages in languages different from the user's default settings.
Who it affects: Blind and low vision users using screen readers who need correct pronunciation for comprehension, international users accessing content in different languages, users with dyslexia or reading disabilities using assistive reading tools, and users of automatic translation services
How to fix: Add the lang attribute to the <html> element with the appropriate language code (e.g., <html lang="en"> for English, <html lang="fr"> for French). Use ISO 639-1 two-letter codes for modern languages. For XHTML, also include xml:lang with the same value. Ensure the declared language matches the actual primary language of your content. For multilingual pages, use the language that represents the majority of the content.
```

### 6.6 Language Mismatches
```

---

ID:  ErrNoPrimaryLangAttr
Type: Error
Impact: High
WCAG: 3.1.1 Language of Page
Category: language
Description: HTML element is missing the required lang attribute to identify the page's primary language
Why it matters: Both assistive technologies and browsers render text more accurately when the language is identified. Screen readers need to know which language pronunciation rules to use - without this, they may mispronounce words, use wrong inflections, or attempt to read content in the wrong language entirely. This can make content completely incomprehensible. Visual browsers need language information to display characters and scripts correctly, and search engines use it for proper indexing.
Who it affects: Screen reader users who may hear garbled pronunciation if the page language doesn't match their assistive technology's default language, users relying on automatic translation tools, users of voice assistants, and users with dyslexia using reading assistance tools
How to fix: Add the lang attribute to the html element with the appropriate ISO 639-1 language code (e.g., lang="en" for English, lang="es" for Spanish, lang="fr" for French). If the page uses multiple languages equally, use the language that appears first or is used for navigation.
```

```

---

ID:  ErrPrimaryLangAndXmlLangMismatch
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

---

ID:  ErrPrimaryLangUnrecognized
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

---

ID:  ErrPrimaryXmlLangUnrecognized
Type: Error
Impact: High
WCAG: 3.1.1
Category: language
Description: xml:lang language code not recognized
Why it matters: Invalid xml:lang codes prevent proper pronunciation
Who it affects: Screen reader users in XML/XHTML contexts
How to fix: Use valid ISO 639-1 language codes
```

```

---

ID:  ErrRegionQualifierForPrimaryLangNotRecognized
Type: Error
Impact: Medium
WCAG: 3.1.1
Category: language
Description: Region qualifier in primary language code not recognized (e.g., "en-XY")
Why it matters: Invalid region codes may cause incorrect pronunciation
Who it affects: Screen reader users
How to fix: Use valid ISO 3166-1 region codes like "en-US", "en-GB"
```

```

---

ID:  ErrRegionQualifierForPrimaryXmlLangNotRecognized
Type: Error
Impact: Medium
WCAG: 3.1.1
Category: language
Description: Region qualifier in xml:lang not recognized
Why it matters: Invalid region codes in xml:lang may cause issues
Who it affects: Screen reader users
How to fix: Use valid ISO 3166-1 region codes
```

```

---

ID:  WarnEmptyLangAttribute
Type: Warning
Impact: Medium
WCAG: 3.1.1 Language of Page (Level A)
Category: language
Description: Language attribute exists but appears to be empty or contains only whitespace
Why it matters: An empty or whitespace-only lang attribute is ambiguous - it's unclear if the language is truly unknown or if this is an error. Screen readers may use fallback behavior that doesn't match the actual content language. This is less severe than a completely empty lang="" but still prevents proper language identification. Browsers and assistive technologies cannot determine the intended language for pronunciation and processing.
Who it affects: Screen reader users who need proper language identification for correct pronunciation, multilingual users relying on language switching, users of translation tools, and users with reading disabilities using text-to-speech
How to fix: Either add a valid language code to the attribute (e.g., lang="en") or remove the attribute entirely if the language is unknown. Check for common causes like template variables that didn't populate, CMS configuration issues, or JavaScript that clears lang attributes. Ensure any whitespace is removed and a valid ISO 639 language code is provided.
```

```

---

ID:  WarnInvalidLangChange
Type: Warning
Impact: Medium
WCAG: 3.1.2 Language of Parts (Level AA)
Category: language
Description: Language change indicated but with invalid or unrecognized language code
Why it matters: Invalid language codes on content sections prevent screen readers from switching language processors correctly. This can cause content in foreign languages to be pronounced using the wrong language rules, making it incomprehensible. For example, French text might be read with English pronunciation rules. Users expect language changes to be handled smoothly, and invalid codes break this functionality.
Who it affects: Multilingual screen reader users who need proper language switching, users reading content in multiple languages, users with reading disabilities using assistive tools, and users relying on proper pronunciation for comprehension
How to fix: Verify all lang attributes on elements use valid ISO 639 language codes. Common fixes include correcting typos ("fre" → "fr"), using standard codes instead of full names ("French" → "fr"), and ensuring region codes are properly formatted ("en-us" → "en-US"). Test with screen readers to ensure language changes are announced and pronounced correctly.
```

### 6.6 Additional Language Issues

```

---

### Links

ID:  AI_ErrAmbiguousLinkText
Type: Error
Impact: Medium
WCAG: 2.4.4
Category: links
Description: Link text "{element_text}" is ambiguous without surrounding context
Why it matters: Screen reader users navigating by links won't understand the link's purpose
Who it affects: Screen reader users navigating out of context
How to fix: Use descriptive link text that makes sense without context, or add aria-label
```

### Navigation Issues

```

---

ID:  AI_ErrLinkWithoutText
Type: Error
Impact: High
WCAG: 2.4.4, 4.1.2
Category: links
Description: Link element has no accessible text
Why it matters: Screen readers announce this as "link" without any context
Who it affects: Screen reader users
How to fix: Add link text, aria-label, or aria-labelledby attribute
```

```

---

ID:  DiscoPDFLinksFound
Type: Discovery
Impact: N/A
WCAG: 1.1.1, 1.3.1, 2.1.1, 2.4.1
Category: pdf
Description: Links to PDF documents detected on page
Why it matters: PDF documents often have accessibility issues and may not be accessible to all users
Who it affects: Screen reader users, users with disabilities who have difficulty with PDF formats
How to fix: Ensure PDFs are accessible (tagged, structured, with text content) or provide HTML alternatives
```

---

## 12. PAGE STRUCTURE

### 12.1 Page Title
```

---

ID:  ErrHreflangAttrEmpty
Type: Error
Impact: Low
WCAG: 3.1.1
Category: language
Description: hreflang attribute is empty on link
Why it matters: Empty hreflang provides no language information for the linked resource
Who it affects: Screen reader users, search engines
How to fix: Add valid language code or remove empty hreflang attribute
```

```

---

ID:  ErrHreflangNotOnLink
Type: Error
Impact: Low
WCAG: 3.1.1
Category: language
Description: hreflang attribute on non-link element
Why it matters: hreflang only works on links
Who it affects: Screen reader users
How to fix: Move hreflang to anchor elements only
```

### 6.5 Language Warnings

```

---

ID: ErrInvalidGenericLinkName
Type: Error
Impact: High
WCAG: 2.4.4 Link Purpose (In Context) (Level A)
Description: Link text is generic and provides no information about destination
Why it matters: Generic link text like "click here" provides no context when links are reviewed out of context.
Who it affects: Screen reader users navigating by links, users with cognitive disabilities who need clear link purposes.
How to fix: Use descriptive link text that explains the destination or action, avoid generic phrases like "click here" or "read more".

---

ID:  ErrLinkOpensNewWindowNoWarning
Type: Error
Impact: Medium
WCAG: 3.2.2 On Input
Category: links
Description: Link opens in new window/tab without warning users
Why it matters: Unexpectedly opening new windows can disorient users, especially those using screen readers or magnification. Users may not realize a new window opened and become confused when the back button doesn't work. This is particularly problematic for users with cognitive disabilities or those unfamiliar with browser behaviors.
Who it affects: Screen reader users who may not notice the context change, users with cognitive disabilities who may become disoriented, users with motor disabilities who have difficulty managing multiple windows, and novice computer users
How to fix: Add visible text or an icon indicating the link opens in a new window. Include this information in the accessible name (e.g., "Annual report (opens in new window)"). Consider whether opening in a new window is necessary - often it's better to open in the same window and let users control this behavior.
```

```

---

ID:  ErrLinkTextNotDescriptive
Type: Error
Impact: High
WCAG: 2.4.4 Link Purpose (In Context)
Category: links
Description: Link text does not adequately describe the link's destination or purpose
Why it matters: Users need to understand where a link will take them before activating it. Vague link text like "click here" or "read more" provides no information about the destination. Screen reader users often navigate by pulling up a list of all links, where non-descriptive text becomes meaningless out of context.
Who it affects: Screen reader users navigating by links list, users with cognitive disabilities who need clear navigation cues, and users with motor disabilities who need to make informed decisions before activating links
How to fix: Write link text that describes the destination or action (e.g., "Download 2024 annual report" instead of "Download"). Avoid generic phrases. If design constraints require short link text, provide additional context through aria-label or aria-describedby, or ensure surrounding text provides context.
```

```

---

ID:  ErrPrimaryHrefLangNotRecognized
Type: Error
Impact: Low
WCAG: 3.1.1
Category: language
Description: hreflang language code not recognized
Why it matters: Invalid hreflang codes provide incorrect information about linked resources
Who it affects: Screen reader users, search engines
How to fix: Use valid ISO 639-1 language codes
```

```

---

ID:  ErrRegionQualifierForHreflangUnrecognized
Type: Error
Impact: Low
WCAG: 3.1.1
Category: language
Description: hreflang region qualifier not recognized
Why it matters: Invalid region codes in hreflang attributes
Who it affects: Screen reader users, search engines
How to fix: Use valid ISO 3166-1 region codes
```

---

## 7. FOCUS & KEYBOARD

### 7.1 Focus Indicators
```

---

ID: WarnAnchorTargetTabindex
Type: Warning
Impact: Low
WCAG: 2.1.1 Keyboard (Level A)
Description: Anchor target element has unnecessary tabindex
Why it matters: Elements that are link targets don't need tabindex; adding it may create confusion.
Who it affects: Keyboard users encountering unexpected tab stops.
How to fix: Remove tabindex from elements that are only link targets, not interactive controls.

---

ID: WarnColorOnlyLink
Type: Warning
Impact: Medium
WCAG: 1.4.1 Use of Color (Level A)
Description: Link distinguished only by color without underline or other indicator
Why it matters: Users who cannot perceive color differences cannot identify links in text.
Who it affects: Colorblind users, users with low vision, users of monochrome displays.
How to fix: Add underlines to links, use other visual indicators beyond color, ensure 3:1 contrast with surrounding text.

---

ID: WarnGenericDocumentLinkText
Type: Warning
Impact: Medium
WCAG: 2.4.4 Link Purpose (In Context) (Level A)
Description: Document link uses generic text like "PDF" without describing content
Why it matters: Users need to know what document they're downloading, not just its format.
Who it affects: All users, especially screen reader users reviewing links.
How to fix: Include document title and format in link text (e.g., "Annual Report 2023 (PDF, 2MB)").

---

ID: WarnGenericLinkNoImprovement
Type: Warning
Impact: Medium
WCAG: 2.4.4 Link Purpose (In Context) (Level A)
Description: Generic link text with no surrounding context to clarify purpose
Why it matters: Generic links without context force users to explore further to understand destinations.
Who it affects: Screen reader users navigating by links, users with cognitive disabilities.
How to fix: Rewrite link text to be descriptive, or ensure surrounding text provides clear context.

---

### Lists

ID: ErrEmptyList
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: List element (ul, ol, dl) contains no list items
Why it matters: Empty lists create confusion about document structure and may indicate missing content or markup errors.
Who it affects: Screen reader users who encounter empty list announcements, all users missing potentially important content.
How to fix: Remove empty list elements or populate them with appropriate list items, ensure lists are only used for actual list content.

---

ID: ErrFakeListImplementation
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Visual list created without proper list markup (using br tags, dashes, or bullets)
Why it matters: Fake lists don't convey proper structure to assistive technologies, preventing users from understanding relationships between items.
Who it affects: Screen reader users who cannot navigate lists properly, users who rely on structural navigation.
How to fix: Use proper ul/ol elements with li items for lists, avoid using visual characters or br tags to simulate list appearance.

---

ID: WarnCustomBulletStyling
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: List uses custom bullet styling that may not be accessible
Why it matters: Custom bullets using CSS or images may not be announced correctly by screen readers.
Who it affects: Screen reader users who may miss list semantics.
How to fix: Use CSS ::marker pseudo-element for custom bullets, ensure list semantics are preserved.

---

ID: WarnDeepListNesting
Type: Warning
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Lists nested more than 3 levels deep
Why it matters: Deeply nested lists are difficult to understand and navigate.
Who it affects: Screen reader users, users with cognitive disabilities.
How to fix: Simplify list structure, consider alternative presentations for complex hierarchies.

---

ID:  WarnFontNotInRecommenedListForA11y
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

---

### Maps

ID: ErrDivMapMissingAttributes
Type: Error
Impact: High
WCAG: 1.1.1 Non-text Content (Level A)
Description: Map container div is missing required accessibility attributes
Why it matters: Maps without proper accessibility attributes are completely inaccessible to screen reader users who cannot perceive the visual information.
Who it affects: Blind and low vision users, users who rely on screen readers to understand map content and functionality.
How to fix: Add appropriate ARIA labels and descriptions, provide text alternatives for map information, ensure all map controls are keyboard accessible.

---

ID: ErrMapMissingTitle
Type: Error
Impact: Medium
WCAG: 1.1.1 Non-text Content (Level A)
Description: Map iframe missing title attribute
Why it matters: Without titles, screen reader users don't know what the embedded map contains or represents.
Who it affects: Screen reader users who need to understand embedded content purpose.
How to fix: Add descriptive title attribute to map iframes (e.g., title="Map showing office location").

---

### Media

ID: ErrNativeVideoMissingControls
Type: Error
Impact: High
WCAG: 2.1.1 Keyboard (Level A)
Description: Native HTML5 video element missing controls attribute
Why it matters: Without controls, users cannot play, pause, or adjust video playback.
Who it affects: All users who need to control video playback, especially keyboard and screen reader users.
How to fix: Add controls attribute to all video elements, or provide custom accessible controls.

---

ID: ErrVideoIframeMissingTitle
Type: Error
Impact: Medium
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Video iframe lacks title attribute
Why it matters: Without titles, screen reader users don't know what video content is embedded.
Who it affects: Screen reader users who need to understand embedded content.
How to fix: Add descriptive title attribute to video iframes describing the video content.

---

ID: WarnVideoAutoplay
Type: Warning
Impact: Medium
WCAG: 1.4.2 Audio Control (Level A)
Description: Video set to autoplay which may distract users
Why it matters: Autoplay video can be disruptive and use bandwidth unexpectedly.
Who it affects: Users with cognitive disabilities, users on limited data plans.
How to fix: Remove autoplay or mute autoplaying videos, provide clear play controls.

---

### Navigation

ID:  AI_ErrMenuWithoutARIA
Type: Error
Impact: High
WCAG: 4.1.2
Category: navigation
Description: Navigation menu lacks proper ARIA markup
Why it matters: Screen readers won't recognize this as a navigation menu
Who it affects: Screen reader users
How to fix: Add role="navigation" to container and appropriate ARIA attributes for menu items
```

```

---

ID:  ErrCompletelyEmptyNavLandmark
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Navigation landmark contains no content
Why it matters: Empty navigation serves no purpose
Who it affects: All users
How to fix: Add navigation content or remove empty landmark
```

```

---

ID: ErrDuplicateNavNames
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Multiple navigation elements have identical accessible names
Why it matters: Users cannot distinguish between different navigation areas when they have the same name, causing confusion about page structure.
Who it affects: Screen reader users navigating by landmarks, users with cognitive disabilities who rely on clear labeling.
How to fix: Provide unique accessible names for each navigation element using aria-label or aria-labelledby.

---

ID: ErrInappropriateMenuRole
Type: Error
Impact: Medium
WCAG: 4.1.2 Name, Role, Value (Level A)
Description: Menu role used inappropriately for navigation links
Why it matters: Menu role is for application menus, not navigation. Misuse causes incorrect keyboard behavior and screen reader announcements.
Who it affects: Screen reader users expecting application menu behavior, keyboard users expecting arrow key navigation.
How to fix: Use nav element or role="navigation" for site navigation, reserve role="menu" for actual application menus with proper ARIA patterns.

---

ID:  ErrNavLandmarkAccessibleNameIsBlank
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

---

ID:  ErrNavLandmarkContainsOnlyWhiteSpace
Type: Error
Impact: High
WCAG: 1.3.1
Category: landmarks
Description: Navigation landmark contains only whitespace
Why it matters: Whitespace-only navigation is not functional
Who it affects: All users
How to fix: Add navigation links or remove the landmark
```

#### Region Landmark Issues
```

---

ID: ErrNavMissingAccessibleName
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Navigation element lacks accessible name to distinguish it
Why it matters: When pages have multiple navigation areas, users need to distinguish between them.
Who it affects: Screen reader users navigating by landmarks, users who need to understand page structure.
How to fix: Add aria-label or aria-labelledby to nav elements to identify their purpose (e.g., "Main navigation", "Breadcrumb").

---

ID:  ErrNestedNavLandmarks
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

---

ID:  WarnNavLandmarkAccessibleNameUsesNavigation
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: landmarks
Description: Navigation landmark uses generic term "navigation" in label
Why it matters: Generic labels don't describe specific purpose
Who it affects: Screen reader users
How to fix: Use more descriptive labels like "Product categories" or "User account menu"
```

```

---

ID:  WarnNoNavigationLandmark
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships, 2.4.1 Bypass Blocks
Category: landmarks
Description: Page has no navigation landmarks to identify navigation regions
Why it matters: Navigation landmarks identify areas containing navigation links, allowing users to quickly jump to menus without reading through other content. Most web pages have multiple navigation areas (main menu, footer links, sidebar navigation, breadcrumbs) but without proper markup, these are just lists of links mixed with other content. Screen reader users must hunt for navigation areas or listen to all links to find what they need. Navigation landmarks make these areas immediately discoverable and allow users to skip between different navigation regions efficiently.
Who it affects: Screen reader users who use landmarks to find navigation menus quickly, keyboard users navigating complex sites with multiple menus, users with cognitive disabilities who need clear identification of navigation areas, and users with motor disabilities who need to minimize unnecessary navigation
How to fix: Wrap navigation areas in <nav> elements or add role="navigation" to containers with navigation links. If you have multiple navigation areas, label each one with aria-label to distinguish them (e.g., aria-label="Main navigation", aria-label="Footer links", aria-label="Breadcrumb"). Not every group of links needs to be a navigation landmark - use it for major navigation blocks that users would want to find quickly.
```

### 4.2 Multiple Landmarks
```

---

ID:  WarnRegionLandmarkAccessibleNameUsesNavigation
Type: Warning
Impact: Low
WCAG: 2.4.6
Category: landmarks
Description: Region landmark incorrectly uses "navigation" in its label
Why it matters: Confusing landmark type and purpose
Who it affects: Screen reader users
How to fix: Use appropriate label or change to nav landmark
```

#### Banner Landmark Issues
```

---

### Reading Order

ID:  AI_ErrReadingOrderMismatch
Type: Error
Impact: High
WCAG: 1.3.2, 2.4.3
Category: structure
Description: Visual reading order doesn't match DOM order - content may be read out of sequence
Why it matters: Screen readers follow DOM order, which may not match the visual layout, causing confusion
Who it affects: Screen reader users
How to fix: Reorder DOM elements to match the visual reading flow or use CSS flexbox/grid with proper order
```

### Modal and Dialog Issues

```

---

ID:  AI_ErrToggleWithoutState
Type: Error
Impact: High
WCAG: 4.1.2
Category: forms
Description: Toggle button doesn't indicate its state (expanded/collapsed)
Why it matters: Users don't know the current state of the control
Who it affects: Screen reader users, cognitive disability users
How to fix: Add aria-expanded="true/false" and update it when state changes
```

### Reading Order Issues

```

---

### Semantic Structure

ID:  AI_ErrInteractiveElementIssue
Type: Error
Impact: High
WCAG: 2.1.1, 4.1.2
Category: interactive
Description: Interactive {element_tag} element "{element_text}" has accessibility issues
Why it matters: Interactive elements without proper semantic markup or keyboard support create barriers for assistive technology users
Who it affects: Keyboard users, screen reader users, voice control users
How to fix: Use semantic HTML elements or add appropriate ARIA roles and keyboard support
```

```

---

ID: ErrHeaderMissingScope
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Table header (th) element missing scope attribute
Why it matters: Without scope attributes, screen readers cannot properly associate headers with data cells, making tables difficult to understand.
Who it affects: Screen reader users navigating complex tables, users who rely on proper table semantics for comprehension.
How to fix: Add scope="col" for column headers and scope="row" for row headers to all th elements.

---

ID: WarnVisualHierarchy
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Visual hierarchy doesn't match semantic structure
Why it matters: Mismatch between visual and semantic structure confuses understanding.
Who it affects: Screen reader users, users with cognitive disabilities.
How to fix: Ensure visual presentation matches HTML semantic structure.

---

ID:  [unique_identifier]
Type: [Error|Warning|Info|Discovery]
Impact: [High|Medium|Low|N/A]
WCAG: [comma-separated list]
Category: [category_name]
Description: [what the issue is]
Why it matters: [accessibility impact]
Who it affects: [affected user groups]
How to fix: [remediation steps]
```

---

## AI-Detected Issues

These issues are detected through AI visual and semantic analysis of the page.

### Heading Issues

```

---

### Tables

ID: ErrTableMissingCaption
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Data table lacks caption element to describe its content
Why it matters: Without captions, users may not understand the table's purpose or content before navigating through it.
Who it affects: Screen reader users who need table context, users with cognitive disabilities.
How to fix: Add <caption> element as first child of table describing what data the table contains.

---

ID: ErrTableNoColumnHeaders
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Data table has no column headers (th elements)
Why it matters: Without headers, screen reader users cannot understand what each column represents when navigating cells.
Who it affects: Screen reader users navigating tables, users who need to understand data relationships.
How to fix: Use <th> elements for column headers in first row, add scope="col" to clarify header relationships.

---

ID: WarnTableMissingThead
Type: Warning
Impact: Low
WCAG: 1.3.1 Info and Relationships (Level A)
Description: Table missing thead element for headers
Why it matters: Thead helps screen readers distinguish headers from data rows.
Who it affects: Screen reader users navigating tables.
How to fix: Wrap header rows in thead element, data rows in tbody.

---

### Timing

ID: ErrAutoStartTimers
Type: Error
Impact: High
WCAG: 2.2.2 Pause, Stop, Hide (Level A)
Description: Timer starts automatically without user control to pause or stop
Why it matters: Auto-starting timers can create stress and barriers for users who need more time to complete tasks or read content.
Who it affects: Users with cognitive disabilities, users with reading disabilities, users with motor impairments who need more time, screen reader users.
How to fix: Provide controls to pause, stop, or extend time limits, avoid auto-starting timers unless essential, allow users to control timing of content updates.

---

ID: ErrTimersWithoutControls
Type: Error
Impact: High
WCAG: 2.2.1 Timing Adjustable (Level A)
Description: Time-based content lacks user controls
Why it matters: Users need control over timed content to have enough time to read and interact with it.
Who it affects: Users with cognitive disabilities, users with reading disabilities, screen reader users.
How to fix: Provide controls to pause, stop, or extend time limits; avoid unnecessary time constraints.

---

ID: WarnFastInterval
Type: Warning
Impact: Medium
WCAG: 2.2.2 Pause, Stop, Hide (Level A)
Description: JavaScript interval running faster than once per second
Why it matters: Rapid updates can be distracting and difficult to process.
Who it affects: Users with cognitive disabilities, users with attention disorders.
How to fix: Slow down update intervals, provide pause controls for rapid updates.

---

### Typography

ID:  DiscoFontFound
Type: Discovery
Impact: N/A
WCAG: N/A
Category: fonts
Description: Font '{found}' detected in use on the page for accessibility review
Why it matters: Tracking font usage helps identify typography choices that may affect readability. Font '{found}' has been detected on this page. While not inherently an accessibility issue, certain fonts can be harder to read for users with dyslexia, low vision, or reading disabilities. This discovery item documents which fonts are in use so they can be evaluated for legibility, character distinction, and overall readability as part of a comprehensive accessibility review.
Who it affects: This information helps accessibility auditors and developers understand the typography landscape of the page, particularly relevant for users with dyslexia who benefit from clear sans-serif fonts, users with low vision who need good character distinction, and users with reading disabilities who benefit from consistent, readable typefaces
How to fix: No action required - this is informational only. The font '{found}' is currently in use. For accessibility best practices, consider using fonts with clear character distinction (avoiding ambiguous characters like I/l/1), adequate spacing between letters, and good readability at various sizes. Popular accessible fonts include Arial, Verdana, Tahoma, and specialized dyslexia-friendly fonts like OpenDyslexic. Document your font choices and test readability with actual users when possible.
```

---

## 9. TITLE & ARIA

### 9.1 Title Issues
```

---

ID: ErrSmallText
Type: Error
Impact: Medium
WCAG: 1.4.4 Resize text (Level AA)
Description: Text is too small to read comfortably (less than 12px)
Why it matters: Small text is difficult to read, especially for users with low vision or on mobile devices.
Who it affects: Users with low vision, aging users, mobile device users, users with reading disabilities.
How to fix: Use minimum 14px (preferably 16px) for body text, ensure text can be zoomed to 200% without loss of functionality.

---

ID:  WarnFontsizeIsBelow16px
Type: Warning
Impact: Medium
WCAG: 1.4.4
Category: fonts
Description: Font size is {fontSize}px, below recommended 16px minimum
Why it matters: Text at {fontSize}px is harder to read than the recommended minimum of 16px. Small text requires more effort to read and can cause eye strain, especially for extended reading.
Who it affects: Users with low vision, older users experiencing age-related vision changes, users with reading disabilities, and anyone viewing content on small screens
How to fix: Increase font size from {fontSize}px to at least 16px for body text. Consider using relative units (rem, em) for better scalability.
```

### 8.2 Font Discovery
```

---

ID: WarnItalicText
Type: Warning
Impact: Low
WCAG: 1.4.8 Visual Presentation (Level AAA)
Description: Italic text used extensively which can reduce readability
Why it matters: Italic text is harder to read, especially for users with dyslexia.
Who it affects: Users with dyslexia, users with low vision.
How to fix: Limit italic text to short emphasis, use bold for stronger emphasis.

---

ID: WarnJustifiedText
Type: Warning
Impact: Medium
WCAG: 1.4.8 Visual Presentation (Level AAA)
Description: Text uses full justification affecting readability
Why it matters: Justified text creates uneven spacing that makes reading difficult.
Who it affects: Users with dyslexia, users with cognitive disabilities.
How to fix: Use left-aligned text for body content, avoid full justification.

---

ID: WarnRightAlignedText
Type: Warning
Impact: Low
WCAG: 1.4.8 Visual Presentation (Level AAA)
Description: Body text is right-aligned affecting readability
Why it matters: Right-aligned text is difficult to read for extended content.
Who it affects: Users with dyslexia, users with reading disabilities.
How to fix: Use left alignment for body text in left-to-right languages.

---

ID: WarnSmallLineHeight
Type: Warning
Impact: Medium
WCAG: 1.4.12 Text Spacing (Level AA)
Description: Line height less than 1.5 times font size
Why it matters: Tight line spacing makes text difficult to read and track.
Who it affects: Users with dyslexia, users with low vision.
How to fix: Set line-height to at least 1.5 for body text.

---

