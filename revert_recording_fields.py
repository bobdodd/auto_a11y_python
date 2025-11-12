#!/usr/bin/env python3
"""
Revert migration - restore original JSON field names.

This script reverts the previous migration that translated field names.
Now we keep the original JSON structure to match the input format.

Field reversions:
- Key Takeaways: 'title' -> 'topic'
- User Painpoints: 'user_statement' -> 'user_quote', 'locations' -> 'timecodes'
- User Assertions: Keep as-is (already in correct format)
"""

from auto_a11y.core.database import Database

def revert_recordings():
    """Revert all recordings to use original JSON field names"""

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

        # Revert Key Takeaways: 'title' -> 'topic'
        key_takeaways = recording.get('key_takeaways', [])
        if key_takeaways:
            for takeaway in key_takeaways:
                if 'title' in takeaway and 'topic' not in takeaway:
                    takeaway['topic'] = takeaway.pop('title')
                    needs_update = True
                    print(f"  - Reverted takeaway: moved 'title' back to 'topic'")

        # Revert User Painpoints
        user_painpoints = recording.get('user_painpoints', [])
        if user_painpoints:
            for painpoint in user_painpoints:
                fixed_fields = []

                if 'user_statement' in painpoint and 'user_quote' not in painpoint:
                    painpoint['user_quote'] = painpoint.pop('user_statement')
                    fixed_fields.append("'user_statement' -> 'user_quote'")
                    needs_update = True

                if 'locations' in painpoint and 'timecodes' not in painpoint:
                    painpoint['timecodes'] = painpoint.pop('locations')
                    fixed_fields.append("'locations' -> 'timecodes'")
                    needs_update = True

                # Add back fields from JSON
                if 'impact' not in painpoint:
                    painpoint['impact'] = ''
                    fixed_fields.append("added 'impact'")
                    needs_update = True

                if fixed_fields:
                    print(f"  - Reverted painpoint: {', '.join(fixed_fields)}")

        # Revert User Assertions
        user_assertions = recording.get('user_assertions', [])
        if user_assertions:
            for assertion in user_assertions:
                fixed_fields = []

                if 'title' in assertion and 'assertion' not in assertion:
                    assertion['assertion'] = assertion.pop('title')
                    fixed_fields.append("'title' -> 'assertion'")
                    needs_update = True

                if 'text_spoken' in assertion and 'user_quote' not in assertion:
                    assertion['user_quote'] = assertion.pop('text_spoken')
                    fixed_fields.append("'text_spoken' -> 'user_quote'")
                    needs_update = True

                # Convert flat timecode fields to timecodes array
                if 'start_time' in assertion or 'end_time' in assertion:
                    timecode = {}
                    if 'start_time' in assertion:
                        timecode['start'] = assertion.pop('start_time')
                    if 'end_time' in assertion:
                        timecode['end'] = assertion.pop('end_time')
                    if 'duration' in assertion:
                        timecode['duration'] = assertion.pop('duration')

                    if timecode and 'timecodes' not in assertion:
                        assertion['timecodes'] = [timecode]
                        fixed_fields.append("converted flat fields to 'timecodes' array")
                        needs_update = True

                # Remove 'all_timecodes' if it exists (redundant)
                if 'all_timecodes' in assertion:
                    assertion.pop('all_timecodes')
                    fixed_fields.append("removed 'all_timecodes'")
                    needs_update = True

                if fixed_fields:
                    print(f"  - Reverted assertion: {', '.join(fixed_fields)}")

        # Update database if needed
        if needs_update:
            recordings_collection.update_one(
                {'_id': recording['_id']},
                {
                    '$set': {
                        'key_takeaways': key_takeaways,
                        'user_painpoints': user_painpoints,
                        'user_assertions': user_assertions
                    }
                }
            )
            updated_count += 1
            print(f"  ✓ Updated in database")
        else:
            print(f"  - No changes needed")

        print()

    print(f"\nRevert complete!")
    print(f"Updated {updated_count} of {len(recordings)} recordings")

if __name__ == '__main__':
    revert_recordings()
