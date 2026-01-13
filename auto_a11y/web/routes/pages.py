"""
Page management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_babel import gettext as _, lazy_gettext, force_locale
from auto_a11y.models import PageStatus
from auto_a11y.reporting.issue_catalog import IssueCatalog
from auto_a11y.reporting.wcag_mapper import enrich_wcag_criteria
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)
pages_bp = Blueprint('pages', __name__)


def enrich_test_result_with_catalog(test_result):
    """Enrich test result issues with catalog metadata"""
    if not test_result:
        return test_result
    
    # Helper to substitute {placeholder} style placeholders
    def substitute_placeholders(template, values):
        """Replace {key} placeholders in template with values from dict."""
        if not template or not values:
            return template
        
        def replace_match(match):
            key = match.group(1)
            return str(values.get(key, match.group(0)))
        
        return re.sub(r'\{([^}]+)\}', replace_match, template)

    def enrich_issue_bilingual(issue):
        """
        Enrich an issue with bilingual metadata (EN and FR).
        Follows the same pattern as static_html_generator.py for consistency.

        Args:
            issue: Issue object with id, description, metadata attributes

        Returns:
            The same issue object with enriched bilingual metadata fields
        """
        # Extract error code from issue ID
        issue_id = issue.id if hasattr(issue, 'id') else ''
        error_code = issue_id
        if '_' in issue_id:
            parts = issue_id.split('_')
            for i, part in enumerate(parts):
                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                    error_code = '_'.join(parts[i:])
                    break

        # Ensure issue has metadata dict
        if not hasattr(issue, 'metadata') or not issue.metadata:
            issue.metadata = {}

        # Build issue dict for IssueCatalog.enrich_issue()
        issue_dict = {
            'id': issue_id,
            'description': issue.description if hasattr(issue, 'description') else '',
            'impact': issue.impact if hasattr(issue, 'impact') else 'moderate',
            'xpath': issue.xpath if hasattr(issue, 'xpath') else '',
            'html_snippet': issue.html if hasattr(issue, 'html') else '',
            'touchpoint': issue.touchpoint if hasattr(issue, 'touchpoint') else '',
            'failure_summary': issue.failure_summary if hasattr(issue, 'failure_summary') else '',
            'metadata': {}
        }

        # Copy metadata if present
        if hasattr(issue, 'metadata') and issue.metadata:
            issue_dict['metadata'] = dict(issue.metadata)

        # Enrich with IssueCatalog in both languages (same as static generator)
        with force_locale('en'):
            enriched_en = IssueCatalog.enrich_issue(issue_dict.copy())

        with force_locale('fr'):
            enriched_fr = IssueCatalog.enrich_issue(issue_dict.copy())

        # Store bilingual metadata fields (same as static generator)
        issue.metadata['what_en'] = enriched_en.get('description_full', enriched_en.get('description', ''))
        issue.metadata['what_fr'] = enriched_fr.get('description_full', enriched_fr.get('description', ''))
        issue.metadata['what_generic_en'] = enriched_en.get('what_generic', enriched_en.get('description', ''))
        issue.metadata['what_generic_fr'] = enriched_fr.get('what_generic', enriched_fr.get('description', ''))
        issue.metadata['why_en'] = enriched_en.get('why_it_matters', '')
        issue.metadata['why_fr'] = enriched_fr.get('why_it_matters', '')
        issue.metadata['who_en'] = enriched_en.get('who_it_affects', '')
        issue.metadata['who_fr'] = enriched_fr.get('who_it_affects', '')
        issue.metadata['full_remediation_en'] = enriched_en.get('how_to_fix', '')
        issue.metadata['full_remediation_fr'] = enriched_fr.get('how_to_fix', '')

        # Set backward-compatible single-language fields (default to EN)
        issue.metadata['what'] = issue.metadata['what_en']
        issue.metadata['what_generic'] = issue.metadata['what_generic_en']
        issue.metadata['why'] = issue.metadata['why_en']
        issue.metadata['who'] = issue.metadata['who_en']
        issue.metadata['how'] = issue.metadata['full_remediation_en']
        issue.metadata['full_remediation'] = issue.metadata['full_remediation_en']

        # Handle WCAG criteria
        wcag_full_raw = enriched_en.get('wcag_full', '')
        if isinstance(wcag_full_raw, str) and wcag_full_raw:
            issue.metadata['wcag_full'] = [c.strip() for c in wcag_full_raw.split(',') if c.strip()]
        elif isinstance(wcag_full_raw, list):
            issue.metadata['wcag_full'] = wcag_full_raw
        else:
            issue.metadata['wcag_full'] = []

        # Store impact detail
        issue.metadata['impact_detail'] = enriched_en.get('impact', '')

        return issue

    # Enrich violations - use bilingual enrichment pattern
    if hasattr(test_result, 'violations') and test_result.violations:
        for violation in test_result.violations:
            enrich_issue_bilingual(violation)

    # Enrich warnings - use bilingual enrichment pattern
    if hasattr(test_result, 'warnings') and test_result.warnings:
        for warning in test_result.warnings:
            enrich_issue_bilingual(warning)

    # Enrich info items - use bilingual enrichment pattern
    if hasattr(test_result, 'info') and test_result.info:
        for info in test_result.info:
            enrich_issue_bilingual(info)

    # Enrich discovery items - use bilingual enrichment pattern
    if hasattr(test_result, 'discovery') and test_result.discovery:
        for discovery in test_result.discovery:
            enrich_issue_bilingual(discovery)

    return test_result


@pages_bp.route('/<page_id>')
def view_page(page_id):
    """View page details and test results"""
    page = current_app.db.get_page(page_id)
    if not page:
        flash('Page not found', 'error')
        return redirect(url_for('projects.list_projects'))

    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id)

    # Get latest test result and enrich with catalog data
    test_result = current_app.db.get_latest_test_result(page_id)
    test_result = enrich_test_result_with_catalog(test_result)

    # Check if this is multi-state testing (has session_id and related results)
    state_results = []
    selected_state_index = 0  # Default to first state
    if test_result and test_result.session_id:
        # Get all results for this session
        all_session_results = current_app.db.get_test_results_by_session(test_result.session_id)
        # Filter to only include results for THIS page (session may span multiple pages)
        page_session_results = [r for r in all_session_results if r.page_id == page_id]
        # Enrich each one with catalog data
        state_results = [enrich_test_result_with_catalog(r) for r in page_session_results]
        # Sort by state_sequence to ensure proper order
        state_results.sort(key=lambda r: r.state_sequence if hasattr(r, 'state_sequence') else 0)

        # Check if user selected a specific state via query parameter
        selected_state = request.args.get('state', type=int)
        if selected_state is not None and 0 <= selected_state < len(state_results):
            selected_state_index = selected_state
            # Use the selected state as the main result to display
            test_result = state_results[selected_state]

    # Calculate accessibility score
    score_data = None
    compliance_score = None
    if test_result:
        from auto_a11y.testing.result_processor import ResultProcessor
        processor = ResultProcessor()
        score_data = processor.calculate_score(test_result)

        # Calculate compliance score (tests with zero violations)
        # Get unique test codes that have violations/warnings
        failed_test_codes = set()

        # Extract test codes from violations (structure: dict with 'id' key)
        for v in test_result.violations:
            test_code = v.get('id', '') if isinstance(v, dict) else (v.id if hasattr(v, 'id') else '')
            if test_code:
                # Extract base code (before underscore if present)
                base_code = test_code.split('_')[0] if '_' in test_code else test_code
                failed_test_codes.add(base_code)

        # Extract test codes from warnings
        for w in test_result.warnings:
            test_code = w.get('id', '') if isinstance(w, dict) else (w.id if hasattr(w, 'id') else '')
            if test_code:
                base_code = test_code.split('_')[0] if '_' in test_code else test_code
                failed_test_codes.add(base_code)

        # Count total tests run from metadata
        total_tests = test_result.metadata.get('test_count', 0) if hasattr(test_result, 'metadata') and test_result.metadata else 0
        failed_tests = len(failed_test_codes)
        passed_tests = max(0, total_tests - failed_tests)

        compliance_score = {
            'score': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_tests': total_tests
        }

    # Get test history
    test_history = current_app.db.get_test_results(page_id=page_id, limit=10)

    # Get available test users for this website/project
    # Fetch both website-specific users AND project-level users
    website_users = current_app.db.get_website_users(page.website_id, enabled_only=True)
    project_users = current_app.db.get_project_users(project.id, enabled_only=True)
    # Combine both lists (project users have priority as they can be used across websites)
    all_users = list(project_users) + list(website_users)
    website_users = all_users  # Use combined list for template

    # Touchpoint display names (translated)
    # Match actual touchpoint keys used in test results
    touchpoint_names = {
        'accessible_names': lazy_gettext('Accessible Names'),
        'animation': lazy_gettext('Animation'),
        'aria': lazy_gettext('ARIA'),
        'buttons': lazy_gettext('Buttons'),
        'colors': lazy_gettext('Colors & Contrast'),
        'colors_contrast': lazy_gettext('Colors & Contrast'),  # Legacy key
        'dialogs': lazy_gettext('Dialogs & Modals'),
        'document_links': lazy_gettext('Electronic Documents'),
        'documents': lazy_gettext('Electronic Documents'),
        'electronic_documents': lazy_gettext('Electronic Documents'),
        'event_handlers': lazy_gettext('Event Handling'),
        'event_handling': lazy_gettext('Event Handling'),
        'floating_dialogs': lazy_gettext('Dialogs & Modals'),
        'focus_management': lazy_gettext('Focus Management'),
        'fonts': lazy_gettext('Fonts'),
        'forms': lazy_gettext('Forms'),
        'headings': lazy_gettext('Headings'),
        'iframes': lazy_gettext('Iframes'),
        'images': lazy_gettext('Images'),
        'keyboard_navigation': lazy_gettext('Keyboard Navigation'),
        'landmarks': lazy_gettext('Landmarks'),
        'language': lazy_gettext('Language'),
        'links': lazy_gettext('Links'),
        'list': lazy_gettext('Lists'),
        'lists': lazy_gettext('Lists'),
        'maps': lazy_gettext('Maps'),
        'media': lazy_gettext('Media'),
        'modals': lazy_gettext('Dialogs & Modals'),
        'navigation': lazy_gettext('Navigation'),
        'page': lazy_gettext('Page'),
        'page_state': lazy_gettext('Page State'),
        'reading_order': lazy_gettext('Reading Order'),
        'responsive': lazy_gettext('Responsive Design'),
        'semantic_structure': lazy_gettext('Semantic Structure'),
        'styles': lazy_gettext('Inline Styles'),
        'tabindex': lazy_gettext('Keyboard Navigation'),
        'tables': lazy_gettext('Tables'),
        'timers': lazy_gettext('Timing'),
        'timing': lazy_gettext('Timing'),
        'title_attributes': lazy_gettext('Title Attributes'),
        'video': lazy_gettext('Media'),
        'other': lazy_gettext('Other')
    }

    return render_template('pages/view.html',
                         page=page,
                         website=website,
                         project=project,
                         latest_result=test_result,
                         state_results=state_results,  # NEW: Multi-state results
                         selected_state_index=selected_state_index,  # NEW: Currently selected state
                         score_data=score_data,
                         compliance_score=compliance_score,
                         test_history=test_history,
                         website_users=website_users,
                         touchpoint_names=touchpoint_names)


@pages_bp.route('/<page_id>/edit', methods=['GET', 'POST'])
def edit_page(page_id):
    """Edit page details"""
    page = current_app.db.get_page(page_id)
    if not page:
        flash('Page not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id)
    
    if request.method == 'POST':
        # Update page details
        page.title = request.form.get('title', page.title)
        page.priority = request.form.get('priority', page.priority)
        page.notes = request.form.get('notes', page.notes)
        
        if current_app.db.update_page(page):
            flash('Page updated successfully', 'success')
            return redirect(url_for('pages.view_page', page_id=page_id))
        else:
            flash('Failed to update page', 'error')
    
    return render_template('pages/edit.html',
                         page=page,
                         website=website,
                         project=project)


@pages_bp.route('/<page_id>/test', methods=['POST'])
def test_page(page_id):
    """Run accessibility test on page"""
    from auto_a11y.testing import TestRunner
    from auto_a11y.core.task_runner import task_runner
    import asyncio

    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404

    # Check if multi-state testing requested
    data = request.get_json() if request.is_json else {}
    enable_multi_state = data.get('enable_multi_state', True)  # Default: enabled
    website_user_id = data.get('website_user_id')  # Optional authenticated user

    # Update page status
    page.status = PageStatus.QUEUED
    current_app.db.update_page(page)

    # Get project config to apply project-specific browser settings
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id) if website else None

    # Create browser config with project-specific settings
    browser_config = current_app.app_config.__dict__.copy()
    if project and project.config:
        browser_config['stealth_mode'] = project.config.get('stealth_mode', False)

        # Apply project-specific headless browser setting
        headless_setting = project.config.get('headless_browser', 'true')
        browser_config['BROWSER_HEADLESS'] = (headless_setting == 'true')

    # Get AI API key from config (if available)
    ai_key = getattr(current_app.app_config, 'CLAUDE_API_KEY', None)

    # Store references needed in async context
    db = current_app.db

    # Define sync wrapper that creates a clean event loop
    def run_test_sync():
        # Create a fresh event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Define async function inside the new loop context
            async def run_test_with_cleanup():
                # Create test runner inside the async context with new event loop
                test_runner_instance = TestRunner(db, browser_config)
                try:
                    # Use multi-state testing if enabled
                    if enable_multi_state:
                        results = await test_runner_instance.test_page_multi_state(
                            page,
                            enable_multi_state=True,
                            take_screenshot=True,
                            run_ai_analysis=None,  # Let test_runner decide based on project config
                            ai_api_key=ai_key,
                            website_user_id=website_user_id
                        )
                        # Return list of results
                        return results
                    else:
                        # Single-state testing (backward compatible)
                        result = await test_runner_instance.test_page(
                            page,
                            take_screenshot=True,
                            run_ai_analysis=None,
                            ai_api_key=ai_key,
                            website_user_id=website_user_id
                        )
                        return [result]  # Wrap in list for consistency
                finally:
                    await test_runner_instance.cleanup()

            # Run the async function in the new loop
            return loop.run_until_complete(run_test_with_cleanup())
        finally:
            loop.close()

    # Submit test task
    job_id = task_runner.submit_task(
        func=run_test_sync,
        args=(),
        task_id=f'test_page_{page_id}_{datetime.now().timestamp()}'
    )

    return jsonify({
        'success': True,
        'message': 'Page queued for testing' + (' (multi-state enabled)' if enable_multi_state else ''),
        'job_id': job_id,
        'multi_state': enable_multi_state,
        'status_url': url_for('pages.test_status', page_id=page_id)
    })


@pages_bp.route('/<page_id>/test-status')
def test_status(page_id):
    """Check test job status"""
    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    return jsonify({
        'status': page.status.value,
        'message': f'Page is {page.status.value}'
    })


@pages_bp.route('/<page_id>/cancel-test', methods=['POST'])
def cancel_test(page_id):
    """Cancel a queued or running page test"""
    from auto_a11y.core.task_runner import task_runner
    
    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    # Check if page is actually queued or testing
    if page.status not in [PageStatus.QUEUED, PageStatus.TESTING]:
        return jsonify({
            'success': False,
            'message': f'Page is not being tested (status: {page.status.value})'
        })
    
    # Try to cancel the task
    job_id = request.form.get('job_id')
    
    # Look for task by pattern if no job_id provided
    if not job_id:
        # Look for any active task for this page
        task_pattern = f'test_page_{page_id}_'
        active_tasks = task_runner.get_active_tasks()
        
        for task_id in active_tasks:
            if task_id.startswith(task_pattern):
                job_id = task_id
                break
    
    cancelled = False
    if job_id:
        try:
            cancelled = task_runner.cancel_task(job_id)
            logger.info(f"Task cancellation attempt for {job_id}: {cancelled}")
        except Exception as e:
            logger.error(f"Error cancelling task {job_id}: {e}")
    
    # Update page status back to discovered/tested based on history
    if cancelled or page.status == PageStatus.QUEUED:
        # Check if page has been tested before
        test_history = current_app.db.get_test_results(page_id=page_id, limit=1)
        if test_history:
            page.status = PageStatus.TESTED
        else:
            page.status = PageStatus.DISCOVERED
        
        current_app.db.update_page(page)
        
        return jsonify({
            'success': True,
            'message': 'Test cancelled successfully',
            'new_status': page.status.value
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Could not cancel test - it may have already started'
        })


@pages_bp.route('/<page_id>/delete', methods=['POST'])
def delete_page(page_id):
    """Delete page"""
    page = current_app.db.get_page(page_id)
    if not page:
        flash('Page not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    website_id = page.website_id
    
    if current_app.db.delete_page(page_id):
        flash(f'Page deleted successfully', 'success')
    else:
        flash('Failed to delete page', 'error')
    
    return redirect(url_for('websites.view_website', website_id=website_id))


@pages_bp.route('/<page_id>/violations')
def view_violations(page_id):
    """View detailed violations for page"""
    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404

    test_result = current_app.db.get_latest_test_result(page_id)
    if not test_result:
        return jsonify({'error': 'No test results found'}), 404

    return render_template('pages/violations.html',
                         page=page,
                         test_result=test_result)


@pages_bp.route('/<page_id>/matrix', methods=['GET', 'POST'])
def configure_test_matrix(page_id):
    """Configure test state matrix for page"""
    from auto_a11y.models import TestStateMatrix, ScriptStateDefinition

    page = current_app.db.get_page(page_id)
    if not page:
        flash(_('Page not found'), 'error')
        return redirect(url_for('projects.list_projects'))

    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id)

    # Get all scripts for this page (page-level and website-level)
    all_scripts = current_app.db.get_scripts_for_page_v2(
        page_id=page_id,
        website_id=page.website_id,
        enabled_only=False
    )

    # Filter to only enabled scripts with multi-state testing
    testable_scripts = [
        s for s in all_scripts
        if s.enabled and (s.test_before_execution or s.test_after_execution)
    ]

    if request.method == 'POST':
        try:
            # Get or create matrix
            matrix = current_app.db.get_test_state_matrix_by_page(page_id)

            if not matrix:
                # Create new matrix
                matrix = TestStateMatrix(
                    page_id=page_id,
                    website_id=page.website_id
                )

            # Update scripts in matrix
            matrix.scripts = []
            for script in testable_scripts:
                script_def = ScriptStateDefinition(
                    script_id=script.id,
                    script_name=script.name,
                    test_before=script.test_before_execution,
                    test_after=script.test_after_execution,
                    execution_order=len(matrix.scripts)  # Assign order based on position
                )
                matrix.scripts.append(script_def)

            # Parse combinations data from form (simple list format)
            combinations_data = request.form.get('combinations_data')
            if combinations_data:
                import json
                matrix.combinations = json.loads(combinations_data)
                matrix.matrix = {}  # Clear legacy matrix format
            else:
                matrix.initialize_matrix()

            # Parse script order from form
            script_order_data = request.form.get('script_order')
            if script_order_data:
                import json
                script_order = json.loads(script_order_data)
                order_map = {item['script_id']: item['execution_order'] for item in script_order}
                for script_def in matrix.scripts:
                    if script_def.script_id in order_map:
                        script_def.execution_order = order_map[script_def.script_id]
                # Sort scripts by execution order
                matrix.scripts.sort(key=lambda s: s.execution_order)

            # Save or update matrix
            if matrix._id:
                current_app.db.update_test_state_matrix(matrix)
                flash(_('Test matrix updated successfully'), 'success')
            else:
                current_app.db.create_test_state_matrix(matrix)
                flash(_('Test matrix created successfully'), 'success')

            return redirect(url_for('pages.configure_test_matrix', page_id=page_id))

        except Exception as e:
            logger.error(f"Error saving test matrix: {e}")
            flash(_('Failed to save test matrix: %(error)s', error=str(e)), 'error')

    # GET request - load existing matrix or create default
    matrix = current_app.db.get_test_state_matrix_by_page(page_id)

    if not matrix:
        # Create default matrix for display
        matrix = TestStateMatrix(
            page_id=page_id,
            website_id=page.website_id
        )

        # Add testable scripts to matrix
        for script in testable_scripts:
            script_def = ScriptStateDefinition(
                script_id=script.id,
                script_name=script.name,
                test_before=script.test_before_execution,
                test_after=script.test_after_execution,
                execution_order=len(matrix.scripts)
            )
            matrix.scripts.append(script_def)

        # Initialize with defaults
        if matrix.scripts:
            matrix.initialize_matrix()

    enabled_combinations = matrix.get_enabled_combinations() if matrix.scripts else []

    return render_template('pages/test_matrix_v2.html',
                         page=page,
                         website=website,
                         project=project,
                         matrix=matrix,
                         testable_scripts=testable_scripts,
                         enabled_count=len(enabled_combinations))