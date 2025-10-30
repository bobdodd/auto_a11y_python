"""
RESTful API routes
"""

from flask import Blueprint, jsonify, request, current_app
from auto_a11y.models import Project, Website, Page, ProjectStatus, PageStatus
from auto_a11y.core.job_manager import JobManager, JobStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)


# Fixture Test Status API

@api_bp.route('/fixture-tests/status', methods=['GET'])
def get_fixture_test_status():
    """Get fixture test status for all tests"""
    try:
        # Get test configuration
        test_config = current_app.test_config
        
        # Get all test statuses
        statuses = test_config.get_all_test_statuses()
        
        # Get fixture run summary
        summary = None
        if test_config.fixture_validator:
            summary = test_config.fixture_validator.get_fixture_run_summary()
        
        # Get passing tests
        passing_tests = set()
        if test_config.fixture_validator:
            passing_tests = test_config.fixture_validator.get_passing_tests()

        # Calculate category counts
        all_pass_count = 0
        partial_pass_count = 0
        all_fail_count = 0

        for error_code, status in statuses.items():
            category = status.get('status_category', 'all_fail')
            if category == 'all_pass':
                all_pass_count += 1
            elif category == 'partial_pass':
                partial_pass_count += 1
            else:
                all_fail_count += 1

        return jsonify({
            'success': True,
            'debug_mode': test_config.debug_mode,
            'fixture_run_summary': summary,
            'passing_tests': list(passing_tests),
            'test_statuses': statuses,
            'total_tests': len(statuses),
            'passing_count': len(passing_tests),
            'all_pass_count': all_pass_count,
            'partial_pass_count': partial_pass_count,
            'all_fail_count': all_fail_count
        })
    except Exception as e:
        logger.error(f"Error getting fixture test status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/fixture-tests/check/<error_code>', methods=['GET'])
def check_test_availability(error_code):
    """Check if a specific test is available based on fixture status"""
    try:
        test_config = current_app.test_config
        
        # Get fixture status for this test
        status = test_config.get_test_fixture_status(error_code)
        
        return jsonify({
            'success': True,
            'error_code': error_code,
            'available': status.get('available', False),
            'passed_fixture': status.get('passed_fixture', False),
            'debug_override': status.get('debug_override', False),
            'fixture_path': status.get('fixture_path', ''),
            'tested_at': status.get('tested_at')
        })
    except Exception as e:
        logger.error(f"Error checking test availability for {error_code}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Projects API

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    status = request.args.get('status')
    
    skip = (page - 1) * limit
    
    if status:
        try:
            status_enum = ProjectStatus(status)
            projects = current_app.db.get_projects(status=status_enum, limit=limit, skip=skip)
        except ValueError:
            return jsonify({'error': 'Invalid status value'}), 400
    else:
        projects = current_app.db.get_projects(limit=limit, skip=skip)
    
    return jsonify({
        'projects': [p.to_dict() for p in projects],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': current_app.db.projects.count_documents({})
        }
    })


@api_bp.route('/projects', methods=['POST'])
def create_project():
    """Create new project"""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Project name is required'}), 400
    
    # Check if project exists
    existing = current_app.db.projects.find_one({'name': data['name']})
    if existing:
        return jsonify({'error': f'Project {data["name"]} already exists'}), 409
    
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        status=ProjectStatus.ACTIVE,
        config=data.get('config', {})
    )
    
    project_id = current_app.db.create_project(project)
    
    return jsonify({
        'id': project_id,
        'message': f'Project created successfully'
    }), 201


