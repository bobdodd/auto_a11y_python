#!/usr/bin/env python3
"""
Script to migrate existing test results to properly categorize issues
into violations (Err), warnings (Warn), info (Info), and discovery (Disco)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_a11y.core import Database
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_test_results(db: Database):
    """Migrate test results to new format with proper categorization"""
    
    # Get all test results
    test_results = list(db.test_results.find({}))
    logger.info(f"Found {len(test_results)} test results to migrate")
    
    migrated_count = 0
    already_migrated = 0
    
    for result in test_results:
        # Check if already migrated (has info and discovery fields)
        if 'info' in result and 'discovery' in result:
            already_migrated += 1
            continue
        
        # Initialize new arrays
        new_violations = []  # For _Err
        new_warnings = []    # For _Warn
        new_info = []        # For _Info
        new_discovery = []   # For _Disco
        
        # Process existing violations array
        for item in result.get('violations', []):
            item_id = item.get('id', '')
            
            # Categorize based on ID pattern
            if '_Err' in item_id:
                new_violations.append(item)
            elif '_Warn' in item_id:
                new_warnings.append(item)
            elif '_Info' in item_id:
                new_info.append(item)
            elif '_Disco' in item_id:
                new_discovery.append(item)
            else:
                # Default to violations if pattern not recognized
                new_violations.append(item)
        
        # Keep existing warnings array items in warnings
        for item in result.get('warnings', []):
            new_warnings.append(item)
        
        # Update the document
        update_data = {
            '$set': {
                'violations': new_violations,
                'warnings': new_warnings,
                'info': new_info,
                'discovery': new_discovery,
                'migrated_at': datetime.now()
            }
        }
        
        db.test_results.update_one({'_id': result['_id']}, update_data)
        migrated_count += 1
        
        if migrated_count % 10 == 0:
            logger.info(f"Migrated {migrated_count} test results...")
    
    logger.info(f"Migration complete!")
    logger.info(f"  - Migrated: {migrated_count}")
    logger.info(f"  - Already migrated: {already_migrated}")
    logger.info(f"  - Total: {len(test_results)}")
    
    # Show sample counts from latest migrated result
    if migrated_count > 0:
        sample = db.test_results.find_one({'migrated_at': {'$exists': True}}, sort=[('migrated_at', -1)])
        if sample:
            logger.info(f"\nSample migrated result counts:")
            logger.info(f"  - Violations (Errors): {len(sample.get('violations', []))}")
            logger.info(f"  - Warnings: {len(sample.get('warnings', []))}")
            logger.info(f"  - Info Notes: {len(sample.get('info', []))}")
            logger.info(f"  - Discovery: {len(sample.get('discovery', []))}")


def main():
    """Main function"""
    # Connect to database
    db = Database('mongodb://localhost:27017/', 'auto_a11y')
    
    # Confirm before proceeding
    response = input("This will migrate all test results to the new format. Continue? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Migration cancelled")
        return
    
    # Run migration
    migrate_test_results(db)
    
    logger.info("Migration completed successfully!")


if __name__ == '__main__':
    main()