#!/usr/bin/env python3
"""
Fix format placeholder errors in .po file by examining the specific error lines.

Extracts the problematic lines from the compile error and adds no-python-format flags.
"""

import polib
import subprocess
from pathlib import Path


def get_error_lines():
    """Run pybabel compile and extract error line numbers"""
    result = subprocess.run(
        ['pybabel', 'compile', '-d', 'auto_a11y/web/translations'],
        capture_output=True,
        text=True
    )

    error_lines = []
    for line in result.stderr.split('\n'):
        if 'incompatible format' in line and '.po:' in line:
            # Extract line number from error like:
            # error: auto_a11y/web/translations/fr/LC_MESSAGES/messages.po:10469: incompatible format...
            parts = line.split(':')
            if len(parts) >= 3:
                try:
                    line_num = int(parts[2])
                    error_lines.append(line_num)
                except ValueError:
                    pass

    return sorted(set(error_lines))


def find_entry_by_line_number(po, target_line):
    """Find PO entry that contains the given line number"""
    # polib doesn't track exact line numbers, so we need to parse the file
    po_file_path = Path(__file__).parent.parent / 'auto_a11y' / 'web' / 'translations' / 'fr' / 'LC_MESSAGES' / 'messages.po'

    with open(po_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Get context around the error line
    if target_line < 1 or target_line > len(lines):
        return None

    # Search backwards for msgctxt or msgid
    msgctxt = None
    for i in range(target_line - 1, max(0, target_line - 50), -1):
        line = lines[i].strip()
        if line.startswith('msgctxt '):
            msgctxt_value = line.split('"')[1] if '"' in line else None
            if msgctxt_value:
                # Find entry with this msgctxt
                for entry in po:
                    if entry.msgctxt == msgctxt_value:
                        return entry
            break
        elif line.startswith('msgid ') and not line.startswith('msgid ""'):
            # Try to find by msgid
            msgid_value = line.split('"')[1] if '"' in line else None
            if msgid_value:
                # Find entry with this msgid prefix
                for entry in po:
                    if entry.msgid.startswith(msgid_value):
                        return entry
            break

    return None


def main():
    # Get error lines from compile output
    print("Running pybabel compile to identify problematic entries...")
    error_lines = get_error_lines()

    if not error_lines:
        print("No format errors found!")
        return 0

    print(f"Found {len(error_lines)} entries with format errors:")
    for line_num in error_lines:
        print(f"  Line {line_num}")

    # Load .po file
    po_file_path = Path(__file__).parent.parent / 'auto_a11y' / 'web' / 'translations' / 'fr' / 'LC_MESSAGES' / 'messages.po'

    print(f"\nLoading {po_file_path}")
    po = polib.pofile(str(po_file_path))

    # Find and fix entries
    fixed = 0

    for line_num in error_lines:
        entry = find_entry_by_line_number(po, line_num)
        if entry:
            if 'no-python-format' not in entry.flags:
                entry.flags.append('no-python-format')
                fixed += 1
                print(f"  Fixed: {entry.msgctxt or entry.msgid[:50]}...")
        else:
            print(f"  Warning: Could not find entry for line {line_num}")

    print(f"\nFixed {fixed} entries by adding 'no-python-format' flag")

    # Save .po file
    print(f"\nSaving {po_file_path}")
    po.save(str(po_file_path))
    print("✓ Saved successfully")

    print(f"\nRetrying compile...")
    result = subprocess.run(
        ['pybabel', 'compile', '-d', 'auto_a11y/web/translations'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ Compilation successful!")
    else:
        print("✗ Still have errors:")
        print(result.stderr)
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
