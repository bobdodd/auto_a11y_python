#!/usr/bin/env python3
"""Fix screenshot paths in database to remove 'screenshots/' prefix"""

from auto_a11y.core.database import Database

db = Database('mongodb://localhost:27017/', 'auto_a11y')

# Find all pages with screenshot_path starting with 'screenshots/'
pages_to_update = list(db.pages.find({'screenshot_path': {'$regex': '^screenshots/'}}))

print(f'Found {len(pages_to_update)} pages with screenshots/ prefix')

updated = 0
for page in pages_to_update:
    old_path = page['screenshot_path']
    new_path = old_path.replace('screenshots/', '', 1)

    db.pages.update_one(
        {'_id': page['_id']},
        {'$set': {'screenshot_path': new_path}}
    )
    updated += 1

    if updated % 100 == 0:
        print(f'Updated {updated} pages...')

print(f'\nDone! Updated {updated} pages')
print('Screenshot paths now use just filenames without screenshots/ prefix')