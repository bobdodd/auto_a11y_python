"""
Page Setup Scripts Management Routes
"""

from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from auto_a11y.models import PageSetupScript, ScriptStep, ActionType, ScriptScope, ExecutionTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
scripts_bp = Blueprint('scripts', __name__)


@scripts_bp.route('/page/<page_id>/scripts')
def list_page_scripts(page_id):
    """List all scripts for a page"""
    page = current_app.db.get_page(page_id)
    if not page:
        flash('Page not found', 'error')
        return redirect(url_for('index'))

    # Get website and project for context
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    # Get page-level scripts
    page_scripts = current_app.db.get_page_setup_scripts_for_page(page_id)

    # Get website-level scripts
    website_scripts = current_app.db.get_scripts_for_website(
        page.website_id,
        scope=ScriptScope.WEBSITE.value,  # Pass the string value, not the enum
        enabled_only=False
    )

    return render_template('scripts/list.html',
                         page=page,
                         website=website,
                         project=project,
                         page_scripts=page_scripts,
                         website_scripts=website_scripts)


@scripts_bp.route('/page/<page_id>/scripts/create', methods=['GET', 'POST'])
def create_page_script(page_id):
    """Create a new page setup script"""
    page = current_app.db.get_page(page_id)
    if not page:
        flash('Page not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Parse form data
            data = request.form

            # Create script steps from dynamic form
            steps = []
            step_count = 0
            while f'step_{step_count}_action' in data:
                selector = data.get(f'step_{step_count}_selector', '')
                logger.warning(f"Step {step_count}: selector field value = '{selector}'")
                step = ScriptStep(
                    step_number=step_count + 1,
                    action_type=ActionType(data[f'step_{step_count}_action']),
                    selector=selector if selector else None,
                    value=data.get(f'step_{step_count}_value', ''),
                    description=data.get(f'step_{step_count}_description', ''),
                    timeout=int(data.get(f'step_{step_count}_timeout', 5000)),
                    wait_after=int(data.get(f'step_{step_count}_wait_after', 0))
                )
                logger.warning(f"Created step: {step.to_dict()}")
                steps.append(step)
                step_count += 1

            # Parse multi-value fields
            expect_visible = [x.strip() for x in data.get('expect_visible_after', '').split('\n') if x.strip()]
            expect_hidden = [x.strip() for x in data.get('expect_hidden_after', '').split('\n') if x.strip()]

            # Create script
            script = PageSetupScript(
                page_id=page_id,
                website_id=page.website_id,
                name=data['name'],
                description=data.get('description', ''),
                enabled=data.get('enabled') == 'on',
                scope=ScriptScope.PAGE,  # Page-level by default
                trigger=ExecutionTrigger(data.get('trigger', 'always')),
                test_before_execution=data.get('test_before_execution') == 'on',
                test_after_execution=data.get('test_after_execution') == 'on',
                expect_visible_after=expect_visible,
                expect_hidden_after=expect_hidden,
                clear_cookies_before=data.get('clear_cookies_before') == 'on',
                clear_local_storage_before=data.get('clear_local_storage_before') == 'on',
                steps=steps
            )

            # Save to database
            script_id = current_app.db.create_page_setup_script(script)

            flash(f'Script "{script.name}" created successfully', 'success')
            return redirect(url_for('scripts.edit_script', script_id=script_id))

        except Exception as e:
            logger.error(f"Error creating script: {e}")
            flash(f'Error creating script: {str(e)}', 'error')

    # GET request - show form
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    # Get all action types for dropdown
    action_types = [
        {'value': ActionType.CLICK.value, 'label': 'Click Element'},
        {'value': ActionType.TYPE.value, 'label': 'Type Text'},
        {'value': ActionType.SELECT.value, 'label': 'Select Dropdown Option'},
        {'value': ActionType.WAIT_FOR_SELECTOR.value, 'label': 'Wait for Element'},
        {'value': ActionType.WAIT.value, 'label': 'Wait (Fixed Time)'},
        {'value': ActionType.WAIT_FOR_NETWORK_IDLE.value, 'label': 'Wait for Network Idle'},
        {'value': ActionType.SCROLL.value, 'label': 'Scroll to Element'},
        {'value': ActionType.HOVER.value, 'label': 'Hover Over Element'},
        {'value': ActionType.WAIT_FOR_NAVIGATION.value, 'label': 'Wait for Navigation'},
        {'value': ActionType.SCREENSHOT.value, 'label': 'Take Screenshot'}
    ]

    trigger_options = [
        {'value': ExecutionTrigger.ALWAYS.value, 'label': 'Always (Every Test)', 'description': 'Runs every time this page is tested'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE.value, 'label': 'Once Per Page', 'description': 'Runs every time this page is tested'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE_FIRST_VISIT.value, 'label': 'Once Per Page (First Visit Only)', 'description': 'Runs only on the first test of this page in a session'},
        {'value': ExecutionTrigger.CONDITIONAL.value, 'label': 'Conditional (If Element Exists)', 'description': 'Runs only if the condition selector exists'}
    ]

    scope_options = [
        {'value': ScriptScope.PAGE.value, 'label': 'Page-Level', 'description': 'Runs only on this specific page'},
    ]

    return render_template('scripts/create.html',
                         page=page,
                         website=website,
                         project=project,
                         action_types=action_types,
                         trigger_options=trigger_options,
                         scope_options=scope_options,
                         is_website_script=False)


@scripts_bp.route('/website/<website_id>/scripts/create', methods=['GET', 'POST'])
def create_website_script(website_id):
    """Create a new website-level setup script"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Parse form data
            data = request.form

            # Create script steps from dynamic form
            steps = []
            step_count = 0
            while f'step_{step_count}_action' in data:
                selector = data.get(f'step_{step_count}_selector', '')
                step = ScriptStep(
                    step_number=step_count + 1,
                    action_type=ActionType(data[f'step_{step_count}_action']),
                    selector=selector if selector else None,
                    value=data.get(f'step_{step_count}_value', ''),
                    description=data.get(f'step_{step_count}_description', ''),
                    timeout=int(data.get(f'step_{step_count}_timeout', 5000)),
                    wait_after=int(data.get(f'step_{step_count}_wait_after', 0))
                )
                steps.append(step)
                step_count += 1

            # Parse multi-value fields
            expect_visible = [x.strip() for x in data.get('expect_visible_after', '').split('\n') if x.strip()]
            expect_hidden = [x.strip() for x in data.get('expect_hidden_after', '').split('\n') if x.strip()]

            # Create script with WEBSITE scope
            script = PageSetupScript(
                page_id=None,  # No specific page
                website_id=website_id,
                name=data['name'],
                description=data.get('description', ''),
                enabled=data.get('enabled') == 'on',
                scope=ScriptScope.WEBSITE,  # Website-level
                trigger=ExecutionTrigger(data.get('trigger', 'once_per_session')),
                test_before_execution=data.get('test_before_execution') == 'on',
                test_after_execution=data.get('test_after_execution') == 'on',
                expect_visible_after=expect_visible,
                expect_hidden_after=expect_hidden,
                clear_cookies_before=data.get('clear_cookies_before') == 'on',
                clear_local_storage_before=data.get('clear_local_storage_before') == 'on',
                condition_selector=data.get('condition_selector', ''),
                wait_for_selector=data.get('wait_for_selector') == 'on',
                wait_timeout=int(data.get('wait_timeout', 5000)),
                steps=steps
            )

            # Save to database
            script_id = current_app.db.create_page_setup_script(script)

            flash(f'Website script "{script.name}" created successfully', 'success')
            return redirect(url_for('scripts.edit_script', script_id=script_id))

        except Exception as e:
            logger.error(f"Error creating website script: {e}")
            flash(f'Error creating script: {str(e)}', 'error')

    # GET request - show form
    project = current_app.db.get_project(website.project_id)

    # Get all action types for dropdown
    action_types = [
        {'value': ActionType.CLICK.value, 'label': 'Click Element'},
        {'value': ActionType.TYPE.value, 'label': 'Type Text'},
        {'value': ActionType.SELECT.value, 'label': 'Select Dropdown Option'},
        {'value': ActionType.WAIT_FOR_SELECTOR.value, 'label': 'Wait for Element'},
        {'value': ActionType.WAIT.value, 'label': 'Wait (Fixed Time)'},
        {'value': ActionType.WAIT_FOR_NETWORK_IDLE.value, 'label': 'Wait for Network Idle'},
        {'value': ActionType.SCROLL.value, 'label': 'Scroll to Element'},
        {'value': ActionType.HOVER.value, 'label': 'Hover Over Element'},
        {'value': ActionType.WAIT_FOR_NAVIGATION.value, 'label': 'Wait for Navigation'},
        {'value': ActionType.SCREENSHOT.value, 'label': 'Take Screenshot'}
    ]

    trigger_options = [
        {'value': ExecutionTrigger.ONCE_PER_SESSION.value, 'label': 'Once Per Session', 'description': 'Runs once at the start of testing'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE.value, 'label': 'Once Per Page', 'description': 'Runs before testing each page'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE_FIRST_VISIT.value, 'label': 'Once Per Page (First Visit Only)', 'description': 'Runs only on the first test of this page in a session'},
        {'value': ExecutionTrigger.ALWAYS.value, 'label': 'Always (Every Test)', 'description': 'Runs every time a page is tested'},
        {'value': ExecutionTrigger.CONDITIONAL.value, 'label': 'Conditional', 'description': 'Runs only if element exists'}
    ]

    scope_options = [
        {'value': ScriptScope.WEBSITE.value, 'label': 'Website-Level', 'description': 'Applies to all pages in this website'},
    ]

    return render_template('scripts/create.html',
                         page=None,  # No specific page
                         website=website,
                         project=project,
                         action_types=action_types,
                         trigger_options=trigger_options,
                         scope_options=scope_options,
                         is_website_script=True)


@scripts_bp.route('/website/<website_id>/scripts')
def list_website_scripts(website_id):
    """List all scripts for a website"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    # Get project for context
    project = current_app.db.get_project(website.project_id) if website else None

    # Get website-level scripts
    website_scripts = current_app.db.get_scripts_for_website(
        website_id,
        scope=ScriptScope.WEBSITE.value,
        enabled_only=False
    )

    return render_template('scripts/list.html',
                         page=None,  # No specific page
                         website=website,
                         project=project,
                         page_scripts=[],  # No page-specific scripts
                         website_scripts=website_scripts)


@scripts_bp.route('/<script_id>')
def view_script(script_id):
    """View script details"""
    script = current_app.db.get_page_setup_script(script_id)
    if not script:
        flash('Script not found', 'error')
        return redirect(url_for('index'))

    # Get related page/website/project
    page = current_app.db.get_page(script.page_id) if script.page_id else None
    website = current_app.db.get_website(script.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    return render_template('scripts/view.html',
                         script=script,
                         page=page,
                         website=website,
                         project=project)


@scripts_bp.route('/<script_id>/edit', methods=['GET', 'POST'])
def edit_script(script_id):
    """Edit an existing script"""
    script = current_app.db.get_page_setup_script(script_id)
    if not script:
        flash('Script not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            data = request.form

            # Update script steps
            steps = []
            step_count = 0
            logger.warning(f"EDIT: Parsing form data. Keys: {list(data.keys())}")
            while f'step_{step_count}_action' in data:
                selector = data.get(f'step_{step_count}_selector', '')
                logger.warning(f"EDIT Step {step_count}: selector field value = '{selector}'")
                step = ScriptStep(
                    step_number=step_count + 1,
                    action_type=ActionType(data[f'step_{step_count}_action']),
                    selector=selector if selector else None,
                    value=data.get(f'step_{step_count}_value', ''),
                    description=data.get(f'step_{step_count}_description', ''),
                    timeout=int(data.get(f'step_{step_count}_timeout', 5000)),
                    wait_after=int(data.get(f'step_{step_count}_wait_after', 0))
                )
                logger.warning(f"EDIT Created step: {step.to_dict()}")
                steps.append(step)
                step_count += 1

            # Parse multi-value fields
            expect_visible = [x.strip() for x in data.get('expect_visible_after', '').split('\n') if x.strip()]
            expect_hidden = [x.strip() for x in data.get('expect_hidden_after', '').split('\n') if x.strip()]

            # Update script
            script.name = data['name']
            script.description = data.get('description', '')
            script.enabled = data.get('enabled') == 'on'
            script.trigger = ExecutionTrigger(data.get('trigger', 'always'))
            script.test_before_execution = data.get('test_before_execution') == 'on'
            script.test_after_execution = data.get('test_after_execution') == 'on'
            script.expect_visible_after = expect_visible
            script.expect_hidden_after = expect_hidden
            script.clear_cookies_before = data.get('clear_cookies_before') == 'on'
            script.clear_local_storage_before = data.get('clear_local_storage_before') == 'on'
            script.condition_selector = data.get('condition_selector', '')
            script.wait_for_selector = data.get('wait_for_selector') == 'on'
            script.wait_timeout = int(data.get('wait_timeout', 5000))
            script.steps = steps
            script.last_modified = datetime.now()

            # Save changes
            current_app.db.update_page_setup_script(script)

            flash(f'Script "{script.name}" updated successfully', 'success')
            return redirect(url_for('scripts.view_script', script_id=script_id))

        except Exception as e:
            logger.error(f"Error updating script: {e}")
            flash(f'Error updating script: {str(e)}', 'error')

    # GET request - show form
    page = current_app.db.get_page(script.page_id) if script.page_id else None
    website = current_app.db.get_website(script.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    # Debug: Log the script steps being loaded
    logger.warning(f"EDIT GET: Loading script '{script.name}' with {len(script.steps)} steps")
    for i, step in enumerate(script.steps):
        logger.warning(f"EDIT GET Step {i}: {step.to_dict()}")

    action_types = [
        {'value': ActionType.CLICK.value, 'label': 'Click Element'},
        {'value': ActionType.TYPE.value, 'label': 'Type Text'},
        {'value': ActionType.SELECT.value, 'label': 'Select Dropdown Option'},
        {'value': ActionType.WAIT_FOR_SELECTOR.value, 'label': 'Wait for Element'},
        {'value': ActionType.WAIT.value, 'label': 'Wait (Fixed Time)'},
        {'value': ActionType.WAIT_FOR_NETWORK_IDLE.value, 'label': 'Wait for Network Idle'},
        {'value': ActionType.SCROLL.value, 'label': 'Scroll to Element'},
        {'value': ActionType.HOVER.value, 'label': 'Hover Over Element'},
        {'value': ActionType.WAIT_FOR_NAVIGATION.value, 'label': 'Wait for Navigation'},
        {'value': ActionType.SCREENSHOT.value, 'label': 'Take Screenshot'}
    ]

    trigger_options = [
        {'value': ExecutionTrigger.ONCE_PER_SESSION.value, 'label': 'Once Per Session', 'description': 'Runs once at the start of testing'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE.value, 'label': 'Once Per Page', 'description': 'Runs before testing each page'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE_FIRST_VISIT.value, 'label': 'Once Per Page (First Visit Only)', 'description': 'Runs only on the first test of this page in a session'},
        {'value': ExecutionTrigger.ALWAYS.value, 'label': 'Always (Every Test)', 'description': 'Runs every time a page is tested'},
        {'value': ExecutionTrigger.CONDITIONAL.value, 'label': 'Conditional', 'description': 'Runs only if element exists'}
    ]

    scope_options = [
        {'value': ScriptScope.PAGE.value, 'label': 'Page-Level', 'description': 'Runs only on this specific page'},
        {'value': ScriptScope.WEBSITE.value, 'label': 'Website-Level', 'description': 'Applies to all pages in this website'},
    ]

    return render_template('scripts/edit.html',
                         script=script,
                         page=page,
                         website=website,
                         project=project,
                         action_types=action_types,
                         trigger_options=trigger_options,
                         scope_options=scope_options,
                         is_website_script=(script.scope == ScriptScope.WEBSITE))


@scripts_bp.route('/<script_id>/delete', methods=['POST'])
def delete_script(script_id):
    """Delete a script"""
    script = current_app.db.get_page_setup_script(script_id)
    if not script:
        return jsonify({'error': 'Script not found'}), 404

    try:
        current_app.db.delete_page_setup_script(script_id)
        flash(f'Script "{script.name}" deleted successfully', 'success')

        # Return redirect URL
        if script.page_id:
            return jsonify({
                'success': True,
                'redirect': url_for('scripts.list_page_scripts', page_id=script.page_id)
            })
        else:
            return jsonify({
                'success': True,
                'redirect': url_for('index')
            })
    except Exception as e:
        logger.error(f"Error deleting script: {e}")
        return jsonify({'error': str(e)}), 500


@scripts_bp.route('/<script_id>/toggle', methods=['POST'])
def toggle_script(script_id):
    """Enable/disable a script"""
    logger.warning(f"{'='*60}")
    logger.warning(f"TOGGLE ROUTE HIT! script_id: {script_id}")
    logger.warning(f"{'='*60}")

    script = current_app.db.get_page_setup_script(script_id)
    if not script:
        logger.warning(f"ERROR: Script not found: {script_id}")
        return jsonify({'error': 'Script not found'}), 404

    try:
        old_state = script.enabled
        logger.warning(f"Old state: {old_state}")

        script.enabled = not script.enabled
        new_state = script.enabled
        logger.warning(f"New state: {new_state}")

        success = current_app.db.update_page_setup_script(script)
        logger.warning(f"Database update success: {success}")

        # Verify the update by reading back from database
        verified_script = current_app.db.get_page_setup_script(script_id)
        logger.warning(f"Verified from DB: enabled={verified_script.enabled}")

        return jsonify({
            'success': success,
            'enabled': script.enabled,
            'message': f'Script {"enabled" if script.enabled else "disabled"}',
            'old_state': old_state,
            'new_state': new_state
        })
    except Exception as e:
        import traceback
        logger.warning(f"ERROR: {e}")
        logger.warning(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@scripts_bp.route('/<script_id>/test', methods=['POST'])
def test_script(script_id):
    """Test a script (dry run)"""
    script = current_app.db.get_page_setup_script(script_id)
    if not script:
        return jsonify({'error': 'Script not found'}), 404

    # TODO: Implement script testing functionality
    # This would run the script without affecting test results

    return jsonify({
        'success': True,
        'message': 'Script test feature coming soon'
    })
