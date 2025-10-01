"""
Project management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from auto_a11y.models import Project, ProjectStatus
import logging

logger = logging.getLogger(__name__)
projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/api/list')
def api_list_projects():
    """API endpoint to list all projects"""
    try:
        projects = current_app.db.get_all_projects()
        return jsonify({
            'success': True,
            'projects': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description
                } for p in projects
            ]
        })
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@projects_bp.route('/api/<project_id>/websites')
def api_project_websites(project_id):
    """API endpoint to list websites in a project"""
    try:
        websites = current_app.db.get_websites(project_id)
        return jsonify({
            'success': True,
            'websites': [
                {
                    'id': w.id,
                    'name': w.name,
                    'url': w.url
                } for w in websites
            ]
        })
    except Exception as e:
        logger.error(f"Error listing project websites: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@projects_bp.route('/')
def list_projects():
    """List all projects"""
    status_filter = request.args.get('status')
    
    if status_filter:
        status = ProjectStatus(status_filter)
        projects = current_app.db.get_projects(status=status)
    else:
        projects = current_app.db.get_projects()
    
    return render_template('projects/list.html', projects=projects)


@projects_bp.route('/create', methods=['GET', 'POST'])
def create_project():
    """Create new project"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        wcag_level = request.form.get('wcag_level', 'AA')
        
        if not name:
            flash('Project name is required', 'error')
            # Get fixture test status for error case
            test_statuses = {}
            passing_tests = set()
            if hasattr(current_app, 'test_config') and current_app.test_config:
                test_statuses = current_app.test_config.get_all_test_statuses()
                if current_app.test_config.fixture_validator:
                    passing_tests = current_app.test_config.fixture_validator.get_passing_tests()
                debug_mode = current_app.test_config.debug_mode
            else:
                debug_mode = current_app.app_config.DEBUG
            return render_template('projects/create.html',
                                 test_statuses=test_statuses,
                                 passing_tests=passing_tests,
                                 debug_mode=debug_mode)
        
        # Check if project name exists
        existing = current_app.db.projects.find_one({'name': name})
        if existing:
            flash(f'Project "{name}" already exists', 'error')
            # Get fixture test status for error case
            test_statuses = {}
            passing_tests = set()
            if hasattr(current_app, 'test_config') and current_app.test_config:
                test_statuses = current_app.test_config.get_all_test_statuses()
                if current_app.test_config.fixture_validator:
                    passing_tests = current_app.test_config.fixture_validator.get_passing_tests()
                debug_mode = current_app.test_config.debug_mode
            else:
                debug_mode = current_app.app_config.DEBUG
            return render_template('projects/create.html',
                                 test_statuses=test_statuses,
                                 passing_tests=passing_tests,
                                 debug_mode=debug_mode)
        
        # Get touchpoint configuration
        from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING
        
        touchpoints_config = {}
        touchpoint_ids = [
            'headings', 'images', 'forms', 'buttons', 'links', 'navigation',
            'colors_contrast', 'keyboard_navigation', 'landmarks', 'language',
            'tables', 'lists', 'media', 'dialogs', 'animation', 'timing',
            'typography', 'semantic_structure', 'aria', 'focus_management',
            'reading_order', 'event_handling', 'accessible_names'
        ]
        
        for touchpoint_id in touchpoint_ids:
            enabled = request.form.get(f'touchpoint_{touchpoint_id}') == 'on'
            
            # Get individual test configurations for this touchpoint
            tests_config = {}
            test_ids = TOUCHPOINT_TEST_MAPPING.get(touchpoint_id, [])
            
            for test_id in test_ids:
                # Check if individual test checkbox exists and is checked
                test_enabled = request.form.get(f'test_{touchpoint_id}_{test_id}') == 'on'
                tests_config[test_id] = test_enabled
            
            touchpoints_config[touchpoint_id] = {
                'enabled': enabled,
                'tests': tests_config
            }
        
        # Get AI testing configuration
        enable_ai_testing = request.form.get('enable_ai_testing') == 'on'
        ai_tests = []
        if enable_ai_testing:
            # Collect selected AI tests
            for test_name in ['headings', 'reading_order', 'modals', 'language', 'animations', 'interactive']:
                if request.form.get(f'ai_test_{test_name}'):
                    ai_tests.append(test_name)
        
        # Create project with WCAG level, touchpoints, and AI config
        project = Project(
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
            config={
                'wcag_level': wcag_level,
                'touchpoints': touchpoints_config,
                'enable_ai_testing': enable_ai_testing,
                'ai_tests': ai_tests
            }
        )
        
        project_id = current_app.db.create_project(project)
        flash(f'Project "{name}" created successfully', 'success')
        
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Get fixture test status for all tests
    test_statuses = {}
    passing_tests = set()
    
    if hasattr(current_app, 'test_config') and current_app.test_config:
        test_statuses = current_app.test_config.get_all_test_statuses()
        if current_app.test_config.fixture_validator:
            passing_tests = current_app.test_config.fixture_validator.get_passing_tests()
        debug_mode = current_app.test_config.debug_mode
    else:
        debug_mode = current_app.app_config.DEBUG
    
    return render_template('projects/create.html',
                         test_statuses=test_statuses,
                         passing_tests=passing_tests,
                         debug_mode=debug_mode)


