"""
Website management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from auto_a11y.models import Website, ScrapingConfig, Page, PageStatus
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)
websites_bp = Blueprint('websites', __name__)


@websites_bp.route('/api/list')
def api_list_websites():
    """API endpoint to list all websites"""
    try:
        websites = current_app.db.get_all_websites()
        return jsonify({
            'success': True,
            'websites': [
                {
                    'id': w.id,
                    'name': w.name,
                    'url': w.url,
                    'project_id': w.project_id
                } for w in websites
            ]
        })
    except Exception as e:
        logger.error(f"Error listing websites: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@websites_bp.route('/<website_id>')
def view_website(website_id):
    """View website details"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    project = current_app.db.get_project(website.project_id)
    pages = current_app.db.get_pages(website_id, limit=100)
    
    # Calculate statistics
    stats = {
        'total_pages': len(pages),
        'tested_pages': sum(1 for p in pages if p.status == PageStatus.TESTED),
        'pages_with_issues': sum(1 for p in pages if p.has_issues),
        'total_violations': sum(p.violation_count for p in pages),
        'total_warnings': sum(p.warning_count for p in pages)
    }
    
    return render_template('websites/view.html',
                         website=website,
                         project=project,
                         pages=pages,
                         stats=stats)


@websites_bp.route('/<website_id>/edit', methods=['GET', 'POST'])
def edit_website(website_id):
    """Edit website configuration"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    if request.method == 'POST':
        website.name = request.form.get('name', website.name)
        website.url = request.form.get('url', website.url)
        
        # Update scraping config
        website.scraping_config.max_pages = int(request.form.get('max_pages', 500))
        website.scraping_config.max_depth = int(request.form.get('max_depth', 3))
        website.scraping_config.follow_external = request.form.get('follow_external') == 'on'
        website.scraping_config.include_subdomains = request.form.get('include_subdomains') == 'on'
        website.scraping_config.respect_robots = request.form.get('respect_robots') == 'on'
        website.scraping_config.request_delay = float(request.form.get('request_delay', 1.0))
        
        if current_app.db.update_website(website):
            flash('Website updated successfully', 'success')
            return redirect(url_for('websites.view_website', website_id=website_id))
        else:
            flash('Failed to update website', 'error')
    
    project = current_app.db.get_project(website.project_id)
    return render_template('websites/edit.html', website=website, project=project)


@websites_bp.route('/<website_id>/delete', methods=['POST'])
def delete_website(website_id):
    """Delete website"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    project_id = website.project_id
    
    if current_app.db.delete_website(website_id):
        flash(f'Website "{website.display_name}" deleted successfully', 'success')
    else:
        flash('Failed to delete website', 'error')
    
    return redirect(url_for('projects.view_project', project_id=project_id))


@websites_bp.route('/<website_id>/discover', methods=['POST'])
def discover_pages(website_id):
    """Start page discovery for website with optional max pages limit"""
    from auto_a11y.core.website_manager import WebsiteManager
    from auto_a11y.core.task_runner import task_runner
    
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    # Get max_pages parameter from request
    max_pages = None
    if request.is_json:
        max_pages = request.json.get('max_pages')
    else:
        max_pages = request.form.get('max_pages')
    
    if max_pages:
        try:
            max_pages = int(max_pages)
            if max_pages <= 0:
                max_pages = None
            else:
                logger.info(f"Discovery will be limited to {max_pages} pages")
        except (ValueError, TypeError):
            max_pages = None
    
    try:
        # Check if Chromium is available
        from pyppeteer import chromium_downloader
        import os
        
        try:
            chromium_path = chromium_downloader.chromium_executable()
            logger.info(f"Chromium path detected: {chromium_path}")
            
            if not chromium_path:
                logger.warning("Chromium path is None")
                return jsonify({
                    'success': False,
                    'error': 'Chromium browser not found. Please run: python run.py --download-browser',
                    'message': 'Browser required for page discovery'
                }), 500
                
            if not os.path.exists(chromium_path):
                logger.warning(f"Chromium path does not exist: {chromium_path}")
                return jsonify({
                    'success': False,
                    'error': f'Chromium browser not found at {chromium_path}. Please run: python run.py --download-browser',
                    'message': 'Browser required for page discovery'
                }), 500
                
            logger.info(f"Chromium found and verified at: {chromium_path}")
            
        except Exception as chrome_error:
            logger.error(f"Error checking Chromium: {chrome_error}")
            return jsonify({
                'success': False,
                'error': f'Error checking Chromium: {chrome_error}',
                'message': 'Failed to verify browser installation'
            }), 500
        
        # Create website manager
        website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
        logger.info(f"Created website manager for website {website_id}")
        
        # Submit discovery task - use a more predictable job ID format
        import uuid
        task_id = f'discovery_{website_id}_{uuid.uuid4().hex[:8]}'
        logger.info(f"Submitting discovery task with ID: {task_id}")
        
        # Create a wrapper that handles the async execution properly
        def discovery_wrapper():
            import asyncio
            import nest_asyncio
            nest_asyncio.apply()
            
            logger.info(f"Discovery wrapper starting for website {website_id}, task_id: {task_id}")
            
            # Get user info from session if available
            user_id = session.get('user_id') if session else None
            session_id = session.get('session_id') if session else None
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    website_manager.discover_pages(
                        website_id, 
                        max_pages=max_pages, 
                        job_id=task_id,
                        user_id=user_id,
                        session_id=session_id
                    )
                )
                logger.info(f"Discovery wrapper completed, result job_id: {result.job_id if result else 'None'}")
                return result
            finally:
                loop.close()
        
        submitted_id = task_runner.submit_task(
            func=discovery_wrapper,
            args=(),
            task_id=task_id
        )
        
        logger.info(f"Discovery task submitted successfully with ID: {submitted_id}")
        
        message = f'Page discovery started'
        if max_pages:
            message += f' (limited to {max_pages} pages)'
        
        return jsonify({
            'success': True,
            'message': message,
            'job_id': submitted_id,
            'max_pages': max_pages,
            'status_url': url_for('websites.discovery_status', website_id=website_id, job_id=submitted_id)
        })
        
    except Exception as e:
        logger.error(f"Failed to start discovery: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to start page discovery'
        }), 500


