#!/usr/bin/env python3
"""
Apply what_generic fields to all catalog entries that need them.
Version 3: Line-by-line processing with state machine.
"""

import re
from what_generic_additions import WHAT_GENERIC_ADDITIONS

def apply_what_generic():
    """Apply what_generic fields to the catalog file"""

    catalog_file = 'auto_a11y/reporting/issue_descriptions_enhanced.py'

    # Read all lines
    with open(catalog_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    changes_made = 0
    skipped = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this line starts an entry we need to update
        entry_match = re.match(r"(\s*)'([A-Z][a-zA-Z0-9_]+)':\s*\{", line)
        if entry_match:
            indent = entry_match.group(1)
            code = entry_match.group(2)

            if code in WHAT_GENERIC_ADDITIONS:
                # Scan ahead to find 'what': line and check for existing 'what_generic'
                j = i + 1
                found_what = False
                found_what_generic = False
                what_line_idx = -1

                while j < len(lines) and not (lines[j].strip() in ['},', '}']):
                    if "'what_generic':" in lines[j]:
                        found_what_generic = True
                        break
                    if "'what':" in lines[j]:
                        found_what = True
                        what_line_idx = j
                    j += 1

                if found_what_generic:
                    skipped += 1
                    print(f"○ Skipped {code} (already has what_generic)")
                elif found_what and what_line_idx >= 0:
                    # Found the 'what' line, now find where it ends
                    k = what_line_idx
                    while k < len(lines):
                        new_lines.append(lines[k])

                        # Check if this line ends the 'what' value
                        # Ends with ", or ",\n or just " on some lines
                        if '",\n' in lines[k] or lines[k].strip().endswith('",'):
                            # Insert what_generic on the next line
                            generic_text = WHAT_GENERIC_ADDITIONS[code]
                            field_indent = indent + '            '  # Match dict field indentation
                            what_generic_line = f'{field_indent}\'what_generic\': "{generic_text}",\n'
                            new_lines.append(what_generic_line)
                            changes_made += 1
                            print(f"✓ Added what_generic to {code}")
                            i = k
                            break

                        k += 1
                else:
                    print(f"⚠ Warning: Could not find 'what' field for {code}")

        i += 1

    # Write back
    with open(catalog_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\n{'='*60}")
    print(f"✅ Applied {changes_made} what_generic fields")
    print(f"○  Skipped {skipped} (already had what_generic)")
    print(f"{'='*60}")

    return changes_made

if __name__ == '__main__':
    print("Applying what_generic fields to catalog...")
    print("="*60)

    changes = apply_what_generic()

    if changes > 0:
        print("\n✅ Success! All what_generic fields have been added.")
        print("Run 'git diff' to review changes.")
    else:
        print("\n⚠ No changes were made.")