@projects_bp.route('/<project_id>')
def view_project(project_id):
    """View project details"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    websites = current_app.db.get_websites(project_id)
    stats = current_app.db.get_project_stats(project_id)
    
    return render_template('projects/view.html', 
                         project=project, 
                         websites=websites,
                         stats=stats)


@projects_bp.route('/<project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit project"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    if request.method == 'POST':
        project.name = request.form.get('name', project.name)
        project.description = request.form.get('description', project.description)
        status = request.form.get('status', project.status.value)
        project.status = ProjectStatus(status)
        
        # Update WCAG level in config
        wcag_level = request.form.get('wcag_level', 'AA')
        if not project.config:
            project.config = {}
        project.config['wcag_level'] = wcag_level
        
        # Update touchpoint configuration
        from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING
        
        touchpoints_config = {}
        touchpoint_ids = [
            'headings', 'images', 'forms', 'buttons', 'links', 'navigation',
            'colors_contrast', 'keyboard_navigation', 'landmarks', 'language',
            'tables', 'lists', 'media', 'dialogs', 'animation', 'timing',
            'typography', 'semantic_structure', 'aria', 'focus_management',
            'reading_order', 'event_handling', 'accessible_names'
        ]
        
        for touchpoint_id in touchpoint_ids:
            enabled = request.form.get(f'touchpoint_{touchpoint_id}') == 'on'
            
            # Get individual test configurations for this touchpoint
            tests_config = {}
            test_ids = TOUCHPOINT_TEST_MAPPING.get(touchpoint_id, [])
            
            for test_id in test_ids:
                # Check if individual test checkbox exists and is checked
                test_enabled = request.form.get(f'test_{touchpoint_id}_{test_id}') == 'on'
                tests_config[test_id] = test_enabled
            
            touchpoints_config[touchpoint_id] = {
                'enabled': enabled,
                'tests': tests_config
            }
        
        project.config['touchpoints'] = touchpoints_config
        
        # Update AI testing configuration
        enable_ai_testing = request.form.get('enable_ai_testing') == 'on'
        project.config['enable_ai_testing'] = enable_ai_testing
        
        ai_tests = []
        if enable_ai_testing:
            # Collect selected AI tests
            for test_name in ['headings', 'reading_order', 'modals', 'language', 'animations', 'interactive']:
                if request.form.get(f'ai_test_{test_name}'):
                    ai_tests.append(test_name)
        project.config['ai_tests'] = ai_tests
        
        if current_app.db.update_project(project):
            flash('Project updated successfully', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        else:
            flash('Failed to update project', 'error')
    
    return render_template('projects/edit.html', project=project)


@projects_bp.route('/<project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete project"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    if current_app.db.delete_project(project_id):
        flash(f'Project "{project.name}" deleted successfully', 'success')
    else:
        flash('Failed to delete project', 'error')
    
    return redirect(url_for('projects.list_projects'))


@projects_bp.route('/<project_id>/add-website', methods=['POST'])
def add_website(project_id):
    """Add website to project"""
    from auto_a11y.models import Website, ScrapingConfig
    
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    url = request.form.get('url')
    name = request.form.get('name', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create website
    website = Website(
        project_id=project_id,
        url=url,
        name=name,
        scraping_config=ScrapingConfig()
    )
    
    website_id = current_app.db.create_website(website)
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'website_id': website_id,
            'redirect': url_for('websites.view_website', website_id=website_id)
        })
    else:
        # Regular form submission - redirect directly
        flash(f'Website "{name or url}" added successfully', 'success')
        return redirect(url_for('websites.view_website', website_id=website_id))


@projects_bp.route('/<project_id>/test-all', methods=['POST'])
def test_project(project_id):
    """Test all websites in a project"""
    import asyncio
    from auto_a11y.core.website_manager import WebsiteManager
    
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    # Get test parameters
    take_screenshot = request.form.get('take_screenshot', 'true') == 'true'
    run_ai = request.form.get('run_ai', 'false') == 'true'
    test_all = request.form.get('test_all', 'true') == 'true'
    
    try:
        # Initialize website manager
        manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
        
        # Generate unique job ID
        import uuid
        job_id = f"proj_{project_id}_{uuid.uuid4().hex[:8]}"
        
        # Run project-level testing
        # Try to get the running loop, or create a new one
        try:
            loop = asyncio.get_running_loop()
            logger.info("Using existing event loop for project testing")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info("Created new event loop for project testing")
        
        try:
            jobs = loop.run_until_complete(manager.test_project(
                project_id=project_id,
                job_id=job_id,
                test_all=test_all,
                take_screenshot=take_screenshot,
                run_ai_analysis=run_ai
            ))
        finally:
            # Don't close the loop immediately if it's running
            try:
                if not loop.is_running():
                    loop.close()
                    logger.info("Closed project testing event loop")
            except:
                pass
        
        if jobs:
            flash(f'Started testing {len(jobs)} websites in project "{project.name}"', 'success')
        else:
            flash('No websites found to test in this project', 'warning')
        
    except Exception as e:
        logger.error(f"Failed to start project testing: {e}")
        flash(f'Failed to start testing: {str(e)}', 'error')
    
    return redirect(url_for('projects.view_project', project_id=project_id))


@projects_bp.route('/<project_id>/report', methods=['GET', 'POST'])
def generate_project_report(project_id):
    """Generate accessibility report for entire project"""
    from auto_a11y.reporting.project_report import ProjectReport
    from flask import send_file
    from pathlib import Path
    
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))
    
    format = request.args.get('format', 'html')
    
    try:
        # Get all websites and pages for the project
        websites = current_app.db.get_websites(project_id)
        pages_by_website = {}
        
        for website in websites:
            pages = current_app.db.get_pages(website.id)
            pages_by_website[website.id] = pages
        
        # Generate report
        report = ProjectReport(current_app.db, project, websites, pages_by_website)
        report.generate()
        
        # Save and return report
        report_path = report.save(format)
        report_path = Path(report_path)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_path.name,
            mimetype={
                'html': 'text/html',
                'json': 'application/json'
            }.get(format, 'application/octet-stream')
        )
        
    except Exception as e:
        logger.error(f"Failed to generate project report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))