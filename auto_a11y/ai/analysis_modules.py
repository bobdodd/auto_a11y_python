"""
Specific AI analysis modules for different accessibility aspects
"""

import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, NavigableString
import re

logger = logging.getLogger(__name__)


def find_element_xpath_by_text(html: str, text_sample: str) -> Optional[str]:
    """
    Find an element in HTML by its text content and return a precise xpath.
    
    Args:
        html: The HTML content to search
        text_sample: The text to find
        
    Returns:
        XPath string or None if not found
    """
    if not html or not text_sample:
        return None
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Clean the text sample for comparison
    clean_text = text_sample.strip()
    
    # Find elements containing this text
    # First try exact match, then partial match
    for element in soup.find_all(string=lambda t: t and clean_text in t):
        if isinstance(element, NavigableString):
            parent = element.parent
            if parent and parent.name:
                xpath = _build_xpath_for_element(parent, soup)
                if xpath:
                    return xpath
    
    # Also try finding by normalized text in elements
    for tag in ['p', 'span', 'div', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'label', 'button']:
        for element in soup.find_all(tag):
            element_text = element.get_text(strip=True)
            if clean_text in element_text:
                xpath = _build_xpath_for_element(element, soup)
                if xpath:
                    return xpath
    
    return None


def _build_xpath_for_element(element, soup) -> Optional[str]:
    """
    Build a precise xpath for a BeautifulSoup element.
    
    Args:
        element: BeautifulSoup element
        soup: Root soup object
        
    Returns:
        XPath string
    """
    if not element or not element.name:
        return None
    
    tag = element.name
    
    # Priority 1: ID (most specific)
    if element.get('id'):
        return f"//*[@id='{element.get('id')}']"
    
    # Priority 2: Unique class combination
    classes = element.get('class', [])
    if classes:
        class_str = ' '.join(classes)
        # Check if this class combo is unique
        matching = soup.find_all(tag, class_=classes)
        if len(matching) == 1:
            if len(classes) == 1:
                return f"//{tag}[@class='{class_str}']"
            else:
                conditions = " and ".join([f"contains(@class, '{c}')" for c in classes])
                return f"//{tag}[{conditions}]"
        elif len(matching) > 1:
            # Find index among siblings with same class
            for idx, el in enumerate(matching, 1):
                if el == element:
                    if len(classes) == 1:
                        return f"(//{tag}[@class='{class_str}'])[{idx}]"
                    else:
                        conditions = " and ".join([f"contains(@class, '{c}')" for c in classes])
                        return f"(//{tag}[{conditions}])[{idx}]"
    
    # Priority 3: Text content (for short, unique text)
    element_text = element.get_text(strip=True)
    if element_text and len(element_text) <= 60:
        # Escape quotes
        escaped_text = element_text.replace("'", "&apos;")
        # Check uniqueness
        matching = soup.find_all(tag, string=lambda t: t and element_text in t)
        if len(matching) <= 1:
            if len(element_text) <= 30:
                return f"//{tag}[normalize-space()='{escaped_text}']"
            else:
                return f"//{tag}[contains(normalize-space(), '{escaped_text[:40]}')]"
    
    # Priority 4: Position among all same tags
    all_same_tags = soup.find_all(tag)
    for idx, el in enumerate(all_same_tags, 1):
        if el == element:
            return f"(//{tag})[{idx}]"
    
    return f"//{tag}"


