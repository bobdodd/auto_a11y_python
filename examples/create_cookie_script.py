#!/usr/bin/env python3
"""
Example: Creating a Page Setup Script for Cookie Notice Dismissal

This example demonstrates how to create a page setup script that automatically
dismisses a cookie notice before running accessibility tests.

Usage:
    python examples/create_cookie_script.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_a11y.core.database import Database
from auto_a11y.models import PageSetupScript, ScriptStep, ActionType, ScriptValidation


def create_cookie_dismissal_script(db: Database, page_id: str) -> str:
    """
    Create a script to dismiss a cookie notice

    Args:
        db: Database connection
        page_id: ID of the page to associate script with

    Returns:
        Script ID
    """
    print(f"Creating cookie dismissal script for page {page_id}...")

    # Create script with steps
    script = PageSetupScript(
        page_id=page_id,
        name='Dismiss Cookie Notice',
        description='Automatically clicks the accept button on the cookie banner',
        enabled=True,
        steps=[
            # Step 1: Wait for cookie banner to appear
            ScriptStep(
                step_number=1,
                action_type=ActionType.WAIT_FOR_SELECTOR,
                selector='.cookie-banner, #cookie-notice, [data-cookie-banner]',
                description='Wait for cookie banner to appear',
                timeout=5000
            ),
            # Step 2: Click the accept button
            ScriptStep(
                step_number=2,
                action_type=ActionType.CLICK,
                selector='.cookie-accept, .accept-cookies, button[data-accept-cookies]',
                description='Click accept cookies button',
                wait_after=1000  # Wait 1 second for banner to disappear
            ),
            # Step 3: Wait for network idle after interaction
            ScriptStep(
                step_number=3,
                action_type=ActionType.WAIT_FOR_NETWORK_IDLE,
                description='Wait for network to be idle after cookie acceptance',
                timeout=3000
            )
        ],
        # Optional: Validate that cookie banner is gone
        validation=ScriptValidation(
            failure_selectors=[
                '.cookie-banner',
                '#cookie-notice'
            ]
        )
    )

    # Save to database
    script_id = db.create_page_setup_script(script)
    print(f"✅ Script created with ID: {script_id}")

    # Associate script with page
    page = db.get_page(page_id)
    if page:
        page.setup_script_id = script_id
        db.update_page(page)
        print(f"✅ Script associated with page: {page.url}")
    else:
        print(f"⚠️  Page not found: {page_id}")

    return script_id


def create_authentication_script(db: Database, page_id: str) -> str:
    """
    Create a script to authenticate before testing

    Args:
        db: Database connection
        page_id: ID of the page to associate script with

    Returns:
        Script ID
    """
    print(f"Creating authentication script for page {page_id}...")

    # Create script with steps
    script = PageSetupScript(
        page_id=page_id,
        name='Sign In',
        description='Automatically signs in with test credentials',
        enabled=True,
        steps=[
            # Step 1: Wait for login form
            ScriptStep(
                step_number=1,
                action_type=ActionType.WAIT_FOR_SELECTOR,
                selector='input#username, input[name="username"]',
                description='Wait for username field to appear',
                timeout=5000
            ),
            # Step 2: Enter username
            ScriptStep(
                step_number=2,
                action_type=ActionType.TYPE,
                selector='input#username, input[name="username"]',
                value='testuser@example.com',
                description='Enter test username'
            ),
            # Step 3: Enter password (from environment variable for security)
            ScriptStep(
                step_number=3,
                action_type=ActionType.TYPE,
                selector='input#password, input[name="password"]',
                value='${ENV:TEST_PASSWORD}',  # Will be replaced with env var
                description='Enter test password from environment variable'
            ),
            # Step 4: Click submit button
            ScriptStep(
                step_number=4,
                action_type=ActionType.CLICK,
                selector='button[type="submit"], input[type="submit"]',
                description='Click login button'
            ),
            # Step 5: Wait for navigation to dashboard
            ScriptStep(
                step_number=5,
                action_type=ActionType.WAIT_FOR_NAVIGATION,
                description='Wait for redirect after login',
                timeout=10000
            ),
            # Step 6: Verify login success
            ScriptStep(
                step_number=6,
                action_type=ActionType.WAIT_FOR_SELECTOR,
                selector='.user-profile, [data-user-menu]',
                description='Wait for user profile element to confirm login',
                timeout=5000
            )
        ],
        # Validate successful login
        validation=ScriptValidation(
            success_selector='.user-profile, .dashboard',
            failure_selectors=[
                '.error-message',
                '.login-failed',
                'input#username'  # Still on login page = failure
            ]
        )
    )

    # Save to database
    script_id = db.create_page_setup_script(script)
    print(f"✅ Script created with ID: {script_id}")

    # Associate script with page
    page = db.get_page(page_id)
    if page:
        page.setup_script_id = script_id
        db.update_page(page)
        print(f"✅ Script associated with page: {page.url}")
    else:
        print(f"⚠️  Page not found: {page_id}")

    return script_id


def list_scripts_for_page(db: Database, page_id: str):
    """
    List all scripts for a page

    Args:
        db: Database connection
        page_id: ID of the page
    """
    print(f"\nScripts for page {page_id}:")
    print("-" * 80)

    scripts = db.get_page_setup_scripts_for_page(page_id)

    if not scripts:
        print("  No scripts found")
        return

    for script in scripts:
        status = "✅ ENABLED" if script.enabled else "⛔ DISABLED"
        print(f"\n  {status} {script.name} ({script.id})")
        print(f"    Description: {script.description}")
        print(f"    Steps: {len(script.steps)}")
        print(f"    Created: {script.created_date}")
        if script.execution_stats.last_executed:
            success_rate = (
                script.execution_stats.success_count /
                (script.execution_stats.success_count + script.execution_stats.failure_count)
                * 100
            ) if (script.execution_stats.success_count + script.execution_stats.failure_count) > 0 else 0
            print(f"    Success Rate: {success_rate:.1f}% "
                  f"({script.execution_stats.success_count} success, "
                  f"{script.execution_stats.failure_count} failures)")
            print(f"    Avg Duration: {script.execution_stats.average_duration_ms}ms")


def main():
    """Main example function"""
    # Connect to database
    db = Database('mongodb://localhost:27017/', 'auto_a11y')

    print("Interactive Page Training - Script Creation Examples")
    print("=" * 80)

    # Example 1: Cookie Notice Dismissal
    print("\n📌 EXAMPLE 1: Cookie Notice Dismissal")
    print("-" * 80)
    print("This script automatically dismisses cookie banners before testing.")
    print("\nTo use this example:")
    print("1. Find a page ID that has a cookie banner")
    print("2. Replace 'YOUR_PAGE_ID_HERE' with the actual page ID")
    print("3. Run this script to create the setup script")
    print("\nExample:")
    print("  page_id = '67890abcdef1234567890abc'")
    print("  script_id = create_cookie_dismissal_script(db, page_id)")

    # Example 2: Authentication
    print("\n\n📌 EXAMPLE 2: Authentication")
    print("-" * 80)
    print("This script logs in before testing authenticated pages.")
    print("\nTo use this example:")
    print("1. Set environment variable: export TEST_PASSWORD='your_test_password'")
    print("2. Find a page ID that requires authentication")
    print("3. Replace 'YOUR_PAGE_ID_HERE' with the actual page ID")
    print("4. Run this script to create the setup script")
    print("\nExample:")
    print("  import os")
    print("  os.environ['TEST_PASSWORD'] = 'testpass123'")
    print("  page_id = '67890abcdef1234567890def'")
    print("  script_id = create_authentication_script(db, page_id)")

    # Example 3: Listing Scripts
    print("\n\n📌 EXAMPLE 3: List Scripts for a Page")
    print("-" * 80)
    print("View all scripts associated with a page:")
    print("\nExample:")
    print("  list_scripts_for_page(db, 'YOUR_PAGE_ID_HERE')")

    print("\n\n" + "=" * 80)
    print("To actually create scripts, uncomment the function calls below and")
    print("replace 'YOUR_PAGE_ID_HERE' with real page IDs from your database.")
    print("=" * 80)

    # Uncomment and modify these lines to actually create scripts:

    # # Create cookie dismissal script
    # page_id = 'YOUR_PAGE_ID_HERE'
    # cookie_script_id = create_cookie_dismissal_script(db, page_id)
    # list_scripts_for_page(db, page_id)

    # # Create authentication script
    # page_id = 'YOUR_PAGE_ID_HERE'
    # auth_script_id = create_authentication_script(db, page_id)
    # list_scripts_for_page(db, page_id)


if __name__ == '__main__':
    main()
