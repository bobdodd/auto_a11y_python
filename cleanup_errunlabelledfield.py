#!/usr/bin/env python3
"""
Cleanup script to remove all ErrUnlabelledField entries from the database.
This error code has been merged into ErrNoLabel.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auto_a11y.core.database import Database
from config import Config

def cleanup_errunlabelledfield():
    """Remove all ErrUnlabelledField fixture test results from database."""

    print("=" * 80)
    print("CLEANING UP ErrUnlabelledField FROM DATABASE")
    print("=" * 80)
    print()

    # Initialize database connection
    config = Config()
    db = Database(config.MONGODB_URI, config.DATABASE_NAME)

    # Find all fixture test results with ErrUnlabelledField
    print("Searching for ErrUnlabelledField fixture test results...")

    # Query for fixture tests with this error code in the fixture_id
    query = {
        "fixture_id": {"$regex": "ErrUnlabelledField", "$options": "i"}
    }

    fixture_tests_collection = db.db['fixture_tests']
    results = list(fixture_tests_collection.find(query))

    if results:
        print(f"Found {len(results)} fixture test results with ErrUnlabelledField")
        print()

        for result in results:
            fixture_id = result.get('fixture_id', 'unknown')
            test_run_id = result.get('test_run_id', 'unknown')
            print(f"  - Fixture: {fixture_id}, Test Run: {test_run_id}")

        print()
        response = input(f"Delete all {len(results)} ErrUnlabelledField fixture test results? (yes/no): ")

        if response.lower() == 'yes':
            delete_result = fixture_tests_collection.delete_many(query)
            print(f"✅ Deleted {delete_result.deleted_count} fixture test results")
        else:
            print("❌ Cleanup cancelled")
    else:
        print("✅ No ErrUnlabelledField fixture test results found in database")

    print()

    # Also check for test results that might have this error code
    print("Searching for test results with ErrUnlabelledField errors...")

    test_results_collection = db.db['test_results']
    error_query = {
        "errors.err": "ErrUnlabelledField"
    }

    error_results = list(test_results_collection.find(error_query))

    if error_results:
        print(f"Found {len(error_results)} test results containing ErrUnlabelledField errors")
        print()

        for result in error_results:
            page_id = result.get('page_id', 'unknown')
            error_count = sum(1 for err in result.get('errors', []) if err.get('err') == 'ErrUnlabelledField')
            print(f"  - Page ID: {page_id}, ErrUnlabelledField count: {error_count}")

        print()
        print("⚠️  Note: These are actual test results (not fixtures).")
        print("You may want to re-run tests to generate updated results with ErrNoLabel instead.")
    else:
        print("✅ No test results with ErrUnlabelledField errors found")

    print()
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        cleanup_errunlabelledfield()
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
