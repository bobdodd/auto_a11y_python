#!/usr/bin/env python3
"""
Apply what_generic fields to all catalog entries that need them.
This script updates issue_descriptions_enhanced.py in place.
"""

import re
import sys
from what_generic_additions import WHAT_GENERIC_ADDITIONS

def apply_what_generic():
    """Apply what_generic fields to the catalog file"""

    catalog_file = 'auto_a11y/reporting/issue_descriptions_enhanced.py'

    # Read the file
    with open(catalog_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified_lines = []
    changes_made = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        modified_lines.append(line)

        # Check if this is an entry that needs what_generic
        entry_match = re.match(r"(\s*)'([A-Z][a-zA-Z0-9_]+)':\s*\{", line)
        if entry_match:
            indent = entry_match.group(1)
            code = entry_match.group(2)

            if code in WHAT_GENERIC_ADDITIONS:
                # Find the 'what': line
                j = i + 1
                found_what = False
                already_has_generic = False
                what_line_index = -1

                while j < len(lines):
                    # Check for entry end
                    if lines[j].strip() in ['},', '}']:
                        break

                    # Check if already has what_generic
                    if "'what_generic':" in lines[j]:
                        already_has_generic = True
                        break

                    # Find the 'what': line
                    if "'what':" in lines[j]:
                        found_what = True
                        what_line_index = j

                        # Find the end of the 'what' field (could be multi-line)
                        k = j
                        while k < len(lines):
                            # Already added this line
                            if k > j:
                                modified_lines.append(lines[k])

                            # Check if this line ends the 'what' field
                            if lines[k].strip().endswith('",') or lines[k].strip().endswith('",}'):
                                # Insert what_generic after this line
                                generic_text = WHAT_GENERIC_ADDITIONS[code]
                                what_generic_line = f'{indent}    \'what_generic\': "{generic_text}",\n'
                                modified_lines.append(what_generic_line)
                                changes_made += 1
                                print(f"✓ Added what_generic to {code}")

                                # Skip to after the what field
                                i = k
                                break

                            k += 1

                        if k >= len(lines):
                            print(f"⚠ Warning: Could not find end of 'what' field for {code}")

                        break

                    # Add non-what lines
                    if not found_what:
                        modified_lines.append(lines[j])

                    j += 1

                if already_has_generic:
                    print(f"○ Skipped {code} (already has what_generic)")
                elif not found_what:
                    print(f"⚠ Warning: Could not find 'what' field for {code}")

        i += 1

    # Write back to file
    with open(catalog_file, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)

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
