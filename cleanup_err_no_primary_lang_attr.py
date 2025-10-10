#!/usr/bin/env python3
"""
Cleanup script to remove ErrNoPrimaryLangAttr entries from database.
This error code is a duplicate of ErrNoPageLanguage.
"""

import sys
import os
from pymongo import MongoClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config

def cleanup_err_no_primary_lang_attr():
    """Remove all ErrNoPrimaryLangAttr entries from database"""

    config = Config()
    client = MongoClient(config.MONGODB_URI)
    db = client[config.DATABASE_NAME]

    # Collections to clean
    collections_to_clean = ['fixture_tests', 'test_results']

    total_deleted = 0

    for collection_name in collections_to_clean:
        collection = db[collection_name]

        # Find documents with ErrNoPrimaryLangAttr
        result = collection.delete_many({
            '$or': [
                {'issue_id': 'ErrNoPrimaryLangAttr'},
                {'err': 'ErrNoPrimaryLangAttr'},
                {'errors.err': 'ErrNoPrimaryLangAttr'}
            ]
        })

        deleted = result.deleted_count
        total_deleted += deleted

        print(f"Deleted {deleted} documents from {collection_name} collection")

    print(f"\nTotal documents deleted: {total_deleted}")

    client.close()

if __name__ == '__main__':
    print("Cleaning up ErrNoPrimaryLangAttr (duplicate of ErrNoPageLanguage)...")
    cleanup_err_no_primary_lang_attr()
    print("Cleanup complete!")
