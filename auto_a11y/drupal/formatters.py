"""
HTML formatters for Drupal export.

This module provides functions to format Auto A11y content as HTML
for inclusion in Drupal body fields.
"""

from typing import List, Dict, Any, Optional
import html


def format_recording_body(
    key_takeaways: List[Dict[str, Any]],
    user_painpoints: List[Dict[str, Any]],
    user_assertions: List[Dict[str, Any]],
    description: Optional[str] = None,
    auditor_info: Optional[str] = None
) -> str:
    """
    Format recording content as HTML for Drupal audit_video body field.

    Args:
        key_takeaways: List of key takeaway dicts with 'number', 'topic', 'description'
        user_painpoints: List of painpoint dicts with 'title', 'user_quote', 'impact', 'timecodes'
        user_assertions: List of assertion dicts with 'number', 'assertion', 'user_quote', 'timecodes'
        description: Optional recording description
        auditor_info: Optional auditor information (name, role, etc.)

    Returns:
        HTML string formatted for Drupal body field
    """
    parts = []

    # Add description if provided
    if description:
        parts.append(f"<p>{html.escape(description)}</p>\n")

    # Add auditor info if provided
    if auditor_info:
        parts.append(f"<p><em>{html.escape(auditor_info)}</em></p>\n")

    # Add Key Takeaways section
    if key_takeaways:
        parts.append("<h3>Key Takeaways</h3>\n")
        parts.append("<ol>\n")
        for takeaway in key_takeaways:
            topic = html.escape(takeaway.get('topic', ''))
            description = html.escape(takeaway.get('description', ''))
            parts.append(f"  <li><strong>{topic}</strong>")
            if description:
                parts.append(f" &ndash; {description}")
            parts.append("</li>\n")
        parts.append("</ol>\n")

    # Add User Painpoints section
    if user_painpoints:
        parts.append("<h3>User Painpoints</h3>\n")
        for painpoint in user_painpoints:
            title = html.escape(painpoint.get('title', ''))
            user_quote = painpoint.get('user_quote', '')
            impact = painpoint.get('impact', '')
            timecodes = painpoint.get('timecodes', [])

            # Painpoint title with impact badge
            if impact:
                impact_upper = html.escape(impact.upper())
                parts.append(f"<h4><span class=\"badge badge-{impact.lower()}\">{impact_upper}</span> {title}</h4>\n")
            else:
                parts.append(f"<h4>{title}</h4>\n")

            # User quote
            if user_quote:
                parts.append(f"<blockquote>\n")
                parts.append(f"  <p><em>\"{html.escape(user_quote)}\"</em></p>\n")
                parts.append(f"</blockquote>\n")

            # Timecodes
            if timecodes:
                parts.append("<p><strong>Timecodes:</strong> ")
                timecode_strs = []
                for tc in timecodes:
                    start = html.escape(tc.get('start', ''))
                    end = html.escape(tc.get('end', ''))
                    if start and end:
                        timecode_strs.append(f"{start} &ndash; {end}")
                    elif start:
                        timecode_strs.append(start)
                parts.append(", ".join(timecode_strs))
                parts.append("</p>\n")

    # Add User Assertions section
    if user_assertions:
        parts.append("<h3>User Assertions</h3>\n")
        parts.append("<ol>\n")
        for assertion in user_assertions:
            assertion_text = html.escape(assertion.get('assertion', ''))
            user_quote = assertion.get('user_quote', '')
            context = assertion.get('context', '')
            timecodes = assertion.get('timecodes', [])

            parts.append(f"  <li>\n")
            parts.append(f"    <p><strong>{assertion_text}</strong></p>\n")

            # User quote
            if user_quote:
                parts.append(f"    <blockquote>\n")
                parts.append(f"      <p><em>\"{html.escape(user_quote)}\"</em></p>\n")
                parts.append(f"    </blockquote>\n")

            # Context
            if context:
                parts.append(f"    <p><em>Context:</em> {html.escape(context)}</p>\n")

            # Timecodes
            if timecodes:
                parts.append("    <p><strong>Timecodes:</strong> ")
                timecode_strs = []
                for tc in timecodes:
                    start = html.escape(tc.get('start', ''))
                    end = html.escape(tc.get('end', ''))
                    if start and end:
                        timecode_strs.append(f"{start} &ndash; {end}")
                    elif start:
                        timecode_strs.append(start)
                parts.append(", ".join(timecode_strs))
                parts.append("</p>\n")

            parts.append("  </li>\n")
        parts.append("</ol>\n")

    return "".join(parts)


def format_issue_body(
    what: str,
    why: str,
    who: str,
    how: str,
    additional_context: Optional[str] = None
) -> str:
    """
    Format issue content as HTML for Drupal issue body field.

    Follows the What/Why/Who/How structure expected by Drupal.

    Args:
        what: What is the issue?
        why: Why is it a problem?
        who: Who is affected?
        how: How to fix it?
        additional_context: Optional additional context

    Returns:
        HTML string formatted for Drupal body field
    """
    parts = []

    if what:
        parts.append("<h4>What</h4>\n")
        parts.append(f"<p>{html.escape(what)}</p>\n")

    if why:
        parts.append("<h4>Why</h4>\n")
        parts.append(f"<p>{html.escape(why)}</p>\n")

    if who:
        parts.append("<h4>Who</h4>\n")
        parts.append(f"<p>{html.escape(who)}</p>\n")

    if how:
        parts.append("<h4>How to Remediate</h4>\n")
        parts.append(f"<p>{html.escape(how)}</p>\n")

    if additional_context:
        parts.append("<h4>Additional Context</h4>\n")
        parts.append(f"<p>{html.escape(additional_context)}</p>\n")

    return "".join(parts)


def format_timecode(timecode: Dict[str, str]) -> str:
    """
    Format a timecode dict as a readable string.

    Args:
        timecode: Dict with 'start' and optionally 'end' keys

    Returns:
        Formatted timecode string (e.g., "01:23:45" or "01:23:45 - 01:24:30")
    """
    start = timecode.get('start', '')
    end = timecode.get('end', '')

    if start and end:
        return f"{start} - {end}"
    elif start:
        return start
    else:
        return ""


def escape_for_drupal(text: str) -> str:
    """
    Escape text for safe inclusion in Drupal HTML.

    This is a wrapper around html.escape for consistency.

    Args:
        text: Text to escape

    Returns:
        HTML-escaped text
    """
    return html.escape(text) if text else ""
