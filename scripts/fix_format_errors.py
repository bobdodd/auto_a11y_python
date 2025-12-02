#!/usr/bin/env python3
"""
Fix format placeholder errors in .po file.

The issue is that strings containing percentages like "8%" are being
interpreted as format strings by gettext, causing false positives.

This script adds the #, no-python-format flag to entries that contain
percentages but aren't actually Python format strings.
"""

import polib
import re
from pathlib import Path


def has_python_format(text):
    """Check if text contains actual Python format placeholders"""
    if not text:
        return False
    # Match %(name)s, %(name)d, etc.
    return bool(re.search(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)[sd]', text))


def has_percentage(text):
    """Check if text contains percentage numbers like 8%"""
    if not text:
        return False
    # Match patterns like "8%", "100%", etc.
    return bool(re.search(r'\d+%', text))


def main():
    # Path to .po file
    po_file_path = Path(__file__).parent.parent / 'auto_a11y' / 'web' / 'translations' / 'fr' / 'LC_MESSAGES' / 'messages.po'

    if not po_file_path.exists():
        print(f"Error: .po file not found: {po_file_path}")
        return 1

    print(f"Loading {po_file_path}")
    po = polib.pofile(str(po_file_path))

    print(f"Loaded {len(po)} entries")

    # Fix entries with percentages but no Python format strings
    fixed = 0

    for entry in po:
        msgid_text = entry.msgid
        msgstr_text = entry.msgstr

        # Check if this entry has percentages but no Python format strings
        has_percent = has_percentage(msgid_text) or has_percentage(msgstr_text)
        has_format = has_python_format(msgid_text) or has_python_format(msgstr_text)

        if has_percent and not has_format:
            # This entry has percentages but isn't a format string
            # Add no-python-format flag if not already present
            if 'no-python-format' not in entry.flags:
                entry.flags.append('no-python-format')
                fixed += 1

    print(f"\nFixed {fixed} entries by adding 'no-python-format' flag")

    # Save .po file
    print(f"\nSaving {po_file_path}")
    po.save(str(po_file_path))
    print("✓ Saved successfully")

    print(f"\nNext: pybabel compile -d auto_a11y/web/translations")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