@websites_bp.route('/<website_id>/discovery-status')
def discovery_status(website_id):
    """Check discovery job status with enhanced progress tracking"""
    from auto_a11y.core.website_manager import WebsiteManager
    
    job_id = request.args.get('job_id')
    
    # Get total page count for website
    total_pages = current_app.db.pages.count_documents({'website_id': website_id})
    
    if not job_id:
        # No specific job requested, check if any discovery is running
        # This helps with page refreshes where job_id might be lost
        return jsonify({
            'status': 'idle',
            'pages_found': total_pages,
            'message': f'{total_pages} pages in website'
        })
    
    # Get job status from database via WebsiteManager
    website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
    job_status = website_manager.get_job_status(job_id)
    
    if not job_status:
        # Job not found - it might have completed or been cleaned up
        return jsonify({
            'status': 'completed',
            'pages_found': total_pages,
            'message': f'Discovery completed - found {total_pages} pages'
        })
    
    # Extract progress details from database-backed job
    status = job_status.get('status', 'unknown')
    progress = job_status.get('progress', {})
    
    logger.info(f"Job {job_id} status: {status}, progress: {progress}")
    
    # Extract details from progress
    details = progress.get('details', {})
    
    # Build detailed response
    response = {
        'status': status,
        'pages_found': details.get('pages_found', 0),
        'current_depth': details.get('current_depth', 0),
        'queue_size': details.get('queue_size', 0),
        'current_url': progress.get('message', ''),  # message contains current URL
        'error': job_status.get('error')
    }
    
    # Create informative message based on status
    if status == 'running':
        pages_found = details.get('pages_found', 0)
        queue_size = details.get('queue_size', 0)
        current_url = progress.get('message', '')
        if current_url:
            # Don't truncate URLs - users need to see what's being processed
            response['message'] = f'Found {pages_found} pages. Scanning: {current_url}'
        else:
            response['message'] = f'Found {pages_found} pages...'
    elif status == 'completed':
        response['message'] = f'Discovery completed - found {details.get("pages_found", 0)} pages'
    elif status == 'failed':
        response['message'] = f'Discovery failed: {job_status.get("error", "Unknown error")}'
    elif status == 'cancelled':
        response['message'] = 'Discovery was cancelled'
    elif status == 'cancelling':
        response['message'] = 'Cancelling discovery...'
    elif status == 'pending':
        response['message'] = 'Discovery is starting...'
    else:
        response['message'] = f'Discovery {status}'
    
    return jsonify(response)


