#!/usr/bin/env python3
"""
Investigate the audit_video content type in Drupal.

This script explores the audit_video content type to see if it's suitable
for storing our recording data.
"""

import sys
import json
import logging
from auto_a11y.drupal.client import DrupalJSONAPIClient
from auto_a11y.drupal.config import get_drupal_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Investigate audit_video content type"""

    print("="*70)
    print("Investigating Drupal 'audit_video' Content Type")
    print("="*70)
    print()

    try:
        # Load config and create client
        config = get_drupal_config()
        client = DrupalJSONAPIClient(
            base_url=config.base_url,
            username=config.username,
            password=config.password
        )

        # Get the audit_video resource definition
        print("1. Fetching audit_video resource definition...")
        response = client.get('node/audit_video')

        print(f"   Status: Success")
        print()

        # Check if there are any existing audit_videos
        if 'data' in response:
            videos = response['data']
            print(f"2. Found {len(videos)} existing audit_video entries")
            print()

            if videos:
                print("   Sample audit_video:")
                sample = videos[0]
                print(f"   ID: {sample.get('id')}")
                print(f"   Type: {sample.get('type')}")

                if 'attributes' in sample:
                    attrs = sample['attributes']
                    print(f"\n   Attributes:")
                    for key, value in attrs.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"     - {key}: {value[:100]}...")
                        else:
                            print(f"     - {key}: {value}")

                if 'relationships' in sample:
                    rels = sample['relationships']
                    print(f"\n   Relationships:")
                    for key, value in rels.items():
                        print(f"     - {key}: {value}")

                print()
        else:
            print("2. No existing audit_video entries found")
            print()

        # Get the full schema by looking at the resource object
        print("3. Fetching JSON:API resource object for audit_video...")
        try:
            # Fetch the entry point which includes field definitions
            index_response = client.get('')

            # Look for audit_video in the links
            if 'links' in index_response:
                audit_video_link = index_response['links'].get('node--audit_video', {})
                if isinstance(audit_video_link, dict):
                    print(f"   Resource link: {audit_video_link.get('href', 'Not found')}")
            print()

        except Exception as e:
            print(f"   Could not fetch schema: {e}")
            print()

        # Try to get field definitions using a different approach
        print("4. Trying to understand audit_video structure...")
        print()
        print("   To see all available fields, we need to either:")
        print("   a) Look at an existing audit_video entry")
        print("   b) Examine Drupal's field configuration")
        print("   c) Try creating a test entry and see what validates")
        print()

        # Let's try examining the meta or included data
        if 'data' in response and len(response.get('data', [])) > 0:
            print("5. Detailed examination of first audit_video:")
            first_video = response['data'][0]
            print(json.dumps(first_video, indent=2))
            print()

        client.close()

        return 0

    except Exception as e:
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
