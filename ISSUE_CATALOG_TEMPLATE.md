asxz# Accessibility Issue Catalog - Complete List for Review

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
ID: ErrImageWithEmptyAlt
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
ID: ErrImageWithImgFileExtensionAlt
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
ID: ErrAltOnElementThatDoesntTakeIt
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
ID: DiscoFoundInlineSvg
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
ID: DiscoFoundSvgImage
Type: Discovery
Impact: N/A
WCAG: 1.1.1 Non-text Content (Level A)
Category: Images
Description: SVG element with role="img" detected that requires manual review to verify appropriate text alternatives are provided
Why it matters: SVG elements with role="img" are explicitly marked as images and treated as a single graphic by assistive technologies, requiring appropriate text alternatives. While the role="img" indicates developer awareness of accessibility needs, manual review is needed to verify that any aria-label, aria-labelledby, or internal <title> elements adequately describe the image's content or function, and that the description is appropriate for the SVG's context and purpose.
Who it affects: Blind and low vision users using screen readers who depend on text alternatives to understand image content, users with cognitive disabilities who benefit from clear, concise descriptions of visual information, keyboard users who may encounter the SVG in their navigation flow, and users of assistive technologies that treat role="img" SVGs as atomic image elements
How to fix: Verify the SVG with role="img" has appropriate accessible names through aria-label or aria-labelledby attributes, ensure any <title> or <desc> elements inside the SVG are properly referenced if used for labeling, confirm decorative SVGs are hidden with aria-hidden="true" rather than given role="img", check that the text alternative accurately describes the SVG's meaning in context, and test with screen readers to ensure the image is announced with meaningful information
```

### 1.7 URL used as ALT text

```
ID: ErrImageWithURLAsAlt
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
ID: ErrImageAltContainsHTML
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
ID: ErrUnlabelledField
Type: Error
Impact: High
3.3.2 Labels or Instructions (Level A)
Category: Forms
Description: Form input element lacks an accessible name through <label>, aria-label, aria-labelledby, or other labeling methods, leaving the field's purpose undefined for assistive technologies
Why it matters: Without labels, users cannot determine what information to enter, leading to form errors, abandoned transactions, and inability to complete critical tasks. Screen readers announce only the field type like "edit" or "combo box" without context, forcing users to guess based on surrounding content that may not be programmatically associated. This creates barriers for independent form completion and may result in users submitting incorrect information or being unable to proceed.
Who it affects: Blind and low vision users using screen readers who hear no field description when navigating forms, users with cognitive disabilities who need clear labels to understand what information is required, users with motor disabilities using voice control who cannot reference unlabeled fields by name, mobile users where placeholder text may disappear on focus, and users who rely on browser autofill features that depend on proper field labeling
How to fix: Add explicit <label> elements with for attribute matching the input's id (preferred method), use aria-label for simple labels when visual text isn't needed, implement aria-labelledby to reference existing visible text, ensure placeholder text is not the only labeling method as it disappears on input, wrap inputs and label text together for implicit association, and verify all form controls including select elements, textareas, and custom widgets have accessible names
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
WCAG: 1.3.1 Info and Relationships, 2.4.6 Headings and Labels
Category: forms
Description: Form element has no accessible name to describe its purpose
Why it matters: When a form lacks an accessible name, screen reader users hear only "form" without knowing what the form does - is it a search form, login form, contact form, or something else? Users navigating by landmarks or forms need to understand each form's purpose to decide whether to interact with it. This is especially important on pages with multiple forms. Without proper labeling, users might fill out the wrong form, skip important forms, or waste time exploring forms to understand their purpose.
Who it affects: Screen reader users navigating by forms or landmarks who need to identify form purposes, users with cognitive disabilities who need clear labels to understand what each form does, and keyboard users who tab through forms and need context about what they're interacting with
How to fix: Add an accessible name to the form element using aria-label (e.g., aria-label="Contact form") or aria-labelledby to reference a visible heading. If the form has a visible heading immediately before it, use aria-labelledby to point to that heading's ID. For search forms, "Search" is usually sufficient. The label should clearly indicate the form's purpose and be unique if there are multiple forms on the page.
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
ID: DiscoFormPage
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

### 2.6 Additional Form Issues

