#!/usr/bin/env python3
"""
Migration script to fix field names in existing recordings.

This script updates recordings that were parsed with old field names to use
the correct field names expected by the templates.

Field mappings:
- Key Takeaways: 'topic' -> 'title'
- User Painpoints: 'difficulty' -> 'title', 'description' -> 'user_statement', 'timecodes' -> 'locations'
- User Assertions: No changes needed (already correct)
"""

from auto_a11y.core.database import Database

def migrate_recordings():
    """Migrate all recordings to use correct field names"""

    # Initialize database
    db = Database('mongodb://localhost:27017/', 'auto_a11y')
    recordings_collection = db.db['recordings']

    # Get all recordings
    recordings = list(recordings_collection.find())

    print(f"Found {len(recordings)} recordings to check\n")

    updated_count = 0

    for recording in recordings:
        recording_id = recording.get('recording_id', 'Unknown')
        title = recording.get('title', 'Unknown')
        needs_update = False

        print(f"Checking: {recording_id} - {title}")

        # Fix Key Takeaways: 'topic' -> 'title'
        key_takeaways = recording.get('key_takeaways', [])
        if key_takeaways:
            for takeaway in key_takeaways:
                if 'topic' in takeaway and 'title' not in takeaway:
                    takeaway['title'] = takeaway.pop('topic')
                    needs_update = True
                    print(f"  - Fixed takeaway: moved 'topic' to 'title'")

        # Fix User Painpoints: 'difficulty' -> 'title', 'description' -> 'user_statement', 'timecodes' -> 'locations'
        user_painpoints = recording.get('user_painpoints', [])
        if user_painpoints:
            for painpoint in user_painpoints:
                fixed_fields = []

                if 'difficulty' in painpoint and 'title' not in painpoint:
                    painpoint['title'] = painpoint.pop('difficulty')
                    fixed_fields.append("'difficulty' -> 'title'")
                    needs_update = True

                if 'description' in painpoint and 'user_statement' not in painpoint:
                    painpoint['user_statement'] = painpoint.pop('description')
                    fixed_fields.append("'description' -> 'user_statement'")
                    needs_update = True

                if 'timecodes' in painpoint and 'locations' not in painpoint:
                    painpoint['locations'] = painpoint.pop('timecodes')
                    fixed_fields.append("'timecodes' -> 'locations'")
                    needs_update = True

                # Remove extra fields not needed by template
                if 'number' in painpoint:
                    painpoint.pop('number')
                    fixed_fields.append("removed 'number'")
                    needs_update = True

                if 'impact' in painpoint:
                    painpoint.pop('impact')
                    fixed_fields.append("removed 'impact'")
                    needs_update = True

                if fixed_fields:
                    print(f"  - Fixed painpoint: {', '.join(fixed_fields)}")

        # Update database if needed
        if needs_update:
            recordings_collection.update_one(
                {'_id': recording['_id']},
                {
                    '$set': {
                        'key_takeaways': key_takeaways,
                        'user_painpoints': user_painpoints
                    }
                }
            )
            updated_count += 1
            print(f"  ✓ Updated in database")
        else:
            print(f"  - No changes needed")

        print()

    print(f"\nMigration complete!")
    print(f"Updated {updated_count} of {len(recordings)} recordings")

if __name__ == '__main__':
    migrate_recordings()
