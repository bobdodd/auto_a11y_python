#!/usr/bin/env python3
"""
Clean up old language error codes from the fixture_tests collection.
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'auto_a11y')

print(f"Connecting to MongoDB: {MONGO_URI}")
print(f"Database: {DB_NAME}\n")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("=" * 70)
print("CLEANING fixture_tests COLLECTION")
print("=" * 70)

# Delete old error code tests
old_codes_to_delete = ['WarnElementLangEmpty', 'WarnEmptyLangAttribute', 'ErrElementLangEmpty']

for code in old_codes_to_delete:
    count = db.fixture_tests.count_documents({'expected_code': code})
    if count > 0:
        print(f"\n❌ Deleting {count} fixture tests for '{code}'")
        result = db.fixture_tests.delete_many({'expected_code': code})
        print(f"   Deleted {result.deleted_count} documents")

# Update fixture_path references that point to old files
print("\n" + "=" * 70)
print("UPDATING FIXTURE PATHS")
print("=" * 70)

# These files were renamed
renames = {
    'Language/WarnElementLangEmpty_001_violations_basic.html': 'Language/ErrEmptyLanguageAttribute_001_violations_basic.html',
    'Language/WarnElementLangEmpty_002_correct_with_codes.html': 'Language/ErrEmptyLanguageAttribute_002_correct_with_valid_lang.html'
}

for old_path, new_path in renames.items():
    count = db.fixture_tests.count_documents({'fixture_path': old_path})
    if count > 0:
        print(f"\n📝 Updating {count} references from:")
        print(f"   '{old_path}'")
        print(f"   to '{new_path}'")
        result = db.fixture_tests.update_many(
            {'fixture_path': old_path},
            {'$set': {
                'fixture_path': new_path,
                'expected_code': 'ErrEmptyLanguageAttribute'
            }}
        )
        print(f"   Updated {result.modified_count} documents")

print("\n" + "=" * 70)
print("✅ CLEANUP COMPLETE!")
print("=" * 70)
print("\nRemaining language error codes in fixture_tests:")

# Show what's left
pipeline = [
    {"$match": {"expected_code": {"$regex": "Lang", "$options": "i"}}},
    {"$group": {"_id": "$expected_code", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]

results = list(db.fixture_tests.aggregate(pipeline))
for result in results:
    icon = "✅" if result['_id'] in ['ErrHtmlLangEmpty', 'ErrEmptyLanguageAttribute'] else "  "
    print(f"{icon} {result['_id']}: {result['count']} fixture tests")

print("\n" + "=" * 70)

client.close()
