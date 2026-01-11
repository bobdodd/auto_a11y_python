"""
Testing and analysis routes
"""

from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required
from auto_a11y.models import PageStatus
from auto_a11y.core.job_manager import JobType, JobStatus
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
testing_bp = Blueprint('testing', __name__)


def calculate_aggregate_stats(db):
    """Calculate aggregate statistics across all projects"""
    projects = db.get_all_projects()

    total_pages = 0
    tested_pages = 0
    total_violations = 0
    total_warnings = 0
    website_count = 0

    for project in projects:
        stats = db.get_project_stats(project.id)
        total_pages += stats.get('total_pages', 0)
        tested_pages += stats.get('tested_pages', 0)
        total_violations += stats.get('total_violations', 0)
        total_warnings += stats.get('total_warnings', 0)
        website_count += stats.get('website_count', 0)

    return {
        'website_count': website_count,
        'total_pages': total_pages,
        'tested_pages': tested_pages,
        'untested_pages': total_pages - tested_pages,
        'total_violations': total_violations,
        'total_warnings': total_warnings,
        'test_coverage': (tested_pages / total_pages * 100) if total_pages > 0 else 0
    }


def get_recent_results_with_context(db, project_id=None, website_id=None, limit=20):
    """Get recent test results with full page/website/project context.

    Optimized to minimize database queries by:
    1. Pre-loading all needed pages, websites, projects in bulk
    2. Using in-memory lookups instead of individual queries
    """
    # Get results from database first
    results = db.get_test_results(limit=limit * 2)  # Get extra to account for filtering

    if not results:
        return []

    # Collect all unique page IDs from results
    page_ids = list(set(r.page_id for r in results if r.page_id))

    if not page_ids:
        return []

    # Bulk load all pages we need (single query)
    pages_map = {}
    for page_id in page_ids:
        page = db.get_page(page_id)
        if page:
            pages_map[page_id] = page

    # Collect website IDs from pages
    website_ids = list(set(p.website_id for p in pages_map.values() if p.website_id))

    # Bulk load all websites (could optimize further with a bulk query method)
    websites_map = {}
    for ws_id in website_ids:
        ws = db.get_website(ws_id)
        if ws:
            websites_map[ws_id] = ws

    # Collect project IDs from websites
    project_ids = list(set(w.project_id for w in websites_map.values() if w.project_id))

    # Bulk load all projects
    projects_map = {}
    for proj_id in project_ids:
        proj = db.get_project(proj_id)
        if proj:
            projects_map[proj_id] = proj

    # Now filter results based on project_id/website_id if specified
    filtered_results = []
    for result in results:
        page = pages_map.get(result.page_id)
        if not page:
            continue

        website = websites_map.get(page.website_id)
        if not website:
            continue

        project = projects_map.get(website.project_id) if website.project_id else None

        # Apply filters
        if website_id and page.website_id != website_id:
            continue
        if project_id and (not website.project_id or website.project_id != project_id):
            continue

        filtered_results.append({
            'result': result,
            'page': page,
            'website': website,
            'project': project
        })

        if len(filtered_results) >= limit:
            break

    return filtered_results