```
ID: ErrFormEmptyHasNoChildNodes
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
ID: ErrFormEmptyHasNoInteractiveElements
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
ID: ErrFieldLabelledUsinAriaLabel
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
ID: ErrFielLabelledBySomethingNotALabel
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
ID: WarnFieldLabelledByMulitpleElements
Type: Warning
Impact: Low
WCAG: 3.3.2
Category: forms
Description: Field is labeled by multiple elements via aria-labelledby
Why it matters: Multiple labels may be confusing or incorrectly concatenated
Who it affects: Screen reader users
How to fix: Ensure multiple labels make sense when read together
```

```
ID: WarnFieldLabelledByElementThatIsNotALabel
Type: Warning
Impact: Medium
WCAG: 1.3.1, 3.3.2
Category: forms
Description: Field labeled by element that is not semantically a label
Why it matters: Non-label elements may not convey proper semantic meaning
Who it affects: Screen reader users
How to fix: Use proper label elements or ensure aria-labelledby references appropriate content
```

```
ID: forms_ErrNoButtonText
Type: Error
Impact: High
WCAG: 2.4.6, 4.1.2
Category: forms
Description: Button has no accessible text
Why it matters: Users cannot determine button purpose
Who it affects: Screen reader users, voice control users
How to fix: Add text content, aria-label, or aria-labelledby to button
```

---

## 3. HEADINGS

### 3.1 Missing Headings
```
ID: ErrNoHeadingsOnPage
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
ID: ErrNoH1OnPage
Type: Error
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
ID: ErrEmptyHeading
Type: Error
Impact: High
WCAG: 1.3.1 Info and Relationships, 2.4.6 Headings and Labels
Category: headings
Description: Heading element (h1-h6) contains no text content or only whitespace
Why it matters: Empty headings disrupt document structure and navigation. Screen reader users rely on headings to understand page organization and navigate efficiently using heading shortcuts. An empty heading creates a navigation point with no information, confusing users about the page structure. It may indicate missing content or poor markup practices that affect the overall accessibility of the page.
Who it affects: Screen reader users who navigate by headings and cannot determine what section the empty heading represents, users with cognitive disabilities who rely on clear structure to understand content organization, and users of browser plugins or assistive technologies that generate page outlines
How to fix: Either add meaningful text content to the heading that describes the section it introduces, or remove the empty heading element entirely if it serves no structural purpose. Never use headings for visual spacing - use CSS margin/padding instead. Ensure all headings have descriptive text that helps users understand the content structure.
```

### 3.3 Heading Hierarchy
```
ID: ErrHeadingLevelsSkipped
Type: Error
Impact: Medium
WCAG: 1.3.1 Info and Relationships
Category: headings
Description: Heading levels are not in sequential order - one or more levels are skipped (e.g., h1 followed by h3 with no h2)
Why it matters: Heading levels create a hierarchical outline of your content, like nested bullet points. When you skip levels (jump from h1 to h3), you break this logical structure. It's like having chapter 1, then jumping to section 1.1.1 without section 1.1. Screen reader users navigating by headings will be confused about the relationship between sections - is the h3 a subsection of something that's missing? This broken hierarchy makes it hard to understand how content is organized and can cause users to think content is missing or that they've accidentally skipped something.
Who it affects: Screen reader users navigating by heading structure who rely on levels to understand content relationships, users with cognitive disabilities who need logical, predictable content organization, users of assistive technology that generates document outlines, and developers or content authors maintaining the page who need to understand the intended structure
How to fix: Always use heading levels sequentially. After h1, use h2 for the next level, then h3, and so on. Don't skip levels when going down (h1→h2→h3, not h1→h3). You can skip levels going back up (h3 can be followed by h2 for a new section). If you need a heading to look smaller visually, use CSS to style it rather than choosing a lower heading level. The heading level should reflect the content's logical structure, not its visual appearance.
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

```
ID: VisibleHeadingDoesNotMatchA11yName
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
ID: ErrNoMainLandmarkOnPage
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
ID: ErrNoBannerLandmarkOnPage
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
ID: WarnNoContentinfoLandmarkOnPage
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
ID: WarnNoNavLandmarksOnPage
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
ID: ErrMultipleMainLandmarksOnPage
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

### 4.6 Additional Landmark Issues

