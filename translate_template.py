#!/usr/bin/env python3
"""
Helper script to automatically add translation markers to HTML templates.
This handles common patterns but may require manual review.
"""
import re
import sys
from pathlib import Path

def add_translation_markers(content):
    """Add _() markers to translatable strings in HTML templates."""

    # Patterns to translate (order matters!)
    patterns = [
        # Button text content (not already translated)
        (r'(<button[^>]*>)([^{<]+)(</button>)', r'\1{{ _(\'\2\') }}\3'),

        # Labels (not already translated)
        (r'(<label[^>]*>)([^{<]+)(</label>)', r'\1{{ _(\'\2\') }}\3'),

        # Headings h1-h6 (not already translated)
        (r'(<h[1-6][^>]*>)([^{<]+)(</h[1-6]>)', r'\1{{ _(\'\2\') }}\3'),

        # Option tags (not already translated)
        (r'(<option[^>]*>)([^{<]+)(</option>)', r'\1{{ _(\'\2\') }}\3'),

        # Paragraph text (not already translated, be careful with this)
        # (r'(<p[^>]*>)([^{<]+)(</p>)', r'\1{{ _(\'\2\') }}\3'),

        # Div with class="form-text" (help text)
        (r'(<div class="form-text"[^>]*>)([^{<]+)(</div>)', r'\1{{ _(\'\2\') }}\3'),

        # Strong tags
        (r'(<strong>)([^{<]+)(</strong>)', r'\1{{ _(\'\2\') }}\3'),

        # Span text (be selective)
        # (r'(<span[^>]*>)([^{<]+)(</span>)', r'\1{{ _(\'\2\') }}\3'),

        # Placeholder attributes (not already translated)
        (r'placeholder="([^"]+)"', r'placeholder="{{ _(\'\\1\') }}"'),

        # Title attributes (not already translated)
        (r'title="([^"]+)"', r'title="{{ _(\'\\1\') }}"'),

        # Alert messages
        (r'(<div class="alert[^"]*"[^>]*>)([^{<]+)', r'\1{{ _(\'\2\') }}'),
    ]

    result = content
    for pattern, replacement in patterns:
        # Only replace if not already using _()
        # This is a simple check - may need refinement
        result = re.sub(pattern, replacement, result)

    # Clean up extra whitespace in translations
    result = re.sub(r"{{ _\('\\s+", r"{{ _('", result)
    result = re.sub(r"\\s+'\) }}", r"') }}", result)

    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_template.py <template_file>")
        sys.exit(1)

    template_path = Path(sys.argv[1])
    if not template_path.exists():
        print(f"Error: File not found: {template_path}")
        sys.exit(1)

    # Read the file
    content = template_path.read_text(encoding='utf-8')

    # Add translation markers
    translated = add_translation_markers(content)

    # Write back
    template_path.write_text(translated, encoding='utf-8')
    print(f"✓ Translated: {template_path}")

if __name__ == '__main__':
    main()
