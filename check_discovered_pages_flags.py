#!/usr/bin/env python3
"""Check discovered pages include_in_report flags for Credit Valley project"""

from pymongo import MongoClient
import os

# Get MongoDB URI from environment or use default
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'auto_a11y')

# Credit Valley project ID
PROJECT_ID = '6900fcff4298b1efb3e50738'

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Find discovered pages for this project
discovered_pages = list(db.discovered_pages.find({'project_id': PROJECT_ID}))

print(f"Found {len(discovered_pages)} discovered pages for Credit Valley project\n")

if discovered_pages:
    # Check flags
    total_include_in_report_true = 0
    total_include_in_report_false = 0
    total_include_in_report_missing = 0

    for page in discovered_pages:
        title = page.get('title', 'Unknown')
        include_in_report = page.get('include_in_report')

        if include_in_report is None:
            total_include_in_report_missing += 1
            flag_status = "MISSING"
        elif include_in_report is True:
            total_include_in_report_true += 1
            flag_status = "TRUE"
        else:
            total_include_in_report_false += 1
            flag_status = "FALSE"

        print(f"Page: {title}")
        print(f"  include_in_report: {flag_status}")
        print()

    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"  include_in_report = True:    {total_include_in_report_true}")
    print(f"  include_in_report = False:   {total_include_in_report_false}")
    print(f"  include_in_report = Missing: {total_include_in_report_missing}")
    print("="*60)

    if total_include_in_report_false > 0 or total_include_in_report_missing > 0:
        print("\n⚠️  ISSUE FOUND: Some discovered pages have include_in_report = False or missing!")
        print("These pages will NOT be marked as 'Include in Report' when uploaded to Drupal.")
else:
    print("No discovered pages found for this project.")