def generate_xpath(element_tag: str, element_id: str = None, element_class: str = None, 
                   element_text: str = None, element_index: int = None, use_text: bool = False) -> str:
    """
    Generate an XPath selector from element attributes
    Similar to Chrome DevTools Elements.DOMPath.xPath for consistency
    
    Args:
        element_tag: HTML tag name
        element_id: Element ID attribute
        element_class: Element class attribute
        element_text: Text content (only used if use_text=True)
        element_index: Position index among siblings
        use_text: Whether to include text in XPath (default False for reliability)
        
    Returns:
        XPath selector string that can be used in Chrome DevTools
    """
    # Sanitize inputs
    if element_tag:
        element_tag = element_tag.strip().lower()
    if element_id:
        element_id = element_id.strip()
    if element_class:
        element_class = element_class.strip()
        
    # Priority 1: ID (most specific and reliable)
    if element_id:
        # Escape single quotes in ID
        escaped_id = element_id.replace("'", "&apos;")
        return f"//*[@id='{escaped_id}']"
    
    # Priority 2: Class name (without text to avoid duplicates)
    elif element_class:
        # Handle multiple classes
        classes = element_class.split()
        if len(classes) == 1:
            # Single class - exact match
            escaped_class = element_class.replace("'", "&apos;")
            xpath = f"//{element_tag}[@class='{escaped_class}']"
        else:
            # Multiple classes - use contains for each
            class_conditions = " and ".join([f"contains(@class, '{cls.replace(chr(39), '&apos;')}')" for cls in classes])
            xpath = f"//{element_tag}[{class_conditions}]"
        
        # Add index if provided for more specificity
        if element_index is not None and element_index > 0:
            xpath = f"({xpath})[{element_index}]"
            
        return xpath
    
    # Priority 3: Position index (more reliable than text)
    elif element_index is not None and element_index > 0:
        return f"(//{element_tag})[{element_index}]"
    
    # Priority 4: Text content (only if explicitly requested and no other option)
    elif use_text and element_text:
        # Clean and escape text
        text_snippet = element_text[:50].replace("'", "&apos;").replace('"', "&quot;")
        
        # Special case for single character elements (like × for close buttons)
        if len(element_text) == 1:
            return f"//{element_tag}[text()='{text_snippet}']"
        elif len(element_text) <= 30:
            return f"//{element_tag}[normalize-space()='{text_snippet}']"
        else:
            return f"//{element_tag}[contains(normalize-space(), '{text_snippet}')]"
    
    # Last resort: Tag with first position
    else:
        # Return first occurrence to be more specific
        logger.warning(f"Generating positional XPath for {element_tag}")
        return f"(//{element_tag})[1]"


class HeadingAnalyzer:
    """Analyzes heading structure visually and semantically"""
    
    def __init__(self, client):
        """
        Initialize heading analyzer
        
        Args:
            client: Claude client instance
        """
        self.client = client
    
    async def analyze(self, screenshot: bytes, html: str) -> Dict[str, Any]:
        """
        Analyze headings for visual/semantic mismatches
        
        Args:
            screenshot: Page screenshot
            html: Page HTML
            
        Returns:
            Analysis results with specific issue codes
        """
        prompt = """Analyze heading structure in this web page screenshot and HTML.

Look for text that VISUALLY appears to be a heading (larger/bolder font, section title style) but is NOT using proper heading tags.

IMPORTANT: First check the HTML - if text is already inside <h1>, <h2>, <h3>, <h4>, <h5>, or <h6> tags, do NOT report it.

For each issue, find the element in HTML and extract its class and id attributes.

ISSUE CODES:

1. AI_ErrVisualHeadingNotMarked - Text looks like heading but uses <div>, <p>, <span>
   Required: visual_text (exact text), element_tag, element_class, element_id, suggested_level

2. AI_ErrHeadingLevelMismatch - Heading level wrong for visual prominence  
   Required: heading_text, element_tag, current_level, suggested_level, element_class, element_id

Return JSON:
{
    "issues": [
        {
            "err": "AI_ErrVisualHeadingNotMarked",
            "type": "err",
            "visual_text": "exact text",
            "element_tag": "div",
            "element_class": "class-from-html",
            "element_id": "id-or-null",
            "suggested_level": 2,
            "description": "Text 'Example' uses <div> instead of heading"
        }
    ],
    "summary": "Brief summary"
}

RULES:
- Do NOT report text already in h1-h6 tags
- Extract element_class and element_id from the HTML
- Report only clear issues where heading markup is missing"""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
            
            # Ensure we have the expected structure
            if 'issues' not in result:
                result['issues'] = []
            
            return result
            
        except Exception as e:
            logger.error(f"Heading analysis failed: {e}")
            return {
                'error': str(e),
                'issues': []
            }


