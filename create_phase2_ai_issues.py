#!/usr/bin/env python3
"""
Create Phase 2 translation template for AI-Detected Issues.
Based on successful Phase 1 workflow.
"""

import json
from collections import defaultdict

# Load phase1 completed issues
with open('phase1_strings.json', 'r') as f:
    phase1 = json.load(f)

phase1_issues = set()
for category, issues in phase1['categories'].items():
    for issue in issues:
        phase1_issues.add(issue['issue_code'])

# Load all extracted strings
with open('extracted_strings.json', 'r') as f:
    all_data = json.load(f)

# Filter for AI-detected issues
ai_issues = defaultdict(list)
total_strings = 0

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    # Only include AI_ issues not in phase1
    if issue_code.startswith('AI_') and issue_code not in phase1_issues:
        if issue_code not in [i['issue_code'] for i in ai_issues['AI-Detected']]:
            ai_issues['AI-Detected'].append({
                'issue_code': issue_code,
                'strings': []
            })

        # Add string to this issue
        for issue in ai_issues['AI-Detected']:
            if issue['issue_code'] == issue_code:
                issue['strings'].append(string_data)
                total_strings += 1
                break

# Save Phase 2 data
phase2_data = {
    'phase': 2,
    'name': 'AI-Detected Issues',
    'description': 'AI-detected accessibility issues requiring ARIA markup and focus management',
    'total_issues': len(ai_issues['AI-Detected']),
    'total_strings': total_strings,
    'categories': {
        'AI-Detected': ai_issues['AI-Detected']
    }
}

with open('phase2_ai_strings.json', 'w', encoding='utf-8') as f:
    json.dump(phase2_data, f, indent=2, ensure_ascii=False)

print(f"Phase 2: AI-Detected Issues")
print(f"=" * 60)
print(f"Total issues: {len(ai_issues['AI-Detected'])}")
print(f"Total strings: {total_strings}")
print(f"\nIssues included:")
for issue in ai_issues['AI-Detected']:
    print(f"  - {issue['issue_code']}: {len(issue['strings'])} strings")

print(f"\nSaved to: phase2_ai_strings.json")
