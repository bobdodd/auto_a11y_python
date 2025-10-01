"""
Testing and analysis routes
"""

from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from auto_a11y.models import PageStatus
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
testing_bp = Blueprint('testing', __name__)


@testing_bp.route('/result/<result_id>')
def view_result(result_id):
    """View individual test result details"""
    result = current_app.db.get_test_result(result_id)
    if not result:
        return jsonify({'error': 'Test result not found'}), 404
    
    # Get related page and website info
    page = current_app.db.get_page(result.page_id)
    website = current_app.db.get_website(page.website_id) if page else None
    project = current_app.db.get_project(website.project_id) if website else None
    
    return render_template('testing/result.html',
                         result=result,
                         page=page,
                         website=website,
                         project=project)


@testing_bp.route('/dashboard')
def testing_dashboard():
    """Testing dashboard showing active jobs"""
    # Get testing statistics
    stats = {
        'active_tests': 0,  # Would come from job queue
        'queued_tests': 0,
        'completed_today': current_app.db.test_results.count_documents({
            'test_date': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
        }),
        'failed_tests': 0
    }
    
    # Get recent test results
    recent_results = current_app.db.get_test_results(limit=20)
    
    return render_template('testing/dashboard.html',
                         stats=stats,
                         recent_results=recent_results)


@testing_bp.route('/run-test', methods=['POST'])
def run_test():
    """Run accessibility test on specified page(s)"""
    data = request.get_json()
    
    page_ids = data.get('page_ids', [])
    test_config = data.get('config', {})
    
    if not page_ids:
        return jsonify({'error': 'No pages specified'}), 400
    
    # Validate pages exist
    valid_pages = []
    for page_id in page_ids:
        page = current_app.db.get_page(page_id)
        if page:
            valid_pages.append(page)
    
    if not valid_pages:
        return jsonify({'error': 'No valid pages found'}), 400
    
    # Queue test jobs
    job_ids = []
    for page in valid_pages:
        job_id = f'test_{page.id}_{datetime.now().timestamp()}'
        job_ids.append(job_id)
        
        # Update page status
        page.status = PageStatus.QUEUED
        current_app.db.update_page(page)
    
    return jsonify({
        'success': True,
        'jobs_created': len(job_ids),
        'job_ids': job_ids,
        'message': f'Queued {len(job_ids)} pages for testing'
    })


@testing_bp.route('/batch-test', methods=['POST'])
def batch_test():
    """Run batch testing on multiple pages"""
    data = request.get_json()
    
    website_id = data.get('website_id')
    filter_criteria = data.get('filter', {})
    test_config = data.get('config', {})
    
    if not website_id:
        return jsonify({'error': 'Website ID required'}), 400
    
    # Get pages based on filter
    pages = current_app.db.get_pages(website_id)
    
    # Apply filters
    if filter_criteria.get('untested_only'):
        pages = [p for p in pages if p.needs_testing]
    
    if filter_criteria.get('priority'):
        priority = filter_criteria['priority']
        pages = [p for p in pages if p.priority == priority]
    
    if not pages:
        return jsonify({'error': 'No pages match criteria'}), 404
    
    # Queue batch job
    batch_id = f'batch_{website_id}_{datetime.now().timestamp()}'
    
    return jsonify({
        'success': True,
        'batch_id': batch_id,
        'pages_queued': len(pages),
        'message': f'Batch testing started for {len(pages)} pages'
    })


@testing_bp.route('/job/<job_id>/status')
def job_status(job_id):
    """Get status of testing job"""
    # In production, check actual job queue
    return jsonify({
        'job_id': job_id,
        'status': 'in_progress',
        'progress': 45,
        'current_page': 'https://example.com/page',
        'pages_completed': 5,
        'pages_total': 10,
        'violations_found': 23
    })


@testing_bp.route('/job/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel testing job"""
    # In production, cancel actual job
    return jsonify({
        'success': True,
        'message': f'Job {job_id} cancelled'
    })


@testing_bp.route('/fixture-status')
def fixture_status():
    """Display fixture test status page"""
    return render_template('testing/fixture_status.html')


@testing_bp.route('/configure', methods=['GET', 'POST'])
def configure_testing():
    """Configure testing settings"""
    if request.method == 'POST':
        # Save testing configuration
        config = request.get_json()

        # Validate configuration
        if not config:
            return jsonify({'error': 'Invalid configuration'}), 400

        # Update runtime configuration
        if 'parallel_tests' in config:
            current_app.app_config.PARALLEL_TESTS = config['parallel_tests']
        if 'test_timeout' in config:
            current_app.app_config.TEST_TIMEOUT = config['test_timeout']
        if 'run_ai_analysis' in config:
            current_app.app_config.RUN_AI_ANALYSIS = config['run_ai_analysis']
        if 'browser_headless' in config:
            current_app.app_config.BROWSER_HEADLESS = config['browser_headless']
        if 'viewport_width' in config:
            current_app.app_config.BROWSER_VIEWPORT_WIDTH = config['viewport_width']
        if 'viewport_height' in config:
            current_app.app_config.BROWSER_VIEWPORT_HEIGHT = config['viewport_height']
        if 'pages_per_page' in config:
            current_app.app_config.PAGES_PER_PAGE = config['pages_per_page']
        if 'max_pages_per_page' in config:
            current_app.app_config.MAX_PAGES_PER_PAGE = config['max_pages_per_page']

        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully (applies to new operations)'
        })

    # Get current configuration with backward compatibility
    current_config = {
        'parallel_tests': current_app.app_config.PARALLEL_TESTS,
        'test_timeout': current_app.app_config.TEST_TIMEOUT,
        'run_ai_analysis': current_app.app_config.RUN_AI_ANALYSIS,
        'browser_headless': current_app.app_config.BROWSER_HEADLESS,
        'viewport_width': current_app.app_config.BROWSER_VIEWPORT_WIDTH,
        'viewport_height': current_app.app_config.BROWSER_VIEWPORT_HEIGHT,
        'pages_per_page': getattr(current_app.app_config, 'PAGES_PER_PAGE', 100),
        'max_pages_per_page': getattr(current_app.app_config, 'MAX_PAGES_PER_PAGE', 500)
    }

    return render_template('testing/configure.html', config=current_config)