class ReadingOrderAnalyzer:
    """Analyzes reading order consistency"""
    
    def __init__(self, client):
        self.client = client
    
    async def analyze(self, screenshot: bytes, html: str) -> Dict[str, Any]:
        """
        Check if visual reading order matches DOM order
        
        Args:
            screenshot: Page screenshot
            html: Page HTML
            
        Returns:
            Reading order analysis with specific issue codes
        """
        prompt = """Analyze the reading order of this web page.

Compare the VISUAL reading order (left-to-right, top-to-bottom) with the DOM order in HTML.

ISSUE CODES (use these exactly):
- AI_ErrReadingOrderMismatch: Content appears in different order visually vs DOM (screen readers read wrong order)
- AI_ErrVisualGroupingBroken: Related content appears grouped visually but is separated in DOM

Return ONLY valid JSON:
{
    "reading_order_matches": true/false,
    "issues": [
        {
            "err": "AI_ErrReadingOrderMismatch",
            "type": "err",
            "visual_first": "What appears first visually",
            "dom_first": "What comes first in DOM",
            "element_tag": "tag of misplaced element",
            "element_class": "class if present",
            "element_id": "id if present",
            "description": "Specific description of the mismatch"
        }
    ],
    "summary": "Brief summary"
}

IMPORTANT: Only report SIGNIFICANT mismatches that affect comprehension. Minor reordering within a section is usually fine."""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
            if 'issues' not in result:
                result['issues'] = []
            return result
        except Exception as e:
            logger.error(f"Reading order analysis failed: {e}")
            return {'error': str(e), 'issues': []}


class ModalAnalyzer:
    """Analyzes modal dialogs and overlays"""
    
    def __init__(self, client):
        self.client = client
    
    async def analyze(self, screenshot: bytes, html: str) -> Dict[str, Any]:
        """
        Detect and analyze modal dialogs
        
        Args:
            screenshot: Page screenshot
            html: Page HTML
            
        Returns:
            Modal analysis with specific issue codes
        """
        prompt = """Analyze any modal dialogs, popups, or overlays visible in this page.

ISSUE CODES (use these exactly):
- AI_ErrDialogMissingRole: Modal/dialog visible but lacks role="dialog" or role="alertdialog"
- AI_ErrDialogMissingLabel: Dialog has role but no aria-label or aria-labelledby
- AI_ErrDialogNoCloseButton: Modal has no visible close mechanism (button, X, etc.)
- AI_WarnDialogBackgroundNotInert: Content behind modal appears still interactive (not properly disabled)

Return ONLY valid JSON:
{
    "modals_found": true/false,
    "modals": [
        {
            "has_role": true/false,
            "has_label": true/false,
            "has_close": true/false,
            "element_tag": "div/dialog/etc",
            "element_class": "modal class",
            "element_id": "modal id"
        }
    ],
    "issues": [
        {
            "err": "AI_ErrDialogMissingRole",
            "type": "err",
            "element_tag": "div",
            "element_class": "modal-class",
            "element_id": "modal-id",
            "description": "Visible modal dialog lacks role='dialog'"
        }
    ]
}

IMPORTANT: Only analyze modals that are CURRENTLY VISIBLE in the screenshot."""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
            if 'issues' not in result:
                result['issues'] = []
            return result
        except Exception as e:
            logger.error(f"Modal analysis failed: {e}")
            return {'error': str(e), 'modals_found': False, 'issues': []}


class LanguageAnalyzer:
    """Analyzes language declarations and changes"""
    
    def __init__(self, client):
        self.client = client
    
    async def analyze(self, screenshot: bytes, html: str) -> Dict[str, Any]:
        """
        Detect language usage and proper markup
        
        Args:
            screenshot: Page screenshot  
            html: Page HTML
            
        Returns:
            Language analysis with specific issue codes
        """
        # First check HTML for lang attribute
        soup = BeautifulSoup(html, 'html.parser')
        html_tag = soup.find('html')
        html_lang = html_tag.get('lang') if html_tag else None
        
        prompt = f"""Analyze language usage in this web page screenshot and HTML.

The HTML tag has lang="{html_lang or 'not set'}".

Look for text in DIFFERENT languages than the page's primary language ({html_lang or 'unknown'}).
Use the HTML to find the EXACT text - do NOT guess or paraphrase text.

ISSUE CODES (use these exactly):
- AI_ErrPageLanguageMissing: No lang attribute on <html> element (only if html_lang is missing)
- AI_ErrPageLanguageWrong: Page lang attribute doesn't match visible content language
- AI_ErrForeignTextUnmarked: Foreign language text found without lang attribute (ERROR - screen readers will mispronounce)

For each foreign text found:
1. Extract the EXACT text from the HTML
2. Find the element's class or id attribute
3. If no class/id, find the nearest parent section/div with a class

Return ONLY valid JSON:
{{
    "detected_language": "en/fr/es/de/etc",
    "html_lang": "{html_lang or 'missing'}",
    "language_matches": true/false,
    "foreign_content": [
        {{
            "text_sample": "EXACT text from HTML",
            "detected_language": "language code",
            "has_lang_attr": true/false
        }}
    ],
    "issues": [
        {{
            "err": "AI_ErrForeignTextUnmarked",
            "type": "err",
            "text_sample": "EXACT foreign text from HTML",
            "detected_language": "de",
            "element_tag": "p/span/div/h2/section/a",
            "element_class": "class-from-element-or-parent",
            "element_id": "id-if-exists-or-null",
            "parent_class": "class-of-nearest-parent-with-class",
            "description": "German text found without lang='de' attribute"
        }}
    ]
}}

CRITICAL: 
- Use the EXACT text from the HTML. Do NOT paraphrase or translate the text.
- Always try to find a class or id attribute for element identification."""
        
        try:
            result = await self.client.analyze_with_image_and_html(screenshot, html, prompt)
            if 'issues' not in result:
                result['issues'] = []
            return result
        except Exception as e:
            logger.error(f"Language analysis failed: {e}")
            return {'error': str(e), 'issues': []}


