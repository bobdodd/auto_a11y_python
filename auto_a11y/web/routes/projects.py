"""
Project management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from auto_a11y.models import Project, ProjectStatus
import logging

logger = logging.getLogger(__name__)
projects_bp = Blueprint('projects', __name__)


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
        
        if not name:
            flash('Project name is required', 'error')
            return render_template('projects/create.html')
        
        # Check if project name exists
        existing = current_app.db.projects.find_one({'name': name})
        if existing:
            flash(f'Project "{name}" already exists', 'error')
            return render_template('projects/create.html')
        
        # Create project
        project = Project(
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE
        )
        
        project_id = current_app.db.create_project(project)
        flash(f'Project "{name}" created successfully', 'success')
        
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    return render_template('projects/create.html')


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