@websites_bp.route('/<website_id>/cancel-discovery', methods=['POST'])
def cancel_discovery(website_id):
    """Cancel an active discovery job"""
    from auto_a11y.core.website_manager import WebsiteManager
    
    # Log all request data for debugging
    logger.info(f"Cancel request received for website {website_id}")
    logger.info(f"  Request method: {request.method}")
    logger.info(f"  Request is_json: {request.is_json}")
    logger.info(f"  Request form data: {dict(request.form)}")
    logger.info(f"  Request json data: {request.json if request.is_json else 'N/A'}")
    logger.info(f"  Request values: {dict(request.values)}")
    
    # Try multiple ways to get job_id
    job_id = None
    if request.form and 'job_id' in request.form:
        job_id = request.form.get('job_id')
        logger.info(f"Got job_id from form: {job_id}")
    elif request.is_json and request.json and 'job_id' in request.json:
        job_id = request.json.get('job_id')
        logger.info(f"Got job_id from json: {job_id}")
    elif 'job_id' in request.values:
        job_id = request.values.get('job_id')
        logger.info(f"Got job_id from values: {job_id}")
    
    logger.info(f"Final job_id extracted: {job_id}")
    
    if not job_id:
        logger.error("No job_id provided in cancel request")
        return jsonify({'error': 'Job ID required'}), 400
    
    try:
        logger.info(f"Attempting to cancel discovery job {job_id} for website {website_id}")
        
        # Cancel using the database-backed job manager
        website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
        
        # Get user info for tracking who cancelled
        try:
            from flask import session
            user_id = session.get('user_id') if 'user_id' in session else None
        except:
            user_id = None
        
        # Request cancellation through the job manager
        cancelled = website_manager.cancel_discovery(job_id, user_id=user_id)
        
        if cancelled:
            logger.info(f"Successfully cancelled discovery job {job_id} for website {website_id}")
            return jsonify({
                'success': True,
                'message': 'Discovery cancelled successfully'
            })
        else:
            logger.warning(f"Could not cancel discovery job {job_id} - job not found or not cancellable")
            return jsonify({
                'success': False,
                'message': 'Job not found or already completed'
            })
    except Exception as e:
        logger.error(f"Error cancelling discovery job: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to cancel discovery'
        }), 500


