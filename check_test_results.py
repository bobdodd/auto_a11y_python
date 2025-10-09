#!/usr/bin/env python3
"""Check what error codes are in the test_results collection"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'auto_a11y')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Check test_results collection
print("=" * 70)
print("CHECKING TEST_RESULTS FOR OLD ERROR CODES")
print("=" * 70)

old_codes = ['WarnElementLangEmpty', 'WarnEmptyLangAttribute', 'ErrElementLangEmpty']

for code in old_codes:
    count = db.test_results.count_documents({'error_code': code})
    print(f"\n{code}: {count} documents")

    if count > 0:
        # Show sample
        sample = db.test_results.find_one({'error_code': code})
        print(f"  Sample: {sample.get('fixture_path', 'N/A')}")
        print(f"  Created: {sample.get('created_at', 'N/A')}")

print("\n" + "=" * 70)
print("CHECKING UNIQUE ERROR CODES IN test_results")
print("=" * 70)

# Get all unique error codes that contain "Lang"
pipeline = [
    {"$match": {"error_code": {"$regex": "Lang", "$options": "i"}}},
    {"$group": {"_id": "$error_code", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
]

results = list(db.test_results.aggregate(pipeline))
for result in results:
    print(f"{result['_id']}: {result['count']} documents")

client.close()
