#!/usr/bin/env python3
"""
Analyze remaining untranslated strings by touchpoint to help prioritize Phase 2.
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

print(f"Phase 1 completed: {len(phase1_issues)} issues")

# Load all extracted strings
with open('extracted_strings.json', 'r') as f:
    all_data = json.load(f)

# Group remaining issues by touchpoint
remaining_by_touchpoint = defaultdict(lambda: {'issues': set(), 'string_count': 0})
total_remaining_strings = 0

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    if issue_code not in phase1_issues:
        # Extract touchpoint from issue code
        if issue_code.startswith('AI_'):
            touchpoint = 'AI'
        elif '_' in issue_code:
            touchpoint = issue_code.split('_')[0]
        else:
            touchpoint = 'Other'

        remaining_by_touchpoint[touchpoint]['issues'].add(issue_code)
        remaining_by_touchpoint[touchpoint]['string_count'] += 1
        total_remaining_strings += 1

# Print analysis
print(f"\nTotal remaining: {total_remaining_strings} strings\n")
print("=" * 70)
print(f"{'Touchpoint':<20} {'Issues':<10} {'Strings':<10} {'Avg/Issue':<10}")
print("=" * 70)

# Sort by string count descending
sorted_touchpoints = sorted(
    remaining_by_touchpoint.items(),
    key=lambda x: x[1]['string_count'],
    reverse=True
)

for touchpoint, data in sorted_touchpoints:
    issue_count = len(data['issues'])
    string_count = data['string_count']
    avg_per_issue = string_count / issue_count if issue_count > 0 else 0
    print(f"{touchpoint:<20} {issue_count:<10} {string_count:<10} {avg_per_issue:<10.1f}")

print("=" * 70)

# Show some examples from each touchpoint
print("\n\nSample issues from each touchpoint:\n")
print("=" * 70)

for touchpoint, data in sorted_touchpoints[:10]:  # Top 10 touchpoints
    print(f"\n{touchpoint}: {len(data['issues'])} issues")
    sample_issues = sorted(list(data['issues']))[:5]  # Show first 5
    for issue in sample_issues:
        print(f"  - {issue}")
    if len(data['issues']) > 5:
        print(f"  ... and {len(data['issues']) - 5} more")

print("\n" + "=" * 70)
print("\nRecommendations for Phase 2:")
print("=" * 70)

# Find good candidates for Phase 2
medium_sized = [(tp, data) for tp, data in sorted_touchpoints
                if 50 <= data['string_count'] <= 200]

if medium_sized:
    print("\nMedium-sized touchpoints (50-200 strings, good for next phase):")
    for tp, data in medium_sized:
        print(f"  - {tp}: {len(data['issues'])} issues, {data['string_count']} strings")

small = [(tp, data) for tp, data in sorted_touchpoints
         if data['string_count'] < 50]

if small:
    print("\nSmaller touchpoints (< 50 strings, quick wins):")
    for tp, data in small:
        print(f"  - {tp}: {len(data['issues'])} issues, {data['string_count']} strings")
