#!/usr/bin/env python3
"""
Create Phase 4 translation template for Landmarks.
"""

import json
from collections import defaultdict

# Load completed issues from all previous phases
completed_issues = set()

for phase_file in ['phase1_strings.json', 'phase2_ai_strings.json', 'phase3_warnings_strings.json']:
    with open(phase_file, 'r') as f:
        phase = json.load(f)
        for category, issues in phase['categories'].items():
            for issue in issues:
                completed_issues.add(issue['issue_code'])

print(f"Completed issues from Phases 1-3: {len(completed_issues)}")

# Load all extracted strings
with open('extracted_strings.json', 'r') as f:
    all_data = json.load(f)

# Filter for Landmark issues
landmark_issues = defaultdict(list)
total_strings = 0

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    # Only include Landmark issues not already completed
    if ('Landmark' in issue_code or 'landmark' in issue_code) and issue_code not in completed_issues:
        if issue_code not in [i['issue_code'] for i in landmark_issues['Landmarks']]:
            landmark_issues['Landmarks'].append({
                'issue_code': issue_code,
                'strings': []
            })

        # Add string to this issue
        for issue in landmark_issues['Landmarks']:
            if issue['issue_code'] == issue_code:
                issue['strings'].append(string_data)
                total_strings += 1
                break

# Save Phase 4 data
phase4_data = {
    'phase': 4,
    'name': 'Landmarks',
    'description': 'ARIA landmark and region accessibility issues',
    'total_issues': len(landmark_issues['Landmarks']),
    'total_strings': total_strings,
    'categories': {
        'Landmarks': landmark_issues['Landmarks']
    }
}

with open('phase4_landmarks_strings.json', 'w', encoding='utf-8') as f:
    json.dump(phase4_data, f, indent=2, ensure_ascii=False)

print(f"\nPhase 4: Landmarks")
print(f"=" * 60)
print(f"Total issues: {len(landmark_issues['Landmarks'])}")
print(f"Total strings: {total_strings}")
print(f"\nTop 10 issues by string count:")

# Sort by string count
sorted_issues = sorted(landmark_issues['Landmarks'], key=lambda x: len(x['strings']), reverse=True)
for i, issue in enumerate(sorted_issues[:10]):
    print(f"  {i+1}. {issue['issue_code']}: {len(issue['strings'])} strings")

if len(sorted_issues) > 10:
    remaining = sum(len(i['strings']) for i in sorted_issues[10:])
    print(f"  ... and {len(sorted_issues) - 10} more issues ({remaining} strings)")

print(f"\nSaved to: phase4_landmarks_strings.json")
