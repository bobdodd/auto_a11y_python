#!/usr/bin/env python
"""
Simple migration script to rename 'category' field to 'touchpoint' in MongoDB
and map old category values to new touchpoint values.
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
from auto_a11y.core.touchpoints import TouchpointMapper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def rename_category_to_touchpoint():
    """Rename category field to touchpoint and map values"""
    
    # Connect to MongoDB
    client = MongoClient(config.MONGODB_URI)
    db = client[config.DATABASE_NAME]
    test_results = db.test_results
    
    logger.info("Starting category → touchpoint renaming...")
    
    # Count documents
    total_count = test_results.count_documents({})
    logger.info(f"Found {total_count} test results to process")
    
    if total_count == 0:
        logger.info("No test results to migrate")
        return
    
    # Process each document
    updated_count = 0
    
    for i, doc in enumerate(test_results.find({}), 1):
        updates_needed = False
        
        # Process violations
        for field in ['violations', 'warnings', 'info', 'discovery']:
            if field in doc and doc[field]:
                for item in doc[field]:
                    # Check if we need to rename category to touchpoint
                    if 'category' in item and 'touchpoint' not in item:
                        old_category = item['category']
                        
                        # Map to new touchpoint
                        touchpoint_id = TouchpointMapper.get_touchpoint_for_category(old_category)
                        new_touchpoint = touchpoint_id.value if touchpoint_id else old_category
                        
                        # Rename field
                        item['touchpoint'] = new_touchpoint
                        del item['category']
                        updates_needed = True
                    
                    # If touchpoint already exists but still has category, just remove category
                    elif 'touchpoint' in item and 'category' in item:
                        del item['category']
                        updates_needed = True
        
        # Update document if needed
        if updates_needed:
            test_results.replace_one({'_id': doc['_id']}, doc)
            updated_count += 1
        
        # Progress indicator
        if i % 10 == 0:
            logger.info(f"Processed {i}/{total_count} documents...")
    
    logger.info("=" * 50)
    logger.info("Renaming Complete!")
    logger.info(f"Total documents processed: {total_count}")
    logger.info(f"Documents updated: {updated_count}")
    logger.info(f"Documents unchanged: {total_count - updated_count}")


def verify_renaming():
    """Verify that renaming was successful"""
    
    client = MongoClient(config.MONGODB_URI)
    db = client[config.DATABASE_NAME]
    test_results = db.test_results
    
    logger.info("Verifying renaming...")
    
    # Check for any remaining 'category' fields
    docs_with_category = 0
    docs_with_touchpoint = 0
    
    for doc in test_results.find({}):
        has_category = False
        has_touchpoint = False
        
        for field in ['violations', 'warnings', 'info', 'discovery']:
            if field in doc:
                for item in doc[field]:
                    if 'category' in item:
                        has_category = True
                    if 'touchpoint' in item:
                        has_touchpoint = True
        
        if has_category:
            docs_with_category += 1
        if has_touchpoint:
            docs_with_touchpoint += 1
    
    logger.info(f"Documents with 'category' field: {docs_with_category}")
    logger.info(f"Documents with 'touchpoint' field: {docs_with_touchpoint}")
    
    if docs_with_category == 0:
        logger.info("✅ All 'category' fields have been renamed to 'touchpoint'")
        return True
    else:
        logger.warning(f"⚠️ {docs_with_category} documents still have 'category' field")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rename category to touchpoint')
    parser.add_argument('--verify', action='store_true', help='Verify renaming')
    
    args = parser.parse_args()
    
    if args.verify:
        success = verify_renaming()
        sys.exit(0 if success else 1)
    else:
        # Run the renaming
        rename_category_to_touchpoint()
        
        # Verify after renaming
        logger.info("")
        verify_renaming()


if __name__ == '__main__':
    main()