#### Main Landmark Issues
```
ID: ErrMainLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: ErrMainLandmarkHasTabindexOfZeroCanOnlyHaveMinusOneAtMost
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
ID: ErrMainLandmarkIsHidden
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
ID: ErrDuplicateLabelForComplementaryLandmark
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
ID: ErrComplementaryLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: ErrComplementaryLandmarkMayNotBeChildOfAnotherLandmark
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
ID: WarnComplementaryLandmarkHasNoLabel
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
ID: ErrComplementaryLandmarkAccessibleNameIsBlank
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
ID: WarnComplementaryLandmarkAccessibleNameUsesComplementary
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
ID: ErrDuplicateLabelForNavLandmark
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
ID: ErrNavLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: WarnNavLandmarkAccessibleNameUsesNavigation
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
ID: ErrCompletelyEmptyNavLandmark
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
ID: ErrNavLandmarkContainsOnlyWhiteSpace
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
ID: ErrDuplicateLabelForRegionLandmark
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
ID: ErrRegionLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: WarnRegionLandmarkHasNoLabelSoIsNotConsideredALandmark
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
ID: RegionLandmarkAccessibleNameIsBlank
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
ID: WarnRegionLandmarkAccessibleNameUsesNavigation
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
ID: ErrDuplicateLabelForBannerLandmark
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
ID: ErrBannerLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: WarnBannerLandmarkAccessibleNameUsesBanner
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
ID: WarnMultipleBannerLandmarksButNotAllHaveLabels
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
ID: ErrDuplicateLabelForContentinfoLandmark
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
ID: ErrContentInfoLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: ErrContentinfoLandmarkMayNotBeChildOfAnotherLandmark
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
ID: WarnContentInfoLandmarkHasNoLabel
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
ID: ErrContentInfoLandmarkAccessibleNameIsBlank
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
ID: WarnContentinfoLandmarkAccessibleNameUsesContentinfo
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
ID: WarnMultipleContentInfoLandmarksButNotAllHaveLabels
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
ID: WarnFormHasNoLabelSoIsNotLandmark
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
ID: ErrDuplicateLabelForFormLandmark
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
ID: ErrFormUsesAriaLabelInsteadOfVisibleElement
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
ID: ErrFormUsesTitleAttribute
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
ID: ErrFormAriaLabelledByIsBlank
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
ID: ErrFormAriaLabelledByReferenceDoesNotExist
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
ID: ErrFormAriaLabelledByReferenceDoesNotReferenceAHeading
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
ID: ErrFormAriaLabelledByReferenceDIsHidden
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
ID: ErrFormLandmarkHasAriaLabelAndAriaLabelledByAttrs
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
ID: ErrFormLandmarkAccessibleNameIsBlank
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
ID: WarnFormLandmarkAccessibleNameUsesForm
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
ID: ErrDuplicateLabelForSearchLandmark
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
ID: WarnHeadingFoundInsideLandmarkButDoesntLabelLandmark
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
ID: WarnHeadingFoundInLandmarkButIsLabelledByAnAriaLabelledBy
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
ID: WarnMultipleComplementaryLandmarksButNotAllHaveLabels
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
ID: WarnMultipleNavLandmarksButNotAllHaveLabels
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
ID: WarnMultipleRegionLandmarksButNotAllHaveLabels
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

### 5.1 Contrast Errors
```
ID: ErrTextContrast
Type: Error
Impact: High
WCAG: 1.4.3 Contrast (Minimum), 1.4.6 Contrast (Enhanced)
Category: color
Description: Text color has insufficient contrast ratio with its background color
Why it matters: Users with low vision, color blindness, or who are viewing content in bright sunlight may not be able to read text that doesn't have sufficient contrast with its background. This creates barriers to accessing information and can make content completely unreadable. Insufficient contrast is one of the most common accessibility issues and affects a large number of users.
Who it affects: Users with low vision who need higher contrast to distinguish text, users with color blindness who may have difficulty distinguishing certain color combinations, older users experiencing age-related vision changes, and any user viewing content in bright sunlight or on low-quality displays
How to fix: Ensure text has a contrast ratio of at least 4.5:1 with its background for normal text, or 3:1 for large text (18pt or 14pt bold). For enhanced accessibility (Level AAA), use 7:1 for normal text and 4.5:1 for large text. Use a contrast checking tool to verify ratios and test with actual users when possible. Consider providing a high contrast mode option.
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
Type: Warning
Impact: Low
WCAG: 1.4.3
Category: color
Description: Color-related styles defined inline
Why it matters: Harder to maintain consistent color scheme
Who it affects: Users needing high contrast modes
How to fix: Use CSS classes instead of inline styles
```

```
ID: ErrColorRelatedStyleDefinedExplicitlyInStyleTag
Type: Warning
Impact: Low
WCAG: 1.4.3
Category: color
Description: Color-related styles defined in style tag
Why it matters: Embedded color styles harder to override for user preferences
Who it affects: Users with custom stylesheets, high contrast mode users
How to fix: Use external stylesheets for better maintainability
```

---

## 6. LANGUAGE

### 6.1 Missing Language
```
ID: ErrNoPrimaryLangAttr
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

