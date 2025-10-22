#!/usr/bin/env python3
"""
Audit catalog entries to identify which need what_generic fields.

Simple version that directly parses the catalog file without imports.

Usage:
    python3 scripts/audit_generic_descriptions_simple.py
    python3 scripts/audit_generic_descriptions_simple.py --generate-template
"""

import re
import sys
from pathlib import Path


def has_placeholders(text):
    """Check if text contains placeholder patterns like {variable}"""
    if not text:
        return False
    return bool(re.search(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', text))


def extract_placeholders(text):
    """Extract all placeholder names from text"""
    if not text:
        return []
    return re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', text)


def is_likely_grouped(error_code):
    """
    Determine if this error is likely to appear multiple times on a page.

    Errors likely to be grouped:
    - Multiple of same element type (ErrMultiple*, ErrDuplicate*)
    - Element-level checks (each element checked individually)
    - Not page-level checks (only one per page)
    """
    # Page-level errors (only one per page) - NOT likely to be grouped
    page_level_indicators = [
        'ErrNoPageTitle', 'ErrEmptyPageTitle', 'ErrNoPageLanguage',
        'ErrNoH1', 'ErrNoMain', 'DiscoPage', 'DiscoBreakpoints'
    ]

    if any(indicator in error_code for indicator in page_level_indicators):
        return False

    # Explicitly multiple/duplicate - VERY likely to be grouped
    if any(prefix in error_code for prefix in ['ErrMultiple', 'ErrDuplicate', 'DiscoFont']):
        return True

    # Discovery items - often appear multiple times
    if error_code.startswith('Disco'):
        return True

    # Element-level errors - likely to be grouped
    # Most element checks can fail on multiple elements
    return True


def parse_catalog_file():
    """Parse the catalog file and extract entries"""

    catalog_file = Path(__file__).parent.parent / 'auto_a11y' / 'reporting' / 'issue_descriptions_enhanced.py'

    with open(catalog_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the descriptions dictionary
    # Pattern: 'ErrorCode': {  ...fields...  },
    entries = []

    # Split content into individual entry blocks
    # Each entry starts with 'CODE': { and ends with },
    pattern = r"'([A-Z][a-zA-Z0-9_]+)':\s*\{([^}]+?'what':[^}]+?)\},"

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        error_code = match.group(1)
        entry_content = match.group(2)

        # Extract 'what' field
        what_match = re.search(r"'what':\s*['\"](.+?)['\"](?:,|\s*$)", entry_content, re.DOTALL)
        what = what_match.group(1) if what_match else ''

        # Extract 'what_generic' field if it exists
        what_generic_match = re.search(r"'what_generic':\s*['\"](.+?)['\"](?:,|\s*$)", entry_content, re.DOTALL)
        what_generic = what_generic_match.group(1) if what_generic_match else ''

        entries.append({
            'code': error_code,
            'what': what,
            'what_generic': what_generic
        })

    return entries


def audit_catalog():
    """Audit the catalog and report entries needing what_generic fields"""

    print("=" * 80)
    print("CATALOG AUDIT: Entries Needing what_generic Fields")
    print("=" * 80)
    print()

    entries = parse_catalog_file()

    needs_generic = []
    has_generic = []
    no_placeholders = []

    print(f"Found {len(entries)} catalog entries\n")

    for entry in entries:
        error_code = entry['code']
        what = entry['what']
        what_generic = entry['what_generic']

        has_placeholders_in_what = has_placeholders(what)

        if has_placeholders_in_what:
            if what_generic:
                has_generic.append(entry)
            else:
                placeholders = extract_placeholders(what)
                likely_grouped = is_likely_grouped(error_code)

                needs_generic.append({
                    'code': error_code,
                    'what': what,
                    'placeholders': placeholders,
                    'likely_grouped': likely_grouped
                })
        else:
            no_placeholders.append(error_code)

    # Report results
    print(f"✅ Entries with what_generic already defined: {len(has_generic)}")
    for entry in has_generic:
        print(f"   - {entry['code']}")
    print()

    print(f"⚠️  Entries with placeholders but NO what_generic: {len(needs_generic)}")
    print()

    # Sort by priority (likely grouped first)
    needs_generic_sorted = sorted(needs_generic, key=lambda x: (not x['likely_grouped'], x['code']))

    # High priority (likely to be grouped)
    high_priority = [e for e in needs_generic_sorted if e['likely_grouped']]
    low_priority = [e for e in needs_generic_sorted if not e['likely_grouped']]

    print(f"🔴 HIGH PRIORITY ({len(high_priority)}) - Likely to appear multiple times:")
    print("-" * 80)
    for entry in high_priority[:20]:  # Show first 20
        print(f"\n{entry['code']}")
        print(f"  Placeholders: {', '.join(entry['placeholders'])}")
        what_preview = entry['what'].replace('\n', ' ')[:100]
        print(f"  Current: {what_preview}...")

    if len(high_priority) > 20:
        print(f"\n... and {len(high_priority) - 20} more high priority entries")

    print("\n" + "=" * 80)
    print(f"🟡 LOWER PRIORITY ({len(low_priority)}) - Less likely to be grouped:")
    print("-" * 80)
    if low_priority:
        print(f"  (Run with --show-all to see all {len(low_priority)} entries)")

    print("\n" + "=" * 80)
    print(f"✅ No placeholders, no action needed: {len(no_placeholders)}")
    print("=" * 80)

    return {
        'has_generic': has_generic,
        'needs_generic': needs_generic_sorted,
        'no_placeholders': no_placeholders,
        'high_priority': high_priority,
        'low_priority': low_priority
    }


def generate_template(results):
    """Generate a template file with suggested what_generic text"""

    print("\n" + "=" * 80)
    print("GENERATING TEMPLATE")
    print("=" * 80)

    output_file = Path(__file__).parent.parent / 'scripts' / 'what_generic_template.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Template for adding what_generic fields\n")
        f.write("# Review each entry and write properly generic text\n")
        f.write("# Then manually add these to issue_descriptions_enhanced.py\n\n")

        f.write("=" * 80 + "\n")
        f.write(f"HIGH PRIORITY ({len(results['high_priority'])}) - Likely to be grouped on pages\n")
        f.write("=" * 80 + "\n\n")

        for entry in results['high_priority']:
            f.write(f"Error Code: {entry['code']}\n")
            f.write(f"Placeholders: {', '.join(entry['placeholders'])}\n")
            f.write(f"Current 'what': {entry['what']}\n")
            f.write(f"\nSuggested 'what_generic':\n")
            f.write(f"# TODO: Write generic text without specific values\n")
            f.write(f"# Remove references to counts, specific element names, etc.\n")
            f.write(f"# Example: 'Multiple landmarks...' instead of 'Found {{count}} landmarks...'\n\n")
            f.write("-" * 80 + "\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write(f"LOWER PRIORITY ({len(results['low_priority'])}) - Less likely to be grouped\n")
        f.write("=" * 80 + "\n\n")

        for entry in results['low_priority']:
            f.write(f"Error Code: {entry['code']}\n")
            f.write(f"Placeholders: {', '.join(entry['placeholders'])}\n")
            f.write(f"Current 'what': {entry['what']}\n")
            f.write(f"\nSuggested 'what_generic':\n")
            f.write(f"# TODO: Write generic text without specific values\n\n")
            f.write("-" * 80 + "\n\n")

    print(f"\n✅ Template written to: {output_file}")
    print("Review the template and manually add what_generic fields to the catalog")


if __name__ == '__main__':
    results = audit_catalog()

    if '--generate-template' in sys.argv:
        generate_template(results)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total entries analyzed: {len(results['has_generic']) + len(results['needs_generic']) + len(results['no_placeholders'])}")
    print(f"Already have what_generic: {len(results['has_generic'])}")
    print(f"Need what_generic - High Priority: {len(results['high_priority'])}")
    print(f"Need what_generic - Lower Priority: {len(results['low_priority'])}")
    print(f"No action needed: {len(results['no_placeholders'])}")
    print()
    print("Run with --generate-template to create a template file for adding what_generic fields")
