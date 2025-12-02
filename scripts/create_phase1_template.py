#!/usr/bin/env python3
"""
Create translation template for Phase 1 issues.

Reads phase1_strings.json and extracted_strings.json to create a flat template
for AI translation with all necessary metadata.
"""

import json
import sys
from pathlib import Path


def main():
    # Load Phase 1 issue categorization
    phase1_file = 'phase1_strings.json'
    if not Path(phase1_file).exists():
        print(f"Error: {phase1_file} not found", file=sys.stderr)
        print("Run: python scripts/identify_phase1_issues.py", file=sys.stderr)
        return 1

    with open(phase1_file, 'r', encoding='utf-8') as f:
        phase1_data = json.load(f)

    # Load all extracted strings
    extracted_file = 'extracted_strings.json'
    if not Path(extracted_file).exists():
        print(f"Error: {extracted_file} not found", file=sys.stderr)
        return 1

    with open(extracted_file, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)

    all_strings = extracted_data['strings']

    # Build lookup for quick access
    string_lookup = {}
    for string_data in all_strings:
        key = (string_data['issue_code'], string_data['field'])
        string_lookup[key] = string_data

    # Create flat list of entries to translate
    entries = []

    for category, issues in phase1_data['categories'].items():
        for issue in issues:
            issue_code = issue['issue_code']

            # Get all strings for this issue
            for string_data in issue['strings']:
                field = string_data['field']

                # Build entry with all needed metadata
                entry = {
                    'category': category,
                    'issue_code': issue_code,
                    'field': field,
                    'msgctxt': string_data['msgctxt'],
                    'msgid': string_data['msgid'],
                    'msgstr': ''  # To be filled by translation
                }
                entries.append(entry)

    # Create output template
    template = {
        'metadata': {
            'total_entries': len(entries),
            'by_category': {}
        },
        'entries': entries
    }

    # Calculate category counts
    for category in phase1_data['categories'].keys():
        count = sum(1 for e in entries if e['category'] == category)
        template['metadata']['by_category'][category] = count

    # Save template
    output_file = 'phase1_translation_template.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"Created translation template: {output_file}")
    print(f"Total entries: {len(entries)}")
    print(f"\nBy category:")
    for category, count in template['metadata']['by_category'].items():
        print(f"  {category}: {count}")

    print(f"\nNext: python scripts/translate_with_anthropic.py")

    return 0


if __name__ == '__main__':
    sys.exit(main())
