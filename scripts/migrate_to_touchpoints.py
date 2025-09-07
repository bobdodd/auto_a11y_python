#!/usr/bin/env python
"""
Migration script to update existing database records from categories to touchpoints.

This script:
1. Updates all test_results to add touchpoint field to violations and AI findings
2. Preserves existing category field for backward compatibility
3. Maps old categories to new touchpoints
"""

import sys
import os
from pathlib import Path
from pymongo import MongoClient
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from auto_a11y.core.touchpoints import TouchpointMapper, TouchpointID

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TouchpointMigration:
    """Handles migration of categories to touchpoints in MongoDB"""
    
    def __init__(self, mongo_uri: str, database_name: str):
        """
        Initialize migration
        
        Args:
            mongo_uri: MongoDB connection string
            database_name: Name of database
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database_name]
        self.test_results = self.db.test_results
        self.backup_coll = self.db.test_results_backup_pre_touchpoints
        
    def backup_collection(self):
        """Create backup of test_results collection before migration"""
        logger.info("Creating backup of test_results collection...")
        
        # Check if backup already exists
        if 'test_results_backup_pre_touchpoints' in self.db.list_collection_names():
            response = input("Backup collection already exists. Overwrite? (y/n): ")
            if response.lower() != 'y':
                logger.info("Using existing backup")
                return
            else:
                self.db.test_results_backup_pre_touchpoints.drop()
        
        # Create backup
        pipeline = [{"$match": {}}, {"$out": "test_results_backup_pre_touchpoints"}]
        self.test_results.aggregate(pipeline)
        
        backup_count = self.db.test_results_backup_pre_touchpoints.count_documents({})
        logger.info(f"Backed up {backup_count} documents")
    
    def migrate_violation(self, violation: dict) -> dict:
        """
        Add touchpoint to a violation
        
        Args:
            violation: Violation dictionary
            
        Returns:
            Updated violation dictionary
        """
        # Skip if already has touchpoint
        if 'touchpoint' in violation and violation['touchpoint']:
            return violation
        
        # Try to map by error code
        error_id = violation.get('id', '')
        if '_' in error_id:
            # Extract error code from ID (format: testname_ErrorCode)
            error_code = error_id.split('_', 1)[1]
            touchpoint_id = TouchpointMapper.get_touchpoint_for_error_code(error_code)
            
            if touchpoint_id:
                violation['touchpoint'] = touchpoint_id.value
                return violation
        
        # Fall back to category mapping
        category = violation.get('category', '')
        if category:
            touchpoint_id = TouchpointMapper.get_touchpoint_for_category(category)
            violation['touchpoint'] = touchpoint_id.value
        else:
            # Default touchpoint
            violation['touchpoint'] = TouchpointID.ACCESSIBLE_NAMES.value
        
        return violation
    
    def migrate_ai_finding(self, finding: dict) -> dict:
        """
        Add touchpoint to an AI finding
        
        Args:
            finding: AI finding dictionary
            
        Returns:
            Updated AI finding dictionary
        """
        # Skip if already has touchpoint
        if 'touchpoint' in finding and finding['touchpoint']:
            return finding
        
        # Map by AI type
        ai_type = finding.get('type', '')
        touchpoint_id = TouchpointMapper.get_touchpoint_for_ai_type(ai_type)
        finding['touchpoint'] = touchpoint_id.value
        
        return finding
    
    def migrate_test_result(self, test_result: dict) -> dict:
        """
        Migrate a single test result document
        
        Args:
            test_result: Test result document
            
        Returns:
            Updated test result document
        """
        updated = False
        
        # Migrate violations
        if 'violations' in test_result:
            for violation in test_result['violations']:
                original_touchpoint = violation.get('touchpoint')
                self.migrate_violation(violation)
                if violation.get('touchpoint') != original_touchpoint:
                    updated = True
        
        # Migrate warnings
        if 'warnings' in test_result:
            for warning in test_result['warnings']:
                original_touchpoint = warning.get('touchpoint')
                self.migrate_violation(warning)
                if warning.get('touchpoint') != original_touchpoint:
                    updated = True
        
        # Migrate info items
        if 'info' in test_result:
            for info in test_result['info']:
                original_touchpoint = info.get('touchpoint')
                self.migrate_violation(info)
                if info.get('touchpoint') != original_touchpoint:
                    updated = True
        
        # Migrate discovery items
        if 'discovery' in test_result:
            for discovery in test_result['discovery']:
                original_touchpoint = discovery.get('touchpoint')
                self.migrate_violation(discovery)
                if discovery.get('touchpoint') != original_touchpoint:
                    updated = True
        
        # Migrate AI findings
        if 'ai_findings' in test_result:
            for finding in test_result['ai_findings']:
                original_touchpoint = finding.get('touchpoint')
                self.migrate_ai_finding(finding)
                if finding.get('touchpoint') != original_touchpoint:
                    updated = True
        
        # Add migration metadata
        if updated:
            if 'metadata' not in test_result:
                test_result['metadata'] = {}
            test_result['metadata']['touchpoint_migration_date'] = datetime.now()
            test_result['metadata']['touchpoint_migration_version'] = '1.0'
        
        return test_result, updated
    
    def run_migration(self):
        """Run the migration on all test results"""
        logger.info("Starting touchpoint migration...")
        
        # Get total count
        total_count = self.test_results.count_documents({})
        logger.info(f"Found {total_count} test results to process")
        
        if total_count == 0:
            logger.info("No test results to migrate")
            return
        
        # Create backup first
        self.backup_collection()
        
        # Process each document
        updated_count = 0
        error_count = 0
        
        for i, test_result in enumerate(self.test_results.find({}), 1):
            try:
                # Migrate the document
                migrated_result, was_updated = self.migrate_test_result(test_result)
                
                if was_updated:
                    # Update in database
                    self.test_results.replace_one(
                        {'_id': test_result['_id']},
                        migrated_result
                    )
                    updated_count += 1
                
                # Progress indicator
                if i % 100 == 0:
                    logger.info(f"Processed {i}/{total_count} documents...")
                    
            except Exception as e:
                logger.error(f"Error migrating document {test_result.get('_id')}: {e}")
                error_count += 1
        
        # Final report
        logger.info("=" * 50)
        logger.info("Migration Complete!")
        logger.info(f"Total documents processed: {total_count}")
        logger.info(f"Documents updated: {updated_count}")
        logger.info(f"Documents with errors: {error_count}")
        logger.info(f"Documents unchanged: {total_count - updated_count - error_count}")
        
        if error_count > 0:
            logger.warning("Some documents had errors. Check logs for details.")
    
    def rollback(self):
        """Rollback migration by restoring from backup"""
        logger.info("Rolling back migration...")
        
        if 'test_results_backup_pre_touchpoints' not in self.db.list_collection_names():
            logger.error("No backup collection found. Cannot rollback.")
            return False
        
        # Drop current collection
        self.test_results.drop()
        
        # Restore from backup
        pipeline = [{"$match": {}}, {"$out": "test_results"}]
        self.backup_coll.aggregate(pipeline)
        
        logger.info("Rollback complete. Original data restored.")
        return True
    
    def verify_migration(self):
        """Verify that migration was successful"""
        logger.info("Verifying migration...")
        
        # Count documents with touchpoints
        with_touchpoints = 0
        without_touchpoints = 0
        
        for test_result in self.test_results.find({}):
            has_touchpoint = False
            
            # Check violations
            for violation_type in ['violations', 'warnings', 'info', 'discovery']:
                if violation_type in test_result:
                    for violation in test_result[violation_type]:
                        if 'touchpoint' in violation and violation['touchpoint']:
                            has_touchpoint = True
                            break
            
            # Check AI findings
            if 'ai_findings' in test_result:
                for finding in test_result['ai_findings']:
                    if 'touchpoint' in finding and finding['touchpoint']:
                        has_touchpoint = True
                        break
            
            if has_touchpoint:
                with_touchpoints += 1
            else:
                without_touchpoints += 1
        
        logger.info(f"Documents with touchpoints: {with_touchpoints}")
        logger.info(f"Documents without touchpoints: {without_touchpoints}")
        
        return without_touchpoints == 0


def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate categories to touchpoints')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration')
    parser.add_argument('--verify', action='store_true', help='Verify migration')
    parser.add_argument('--dry-run', action='store_true', help='Test migration without making changes')
    
    args = parser.parse_args()
    
    # Initialize migration
    migration = TouchpointMigration(config.MONGODB_URI, config.DATABASE_NAME)
    
    if args.rollback:
        success = migration.rollback()
        sys.exit(0 if success else 1)
    
    if args.verify:
        success = migration.verify_migration()
        sys.exit(0 if success else 1)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        # Test on first 10 documents
        count = 0
        for test_result in migration.test_results.find({}).limit(10):
            migrated_result, was_updated = migration.migrate_test_result(test_result.copy())
            if was_updated:
                count += 1
                logger.info(f"Would update document {test_result['_id']}")
        logger.info(f"Dry run complete. Would update {count}/10 documents")
    else:
        # Run actual migration
        migration.run_migration()
        
        # Verify after migration
        logger.info("")
        migration.verify_migration()


if __name__ == '__main__':
    main()