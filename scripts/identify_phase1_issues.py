#!/usr/bin/env python3
"""
Identify Phase 1 issue categories from extracted strings.

Phase 1 categories:
- Images: Issues related to images, alt text
- Forms: Issues related to form inputs, labels
- Headings: Issues related to heading structure
- Color Contrast: Issues related to color and contrast
"""

import json
import sys
from pathlib import Path

# Phase 1 category patterns
PHASE1_PATTERNS = {
    'Images': [
        'Image', 'Alt', 'Graphic', 'Picture', 'Icon', 'Svg',
        'ErrNoAlt', 'ErrEmptyAlt', 'ErrImageWithEmptyAlt', 'ErrDecorativeImage',
        'ErrImageButton', 'ErrSvgWithoutRole', 'ErrIconWithoutLabel'
    ],
    'Forms': [
        'Form', 'Input', 'Label', 'Button', 'Checkbox', 'Radio', 'Select',
        'ErrNoLabel', 'ErrEmptyLabel', 'ErrInvalidLabel', 'ErrMissingLabel',
        'ErrFormControl', 'ErrFieldset', 'ErrLegend'
    ],
    'Headings': [
        'Heading', 'Title', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
        'ErrEmptyHeading', 'ErrSkippedHeadingLevel', 'ErrMissingH1',
        'ErrMultipleH1', 'ErrHeadingLevel'
    ],
    'Contrast': [
        'Contrast', 'Color', 'Foreground', 'Background',
        'ErrInsufficientContrast', 'ErrLowContrast', 'ErrColorContrast',
        'ErrTextContrast'
    ]
}


def categorize_issue(issue_code, issue_strings):
    """Determine which Phase 1 category an issue belongs to"""
    # Check title and what fields for keywords
    text_to_check = ""
    for string_data in issue_strings:
        if string_data['field'] in ('title', 'what'):
            text_to_check += " " + string_data['msgid']

    text_to_check += " " + issue_code
    text_lower = text_to_check.lower()

    # Check each category
    for category, patterns in PHASE1_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text_lower:
                return category

    return None


def main():
    extracted_file = 'extracted_strings.json'

    if not Path(extracted_file).exists():
        print(f"Error: {extracted_file} not found", file=sys.stderr)
        print("Run: python scripts/extract_issue_descriptions.py > extracted_strings.json", file=sys.stderr)
        return 1

    # Load extracted strings
    with open(extracted_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    strings = data.get('strings', [])

    # Group by issue code
    issues_by_code = {}
    for string_data in strings:
        issue_code = string_data['issue_code']
        if issue_code not in issues_by_code:
            issues_by_code[issue_code] = []
        issues_by_code[issue_code].append(string_data)

    # Categorize issues
    phase1_issues = {
        'Images': [],
        'Forms': [],
        'Headings': [],
        'Contrast': []
    }

    uncategorized = []

    for issue_code, issue_strings in issues_by_code.items():
        category = categorize_issue(issue_code, issue_strings)
        if category:
            phase1_issues[category].append({
                'issue_code': issue_code,
                'string_count': len(issue_strings),
                'strings': issue_strings
            })
        else:
            uncategorized.append(issue_code)

    # Print summary
    print("Phase 1 Issue Categories Summary")
    print("=" * 60)

    total_issues = 0
    total_strings = 0

    for category, issues in phase1_issues.items():
        issue_count = len(issues)
        string_count = sum(issue['string_count'] for issue in issues)
        total_issues += issue_count
        total_strings += string_count

        print(f"\n{category}:")
        print(f"  Issues: {issue_count}")
        print(f"  Strings: {string_count}")

        if issue_count > 0:
            print(f"  Sample issues:")
            for issue in sorted(issues, key=lambda x: x['issue_code'])[:5]:
                print(f"    - {issue['issue_code']} ({issue['string_count']} strings)")

    print(f"\n{'=' * 60}")
    print(f"Total Phase 1:")
    print(f"  Issues: {total_issues}")
    print(f"  Strings: {total_strings}")
    print(f"\nUncategorized issues: {len(uncategorized)}")

    # Save Phase 1 strings to file
    phase1_output = {
        'categories': phase1_issues,
        'summary': {
            'total_issues': total_issues,
            'total_strings': total_strings,
            'by_category': {
                cat: {
                    'issues': len(issues),
                    'strings': sum(i['string_count'] for i in issues)
                }
                for cat, issues in phase1_issues.items()
            }
        }
    }

    output_file = 'phase1_strings.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(phase1_output, f, indent=2, ensure_ascii=False)

    print(f"\nPhase 1 strings saved to: {output_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
