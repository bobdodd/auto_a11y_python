#!/usr/bin/env python3
"""
Migration script: Convert old test results schema to new split schema

OLD SCHEMA:
- test_results collection contains violations/warnings/etc arrays
- Can hit 16MB MongoDB limit with large result sets

NEW SCHEMA:
- test_results: Summary (counts, metadata)
- test_result_items: Individual violations/warnings (separate docs)

USAGE:
    python scripts/migrate_test_results_to_items.py [--dry-run] [--batch-size 100]

OPTIONS:
    --dry-run: Show what would be migrated without making changes
    --batch-size: Number of test results to process at once (default: 100)
    --skip-errors: Continue on errors instead of stopping
"""

import sys
import argparse
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResultMigrator:
    """Migrates test results from old schema to new split schema"""

    def __init__(self, mongo_uri: str, db_name: str, dry_run: bool = False):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.test_results = self.db.test_results
        self.test_result_items = self.db.test_result_items
        self.dry_run = dry_run

        self.stats = {
            'total_found': 0,
            'already_migrated': 0,
            'migrated': 0,
            'failed': 0,
            'items_created': 0
        }

    def find_old_schema_results(self):
        """Find test results that use old schema (have violations array)"""
        query = {
            '_has_detailed_items': {'$ne': True},  # Not already migrated
            '$or': [
                {'violations': {'$exists': True, '$type': 'array'}},
                {'warnings': {'$exists': True, '$type': 'array'}},
                {'info': {'$exists': True, '$type': 'array'}},
                {'discovery': {'$exists': True, '$type': 'array'}},
                {'passes': {'$exists': True, '$type': 'array'}}
            ]
        }
        return self.test_results.find(query)

    def migrate_test_result(self, result_doc, skip_errors=False):
        """
        Migrate a single test result to new schema

        Args:
            result_doc: MongoDB document from test_results collection
            skip_errors: If True, log errors but continue

        Returns:
            Number of items created, or -1 if error
        """
        test_result_id = result_doc['_id']
        page_id = result_doc.get('page_id')
        test_date = result_doc.get('test_date', datetime.now())

        try:
            items = []

            # Extract violations
            for violation in result_doc.get('violations', []):
                items.append({
                    'test_result_id': test_result_id,
                    'page_id': page_id,
                    'test_date': test_date,
                    'item_type': 'violation',
                    'issue_id': violation.get('id'),
                    'impact': violation.get('impact'),
                    'touchpoint': violation.get('touchpoint', violation.get('category')),
                    'xpath': violation.get('xpath'),
                    'element': violation.get('element'),
                    'html': violation.get('html'),
                    'description': violation.get('description'),
                    'failure_summary': violation.get('failure_summary'),
                    'wcag_criteria': violation.get('wcag_criteria', []),
                    'help_url': violation.get('help_url'),
                    'metadata': violation.get('metadata', {})
                })

            # Extract warnings
            for warning in result_doc.get('warnings', []):
                items.append({
                    'test_result_id': test_result_id,
                    'page_id': page_id,
                    'test_date': test_date,
                    'item_type': 'warning',
                    'issue_id': warning.get('id'),
                    'impact': warning.get('impact'),
                    'touchpoint': warning.get('touchpoint', warning.get('category')),
                    'xpath': warning.get('xpath'),
                    'element': warning.get('element'),
                    'html': warning.get('html'),
                    'description': warning.get('description'),
                    'failure_summary': warning.get('failure_summary'),
                    'wcag_criteria': warning.get('wcag_criteria', []),
                    'help_url': warning.get('help_url'),
                    'metadata': warning.get('metadata', {})
                })

            # Extract info
            for info in result_doc.get('info', []):
                items.append({
                    'test_result_id': test_result_id,
                    'page_id': page_id,
                    'test_date': test_date,
                    'item_type': 'info',
                    'issue_id': info.get('id'),
                    'impact': info.get('impact'),
                    'touchpoint': info.get('touchpoint', info.get('category')),
                    'xpath': info.get('xpath'),
                    'element': info.get('element'),
                    'html': info.get('html'),
                    'description': info.get('description'),
                    'metadata': info.get('metadata', {})
                })

            # Extract discovery
            for discovery in result_doc.get('discovery', []):
                items.append({
                    'test_result_id': test_result_id,
                    'page_id': page_id,
                    'test_date': test_date,
                    'item_type': 'discovery',
                    'issue_id': discovery.get('id'),
                    'impact': discovery.get('impact'),
                    'touchpoint': discovery.get('touchpoint', discovery.get('category')),
                    'xpath': discovery.get('xpath'),
                    'element': discovery.get('element'),
                    'html': discovery.get('html'),
                    'description': discovery.get('description'),
                    'metadata': discovery.get('metadata', {})
                })

            # Extract passes
            for passed in result_doc.get('passes', []):
                items.append({
                    'test_result_id': test_result_id,
                    'page_id': page_id,
                    'test_date': test_date,
                    'item_type': 'pass',
                    'issue_id': passed.get('id'),
                    'touchpoint': passed.get('touchpoint', passed.get('category')),
                    'xpath': passed.get('xpath'),
                    'element': passed.get('element'),
                    'html': passed.get('html'),
                    'description': passed.get('description'),
                    'metadata': passed.get('metadata', {})
                })

            if not self.dry_run and items:
                # Insert items
                self.test_result_items.insert_many(items, ordered=False)

                # Update summary document
                self.test_results.update_one(
                    {'_id': test_result_id},
                    {
                        '$set': {
                            '_has_detailed_items': True,
                            '_items_collection': 'test_result_items',
                            '_migrated_at': datetime.now()
                        },
                        '$unset': {
                            'violations': '',
                            'warnings': '',
                            'info': '',
                            'discovery': '',
                            'passes': ''
                        }
                    }
                )

            return len(items)

        except Exception as e:
            logger.error(f"Error migrating test result {test_result_id}: {e}")
            if skip_errors:
                return -1
            else:
                raise

    def run_migration(self, batch_size=100, skip_errors=False):
        """
        Run the migration process

        Args:
            batch_size: Number of results to process before logging progress
            skip_errors: Continue on errors instead of stopping
        """
        logger.info("=" * 80)
        logger.info("TEST RESULT MIGRATION: Old Schema → New Split Schema")
        logger.info("=" * 80)
        logger.info(f"Database: {self.db.name}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        logger.info(f"Batch size: {batch_size}")
        logger.info("")

        # Find results to migrate
        logger.info("Scanning for test results with old schema...")
        old_results = list(self.find_old_schema_results())
        self.stats['total_found'] = len(old_results)

        logger.info(f"Found {self.stats['total_found']} test results to migrate")
        logger.info("")

        if self.stats['total_found'] == 0:
            logger.info("✓ No migration needed - all test results already use new schema")
            return self.stats

        if self.dry_run:
            logger.info("DRY RUN - No changes will be made")
            logger.info("")

        # Migrate each result
        processed = 0
        for result_doc in old_results:
            processed += 1

            try:
                items_count = self.migrate_test_result(result_doc, skip_errors=skip_errors)

                if items_count >= 0:
                    self.stats['migrated'] += 1
                    self.stats['items_created'] += items_count
                else:
                    self.stats['failed'] += 1

                # Log progress every batch_size results
                if processed % batch_size == 0:
                    logger.info(f"Progress: {processed}/{self.stats['total_found']} "
                              f"({int(processed/self.stats['total_found']*100)}%) - "
                              f"Migrated: {self.stats['migrated']}, "
                              f"Items created: {self.stats['items_created']}, "
                              f"Failed: {self.stats['failed']}")

            except Exception as e:
                logger.error(f"Fatal error at result {processed}: {e}")
                if not skip_errors:
                    raise

        # Final summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total found:        {self.stats['total_found']}")
        logger.info(f"Successfully migrated: {self.stats['migrated']}")
        logger.info(f"Failed:             {self.stats['failed']}")
        logger.info(f"Items created:      {self.stats['items_created']}")
        logger.info("")

        if not self.dry_run:
            logger.info("✓ Migration completed successfully!")
            logger.info("")
            logger.info("Old arrays have been removed from summary documents.")
            logger.info("All data is now in the test_result_items collection.")
        else:
            logger.info("✓ Dry run completed successfully!")
            logger.info("")
            logger.info("Run without --dry-run to perform actual migration.")

        return self.stats

    def close(self):
        """Close database connection"""
        self.client.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate test results from old schema to new split schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without making changes'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of test results to process before logging progress (default: 100)'
    )
    parser.add_argument(
        '--skip-errors',
        action='store_true',
        help='Continue on errors instead of stopping'
    )
    parser.add_argument(
        '--mongo-uri',
        default='mongodb://localhost:27017/',
        help='MongoDB connection URI (default: mongodb://localhost:27017/)'
    )
    parser.add_argument(
        '--database',
        default='auto_a11y',
        help='Database name (default: auto_a11y)'
    )

    args = parser.parse_args()

    # Create migrator
    migrator = TestResultMigrator(
        mongo_uri=args.mongo_uri,
        db_name=args.database,
        dry_run=args.dry_run
    )

    try:
        # Run migration
        stats = migrator.run_migration(
            batch_size=args.batch_size,
            skip_errors=args.skip_errors
        )

        # Exit code based on results
        if stats['failed'] > 0:
            logger.warning(f"{stats['failed']} test results failed to migrate")
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("\nMigration interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        migrator.close()


if __name__ == '__main__':
    main()
