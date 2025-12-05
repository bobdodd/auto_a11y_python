#!/usr/bin/env python3
"""
Analyze remaining untranslated strings by issue type (Err, Warn, Disco, Info).
"""

import json
from collections import defaultdict
import re

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

# Group remaining issues by category/type
remaining_issues = defaultdict(lambda: {'issues': set(), 'string_count': 0, 'issue_list': []})
total_remaining_strings = 0

for string_data in all_data['strings']:
    issue_code = string_data['issue_code']

    if issue_code not in phase1_issues:
        # Categorize by error type and topic
        if issue_code.startswith('AI_'):
            category = 'AI-Detected Issues'
        elif 'Disco' in issue_code:
            # Extract topic from discovery issues
            if 'Font' in issue_code:
                category = 'Discovery: Fonts'
            elif 'JS' in issue_code or 'Script' in issue_code:
                category = 'Discovery: JavaScript'
            elif 'PDF' in issue_code:
                category = 'Discovery: PDF'
            elif 'Map' in issue_code:
                category = 'Discovery: Maps'
            elif 'Responsive' in issue_code or 'Breakpoint' in issue_code:
                category = 'Discovery: Responsive'
            elif 'Video' in issue_code or 'Audio' in issue_code or 'Media' in issue_code:
                category = 'Discovery: Media'
            else:
                category = 'Discovery: Other'
        elif 'Err' in issue_code:
            # Try to extract topic from error issues
            if 'Link' in issue_code or 'Anchor' in issue_code:
                category = 'Errors: Links'
            elif 'Button' in issue_code:
                category = 'Errors: Buttons'
            elif 'Landmark' in issue_code or 'Region' in issue_code:
                category = 'Errors: Landmarks'
            elif 'Table' in issue_code:
                category = 'Errors: Tables'
            elif 'List' in issue_code:
                category = 'Errors: Lists'
            elif 'Lang' in issue_code or 'Language' in issue_code:
                category = 'Errors: Language'
            elif 'Title' in issue_code or 'Page' in issue_code:
                category = 'Errors: Page'
            elif 'Navigation' in issue_code or 'Nav' in issue_code:
                category = 'Errors: Navigation'
            elif 'ARIA' in issue_code or 'Aria' in issue_code:
                category = 'Errors: ARIA'
            elif 'Label' in issue_code or 'Name' in issue_code:
                category = 'Errors: Labels'
            elif 'Tab' in issue_code:
                category = 'Errors: Tabs'
            elif 'Keyboard' in issue_code or 'Focus' in issue_code:
                category = 'Errors: Keyboard'
            else:
                category = 'Errors: Other'
        elif 'Warn' in issue_code:
            category = 'Warnings'
        elif 'Info' in issue_code:
            category = 'Info'
        else:
            category = 'Uncategorized'

        if issue_code not in [i['code'] for i in remaining_issues[category]['issue_list']]:
            remaining_issues[category]['issue_list'].append({
                'code': issue_code,
                'string_count': 0
            })

        # Find and increment string count
        for issue in remaining_issues[category]['issue_list']:
            if issue['code'] == issue_code:
                issue['string_count'] += 1
                break

        remaining_issues[category]['issues'].add(issue_code)
        remaining_issues[category]['string_count'] += 1
        total_remaining_strings += 1

# Print analysis
print(f"\nTotal remaining: {total_remaining_strings} strings\n")
print("=" * 80)
print(f"{'Category':<35} {'Issues':<10} {'Strings':<10} {'Avg/Issue':<10}")
print("=" * 80)

# Sort by string count descending
sorted_categories = sorted(
    remaining_issues.items(),
    key=lambda x: x[1]['string_count'],
    reverse=True
)

for category, data in sorted_categories:
    issue_count = len(data['issues'])
    string_count = data['string_count']
    avg_per_issue = string_count / issue_count if issue_count > 0 else 0
    print(f"{category:<35} {issue_count:<10} {string_count:<10} {avg_per_issue:<10.1f}")

print("=" * 80)

# Show details for top categories
print("\n\nTop categories by string count:\n")
print("=" * 80)

for category, data in sorted_categories[:10]:
    print(f"\n{category}: {len(data['issues'])} issues, {data['string_count']} strings")

    # Sort issues by string count
    sorted_issues = sorted(data['issue_list'], key=lambda x: x['string_count'], reverse=True)

    # Show top 10 issues
    for i, issue in enumerate(sorted_issues[:10]):
        print(f"  {i+1}. {issue['code']:<50} {issue['string_count']} strings")

    if len(sorted_issues) > 10:
        remaining = sum(i['string_count'] for i in sorted_issues[10:])
        print(f"  ... and {len(sorted_issues) - 10} more issues ({remaining} strings)")

print("\n" + "=" * 80)
print("\nRecommended Phase 2 targets:")
print("=" * 80)

# Find good candidates
good_sizes = [(cat, data) for cat, data in sorted_categories
              if 30 <= data['string_count'] <= 150]

if good_sizes:
    print("\nGood-sized categories (30-150 strings):")
    for cat, data in good_sizes:
        print(f"  - {cat}: {len(data['issues'])} issues, {data['string_count']} strings")
        print(f"    Effort: ~{data['string_count'] // 15 + 1} batches at 15 strings/batch")
        print()
