"""
Enhanced accessibility issue descriptions with detailed, context-specific explanations
"""

from typing import Dict, Any, Optional
from enum import Enum


class ImpactScale(Enum):
    """Impact scale for accessibility issues"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


def get_detailed_issue_description(issue_code: str, metadata: Dict[str, Any]) -> Dict[str, str]:
    """
    Get detailed, context-specific description for an issue
    
    Args:
        issue_code: The issue code (e.g., 'headings_ErrEmptyHeading')
        metadata: Additional context about the specific issue instance
        
    Returns:
        Dictionary with detailed description fields
    """
    
    # Extract the error type from the issue code
    if '_' in issue_code:
        category, error_type = issue_code.split('_', 1)
    else:
        category = 'unknown'
        error_type = issue_code
    
    # Generate context-specific descriptions based on the error type and metadata
    descriptions = {
        # ============= HEADINGS ERRORS =============
        'ErrEmptyHeading': {
            'title': 'Empty heading element',
            'what': f"A heading element at {metadata.get('xpath', 'unknown location')} contains no text content. The heading tag exists but is completely empty.",
            'why': "Screen reader users rely on headings to understand page structure and navigate efficiently. An empty heading creates a confusing gap in the document outline, announces as 'heading' with no context, and breaks the logical flow of content.",
            'who': "Screen reader users who navigate by headings, users with cognitive disabilities who rely on clear structure, keyboard users using heading navigation shortcuts",
            'impact': ImpactScale.HIGH.value,
            'wcag': ["1.3.1 Info and Relationships", "2.4.6 Headings and Labels"],
            'remediation': f"""
Either remove the empty heading element or add meaningful text content.

Current code (empty heading):
<{metadata.get('element', 'h2')}></{metadata.get('element', 'h2')}>

Option 1 - Add meaningful content:
<{metadata.get('element', 'h2')}>Section Title</{metadata.get('element', 'h2')}>

Option 2 - Remove if not needed:
Delete the empty heading element entirely if it serves no purpose.

Note: Empty headings often occur from CMS templates or dynamic content. Ensure your content generation logic handles empty states properly.
            """
        },
        
        'ErrHeadingLevelsSkipped': {
            'title': f"Heading hierarchy skips from level {metadata.get('from', '?')} to {metadata.get('to', '?')}",
            'what': f"The heading structure jumps from an h{metadata.get('from', '?')} directly to an h{metadata.get('to', '?')} at {metadata.get('xpath', 'unknown location')}, skipping intermediate heading level(s).",
            'why': "Proper heading hierarchy helps users understand the relationship between different sections. Skipped levels break the logical document outline, making it difficult for screen reader users to understand content organization and navigate effectively.",
            'who': "Screen reader users navigating by headings, users with cognitive disabilities who rely on logical structure, users creating mental models of page content",
            'impact': ImpactScale.HIGH.value,
            'wcag': ["1.3.1 Info and Relationships"],
            'remediation': f"""
Maintain sequential heading levels without skipping.

Current structure (incorrect):
<h{metadata.get('from', '1')}>Main Section</h{metadata.get('from', '1')}>
<h{metadata.get('to', '3')}>Subsection</h{metadata.get('to', '3')}>  <!-- Skips h{int(metadata.get('from', 1)) + 1} -->

Corrected structure:
<h{metadata.get('from', '1')}>Main Section</h{metadata.get('from', '1')}>
<h{int(metadata.get('from', 1)) + 1}>Section</h{int(metadata.get('from', 1)) + 1}>
<h{metadata.get('to', '3')}>Subsection</h{metadata.get('to', '3')}>

Remember: Choose heading levels based on document structure, not visual appearance. Use CSS for styling.
            """
        },
        
        'ErrMultipleH1HeadingsOnPage': {
            'title': f"Multiple H1 headings found ({metadata.get('found', 'multiple')} instances)",
            'what': f"The page contains {metadata.get('found', 'multiple')} H1 heading elements instead of the single H1 that should represent the main page topic.",
            'why': "The H1 heading should uniquely identify the main content of the page. Multiple H1s create ambiguity about the page's primary purpose, confuse the document structure, and make it difficult for users to understand the content hierarchy.",
            'who': "Screen reader users, SEO crawlers, users scanning for main content, users with cognitive disabilities",
            'impact': ImpactScale.MEDIUM.value,
            'wcag': ["1.3.1 Info and Relationships", "2.4.6 Headings and Labels"],
            'remediation': f"""
Use only one H1 per page for the main title, with H2-H6 for subsections.

Current structure (incorrect - {metadata.get('found', 'multiple')} H1s):
<h1>Welcome</h1>
<h1>Our Services</h1>
<h1>Contact Us</h1>

Corrected structure:
<h1>Welcome to [Company Name]</h1>  <!-- Single main heading -->
<h2>Our Services</h2>               <!-- Subsection -->
<h2>Contact Us</h2>                 <!-- Subsection -->

