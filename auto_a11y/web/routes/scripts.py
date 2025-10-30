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
                step = ScriptStep(
                    step_number=step_count + 1,
                    action_type=ActionType(data[f'step_{step_count}_action']),
                    selector=data.get(f'step_{step_count}_selector', ''),
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
        {'value': ActionType.WAIT_FOR_TIMEOUT.value, 'label': 'Wait (Fixed Time)'},
        {'value': ActionType.WAIT_FOR_NETWORK_IDLE.value, 'label': 'Wait for Network Idle'},
        {'value': ActionType.SCROLL_TO.value, 'label': 'Scroll to Element'},
        {'value': ActionType.HOVER.value, 'label': 'Hover Over Element'},
        {'value': ActionType.PRESS_KEY.value, 'label': 'Press Key'},
        {'value': ActionType.EVALUATE.value, 'label': 'Run JavaScript'}
    ]

    trigger_options = [
        {'value': ExecutionTrigger.ALWAYS.value, 'label': 'Always (Every Test)'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE.value, 'label': 'Once Per Page'},
        {'value': ExecutionTrigger.CONDITIONAL.value, 'label': 'Conditional (If Element Exists)'}
    ]

    return render_template('scripts/create.html',
                         page=page,
                         website=website,
                         project=project,
                         action_types=action_types,
                         trigger_options=trigger_options)


@scripts_bp.route('/scripts/<script_id>')
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


@scripts_bp.route('/scripts/<script_id>/edit', methods=['GET', 'POST'])
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
            while f'step_{step_count}_action' in data:
                step = ScriptStep(
                    step_number=step_count + 1,
                    action_type=ActionType(data[f'step_{step_count}_action']),
                    selector=data.get(f'step_{step_count}_selector', ''),
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

            # Update script
            script.name = data['name']
            script.description = data.get('description', '')
            script.enabled = data.get('enabled') == 'on'
            script.trigger = ExecutionTrigger(data.get('trigger', 'always'))
            script.test_before_execution = data.get('test_before_execution') == 'on'
            script.test_after_execution = data.get('test_after_execution') == 'on'
            script.expect_visible_after = expect_visible
            script.expect_hidden_after = expect_hidden
            script.steps = steps
            script.updated_date = datetime.now()

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

    action_types = [
        {'value': ActionType.CLICK.value, 'label': 'Click Element'},
        {'value': ActionType.TYPE.value, 'label': 'Type Text'},
        {'value': ActionType.SELECT.value, 'label': 'Select Dropdown Option'},
        {'value': ActionType.WAIT_FOR_SELECTOR.value, 'label': 'Wait for Element'},
        {'value': ActionType.WAIT_FOR_TIMEOUT.value, 'label': 'Wait (Fixed Time)'},
        {'value': ActionType.WAIT_FOR_NETWORK_IDLE.value, 'label': 'Wait for Network Idle'},
        {'value': ActionType.SCROLL_TO.value, 'label': 'Scroll to Element'},
        {'value': ActionType.HOVER.value, 'label': 'Hover Over Element'},
        {'value': ActionType.PRESS_KEY.value, 'label': 'Press Key'},
        {'value': ActionType.EVALUATE.value, 'label': 'Run JavaScript'}
    ]

    trigger_options = [
        {'value': ExecutionTrigger.ALWAYS.value, 'label': 'Always (Every Test)'},
        {'value': ExecutionTrigger.ONCE_PER_PAGE.value, 'label': 'Once Per Page'},
        {'value': ExecutionTrigger.CONDITIONAL.value, 'label': 'Conditional (If Element Exists)'}
    ]

    return render_template('scripts/edit.html',
                         script=script,
                         page=page,
                         website=website,
                         project=project,
                         action_types=action_types,
                         trigger_options=trigger_options)


@scripts_bp.route('/scripts/<script_id>/delete', methods=['POST'])
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


@scripts_bp.route('/scripts/<script_id>/toggle', methods=['POST'])
def toggle_script(script_id):
    """Enable/disable a script"""
    script = current_app.db.get_page_setup_script(script_id)
    if not script:
        return jsonify({'error': 'Script not found'}), 404

    try:
        script.enabled = not script.enabled
        current_app.db.update_page_setup_script(script)

        return jsonify({
            'success': True,
            'enabled': script.enabled,
            'message': f'Script {"enabled" if script.enabled else "disabled"}'
        })
    except Exception as e:
        logger.error(f"Error toggling script: {e}")
        return jsonify({'error': str(e)}), 500


@scripts_bp.route('/scripts/<script_id>/test', methods=['POST'])
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
