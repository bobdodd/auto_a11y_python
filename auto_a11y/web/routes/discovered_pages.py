"""
Discovered Page management routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from bson import ObjectId
from datetime import datetime
import logging

from auto_a11y.models import DiscoveredPage, DrupalSyncStatus
from auto_a11y.drupal import DrupalJSONAPIClient, DiscoveredPageTaxonomies
from auto_a11y.drupal.config import get_drupal_config

logger = logging.getLogger(__name__)
discovered_pages_bp = Blueprint('discovered_pages', __name__)


@discovered_pages_bp.route('/discovered-pages/<page_id>')
def view_discovered_page(page_id):
    """View and edit a discovered page"""
    try:
        db = current_app.db

        # Get the discovered page
        page_doc = db.discovered_pages.find_one({'_id': ObjectId(page_id)})
        if not page_doc:
            flash('Discovered page not found', 'error')
            return redirect(url_for('projects.list_projects'))

        page = DiscoveredPage.from_dict(page_doc)

        # Get the project
        project_doc = db.projects.find_one({'_id': ObjectId(page.project_id)})
        if not project_doc:
            flash('Associated project not found', 'error')
            return redirect(url_for('projects.list_projects'))

        from auto_a11y.models import Project
        project = Project.from_dict(project_doc)

        # Fetch taxonomy terms for the edit form
        interested_because_terms = []
        page_elements_terms = []

        try:
            drupal_config = get_drupal_config()
            if drupal_config.enabled:
                client = DrupalJSONAPIClient(
                    base_url=drupal_config.base_url,
                    username=drupal_config.username,
                    password=drupal_config.password
                )
                taxonomies = DiscoveredPageTaxonomies(client)
                interested_because_terms = taxonomies.get_interested_because_terms()
                page_elements_terms = taxonomies.get_page_elements_terms()
        except Exception as e:
            logger.warning(f"Could not fetch taxonomy terms: {e}")
            # Continue without taxonomies - form will fall back to text input

        return render_template(
            'discovered_pages/view.html',
            page=page,
            project=project,
            interested_because_terms=interested_because_terms,
            page_elements_terms=page_elements_terms
        )

    except Exception as e:
        logger.error(f"Error viewing discovered page: {e}")
        flash(f'Error loading page: {e}', 'error')
        return redirect(url_for('projects.list_projects'))


@discovered_pages_bp.route('/discovered-pages/<page_id>/edit', methods=['POST'])
def edit_discovered_page(page_id):
    """Update a discovered page"""
    try:
        db = current_app.db

        # Get the discovered page
        page_doc = db.discovered_pages.find_one({'_id': ObjectId(page_id)})
        if not page_doc:
            return jsonify({'success': False, 'error': 'Page not found'}), 404

        page = DiscoveredPage.from_dict(page_doc)

        # Update fields from form
        data = request.get_json() if request.is_json else request.form

        page.title = data.get('title', page.title)
        page.url = data.get('url', page.url)
        page.private_notes = data.get('private_notes', page.private_notes)
        page.public_notes = data.get('public_notes', page.public_notes)
        page.include_in_report = data.get('include_in_report', 'false').lower() == 'true'
        page.audited = data.get('audited', 'false').lower() == 'true'
        page.manual_audit = data.get('manual_audit', 'false').lower() == 'true'

        # Handle interested_because (can be list from checkboxes or comma-separated string)
        if request.is_json:
            interested_because = data.get('interested_because', [])
            if isinstance(interested_because, str):
                page.interested_because = [s.strip() for s in interested_because.split(',') if s.strip()]
            else:
                page.interested_because = interested_because
        else:
            # Form data - getlist for checkboxes
            page.interested_because = request.form.getlist('interested_because')

        # Handle page_elements (can be list from checkboxes or comma-separated string)
        if request.is_json:
            page_elements = data.get('page_elements', [])
            if isinstance(page_elements, str):
                page.page_elements = [s.strip() for s in page_elements.split(',') if s.strip()]
            else:
                page.page_elements = page_elements
        else:
            # Form data - getlist for checkboxes
            page.page_elements = request.form.getlist('page_elements')

        page.updated_at = datetime.now()

        # Mark as needing sync if it was previously synced
        if page.drupal_sync_status == DrupalSyncStatus.SYNCED:
            page.drupal_sync_status = DrupalSyncStatus.PENDING

        # Save to database
        db.discovered_pages.update_one(
            {'_id': ObjectId(page_id)},
            {'$set': page.to_dict()}
        )

        if request.is_json:
            return jsonify({'success': True, 'message': 'Page updated successfully'})
        else:
            flash('Page updated successfully', 'success')
            return redirect(url_for('discovered_pages.view_discovered_page', page_id=page_id))

    except Exception as e:
        logger.error(f"Error updating discovered page: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Error updating page: {e}', 'error')
            return redirect(url_for('discovered_pages.view_discovered_page', page_id=page_id))


@discovered_pages_bp.route('/discovered-pages/<page_id>/delete', methods=['POST'])
def delete_discovered_page(page_id):
    """Delete a discovered page"""
    try:
        db = current_app.db

        # Get the page to find its project
        page_doc = db.discovered_pages.find_one({'_id': ObjectId(page_id)})
        if not page_doc:
            return jsonify({'success': False, 'error': 'Page not found'}), 404

        project_id = page_doc.get('project_id')

        # Delete the page
        result = db.discovered_pages.delete_one({'_id': ObjectId(page_id)})

        if result.deleted_count > 0:
            if request.is_json:
                return jsonify({'success': True, 'message': 'Page deleted successfully'})
            else:
                flash('Page deleted successfully', 'success')
                return redirect(url_for('projects.view_project', project_id=project_id))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Page not found'}), 404
            else:
                flash('Page not found', 'error')
                return redirect(url_for('projects.list_projects'))

    except Exception as e:
        logger.error(f"Error deleting discovered page: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Error deleting page: {e}', 'error')
            return redirect(url_for('projects.list_projects'))
