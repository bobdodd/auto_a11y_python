#!/usr/bin/env python3
"""Check what error codes are in the fixture_tests collection"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'auto_a11y')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print("=" * 70)
print("CHECKING fixture_tests FOR OLD ERROR CODES")
print("=" * 70)

old_codes = ['WarnElementLangEmpty', 'WarnEmptyLangAttribute', 'ErrElementLangEmpty']

for code in old_codes:
    count = db.fixture_tests.count_documents({'expected_code': code})
    print(f"\n{code}: {count} documents")

    if count > 0:
        # Show samples
        samples = list(db.fixture_tests.find({'expected_code': code}).limit(3))
        for sample in samples:
            print(f"  - {sample.get('fixture_path', 'N/A')}")
            print(f"    Tested: {sample.get('tested_at', 'N/A')}")

print("\n" + "=" * 70)
print("ALL LANGUAGE-RELATED FIXTURE TESTS")
print("=" * 70)

# Get all unique error codes that contain "Lang"
pipeline = [
    {"$match": {"expected_code": {"$regex": "Lang", "$options": "i"}}},
    {"$group": {"_id": "$expected_code", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]

results = list(db.fixture_tests.aggregate(pipeline))
for result in results:
    print(f"{result['_id']}: {result['count']} fixture tests")

client.close()
