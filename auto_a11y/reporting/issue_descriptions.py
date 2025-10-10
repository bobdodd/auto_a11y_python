"""
Comprehensive accessibility issue descriptions with detailed explanations
"""

from typing import Dict, Any
from enum import Enum


class ImpactScale(Enum):
    """Impact scale for accessibility issues"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IssueDescription:
    """Detailed description of an accessibility issue"""
    
    def __init__(
        self,
        title: str,
        what: str,
        why: str,
        who: str,
        impact: ImpactScale,
        wcag: list,
        remediation: str
    ):
        self.title = title
        self.what = what
        self.why = why
        self.who = who
        self.impact = impact
        self.wcag = wcag
        self.remediation = remediation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'what': self.what,
            'why': self.why,
            'who': self.who,
            'impact': self.impact.value,
            'wcag': self.wcag,
            'remediation': self.remediation
        }


# Comprehensive mapping of all issue codes to detailed descriptions
ISSUE_DESCRIPTIONS = {
    # ============= HEADINGS ERRORS =============
    'headings_ErrEmptyHeading': IssueDescription(
        title="Empty Heading",
        what="A heading element (h1-h6 or role='heading') contains no text content.",
        why="Screen reader users rely on headings to navigate and understand page structure. Empty headings create confusion and break the logical document outline.",
        who="Screen reader users, users with cognitive disabilities who rely on clear structure",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1", "2.4.6"],
        remediation="""
        Remove empty headings or add descriptive text:
        
        Incorrect:
        <h2></h2>
        <h3> </h3>
        
        Correct:
        <h2>Product Features</h2>
        <h3>Advanced Settings</h3>
        
        If the heading is decorative, remove it entirely rather than leaving it empty.
        """
    ),
    
    'headings_ErrHeadingLevelsSkipped': IssueDescription(
        title="Skipped Heading Levels",
        what="The heading hierarchy skips one or more levels (e.g., h1 followed by h3).",
        why="Proper heading hierarchy helps users understand document structure and relationships between sections. Skipped levels break the logical outline and confuse navigation.",
        who="Screen reader users, users navigating by headings, users with cognitive disabilities",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1"],
        remediation="""
        Maintain sequential heading levels without skipping:
        
        Incorrect:
        <h1>Main Title</h1>
        <h3>Subsection</h3>  <!-- Skipped h2 -->
        
        Correct:
        <h1>Main Title</h1>
        <h2>Section</h2>
        <h3>Subsection</h3>
        
        Use CSS for visual styling rather than choosing heading levels based on appearance.
        """
    ),
    
    'headings_ErrHeadingsDontStartWithH1': IssueDescription(
        title="Page Doesn't Start with H1",
        what="The first heading on the page is not an h1 element.",
        why="Pages should start with h1 as the main heading, establishing the primary topic. Starting with a lower level heading breaks the expected document structure.",
        who="Screen reader users, users navigating by headings",
        impact=ImpactScale.MEDIUM,
        wcag=["1.3.1", "2.4.6"],
        remediation="""
        Start each page with an h1 that describes the main content:
        
        Incorrect:
        <h2>Welcome</h2>  <!-- First heading -->
        
        Correct:
        <h1>Welcome to Our Store</h1>
        <h2>Featured Products</h2>
        
        Each page should have exactly one h1 as the main heading.
        """
    ),
    
    'headings_ErrNoHeadingsOnPage': IssueDescription(
        title="No Headings on Page",
        what="The page contains no heading elements at all.",
        why="Headings provide structure and allow quick navigation. Pages without headings are difficult to scan and navigate, especially for screen reader users.",
        who="Screen reader users, users who scan content, users with cognitive disabilities",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1", "2.4.6"],
        remediation="""
        Add appropriate headings to structure your content:
        
        <h1>Page Title</h1>
        <h2>Main Section</h2>
        <h3>Subsection</h3>
        
        Use headings to break up content into logical sections. Don't use bold text or larger fonts as a substitute for proper heading elements.
        """
    ),
    
    'headings_ErrNoH1OnPage': IssueDescription(
        title="Missing H1 Heading",
        what="The page has headings but no h1 element.",
        why="Every page should have exactly one h1 that describes the main content. The h1 provides context and helps users understand what the page is about.",
        who="Screen reader users, SEO, users navigating by headings",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1", "2.4.6"],
        remediation="""
        Add a single h1 element that describes the main content:
        
        Incorrect:
        <h2>About Us</h2>
        <h3>Our History</h3>
        
        Correct:
        <h1>About Our Company</h1>
        <h2>Our History</h2>
        
        The h1 should be unique and descriptive of the page's main purpose.
        """
    ),
    
    'headings_ErrMultipleH1HeadingsOnPage': IssueDescription(
        title="Multiple H1 Headings",
        what="The page contains more than one h1 element.",
        why="Having multiple h1 elements confuses the document structure. There should be one main topic per page, represented by a single h1.",
        who="Screen reader users, users navigating by headings, SEO",
        impact=ImpactScale.MEDIUM,
        wcag=["1.3.1"],
        remediation="""
        Use only one h1 per page, with h2-h6 for subsections:
        
        Incorrect:
        <h1>Welcome</h1>
        <h1>Our Services</h1>
        <h1>Contact Us</h1>
        
        Correct:
        <h1>Welcome to Our Company</h1>
        <h2>Our Services</h2>
        <h2>Contact Us</h2>
        
        If you have multiple independent sections, consider if they should be separate pages.
        """
    ),
    
    # ============= HEADINGS WARNINGS =============
    'headings_WarnHeadingInsideDisplayNone': IssueDescription(
        title="Hidden Heading",
        what="A heading element is hidden using display:none or similar CSS.",
        why="Hidden headings may be read by some screen readers but not others, creating inconsistent experiences. They don't provide visual structure for sighted users.",
        who="Screen reader users (inconsistent behavior), sighted users who scan content",
        impact=ImpactScale.LOW,
        wcag=["1.3.1"],
        remediation="""
        Remove hidden headings or make them visible:
        
        Incorrect:
        <h2 style="display:none">Section Title</h2>
        
        Correct options:
        1. Make it visible: <h2>Section Title</h2>
        2. Remove it entirely if not needed
        3. Use aria-label on the section instead if labeling for screen readers only
        
        If you need to visually hide but keep for screen readers, use:
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
            border: 0;
        }
        """
    ),
    
    'headings_WarnHeadingOver60CharsLong': IssueDescription(
        title="Heading Too Long",
        what="A heading contains more than 60 characters.",
        why="Long headings are difficult to scan and understand quickly. They should be concise and descriptive. Screen reader users hearing long headings repeatedly can find navigation tedious.",
        who="All users, especially screen reader users and users with cognitive disabilities",
        impact=ImpactScale.LOW,
        wcag=["2.4.6"],
        remediation="""
        Keep headings concise and under 60 characters:
        
        Incorrect:
        <h2>Complete Guide to Understanding and Implementing Advanced Accessibility Features in Modern Web Applications</h2>
        
        Correct:
        <h2>Web Accessibility Implementation Guide</h2>
        <p>Learn to implement advanced accessibility features in modern applications.</p>
        
        Move detailed information to paragraph text below the heading.
        """
    ),
    
    # ============= FORMS ERRORS =============
    'forms_ErrUnlabelledField': IssueDescription(
        title="Unlabeled Form Field",
        what="A form input field has no associated label.",
        why="Labels tell users what information to enter. Without labels, screen reader users hear only the field type (e.g., 'edit text') with no context about what to input.",
        who="Screen reader users, voice control users, users with cognitive disabilities",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1", "3.3.2", "4.1.2"],
        remediation="""
        Associate every form field with a label:
        
        Method 1 - Label element:
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email">
        
        Method 2 - Wrapped label:
        <label>
            Email Address
            <input type="email" name="email">
        </label>
        
        Method 3 - aria-label (use sparingly):
        <input type="search" aria-label="Search products">
        
        Method 4 - aria-labelledby:
        <h2 id="billing">Billing Address</h2>
        <input type="text" aria-labelledby="billing street">
        <span id="street">Street Address</span>
        """
    ),
    
    'forms_ErrFormEmptyHasNoChildNodes': IssueDescription(
        title="Empty Form",
        what="A form element exists but contains no content or form fields.",
        why="Empty forms serve no purpose and may confuse users. Screen readers announce the form but users find nothing to interact with.",
        who="All users, especially screen reader users",
        impact=ImpactScale.MEDIUM,
        wcag=["1.3.1"],
        remediation="""
        Remove empty forms or add appropriate content:
        
        Incorrect:
        <form></form>
        
        Correct:
        <form>
            <label for="name">Name</label>
            <input type="text" id="name" name="name">
            <button type="submit">Submit</button>
        </form>
        
        If the form is populated dynamically, ensure it has content before rendering or provide a loading state.
        """
    ),
    
    # ============= FORMS WARNINGS =============
    'forms_WarnFormHasNoLabel': IssueDescription(
        title="Form Without Accessible Name",
        what="A form element lacks an accessible name (no aria-label or aria-labelledby).",
        why="Forms with accessible names help users understand the form's purpose, especially when multiple forms exist on a page. Screen readers can announce the form's purpose.",
        who="Screen reader users navigating between forms",
        impact=ImpactScale.LOW,
        wcag=["1.3.1"],
        remediation="""
        Provide an accessible name for forms when beneficial:
        
        <form aria-label="Contact Form">
            <!-- form fields -->
        </form>
        
        Or using aria-labelledby:
        <h2 id="contact-heading">Contact Us</h2>
        <form aria-labelledby="contact-heading">
            <!-- form fields -->
        </form>
        
        This is especially important when multiple forms exist on the same page.
        """
    ),
    
    # ============= FORMS DISCOVERY =============
    'forms_DiscoFormOnPage': IssueDescription(
        title="Form Detected",
        what="A form element was found on the page.",
        why="Forms require manual testing to ensure all fields are properly labeled, validation messages are accessible, and the form can be submitted using keyboard only.",
        who="All users interacting with forms",
        impact=ImpactScale.MEDIUM,
        wcag=["1.3.1", "3.3.1", "3.3.2", "3.3.3", "3.3.4"],
        remediation="""
        Manually test the form for:
        1. All fields have labels
        2. Required fields are indicated accessibly
        3. Error messages are associated with fields
        4. Form can be completed using keyboard only
        5. Submit button is clearly labeled
        6. Success/error feedback is announced
        
        Example of accessible form structure:
        <form aria-label="Newsletter Signup">
            <label for="email">
                Email Address
                <span aria-label="required">*</span>
            </label>
            <input type="email" id="email" name="email" required aria-describedby="email-error">
            <span id="email-error" role="alert"></span>
            <button type="submit">Subscribe</button>
        </form>
        """
    ),
    
    # ============= IMAGES ERRORS =============
    'images_ErrImageWithNoAlt': IssueDescription(
        title="Image Missing Alt Attribute",
        what="An img element has no alt attribute at all.",
        why="The alt attribute is required for all images. It provides text alternatives for users who cannot see images. Without it, screen readers may read the filename, which is usually meaningless.",
        who="Screen reader users, users with images disabled, users on slow connections",
        impact=ImpactScale.HIGH,
        wcag=["1.1.1"],
        remediation="""
        Add an alt attribute to every image:
        
        Incorrect:
        <img src="logo.png">
        
        Correct for informative images:
        <img src="logo.png" alt="Company Name Logo">
        
        Correct for decorative images:
        <img src="decoration.png" alt="">
        
        Guidelines:
        - Informative images: Describe the content/function
        - Decorative images: Use empty alt=""
        - Complex images: Provide detailed description elsewhere and reference it
        """
    ),
    
    'images_ErrImageWithEmptyAlt': IssueDescription(
        title="Empty Alt Text on Informative Image",
        what="An image that appears to convey information has an empty alt attribute.",
        why="Empty alt attributes should only be used for decorative images. Informative images need descriptions so users understand the content being conveyed.",
        who="Screen reader users, users who cannot see images",
        impact=ImpactScale.HIGH,
        wcag=["1.1.1"],
        remediation="""
        Provide descriptive alt text for informative images:
        
        Incorrect for informative image:
        <img src="sales-chart.png" alt="">
        
        Correct:
        <img src="sales-chart.png" alt="Bar chart showing 30% sales increase from 2023 to 2024">
        
        Only use empty alt for truly decorative images:
        <img src="decorative-border.png" alt="">
        
        Ask yourself: If the image wasn't there, what would I need to know?
        """
    ),
    
    # ============= LANGUAGE ERRORS =============
    # ============= LANDMARKS ERRORS =============
    'landmarks_ErrNoMainLandmarkOnPage': IssueDescription(
        title="Missing Main Landmark",
        what="The page has no <main> element or role='main' landmark.",
        why="The main landmark identifies the primary content area, allowing users to skip repeated content like navigation. It's essential for efficient keyboard navigation.",
        who="Screen reader users, keyboard users, users with motor disabilities",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1", "2.4.1"],
        remediation="""
        Add a main landmark for primary content:
        
        Incorrect structure:
        <nav>...</nav>
        <div class="content">...</div>
        <footer>...</footer>
        
        Correct structure:
        <nav>...</nav>
        <main>
            <!-- Primary page content here -->
        </main>
        <footer>...</footer>
        
        Or using role:
        <div role="main">
            <!-- Primary page content here -->
        </div>
        
        Only one main landmark should exist per page, and it should not be nested in other landmarks.
        """
    ),
    
    'landmarks_ErrMultipleMainLandmarksOnPage': IssueDescription(
        title="Multiple Main Landmarks",
        what="The page contains more than one main landmark.",
        why="There should be only one main content area per page. Multiple main landmarks confuse the page structure and make navigation unpredictable.",
        who="Screen reader users, keyboard users",
        impact=ImpactScale.HIGH,
        wcag=["1.3.1"],
        remediation="""
        Use only one main landmark:
        
        Incorrect:
        <main>Content 1</main>
        <main>Content 2</main>
        
        Correct:
        <main>
            <section>Content 1</section>
            <section>Content 2</section>
        </main>
        
        If you have multiple distinct content areas, use sections or articles within the single main landmark.
        """
    ),
    
    # ============= TABINDEX ERRORS =============
    'tabindex_ErrNegativeTabIndex': IssueDescription(
        title="Negative Tabindex",
        what="An element has a negative tabindex value (e.g., tabindex='-1').",
        why="Negative tabindex removes elements from keyboard navigation. While sometimes appropriate for programmatic focus, it often prevents keyboard users from accessing interactive elements.",
        who="Keyboard users, users with motor disabilities",
        impact=ImpactScale.HIGH,
        wcag=["2.1.1", "2.4.3"],
        remediation="""
        Avoid negative tabindex on interactive elements:
        
        Incorrect:
        <button tabindex="-1">Submit</button>
        <a href="/home" tabindex="-1">Home</a>
        
        Correct:
        <button>Submit</button>  <!-- Natural tab order -->
        <a href="/home">Home</a>
        
        Only use tabindex="-1" for:
        1. Elements that receive programmatic focus (e.g., error messages)
        2. Removing decorative elements from tab order
        3. Skip links targets
        
        Example of appropriate use:
        <div id="error-message" tabindex="-1" role="alert">
            <!-- Focused programmatically when error occurs -->
        </div>
        """
    ),
    
    'tabindex_ErrPositiveTabIndex': IssueDescription(
        title="Positive Tabindex",
        what="An element has a positive tabindex value (e.g., tabindex='1').",
        why="Positive tabindex values override the natural tab order, creating an unpredictable navigation experience. Users expect to tab through elements in the order they appear visually.",
        who="Keyboard users, screen reader users",
        impact=ImpactScale.HIGH,
        wcag=["2.4.3"],
        remediation="""
        Use natural document order instead of positive tabindex:
        
        Incorrect:
        <input tabindex="3" type="text">
        <input tabindex="1" type="email">
        <input tabindex="2" type="tel">
        
        Correct:
        <!-- Arrange elements in logical order in HTML -->
        <input type="email">
        <input type="tel">
        <input type="text">
        
        If you need to change visual order, use CSS while maintaining logical HTML order:
        .form {
            display: flex;
            flex-direction: column;
        }
        .email-field { order: 1; }
        .tel-field { order: 2; }
        .text-field { order: 3; }
        """
    ),
    
    # ============= COLOR/CONTRAST ERRORS =============
    'color_ErrTextContrast': IssueDescription(
        title="Insufficient Text Contrast",
        what="Text color contrast against its background is below WCAG requirements.",
        why="Low contrast makes text difficult or impossible to read, especially for users with low vision, color blindness, or in bright light conditions.",
        who="Users with low vision, color blind users, aging users, all users in poor lighting",
        impact=ImpactScale.HIGH,
        wcag=["1.4.3", "1.4.6"],
        remediation="""
        Ensure sufficient color contrast ratios:
        
        WCAG AA Requirements:
        - Normal text: 4.5:1 minimum
        - Large text (18pt+, or 14pt+ bold): 3:1 minimum
        
        WCAG AAA Requirements:
        - Normal text: 7:1 minimum
        - Large text: 4.5:1 minimum
        
        Examples of good contrast:
        - Black (#000000) on white (#FFFFFF): 21:1
        - Dark gray (#333333) on white (#FFFFFF): 12.6:1
        - Dark blue (#003366) on white (#FFFFFF): 11.4:1
        
        Tools to check contrast:
        - WebAIM Contrast Checker
        - Chrome DevTools (Lighthouse)
        - Colour Contrast Analyser
        
        CSS example:
        /* Good contrast */
        .text {
            color: #333333;  /* Dark gray */
            background-color: #FFFFFF;  /* White */
        }
        """
    ),
    
    # ============= DISCOVERY ITEMS =============
    'fonts_DiscoFontFound': IssueDescription(
        title="Font Usage Detected",
        what="Custom fonts are being used on the page.",
        why="Some fonts can be difficult to read for users with dyslexia or reading difficulties. Font size and spacing also affect readability.",
        who="Users with dyslexia, users with reading difficulties, users with low vision",
        impact=ImpactScale.LOW,
        wcag=["1.4.8", "1.4.12"],
        remediation="""
        Review font choices for readability:
        
        Recommended accessible fonts:
        - Sans-serif: Arial, Helvetica, Verdana, Calibri
        - Serif: Georgia, Times New Roman
        - Monospace: Consolas, Monaco, Courier New
        
        Best practices:
        1. Minimum font size: 16px for body text
        2. Line height: 1.5x font size minimum
        3. Paragraph spacing: 2x font size
        4. Avoid all caps for long text
        5. Allow users to change fonts if needed
        
        CSS example:
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            letter-spacing: 0.02em;
        }
        """
    ),
    
    'color_DiscoStyleElementOnPage': IssueDescription(
        title="Inline Styles Detected",
        what="Style elements or inline styles are present on the page.",
        why="Inline styles can override user stylesheets and make it harder for users to customize appearance for their needs (high contrast, larger text, etc.).",
        who="Users with custom stylesheets, users needing high contrast or large text",
        impact=ImpactScale.LOW,
        wcag=["1.4.4", "1.4.8"],
        remediation="""
        Use external CSS files instead of inline styles:
        
        Avoid:
        <div style="color: red; font-size: 12px;">Text</div>
        <style>
            .text { color: red; }
        </style>
        
        Prefer:
        <!-- In HTML -->
        <div class="error-text">Text</div>
        
        /* In external CSS file */
        .error-text {
            color: #cc0000;
            font-size: 1rem;
        }
        
        Benefits:
        - Users can override with their own styles
        - Better maintainability
        - Consistent styling across pages
        - Improved performance (caching)
        """
    ),
}


def get_issue_description(issue_code: str) -> IssueDescription:
    """
    Get detailed description for an issue code
    
    Args:
        issue_code: The issue code (e.g., 'headings_ErrEmptyHeading')
        
    Returns:
        IssueDescription object or None if not found
    """
    return ISSUE_DESCRIPTIONS.get(issue_code)


def get_wcag_link(criterion: str) -> str:
    """
    Get WCAG documentation link for a criterion
    
    Args:
        criterion: WCAG criterion number (e.g., '1.3.1')
        
    Returns:
        URL to WCAG documentation
    """
    base_url = "https://www.w3.org/WAI/WCAG21/Understanding/"
    
    # Map common criteria to their documentation pages
    criterion_map = {
        "1.1.1": "non-text-content",
        "1.3.1": "info-and-relationships",
        "1.4.3": "contrast-minimum",
        "1.4.4": "resize-text",
        "1.4.6": "contrast-enhanced",
        "1.4.8": "visual-presentation",
        "1.4.12": "text-spacing",
        "2.1.1": "keyboard",
        "2.4.1": "bypass-blocks",
        "2.4.2": "page-titled",
        "2.4.3": "focus-order",
        "2.4.6": "headings-and-labels",
        "2.4.7": "focus-visible",
        "3.1.1": "language-of-page",
        "3.3.1": "error-identification",
        "3.3.2": "labels-or-instructions",
        "3.3.3": "error-suggestion",
        "3.3.4": "error-prevention-legal-financial-data",
        "4.1.2": "name-role-value"
    }
    
    page = criterion_map.get(criterion, "")
    if page:
        return f"{base_url}{page}.html"
    return f"{base_url}"