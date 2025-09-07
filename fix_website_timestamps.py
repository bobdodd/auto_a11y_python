#!/usr/bin/env python3
"""
Utility script to fix website last_tested timestamps based on their pages
"""

from auto_a11y.core.database import Database
from auto_a11y.core.config import Config
from datetime import datetime

def fix_website_timestamps():
    """Update all website last_tested fields based on their pages"""
    
    # Initialize database
    config = Config()
    db = Database(config)
    
    # Get all websites
    websites = db.db.websites.find()
    
    updated_count = 0
    
    for website_doc in websites:
        website_id = str(website_doc['_id'])
        
        # Get all pages for this website
        pages = db.get_pages(website_id)
        
        # Find the most recent test date
        latest_test_date = None
        for page in pages:
            if page.last_tested:
                if latest_test_date is None or page.last_tested > latest_test_date:
                    latest_test_date = page.last_tested
        
        # Update website if we found a test date
        if latest_test_date:
            website = db.get_website(website_id)
            if website:
                website.last_tested = latest_test_date
                db.update_website(website)
                print(f"Updated website {website.display_name}: {latest_test_date}")
                updated_count += 1
        else:
            print(f"No tested pages found for website {website_doc.get('name', website_doc.get('url'))}")
    
    print(f"\nUpdated {updated_count} websites with last_tested timestamps")

if __name__ == "__main__":
    fix_website_timestamps()