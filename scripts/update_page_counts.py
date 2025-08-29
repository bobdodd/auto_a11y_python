#!/usr/bin/env python3
"""
Script to update existing pages with info_count and discovery_count from their latest test results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from datetime import datetime

def update_page_counts():
    """Update pages with info_count and discovery_count from test results"""
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client.auto_a11y
    
    print("Updating page counts...")
    
    # Get all pages
    pages = db.pages.find({})
    total_pages = 0
    updated_pages = 0
    
    for page in pages:
        total_pages += 1
        
        # Find the latest test result for this page
        latest_result = db.test_results.find_one(
            {'page_id': str(page['_id'])},
            sort=[('test_date', -1)]
        )
        
        if latest_result:
            # Count info and discovery items
            info_count = len(latest_result.get('info', []))
            discovery_count = len(latest_result.get('discovery', []))
            
            # Update the page document
            db.pages.update_one(
                {'_id': page['_id']},
                {'$set': {
                    'info_count': info_count,
                    'discovery_count': discovery_count
                }}
            )
            updated_pages += 1
            print(f"  Updated page {page.get('url', 'unknown')}: {info_count} info, {discovery_count} discovery")
        else:
            # Set to 0 if no test results
            db.pages.update_one(
                {'_id': page['_id']},
                {'$set': {
                    'info_count': 0,
                    'discovery_count': 0
                }}
            )
            updated_pages += 1
    
    print(f"\n✅ Completed!")
    print(f"Total pages: {total_pages}")
    print(f"Updated pages: {updated_pages}")

if __name__ == "__main__":
    try:
        update_page_counts()
    except Exception as e:
        print(f"❌ Update failed: {e}")
        sys.exit(1)