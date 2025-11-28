#!/usr/bin/env python3
"""Delete test results for a specific website while keeping scraped pages"""

from pymongo import MongoClient
import os
from datetime import datetime

# Get MongoDB URI from environment or use default
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'auto_a11y')

# Website ID for Credit Valley main website
WEBSITE_ID = '6900fd1f4298b1efb3e50739'

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

print(f"Deleting test results for website: {WEBSITE_ID}")
print(f"Started at: {datetime.now()}")
print()

# Step 1: Get all pages for this website
pages = list(db.pages.find({'website_id': WEBSITE_ID}, {'_id': 1}))
page_ids = [str(p['_id']) for p in pages]
print(f"Found {len(page_ids)} pages for this website")

# Step 2: Count test_result_items for these pages
items_count = db.test_result_items.count_documents({'page_id': {'$in': page_ids}})
print(f"Found {items_count:,} test result items (violations/warnings) to delete")

# Step 3: Count test_results for these pages
test_results_count = db.test_results.count_documents({'page_id': {'$in': page_ids}})
print(f"Found {test_results_count:,} test result documents to delete")
print()

# Step 4: Delete test_result_items first
if items_count > 0:
    print(f"Deleting {items_count:,} test result items...")
    result = db.test_result_items.delete_many({'page_id': {'$in': page_ids}})
    print(f"✓ Deleted {result.deleted_count:,} test result items")
else:
    print("No test result items to delete")

print()

# Step 5: Delete test_results
if test_results_count > 0:
    print(f"Deleting {test_results_count:,} test result documents...")
    result = db.test_results.delete_many({'page_id': {'$in': page_ids}})
    print(f"✓ Deleted {result.deleted_count:,} test results")
else:
    print("No test results to delete")

print()

# Step 6: Reset cached counts on pages
print("Resetting cached violation/warning counts on pages...")
result = db.pages.update_many(
    {'website_id': WEBSITE_ID},
    {'$set': {
        'violation_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'pass_count': 0,
        'status': 'discovered'  # Reset status back to discovered
    }}
)
print(f"✓ Reset counts on {result.modified_count} pages")

print()

# Verify pages are kept
pages_count = db.pages.count_documents({'website_id': WEBSITE_ID})
print(f"Pages kept: {pages_count:,} (not deleted)")

# Check discovered pages - these will be kept
discovered_pages_count = db.discovered_pages.count_documents({'website_id': WEBSITE_ID})
print(f"Discovered pages kept: {discovered_pages_count:,} (not deleted)")

print()
print(f"Completed at: {datetime.now()}")
print()
print("Summary:")
print(f"  - Test result items deleted: {items_count:,}")
print(f"  - Test result documents deleted: {test_results_count:,}")
print(f"  - Pages preserved: {pages_count:,}")
print(f"  - Discovered pages preserved: {discovered_pages_count:,}")
