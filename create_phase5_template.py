#!/usr/bin/env python3
import json

with open('phase5_errors_other_strings.json', 'r', encoding='utf-8') as f:
    phase5 = json.load(f)

entries = []
for category_name, issues in phase5['categories'].items():
    for issue in issues:
        for string_data in issue['strings']:
            entries.append({
                'msgctxt': string_data['msgctxt'],
                'msgid': string_data['msgid'],
                'msgstr': '',
                'issue_code': string_data['issue_code'],
                'field': string_data['field'],
                'category': 'Errors: Other'
            })

template = {
    'metadata': {'phase': 5, 'name': 'Errors: Other', 'total_entries': len(entries)},
    'entries': entries
}

with open('phase5_translation_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, indent=2, ensure_ascii=False)

print(f"Created Phase 5 translation template")
print(f"Total entries: {len(entries)}")
print(f"Estimated batches: {(len(entries) + 14) // 15}")
print(f"Saved to: phase5_translation_template.json")