### 6.5 Additional Language Issues

```
ID: ErrRegionQualifierForPrimaryLangNotRecognized
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
ID: ErrEmptyXmlLangAttr
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
ID: ErrPrimaryXmlLangUnrecognized
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
ID: ErrRegionQualifierForPrimaryXmlLangNotRecognized
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
ID: ErrElementLangEmpty
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
ID: ErrElementRegionQualifierNotRecognized
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
ID: ErrHreflangAttrEmpty
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
ID: ErrPrimaryHrefLangNotRecognized
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
ID: ErrRegionQualifierForHreflangUnrecognized
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
ID: ErrOutlineIsNoneOnInteractiveElement
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
WCAG: 2.4.3 Focus Order
Category: focus
Description: Element uses a positive tabindex value (greater than 0)
Why it matters: Positive tabindex values override the natural tab order of the page, creating an unpredictable navigation experience. When you use tabindex="1" or higher, that element jumps to the front of the tab order, regardless of where it appears visually. This breaks the expected top-to-bottom, left-to-right flow that keyboard users rely on. Users might tab from the header straight to a random form field in the middle of the page, then jump to the footer, then back to the navigation. This confusing order makes it easy to miss content, difficult to predict where focus will go next, and nearly impossible to maintain as the page evolves.
Who it affects: Keyboard users who expect logical, predictable navigation order, screen reader users who rely on consistent focus flow, users with motor disabilities who need efficient keyboard navigation, users with cognitive disabilities who are confused by unpredictable focus movement, and developers maintaining the code who must manage complex tabindex values
How to fix: Remove positive tabindex values and use only tabindex="0" (adds element to natural tab order) or tabindex="-1" (removes from tab order but allows programmatic focus). Let the DOM order determine tab order - if elements need to be reached in a different order, rearrange them in the HTML. If visual order must differ from DOM order for design reasons, consider using CSS Grid or Flexbox with the order property, but be cautious as this can still cause accessibility issues.
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

```
ID: ErrTTabindexOnNonInteractiveElement
Type: Error
Impact: Medium
WCAG: 2.4.3
Category: focus
Description: Tabindex attribute on non-interactive element
Why it matters: Non-interactive elements should not be in tab order unless they serve a specific purpose
Who it affects: Keyboard users
How to fix: Remove tabindex from non-interactive elements or make them properly interactive
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
WCAG: 2.4.1 Bypass Blocks, 4.1.2 Name, Role, Value
Category: title
Description: Iframe element is missing the required title attribute
Why it matters: Iframes embed external content like videos, maps, or forms within your page. Without a title attribute, screen reader users hear only "iframe" with no indication of what content it contains. This is like having a door with no label - users don't know what's behind it. They must enter the iframe and explore its content to understand its purpose, which is time-consuming and may be confusing if the iframe content lacks context. For pages with multiple iframes, users cannot distinguish between them or decide which ones are worth exploring.
Who it affects: Screen reader users who need to understand what each iframe contains before deciding whether to interact with it, keyboard users navigating through iframes who need context about embedded content, users with cognitive disabilities who need clear labeling of all page regions, and users on slow connections who may experience delays loading iframe content
How to fix: Add a title attribute to every iframe that concisely describes its content or purpose (e.g., title="YouTube video: Product demonstration", title="Google Maps: Office location", title="Payment form"). The title should be unique if there are multiple iframes. Keep it brief but descriptive enough that users understand what the iframe contains without having to enter it. For decorative iframes (rare), you can use title="" and add tabindex="-1" to remove it from tab order.
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

## 11. BUTTONS

### 11.1 Button Contrast Issues
```
ID: ErrButtonTextLowContrast
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
ID: ErrButtonNoVisibleFocus
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
ID: WarnButtonGenericText
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
ID: ErrLinkTextNotDescriptive
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
ID: ErrLinkOpensNewWindowNoWarning
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
ID: WarnLinkLooksLikeButton
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
ID: DiscoPDFLinksFound
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
ID: ErrNoPageTitle
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
ID: ErrEmptyPageTitle
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
ID: ErrMultiplePageTitles
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