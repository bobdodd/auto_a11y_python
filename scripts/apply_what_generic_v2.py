#!/usr/bin/env python3
"""
Apply what_generic fields to all catalog entries that need them.
This script updates issue_descriptions_enhanced.py in place.
Version 2: Properly inserts what_generic after what field.
"""

import re
import sys
from what_generic_additions import WHAT_GENERIC_ADDITIONS

def apply_what_generic():
    """Apply what_generic fields to the catalog file"""

    catalog_file = 'auto_a11y/reporting/issue_descriptions_enhanced.py'

    # Read the file
    with open(catalog_file, 'r', encoding='utf-8') as f:
        content = f.read()

    changes_made = 0
    modified_content = content

    # For each code that needs what_generic
    for code, generic_text in sorted(WHAT_GENERIC_ADDITIONS.items()):
        # Pattern to find the entry and its 'what' field
        # We need to find: 'CODE': { ... 'what': "...", ... }

        # First, check if it already has what_generic
        entry_pattern = rf"'{code}':\s*\{{[^}}]*'what_generic':[^}}]*\}},"
        if re.search(entry_pattern, modified_content, re.DOTALL):
            print(f"○ Skipped {code} (already has what_generic)")
            continue

        # Find the entry and its 'what' field
        # Pattern: 'CODE': { ... 'what': "..." or 'what': "...  (multi-line handling)
        entry_start_pattern = rf"('{code}':\s*\{{[^}}]*'what':\s*\")"

        match = re.search(entry_start_pattern, modified_content, re.DOTALL)
        if not match:
            print(f"⚠ Warning: Could not find entry for {code}")
            continue

        # Find the end of the 'what' field (ends with ",)
        # Start searching from the match position
        start_pos = match.end()

        # Find the closing quote and comma for the 'what' field
        # Look for: ", or ",\n
        what_end_pattern = r'",\s*\n'
        what_end_match = re.search(what_end_pattern, modified_content[start_pos:])

        if not what_end_match:
            print(f"⚠ Warning: Could not find end of 'what' field for {code}")
            continue

        # Calculate the insertion point (after the 'what' field)
        insert_pos = start_pos + what_end_match.end()

        # Determine indentation (match the line above)
        lines_before = modified_content[:insert_pos].split('\n')
        last_line = lines_before[-1] if lines_before else ''
        # Get the whitespace at start of line
        indent_match = re.match(r'^(\s*)', last_line)
        indent = indent_match.group(1) if indent_match else '            '

        # Create the what_generic line
        what_generic_line = f'{indent}\'what_generic\': "{generic_text}",\n'

        # Insert it
        modified_content = modified_content[:insert_pos] + what_generic_line + modified_content[insert_pos:]
        changes_made += 1
        print(f"✓ Added what_generic to {code}")

    # Write back to file
    with open(catalog_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print(f"\n{'='*60}")
    print(f"✅ Applied {changes_made} what_generic fields")
    print(f"{'='*60}")

    return changes_made

if __name__ == '__main__':
    if '--dry-run' in sys.argv:
        print("DRY RUN mode - no changes will be made")
        print("Remove --dry-run to apply changes")
        sys.exit(0)

    print("Applying what_generic fields to catalog...")
    print("="*60)

    changes = apply_what_generic()

    if changes > 0:
        print("\n✅ Success! All what_generic fields have been added.")
        print("Run 'git diff' to review changes.")
    else:
        print("\n⚠ No changes were made. All entries may already have what_generic.")
