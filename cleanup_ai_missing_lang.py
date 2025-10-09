#!/usr/bin/env python3
"""
Remove AI_ErrMissingLangAttribute from database.
We already have ErrNoPageLanguage for this check.
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'auto_a11y')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("=" * 70)
print("REMOVING AI_ErrMissingLangAttribute")
print("=" * 70)
print("Reason: Duplicate of ErrNoPageLanguage (non-AI version exists)\n")

code = 'AI_ErrMissingLangAttribute'

# Check fixture_tests
count = db.fixture_tests.count_documents({'expected_code': code})
if count > 0:
    print(f"❌ Deleting {count} fixture tests for '{code}'")
    result = db.fixture_tests.delete_many({'expected_code': code})
    print(f"   Deleted {result.deleted_count} documents")
else:
    print(f"✓ No fixture_tests found for '{code}'")

# Check test_results
count = db.test_results.count_documents({'error_code': code})
if count > 0:
    print(f"\n❌ Deleting {count} test results for '{code}'")
    result = db.test_results.delete_many({'error_code': code})
    print(f"   Deleted {result.deleted_count} documents")
else:
    print(f"✓ No test_results found for '{code}'")

print("\n" + "=" * 70)
print("✅ CLEANUP COMPLETE!")
print("=" * 70)
print("Use ErrNoPageLanguage for missing lang attribute detection")

client.close()
