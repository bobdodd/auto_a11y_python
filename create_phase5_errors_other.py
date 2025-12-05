#!/usr/bin/env python3
"""
Create Phase 5 translation template for Errors: Other.
"""

import json
from collections import defaultdict

# Load completed issues from all previous phases
completed_issues = set()

for phase_file in ['phase1_strings.json', 'phase2_ai_strings.json', 'phase3_warnings_strings.json', 'phase4_landmarks_strings.json']:
    with open(phase_file, 'r') as f:
        phase = json.load(f)
        for category, issues in phase['categories'].items():
            for issue in issues:
                completed_issues.add(issue['issue_code'])

print(f"Completed issues from Phases 1-4: {len(completed_issues)}")

# Load all extracted strings
with open('extracted_strings.json', 'r') as f:
    all_data = json.load(f)

# Filter for "Other" error issues
# These are errors that don't fit into specific categories
other_error_issues = defaultdict(list)
total_strings = 0

# Categories to exclude (already done or will be done separately)
exclude_categories = ['Landmark', 'landmark', 'Warn', 'Tab', 'Language', 'Lang', 'ARIA', 'Aria',
                      'Link', 'Anchor', 'List', 'Keyboard', 'Focus', 'Button', 'Table', 'Navigation', 'Nav']

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    # Only include error issues not already completed and not in specific categories
    if 'Err' in issue_code and issue_code not in completed_issues:
        # Check if it's in a specific category we're excluding
        is_excluded = any(cat in issue_code for cat in exclude_categories)

        if not is_excluded:
            if issue_code not in [i['issue_code'] for i in other_error_issues['Errors: Other']]:
                other_error_issues['Errors: Other'].append({
                    'issue_code': issue_code,
                    'strings': []
                })

            # Add string to this issue
            for issue in other_error_issues['Errors: Other']:
                if issue['issue_code'] == issue_code:
                    issue['strings'].append(string_data)
                    total_strings += 1
                    break

# Save Phase 5 data
phase5_data = {
    'phase': 5,
    'name': 'Errors: Other',
    'description': 'Miscellaneous accessibility errors not in specific categories',
    'total_issues': len(other_error_issues['Errors: Other']),
    'total_strings': total_strings,
    'categories': {
        'Errors: Other': other_error_issues['Errors: Other']
    }
}

with open('phase5_errors_other_strings.json', 'w', encoding='utf-8') as f:
    json.dump(phase5_data, f, indent=2, ensure_ascii=False)

print(f"\nPhase 5: Errors: Other")
print(f"=" * 60)
print(f"Total issues: {len(other_error_issues['Errors: Other'])}")
print(f"Total strings: {total_strings}")
print(f"\nTop 10 issues by string count:")

# Sort by string count
sorted_issues = sorted(other_error_issues['Errors: Other'], key=lambda x: len(x['strings']), reverse=True)
for i, issue in enumerate(sorted_issues[:10]):
    print(f"  {i+1}. {issue['issue_code']}: {len(issue['strings'])} strings")

if len(sorted_issues) > 10:
    remaining = sum(len(i['strings']) for i in sorted_issues[10:])
    print(f"  ... and {len(sorted_issues) - 10} more issues ({remaining} strings)")

print(f"\nSaved to: phase5_errors_other_strings.json")
