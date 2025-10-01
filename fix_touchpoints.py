#!/usr/bin/env python3
"""
Fix missing touchpoints in ISSUE_CATALOG.md using TOUCHPOINT_TEST_MAPPING
"""

import re
from pathlib import Path
import sys

# Import the mapping
sys.path.insert(0, str(Path(__file__).parent))
from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING


def create_reverse_mapping():
    """Create ID -> touchpoint mapping from TOUCHPOINT_TEST_MAPPING"""
    reverse = {}
    for touchpoint, test_ids in TOUCHPOINT_TEST_MAPPING.items():
        for test_id in test_ids:
            reverse[test_id] = touchpoint
    return reverse


def fix_catalog(catalog_path: Path):
    """Fix touchpoints in the catalog file"""
    print(f"Reading {catalog_path}...")

    content = catalog_path.read_text(encoding='utf-8')
    reverse_mapping = create_reverse_mapping()

    fixed_count = 0
    still_missing = []

    # Find all issue blocks
    issue_blocks = re.split(r'(\n---\n)', content)

    new_blocks = []
    for block in issue_blocks:
        if '---' in block:
            new_blocks.append(block)
            continue

        # Check if this block has an ID
        id_match = re.search(r'^ID:\s*(\S+)', block, re.MULTILINE)
        if not id_match:
            new_blocks.append(block)
            continue

        issue_id = id_match.group(1)

        # Check if touchpoint is Unknown or missing
        touchpoint_match = re.search(r'^Touchpoint:\s*(.+)$', block, re.MULTILINE)
        if touchpoint_match:
            current_touchpoint = touchpoint_match.group(1).strip()

            if current_touchpoint in ['Unknown', 'N/A', '[category_name]',
                                     '[images|forms|headings|landmarks|color|language|focus|etc.]']:
                # Try to fix it
                if issue_id in reverse_mapping:
                    correct_touchpoint = reverse_mapping[issue_id]
                    block = re.sub(
                        r'^Touchpoint:\s*.+$',
                        f'Touchpoint: {correct_touchpoint}',
                        block,
                        flags=re.MULTILINE
                    )
                    fixed_count += 1
                    print(f"  Fixed {issue_id}: {current_touchpoint} → {correct_touchpoint}")
                else:
                    still_missing.append(issue_id)

        new_blocks.append(block)

    # Write back
    new_content = ''.join(new_blocks)
    catalog_path.write_text(new_content, encoding='utf-8')

    print(f"\n✅ Fixed {fixed_count} touchpoint assignments")

    if still_missing:
        print(f"\n⚠️  Still missing touchpoints for {len(still_missing)} issues:")
        for issue_id in still_missing[:20]:  # Show first 20
            print(f"  - {issue_id}")
        if len(still_missing) > 20:
            print(f"  ... and {len(still_missing) - 20} more")

    return fixed_count, still_missing


def main():
    """Main entry point"""
    catalog_path = Path(__file__).parent / 'ISSUE_CATALOG.md'

    if not catalog_path.exists():
        print(f"Error: {catalog_path} not found")
        return 1

    fixed_count, still_missing = fix_catalog(catalog_path)

    print(f"\n📝 Updated {catalog_path}")

    return 0 if not still_missing else 0  # Don't fail, just warn


if __name__ == '__main__':
    exit(main())
