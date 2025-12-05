#!/usr/bin/env python3
"""
Create Phase 6 translation template for ALL remaining strings.
"""

import json
from collections import defaultdict

# Load completed issues from all previous phases
completed_issues = set()

phase_files = [
    'phase1_strings.json',
    'phase2_ai_strings.json', 
    'phase3_warnings_strings.json',
    'phase4_landmarks_strings.json',
    'phase5_errors_other_strings.json'
]

for phase_file in phase_files:
    with open(phase_file, 'r') as f:
        phase = json.load(f)
        for category, issues in phase['categories'].items():
            for issue in issues:
                completed_issues.add(issue['issue_code'])

print(f"Completed issues from Phases 1-5: {len(completed_issues)}")

# Load all extracted strings
with open('extracted_strings.json', 'r') as f:
    all_data = json.load(f)

# Get ALL remaining issues
remaining_issues = defaultdict(list)
total_strings = 0

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    # Include any issue not already completed
    if issue_code not in completed_issues:
        if issue_code not in [i['issue_code'] for i in remaining_issues['All Remaining']]:
            remaining_issues['All Remaining'].append({
                'issue_code': issue_code,
                'strings': []
            })

        # Add string to this issue
        for issue in remaining_issues['All Remaining']:
            if issue['issue_code'] == issue_code:
                issue['strings'].append(string_data)
                total_strings += 1
                break

# Save Phase 6 data
phase6_data = {
    'phase': 6,
    'name': 'All Remaining',
    'description': 'Final phase - all remaining accessibility issues',
    'total_issues': len(remaining_issues['All Remaining']),
    'total_strings': total_strings,
    'categories': {
        'All Remaining': remaining_issues['All Remaining']
    }
}

with open('phase6_remaining_strings.json', 'w', encoding='utf-8') as f:
    json.dump(phase6_data, f, indent=2, ensure_ascii=False)

print(f"\nPhase 6: All Remaining")
print(f"=" * 60)
print(f"Total issues: {len(remaining_issues['All Remaining'])}")
print(f"Total strings: {total_strings}")
print(f"\nTop 15 issues by string count:")

# Sort by string count
sorted_issues = sorted(remaining_issues['All Remaining'], key=lambda x: len(x['strings']), reverse=True)
for i, issue in enumerate(sorted_issues[:15]):
    print(f"  {i+1}. {issue['issue_code']}: {len(issue['strings'])} strings")

if len(sorted_issues) > 15:
    remaining = sum(len(i['strings']) for i in sorted_issues[15:])
    print(f"  ... and {len(sorted_issues) - 15} more issues ({remaining} strings)")

print(f"\nSaved to: phase6_remaining_strings.json")
