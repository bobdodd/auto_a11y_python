"""
Page management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_babel import gettext as _, lazy_gettext
from auto_a11y.models import PageStatus
from auto_a11y.reporting.issue_catalog import IssueCatalog
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
pages_bp = Blueprint('pages', __name__)


def enrich_test_result_with_catalog(test_result):
    """Enrich test result issues with catalog metadata"""
    if not test_result:
        return test_result
    
    # Enrich violations
    if hasattr(test_result, 'violations') and test_result.violations:
        for violation in test_result.violations:
            if not hasattr(violation, 'metadata') or not violation.metadata:
                violation.metadata = {}
            
            # Extract the error code from the violation ID
            # IDs can be in formats like:
            # - testname_ErrorCode (e.g., headings_ErrEmptyHeading)
            # - testname_subtest_ErrorCode (e.g., more_links_ErrInvalidGenericLinkName)
            issue_id = violation.id if hasattr(violation, 'id') else ''
            
            # Find the actual error code (starts with Err, Warn, Info, or Disco)
            error_code = issue_id
            if '_' in issue_id:
                parts = issue_id.split('_')
                for i, part in enumerate(parts):
                    if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                        # Found the error code, join from here to end
                        error_code = '_'.join(parts[i:])
                        break
            
            # Always re-enrich to get fresh translations based on current locale
            # (Previously we skipped if metadata existed, but we need to re-enrich
            # to support runtime translation)

            # Get catalog info for this issue as fallback
            catalog_info = IssueCatalog.get_issue(error_code)
            
            # Only update if we got meaningful enriched data
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                # Add enriched metadata - but preserve title if it has specific details
                # (test may provide a short title for accordion and full description for details)
                existing_title = violation.metadata.get('title', '')
                has_specific_title = existing_title and any(pattern in existing_title for pattern in [
                    '".', '"#', 'missing role=', 'missing aria-',
                    'px', ':1', 'alpha=', '°', '%'
                ])

                # Get descriptions with placeholders
                title_template = catalog_info.get('title', '') or catalog_info.get('description', '')
                what_template = catalog_info['description']
                why_template = catalog_info['why_it_matters']
                how_template = catalog_info['how_to_fix']

                # Fill in placeholders from violation data
                placeholder_values = {}
                if hasattr(violation, 'metadata') and violation.metadata:
                    # Include all metadata fields for placeholder substitution
                    for key, value in violation.metadata.items():
                        if value is not None and not isinstance(value, (dict, list)):
                            placeholder_values[key] = str(value)
                    
                    # Extract contrast ratio without ":1" suffix if present
                    contrast_ratio = violation.metadata.get('contrastRatio', '')
                    if isinstance(contrast_ratio, str) and contrast_ratio.endswith(':1'):
                        contrast_ratio = contrast_ratio[:-2]
                    placeholder_values['ratio'] = str(contrast_ratio) if contrast_ratio else ''
                    
                    # Also map common field names for compatibility
                    placeholder_values['fg'] = str(violation.metadata.get('textColor', ''))
                    placeholder_values['bg'] = str(violation.metadata.get('backgroundColor', ''))
                    placeholder_values['fontSize'] = str(violation.metadata.get('fontSize', ''))

                # Replace placeholders in templates
                # But preserve 'what' if it already has specific details (contains identifying patterns)
                existing_what = violation.metadata.get('what', '')
                has_specific_what = any(pattern in existing_what for pattern in [
                    '".', '"#', 'containing', ' element(s)', 'lacks accessibility',
                    'px', ':1', 'alpha=', '°', '%'
                ])
                
                try:
                    # Apply placeholder substitution to title as well
                    if not has_specific_title:
                        violation.metadata['title'] = title_template % placeholder_values
                    # Only overwrite 'what' if it doesn't have specific details already
                    if not has_specific_what:
                        violation.metadata['what'] = what_template % placeholder_values
                    violation.metadata['why'] = why_template % placeholder_values
                    violation.metadata['how'] = how_template % placeholder_values
                except (KeyError, ValueError, TypeError) as e:
                    # If placeholder replacement fails, use templates as-is
                    logger.warning(f"Placeholder substitution failed for {error_code}: {e}, keys available: {list(placeholder_values.keys())}")
                    if not has_specific_title:
                        violation.metadata['title'] = title_template
                    if not has_specific_what:
                        violation.metadata['what'] = what_template
                    violation.metadata['why'] = why_template
                    violation.metadata['how'] = how_template
                
                # Debug: log metadata for ErrSmallText
                if error_code == 'ErrSmallText':
                    logger.warning(f"DEBUG ErrSmallText metadata keys: {list(violation.metadata.keys())}")
                    logger.warning(f"DEBUG ErrSmallText has allInstances: {'allInstances' in violation.metadata}")
                
                violation.metadata['what_generic'] = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
                violation.metadata['who'] = catalog_info['who_it_affects']

                # Handle WCAG criteria properly - use wcag_full for full translated names
                wcag_full_raw = catalog_info.get('wcag_full', '')
                if isinstance(wcag_full_raw, str) and wcag_full_raw and wcag_full_raw != 'N/A':
                    # Split comma-separated string into list
                    violation.metadata['wcag_full'] = [c.strip() for c in wcag_full_raw.split(',') if c.strip()]
                elif isinstance(wcag_full_raw, list):
                    violation.metadata['wcag_full'] = wcag_full_raw
                else:
                    # Fallback to wcag codes if wcag_full not available
                    wcag = catalog_info.get('wcag', [])
                    if isinstance(wcag, list) and wcag:
                        violation.metadata['wcag_full'] = wcag
                    elif isinstance(wcag, str) and wcag != 'N/A':
                        violation.metadata['wcag_full'] = [wcag]
                    else:
                        violation.metadata['wcag_full'] = []
                violation.metadata['full_remediation'] = catalog_info['how_to_fix']
                violation.metadata['impact_detail'] = catalog_info['impact']
    
    # Enrich warnings
    if hasattr(test_result, 'warnings') and test_result.warnings:
        for warning in test_result.warnings:
            if not hasattr(warning, 'metadata') or not warning.metadata:
                warning.metadata = {}
            
            # Extract the error code from the warning ID
            issue_id = warning.id if hasattr(warning, 'id') else ''
            if '_' in issue_id:
                error_code = issue_id.split('_', 1)[1]
            else:
                error_code = issue_id

            # Always re-enrich for translations
            catalog_info = IssueCatalog.get_issue(error_code)
            
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                warning.metadata['title'] = catalog_info.get('title', '') or catalog_info.get('description', '')
                warning.metadata['what'] = catalog_info['description']
                warning.metadata['what_generic'] = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
                warning.metadata['why'] = catalog_info['why_it_matters']
                warning.metadata['who'] = catalog_info['who_it_affects']
                warning.metadata['how'] = catalog_info['how_to_fix']
                # Handle WCAG criteria properly - use wcag_full for full translated names
                wcag_full_raw = catalog_info.get('wcag_full', '')
                if isinstance(wcag_full_raw, str) and wcag_full_raw and wcag_full_raw != 'N/A':
                    warning.metadata['wcag_full'] = [c.strip() for c in wcag_full_raw.split(',') if c.strip()]
                elif isinstance(wcag_full_raw, list):
                    warning.metadata['wcag_full'] = wcag_full_raw
                else:
                    wcag = catalog_info.get('wcag', [])
                    if isinstance(wcag, list) and wcag:
                        warning.metadata['wcag_full'] = wcag
                    elif isinstance(wcag, str) and wcag != 'N/A':
                        warning.metadata['wcag_full'] = [wcag]
                    else:
                        warning.metadata['wcag_full'] = []
                warning.metadata['full_remediation'] = catalog_info['how_to_fix']
                warning.metadata['impact_detail'] = catalog_info['impact']
    
    # Enrich info items
    if hasattr(test_result, 'info') and test_result.info:
        for info in test_result.info:
            if not hasattr(info, 'metadata') or not info.metadata:
                info.metadata = {}
            
            # Extract the error code from the info ID
            issue_id = info.id if hasattr(info, 'id') else ''
            if '_' in issue_id:
                error_code = issue_id.split('_', 1)[1]
            else:
                error_code = issue_id

            # Always re-enrich for translations
            catalog_info = IssueCatalog.get_issue(error_code)
            
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                info.metadata['title'] = catalog_info.get('title', '') or catalog_info.get('description', '')
                info.metadata['what'] = catalog_info['description']
                info.metadata['what_generic'] = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
                info.metadata['why'] = catalog_info['why_it_matters']
                info.metadata['who'] = catalog_info['who_it_affects']
                info.metadata['how'] = catalog_info['how_to_fix']
                # Handle WCAG criteria properly - use wcag_full for full translated names
                wcag_full_raw = catalog_info.get('wcag_full', '')
                if isinstance(wcag_full_raw, str) and wcag_full_raw and wcag_full_raw != 'N/A':
                    info.metadata['wcag_full'] = [c.strip() for c in wcag_full_raw.split(',') if c.strip()]
                elif isinstance(wcag_full_raw, list):
                    info.metadata['wcag_full'] = wcag_full_raw
                else:
                    wcag = catalog_info.get('wcag', [])
                    if isinstance(wcag, list) and wcag:
                        info.metadata['wcag_full'] = wcag
                    elif isinstance(wcag, str) and wcag != 'N/A':
                        info.metadata['wcag_full'] = [wcag]
                    else:
                        info.metadata['wcag_full'] = []
                info.metadata['full_remediation'] = catalog_info['how_to_fix']
                info.metadata['impact_detail'] = catalog_info['impact']
    
    # Enrich discovery items
    if hasattr(test_result, 'discovery') and test_result.discovery:
        for discovery in test_result.discovery:
            if not hasattr(discovery, 'metadata') or not discovery.metadata:
                discovery.metadata = {}
            
            # Extract the error code from the discovery ID
            issue_id = discovery.id if hasattr(discovery, 'id') else ''
            if '_' in issue_id:
                error_code = issue_id.split('_', 1)[1]
            else:
                error_code = issue_id
            
            # Skip if already has enhanced metadata with 'what' field
            if discovery.metadata.get('what'):
                continue
                
            logger.debug(f"Looking up discovery issue: {error_code} (from ID: {issue_id})")
            catalog_info = IssueCatalog.get_issue(error_code)
            
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                discovery.metadata['title'] = catalog_info.get('title', '') or catalog_info.get('description', '')
                discovery.metadata['what'] = catalog_info['description']
                discovery.metadata['what_generic'] = catalog_info.get('what_generic') or catalog_info.get('description_generic') or catalog_info['description']
                discovery.metadata['why'] = catalog_info['why_it_matters']
                discovery.metadata['who'] = catalog_info['who_it_affects']
                discovery.metadata['how'] = catalog_info['how_to_fix']

                # Handle WCAG criteria properly - use wcag_full for full translated names
                wcag_full_raw = catalog_info.get('wcag_full', '')
                if isinstance(wcag_full_raw, str) and wcag_full_raw and wcag_full_raw != 'N/A':
                    discovery.metadata['wcag_full'] = [c.strip() for c in wcag_full_raw.split(',') if c.strip()]
                elif isinstance(wcag_full_raw, list):
                    discovery.metadata['wcag_full'] = wcag_full_raw
                else:
                    wcag = catalog_info.get('wcag', [])
                    if isinstance(wcag, list) and wcag:
                        discovery.metadata['wcag_full'] = wcag
                    elif isinstance(wcag, str) and wcag != 'N/A':
                        discovery.metadata['wcag_full'] = [wcag]
                    else:
                        discovery.metadata['wcag_full'] = []

                discovery.metadata['full_remediation'] = catalog_info['how_to_fix']
                discovery.metadata['impact_detail'] = catalog_info['impact']
                logger.debug(f"Enriched discovery item with catalog data: {discovery.metadata.get('title')}")
    
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
        'document_links': lazy_gettext('Documents'),
        'documents': lazy_gettext('Documents'),
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