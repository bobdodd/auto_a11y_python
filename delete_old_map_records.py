#!/usr/bin/env python3
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['auto_a11y']

# Delete old fixture test records with ARIA paths
result = db.fixture_tests.delete_many({'expected_code': 'ErrMapAriaHidden', 'fixture_path': {'$regex': '^ARIA/'}})
print(f'Deleted {result.deleted_count} old ARIA fixture_tests records for ErrMapAriaHidden')
