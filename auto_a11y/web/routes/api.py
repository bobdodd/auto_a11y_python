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
        
        return jsonify({
            'success': True,
            'debug_mode': test_config.debug_mode,
            'fixture_run_summary': summary,
            'passing_tests': list(passing_tests),
            'test_statuses': statuses,
            'total_tests': len(statuses),
            'passing_count': len(passing_tests)
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