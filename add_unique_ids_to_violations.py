#!/usr/bin/env python3
"""
Migration script to add unique_id fields to all existing violation records.

This script:
1. Finds all test_results documents in MongoDB
2. For each violation/warning/info/discovery item, adds a unique_id field with a UUID
3. Updates the document in place
4. Provides progress reporting and statistics

Usage:
    python add_unique_ids_to_violations.py [--dry-run]
"""

import os
import sys
import uuid
from datetime import datetime
from bson import ObjectId

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_a11y.core.database import Database


def add_unique_ids_to_violations(db: Database, dry_run: bool = False):
    """
    Add unique_id fields to all violations in test_results collection.

    Args:
        db: Database instance
        dry_run: If True, only count what would be updated without making changes
    """
    print("=" * 80)
    print("ADDING UNIQUE IDs TO VIOLATION RECORDS")
    print("=" * 80)
    print()

    if dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()

    # Statistics
    stats = {
        'test_results_total': 0,
        'test_results_updated': 0,
        'violations_updated': 0,
        'warnings_updated': 0,
        'info_updated': 0,
        'discovery_updated': 0,
        'violations_already_had_ids': 0
    }

    # Get all test results
    print("Step 1: Fetching all test results...")
    all_test_results = list(db.test_results.find({}))
    stats['test_results_total'] = len(all_test_results)
    print(f"  Found {stats['test_results_total']} test results")
    print()

    # Process each test result
    print("Step 2: Processing violations...")
    for i, test_result in enumerate(all_test_results, 1):
        result_id = test_result.get('_id')
        page_id = test_result.get('page_id')

        if i % 10 == 0:
            print(f"  Processing {i}/{stats['test_results_total']}...")

        # Track if this document needs updating
        needs_update = False

        # Process violations array
        violations = test_result.get('violations', [])
        for violation in violations:
            if 'unique_id' not in violation or not violation.get('unique_id'):
                violation['unique_id'] = str(uuid.uuid4())
                stats['violations_updated'] += 1
                needs_update = True
            else:
                stats['violations_already_had_ids'] += 1

        # Process warnings array
        warnings = test_result.get('warnings', [])
        for warning in warnings:
            if 'unique_id' not in warning or not warning.get('unique_id'):
                warning['unique_id'] = str(uuid.uuid4())
                stats['warnings_updated'] += 1
                needs_update = True
            else:
                stats['violations_already_had_ids'] += 1

        # Process info array
        info = test_result.get('info', [])
        for info_item in info:
            if 'unique_id' not in info_item or not info_item.get('unique_id'):
                info_item['unique_id'] = str(uuid.uuid4())
                stats['info_updated'] += 1
                needs_update = True
            else:
                stats['violations_already_had_ids'] += 1

        # Process discovery array
        discovery = test_result.get('discovery', [])
        for disco_item in discovery:
            if 'unique_id' not in disco_item or not disco_item.get('unique_id'):
                disco_item['unique_id'] = str(uuid.uuid4())
                stats['discovery_updated'] += 1
                needs_update = True
            else:
                stats['violations_already_had_ids'] += 1

        # Update document if needed
        if needs_update:
            stats['test_results_updated'] += 1

            if not dry_run:
                # Update the document with new unique_ids
                db.test_results.update_one(
                    {'_id': result_id},
                    {
                        '$set': {
                            'violations': violations,
                            'warnings': warnings,
                            'info': info,
                            'discovery': discovery
                        }
                    }
                )

    print()
    print("=" * 80)
    print("MIGRATION COMPLETE")
    print("=" * 80)
    print()
    print("Statistics:")
    print(f"  Test Results Total:          {stats['test_results_total']}")
    print(f"  Test Results Updated:        {stats['test_results_updated']}")
    print(f"  Violations Given IDs:        {stats['violations_updated']}")
    print(f"  Warnings Given IDs:          {stats['warnings_updated']}")
    print(f"  Info Given IDs:              {stats['info_updated']}")
    print(f"  Discovery Given IDs:         {stats['discovery_updated']}")
    print(f"  Total Issues Given IDs:      {stats['violations_updated'] + stats['warnings_updated'] + stats['info_updated'] + stats['discovery_updated']}")
    print(f"  Items Already Had IDs:       {stats['violations_already_had_ids']}")
    print()

    if dry_run:
        print("DRY RUN - No changes were made to the database")
        print("Run without --dry-run to apply changes")
    else:
        print("Database has been updated successfully!")
    print()


def main():
    """Main entry point"""
    # Check for dry run flag
    dry_run = '--dry-run' in sys.argv

    # Get database connection
    db_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGODB_DATABASE', 'auto_a11y')

    print(f"Connecting to database: {db_name}")
    print(f"MongoDB URI: {db_uri}")
    print()

    db = Database(db_uri, db_name)

    # Run migration
    try:
        add_unique_ids_to_violations(db, dry_run=dry_run)
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
