#!/usr/bin/env python3
"""
Create flat translation template from phase4_landmarks_strings.json
"""

import json

# Load phase4 data
with open('phase4_landmarks_strings.json', 'r', encoding='utf-8') as f:
    phase4 = json.load(f)

# Flatten into template format
entries = []

for category_name, issues in phase4['categories'].items():
    for issue in issues:
        for string_data in issue['strings']:
            entries.append({
                'msgctxt': string_data['msgctxt'],
                'msgid': string_data['msgid'],
                'msgstr': '',  # Empty, to be translated
                'issue_code': string_data['issue_code'],
                'field': string_data['field'],
                'category': 'Landmarks'
            })

template = {
    'metadata': {
        'phase': 4,
        'name': 'Landmarks',
        'total_entries': len(entries)
    },
    'entries': entries
}

# Save template
with open('phase4_translation_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)

print(f"Created Phase 4 translation template")
print(f"Total entries: {len(entries)}")
print(f"Estimated batches: {(len(entries) + 14) // 15}")
print(f"Saved to: phase4_translation_template.json")
