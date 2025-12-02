#!/usr/bin/env python3
"""
Add extracted issue description strings to French messages.po file.

This script:
1. Reads extracted strings from extract_issue_descriptions.py output
2. Adds them to the French .po file with empty msgstr (to be translated)
3. Preserves existing translations
4. Uses msgctxt for context-specific translations

Usage:
    python scripts/extract_issue_descriptions.py > extracted_strings.json
    python scripts/add_issue_translations_to_po.py extracted_strings.json
"""

import polib
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_issue_translations_to_po.py <extracted_strings.json>", file=sys.stderr)
        print("", file=sys.stderr)
        print("First run: python scripts/extract_issue_descriptions.py > extracted_strings.json", file=sys.stderr)
        return 1

    extracted_file = sys.argv[1]

    # Load extracted strings
    try:
        with open(extracted_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {extracted_file}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {extracted_file}: {e}", file=sys.stderr)
        return 1

    strings = data.get('strings', [])
    metadata = data.get('metadata', {})

    print(f"Loaded {len(strings)} strings from {extracted_file}")
    print(f"  Total issues: {metadata.get('total_issues')}")
    print(f"  Total strings: {metadata.get('total_strings')}")

    # Path to .po file
    po_file_path = Path(__file__).parent.parent / 'auto_a11y' / 'web' / 'translations' / 'fr' / 'LC_MESSAGES' / 'messages.po'

    if not po_file_path.exists():
        print(f"Error: .po file not found: {po_file_path}", file=sys.stderr)
        return 1

    # Load .po file
    print(f"\nLoading {po_file_path}")
    try:
        po = polib.pofile(str(po_file_path))
    except Exception as e:
        print(f"Error loading .po file: {e}", file=sys.stderr)
        return 1

    print(f"Current .po file has {len(po)} entries")

    # Add strings to .po file
    added = 0
    skipped = 0
    updated = 0

    for string_data in strings:
        msgctxt = string_data['msgctxt']
        msgid = string_data['msgid']
        issue_code = string_data['issue_code']
        field = string_data['field']

        # Check if entry already exists (with msgctxt)
        entry = po.find(msgid, msgctxt=msgctxt)

        if entry:
            # Entry exists
            if entry.msgstr and entry.msgstr != msgid:
                # Already has a translation, skip
                skipped += 1
            else:
                # Has entry but no translation, update metadata
                if not entry.comment:
                    entry.comment = f'Issue: {issue_code}, Field: {field}'
                updated += 1
        else:
            # Create new entry
            entry = polib.POEntry(
                msgctxt=msgctxt,
                msgid=msgid,
                msgstr='',  # Empty, to be translated
                comment=f'Issue: {issue_code}, Field: {field}'
            )
            po.append(entry)
            added += 1

    print(f"\nResults:")
    print(f"  Added: {added} new entries")
    print(f"  Updated: {updated} existing entries")
    print(f"  Skipped: {skipped} already translated")
    print(f"  Total .po entries: {len(po)}")

    # Save .po file
    print(f"\nSaving {po_file_path}")
    try:
        po.save(str(po_file_path))
        print("✓ Saved successfully")
    except Exception as e:
        print(f"Error saving .po file: {e}", file=sys.stderr)
        return 1

    print(f"\nNext steps:")
    print(f"1. Translate the {added} new entries in {po_file_path}")
    print(f"2. Run: pybabel compile -d auto_a11y/web/translations")
    print(f"3. Test the translations in the application")

    return 0


if __name__ == '__main__':
    sys.exit(main())
