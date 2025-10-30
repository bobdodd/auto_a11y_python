#!/usr/bin/env python3
"""
Example: Multi-State Testing with Cookie Banner

This example demonstrates how to set up and use multi-state testing to test
a page both WITH and WITHOUT a cookie banner visible.

Usage:
    python examples/multi_state_testing_example.py
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_a11y.core.database import Database
from auto_a11y.testing.test_runner import TestRunner
from auto_a11y.models import (
    PageSetupScript, ScriptStep, ActionType,
    ScriptScope, ExecutionTrigger
)


async def create_multi_state_cookie_script(db: Database, page_id: str) -> str:
    """
    Create a multi-state cookie dismissal script

    This script will:
    1. Test the page WITH cookie banner visible (state 0)
    2. Execute the dismissal script
    3. Test the page WITHOUT cookie banner (state 1)

    Args:
        db: Database connection
        page_id: ID of the page to associate script with

    Returns:
        Script ID
    """
    print(f"Creating multi-state cookie dismissal script for page {page_id}...")

    # Create multi-state script
    script = PageSetupScript(
        page_id=page_id,
        name='Multi-State Cookie Dismissal',
        description='Tests page with and without cookie banner',
        enabled=True,

        # Multi-state configuration
        test_before_execution=True,   # TEST #1: Page with cookie banner
        test_after_execution=True,    # TEST #2: Page without cookie banner

        # State validation
        expect_hidden_after=[
            '.cookie-banner',
            '#cookie-notice',
            '[data-cookie-banner]'
        ],

        # Script steps
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
        ]
    )

    # Save to database
    script_id = db.create_page_setup_script(script)
    print(f"✅ Multi-state script created with ID: {script_id}")

    # Associate script with page
    page = db.get_page(page_id)
    if page:
        page.setup_script_id = script_id
        db.update_page(page)
        print(f"✅ Script associated with page: {page.url}")
    else:
        print(f"⚠️  Page not found: {page_id}")

    return script_id


async def run_multi_state_test(db: Database, page_id: str):
    """
    Run multi-state test on a page

    Args:
        db: Database connection
        page_id: ID of page to test
    """
    print(f"\nRunning multi-state test on page {page_id}...")

    # Get page
    page = db.get_page(page_id)
    if not page:
        print(f"❌ Page not found: {page_id}")
        return

    # Create test runner
    browser_config = {
        'HEADLESS': True,
        'SCREENSHOTS_DIR': 'screenshots'
    }
    test_runner = TestRunner(db, browser_config)

    try:
        # Start browser
        await test_runner.browser_manager.start()

        # Run multi-state test
        print(f"\n📊 Testing page: {page.url}")
        results = await test_runner.test_page_multi_state(
            page=page,
            enable_multi_state=True,
            take_screenshot=True
        )

        # Display results
        print(f"\n✅ Multi-state test complete!")
        print(f"Generated {len(results)} test results:\n")

        for i, result in enumerate(results):
            state_desc = result.page_state['description'] if result.page_state else f"State {i}"
            print(f"  State {result.state_sequence}: {state_desc}")
            print(f"    Violations: {result.violation_count}")
            print(f"    Warnings: {result.warning_count}")
            print(f"    Info: {result.info_count}")
            print(f"    Passes: {result.pass_count}")
            if result.related_result_ids:
                print(f"    Related results: {len(result.related_result_ids)}")
            print()

        # Compare states
        if len(results) >= 2:
            print("📈 State Comparison:")
            initial_state = results[0]
            after_script = results[1]

            violation_diff = after_script.violation_count - initial_state.violation_count
            if violation_diff > 0:
                print(f"  ⚠️  {violation_diff} MORE violations after script")
            elif violation_diff < 0:
                print(f"  ✅ {abs(violation_diff)} FEWER violations after script")
            else:
                print(f"  ➖ Same number of violations")

    finally:
        # Cleanup
        await test_runner.browser_manager.stop()
        if test_runner.session_manager.session:
            test_runner.session_manager.end_session()


async def query_multi_state_results(db: Database, page_id: str):
    """
    Query and display multi-state test results

    Args:
        db: Database connection
        page_id: ID of page
    """
    print(f"\nQuerying multi-state results for page {page_id}...\n")

    # Get latest results per state
    state_results = db.get_latest_test_results_per_state(page_id, limit=1)

    if not state_results:
        print("No multi-state results found")
        return

    print(f"📊 Latest Test Results by State:\n")
    for state_seq in sorted(state_results.keys()):
        result = state_results[state_seq]
        state_desc = result.page_state['description'] if result.page_state else f"State {state_seq}"

        print(f"  State {state_seq}: {state_desc}")
        print(f"    Test Date: {result.test_date}")
        print(f"    Violations: {result.violation_count}")
        print(f"    Warnings: {result.warning_count}")
        print(f"    Session: {result.session_id}")

        # Show script info if available
        if result.page_state and result.page_state.get('scripts_executed'):
            scripts = result.page_state['scripts_executed']
            print(f"    Scripts Executed: {len(scripts)}")

        print()

    # Get related results for first state
    if state_results:
        first_result = state_results[min(state_results.keys())]
        related = db.get_related_test_results(str(first_result._id))

        if related:
            print(f"🔗 Related Test Results: {len(related)}")
            for rel in related:
                state_desc = rel.page_state['description'] if rel.page_state else "Unknown"
                print(f"  - State {rel.state_sequence}: {state_desc}")


async def main():
    """Main example function"""
    # Connect to database
    db = Database('mongodb://localhost:27017/', 'auto_a11y')

    print("=" * 80)
    print("Multi-State Testing Example - Cookie Banner")
    print("=" * 80)

    print("\n��� What This Example Does:\n")
    print("1. Creates a multi-state cookie dismissal script")
    print("2. Tests page WITH cookie banner visible (State 0)")
    print("3. Executes script to dismiss cookie banner")
    print("4. Tests page WITHOUT cookie banner (State 1)")
    print("5. Saves both test results with state metadata")
    print("6. Compares violations between states")
    print("7. Queries and displays multi-state results")

    print("\n" + "=" * 80)
    print("Setup Instructions")
    print("=" * 80)
    print("\nTo run this example:\n")
    print("1. Find a page ID that has a cookie banner:")
    print("   page = db.get_pages(limit=1)[0]")
    print("   page_id = page.id")
    print("\n2. Uncomment the function calls at the bottom of this file")
    print("\n3. Replace 'YOUR_PAGE_ID_HERE' with the actual page ID")
    print("\n4. Run: python examples/multi_state_testing_example.py")

    print("\n" + "=" * 80)
    print("Expected Output")
    print("=" * 80)
    print("\nAfter running, you should see:")
    print("• Script created and associated with page")
    print("• Two test results generated (State 0 and State 1)")
    print("• Violation counts for each state")
    print("• Comparison showing difference between states")
    print("• State metadata showing cookie banner status")

    print("\n" + "=" * 80)
    print("Database Queries")
    print("=" * 80)
    print("\nYou can query multi-state results using:\n")
    print("# Get all results for a session")
    print("results = db.get_test_results_by_session(session_id)")
    print("\n# Get results for specific page in session")
    print("results = db.get_test_results_by_page_and_session(page_id, session_id)")
    print("\n# Get related results")
    print("related = db.get_related_test_results(result_id)")
    print("\n# Get latest result for each state")
    print("state_results = db.get_latest_test_results_per_state(page_id)")

    print("\n" + "=" * 80)
    print("Uncomment code below to run example")
    print("=" * 80)

    # Uncomment and modify these lines to actually run the example:

    # # Step 1: Get a page with cookie banner
    # pages = db.get_pages(limit=10)
    # if not pages:
    #     print("❌ No pages found in database")
    #     return
    #
    # # Use first page for testing
    # page = pages[0]
    # page_id = page.id
    # print(f"\n🎯 Using page: {page.url} (ID: {page_id})")
    #
    # # Step 2: Create multi-state script
    # script_id = await create_multi_state_cookie_script(db, page_id)
    #
    # # Step 3: Run multi-state test
    # await run_multi_state_test(db, page_id)
    #
    # # Step 4: Query results
    # await query_multi_state_results(db, page_id)
    #
    # print("\n" + "=" * 80)
    # print("✅ Example Complete!")
    # print("=" * 80)
    # print("\nCheck the database for:")
    # print("• Two TestResult records with different state_sequence values")
    # print("• page_state metadata in each result")
    # print("• related_result_ids linking the results together")
    # print("• State validation results (if cookie banner expectations not met)")


if __name__ == '__main__':
    asyncio.run(main())
