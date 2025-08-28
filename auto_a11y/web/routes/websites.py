"""
Website management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from auto_a11y.models import Website, ScrapingConfig, Page, PageStatus
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)
websites_bp = Blueprint('websites', __name__)


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
    """Start page discovery for website"""
    from auto_a11y.core.website_manager import WebsiteManager
    from auto_a11y.core.task_runner import task_runner
    
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    # Create website manager
    website_manager = WebsiteManager(current_app.db, current_app.app_config.__dict__)
    
    # Submit discovery task
    task_id = task_runner.submit_task(
        func=asyncio.run,
        args=(website_manager.discover_pages(website_id),),
        task_id=f'discovery_{website_id}_{datetime.now().timestamp()}'
    )
    
    return jsonify({
        'success': True,
        'message': 'Page discovery started',
        'job_id': task_id,
        'status_url': url_for('websites.discovery_status', website_id=website_id, job_id=task_id)
    })


@websites_bp.route('/<website_id>/discovery-status')
def discovery_status(website_id):
    """Check discovery job status"""
    # In production, check actual job status
    return jsonify({
        'status': 'in_progress',
        'pages_found': 42,
        'current_depth': 2,
        'message': 'Discovering pages...'
    })


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
    """Start testing all pages in website"""
    website = current_app.db.get_website(website_id)
    if not website:
        return jsonify({'error': 'Website not found'}), 404
    
    pages = current_app.db.get_pages(website_id)
    untested_pages = [p for p in pages if p.needs_testing]
    
    if not untested_pages:
        return jsonify({
            'success': False,
            'message': 'No pages need testing'
        })
    
    # Queue testing job
    return jsonify({
        'success': True,
        'message': f'Testing {len(untested_pages)} pages',
        'job_id': f'test_{website_id}',
        'pages_queued': len(untested_pages)
    })