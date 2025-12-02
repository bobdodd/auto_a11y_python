"""
Project management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_babel import gettext as _
from auto_a11y.models import Project, ProjectStatus, ProjectType
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


@projects_bp.route('/api/test-details/<test_id>')
def api_test_details(test_id):
    """API endpoint to get detailed information about a test"""
    try:
        from auto_a11y.reporting.issue_catalog import IssueCatalog
        from auto_a11y.reporting.issue_descriptions_translated import get_detailed_issue_description

        # Get test details from the issue catalog
        test_info = IssueCatalog.get_issue(test_id)

        if not test_info:
            return jsonify({
                'success': False,
                'error': f'Test {test_id} not found in catalog'
            }), 404

        # Get production_ready status from database
        doc_status = current_app.db.get_issue_documentation_status(test_id)
        production_ready = doc_status.get('production_ready', False) if doc_status else False

        # Get enhanced description with message templates
        enhanced_info = get_detailed_issue_description(test_id)

        # Build response with both catalog and enhanced info
        response_data = {
            'id': test_info.get('id', test_id),
            'type': test_info.get('type', 'Unknown'),
            'impact': test_info.get('impact', 'Unknown'),
            'wcag': test_info.get('wcag', []),
            'wcag_full': test_info.get('wcag_full', ''),
            'category': test_info.get('category', ''),
            'description': test_info.get('description', 'No description available'),
            'why_it_matters': test_info.get('why_it_matters', ''),
            'who_it_affects': test_info.get('who_it_affects', ''),
            'how_to_fix': test_info.get('how_to_fix', ''),
            'production_ready': production_ready
        }

        # Add message template info if available
        if enhanced_info:
            response_data['message_template'] = {
                'title': enhanced_info.get('title', ''),
                'what': enhanced_info.get('what', ''),
                'why': enhanced_info.get('why', ''),
                'remediation': enhanced_info.get('remediation', '')
            }

        return jsonify({
            'success': True,
            'test': response_data
        })
    except Exception as e:
        logger.error(f"Error getting test details for {test_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@projects_bp.route('/api/test-details/<test_id>/production-ready', methods=['POST'])
def api_set_test_production_ready(test_id):
    """API endpoint to toggle production_ready flag for a test"""
    try:
        from auto_a11y.reporting.issue_catalog import IssueCatalog

        # Verify test exists in catalog
        test_info = IssueCatalog.get_issue(test_id)
        if not test_info:
            return jsonify({
                'success': False,
                'error': f'Test {test_id} not found in catalog'
            }), 404

        # Get the new value from request
        data = request.get_json()
        production_ready = data.get('production_ready', False)

        # Update in database
        success = current_app.db.set_issue_production_ready(
            test_id,
            production_ready,
            updated_by="web_user"
        )

        if success:
            return jsonify({
                'success': True,
                'message': f'Production ready status updated for {test_id}',
                'production_ready': production_ready
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update production ready status'
            }), 500

    except Exception as e:
        logger.error(f"Error setting production ready for {test_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@projects_bp.route('/api/issue-documentation-stats')
def api_issue_documentation_stats():
    """API endpoint to get statistics about issue documentation status"""
    try:
        from auto_a11y.reporting.issue_catalog import IssueCatalog

        # Get all issue codes from catalog
        all_codes = list(IssueCatalog.ISSUES.keys())

        # Get production ready statuses from database
        statuses = current_app.db.get_all_issue_documentation_statuses()

        # Calculate stats
        production_ready_count = sum(1 for ready in statuses.values() if ready)
        total_count = len(all_codes)
        pending_count = total_count - production_ready_count

        # Get lists
        production_ready_codes = [code for code, ready in statuses.items() if ready]
        pending_codes = [code for code in all_codes if not statuses.get(code, False)]

        return jsonify({
            'success': True,
            'stats': {
                'total': total_count,
                'production_ready': production_ready_count,
                'pending': pending_count,
                'percentage_ready': round(production_ready_count * 100 / total_count, 1) if total_count > 0 else 0
            },
            'production_ready_codes': production_ready_codes,
            'pending_codes': pending_codes
        })

    except Exception as e:
        logger.error(f"Error getting documentation stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
        project_type_value = request.form.get('project_type', 'website')

        # Parse project type
        try:
            project_type = ProjectType(project_type_value)
        except ValueError:
            project_type = ProjectType.WEBSITE

        # Get type-specific fields
        app_identifier = request.form.get('app_identifier', '').strip() or None
        device_model = request.form.get('device_model', '').strip() or None
        location = request.form.get('location', '').strip() or None
        drupal_audit_name = request.form.get('drupal_audit_name', '').strip() or None

        if not name:
            flash('Project name is required', 'error')
            # Redirect to GET handler which will populate everything
            return redirect(url_for('projects.create_project'))
        
        # Check if project name exists
        existing = current_app.db.projects.find_one({'name': name})
        if existing:
            flash(f'Project "{name}" already exists', 'error')
            # Redirect to GET handler which will populate everything
            return redirect(url_for('projects.create_project'))
        
        # Get touchpoint configuration
        from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING
        
        touchpoints_config = {}
        touchpoint_ids = [
            'headings', 'images', 'forms', 'buttons', 'links', 'navigation',
            'colors_contrast', 'keyboard_navigation', 'landmarks', 'language',
            'tables', 'lists', 'media', 'dialogs', 'animation', 'timing',
            'fonts', 'semantic_structure', 'aria', 'focus_management',
            'reading_order', 'event_handling', 'accessible_names', 'page',
            'title_attributes'
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

        # Get stealth mode configuration
        stealth_mode = request.form.get('stealth_mode') == 'true'

        # Get page load strategy
        page_load_strategy = request.form.get('page_load_strategy', 'networkidle2')

        # Get headless browser setting
        headless_browser = request.form.get('headless_browser', 'default')

        # Create project with WCAG level, touchpoints, AI config, and stealth mode
        project = Project(
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
            project_type=project_type,
            app_identifier=app_identifier,
            device_model=device_model,
            location=location,
            drupal_audit_name=drupal_audit_name,
            config={
                'wcag_level': wcag_level,
                'page_load_strategy': page_load_strategy,
                'headless_browser': headless_browser,
                'touchpoints': touchpoints_config,
                'enable_ai_testing': enable_ai_testing,
                'ai_tests': ai_tests,
                'stealth_mode': stealth_mode
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

    # Group tests by touchpoint dynamically
    from collections import defaultdict
    tests_by_touchpoint = defaultdict(list)

    # Map fixture directory names to UI touchpoint names
    touchpoint_mapping = {
        'ARIA': 'aria',
        'AccessibleNames': 'accessible_names',
        'Animation': 'animation',
        'Animations': 'animation',
        'Buttons': 'buttons',
        'Colors': 'colors_contrast',
        'ColorsAndContrast': 'colors_contrast',
        'Contrast': 'colors_contrast',
        'DialogsAndModals': 'dialogs',
        'Modals': 'dialogs',
        'Documents': 'documents',
        'EventHandling': 'event_handling',
        'Focus': 'focus_management',
        'Fonts': 'fonts',
        'Forms': 'forms',
        'Headings': 'headings',
        'IFrames': 'iframes',
        'Images': 'images',
        'SVG': 'images',
        'Interactive': 'aria',
        'Keyboard': 'keyboard_navigation',
        'Tabindex': 'keyboard_navigation',
        'Landmarks': 'landmarks',
        'Language': 'language',
        'Links': 'links',
        'Lists': 'lists',
        'Maps': 'maps',
        'Media': 'media',
        'Video': 'media',
        'Audio': 'media',
        'Navigation': 'navigation',
        'ReadingOrder': 'reading_order',
        'Semantic': 'semantic_structure',
        'SemanticStructure': 'semantic_structure',
        'Structure': 'semantic_structure',
        'DocumentType': 'semantic_structure',
        'Page': 'page',
        'PageTitle': 'page',
        'Tables': 'tables',
        'Timing': 'timing',
        'TitleAttributes': 'title_attributes',
        'Typography': 'fonts',
        'Style': 'styles',
        'Styles': 'styles'
    }

    # Touchpoint display names (ordered)
    touchpoint_names = {
        'accessible_names': _('Accessible Names'),
        'animation': _('Animation'),
        'aria': _('ARIA'),
        'buttons': _('Buttons'),
        'colors_contrast': _('Colors & Contrast'),
        'dialogs': _('Dialogs & Modals'),
        'documents': _('Documents'),
        'event_handling': _('Event Handling'),
        'focus_management': _('Focus Management'),
        'forms': _('Forms'),
        'headings': _('Headings'),
        'iframes': _('Iframes'),
        'styles': _('Inline Styles'),
        'images': _('Images'),
        'keyboard_navigation': _('Keyboard Navigation'),
        'landmarks': _('Landmarks'),
        'language': _('Language'),
        'links': _('Links'),
        'lists': _('Lists'),
        'maps': _('Maps'),
        'media': _('Media'),
        'navigation': _('Navigation'),
        'page': _('Page'),
        'reading_order': _('Reading Order'),
        'semantic_structure': _('Semantic Structure'),
        'tables': _('Tables'),
        'timing': _('Timing'),
        'title_attributes': _('Title Attributes'),
        'fonts': _('Fonts'),
        'other': _('Other')
    }

    # Group all tests by touchpoint
    for error_code, status in test_statuses.items():
        # Try to determine touchpoint from fixture paths
        fixture_paths = status.get('fixture_paths', [])
        if fixture_paths:
            # Get directory from first fixture path
            first_path = fixture_paths[0]
            if '/' in first_path:
                directory = first_path.split('/')[0]
                touchpoint = touchpoint_mapping.get(directory, 'other')
            else:
                touchpoint = 'other'
        else:
            touchpoint = 'other'

        tests_by_touchpoint[touchpoint].append(error_code)

    # Sort tests within each touchpoint
    for touchpoint in tests_by_touchpoint:
        tests_by_touchpoint[touchpoint].sort()

    # Get production ready statuses for all tests
    production_ready_statuses = current_app.db.get_all_issue_documentation_statuses()

    # DEBUG: Log what we're passing to template
    logger.warning(f"DEBUG: Create Project - tests_by_touchpoint keys: {sorted(tests_by_touchpoint.keys())}")
    if 'links' in tests_by_touchpoint:
        logger.warning(f"DEBUG: Links touchpoint has {len(tests_by_touchpoint['links'])} tests")
    else:
        logger.warning(f"DEBUG: 'links' key NOT in tests_by_touchpoint!")
    logger.warning(f"DEBUG: Total passing_tests: {len(passing_tests)}")
    logger.warning(f"DEBUG: Total test_statuses: {len(test_statuses)}")

    return render_template('projects/create.html',
                         test_statuses=test_statuses,
                         passing_tests=passing_tests,
                         debug_mode=debug_mode,
                         tests_by_touchpoint=dict(tests_by_touchpoint),
                         touchpoint_names=touchpoint_names,
                         production_ready_statuses=production_ready_statuses)


@projects_bp.route('/<project_id>')
def view_project(project_id):
    """View project details"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))

    websites = current_app.db.get_websites(project_id)
    stats = current_app.db.get_project_stats(project_id)

    # Calculate stats for each website (violations and warnings)
    website_stats = {}
    for website in websites:
        pages = current_app.db.get_pages(website.id)
        violations = sum(page.violation_count for page in pages)
        warnings = sum(page.warning_count for page in pages)
        website_stats[website.id] = {
            'violations': violations,
            'warnings': warnings
        }

    # Get available test users for this project (for discovery modal)
    project_users = current_app.db.get_project_users(project_id, enabled_only=True)

    # Get recordings for this project
    recordings = current_app.db.get_recordings(project_id=project_id)

    # Get discovered pages for this project
    discovered_pages_cursor = current_app.db.discovered_pages.find({'project_id': project_id}).sort('created_at', -1)
    discovered_pages = list(discovered_pages_cursor)

    return render_template('projects/view.html',
                         project=project,
                         websites=websites,
                         stats=stats,
                         website_stats=website_stats,
                         project_users=project_users,
                         recordings=recordings,
                         discovered_pages=discovered_pages)


