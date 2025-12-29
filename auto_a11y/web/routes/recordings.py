"""
Recording management routes for manual audits
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, current_app, g, session
)
from werkzeug.utils import secure_filename
import logging
import json
from pathlib import Path
from datetime import datetime

from auto_a11y.models import Recording, RecordingIssue, RecordingType
from auto_a11y.importers import DictaphoneImporter

logger = logging.getLogger(__name__)
recordings_bp = Blueprint('recordings', __name__)


@recordings_bp.route('/')
def list_recordings():
    """List all recordings"""
    try:
        project_id = request.args.get('project_id')
        recording_type = request.args.get('recording_type')

        # Convert recording_type string to enum if provided
        recording_type_enum = None
        if recording_type:
            try:
                recording_type_enum = RecordingType(recording_type)
            except ValueError:
                pass

        recordings = current_app.db.get_recordings(
            project_id=project_id,
            recording_type=recording_type_enum
        )

        # Get projects for filter dropdown
        projects = current_app.db.get_all_projects()

        return render_template(
            'recordings/list.html',
            recordings=recordings,
            projects=projects,
            selected_project_id=project_id,
            selected_recording_type=recording_type
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

        # Get language preference - use page language from session/locale
        language = request.args.get('lang')
        if not language:
            # Use the current page language (from session or browser)
            language = session.get('language', request.accept_languages.best_match(['en', 'fr']) or 'en')
        if language not in ['en', 'fr']:
            language = 'en'

        logger.info(f"Viewing recording {recording.recording_id} with language: {language}")

        # Get ALL issues for this recording
        all_issues = current_app.db.get_recording_issues_for_recording(recording.recording_id)

        logger.info(f"Total issues found: {len(all_issues)}")

        # Filter issues by selected language
        issues = [issue for issue in all_issues if issue.language == language]

        logger.info(f"Filtered to {len(issues)} issues for language '{language}'")

        # Get available issue languages for this recording
        issue_languages = sorted(list(set(issue.language for issue in all_issues)))

        logger.info(f"Available issue languages: {issue_languages}")
        logger.info(f"Recording available_languages: {recording.available_languages}")

        # Calculate manual scores
        from auto_a11y.scoring import ManualAccessibilityScorer
        from auto_a11y.wcag_parser import get_wcag_parser
        scorer = ManualAccessibilityScorer()
        scores = scorer.calculate_scores(recording, issues, target_level='AA')

        # Get detailed criteria breakdown for the modal
        wcag_parser = get_wcag_parser()
        all_criteria = wcag_parser.get_criteria_for_level('AA')
        applicable_criteria = scorer.scope_mapper.get_applicable_criteria(
            recording.testing_scope or {},
            target_level='AA'
        )

        # Determine which criteria were removed
        all_criteria_ids = set(c.id for c in all_criteria)
        applicable_criteria_ids = set(c.id for c in applicable_criteria)
        removed_criteria_ids = all_criteria_ids - applicable_criteria_ids

        removed_criteria = [c for c in all_criteria if c.id in removed_criteria_ids]

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

        # Get discovered pages for this recording
        discovered_pages = []
        if recording.discovered_page_ids:
            from bson import ObjectId
            from auto_a11y.models import DiscoveredPage
            for page_id in recording.discovered_page_ids:
                try:
                    page_doc = current_app.db.discovered_pages.find_one({'_id': ObjectId(page_id)})
                    if page_doc:
                        discovered_pages.append(DiscoveredPage.from_dict(page_doc))
                except Exception as e:
                    logger.warning(f"Could not load discovered page {page_id}: {e}")

        return render_template(
            'recordings/detail.html',
            recording=recording,
            issues=issues,
            issues_by_touchpoint=issues_by_touchpoint,
            project=project,
            discovered_pages=discovered_pages,
            scores=scores,
            all_criteria=all_criteria,
            applicable_criteria=applicable_criteria,
            removed_criteria=removed_criteria,
            current_language=language,
            issue_languages=issue_languages
        )
    except Exception as e:
        logger.error(f"Error viewing recording: {e}", exc_info=True)
        flash(f"Error loading recording: {str(e)}", "danger")
        return redirect(url_for('recordings.list_recordings'))


@recordings_bp.route('/combined/<project_id>')
def view_combined_recordings(project_id):
    """View all recordings for a project combined into a single issue list"""
    try:
        # Get project
        project = current_app.db.get_project(project_id)
        if not project:
            flash("Project not found", "danger")
            return redirect(url_for('recordings.list_recordings'))

        # Get all recordings for this project
        recordings = current_app.db.get_recordings(project_id=project_id)

        if not recordings:
            flash("No recordings found for this project", "info")
            return redirect(url_for('projects.view_project', project_id=project_id))

        # Collect all issues from all recordings
        all_issues = []
        for recording in recordings:
            issues = current_app.db.get_recording_issues_for_recording(recording.recording_id)
            # Add recording reference to each issue for display
            for issue in issues:
                issue.recording_ref = recording
            all_issues.extend(issues)

        # Group all issues by touchpoint
        issues_by_touchpoint = {}
        for issue in all_issues:
            touchpoint = issue.touchpoint or "General"
            if touchpoint not in issues_by_touchpoint:
                issues_by_touchpoint[touchpoint] = []
            issues_by_touchpoint[touchpoint].append(issue)

        # Calculate combined statistics
        total_issues = len(all_issues)
        high_count = sum(1 for i in all_issues if i.impact.value.lower() in ['high', 'critical'])
        medium_count = sum(1 for i in all_issues if i.impact.value.lower() in ['medium', 'moderate'])
        low_count = sum(1 for i in all_issues if i.impact.value.lower() == 'low')

        return render_template(
            'recordings/combined.html',
            project=project,
            recordings=recordings,
            all_issues=all_issues,
            issues_by_touchpoint=issues_by_touchpoint,
            total_issues=total_issues,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count
        )
    except Exception as e:
        logger.error(f"Error viewing combined recordings: {e}", exc_info=True)
        flash(f"Error loading combined view: {str(e)}", "danger")
        return redirect(url_for('projects.view_project', project_id=project_id))


@recordings_bp.route('/upload', methods=['GET', 'POST'])
def upload_recording():
    """Upload Dictaphone JSON file"""
    if request.method == 'GET':
        projects = current_app.db.get_all_projects()
        return render_template('recordings/upload.html', projects=projects)

    try:
        # Validate file uploads - at least English required
        if 'json_file_en' not in request.files:
            flash("English JSON file is required", "danger")
            return redirect(url_for('recordings.upload_recording'))

        file_en = request.files['json_file_en']
        if file_en.filename == '':
            flash("English JSON file is required", "danger")
            return redirect(url_for('recordings.upload_recording'))

        if not file_en.filename.endswith('.json'):
            flash("File must be a JSON file", "danger")
            return redirect(url_for('recordings.upload_recording'))

        # Optional French file
        file_fr = request.files.get('json_file_fr')
        has_french = file_fr and file_fr.filename and file_fr.filename.endswith('.json')

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
        test_user_account = request.form.get('test_user_account', '').strip() or None
        recording_type = request.form.get('recording_type', 'audit')
        lived_experience_tester_id = request.form.get('lived_experience_tester_id', '').strip() or None
        test_supervisor_id = request.form.get('test_supervisor_id', '').strip() or None
        page_urls_str = request.form.get('page_urls', '')
        component_names_str = request.form.get('component_names', '')
        app_screens_str = request.form.get('app_screens', '')
        device_sections_str = request.form.get('device_sections', '')
        task_description = request.form.get('task_description', '').strip() or None
        media_file_path = request.form.get('media_file_path', '')

        # Capture testing scope
        testing_scope = {
            'forms': request.form.get('scope_forms') == 'on',
            'video': request.form.get('scope_video') == 'on',
            'live_multimedia': request.form.get('scope_live_multimedia') == 'on',
            'multilingual': request.form.get('scope_multilingual') == 'on',
            'orientation': request.form.get('scope_orientation') == 'on',
            'zoom': request.form.get('scope_zoom') == 'on',
            'timeouts': request.form.get('scope_timeouts') == 'on',
            'motion_actuation': request.form.get('scope_motion_actuation') == 'on',
            'drag_drop': request.form.get('scope_drag_drop') == 'on',
        }

        # Parse multi-line fields
        page_urls = [url.strip() for url in page_urls_str.split('\n') if url.strip()]
        component_names = [c.strip() for c in component_names_str.split('\n') if c.strip()]
        app_screens = [s.strip() for s in app_screens_str.split('\n') if s.strip()]
        device_sections = [d.strip() for d in device_sections_str.split('\n') if d.strip()]

        # Get discovered page IDs (from checkboxes)
        discovered_page_ids = request.form.getlist('discovered_page_ids')

        # Process HTML or JSON content files (key takeaways, painpoints, assertions) - Multi-language
        from auto_a11y.parsers import (
            parse_key_takeaways_html,
            parse_user_painpoints_html,
            parse_user_assertions_html,
            parse_key_takeaways_json,
            parse_user_painpoints_json,
            parse_user_assertions_json
        )

        # Store content by language: {'en': [...], 'fr': [...]}
        key_takeaways_data = {}
        user_painpoints_data = {}
        user_assertions_data = {}

        # Process English content files
        for lang_suffix, lang_code in [('_en', 'en'), ('_fr', 'fr')]:
            # Key Takeaways
            file_key = f'key_takeaways_file{lang_suffix}'
            if file_key in request.files:
                takeaways_file = request.files[file_key]
                if takeaways_file.filename:
                    content = takeaways_file.read().decode('utf-8')
                    try:
                        if takeaways_file.filename.endswith('.json'):
                            json_data = json.loads(content)
                            key_takeaways_data[lang_code] = parse_key_takeaways_json(json_data)
                            logger.info(f"✓ Parsed {len(key_takeaways_data[lang_code])} key takeaways ({lang_code.upper()}) from JSON")
                        elif takeaways_file.filename.endswith('.html') or takeaways_file.filename.endswith('.htm'):
                            key_takeaways_data[lang_code] = parse_key_takeaways_html(content)
                            logger.info(f"✓ Parsed {len(key_takeaways_data[lang_code])} key takeaways ({lang_code.upper()}) from HTML")
                    except Exception as e:
                        logger.error(f"Error parsing key takeaways ({lang_code}): {e}", exc_info=True)
                        flash(f"Error parsing key takeaways ({lang_code}): {str(e)}", "warning")

            # User Painpoints
            file_key = f'user_painpoints_file{lang_suffix}'
            if file_key in request.files:
                painpoints_file = request.files[file_key]
                if painpoints_file.filename:
                    content = painpoints_file.read().decode('utf-8')
                    try:
                        if painpoints_file.filename.endswith('.json'):
                            json_data = json.loads(content)
                            user_painpoints_data[lang_code] = parse_user_painpoints_json(json_data)
                            logger.info(f"✓ Parsed {len(user_painpoints_data[lang_code])} painpoints ({lang_code.upper()}) from JSON")
                        elif painpoints_file.filename.endswith('.html') or painpoints_file.filename.endswith('.htm'):
                            user_painpoints_data[lang_code] = parse_user_painpoints_html(content)
                            logger.info(f"✓ Parsed {len(user_painpoints_data[lang_code])} painpoints ({lang_code.upper()}) from HTML")
                    except Exception as e:
                        logger.error(f"Error parsing user painpoints ({lang_code}): {e}", exc_info=True)
                        flash(f"Error parsing user painpoints ({lang_code}): {str(e)}", "warning")

            # User Assertions
            file_key = f'user_assertions_file{lang_suffix}'
            if file_key in request.files:
                assertions_file = request.files[file_key]
                if assertions_file.filename:
                    content = assertions_file.read().decode('utf-8')
                    try:
                        if assertions_file.filename.endswith('.json'):
                            json_data = json.loads(content)
                            user_assertions_data[lang_code] = parse_user_assertions_json(json_data)
                            logger.info(f"✓ Parsed user assertions ({lang_code.upper()}) from JSON")
                        elif assertions_file.filename.endswith('.html') or assertions_file.filename.endswith('.htm'):
                            user_assertions_data[lang_code] = parse_user_assertions_html(content)
                            logger.info(f"✓ Parsed user assertions ({lang_code.upper()}) from HTML")
                    except Exception as e:
                        logger.error(f"Error parsing user assertions ({lang_code}): {e}", exc_info=True)
                        flash(f"Error parsing user assertions ({lang_code}): {str(e)}", "warning")

        # Process JSON files for both languages
        import tempfile

        # Read English file content
        content_en = file_en.read().decode('utf-8')
        data_en = json.loads(content_en)
        recording_id_value = data_en.get('recording', 'Unknown')

        # Read French file content if provided
        content_fr = None
        data_fr = None
        if has_french:
            content_fr = file_fr.read().decode('utf-8')
            data_fr = json.loads(content_fr)
            # Verify both files have the same recording_id
            recording_id_fr = data_fr.get('recording', '')
            if recording_id_fr != recording_id_value:
                flash(f"Recording IDs don't match: EN='{recording_id_value}', FR='{recording_id_fr}'", "danger")
                return redirect(url_for('recordings.upload_recording'))

        # If lived experience tester selected but no auditor name, look up tester name
        if lived_experience_tester_id and not auditor_name:
            project = current_app.db.get_project(project_id)
            if project and project.lived_experience_testers:
                for tester in project.lived_experience_testers:
                    if tester.get('_id') == lived_experience_tester_id:
                        # Format: "Name (Disability)"
                        name = tester.get('name', 'Unknown')
                        disability = tester.get('disability_type', '')
                        auditor_name = f"{name} ({disability})" if disability else name
                        break

        # Prepare auditor info
        auditor_info = {
            'title': title or f"Recording {recording_id_value}",
            'description': description,
            'auditor_name': auditor_name,
            'auditor_role': auditor_role,
            'test_user_account': test_user_account,
            'lived_experience_tester_id': lived_experience_tester_id,
            'test_supervisor_id': test_supervisor_id,
            'media_file_path': media_file_path,
            'key_takeaways': key_takeaways_data,
            'user_painpoints': user_painpoints_data,
            'user_assertions': user_assertions_data
        }

        # Check if recording with this recording_id already exists
        existing = current_app.db.get_recording_by_recording_id(recording_id_value)
        if existing:
            flash(f"Recording '{recording_id_value}' already exists. Please use a different recording ID.", "danger")
            return redirect(url_for('recordings.upload_recording'))

        # Process English issues
        tmp_file_en = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='_en.json', delete=False) as tmp_file:
                tmp_file.write(content_en)
                tmp_file_en = tmp_file.name

            importer = DictaphoneImporter()
            recording, issues_en = importer.import_from_file(
                tmp_file_en,
                project_id=project_id,
                page_urls=page_urls,
                discovered_page_ids=discovered_page_ids,
                component_names=component_names,
                app_screens=app_screens,
                device_sections=device_sections,
                task_description=task_description,
                auditor_info=auditor_info,
                recording_type=recording_type,
                testing_scope=testing_scope,
                language='en'
            )

            all_issues = issues_en

            # Process French issues if provided
            if has_french:
                tmp_file_fr = None
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='_fr.json', delete=False) as tmp_file:
                        tmp_file.write(content_fr)
                        tmp_file_fr = tmp_file.name

                    _, issues_fr = importer.import_from_file(
                        tmp_file_fr,
                        project_id=project_id,
                        page_urls=page_urls,
                        discovered_page_ids=discovered_page_ids,
                        component_names=component_names,
                        app_screens=app_screens,
                        device_sections=device_sections,
                        task_description=task_description,
                        auditor_info=auditor_info,
                        recording_type=recording_type,
                        testing_scope=testing_scope,
                        language='fr'
                    )
                    all_issues.extend(issues_fr)
                finally:
                    if tmp_file_fr:
                        Path(tmp_file_fr).unlink(missing_ok=True)

            # Save to database
            recording_id = current_app.db.create_recording(recording)
            issue_ids = current_app.db.create_recording_issues_bulk(all_issues)

            # Update project's recording_ids
            project = current_app.db.get_project(project_id)
            if project:
                if recording_id not in project.recording_ids:
                    project.recording_ids.append(recording_id)
                    current_app.db.update_project(project)

            flash(f"Successfully imported recording '{recording.recording_id}' with {len(all_issues)} issues ({len(issues_en)} EN" + (f", {len(issues_fr)} FR" if has_french else "") + ")", "success")
            return redirect(url_for('recordings.view_recording', recording_id=recording_id))

        finally:
            # Clean up temp files
            if tmp_file_en:
                Path(tmp_file_en).unlink(missing_ok=True)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        flash(f"Invalid JSON file: {str(e)}", "danger")
        return redirect(url_for('recordings.upload_recording'))
    except Exception as e:
        logger.error(f"Error uploading recording: {e}", exc_info=True)
        flash(f"Error uploading recording: {str(e)}", "danger")
        return redirect(url_for('recordings.upload_recording'))


@recordings_bp.route('/<recording_id>/edit', methods=['POST'])
def edit_recording(recording_id):
    """Edit a recording's page URLs and discovered pages"""
    try:
        recording = current_app.db.get_recording(recording_id)
        if not recording:
            return jsonify({'success': False, 'error': 'Recording not found'}), 404

        # Get form data
        data = request.get_json() if request.is_json else request.form

        # Update page_urls
        page_urls_str = data.get('page_urls', '')
        if isinstance(page_urls_str, str):
            recording.page_urls = [url.strip() for url in page_urls_str.split('\n') if url.strip()]
        else:
            recording.page_urls = page_urls_str

        # Update discovered_page_ids
        discovered_page_ids = data.get('discovered_page_ids', [])
        if isinstance(discovered_page_ids, str):
            # Handle comma-separated string
            recording.discovered_page_ids = [id.strip() for id in discovered_page_ids.split(',') if id.strip()]
        elif isinstance(discovered_page_ids, list):
            recording.discovered_page_ids = discovered_page_ids
        else:
            recording.discovered_page_ids = []

        # Update timestamp
        from datetime import datetime
        recording.updated_at = datetime.now()

        # Save to database
        current_app.db.update_recording(recording)

        if request.is_json:
            return jsonify({'success': True, 'message': 'Recording updated successfully'})
        else:
            flash('Recording updated successfully', 'success')
            return redirect(url_for('recordings.view_recording', recording_id=recording_id))

    except Exception as e:
        logger.error(f"Error updating recording: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash(f'Error updating recording: {e}', 'error')
            return redirect(url_for('recordings.view_recording', recording_id=recording_id))


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
                    'recording_type': r.recording_type.value,
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
