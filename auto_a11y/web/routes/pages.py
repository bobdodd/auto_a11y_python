"""
Page management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from auto_a11y.models import PageStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/<page_id>')
def view_page(page_id):
    """View page details and test results"""
    page = current_app.db.get_page(page_id)
    if not page:
        flash('Page not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    website = current_app.db.get_website(page.website_id)
    project = current_app.db.get_project(website.project_id)
    
    # Get latest test result
    test_result = current_app.db.get_latest_test_result(page_id)
    
    # Get test history
    test_history = current_app.db.get_test_results(page_id=page_id, limit=10)
    
    return render_template('pages/view.html',
                         page=page,
                         website=website,
                         project=project,
                         test_result=test_result,
                         test_history=test_history)


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
    
    # Get AI settings from config
    run_ai = current_app.app_config.RUN_AI_ANALYSIS
    ai_key = current_app.app_config.CLAUDE_API_KEY if run_ai else None
    
    # Submit test task
    job_id = task_runner.submit_task(
        func=asyncio.run,
        args=(test_runner_instance.test_page(
            page,
            take_screenshot=True,
            run_ai_analysis=run_ai,
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