The H1 should describe the main purpose of the entire page.
            """
        },
        
        'WarnHeadingOver60CharsLong': {
            'title': 'Heading text exceeds recommended length',
            'what': f"A heading at {metadata.get('xpath', 'unknown location')} contains {len(metadata.get('headingText', ''))} characters: \"{metadata.get('headingText', 'N/A')[:100]}{'...' if len(metadata.get('headingText', '')) > 100 else ''}\"",
            'why': "Long headings are difficult to scan quickly and understand at a glance. Screen reader users hearing lengthy headings repeatedly during navigation experience fatigue. Long headings also often indicate unclear content organization.",
            'who': "All users scanning content, screen reader users navigating by headings, users with cognitive disabilities, mobile users with limited screen space",
            'impact': ImpactScale.LOW.value,
            'wcag': ["2.4.6 Headings and Labels"],
            'remediation': f"""
Shorten the heading to be concise (under 60 characters) while maintaining clarity.

Current heading ({len(metadata.get('headingText', ''))} characters):
<h2>{metadata.get('headingText', 'N/A')}</h2>

Suggested improvement:
<h2>[Shorter, clearer version under 60 chars]</h2>
<p>[Move additional details to paragraph text]</p>

Tips for concise headings:
- Focus on key words
- Remove unnecessary articles (a, an, the)
- Move details to paragraph text
- Use descriptive but brief language
            """
        },
        
        # ============= FORMS ERRORS =============
        'ErrUnlabelledField': {
            'title': f"Form field missing label",
            'what': f"A form input field at {metadata.get('xpath', 'unknown location')} has no associated label to identify its purpose. The field type is '{metadata.get('element', 'input')}' but users have no way to know what information to enter.",
            'why': "Labels are essential for form accessibility. Without labels, screen reader users only hear the field type (like 'edit text') with no context about what to input. Voice control users cannot target the field by name. Users with cognitive disabilities cannot understand the field's purpose.",
            'who': "Screen reader users, voice control users, users with cognitive disabilities, users with motor disabilities using speech input",
            'impact': ImpactScale.HIGH.value,
            'wcag': ["1.3.1 Info and Relationships", "3.3.2 Labels or Instructions", "4.1.2 Name, Role, Value"],
            'remediation': f"""
Add a label to identify the form field's purpose.

Current code (unlabeled):
<input type="{metadata.get('inputType', 'text')}" name="{metadata.get('name', 'field')}">

Option 1 - Using label element (recommended):
<label for="unique-id">Field Label</label>
<input type="{metadata.get('inputType', 'text')}" id="unique-id" name="{metadata.get('name', 'field')}">

Option 2 - Wrapping label:
<label>
  Field Label
  <input type="{metadata.get('inputType', 'text')}" name="{metadata.get('name', 'field')}">
</label>

Option 3 - aria-label (use sparingly):
<input type="{metadata.get('inputType', 'text')}" 
       aria-label="Field Label" 
       name="{metadata.get('name', 'field')}">

Note: Placeholder text is NOT a substitute for labels as it disappears when users start typing.
            """
        },
        
        # ============= FORMS DISCOVERY =============
        'DiscoFormOnPage': {
            'title': 'Form detected for manual review',
            'what': f"A form element was detected at {metadata.get('xpath', 'unknown location')}. While automated testing found this form, it requires manual review to ensure full accessibility.",
            'why': "Forms are complex interactive elements that need comprehensive accessibility testing. Automated tools cannot verify all aspects like error handling, validation messages, keyboard navigation flow, and submit confirmation.",
            'who': "All users interacting with forms, especially those using assistive technologies",
            'impact': ImpactScale.MEDIUM.value,
            'wcag': ["1.3.1 Info and Relationships", "3.3.1 Error Identification", "3.3.2 Labels or Instructions", "3.3.3 Error Suggestion", "3.3.4 Error Prevention"],
            'remediation': """
Manually test the following aspects of this form:

1. Labels and Instructions:
   - All fields have clear, associated labels
   - Required fields are clearly indicated
   - Instructions are provided where needed

2. Error Handling:
   - Error messages are clear and specific
   - Errors are announced to screen readers
   - Fields with errors are clearly identified
   - Suggestions for correction are provided

3. Keyboard Navigation:
   - All fields accessible via keyboard
   - Logical tab order
   - Submit button reachable via keyboard
   - No keyboard traps

4. Validation:
   - Client-side validation is accessible
   - Success messages are announced
   - Form submission confirmation is clear

5. Additional Checks:
   - Fieldsets group related fields
   - Progress indicators for multi-step forms
   - Clear submit button text
   - Confirmation before destructive actions
            """
        },
        
        # ============= IMAGES ERRORS =============
        'ErrImageWithNoAlt': {
            'title': 'Image missing alt attribute',
            'what': f"An image at {metadata.get('xpath', 'unknown location')} has no alt attribute. The image source is '{metadata.get('src', 'unknown')}' but provides no text alternative.",
            'why': "The alt attribute is required for all images. Without it, screen reader users have no information about the image content. The screen reader may announce the filename instead, which is typically meaningless (like 'IMG_12345.jpg').",
            'who': "Screen reader users, users with images disabled, users on slow connections, search engines",
            'impact': ImpactScale.HIGH.value,
            'wcag': ["1.1.1 Non-text Content"],
            'remediation': f"""
