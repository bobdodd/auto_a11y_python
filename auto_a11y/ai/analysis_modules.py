"""
Specific AI analysis modules for different accessibility aspects
"""

import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


def generate_xpath(element_tag: str, element_id: str = None, element_class: str = None, 
                   element_text: str = None, element_index: int = None) -> str:
    """
    Generate an XPath selector from element attributes
    Similar to Chrome DevTools Elements.DOMPath.xPath for consistency
    
    Args:
        element_tag: HTML tag name
        element_id: Element ID attribute
        element_class: Element class attribute
        element_text: Text content for more specific matching
        element_index: Position index among siblings
        
    Returns:
        XPath selector string that can be used in Chrome DevTools
    """
    # Priority 1: ID (most specific and reliable)
    if element_id:
        return f"//*[@id='{element_id}']"
    
    # Priority 2: Class name
    elif element_class:
        # Handle multiple classes
        classes = element_class.strip().split()
        if len(classes) == 1:
            xpath = f"//{element_tag}[@class='{element_class}']"
        else:
            # Use contains for multiple classes
            class_conditions = " and ".join([f"contains(@class, '{cls}')" for cls in classes])
            xpath = f"//{element_tag}[{class_conditions}]"
        
        # Add text constraint if available for specificity
        if element_text:
            text_snippet = element_text[:30].replace("'", "&apos;").replace('"', "&quot;")
            xpath = f"{xpath}[contains(text(), '{text_snippet}')]"
        return xpath
    
    # Priority 3: Text content (when no ID or class)
    elif element_text:
        # Escape quotes and truncate for matching
        text_snippet = element_text[:50].replace("'", "&apos;").replace('"', "&quot;")
        if len(element_text) <= 50:
            # Exact match for short text
            return f"//{element_tag}[normalize-space()='{text_snippet}']"
        else:
            # Contains for longer text
            return f"//{element_tag}[contains(normalize-space(), '{text_snippet}')]"
    
    # Priority 4: Position index
    elif element_index is not None:
        return f"(//{element_tag})[{element_index}]"
    
    # Last resort: Just tag name (not ideal, too generic)
    else:
        logger.warning(f"Generating generic XPath for {element_tag} - consider adding more specific attributes")
        return f"//{element_tag}"


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
            Analysis results
        """
        prompt = """Analyze the heading structure in this web page screenshot and HTML.

        STEP 1 - Visual Analysis (Image Only):
        Look at the screenshot and identify text that appears to be headings based on:
        - Larger font size compared to body text
        - Bold or prominent styling
        - Positioned as section titles
        - Clear visual hierarchy
        
        STEP 2 - HTML Analysis:
        Review the HTML and identify all:
        - <h1> through <h6> tags
        - Elements with role="heading" and aria-level
        - For each element found, note its tag name, class, id, and surrounding HTML
        
        STEP 3 - Compare and Report Issues:
        For visual headings not properly marked up, find the HTML element containing that text.
        
        Return ONLY valid JSON in this format:
        {
            "visual_headings": [
                {
                    "text": "heading text",
                    "approximate_location": "top/middle/bottom and left/center/right",
                    "appears_to_be_level": 1-6,
                    "likely_element": "tag name of element containing this text if found",
                    "element_class": "class attribute if found",
                    "element_id": "id attribute if found"
                }
            ],
            "html_headings": [
                {
                    "text": "heading text",
                    "tag": "h1/h2/etc",
                    "level": 1-6,
                    "element_html": "the actual HTML of the heading element",
                    "element_class": "class attribute",
                    "element_id": "id attribute"
                }
            ],
            "issues": [
                {
                    "type": "visual_not_marked",
                    "description": "Text appears to be a heading but not marked up",
                    "visual_text": "the text",
                    "suggested_fix": "Use <h2> tag",
                    "element_tag": "actual tag like div, span, p",
                    "element_html": "the HTML of the element containing the visual heading",
                    "element_class": "class attribute if present",
                    "element_id": "id attribute if present"
                },
                {
                    "type": "wrong_level",
                    "description": "Heading level doesn't match visual hierarchy",
                    "heading_text": "the text",
                    "current_level": 3,
                    "suggested_level": 2,
                    "element_html": "the HTML of the heading element",
                    "element_class": "class attribute if present",
                    "element_id": "id attribute if present"
                }
            ],
            "hierarchy_valid": true/false,
            "summary": "Brief summary of heading structure"
        }"""
        
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
            Reading order analysis
        """
        prompt = """Analyze the reading order of this web page.

        Compare the natural visual reading order (left-to-right, top-to-bottom in English)
        with the DOM order in the HTML.
        
        Look for:
        1. Content that appears visually before other content but comes after in DOM
        2. Multi-column layouts where DOM order doesn't match visual flow
        3. Floating or absolutely positioned elements that disrupt reading order
        4. Content that visually appears related but is separated in DOM
        
        Return ONLY valid JSON:
        {
            "reading_order_matches": true/false,
            "issues": [
                {
                    "description": "Description of mismatch",
                    "visual_order": "What users see first",
                    "dom_order": "What screen readers read first",
                    "impact": "How this affects users"
                }
            ],
            "uses_layout_table": true/false,
            "has_multi_column": true/false,
            "recommendation": "How to fix reading order"
        }"""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
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
            Modal analysis results
        """
        prompt = """Analyze any modal dialogs, popups, or overlays in this page.

        Check for:
        1. Visible modal/dialog/popup overlays in the screenshot
        2. Proper ARIA roles (role="dialog" or role="alertdialog")
        3. Accessible names (aria-label or aria-labelledby)
        4. Focus management indicators
        5. Close buttons or escape mechanisms
        6. Background content handling (should be inert/aria-hidden)
        
        Return ONLY valid JSON:
        {
            "modals_found": true/false,
            "modals": [
                {
                    "type": "dialog/alert/popup",
                    "has_proper_role": true/false,
                    "has_accessible_name": true/false,
                    "has_close_button": true/false,
                    "appears_to_trap_focus": true/false,
                    "background_appears_disabled": true/false
                }
            ],
            "issues": [
                {
                    "type": "missing_role/missing_label/no_close/etc",
                    "description": "Issue description",
                    "wcag_criterion": "2.1.2/4.1.2/etc",
                    "fix": "How to fix"
                }
            ]
        }"""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
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
            Language analysis
        """
        # First check HTML for lang attribute
        soup = BeautifulSoup(html, 'html.parser')
        html_tag = soup.find('html')
        html_lang = html_tag.get('lang') if html_tag else None
        
        prompt = f"""Analyze language usage in this web page.

        The HTML tag has lang="{html_lang or 'not set'}".
        
        Tasks:
        1. Identify the primary language of the visible content
        2. Look for any content in different languages
        3. Check if language changes are properly marked
        
        Return ONLY valid JSON:
        {{
            "primary_language": "en/es/fr/etc or unknown",
            "html_lang_attribute": "{html_lang or 'missing'}",
            "lang_attribute_correct": true/false,
            "foreign_language_content": [
                {{
                    "text_sample": "foreign text",
                    "detected_language": "es/fr/etc",
                    "has_lang_attribute": true/false,
                    "location": "description of where on page"
                }}
            ],
            "issues": [
                {{
                    "type": "missing_lang/wrong_lang/unmarked_foreign",
                    "description": "Issue description",
                    "fix": "Add lang attribute"
                }}
            ]
        }}"""
        
        try:
            result = await self.client.analyze_with_image(screenshot, prompt)
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
            Animation analysis
        """
        prompt = """Analyze this HTML for animations, transitions, and motion.

        Look for:
        1. CSS animations (@keyframes, animation property)
        2. CSS transitions
        3. Auto-playing videos (video autoplay)
        4. Animated GIFs or images
        5. Parallax effects
        6. Infinite animations
        7. Respect for prefers-reduced-motion
        
        Check if:
        - Animations can be paused/stopped
        - prefers-reduced-motion media query is used
        - Animations last longer than 5 seconds
        - Any flashing or strobing effects
        
        Return ONLY valid JSON:
        {
            "has_animations": true/false,
            "animation_types": ["css_animation", "transition", "video", etc],
            "respects_reduced_motion": true/false,
            "has_infinite_animations": true/false,
            "has_auto_playing_media": true/false,
            "potential_seizure_risk": true/false,
            "issues": [
                {
                    "type": "infinite_animation/no_pause_control/no_reduced_motion",
                    "description": "Issue description",
                    "element": "Element or selector",
                    "wcag_criterion": "2.2.2/2.3.1",
                    "fix": "How to fix"
                }
            ]
        }"""
        
        try:
            result = await self.client.analyze_html(html, prompt)
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
            Interactive element analysis
        """
        prompt = """Analyze interactive elements in this web page for keyboard accessibility.

        Identify:
        1. Buttons, links, form inputs (should be keyboard accessible)
        2. Custom interactive elements (divs/spans with click handlers)
        3. Dropdown menus, tabs, accordions
        4. Focus indicators visibility
        
        Check for:
        - Elements that look clickable but aren't semantic buttons/links
        - Custom controls without proper ARIA
        - Missing focus indicators
        - Keyboard traps
        
        For each issue, try to identify the specific HTML element causing the problem.
        
        Return ONLY valid JSON:
        {
            "interactive_elements_found": true/false,
            "custom_controls": [
                {
                    "description": "What it appears to be",
                    "uses_semantic_html": true/false,
                    "has_proper_aria": true/false,
                    "appears_keyboard_accessible": true/false,
                    "element_tag": "div/span/etc if found",
                    "element_class": "class attribute if found",
                    "element_id": "id attribute if found"
                }
            ],
            "focus_indicators_visible": true/false,
            "issues": [
                {
                    "type": "non_semantic_button/missing_aria/no_focus_indicator",
                    "description": "Issue description",
                    "element_description": "What element",
                    "element_tag": "actual tag like div, span",
                    "element_html": "the HTML snippet if found",
                    "element_class": "class attribute if present",
                    "element_id": "id attribute if present",
                    "element_text": "visible text if any",
                    "wcag_criterion": "2.1.1/4.1.2",
                    "fix": "Use <button> or add role='button' and tabindex='0'"
                }
            ]
        }"""
        
        try:
            result = await self.client.analyze_with_image_and_html(
                screenshot, html, prompt
            )
            return result
        except Exception as e:
            logger.error(f"Interactive element analysis failed: {e}")
            return {'error': str(e), 'issues': []}