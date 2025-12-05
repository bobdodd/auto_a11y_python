#!/usr/bin/env python3
"""
Create flat translation template from phase3_warnings_strings.json
"""

import json

# Load phase3 data
with open('phase3_warnings_strings.json', 'r', encoding='utf-8') as f:
    phase3 = json.load(f)

# Flatten into template format
entries = []

for category_name, issues in phase3['categories'].items():
    for issue in issues:
        for string_data in issue['strings']:
            entries.append({
                'msgctxt': string_data['msgctxt'],
                'msgid': string_data['msgid'],
                'msgstr': '',  # Empty, to be translated
                'issue_code': string_data['issue_code'],
                'field': string_data['field'],
                'category': 'Warnings'
            })

template = {
    'metadata': {
        'phase': 3,
        'name': 'Warnings',
        'total_entries': len(entries)
    },
    'entries': entries
}

# Save template
with open('phase3_translation_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)

print(f"Created Phase 3 translation template")
print(f"Total entries: {len(entries)}")
print(f"Estimated batches: {(len(entries) + 14) // 15}")
print(f"Saved to: phase3_translation_template.json")
