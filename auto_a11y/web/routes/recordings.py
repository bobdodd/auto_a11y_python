"""
Recording management routes for manual audits
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, current_app
)
from werkzeug.utils import secure_filename
import logging
import json
from pathlib import Path
from datetime import datetime

from auto_a11y.models import Recording, RecordingIssue, AuditType
from auto_a11y.importers import DictaphoneImporter

logger = logging.getLogger(__name__)
recordings_bp = Blueprint('recordings', __name__)


@recordings_bp.route('/')
def list_recordings():
    """List all recordings"""
    try:
        project_id = request.args.get('project_id')
        audit_type = request.args.get('audit_type')

        # Convert audit_type string to enum if provided
        audit_type_enum = None
        if audit_type:
            try:
                audit_type_enum = AuditType(audit_type)
            except ValueError:
                pass

        recordings = current_app.db.get_recordings(
            project_id=project_id,
            audit_type=audit_type_enum
        )

        # Get projects for filter dropdown
        projects = current_app.db.get_all_projects()

        return render_template(
            'recordings/list.html',
            recordings=recordings,
            projects=projects,
            selected_project_id=project_id,
            selected_audit_type=audit_type
        )
    except Exception as e:
        logger.error(f"Error listing recordings: {e}", exc_info=True)
        flash(f"Error loading recordings: {str(e)}", "danger")
        return render_template('recordings/list.html', recordings=[], projects=[])


@recordings_bp.route('/<recording_id>')
def view_recording(recording_id):
    """View recording details"""
    try:
        recording = current_app.db.get_recording(recording_id)
        if not recording:
            flash("Recording not found", "danger")
            return redirect(url_for('recordings.list_recordings'))

        # Get issues for this recording
        issues = current_app.db.get_recording_issues_for_recording(recording.recording_id)

        # Group issues by touchpoint
        issues_by_touchpoint = {}
        for issue in issues:
            touchpoint = issue.touchpoint or "General"
            if touchpoint not in issues_by_touchpoint:
                issues_by_touchpoint[touchpoint] = []
            issues_by_touchpoint[touchpoint].append(issue)

        # Get project if linked
        project = None
        if recording.project_id:
            project = current_app.db.get_project(recording.project_id)

        return render_template(
            'recordings/detail.html',
            recording=recording,
            issues=issues,
            issues_by_touchpoint=issues_by_touchpoint,
            project=project
        )
    except Exception as e:
        logger.error(f"Error viewing recording: {e}", exc_info=True)
        flash(f"Error loading recording: {str(e)}", "danger")
        return redirect(url_for('recordings.list_recordings'))


@recordings_bp.route('/upload', methods=['GET', 'POST'])
def upload_recording():
    """Upload Dictaphone JSON file"""
    if request.method == 'GET':
        projects = current_app.db.get_all_projects()
        return render_template('recordings/upload.html', projects=projects)

    try:
        # Validate file upload
        if 'json_file' not in request.files:
            flash("No file uploaded", "danger")
            return redirect(url_for('recordings.upload_recording'))

        file = request.files['json_file']
        if file.filename == '':
            flash("No file selected", "danger")
            return redirect(url_for('recordings.upload_recording'))

        if not file.filename.endswith('.json'):
            flash("File must be a JSON file", "danger")
            return redirect(url_for('recordings.upload_recording'))

        # Get form data
        project_id = request.form.get('project_id')
        if not project_id:
            flash("Project is required", "danger")
            return redirect(url_for('recordings.upload_recording'))

        # Optional fields
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        auditor_name = request.form.get('auditor_name', '')
        auditor_role = request.form.get('auditor_role', '')
        audit_type = request.form.get('audit_type', 'manual')
        page_urls_str = request.form.get('page_urls', '')
        media_file_path = request.form.get('media_file_path', '')

        # Parse page URLs
        page_urls = [url.strip() for url in page_urls_str.split('\n') if url.strip()]

        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            # Read file content
            content = file.read().decode('utf-8')
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # Parse JSON to get recording_id
            data = json.loads(content)

            # Prepare auditor info
            auditor_info = {
                'title': title or f"Recording {data.get('recording', 'Unknown')}",
                'description': description,
                'auditor_name': auditor_name,
                'auditor_role': auditor_role,
                'media_file_path': media_file_path
            }

            # Import the recording
            importer = DictaphoneImporter()
            recording, issues = importer.import_from_file(
                tmp_file_path,
                project_id=project_id,
                page_urls=page_urls,
                auditor_info=auditor_info,
                audit_type=audit_type
            )

            # Check if recording with this recording_id already exists
            existing = current_app.db.get_recording_by_recording_id(recording.recording_id)
            if existing:
                flash(f"Recording '{recording.recording_id}' already exists. Please use a different recording ID.", "danger")
                return redirect(url_for('recordings.upload_recording'))

            # Save to database
            recording_id = current_app.db.create_recording(recording)
            issue_ids = current_app.db.create_recording_issues_bulk(issues)

            # Update project's recording_ids
            project = current_app.db.get_project(project_id)
            if project:
                if recording_id not in project.recording_ids:
                    project.recording_ids.append(recording_id)
                    current_app.db.update_project(project)

            flash(f"Successfully imported recording '{recording.recording_id}' with {len(issues)} issues", "success")
            return redirect(url_for('recordings.view_recording', recording_id=recording_id))

        finally:
            # Clean up temp file
            Path(tmp_file_path).unlink(missing_ok=True)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        flash(f"Invalid JSON file: {str(e)}", "danger")
        return redirect(url_for('recordings.upload_recording'))
    except Exception as e:
        logger.error(f"Error uploading recording: {e}", exc_info=True)
        flash(f"Error uploading recording: {str(e)}", "danger")
        return redirect(url_for('recordings.upload_recording'))


@recordings_bp.route('/<recording_id>/delete', methods=['POST'])
def delete_recording(recording_id):
    """Delete a recording"""
    try:
        recording = current_app.db.get_recording(recording_id)
        if not recording:
            flash("Recording not found", "danger")
            return redirect(url_for('recordings.list_recordings'))

        # Remove from project's recording_ids
        if recording.project_id:
            project = current_app.db.get_project(recording.project_id)
            if project and recording_id in project.recording_ids:
                project.recording_ids.remove(recording_id)
                current_app.db.update_project(project)

        # Delete recording (will also delete related issues)
        current_app.db.delete_recording(recording_id)

        flash(f"Recording '{recording.recording_id}' deleted successfully", "success")
        return redirect(url_for('recordings.list_recordings'))
    except Exception as e:
        logger.error(f"Error deleting recording: {e}", exc_info=True)
        flash(f"Error deleting recording: {str(e)}", "danger")
        return redirect(url_for('recordings.list_recordings'))


# API endpoints

@recordings_bp.route('/api/list')
def api_list_recordings():
    """API endpoint to list recordings"""
    try:
        project_id = request.args.get('project_id')
        recordings = current_app.db.get_recordings(project_id=project_id)

        return jsonify({
            'success': True,
            'recordings': [
                {
                    'id': r.id,
                    'recording_id': r.recording_id,
                    'title': r.title,
                    'auditor_name': r.auditor_name,
                    'auditor_role': r.auditor_role,
                    'audit_type': r.audit_type.value,
                    'total_issues': r.total_issues,
                    'high_impact_count': r.high_impact_count,
                    'medium_impact_count': r.medium_impact_count,
                    'low_impact_count': r.low_impact_count,
                    'duration': r.duration,
                    'recorded_date': r.recorded_date.isoformat() if r.recorded_date else None
                } for r in recordings
            ]
        })
    except Exception as e:
        logger.error(f"Error in API list recordings: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@recordings_bp.route('/api/<recording_id>/issues')
def api_recording_issues(recording_id):
    """API endpoint to get issues for a recording"""
    try:
        recording = current_app.db.get_recording(recording_id)
        if not recording:
            return jsonify({'success': False, 'error': 'Recording not found'}), 404

        issues = current_app.db.get_recording_issues_for_recording(recording.recording_id)

        return jsonify({
            'success': True,
            'issues': [
                {
                    'id': i.id,
                    'title': i.title,
                    'short_title': i.short_title,
                    'impact': i.impact.value,
                    'touchpoint': i.touchpoint,
                    'what': i.what,
                    'why': i.why,
                    'who': i.who,
                    'remediation': i.remediation,
                    'timecodes': [tc.to_dict() for tc in i.timecodes],
                    'wcag': [w.to_dict() for w in i.wcag],
                    'status': i.status
                } for i in issues
            ]
        })
    except Exception as e:
        logger.error(f"Error in API recording issues: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@recordings_bp.route('/api/issue/<issue_id>/status', methods=['POST'])
def api_update_issue_status(issue_id):
    """API endpoint to update issue status"""
    try:
        status = request.json.get('status')
        if not status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400

        success = current_app.db.update_recording_issue_status(issue_id, status)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to update status'}), 500
    except Exception as e:
        logger.error(f"Error updating issue status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