class AnimationAnalyzer:
    """Analyzes animations and motion"""
    
    def __init__(self, client):
        self.client = client
    
    async def analyze(self, html: str) -> Dict[str, Any]:
        """
        Detect animations and motion in HTML/CSS
        
        Args:
            html: Page HTML including styles
            
        Returns:
            Animation analysis with specific issue codes
        """
        prompt = """Analyze this HTML for animations, transitions, and motion.

ISSUE CODES (use these exactly):
- AI_ErrInfiniteAnimationNoPause: Infinite CSS animation without pause control
- AI_ErrAutoPlayingMedia: Auto-playing video/audio without controls
- AI_WarnNoReducedMotion: Animations don't respect prefers-reduced-motion
- AI_WarnPotentialFlashing: Animation may cause flashing (seizure risk)

Return ONLY valid JSON:
{
    "has_animations": true/false,
    "respects_reduced_motion": true/false,
    "issues": [
        {
            "err": "AI_ErrInfiniteAnimationNoPause",
            "type": "err",
            "element_tag": "div",
            "element_class": "animated-element",
            "animation_name": "spin",
            "description": "Infinite animation 'spin' has no pause control"
        }
    ]
}

IMPORTANT: Only flag animations that are CLEARLY problematic. Brief hover transitions are fine."""
        
        try:
            result = await self.client.analyze_html(html, prompt)
            if 'issues' not in result:
                result['issues'] = []
            return result
        except Exception as e:
            logger.error(f"Animation analysis failed: {e}")
            return {'error': str(e), 'has_animations': False, 'issues': []}


class InteractiveAnalyzer:
    """Analyzes interactive elements for keyboard accessibility"""
    
    def __init__(self, client):
        self.client = client
    
    async def analyze(self, screenshot: bytes, html: str) -> Dict[str, Any]:
        """
        Analyze interactive elements
        
        Args:
            screenshot: Page screenshot
            html: Page HTML
            
        Returns:
            Interactive element analysis with specific issue codes
        """
        prompt = """Analyze interactive elements in this web page for keyboard accessibility.

Look for elements that APPEAR clickable/interactive but may not be properly accessible.

ISSUE CODES (use these exactly):
- AI_ErrNonSemanticButton: Element looks like a button but uses <div>/<span> with onclick instead of <button>
- AI_ErrNonSemanticLink: Element looks like a link but uses <div>/<span> instead of <a>
- AI_ErrCustomControlNoARIA: Custom widget (tabs, accordion, dropdown) lacks proper ARIA roles/states
- AI_ErrClickableNotFocusable: Element has click handler but no tabindex (not keyboard accessible)
- AI_WarnFocusIndicatorWeak: Focus indicator appears too subtle or missing

Return ONLY valid JSON:
{
    "interactive_elements_found": true/false,
    "issues": [
        {
            "err": "AI_ErrNonSemanticButton",
            "type": "err",
            "element_tag": "div",
            "element_class": "btn custom-button",
            "element_id": "submit-btn",
            "element_text": "Submit",
            "description": "Div styled as button with onclick - should use <button>"
        }
    ]
}

IMPORTANT: 
- Only report elements that are CLEARLY meant to be interactive
- Don't flag <div> with click if it also has proper role="button" and tabindex
- Focus on HIGH-CONFIDENCE issues only"""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
            if 'issues' not in result:
                result['issues'] = []
            return result
        except Exception as e:
            logger.error(f"Interactive analysis failed: {e}")
            return {'error': str(e), 'interactive_elements_found': False, 'issues': []}
