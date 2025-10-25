#!/usr/bin/env python3
"""
Cleanup script to remove WarnFieldLabelledByMultipleElements entries from database.
This warning was redundant with an existing error code.
"""

from auto_a11y.core.database import Database
from config import Config

config = Config()
db = Database(config.MONGODB_URI, config.DATABASE_NAME)

# Get the fixture_tests collection
fixture_tests_collection = db.db['fixture_tests']

# Find all entries with this warning code
query = {'expected_code': 'WarnFieldLabelledByMultipleElements'}
results = list(fixture_tests_collection.find(query))

print(f"Found {len(results)} database entries for WarnFieldLabelledByMultipleElements")

if results:
    for result in results:
        print(f"  - fixture_path: {result.get('fixture_path', 'N/A')}")
        print(f"    tested_at: {result.get('tested_at', 'N/A')}")
        print(f"    passed: {result.get('passed', 'N/A')}")

    # Delete all entries
    delete_result = fixture_tests_collection.delete_many(query)
    print(f"\nDeleted {delete_result.deleted_count} entries from fixture_tests collection")

    # Verify deletion
    remaining = fixture_tests_collection.count_documents(query)
    print(f"Remaining entries: {remaining}")

    if remaining == 0:
        print("\n✓ Successfully removed all WarnFieldLabelledByMultipleElements entries from database")
    else:
        print(f"\n✗ Warning: {remaining} entries still remain in database")
else:
    print("No entries found in database - already clean")