@projects_bp.route('/<project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit project"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.list_projects'))

    # Import TOUCHPOINT_TEST_MAPPING for rendering the form
    from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING

    # Build touchpoint data structure for the template
    touchpoint_names = {
        'headings': _('Headings'),
        'images': _('Images'),
        'forms': _('Forms'),
        'buttons': _('Buttons'),
        'links': _('Links'),
        'navigation': _('Navigation'),
        'colors_contrast': _('Colors & Contrast'),
        'keyboard_navigation': _('Keyboard Navigation'),
        'landmarks': _('Landmarks'),
        'language': _('Language'),
        'tables': _('Tables'),
        'lists': _('Lists'),
        'media': _('Media'),
        'dialogs': _('Dialogs & Modals'),
        'animation': _('Animation'),
        'timing': _('Timing'),
        'fonts': _('Fonts'),
        'semantic_structure': _('Semantic Structure'),
        'aria': _('ARIA'),
        'focus_management': _('Focus Management'),
        'reading_order': _('Reading Order'),
        'event_handling': _('Event Handling'),
        'accessible_names': _('Accessible Names'),
        'page': _('Page'),
        'documents': _('Documents'),
        'maps': _('Maps'),
        'styles': _('Inline Styles'),
        'iframes': _('Iframes')
    }

    if request.method == 'POST':
        project.name = request.form.get('name', project.name)
        project.description = request.form.get('description', project.description)
        status = request.form.get('status', project.status.value)
        project.status = ProjectStatus(status)

        # Update Drupal audit name
        drupal_audit_name = request.form.get('drupal_audit_name', '').strip() or None
        project.drupal_audit_name = drupal_audit_name

        # Update WCAG level in config
        wcag_level = request.form.get('wcag_level', 'AA')
        if not project.config:
            project.config = {}
        project.config['wcag_level'] = wcag_level

        # Update page load strategy in config
        page_load_strategy = request.form.get('page_load_strategy', 'networkidle2')
        project.config['page_load_strategy'] = page_load_strategy

        # Update headless browser setting in config
        headless_browser = request.form.get('headless_browser', 'default')
        project.config['headless_browser'] = headless_browser

        # Update page title length limit
        try:
            title_length_limit = int(request.form.get('title_length_limit', 60))
            # Validate range
            if 30 <= title_length_limit <= 120:
                project.config['titleLengthLimit'] = title_length_limit
            else:
                project.config['titleLengthLimit'] = 60
        except (ValueError, TypeError):
            project.config['titleLengthLimit'] = 60

        # Update heading length limit
        try:
            heading_length_limit = int(request.form.get('heading_length_limit', 60))
            # Validate range
            if 30 <= heading_length_limit <= 120:
                project.config['headingLengthLimit'] = heading_length_limit
            else:
                project.config['headingLengthLimit'] = 60
        except (ValueError, TypeError):
            project.config['headingLengthLimit'] = 60

        # Update touchpoint configuration
        from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING
        
        touchpoints_config = {}
        touchpoint_ids = [
            'headings', 'images', 'forms', 'buttons', 'links', 'navigation',
            'colors_contrast', 'keyboard_navigation', 'landmarks', 'language',
            'tables', 'lists', 'media', 'dialogs', 'animation', 'timing',
            'fonts', 'semantic_structure', 'aria', 'focus_management',
            'reading_order', 'event_handling', 'accessible_names', 'page',
            'title_attributes'
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

        # Update stealth mode configuration
        stealth_mode = request.form.get('stealth_mode') == 'true'
        project.config['stealth_mode'] = stealth_mode

        # Update font accessibility configuration
        use_default_fonts = request.form.get('use_default_fonts') == 'on'
        additional_fonts_raw = request.form.get('additional_inaccessible_fonts', '').strip()
        excluded_fonts_raw = request.form.get('excluded_fonts', '').strip()

        # Parse textarea input (one font per line)
        additional_fonts = [f.strip().lower() for f in additional_fonts_raw.split('\n') if f.strip()]
        excluded_fonts = [f.strip().lower() for f in excluded_fonts_raw.split('\n') if f.strip()]

        project.config['font_accessibility'] = {
            'use_defaults': use_default_fonts,
            'additional_inaccessible_fonts': additional_fonts,
            'excluded_fonts': excluded_fonts
        }

        if current_app.db.update_project(project):
            flash('Project updated successfully', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        else:
            flash('Failed to update project', 'error')

    return render_template('projects/edit.html',
                         project=project,
                         touchpoint_names=touchpoint_names,
                         touchpoint_test_mapping=TOUCHPOINT_TEST_MAPPING)


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
        # Create browser config with project-specific stealth_mode setting
        browser_config = current_app.app_config.__dict__.copy()
        if project and project.config:
            browser_config['stealth_mode'] = project.config.get('stealth_mode', False)
        else:
            browser_config['stealth_mode'] = False

        # Initialize website manager
        manager = WebsiteManager(current_app.db, browser_config)
        logger.info(f"Created website manager for project {project_id} testing (stealth_mode: {browser_config.get('stealth_mode', False)})")
        
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


@projects_bp.route('/api/<project_id>/users')
def api_get_project_users(project_id):
    """API endpoint to get project users"""
    try:
        project_users = current_app.db.get_project_users(project_id, enabled_only=True)

        return jsonify({
            'success': True,
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'display_name': user.display_name,
                    'roles': user.roles
                } for user in project_users
            ]
        })
    except Exception as e:
        logger.error(f"Error fetching project users: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@projects_bp.route('/api/<project_id>/details')
def api_get_project(project_id):
    """API endpoint to get project details including testers and supervisors"""
    try:
        project = current_app.db.get_project(project_id)
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404

        return jsonify({
            'success': True,
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'project_type': project.project_type.value,
                'lived_experience_testers': [t.to_dict() for t in project.lived_experience_testers],
                'test_supervisors': [s.to_dict() for s in project.test_supervisors]
            }
        })
    except Exception as e:
        logger.error(f"Error fetching project: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@projects_bp.route('/api/<project_id>/discovered-pages')
def api_get_discovered_pages(project_id):
    """API endpoint to get discovered pages for a project"""
    try:
        db = current_app.db

        # Query discovered pages for this project
        discovered_pages_docs = db.discovered_pages.find({'project_id': project_id})

        # Convert to list of dicts
        pages = []
        for doc in discovered_pages_docs:
            pages.append({
                '_id': str(doc['_id']),
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'interested_because': doc.get('interested_because', []),
                'page_elements': doc.get('page_elements', [])
            })

        return jsonify({
            'success': True,
            'discovered_pages': pages
        })
    except Exception as e:
        logger.error(f"Error fetching discovered pages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500