@api_bp.route('/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get project by ID"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    stats = current_app.db.get_project_stats(project_id)
    
    response = project.to_dict()
    response['statistics'] = stats
    
    return jsonify(response)


@api_bp.route('/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update project"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        try:
            project.status = ProjectStatus(data['status'])
        except ValueError:
            return jsonify({'error': 'Invalid status value'}), 400
    if 'config' in data:
        project.config.update(data['config'])
    
    if current_app.db.update_project(project):
        return jsonify({'message': 'Project updated successfully'})
    else:
        return jsonify({'error': 'Failed to update project'}), 500


@api_bp.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if current_app.db.delete_project(project_id):
        return jsonify({'message': 'Project deleted successfully'}), 204
    else:
        return jsonify({'error': 'Failed to delete project'}), 500


# Websites API

@api_bp.route('/projects/<project_id>/websites', methods=['GET'])
def get_websites(project_id):
    """Get websites for project"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    websites = current_app.db.get_websites(project_id)
    
    return jsonify({
        'websites': [w.to_dict() for w in websites]
    })


@api_bp.route('/projects/<project_id>/websites', methods=['POST'])
def add_website(project_id):
    """Add website to project"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Website URL is required'}), 400
    
    from auto_a11y.models import Website, ScrapingConfig
    
    website = Website(
        project_id=project_id,
        url=data['url'],
        name=data.get('name'),
        scraping_config=ScrapingConfig(**data.get('scraping_config', {}))
    )
    
    website_id = current_app.db.create_website(website)
    
    return jsonify({
        'id': website_id,
        'message': 'Website added successfully'
    }), 201


@api_bp.route('/websites/<website_id>', methods=['GET'])
def get_website(website_id):
    """Get website by ID"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    return jsonify(website.to_dict())


@api_bp.route('/websites/<website_id>', methods=['DELETE'])
def delete_website(website_id):
    """Delete website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    if current_app.db.delete_website(website_id):
        return jsonify({'message': 'Website deleted successfully'}), 204
    else:
        return jsonify({'error': 'Failed to delete website'}), 500


# Pages API

@api_bp.route('/websites/<website_id>/pages', methods=['GET'])
def get_pages(website_id):
    """Get pages for website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    status = request.args.get('status')
    has_violations = request.args.get('has_violations')
    
    if status:
        try:
            status_enum = PageStatus(status)
            pages = current_app.db.get_pages(website_id, status=status_enum)
        except ValueError:
            return jsonify({'error': 'Invalid status value'}), 400
    else:
        pages = current_app.db.get_pages(website_id)
    
    if has_violations is not None:
        has_violations = has_violations.lower() == 'true'
        pages = [p for p in pages if p.has_issues == has_violations]
    
    return jsonify({
        'pages': [p.to_dict() for p in pages]
    })


@api_bp.route('/websites/<website_id>/pages', methods=['POST'])
def add_page(website_id):
    """Add page to website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'Page URL is required'}), 400
    
    page = Page(
        website_id=website_id,
        url=data['url'],
        priority=data.get('priority', 'normal')
    )
    
    page_id = current_app.db.create_page(page)
    
    return jsonify({
        'id': page_id,
        'message': 'Page added successfully'
    }), 201


@api_bp.route('/pages/<page_id>', methods=['GET'])
def get_page(page_id):
    """Get page by ID"""
    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    return jsonify(page.to_dict())


@api_bp.route('/pages/<page_id>/test', methods=['POST'])
def test_page(page_id):
    """Run test on page"""
    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    data = request.get_json() or {}
    config = data.get('config', {})
    
    # Queue test job
    job_id = f'test_{page_id}_{datetime.now().timestamp()}'
    
    # Update page status
    page.status = PageStatus.QUEUED
    current_app.db.update_page(page)
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Test job queued successfully'
    }), 202


# Test Results API

@api_bp.route('/test-results/<result_id>', methods=['GET'])
def get_test_result(result_id):
    """Get test result by ID"""
    result = current_app.db.get_test_result(result_id)
    if not result:
        return jsonify({'error': 'Test result not found'}), 404
    
    return jsonify(result.to_dict())


@api_bp.route('/pages/<page_id>/test-results', methods=['GET'])
def get_page_test_results(page_id):
    """Get test results for page"""
    page = current_app.db.get_page(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    results = current_app.db.get_test_results(page_id=page_id)
    
    return jsonify({
        'results': [r.to_dict() for r in results]
    })


# Batch Operations

@api_bp.route('/websites/<website_id>/discover', methods=['POST'])
def discover_pages(website_id):
    """Start page discovery for website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    data = request.get_json() or {}
    strategy = data.get('strategy', 'crawl')
    config = data.get('config', {})
    
    # Queue discovery job
    job_id = f'discovery_{website_id}_{datetime.now().timestamp()}'
    
    return jsonify({
        'job_id': job_id,
        'status': 'started',
        'message': 'Page discovery started'
    }), 202


@api_bp.route('/websites/<website_id>/test', methods=['POST'])
def test_website(website_id):
    """Run tests on all pages in website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    data = request.get_json() or {}
    page_ids = data.get('page_ids', 'all')
    config = data.get('config', {})
    
    if page_ids == 'all':
        pages = current_app.db.get_pages(website_id)
    else:
        pages = [current_app.db.get_page(pid) for pid in page_ids]
        pages = [p for p in pages if p]  # Filter None values
    
    if not pages:
        return jsonify({'error': 'No pages to test'}), 400
    
    # Queue batch test job
    job_id = f'batch_test_{website_id}_{datetime.now().timestamp()}'
    
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'pages_queued': len(pages),
        'message': f'Batch testing queued for {len(pages)} pages'
    }), 202