def get_trend_data(db, project_id=None, website_id=None, days=30):
    """Get trend data for violations/warnings over time"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Initialize daily buckets
    trend_data = []
    current_date = start_date
    while current_date <= end_date:
        trend_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'violations': 0,
            'warnings': 0,
            'tests': 0
        })
        current_date += timedelta(days=1)

    # Get test results for the period (limit based on days to reduce load)
    results = db.get_test_results(limit=min(days * 20, 500))

    # Filter by date range and optionally by project/website
    page_ids = None
    if website_id:
        pages = db.get_pages(website_id)
        page_ids = set(p.id for p in pages)
    elif project_id:
        websites = db.get_websites(project_id)
        page_ids = set()
        for website in websites:
            pages = db.get_pages(website.id)
            page_ids.update(p.id for p in pages)

    # Aggregate by day
    date_to_index = {d['date']: i for i, d in enumerate(trend_data)}

    for result in results:
        if result.test_date < start_date:
            continue
        if page_ids and result.page_id not in page_ids:
            continue

        date_str = result.test_date.strftime('%Y-%m-%d')
        if date_str in date_to_index:
            idx = date_to_index[date_str]
            trend_data[idx]['violations'] += result.violation_count
            trend_data[idx]['warnings'] += result.warning_count
            trend_data[idx]['tests'] += 1

    return trend_data


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
@login_required
def testing_dashboard():
    """Testing dashboard - comprehensive testing control center"""
    db = current_app.db

    # Get filter parameters from URL
    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')

    # Get all projects for dropdown
    projects = db.get_all_projects()

    # Get selected project and its websites (if any)
    selected_project = None
    websites = []
    if project_id:
        selected_project = db.get_project(project_id)
        if selected_project:
            websites = db.get_websites(project_id)

    # Get selected website (if any)
    selected_website = None
    if website_id:
        selected_website = db.get_website(website_id)

    # Calculate stats (aggregate or project/website-specific)
    if website_id and selected_website:
        # Stats for single website
        pages = db.get_pages(website_id)
        tested_pages = sum(1 for p in pages if p.status == PageStatus.TESTED)
        stats = {
            'website_count': 1,
            'total_pages': len(pages),
            'tested_pages': tested_pages,
            'untested_pages': len(pages) - tested_pages,
            'total_violations': sum(p.violation_count for p in pages),
            'total_warnings': sum(p.warning_count for p in pages),
            'test_coverage': (tested_pages / len(pages) * 100) if pages else 0
        }
    elif project_id and selected_project:
        stats = db.get_project_stats(project_id)
    else:
        stats = calculate_aggregate_stats(db)

    # Get completed today count
    completed_today = db.test_results.count_documents({
        'test_date': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
    })

    # Get active and queued test counts from job manager
    active_tests = 0
    queued_tests = 0
    active_jobs = []
    try:
        if hasattr(current_app, 'job_manager') and current_app.job_manager:
            all_jobs = current_app.job_manager.get_active_jobs(job_type=JobType.TESTING)
            for job in all_jobs:
                if job.get('status') == JobStatus.RUNNING.value:
                    active_tests += 1
                    active_jobs.append(job)
                elif job.get('status') == JobStatus.PENDING.value:
                    queued_tests += 1
    except Exception as e:
        logger.warning(f"Could not get job counts: {e}")

    # Add job counts to stats
    stats['active_tests'] = active_tests
    stats['queued_tests'] = queued_tests
    stats['completed_today'] = completed_today

    # Get recent results with full context (limit to 10 for faster load)
    recent_results = get_recent_results_with_context(db, project_id, website_id, limit=10)

    # Get scheduled tests (limit to 5)
    schedules = []
    if website_id:
        schedules = db.get_test_schedules_for_website(website_id)[:5]
    elif project_id:
        for w in websites[:3]:  # Limit to first 3 websites for speed
            website_schedules = db.get_test_schedules_for_website(w.id)
            for s in website_schedules:
                s._website_name = w.name  # Add website name for display
            schedules.extend(website_schedules)
            if len(schedules) >= 5:
                break
        schedules = schedules[:5]

    # Get trend data for charts (reduce to 14 days for faster load)
    trend_data = get_trend_data(db, project_id, website_id, days=14)

    # Get project users (testers) for the selected project
    project_users = []
    if project_id:
        project_users = db.get_project_users(project_id, enabled_only=True)

    return render_template('testing/dashboard.html',
                         projects=projects,
                         selected_project=selected_project,
                         websites=websites,
                         selected_website=selected_website,
                         selected_website_id=website_id,
                         stats=stats,
                         recent_results=recent_results,
                         schedules=schedules,
                         active_jobs=active_jobs,
                         trend_data=trend_data,
                         project_users=project_users)


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
        if 'show_error_codes' in config:
            current_app.app_config.SHOW_ERROR_CODES = config['show_error_codes']

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
        'max_pages_per_page': getattr(current_app.app_config, 'MAX_PAGES_PER_PAGE', 500),
        'show_error_codes': getattr(current_app.app_config, 'SHOW_ERROR_CODES', False)
    }

    return render_template('testing/configure.html', config=current_config)


# ============================================================================
# API Endpoints for Dashboard
# ============================================================================

@testing_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for real-time stats (for polling)"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')

    # Calculate stats based on filters
    if website_id:
        website = db.get_website(website_id)
        if website:
            pages = db.get_pages(website_id)
            tested_pages = sum(1 for p in pages if p.status == PageStatus.TESTED)
            stats = {
                'website_count': 1,
                'total_pages': len(pages),
                'tested_pages': tested_pages,
                'untested_pages': len(pages) - tested_pages,
                'total_violations': sum(p.violation_count for p in pages),
                'total_warnings': sum(p.warning_count for p in pages),
                'test_coverage': round((tested_pages / len(pages) * 100), 1) if pages else 0
            }
        else:
            return jsonify({'error': 'Website not found'}), 404
    elif project_id:
        stats = db.get_project_stats(project_id)
    else:
        stats = calculate_aggregate_stats(db)

    # Get completed today
    completed_today = db.test_results.count_documents({
        'test_date': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
    })

    # Get active/queued counts
    active_tests = 0
    queued_tests = 0
    try:
        if hasattr(current_app, 'job_manager') and current_app.job_manager:
            all_jobs = current_app.job_manager.get_active_jobs(job_type=JobType.TESTING)
            for job in all_jobs:
                if job.get('status') == JobStatus.RUNNING.value:
                    active_tests += 1
                elif job.get('status') == JobStatus.PENDING.value:
                    queued_tests += 1
    except Exception as e:
        logger.warning(f"Could not get job counts: {e}")

    stats['active_tests'] = active_tests
    stats['queued_tests'] = queued_tests
    stats['completed_today'] = completed_today

    return jsonify({
        'success': True,
        'stats': stats
    })


@testing_bp.route('/api/active-tests')
@login_required
def api_active_tests():
    """API endpoint for active test progress (for polling)"""
    active_jobs = []

    try:
        if hasattr(current_app, 'job_manager') and current_app.job_manager:
            all_jobs = current_app.job_manager.get_active_jobs(job_type=JobType.TESTING)
            for job in all_jobs:
                if job.get('status') == JobStatus.RUNNING.value:
                    # Get website info for display
                    website_name = 'Unknown'
                    if job.get('website_id'):
                        website = current_app.db.get_website(job['website_id'])
                        if website:
                            website_name = website.name

                    active_jobs.append({
                        'job_id': job.get('job_id'),
                        'website_id': job.get('website_id'),
                        'website_name': website_name,
                        'progress': job.get('progress', 0),
                        'pages_completed': job.get('pages_completed', 0),
                        'pages_total': job.get('pages_total', 0),
                        'current_page': job.get('current_page', ''),
                        'started_at': job.get('started_at', '').isoformat() if job.get('started_at') else None,
                        'violations_found': job.get('violations_found', 0)
                    })
    except Exception as e:
        logger.warning(f"Could not get active jobs: {e}")

    return jsonify({
        'success': True,
        'active_tests': active_jobs,
        'count': len(active_jobs)
    })


@testing_bp.route('/api/run-tests', methods=['POST'])
@login_required
def api_run_tests():
    """API endpoint to start testing (enhanced version)"""
    data = request.get_json() or {}

    website_id = data.get('website_id')
    project_id = data.get('project_id')
    test_untested_only = data.get('untested_only', False)
    include_screenshots = data.get('include_screenshots', True)
    run_ai_analysis = data.get('run_ai_analysis', False)
    tester_ids = data.get('tester_ids', ['guest'])  # List of tester IDs or 'guest'

    if not website_id and not project_id:
        return jsonify({'error': 'Either website_id or project_id is required'}), 400

    # Validate at least one tester is selected
    if not tester_ids:
        return jsonify({'error': 'At least one tester must be selected'}), 400

    db = current_app.db

    try:
        if website_id:
            # Test single website
            website = db.get_website(website_id)
            if not website:
                return jsonify({'error': 'Website not found'}), 404

            pages = db.get_pages(website_id)
            if test_untested_only:
                pages = [p for p in pages if p.status != PageStatus.TESTED]

            if not pages:
                return jsonify({
                    'success': False,
                    'error': 'No pages to test',
                    'message': 'All pages have already been tested' if test_untested_only else 'No pages found'
                }), 400

            # Queue pages for testing
            for page in pages:
                page.status = PageStatus.QUEUED
                db.update_page(page)

            # Build tester description for message
            tester_count = len(tester_ids)
            tester_desc = f" with {tester_count} tester(s)" if tester_count > 1 or 'guest' not in tester_ids else ""

            return jsonify({
                'success': True,
                'message': f'Queued {len(pages)} pages for testing{tester_desc}',
                'pages_queued': len(pages),
                'website_name': website.name,
                'tester_ids': tester_ids
            })

        elif project_id:
            # Test entire project
            project = db.get_project(project_id)
            if not project:
                return jsonify({'error': 'Project not found'}), 404

            websites = db.get_websites(project_id)
            total_pages = 0

            for website in websites:
                pages = db.get_pages(website.id)
                if test_untested_only:
                    pages = [p for p in pages if p.status != PageStatus.TESTED]

                for page in pages:
                    page.status = PageStatus.QUEUED
                    db.update_page(page)
                    total_pages += 1

            if total_pages == 0:
                return jsonify({
                    'success': False,
                    'error': 'No pages to test',
                    'message': 'All pages have already been tested' if test_untested_only else 'No pages found'
                }), 400

            # Build tester description for message
            tester_count = len(tester_ids)
            tester_desc = f" with {tester_count} tester(s)" if tester_count > 1 or 'guest' not in tester_ids else ""

            return jsonify({
                'success': True,
                'message': f'Queued {total_pages} pages across {len(websites)} websites for testing{tester_desc}',
                'pages_queued': total_pages,
                'websites_count': len(websites),
                'project_name': project.name,
                'tester_ids': tester_ids
            })

    except Exception as e:
        logger.error(f"Error starting tests: {e}")
        return jsonify({'error': str(e)}), 500


@testing_bp.route('/api/trends')
@login_required
def api_trends():
    """API endpoint for trend data"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')
    days = int(request.args.get('days', 30))

    trend_data = get_trend_data(db, project_id, website_id, days)

    return jsonify({
        'success': True,
        'trend_data': trend_data
    })


@testing_bp.route('/api/websites/<project_id>')
@login_required
def api_project_websites(project_id):
    """API endpoint to get websites for a project (for dynamic dropdown)"""
    db = current_app.db

    project = db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    websites = db.get_websites(project_id)

    return jsonify({
        'success': True,
        'websites': [
            {
                'id': w.id,
                'name': w.name,
                'url': w.url,
                'page_count': w.page_count
            } for w in websites
        ]
    })