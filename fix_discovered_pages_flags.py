#!/usr/bin/env python3
"""Fix discovered pages include_in_report flags for Credit Valley project"""

from pymongo import MongoClient
import os

# Get MongoDB URI from environment or use default
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'auto_a11y')

# Credit Valley project ID
PROJECT_ID = '6900fcff4298b1efb3e50738'

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Find discovered pages with include_in_report = False
pages_to_update = list(db.discovered_pages.find({
    'project_id': PROJECT_ID,
    'include_in_report': False
}))

print(f"Found {len(pages_to_update)} discovered pages with include_in_report = False\n")

if pages_to_update:
    print("Updating all discovered pages to have include_in_report = True...\n")

    # Update all pages
    result = db.discovered_pages.update_many(
        {
            'project_id': PROJECT_ID,
            'include_in_report': False
        },
        {
            '$set': {
                'include_in_report': True
            }
        }
    )

    print(f"✓ Updated {result.modified_count} discovered pages")
    print(f"  All discovered pages now have include_in_report = True")

    # Verify
    total_pages = db.discovered_pages.count_documents({'project_id': PROJECT_ID})
    pages_with_true = db.discovered_pages.count_documents({
        'project_id': PROJECT_ID,
        'include_in_report': True
    })

    print(f"\nVerification:")
    print(f"  Total discovered pages: {total_pages}")
    print(f"  Pages with include_in_report = True: {pages_with_true}")

    if pages_with_true == total_pages:
        print("\n✅ SUCCESS: All discovered pages now have include_in_report = True")
    else:
        print(f"\n⚠️  WARNING: {total_pages - pages_with_true} pages still have issues")
else:
    print("No pages need updating. All discovered pages already have include_in_report = True")
