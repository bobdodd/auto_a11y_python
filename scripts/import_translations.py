#!/usr/bin/env python3
"""
Import translated strings from JSON to French messages.po file.

This script:
1. Reads translated strings from AI translation output
2. Updates the French .po file with the translations
3. Validates placeholder preservation
4. Reports statistics on imported translations

Usage:
    python scripts/import_translations.py phase1_translated_schema.json
"""

import polib
import json
import sys
import re
from pathlib import Path


def validate_placeholders(original: str, translated: str) -> tuple[bool, str]:
    """Validate that all placeholders are preserved in translation"""
    # Extract placeholders from original
    orig_placeholders = set(re.findall(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)s', original))

    # Extract placeholders from translation
    trans_placeholders = set(re.findall(r'%\([a-zA-Z_][a-zA-Z0-9_]*\)s', translated))

    # Check if all placeholders are preserved
    if orig_placeholders != trans_placeholders:
        return False, f"Placeholder mismatch: {orig_placeholders} != {trans_placeholders}"

    return True, "OK"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_translations.py <translated.json>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Example: python scripts/import_translations.py phase1_translated_schema.json", file=sys.stderr)
        return 1

    translated_file = sys.argv[1]

    # Load translated strings
    try:
        with open(translated_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {translated_file}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {translated_file}: {e}", file=sys.stderr)
        return 1

    entries = data.get('entries', [])
    metadata = data.get('metadata', {})

    print(f"Loaded {len(entries)} translations from {translated_file}")
    print(f"  Total entries: {metadata.get('total_entries')}")
    print(f"  Translated: {metadata.get('translated')}")
    print(f"  Failed: {metadata.get('failed')}")
    print(f"  Warnings: {metadata.get('validation_warnings')}")

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

    # Import translations
    imported = 0
    skipped = 0
    not_found = 0
    validation_errors = 0

    print(f"\nImporting translations...")
    print("=" * 60)

    for entry_data in entries:
        msgctxt = entry_data['msgctxt']
        msgid = entry_data['msgid']
        msgstr = entry_data.get('msgstr', '')
        issue_code = entry_data['issue_code']
        field = entry_data['field']

        # Skip entries that were not translated
        if not msgstr or msgstr == msgid:
            skipped += 1
            continue

        # Validate placeholders
        is_valid, msg = validate_placeholders(msgid, msgstr)
        if not is_valid:
            print(f"  ⚠ Warning: {issue_code}.{field}: {msg}", file=sys.stderr)
            validation_errors += 1
            continue

        # Find entry in .po file (with msgctxt)
        po_entry = po.find(msgid, msgctxt=msgctxt)

        if po_entry:
            # Update translation
            po_entry.msgstr = msgstr
            imported += 1
        else:
            print(f"  ⚠ Warning: Entry not found in .po file: {issue_code}.{field}", file=sys.stderr)
            not_found += 1

    print(f"\n{'=' * 60}")
    print(f"Import Complete!")
    print(f"{'=' * 60}")
    print(f"Results:")
    print(f"  Imported: {imported} translations")
    print(f"  Skipped: {skipped} (not translated)")
    print(f"  Not found: {not_found} (missing from .po)")
    print(f"  Validation errors: {validation_errors}")
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
    print(f"1. Run: pybabel compile -d auto_a11y/web/translations")
    print(f"2. Test the translations in the application")
    print(f"3. Verify translations display correctly in French")

    return 0


if __name__ == '__main__':
    sys.exit(main())