# Reports API

@api_bp.route('/projects/<project_id>/reports', methods=['POST'])
def generate_report(project_id):
    """Generate report for project"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json() or {}
    format_type = data.get('format', 'xlsx')
    include = data.get('include', {})
    filters = data.get('filters', {})
    
    # Queue report generation
    report_id = f'report_{project_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    return jsonify({
        'report_id': report_id,
        'status': 'generating',
        'message': 'Report generation started'
    }), 202


# Health Check

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        # Check database connection
        current_app.db.client.server_info()
        db_status = 'healthy'
    except:
        db_status = 'unhealthy'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })


# Jobs API

@api_bp.route('/jobs/stats', methods=['GET'])
def get_job_stats():
    """Get job statistics"""
    try:
        job_manager = JobManager(current_app.db)
        
        # Get overall statistics
        stats = job_manager.get_job_statistics(hours=24)
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting job stats: {e}")
        return jsonify({'error': 'Failed to get job statistics'}), 500


@api_bp.route('/jobs/clear-all', methods=['POST'])
def clear_all_jobs():
    """Clear all running and pending jobs - emergency reset"""
    try:
        job_manager = JobManager(current_app.db)
        
        # Clear all running jobs
        running_result = job_manager.collection.update_many(
            {'status': {'$in': [JobStatus.RUNNING.value, JobStatus.CANCELLING.value]}},
            {
                '$set': {
                    'status': JobStatus.CANCELLED.value,
                    'completed_at': datetime.now(),
                    'error': 'Job cleared by administrator'
                }
            }
        )
        
        # Clear all pending jobs
        pending_result = job_manager.collection.update_many(
            {'status': JobStatus.PENDING.value},
            {
                '$set': {
                    'status': JobStatus.CANCELLED.value,
                    'completed_at': datetime.now(),
                    'error': 'Job cleared by administrator'
                }
            }
        )
        
        # Also reset page statuses that are stuck in QUEUED or TESTING states
        pages_result = current_app.db.pages.update_many(
            {'status': {'$in': [PageStatus.QUEUED.value, PageStatus.TESTING.value]}},
            {
                '$set': {
                    'status': PageStatus.DISCOVERED.value,
                    'error_reason': 'Job cleared by administrator'
                }
            }
        )
        
        total_cleared = running_result.modified_count + pending_result.modified_count
        
        logger.info(f"Cleared {total_cleared} jobs (running: {running_result.modified_count}, pending: {pending_result.modified_count})")
        logger.info(f"Reset {pages_result.modified_count} pages from queued/testing to discovered status")
        
        return jsonify({
            'success': True,
            'cleared_count': total_cleared,
            'running_cleared': running_result.modified_count,
            'pending_cleared': pending_result.modified_count,
            'pages_reset': pages_result.modified_count,
            'message': f'Successfully cleared {total_cleared} jobs and reset {pages_result.modified_count} pages'
        })
        
    except Exception as e:
        logger.error(f"Error clearing all jobs: {e}")
        return jsonify({'error': f'Failed to clear jobs: {str(e)}'}), 500


@api_bp.route('/jobs/clear-stale', methods=['POST'])
def clear_stale_jobs():
    """Clear stale jobs that have been running for too long"""
    try:
        job_manager = JobManager(current_app.db)
        
        # Clear jobs running for more than 24 hours
        cleared_count = job_manager.cleanup_stale_jobs(stale_after_hours=24)
        
        # Also reset old pages stuck in QUEUED or TESTING states for more than 24 hours
        from datetime import timedelta
        stale_time = datetime.now() - timedelta(hours=24)
        pages_result = current_app.db.pages.update_many(
            {
                'status': {'$in': [PageStatus.QUEUED.value, PageStatus.TESTING.value]},
                '$or': [
                    {'last_tested': {'$lt': stale_time}},
                    {'last_tested': None, 'discovered_at': {'$lt': stale_time}}
                ]
            },
            {
                '$set': {
                    'status': PageStatus.DISCOVERED.value,
                    'error_reason': 'Stale job cleared by administrator'
                }
            }
        )
        
        logger.info(f"Cleared {cleared_count} stale jobs")
        logger.info(f"Reset {pages_result.modified_count} stale pages")
        
        return jsonify({
            'success': True,
            'cleared_count': cleared_count,
            'pages_reset': pages_result.modified_count,
            'message': f'Successfully cleared {cleared_count} stale jobs and reset {pages_result.modified_count} pages'
        })
        
    except Exception as e:
        logger.error(f"Error clearing stale jobs: {e}")
        return jsonify({'error': f'Failed to clear stale jobs: {str(e)}'}), 500


@api_bp.route('/jobs/active', methods=['GET'])
def get_active_jobs():
    """Get list of active jobs"""
    try:
        job_manager = JobManager(current_app.db)
        
        # Get active jobs
        active_jobs = list(job_manager.collection.find(
            {'status': {'$in': [JobStatus.RUNNING.value, JobStatus.PENDING.value, JobStatus.CANCELLING.value]}},
            {'_id': 0}  # Exclude MongoDB _id from response
        ).sort('created_at', -1).limit(100))
        
        return jsonify({
            'jobs': active_jobs,
            'count': len(active_jobs)
        })
        
    except Exception as e:
        logger.error(f"Error getting active jobs: {e}")
        return jsonify({'error': 'Failed to get active jobs'}), 500


@api_bp.route('/jobs/cleanup-page-counts', methods=['POST'])
def cleanup_page_counts():
    """Clean up violation counts for pages that haven't been tested"""
    try:
        # Reset violation/warning/info counts for all pages that aren't in TESTED status
        result = current_app.db.pages.update_many(
            {'status': {'$ne': PageStatus.TESTED.value}},
            {
                '$set': {
                    'violation_count': 0,
                    'warning_count': 0,
                    'info_count': 0,
                    'discovery_count': 0,
                    'pass_count': 0,
                    'test_duration_ms': None
                }
            }
        )
        
        logger.info(f"Cleaned up counts for {result.modified_count} untested pages")
        
        return jsonify({
            'success': True,
            'pages_cleaned': result.modified_count,
            'message': f'Reset counts for {result.modified_count} untested pages'
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up page counts: {e}")
        return jsonify({'error': f'Failed to clean up page counts: {str(e)}'}), 500


# Multi-State Testing API Endpoints

@api_bp.route('/test-results/<result_id>/states', methods=['GET'])
def get_test_result_states(result_id):
    """
    Get all related state test results for a given result

    Returns all test results from the same testing session, showing different
    page states (before/after scripts, button states, etc.)
    """
    try:
        # Get the result
        result = current_app.db.get_test_result(result_id)
        if not result:
            return jsonify({'error': 'Test result not found'}), 404

        # Get related results
        related_results = current_app.db.get_related_test_results(result_id)

        # Include the original result
        all_results = [result] + related_results

        # Sort by state_sequence
        all_results.sort(key=lambda r: r.state_sequence)

        # Serialize results
        results_data = []
        for r in all_results:
            state_info = {
                'result_id': str(r._id) if r._id else None,
                'state_sequence': r.state_sequence,
                'page_state': r.page_state,
                'session_id': r.session_id,
                'test_date': r.test_date.isoformat() if r.test_date else None,
                'violation_count': r.violation_count,
                'warning_count': r.warning_count,
                'info_count': r.info_count,
                'pass_count': r.pass_count,
                'duration_ms': r.duration_ms
            }
            results_data.append(state_info)

        return jsonify({
            'success': True,
            'result_id': result_id,
            'total_states': len(results_data),
            'states': results_data
        })

    except Exception as e:
        logger.error(f"Error getting test result states: {e}")
        return jsonify({'error': f'Failed to get test result states: {str(e)}'}), 500


@api_bp.route('/pages/<page_id>/test-states', methods=['GET'])
def get_page_test_states(page_id):
    """
    Get latest test results per state for a page

    Shows the most recent test result for each state (initial, after script, etc.)
    """
    try:
        # Check page exists
        page = current_app.db.get_page(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404

        # Get latest results per state
        state_results = current_app.db.get_latest_test_results_per_state(page_id)

        # Serialize results
        states_data = {}
        for state_seq, result in state_results.items():
            states_data[state_seq] = {
                'result_id': str(result._id) if result._id else None,
                'state_sequence': state_seq,
                'page_state': result.page_state,
                'session_id': result.session_id,
                'test_date': result.test_date.isoformat() if result.test_date else None,
                'violation_count': result.violation_count,
                'warning_count': result.warning_count,
                'info_count': result.info_count,
                'pass_count': result.pass_count,
                'duration_ms': result.duration_ms
            }

        return jsonify({
            'success': True,
            'page_id': page_id,
            'page_url': page.url,
            'total_states': len(states_data),
            'states': states_data
        })

    except Exception as e:
        logger.error(f"Error getting page test states: {e}")
        return jsonify({'error': f'Failed to get page test states: {str(e)}'}), 500


@api_bp.route('/pages/<page_id>/test-sessions', methods=['GET'])
def get_page_test_sessions(page_id):
    """
    Get all test sessions for a page with their state counts

    Shows all testing sessions and how many states were tested in each
    """
    try:
        # Check page exists
        page = current_app.db.get_page(page_id)
        if not page:
            return jsonify({'error': 'Page not found'}), 404

        # Get all test results for page
        all_results = current_app.db.get_test_results(page_id=page_id, limit=1000)

        # Group by session
        sessions = {}
        for result in all_results:
            session_id = result.session_id or 'single_state'

            if session_id not in sessions:
                sessions[session_id] = {
                    'session_id': session_id,
                    'test_date': result.test_date,
                    'states': [],
                    'total_violations': 0,
                    'total_warnings': 0
                }

            sessions[session_id]['states'].append({
                'result_id': str(result._id) if result._id else None,
                'state_sequence': result.state_sequence,
                'state_description': result.page_state.get('description') if result.page_state else None,
                'violation_count': result.violation_count,
                'warning_count': result.warning_count
            })

            sessions[session_id]['total_violations'] += result.violation_count
            sessions[session_id]['total_warnings'] += result.warning_count

        # Convert to list and sort by date
        sessions_list = list(sessions.values())
        sessions_list.sort(key=lambda s: s['test_date'], reverse=True)

        # Sort states within each session
        for session in sessions_list:
            session['states'].sort(key=lambda s: s['state_sequence'])
            session['state_count'] = len(session['states'])
            session['test_date'] = session['test_date'].isoformat() if session['test_date'] else None

        return jsonify({
            'success': True,
            'page_id': page_id,
            'page_url': page.url,
            'total_sessions': len(sessions_list),
            'sessions': sessions_list
        })

    except Exception as e:
        logger.error(f"Error getting page test sessions: {e}")
        return jsonify({'error': f'Failed to get page test sessions: {str(e)}'}), 500


@api_bp.route('/test-results/compare', methods=['POST'])
def compare_test_results():
    """
    Compare two test results (typically from different states)

    Request body:
    {
        "result_id_1": "...",
        "result_id_2": "..."
    }

    Returns:
    - Violations that appeared in result_2 (new violations)
    - Violations that disappeared from result_1 (fixed violations)
    - Violations that exist in both (persistent violations)
    """
    try:
        data = request.get_json()
        result_id_1 = data.get('result_id_1')
        result_id_2 = data.get('result_id_2')

        if not result_id_1 or not result_id_2:
            return jsonify({'error': 'Both result_id_1 and result_id_2 are required'}), 400

        # Get results
        result1 = current_app.db.get_test_result(result_id_1)
        result2 = current_app.db.get_test_result(result_id_2)

        if not result1 or not result2:
            return jsonify({'error': 'One or both test results not found'}), 404

        # Get violation IDs (using issue_id for comparison)
        violations1_ids = {v.id for v in result1.violations}
        violations2_ids = {v.id for v in result2.violations}

        # Calculate differences
        new_violations = [v for v in result2.violations if v.id not in violations1_ids]
        fixed_violations = [v for v in result1.violations if v.id not in violations2_ids]
        persistent_violations = [v for v in result2.violations if v.id in violations1_ids]

        # Serialize violations
        def serialize_violation(v):
            return {
                'id': v.id,
                'impact': v.impact.value if hasattr(v.impact, 'value') else v.impact,
                'touchpoint': v.touchpoint,
                'description': v.description,
                'element': v.element
            }

        comparison = {
            'result_1': {
                'id': result_id_1,
                'state_sequence': result1.state_sequence,
                'state_description': result1.page_state.get('description') if result1.page_state else None,
                'violation_count': result1.violation_count,
                'test_date': result1.test_date.isoformat() if result1.test_date else None
            },
            'result_2': {
                'id': result_id_2,
                'state_sequence': result2.state_sequence,
                'state_description': result2.page_state.get('description') if result2.page_state else None,
                'violation_count': result2.violation_count,
                'test_date': result2.test_date.isoformat() if result2.test_date else None
            },
            'new_violations': [serialize_violation(v) for v in new_violations],
            'fixed_violations': [serialize_violation(v) for v in fixed_violations],
            'persistent_violations': [serialize_violation(v) for v in persistent_violations],
            'summary': {
                'new_count': len(new_violations),
                'fixed_count': len(fixed_violations),
                'persistent_count': len(persistent_violations),
                'net_change': result2.violation_count - result1.violation_count
            }
        }

        return jsonify({
            'success': True,
            'comparison': comparison
        })

    except Exception as e:
        logger.error(f"Error comparing test results: {e}")
        return jsonify({'error': f'Failed to compare test results: {str(e)}'}), 500