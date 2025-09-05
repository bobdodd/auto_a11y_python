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
            # IDs are in format: testname_ErrorCode, we need just ErrorCode
            issue_id = violation.id if hasattr(violation, 'id') else ''
            if '_' in issue_id:
                # Extract the error code after the test name prefix
                error_code = issue_id.split('_', 1)[1]
            else:
                error_code = issue_id
            
            # Skip if already has enhanced metadata with 'what' field
            # This preserves the metadata replacement done in result_processor.py
            if violation.metadata.get('what'):
                continue
                
            # Get catalog info for this issue as fallback
            catalog_info = IssueCatalog.get_issue(error_code)
            
            # Only update if we got meaningful enriched data
            if catalog_info and catalog_info.get('description') != f"Issue {error_code} needs documentation":
                # Add enriched metadata
                violation.metadata['title'] = catalog_info.get('type', '')
                violation.metadata['what'] = catalog_info['description']
                violation.metadata['why'] = catalog_info['why_it_matters']
                violation.metadata['who'] = catalog_info['who_it_affects']
                violation.metadata['how'] = catalog_info['how_to_fix']
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
    
    # Create test runner
    test_runner_instance = TestRunner(current_app.db, current_app.app_config.__dict__)
    
    # Get AI API key from config (if available)
    # The test_runner will determine if AI should run based on project settings
    ai_key = getattr(current_app.app_config, 'CLAUDE_API_KEY', None)
    
    # Submit test task
    job_id = task_runner.submit_task(
        func=asyncio.run,
        args=(test_runner_instance.test_page(
            page,
            take_screenshot=True,
            run_ai_analysis=None,  # Let test_runner decide based on project config
            ai_api_key=ai_key
        ),),
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