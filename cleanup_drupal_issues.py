#!/usr/bin/env python3
"""
Cleanup script for drupal_issues collection.

This script removes the old unique index and clears old records that don't have unique_ids.
Run this before restarting Flask.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_a11y.core.database import Database


def main():
    # Get database connection
    db_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGODB_DATABASE', 'auto_a11y')

    print(f"Connecting to database: {db_name}")

    # Connect directly to MongoDB (bypass Database class to avoid index creation)
    from pymongo import MongoClient
    client = MongoClient(db_uri)
    db = client[db_name]
    drupal_issues = db.drupal_issues

    print("=" * 80)
    print("CLEANING UP DRUPAL_ISSUES COLLECTION")
    print("=" * 80)
    print()

    # Step 1: Check existing indexes
    print("Step 1: Checking existing indexes...")
    existing_indexes = list(drupal_issues.list_indexes())
    print(f"  Found {len(existing_indexes)} indexes:")
    for idx in existing_indexes:
        print(f"    - {idx['name']}: {idx.get('key', {})}")
    print()

    # Step 2: Drop old unique index if it exists
    print("Step 2: Dropping old indexes...")
    try:
        # Drop the old violation_id + project_id unique index
        drupal_issues.drop_index("violation_id_1_project_id_1")
        print("  ✓ Dropped old index: violation_id_1_project_id_1")
    except Exception as e:
        print(f"  - Old index not found (already dropped or never existed): {e}")
    print()

    # Step 3: Count records without unique_id
    print("Step 3: Checking for records without unique_id...")
    count_without_unique_id = drupal_issues.count_documents({'unique_id': None})
    count_total = drupal_issues.count_documents({})
    print(f"  Total records: {count_total}")
    print(f"  Records without unique_id: {count_without_unique_id}")
    print()

    # Step 4: Delete old records without unique_id
    if count_without_unique_id > 0:
        print(f"Step 4: Deleting {count_without_unique_id} old records without unique_id...")
        result = drupal_issues.delete_many({'unique_id': None})
        print(f"  ✓ Deleted {result.deleted_count} records")
    else:
        print("Step 4: No records need deletion")
    print()

    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print()
    print("You can now restart Flask. The new unique index will be created on startup.")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
