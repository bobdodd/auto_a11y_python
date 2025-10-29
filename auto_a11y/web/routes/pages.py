"""
Page management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
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
            
            # Check if metadata has unfilled placeholders that need fixing
            # This handles old test results stored before placeholder mapping was fixed
            if violation.metadata.get('what'):
                what_text = violation.metadata.get('what', '')
                # Check if it has unfilled contrast placeholders
                if any(placeholder in what_text for placeholder in ['{ratio}', '{fg}', '{bg}']):
                    # Has unfilled placeholders - fix them
                    contrast_ratio = violation.metadata.get('contrastRatio', '')
                    if isinstance(contrast_ratio, str) and contrast_ratio.endswith(':1'):
                        contrast_ratio = contrast_ratio[:-2]

                    # Replace placeholders in all description fields
                    for field in ['what', 'why', 'title', 'full_remediation']:
                        if field in violation.metadata and isinstance(violation.metadata[field], str):
                            text = violation.metadata[field]
                            text = text.replace('{ratio}', str(contrast_ratio))
                            text = text.replace('{fg}', str(violation.metadata.get('textColor', '')))
                            text = text.replace('{bg}', str(violation.metadata.get('backgroundColor', '')))
                            text = text.replace('{fontSize}', str(violation.metadata.get('fontSize', '')))
                            violation.metadata[field] = text
                    # Skip further enrichment since we just fixed the placeholders
                    continue
                else:
                    # Already enriched and placeholders are filled, skip
                    continue

            # Get catalog info for this issue as fallback
            catalog_info = IssueCatalog.get_issue(error_code)
            
            # Only update if we got meaningful enriched data
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                # Add enriched metadata
                violation.metadata['title'] = catalog_info.get('type', '')

                # Get descriptions with placeholders
                what_template = catalog_info['description']
                why_template = catalog_info['why_it_matters']
                how_template = catalog_info['how_to_fix']

                # Fill in placeholders from violation data (for contrast violations)
                placeholder_values = {}
                if hasattr(violation, 'metadata') and violation.metadata:
                    # Extract contrast ratio without ":1" suffix if present
                    contrast_ratio = violation.metadata.get('contrastRatio', '')
                    if isinstance(contrast_ratio, str) and contrast_ratio.endswith(':1'):
                        contrast_ratio = contrast_ratio[:-2]

                    # Convert all values to strings for format()
                    placeholder_values = {
                        'ratio': str(contrast_ratio) if contrast_ratio else '',
                        'fg': str(violation.metadata.get('textColor', '')),
                        'bg': str(violation.metadata.get('backgroundColor', '')),
                        'fontSize': str(violation.metadata.get('fontSize', '')),
                        'breakpoint': str(violation.metadata.get('breakpoint', ''))
                    }

                # Replace placeholders in templates
                try:
                    violation.metadata['what'] = what_template.format(**placeholder_values)
                    violation.metadata['why'] = why_template.format(**placeholder_values)
                    violation.metadata['how'] = how_template.format(**placeholder_values)
                except (KeyError, ValueError):
                    # If placeholder replacement fails, use templates as-is
                    violation.metadata['what'] = what_template
                    violation.metadata['why'] = why_template
                    violation.metadata['how'] = how_template

                violation.metadata['what_generic'] = catalog_info['description']  # Always store generic for grouped headers
                violation.metadata['who'] = catalog_info['who_it_affects']

                # Handle WCAG criteria properly
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
            
            # Skip if already has enhanced metadata with 'what' field
            if warning.metadata.get('what'):
                continue
                
            catalog_info = IssueCatalog.get_issue(error_code)
            
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                warning.metadata['title'] = catalog_info.get('type', '')
                warning.metadata['what'] = catalog_info['description']
                warning.metadata['what_generic'] = catalog_info['description']  # Always store generic for grouped headers
                warning.metadata['why'] = catalog_info['why_it_matters']
                warning.metadata['who'] = catalog_info['who_it_affects']
                warning.metadata['how'] = catalog_info['how_to_fix']
                # Handle WCAG criteria properly
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
            
            # Skip if already has enhanced metadata with 'what' field
            if info.metadata.get('what'):
                continue
                
            catalog_info = IssueCatalog.get_issue(error_code)
            
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                info.metadata['title'] = catalog_info.get('type', '')
                info.metadata['what'] = catalog_info['description']
                info.metadata['what_generic'] = catalog_info['description']  # Always store generic for grouped headers
                info.metadata['why'] = catalog_info['why_it_matters']
                info.metadata['who'] = catalog_info['who_it_affects']
                info.metadata['how'] = catalog_info['how_to_fix']
                # Handle WCAG criteria properly
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
                discovery.metadata['title'] = catalog_info.get('type', '')
                discovery.metadata['what'] = catalog_info['description']
                discovery.metadata['what_generic'] = catalog_info['description']  # Always store generic for grouped headers
                discovery.metadata['why'] = catalog_info['why_it_matters']
                discovery.metadata['who'] = catalog_info['who_it_affects']
                discovery.metadata['how'] = catalog_info['how_to_fix']
                
                # Handle WCAG criteria properly - may be list, string, or N/A
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
    
    # Get test history
    test_history = current_app.db.get_test_results(page_id=page_id, limit=10)
    
    return render_template('pages/view.html',
                         page=page,
                         website=website,
                         project=project,
                         latest_result=test_result,
                         test_history=test_history)


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
                    return await test_runner_instance.test_page(
                        page,
                        take_screenshot=True,
                        run_ai_analysis=None,  # Let test_runner decide based on project config
                        ai_api_key=ai_key
                    )
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
        'message': 'Page queued for testing',
        'job_id': job_id,
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