@websites_bp.route('/<website_id>/add-page', methods=['POST'])
def add_page(website_id):
    """Manually add a page to website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    url = request.form.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create page
    page = Page(
        website_id=website_id,
        url=url,
        priority=request.form.get('priority', 'normal'),
        discovered_from='manual'
    )
    
    page_id = current_app.db.create_page(page)
    
    return jsonify({
        'success': True,
        'page_id': page_id,
        'message': f'Page added successfully'
    })


@websites_bp.route('/<website_id>/test-all', methods=['POST'])
def test_all_pages(website_id):
    """Start testing all pages in website using database-backed job management"""
    from auto_a11y.core.website_manager import WebsiteManager
    from auto_a11y.core.task_runner import task_runner
    import uuid
    
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    pages = current_app.db.get_pages(website_id)
    # Allow testing of all pages, not just untested ones
    # Users may want to re-test pages to check for improvements
    testable_pages = [p for p in pages if p.status != PageStatus.TESTING]  # Exclude currently testing pages
    
    if not testable_pages:
        return jsonify({
            'success': False,
            'message': 'No pages available for testing (some may be currently testing)'
        })
    
    try:
        # Create website manager
        website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
        logger.info(f"Created website manager for testing website {website_id}")
        
        # Generate job ID
        job_id = f'testing_{website_id}_{uuid.uuid4().hex[:8]}'
        logger.info(f"Submitting testing job with ID: {job_id}")
        
        # Get AI configuration
        ai_key = getattr(current_app.app_config, 'CLAUDE_API_KEY', None)
        
        # Create a wrapper that handles the async execution properly
        def testing_wrapper():
            import asyncio
            import nest_asyncio
            nest_asyncio.apply()
            
            logger.info(f"Testing wrapper starting for website {website_id}, job_id: {job_id}")
            
            # Get user info from session if available
            user_id = session.get('user_id') if session else None
            session_id = session.get('session_id') if session else None
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Get page IDs for testing
                page_ids = [p.id for p in testable_pages]
                
                result = loop.run_until_complete(
                    website_manager.test_website(
                        website_id=website_id,
                        page_ids=page_ids,
                        job_id=job_id,
                        user_id=user_id,
                        session_id=session_id,
                        test_all=False,  # We're providing specific page_ids
                        take_screenshot=True,
                        run_ai_analysis=None,
                        ai_api_key=ai_key
                    )
                )
                logger.info(f"Testing wrapper completed, result job_id: {result.job_id if result else 'None'}")
                return result
            finally:
                loop.close()
        
        # Submit testing task
        submitted_id = task_runner.submit_task(
            func=testing_wrapper,
            args=(),
            task_id=job_id
        )
        
        logger.info(f"Testing job submitted successfully with ID: {submitted_id}")
        
        return jsonify({
            'success': True,
            'message': f'Testing {len(testable_pages)} pages',
            'job_id': submitted_id,
            'pages_queued': len(testable_pages),
            'status_url': url_for('websites.test_status', website_id=website_id)
        })
        
    except Exception as e:
        logger.error(f"Failed to start testing: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to start testing'
        }), 500


@websites_bp.route('/<website_id>/cancel-testing', methods=['POST'])
def cancel_testing(website_id):
    """Cancel an active testing job"""
    from auto_a11y.core.website_manager import WebsiteManager
    
    # Log all request data for debugging
    logger.info(f"Cancel testing request received for website {website_id}")
    logger.info(f"  Request form data: {dict(request.form)}")
    logger.info(f"  Request json data: {request.json if request.is_json else 'N/A'}")
    
    # Get job_id from request
    job_id = None
    if request.form and 'job_id' in request.form:
        job_id = request.form.get('job_id')
    elif request.is_json and request.json and 'job_id' in request.json:
        job_id = request.json.get('job_id')
    
    logger.info(f"Final job_id extracted: {job_id}")
    
    if not job_id:
        logger.error("No job_id provided in cancel testing request")
        return jsonify({'error': 'Job ID required'}), 400
    
    try:
        logger.info(f"Attempting to cancel testing job {job_id} for website {website_id}")
        
        # Cancel using the database-backed job manager
        website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
        
        # Get user info for tracking who cancelled
        user_id = session.get('user_id') if session else None
        
        # Request cancellation through the job manager
        cancelled = website_manager.cancel_testing(job_id, user_id=user_id)
        
        if cancelled:
            logger.info(f"Successfully cancelled testing job {job_id} for website {website_id}")
            return jsonify({
                'success': True,
                'message': 'Testing cancelled successfully'
            })
        else:
            logger.warning(f"Could not cancel testing job {job_id} - job not found or not cancellable")
            return jsonify({
                'success': False,
                'message': 'Job not found or already completed'
            })
    except Exception as e:
        logger.error(f"Error cancelling testing job: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to cancel testing'
        }), 500


@websites_bp.route('/<website_id>/test-status')
def test_status(website_id):
    """Check testing status using database-backed job management"""
    from auto_a11y.core.website_manager import WebsiteManager
    from auto_a11y.core.job_manager import JobType
    
    # Get job_id from request args if provided
    job_id = request.args.get('job_id')
    
    # Get fresh website data from database
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    # If a specific job_id is provided, get its status
    if job_id:
        website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
        job_status = website_manager.get_job_status(job_id)
        
        if job_status:
            status = job_status.get('status', 'unknown')
            progress = job_status.get('progress', {})
            details = progress.get('details', {})
            
            return jsonify({
                'status': status,
                'job_id': job_id,
                'pages_tested': details.get('pages_tested', 0),
                'pages_passed': details.get('pages_passed', 0),
                'pages_failed': details.get('pages_failed', 0),
                'pages_skipped': details.get('pages_skipped', 0),
                'total_pages': details.get('total_pages', 0),
                'current_page': details.get('current_page', ''),
                'message': progress.get('message', ''),
                'error': job_status.get('error'),
                'all_complete': status in ['completed', 'failed', 'cancelled']
            })
    
    # Otherwise, get page-level status (for backward compatibility)
    pages = current_app.db.get_pages(website_id)
    
    # Count pages by status
    total_pages = len(pages)
    tested_pages = sum(1 for p in pages if p.status == PageStatus.TESTED)
    testing_pages = sum(1 for p in pages if p.status == PageStatus.TESTING)
    queued_pages = sum(1 for p in pages if p.status == PageStatus.QUEUED)
    error_pages = sum(1 for p in pages if p.status == PageStatus.ERROR)
    
    # Check if all pages are complete (tested or error)
    all_complete = (testing_pages == 0 and queued_pages == 0)
    
    # Get last tested time - refresh from database to get latest
    if all_complete:
        # Refresh website data to get the updated last_tested
        website = current_app.db.get_website(website_id)
    
    last_tested = None
    if website and website.last_tested:
        last_tested = website.last_tested.strftime('%Y-%m-%d %H:%M')
    
    return jsonify({
        'total_pages': total_pages,
        'tested_pages': tested_pages,
        'testing_pages': testing_pages,
        'queued_pages': queued_pages,
        'error_pages': error_pages,
        'all_complete': all_complete,
        'last_tested': last_tested,
        'message': f'Testing: {tested_pages}/{total_pages} complete'
    })