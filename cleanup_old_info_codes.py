#!/usr/bin/env python3
"""
Clean up old Info codes from the database that have been converted to Warn codes:
- InfoNoColorSchemeSupport -> WarnNoColorSchemeSupport
- InfoNoContrastSupport -> WarnNoContrastSupport
"""

from auto_a11y.core.database import Database
from config import Config

def main():
    config = Config()
    db = Database(config.MONGODB_URI, config.DATABASE_NAME)

    old_codes = [
        'InfoNoColorSchemeSupport',
        'InfoNoContrastSupport'
    ]

    print("Cleaning up old Info codes from database...")
    print(f"Looking for: {', '.join(old_codes)}")
    print()

    # Clean fixture_test_runs collection
    if 'fixture_test_runs' in db.db.list_collection_names():
        for old_code in old_codes:
            result = db.db.fixture_test_runs.delete_many({'error_code': old_code})
            if result.deleted_count > 0:
                print(f"✓ Deleted {result.deleted_count} fixture_test_runs entries for {old_code}")

    # Clean any test_results that might have these codes
    if 'test_results' in db.db.list_collection_names():
        for old_code in old_codes:
            # Check violations array
            result = db.db.test_results.update_many(
                {'violations.id': {'$regex': f'.*{old_code}.*'}},
                {'$pull': {'violations': {'id': {'$regex': f'.*{old_code}.*'}}}}
            )
            if result.modified_count > 0:
                print(f"✓ Removed {old_code} from {result.modified_count} test_results violations")

            # Check warnings array
            result = db.db.test_results.update_many(
                {'warnings.id': {'$regex': f'.*{old_code}.*'}},
                {'$pull': {'warnings': {'id': {'$regex': f'.*{old_code}.*'}}}}
            )
            if result.modified_count > 0:
                print(f"✓ Removed {old_code} from {result.modified_count} test_results warnings")

            # Check info array
            result = db.db.test_results.update_many(
                {'info.id': {'$regex': f'.*{old_code}.*'}},
                {'$pull': {'info': {'id': {'$regex': f'.*{old_code}.*'}}}}
            )
            if result.modified_count > 0:
                print(f"✓ Removed {old_code} from {result.modified_count} test_results info")

    print()
    print("Database cleanup complete!")
    print("Note: You may need to restart the Flask server for changes to take effect.")

if __name__ == '__main__':
    main()