Add an appropriate alt attribute to the image.

Current code (missing alt):
<img src="{metadata.get('src', 'image.jpg')}">

For informative images (convey content):
<img src="{metadata.get('src', 'image.jpg')}" alt="Description of what the image shows">

For decorative images (no information):
<img src="{metadata.get('src', 'image.jpg')}" alt="">

For complex images (charts, diagrams):
<img src="{metadata.get('src', 'image.jpg')}" alt="Brief description" aria-describedby="detailed-desc">
<div id="detailed-desc">Full description of the complex image...</div>

Guidelines:
- Be concise but descriptive
- Don't start with "Image of" or "Picture of"
- Consider the image's context and purpose
- Empty alt="" only for purely decorative images
            """
        },
        
        # ============= LANGUAGE ERRORS =============
        'ErrNoPrimaryLangAttr': {
            'title': 'Page language not declared',
            'what': "The HTML element lacks a lang attribute to declare the page's primary language.",
            'why': "Screen readers need the lang attribute to use the correct pronunciation rules. Without it, content may be pronounced incorrectly, making it incomprehensible. For example, English words might be pronounced with French pronunciation rules, or vice versa.",
            'who': "Screen reader users, automatic translation tools, search engines for international content",
            'impact': ImpactScale.HIGH.value,
            'wcag': ["3.1.1 Language of Page"],
            'remediation': """
Add the appropriate lang attribute to the html element.

Current code (missing lang):
<!DOCTYPE html>
<html>

Corrected code:
<!DOCTYPE html>
<html lang="en">  <!-- For English -->

Common language codes:
- lang="en" - English
- lang="en-US" - US English
- lang="en-GB" - British English
- lang="es" - Spanish
- lang="fr" - French
- lang="de" - German
- lang="zh" - Chinese
- lang="ja" - Japanese
- lang="ar" - Arabic
- lang="hi" - Hindi

Use the correct ISO 639-1 code for your content's primary language.
            """
        },
        
        # ============= COLOR/CONTRAST ERRORS =============
        'ErrTextContrast': {
            'title': f"Insufficient color contrast (ratio: {metadata.get('contrastRatio', 'unknown')})",
            'what': f"Text at {metadata.get('xpath', 'unknown location')} has insufficient contrast. The foreground color '{metadata.get('foreground', 'unknown')}' against background '{metadata.get('background', 'unknown')}' results in a contrast ratio of {metadata.get('contrastRatio', 'unknown')}:1.",
            'why': "Sufficient color contrast ensures text is readable for users with low vision, color blindness, or in challenging lighting conditions. Low contrast text is difficult or impossible to read for many users.",
            'who': "Users with low vision, color blind users, aging users with reduced contrast sensitivity, all users in bright sunlight or glare",
            'impact': ImpactScale.HIGH.value,
            'wcag': ["1.4.3 Contrast (Minimum)", "1.4.6 Contrast (Enhanced)"],
            'remediation': f"""
Increase the contrast ratio to meet WCAG requirements.

Current colors:
- Foreground: {metadata.get('foreground', '#666666')}
- Background: {metadata.get('background', '#FFFFFF')}
- Contrast ratio: {metadata.get('contrastRatio', 'unknown')}:1

WCAG Requirements:
- Normal text: 4.5:1 minimum (AA), 7:1 (AAA)
- Large text (18pt+/14pt+ bold): 3:1 minimum (AA), 4.5:1 (AAA)

Suggested improvements:
1. Darken the text color
2. Lighten the background
3. Increase font size/weight if appropriate

Example fix:
/* Current (insufficient) */
.text {{
    color: {metadata.get('foreground', '#666666')};
    background: {metadata.get('background', '#FFFFFF')};
}}

/* Improved (meets WCAG AA) */
.text {{
    color: #333333;  /* Darker text */
    background: #FFFFFF;
}}

Use a contrast checker tool to verify your color choices meet requirements.
            """
        }
    }
    
    # Get the specific description for this error type
    if error_type in descriptions:
        return descriptions[error_type]
    
    # Default fallback
    return {
        'title': f"Accessibility issue: {error_type}",
        'what': f"An accessibility issue of type '{error_type}' was detected at {metadata.get('xpath', 'unknown location')}.",
        'why': "This issue may create barriers for users with disabilities.",
        'who': "Users with disabilities",
        'impact': ImpactScale.MEDIUM.value,
        'wcag': ["Multiple criteria may apply"],
        'remediation': "Review the specific issue and apply appropriate accessibility fixes."
    }


def format_issue_for_display(issue_code: str, violation_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format an issue with all its metadata for display
    
    Args:
        issue_code: The issue code
        violation_data: The raw violation data from JavaScript tests
        
    Returns:
        Formatted issue description
    """
    # Get the detailed description using the metadata
    description = get_detailed_issue_description(issue_code, violation_data)
    
    # Add any additional runtime data
    description['issue_id'] = issue_code
    description['location'] = violation_data.get('xpath', 'Not specified')
    description['element'] = violation_data.get('element', 'Not specified')
    description['url'] = violation_data.get('url', 'Not specified')
    
    return description