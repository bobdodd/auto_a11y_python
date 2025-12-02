#!/usr/bin/env python3
"""Check SML Footer recording duration in database"""

from pymongo import MongoClient
import os

# Get MongoDB URI from environment or use default
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'auto_a11y')

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Find the SML Footer recording
recordings = list(db.recordings.find({'title': {'$regex': 'Footer', '$options': 'i'}}))

print(f"Found {len(recordings)} recordings with 'Footer' in title:\n")

for rec in recordings:
    print(f"Title: {rec.get('title')}")
    print(f"Recording ID: {rec.get('recording_id')}")
    print(f"Duration field: {rec.get('duration')} (type: {type(rec.get('duration'))})")
    print(f"Project ID: {rec.get('project_id')}")
    print(f"Sync status: {rec.get('drupal_sync_status')}")
    print(f"Total issues: {rec.get('total_issues')}")
    print()
