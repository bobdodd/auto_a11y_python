#!/usr/bin/env python3
"""
Create Phase 3 translation template for Warnings.
"""

import json
from collections import defaultdict

# Load phase1 and phase2 completed issues
completed_issues = set()

with open('phase1_strings.json', 'r') as f:
    phase1 = json.load(f)
    for category, issues in phase1['categories'].items():
        for issue in issues:
            completed_issues.add(issue['issue_code'])

with open('phase2_ai_strings.json', 'r') as f:
    phase2 = json.load(f)
    for category, issues in phase2['categories'].items():
        for issue in issues:
            completed_issues.add(issue['issue_code'])

print(f"Completed issues from Phase 1 & 2: {len(completed_issues)}")

# Load all extracted strings
with open('extracted_strings.json', 'r') as f:
    all_data = json.load(f)

# Filter for Warning issues
warning_issues = defaultdict(list)
total_strings = 0

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    # Only include Warn issues not already completed
    if 'Warn' in issue_code and issue_code not in completed_issues:
        if issue_code not in [i['issue_code'] for i in warning_issues['Warnings']]:
            warning_issues['Warnings'].append({
                'issue_code': issue_code,
                'strings': []
            })

        # Add string to this issue
        for issue in warning_issues['Warnings']:
            if issue['issue_code'] == issue_code:
                issue['strings'].append(string_data)
                total_strings += 1
                break

# Save Phase 3 data
phase3_data = {
    'phase': 3,
    'name': 'Warnings',
    'description': 'Accessibility warnings - potential issues that may impact users',
    'total_issues': len(warning_issues['Warnings']),
    'total_strings': total_strings,
    'categories': {
        'Warnings': warning_issues['Warnings']
    }
}

with open('phase3_warnings_strings.json', 'w', encoding='utf-8') as f:
    json.dump(phase3_data, f, indent=2, ensure_ascii=False)

print(f"\nPhase 3: Warnings")
print(f"=" * 60)
print(f"Total issues: {len(warning_issues['Warnings'])}")
print(f"Total strings: {total_strings}")
print(f"\nTop 10 issues by string count:")

# Sort by string count
sorted_issues = sorted(warning_issues['Warnings'], key=lambda x: len(x['strings']), reverse=True)
for i, issue in enumerate(sorted_issues[:10]):
    print(f"  {i+1}. {issue['issue_code']}: {len(issue['strings'])} strings")

if len(sorted_issues) > 10:
    remaining = sum(len(i['strings']) for i in sorted_issues[10:])
    print(f"  ... and {len(sorted_issues) - 10} more issues ({remaining} strings)")

print(f"\nSaved to: phase3_warnings_strings.json")
