#!/usr/bin/env python3
"""
Examine the body field structure of existing audit_video entries.

This script looks at several audit_video entries to understand how
key takeaways, painpoints, and assertions are formatted in the HTML body.
"""

import sys
import logging
from auto_a11y.drupal.client import DrupalJSONAPIClient
from auto_a11y.drupal.config import get_drupal_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Examine audit_video body field structures"""

    print("="*70)
    print("Examining Audit Video Body Field Structures")
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

        # Get audit_video entries with longer body content
        print("1. Fetching audit_video entries...")
        response = client.get('node/audit_video', params={'page[limit]': 50})

        videos = response.get('data', [])
        print(f"   Found {len(videos)} videos to examine")
        print()

        # Filter to videos with substantial body content (>500 chars for structured content)
        videos_with_content = []
        for video in videos:
            body = video['attributes'].get('body', {})
            body_value = body.get('value', '') if body else ''
            if body_value and len(body_value) > 500:
                videos_with_content.append((len(body_value), video))

        # Sort by length descending to see the most detailed ones
        videos_with_content.sort(reverse=True, key=lambda x: x[0])

        print(f"   {len(videos_with_content)} videos have substantial body content (>500 chars)")
        print()

        # Examine the top 5 with most content
        for idx, (length, video) in enumerate(videos_with_content[:5], 1):
            print(f"{'='*70}")
            print(f"Video {idx}: {video['attributes'].get('title', 'Untitled')}")
            print(f"{'='*70}")
            print()

            body = video['attributes'].get('body', {})
            body_value = body.get('value', '')

            print("Body HTML:")
            print("-" * 70)
            print(body_value)
            print("-" * 70)
            print()
            print(f"Length: {len(body_value)} characters")
            print()

            # Show basic info
            print("Basic Info:")
            print(f"  - Created: {video['attributes'].get('created', 'N/A')}")
            print(f"  - Play Sequence: {video['attributes'].get('field_play_sequence', 'N/A')}")
            print(f"  - Video URL: {video['attributes'].get('field_video_url', {}).get('uri', 'N/A')}")
            print()
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
