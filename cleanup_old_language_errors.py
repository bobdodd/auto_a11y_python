#!/usr/bin/env python3
"""
Clean up old language error codes from the database.

This script removes or updates records with deprecated error codes:
- WarnElementLangEmpty -> ErrEmptyLanguageAttribute
- WarnEmptyLangAttribute -> (delete - deprecated)
- ErrElementLangEmpty -> ErrEmptyLanguageAttribute
"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('MONGODB_DATABASE', 'auto_a11y')

print(f"Connecting to MongoDB: {MONGO_URI}")
print(f"Database: {DB_NAME}\n")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections that might contain error codes
collections_to_check = ['test_results', 'pages', 'websites', 'projects']

# Old error codes to clean up
old_codes = {
    'WarnElementLangEmpty': 'ErrEmptyLanguageAttribute',
    'WarnEmptyLangAttribute': None,  # Delete this one
    'ErrElementLangEmpty': 'ErrEmptyLanguageAttribute'
}

print("=" * 60)
print("DATABASE CLEANUP: Old Language Error Codes")
print("=" * 60)

for collection_name in collections_to_check:
    collection = db[collection_name]
    print(f"\n📁 Checking collection: {collection_name}")

    for old_code, new_code in old_codes.items():
        # Check in errors array
        query = {'errors.err': old_code}
        count = collection.count_documents(query)

        if count > 0:
            print(f"  Found {count} documents with '{old_code}' in errors array")

            if new_code:
                # Update to new code
                result = collection.update_many(
                    query,
                    {'$set': {'errors.$[elem].err': new_code}},
                    array_filters=[{'elem.err': old_code}]
                )
                print(f"    ✅ Updated {result.modified_count} documents to '{new_code}'")
            else:
                # Remove the error entries
                result = collection.update_many(
                    query,
                    {'$pull': {'errors': {'err': old_code}}}
                )
                print(f"    🗑️  Removed from {result.modified_count} documents")

        # Check in error_summary
        query_summary = {f'error_summary.{old_code}': {'$exists': True}}
        count_summary = collection.count_documents(query_summary)

        if count_summary > 0:
            print(f"  Found {count_summary} documents with '{old_code}' in error_summary")

            if new_code:
                # Rename the field
                result = collection.update_many(
                    query_summary,
                    {'$rename': {f'error_summary.{old_code}': f'error_summary.{new_code}'}}
                )
                print(f"    ✅ Renamed field in {result.modified_count} documents")
            else:
                # Remove the field
                result = collection.update_many(
                    query_summary,
                    {'$unset': {f'error_summary.{old_code}': ''}}
                )
                print(f"    🗑️  Removed field from {result.modified_count} documents")

print("\n" + "=" * 60)
print("✅ Database cleanup complete!")
print("=" * 60)
print("\nOld codes cleaned up:")
print("  - WarnElementLangEmpty → ErrEmptyLanguageAttribute")
print("  - WarnEmptyLangAttribute → (deleted)")
print("  - ErrElementLangEmpty → ErrEmptyLanguageAttribute")
print("\nCorrect codes now in use:")
print("  - ErrHtmlLangEmpty (for <html> element)")
print("  - ErrEmptyLanguageAttribute (for other elements)")
print("=" * 60)

client.close()
