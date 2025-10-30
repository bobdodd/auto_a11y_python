#!/usr/bin/env python3
"""
Example: Creating Page Setup Scripts with Multi-Level Architecture

This example demonstrates the NEW multi-level architecture where scripts can be:
- Website-level (run once per session)
- Page-level (run every time page is tested)
- With conditional execution and violation detection

Usage:
    python examples/create_cookie_script_v2.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auto_a11y.core.database import Database
from auto_a11y.models import (
    PageSetupScript, ScriptStep, ActionType,
    ScriptScope, ExecutionTrigger, ScriptValidation
)


def create_cookie_dismissal_website_level(db: Database, website_id: str) -> str:
    """
    Create a WEBSITE-LEVEL cookie dismissal script (NEW!)

    This script:
    - Runs ONCE per test session (on first page only)
    - Detects if cookie banner reappears (violation)
    - Works across all pages in the website

    Args:
        db: Database connection
        website_id: Website ID

    Returns:
        Script ID
    """
    print(f"Creating website-level cookie dismissal script for website {website_id}...")

    script = PageSetupScript(
        name='Dismiss Cookie Notice',
        description='Automatically dismisses cookie banner on first page, '
                    'reports violation if it reappears',

        # NEW: Website-level scope (not page-specific!)
        scope=ScriptScope.WEBSITE,
        website_id=website_id,

        # NEW: Run once per session
        trigger=ExecutionTrigger.ONCE_PER_SESSION,

        # NEW: Condition selector (check if banner exists)
        condition_selector='.cookie-banner, #cookie-notice, [data-cookie-banner]',

        # NEW: Report violation if condition met AFTER first execution
        report_violation_if_condition_met=True,
        violation_message='Cookie banner persists after initial dismissal',
        violation_code='WarnCookieBannerPersists',

        enabled=True,
        steps=[
            ScriptStep(
                step_number=1,
                action_type=ActionType.WAIT_FOR_SELECTOR,
                selector='.cookie-banner, #cookie-notice, [data-cookie-banner]',
                description='Wait for cookie banner to appear',
                timeout=5000
            ),
            ScriptStep(
                step_number=2,
                action_type=ActionType.CLICK,
                selector='.cookie-accept, .accept-cookies, button[data-accept-cookies]',
                description='Click accept cookies button',
                wait_after=1000
            ),
            ScriptStep(
                step_number=3,
                action_type=ActionType.WAIT_FOR_NETWORK_IDLE,
                description='Wait for network to be idle after cookie acceptance',
                timeout=3000
            )
        ]
    )

    script_id = db.create_page_setup_script(script)
    print(f"✅ Website-level script created with ID: {script_id}")
    print(f"   This script will run ONCE on the first page tested")
    print(f"   If cookie banner reappears on later pages → VIOLATION reported")

    return script_id


def create_optional_newsletter_conditional(db: Database, website_id: str) -> str:
    """
    Create a CONDITIONAL script for optional newsletter popup

    This script:
    - Only executes IF popup exists
    - Does NOT report violation if popup found (it's optional)
    - Runs once per session

    Args:
        db: Database connection
        website_id: Website ID

    Returns:
        Script ID
    """
    print(f"Creating conditional newsletter popup script for website {website_id}...")

    script = PageSetupScript(
        name='Dismiss Newsletter Popup (Optional)',
        description='Closes newsletter popup if present (optional, no violation)',

        scope=ScriptScope.WEBSITE,
        website_id=website_id,

        # NEW: Conditional trigger (only run if element exists)
        trigger=ExecutionTrigger.CONDITIONAL,
        condition_selector='.newsletter-popup, #newsletter-modal',

        # Don't report violation (popup is optional)
        report_violation_if_condition_met=False,

        enabled=True,
        steps=[
            ScriptStep(
                step_number=1,
                action_type=ActionType.CLICK,
                selector='.newsletter-popup .close, #newsletter-modal .close',
                description='Click close button on newsletter popup'
            )
        ]
    )

    script_id = db.create_page_setup_script(script)
    print(f"✅ Conditional script created with ID: {script_id}")
    print(f"   This script only runs if popup exists (no violation if found)")

    return script_id


def create_page_specific_dialog(db: Database, page_id: str, website_id: str) -> str:
    """
    Create a PAGE-LEVEL script for opening a specific dialog

    This script:
    - Runs EVERY TIME this specific page is tested
    - Opens a dialog so its content can be tested

    Args:
        db: Database connection
        page_id: Page ID
        website_id: Website ID

    Returns:
        Script ID
    """
    print(f"Creating page-specific dialog opener for page {page_id}...")

    script = PageSetupScript(
        name='Open Help Dialog',
        description='Opens the help dialog on this specific page for testing',

        # NEW: Page-level scope (specific to one page)
        scope=ScriptScope.PAGE,
        page_id=page_id,
        website_id=website_id,

        # NEW: Run every time this page is tested
        trigger=ExecutionTrigger.ONCE_PER_PAGE,

        enabled=True,
        steps=[
            ScriptStep(
                step_number=1,
                action_type=ActionType.CLICK,
                selector='button.help, #help-button',
                description='Click help button'
            ),
            ScriptStep(
                step_number=2,
                action_type=ActionType.WAIT_FOR_SELECTOR,
                selector='.help-dialog, #help-modal',
                description='Wait for help dialog to appear',
                timeout=5000
            )
        ]
    )

    script_id = db.create_page_setup_script(script)
    print(f"✅ Page-level script created with ID: {script_id}")
    print(f"   This script runs EVERY TIME page {page_id} is tested")

    return script_id


def create_authentication_always(db: Database, website_id: str) -> str:
    """
    Create an ALWAYS-executing authentication script

    This script:
    - Runs unconditionally (ALWAYS trigger)
    - Can be website or test-run level
    - Uses environment variables for password security

    Args:
        db: Database connection
        website_id: Website ID

    Returns:
        Script ID
    """
    print(f"Creating authentication script for website {website_id}...")

    script = PageSetupScript(
        name='Sign In',
        description='Authenticates with test credentials before testing',

        scope=ScriptScope.WEBSITE,
        website_id=website_id,

        # NEW: Always execute (unconditional)
        trigger=ExecutionTrigger.ALWAYS,

        enabled=True,
        steps=[
            ScriptStep(
                step_number=1,
                action_type=ActionType.WAIT_FOR_SELECTOR,
                selector='input#username, input[name="username"]',
                description='Wait for username field',
                timeout=5000
            ),
            ScriptStep(
                step_number=2,
                action_type=ActionType.TYPE,
                selector='input#username, input[name="username"]',
                value='testuser@example.com',
                description='Enter test username'
            ),
            ScriptStep(
                step_number=3,
                action_type=ActionType.TYPE,
                selector='input#password, input[name="password"]',
                value='${ENV:TEST_PASSWORD}',  # Secure: from environment
                description='Enter test password from environment'
            ),
            ScriptStep(
                step_number=4,
                action_type=ActionType.CLICK,
                selector='button[type="submit"], input[type="submit"]',
                description='Click login button'
            ),
            ScriptStep(
                step_number=5,
                action_type=ActionType.WAIT_FOR_NAVIGATION,
                description='Wait for redirect after login',
                timeout=10000
            )
        ],

        # Validation: Ensure login succeeded
        validation=ScriptValidation(
            success_selector='.user-profile, .dashboard',
            failure_selectors=[
                '.error-message',
                '.login-failed',
                'input#username'  # Still on login page = failure
            ]
        )
    )

    script_id = db.create_page_setup_script(script)
    print(f"✅ Authentication script created with ID: {script_id}")
    print(f"   This script runs ALWAYS (unconditional)")
    print(f"   Remember to set TEST_PASSWORD environment variable!")

    return script_id


def demonstrate_execution_flow():
    """
    Demonstrate how the new architecture works during testing
    """
    print("\n" + "=" * 80)
    print("EXECUTION FLOW EXAMPLE")
    print("=" * 80)

    print("""
Website-Level Script (ONCE_PER_SESSION, Cookie Notice):
┌────────────────────────────────────────────────────────────────┐
│ Page 1 (First Test):                                           │
│   1. Check condition: cookie banner EXISTS                     │
│   2. Execute script: Click accept button                       │
│   3. Mark as executed in session                               │
│   4. Continue with accessibility tests                         │
│                                                                  │
│ Page 2 (Second Test):                                          │
│   1. Check condition: cookie banner EXISTS                     │
│   2. Script already executed → Check for VIOLATION             │
│   3. ⚠️  VIOLATION: Cookie banner persists                     │
│   4. Add violation to test results                             │
│   5. Continue with accessibility tests                         │
│                                                                  │
│ Page 3 (Third Test):                                           │
│   1. Check condition: cookie banner NOT found                  │
│   2. Skip (no violation, banner gone as expected)              │
│   3. Continue with accessibility tests                         │
└────────────────────────────────────────────────────────────────┘

Page-Level Script (ONCE_PER_PAGE, Dialog Opener):
┌────────────────────────────────────────────────────────────────┐
│ Every time the specific page is tested:                       │
│   1. Execute script: Click button to open dialog              │
│   2. Wait for dialog to appear                                │
│   3. Continue with accessibility tests on OPEN dialog         │
└────────────────────────────────────────────────────────────────┘

Conditional Script (CONDITIONAL, Newsletter Popup):
┌────────────────────────────────────────────────────────────────┐
│ Each page:                                                     │
│   1. Check condition: popup EXISTS or NOT                      │
│   2. If EXISTS → Execute script (close popup)                 │
│   3. If NOT EXISTS → Skip (no violation)                       │
│   4. Continue with accessibility tests                         │
└────────────────────────────────────────────────────────────────┘
""")


def main():
    """Main example function"""
    db = Database('mongodb://localhost:27017/', 'auto_a11y')

    print("\n" + "=" * 80)
    print("INTERACTIVE PAGE TRAINING - MULTI-LEVEL ARCHITECTURE v2.0")
    print("=" * 80)

    print("""
This example demonstrates the NEW multi-level architecture where scripts can be:

📌 SCOPES:
   - WEBSITE: Run once per test session (all pages)
   - PAGE: Run every time specific page is tested
   - TEST_RUN: Run before a batch of pages (future)

🎯 TRIGGERS:
   - ONCE_PER_SESSION: Execute only once across all pages
   - ONCE_PER_PAGE: Execute every time page is tested
   - CONDITIONAL: Execute only if element exists
   - ALWAYS: Execute unconditionally

⚠️  VIOLATION DETECTION:
   - Report if condition reappears after dismissal
   - Example: Cookie banner dismissed but reappears = violation

""")

    # Example 1: Website-level cookie notice (PRIMARY USE CASE)
    print("\n📌 EXAMPLE 1: Cookie Notice (Website-Level, Once Per Session)")
    print("-" * 80)
    print("This is your PRIMARY use case:")
    print("- Dismisses cookie banner on FIRST page only")
    print("- Reports VIOLATION if banner reappears on subsequent pages")
    print("\nTo use:")
    print("  website_id = 'YOUR_WEBSITE_ID'")
    print("  script_id = create_cookie_dismissal_website_level(db, website_id)")

    # Example 2: Conditional newsletter (no violation)
    print("\n\n📌 EXAMPLE 2: Newsletter Popup (Conditional, No Violation)")
    print("-" * 80)
    print("This script:")
    print("- Only runs IF popup exists")
    print("- Does NOT report violation (popup is optional)")
    print("\nTo use:")
    print("  website_id = 'YOUR_WEBSITE_ID'")
    print("  script_id = create_optional_newsletter_conditional(db, website_id)")

    # Example 3: Page-specific dialog
    print("\n\n📌 EXAMPLE 3: Page-Specific Dialog (Page-Level)")
    print("-" * 80)
    print("This script:")
    print("- Runs EVERY TIME this specific page is tested")
    print("- Opens a dialog so its content can be tested")
    print("\nTo use:")
    print("  page_id = 'YOUR_PAGE_ID'")
    print("  website_id = 'YOUR_WEBSITE_ID'")
    print("  script_id = create_page_specific_dialog(db, page_id, website_id)")

    # Example 4: Authentication (always)
    print("\n\n📌 EXAMPLE 4: Authentication (Always Execute)")
    print("-" * 80)
    print("This script:")
    print("- Runs ALWAYS (unconditional)")
    print("- Uses environment variables for password")
    print("- Validates login succeeded")
    print("\nTo use:")
    print("  export TEST_PASSWORD='your_test_password'")
    print("  website_id = 'YOUR_WEBSITE_ID'")
    print("  script_id = create_authentication_always(db, website_id)")

    # Demonstrate execution flow
    demonstrate_execution_flow()

    print("\n" + "=" * 80)
    print("To actually create scripts, uncomment the function calls below and")
    print("replace 'YOUR_WEBSITE_ID' and 'YOUR_PAGE_ID' with real IDs")
    print("=" * 80)

    # Uncomment to create scripts:
    # website_id = 'YOUR_WEBSITE_ID'
    # create_cookie_dismissal_website_level(db, website_id)
    # create_optional_newsletter_conditional(db, website_id)
    # create_authentication_always(db, website_id)
    #
    # page_id = 'YOUR_PAGE_ID'
    # create_page_specific_dialog(db, page_id, website_id)


if __name__ == '__main__':
    main()
