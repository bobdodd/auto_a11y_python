"""
Routes for managing project participants (lived experience testers and test supervisors)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from auto_a11y.models import LivedExperienceTester, TestSupervisor
import logging

logger = logging.getLogger(__name__)

project_participants_bp = Blueprint('project_participants', __name__)


@project_participants_bp.route('/projects/<project_id>/participants')
def list_participants(project_id):
    """List all lived experience testers and supervisors for a project"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('index'))

    return render_template('project_participants/list.html',
                         project=project,
                         testers=project.lived_experience_testers,
                         supervisors=project.test_supervisors)


# ===== TESTER ROUTES =====

@project_participants_bp.route('/projects/<project_id>/participants/testers/create', methods=['GET', 'POST'])
def create_tester(project_id):
    """Create a new lived experience tester"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            data = request.form

            # Parse assistive technologies from comma-separated string
            assistive_tech_str = data.get('assistive_tech', '').strip()
            assistive_tech = [a.strip() for a in assistive_tech_str.split(',') if a.strip()] if assistive_tech_str else []

            # Create tester
            tester = LivedExperienceTester(
                name=data.get('name', '').strip(),
                email=data.get('email', '').strip() or None,
                disability_type=data.get('disability_type', '').strip() or None,
                assistive_tech=assistive_tech,
                notes=data.get('notes', '').strip() or None
            )

            # Add to project (this auto-generates ID and updates timestamp)
            project.add_tester(tester)
            current_app.db.update_project(project)

            flash(f'Lived experience tester "{tester.name}" added successfully', 'success')
            return redirect(url_for('project_participants.list_participants', project_id=project_id))

        except Exception as e:
            logger.error(f"Error creating tester: {e}")
            flash(f'Error creating tester: {str(e)}', 'error')

    return render_template('project_participants/create_tester.html', project=project)


@project_participants_bp.route('/projects/<project_id>/participants/testers/<tester_id>/edit', methods=['GET', 'POST'])
def edit_tester(project_id, tester_id):
    """Edit a lived experience tester"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('index'))

    tester = project.get_tester(tester_id)
    if not tester:
        flash('Tester not found', 'error')
        return redirect(url_for('project_participants.list_participants', project_id=project_id))

    if request.method == 'POST':
        try:
            data = request.form

            # Parse assistive technologies
            assistive_tech_str = data.get('assistive_tech', '').strip()
            assistive_tech = [a.strip() for a in assistive_tech_str.split(',') if a.strip()] if assistive_tech_str else []

            # Update tester fields
            tester.name = data.get('name', '').strip()
            tester.email = data.get('email', '').strip() or None
            tester.disability_type = data.get('disability_type', '').strip() or None
            tester.assistive_tech = assistive_tech
            tester.notes = data.get('notes', '').strip() or None

            # Update in project
            project.update_tester(tester)
            current_app.db.update_project(project)

            flash(f'Tester "{tester.name}" updated successfully', 'success')
            return redirect(url_for('project_participants.list_participants', project_id=project_id))

        except Exception as e:
            logger.error(f"Error updating tester: {e}")
            flash(f'Error updating tester: {str(e)}', 'error')

    return render_template('project_participants/edit_tester.html',
                         project=project,
                         tester=tester)


@project_participants_bp.route('/projects/<project_id>/participants/testers/<tester_id>/delete', methods=['POST'])
def delete_tester(project_id, tester_id):
    """Delete a lived experience tester"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    try:
        success = project.remove_tester(tester_id)
        if success:
            current_app.db.update_project(project)
            return jsonify({
                'success': True,
                'message': 'Tester deleted successfully',
                'redirect': url_for('project_participants.list_participants', project_id=project_id)
            })
        else:
            return jsonify({'error': 'Tester not found'}), 404

    except Exception as e:
        logger.error(f"Error deleting tester: {e}")
        return jsonify({'error': str(e)}), 500


# ===== SUPERVISOR ROUTES =====

@project_participants_bp.route('/projects/<project_id>/participants/supervisors/create', methods=['GET', 'POST'])
def create_supervisor(project_id):
    """Create a new test supervisor"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            data = request.form

            # Create supervisor
            supervisor = TestSupervisor(
                name=data.get('name', '').strip(),
                email=data.get('email', '').strip() or None,
                role=data.get('role', '').strip() or None,
                organization=data.get('organization', '').strip() or None,
                notes=data.get('notes', '').strip() or None
            )

            # Add to project (this auto-generates ID and updates timestamp)
            project.add_supervisor(supervisor)
            current_app.db.update_project(project)

            flash(f'Test supervisor "{supervisor.name}" added successfully', 'success')
            return redirect(url_for('project_participants.list_participants', project_id=project_id))

        except Exception as e:
            logger.error(f"Error creating supervisor: {e}")
            flash(f'Error creating supervisor: {str(e)}', 'error')

    return render_template('project_participants/create_supervisor.html', project=project)


@project_participants_bp.route('/projects/<project_id>/participants/supervisors/<supervisor_id>/edit', methods=['GET', 'POST'])
def edit_supervisor(project_id, supervisor_id):
    """Edit a test supervisor"""
    project = current_app.db.get_project(project_id)
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('index'))

    supervisor = project.get_supervisor(supervisor_id)
    if not supervisor:
        flash('Supervisor not found', 'error')
        return redirect(url_for('project_participants.list_participants', project_id=project_id))

    if request.method == 'POST':
        try:
            data = request.form

            # Update supervisor fields
            supervisor.name = data.get('name', '').strip()
            supervisor.email = data.get('email', '').strip() or None
            supervisor.role = data.get('role', '').strip() or None
            supervisor.organization = data.get('organization', '').strip() or None
            supervisor.notes = data.get('notes', '').strip() or None

            # Update in project
            project.update_supervisor(supervisor)
            current_app.db.update_project(project)

            flash(f'Supervisor "{supervisor.name}" updated successfully', 'success')
            return redirect(url_for('project_participants.list_participants', project_id=project_id))

        except Exception as e:
            logger.error(f"Error updating supervisor: {e}")
            flash(f'Error updating supervisor: {str(e)}', 'error')

    return render_template('project_participants/edit_supervisor.html',
                         project=project,
                         supervisor=supervisor)


@project_participants_bp.route('/projects/<project_id>/participants/supervisors/<supervisor_id>/delete', methods=['POST'])
def delete_supervisor(project_id, supervisor_id):
    """Delete a test supervisor"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    try:
        success = project.remove_supervisor(supervisor_id)
        if success:
            current_app.db.update_project(project)
            return jsonify({
                'success': True,
                'message': 'Supervisor deleted successfully',
                'redirect': url_for('project_participants.list_participants', project_id=project_id)
            })
        else:
            return jsonify({'error': 'Supervisor not found'}), 404

    except Exception as e:
        logger.error(f"Error deleting supervisor: {e}")
        return jsonify({'error': str(e)}), 500
