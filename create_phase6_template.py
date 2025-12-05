#!/usr/bin/env python3
"""
Create flat translation template from phase6_remaining_strings.json
"""

import json

# Load phase6 data
with open('phase6_remaining_strings.json', 'r', encoding='utf-8') as f:
    phase6 = json.load(f)

# Flatten into template format
entries = []

for category_name, issues in phase6['categories'].items():
    for issue in issues:
        for string_data in issue['strings']:
            entries.append({
                'msgctxt': string_data['msgctxt'],
                'msgid': string_data['msgid'],
                'msgstr': '',  # Empty, to be translated
                'issue_code': string_data['issue_code'],
                'field': string_data['field'],
                'category': 'All Remaining'
            })

template = {
    'metadata': {
        'phase': 6,
        'name': 'All Remaining',
        'total_entries': len(entries)
    },
    'entries': entries
}

# Save template
with open('phase6_translation_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)

print(f"Created Phase 6 translation template")
print(f"Total entries: {len(entries)}")
print(f"Estimated batches: {(len(entries) + 14) // 15}")
print(f"Saved to: phase6_translation_template.json")
