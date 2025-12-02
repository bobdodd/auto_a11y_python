#!/usr/bin/env python3
"""Check SML Footer RecordingIssues in database"""

from pymongo import MongoClient
import os
import json

# Get MongoDB URI from environment or use default
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'auto_a11y')

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Find the SML Footer recording first
recordings = list(db.recordings.find({'title': {'$regex': 'Footer', '$options': 'i'}}))

print(f"Found {len(recordings)} recordings with 'Footer' in title:\n")

for rec in recordings:
    recording_id = rec.get('recording_id')
    print(f"Recording Title: {rec.get('title')}")
    print(f"Recording ID: {recording_id}")
    print(f"Total issues (metadata): {rec.get('total_issues')}")
    print(f"Duration: {rec.get('duration')}")
    print()

    # Now find RecordingIssues for this recording
    recording_issues = list(db.recording_issues.find({'recording_id': recording_id}))

    print(f"Found {len(recording_issues)} RecordingIssues in database for recording_id '{recording_id}':\n")

    if recording_issues:
        for idx, issue in enumerate(recording_issues, 1):
            print(f"Issue #{idx}:")
            print(f"  Title: {issue.get('title')}")
            print(f"  Issue ID: {issue.get('issue_id')}")
            print(f"  Impact: {issue.get('impact')}")
            print(f"  Drupal UUID: {issue.get('drupal_uuid')}")
            print(f"  Drupal Sync Status: {issue.get('drupal_sync_status')}")
            print(f"  What: {issue.get('what', '')[:100]}..." if issue.get('what') else "  What: None")
            print(f"  Why: {issue.get('why', '')[:100]}..." if issue.get('why') else "  Why: None")
            print()
    else:
        print("❌ No RecordingIssues found in database!")
        print("This explains why upload reports 0 issues - they don't exist in the database.")
        print("\nChecking if issues might be under a different recording_id format...")

        # Try variations
        alt_recordings = list(db.recordings.find({'title': 'SML - Footer'}))
        for alt_rec in alt_recordings:
            alt_id = alt_rec.get('recording_id')
            print(f"\nTrying exact title match with recording_id: {alt_id}")
            alt_issues = list(db.recording_issues.find({'recording_id': alt_id}))
            print(f"Found {len(alt_issues)} issues")
