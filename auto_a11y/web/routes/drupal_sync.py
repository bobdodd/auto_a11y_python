"""
Flask routes for Drupal synchronization
"""

import logging
from flask import Blueprint, render_template, request, jsonify, Response, stream_with_context, current_app
from bson import ObjectId
import json
from datetime import datetime

from auto_a11y.models import Project, DiscoveredPage, Recording, Issue, DrupalSyncStatus
from auto_a11y.drupal import (
    DrupalJSONAPIClient,
    DiscoveredPageExporter,
    DiscoveredPageImporter,
    DiscoveredPageTaxonomies,
    RecordingExporter,
    IssueImporter,
    IssueExporter
)
from auto_a11y.drupal.config import get_drupal_config

logger = logging.getLogger(__name__)

drupal_sync_bp = Blueprint('drupal_sync', __name__)


@drupal_sync_bp.route('/projects/<project_id>/sync')
def project_sync_page(project_id):
    """Drupal synchronization page for a project"""
    try:
        db = current_app.db

        # Get project
        project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
        if not project_doc:
            return "Project not found", 404

        project = Project.from_dict(project_doc)

        return render_template('drupal_sync/project_sync.html', project=project)
    except Exception as e:
        logger.error(f"Error loading sync page: {e}")
        return f"Error loading sync page: {e}", 500


@drupal_sync_bp.route('/audits/list')
def list_audits():
    """List all available audits from Drupal"""
    logger.warning("=== /drupal/audits/list endpoint called ===")
    try:
        import requests
        import base64

        logger.warning("Getting Drupal config...")
        config = get_drupal_config()
        logger.warning(f"Drupal enabled: {config.enabled}")

        # Check if Drupal is enabled
        if not config.enabled:
            return jsonify({
                'success': False,
                'error': 'Drupal integration is not enabled'
            })

        credentials = f"{config.username}:{config.password}"
        b64_creds = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {b64_creds}'
        }

        url = f"{config.base_url}/rest/open_audits?_format=json"
        logger.warning(f"Fetching audits from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.warning(f"Response status: {response.status_code}")

        audits = response.json()
        logger.warning(f"Received {len(audits)} open audits from Drupal")

        # Note: The /rest/open_audits endpoint already filters for active/open audits
        # No additional filtering needed

        # Sort audits by title
        audits_sorted = sorted(audits, key=lambda x: x.get('title', '').lower())

        result = {
            'success': True,
            'audits': [
                {
                    'title': audit.get('title', ''),
                    'uuid': audit.get('uuid') or audit.get('uuId'),
                    'nid': audit.get('nid')
                }
                for audit in audits_sorted
            ]
        }
        logger.warning(f"Returning {len(result['audits'])} audits to client")
        return jsonify(result)

    except Exception as e:
        logger.warning(f"ERROR listing Drupal audits: {e}")
        logger.error(f"Error listing Drupal audits: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


def _get_drupal_client():
    """Get configured Drupal client"""
    try:
        config = get_drupal_config()
        return DrupalJSONAPIClient(
            base_url=config.base_url,
            username=config.username,
            password=config.password
        )
    except Exception as e:
        logger.error(f"Failed to initialize Drupal client: {e}")
        return None


def _lookup_audit_uuid(client, project):
    """Look up Drupal audit UUID by project's drupal_audit_name or name"""
    try:
        import requests
        import base64

        config = get_drupal_config()
        credentials = f"{config.username}:{config.password}"
        b64_creds = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {b64_creds}'
        }

        url = f"{config.base_url}/rest/open_audits?_format=json"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        audits = response.json()

        # Use drupal_audit_name if set, otherwise use project name
        audit_name = project.drupal_audit_name or project.name

        # Find audit by name
        for audit in audits:
            if audit.get('title', '').lower() == audit_name.lower():
                return audit.get('uuid') or audit.get('uuId')

        return None
    except Exception as e:
        logger.error(f"Failed to lookup audit UUID: {e}")
        return None


@drupal_sync_bp.route('/projects/<project_id>/sync/status')
def sync_status(project_id):
    """Get sync status for a project"""
    try:
        db = current_app.db

        # Get project
        project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
        if not project_doc:
            return jsonify({'error': 'Project not found'}), 404

        project = Project.from_dict(project_doc)

        # Check if Drupal is configured
        try:
            config = get_drupal_config()
            drupal_enabled = config.enabled
        except:
            drupal_enabled = False

        # Count discovered pages
        discovered_pages = list(db.discovered_pages.find({'project_id': project_id}))
        pages_synced = sum(1 for p in discovered_pages if p.get('drupal_sync_status') == 'synced')
        pages_pending = sum(1 for p in discovered_pages if p.get('drupal_sync_status') in ['not_synced', 'pending'])
        pages_failed = sum(1 for p in discovered_pages if p.get('drupal_sync_status') == 'sync_failed')

        # Count recordings
        recordings = list(db.recordings.find({'project_id': project_id}))
        recordings_synced = sum(1 for r in recordings if r.get('drupal_sync_status') == 'synced')
        recordings_pending = sum(1 for r in recordings if r.get('drupal_sync_status') in ['not_synced', 'pending'])
        recordings_failed = sum(1 for r in recordings if r.get('drupal_sync_status') == 'sync_failed')

        # Get last sync time
        last_sync_times = []
        for p in discovered_pages:
            if p.get('drupal_last_synced'):
                last_sync_times.append(p['drupal_last_synced'])
        for r in recordings:
            if r.get('drupal_last_synced'):
                last_sync_times.append(r['drupal_last_synced'])

        last_sync_time = max(last_sync_times) if last_sync_times else None

        # Get sync errors
        sync_errors = []
        for p in discovered_pages:
            if p.get('drupal_error_message'):
                sync_errors.append(f"Page '{p.get('title')}': {p['drupal_error_message']}")
        for r in recordings:
            if r.get('drupal_error_message'):
                sync_errors.append(f"Recording '{r.get('title')}': {r['drupal_error_message']}")

        return jsonify({
            'drupal_enabled': drupal_enabled,
            'project_name': project.name,
            'discovered_pages': {
                'total': len(discovered_pages),
                'synced': pages_synced,
                'pending': pages_pending,
                'failed': pages_failed
            },
            'recordings': {
                'total': len(recordings),
                'synced': recordings_synced,
                'pending': recordings_pending,
                'failed': recordings_failed
            },
            'last_sync_time': last_sync_time.isoformat() if last_sync_time else None,
            'sync_errors': sync_errors[:5]  # Limit to 5 most recent errors
        })

    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return jsonify({'error': str(e)}), 500


@drupal_sync_bp.route('/projects/<project_id>/sync/upload', methods=['POST'])
def upload_to_drupal(project_id):
    """Upload discovered pages and recordings to Drupal"""

    def generate():
        try:
            db = current_app.db

            # Get project
            project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
            if not project_doc:
                yield json.dumps({'type': 'error', 'error': 'Project not found'}) + '\n'
                return

            project = Project.from_dict(project_doc)

            # Get selected items from request
            data = request.get_json()
            discovered_page_ids = data.get('discovered_page_ids', [])
            recording_ids = data.get('recording_ids', [])
            issue_ids = data.get('issue_ids', [])
            options = data.get('options', {})

            yield json.dumps({
                'type': 'info',
                'message': f'Starting upload for project: {project.name}'
            }) + '\n'

            # Initialize Drupal client
            client = _get_drupal_client()
            if not client:
                yield json.dumps({'type': 'error', 'error': 'Failed to initialize Drupal client'}) + '\n'
                return

            # Lookup audit UUID
            yield json.dumps({'type': 'info', 'message': 'Looking up Drupal audit...'}) + '\n'
            audit_uuid = _lookup_audit_uuid(client, project)

            if not audit_uuid:
                audit_name = project.drupal_audit_name or project.name
                yield json.dumps({
                    'type': 'error',
                    'error': f'Audit not found in Drupal: {audit_name}'
                }) + '\n'
                return

            yield json.dumps({
                'type': 'info',
                'message': f'Found audit UUID: {audit_uuid}'
            }) + '\n'

            # Initialize exporters
            taxonomies = DiscoveredPageTaxonomies(client)
            page_exporter = DiscoveredPageExporter(client, taxonomies)
            recording_exporter = RecordingExporter(client)
            issue_exporter = IssueExporter(client)

            total_items = len(discovered_page_ids) + len(recording_ids) + len(issue_ids)
            current_item = 0
            success_count = 0
            failure_count = 0

            # Export discovered pages
            for page_id in discovered_page_ids:
                current_item += 1

                try:
                    page_doc = db.discovered_pages.find_one({'_id': ObjectId(page_id)})
                    if not page_doc:
                        yield json.dumps({
                            'type': 'error',
                            'current': current_item,
                            'total': total_items,
                            'item': page_id,
                            'error': 'Page not found'
                        }) + '\n'
                        failure_count += 1
                        continue

                    page = DiscoveredPage.from_dict(page_doc)

                    yield json.dumps({
                        'type': 'progress',
                        'current': current_item,
                        'total': total_items,
                        'item': page.title,
                        'status': 'exporting'
                    }) + '\n'

                    # Export page
                    result = page_exporter.export_from_discovered_page_model(page, audit_uuid)

                    if result.get('success'):
                        # Update database with Drupal UUID
                        db.discovered_pages.update_one(
                            {'_id': ObjectId(page_id)},
                            {
                                '$set': {
                                    'drupal_uuid': result['uuid'],
                                    'drupal_sync_status': 'synced',
                                    'drupal_last_synced': datetime.now(),
                                    'drupal_error_message': None
                                }
                            }
                        )

                        yield json.dumps({
                            'type': 'success',
                            'current': current_item,
                            'total': total_items,
                            'item': page.title,
                            'uuid': result['uuid'],
                            'nid': result.get('nid')
                        }) + '\n'
                        success_count += 1
                    else:
                        # Update database with error
                        db.discovered_pages.update_one(
                            {'_id': ObjectId(page_id)},
                            {
                                '$set': {
                                    'drupal_sync_status': 'sync_failed',
                                    'drupal_error_message': result.get('error')
                                }
                            }
                        )

                        yield json.dumps({
                            'type': 'error',
                            'current': current_item,
                            'total': total_items,
                            'item': page.title,
                            'error': result.get('error')
                        }) + '\n'
                        failure_count += 1

                except Exception as e:
                    logger.error(f"Error exporting page {page_id}: {e}")
                    yield json.dumps({
                        'type': 'error',
                        'current': current_item,
                        'total': total_items,
                        'item': page_id,
                        'error': str(e)
                    }) + '\n'
                    failure_count += 1

            # Export recordings
            for recording_id in recording_ids:
                current_item += 1

                try:
                    recording_doc = db.recordings.find_one({'_id': ObjectId(recording_id)})
                    if not recording_doc:
                        yield json.dumps({
                            'type': 'error',
                            'current': current_item,
                            'total': total_items,
                            'item': recording_id,
                            'error': 'Recording not found'
                        }) + '\n'
                        failure_count += 1
                        continue

                    recording = Recording.from_dict(recording_doc)

                    yield json.dumps({
                        'type': 'progress',
                        'current': current_item,
                        'total': total_items,
                        'item': recording.title,
                        'status': 'exporting'
                    }) + '\n'

                    # Fetch discovered page UUIDs if recording has discovered pages
                    discovered_page_uuids = []
                    if recording.discovered_page_ids:
                        for page_id in recording.discovered_page_ids:
                            try:
                                page_doc = db.discovered_pages.find_one({'_id': ObjectId(page_id)})
                                if page_doc and page_doc.get('drupal_uuid'):
                                    discovered_page_uuids.append(page_doc['drupal_uuid'])
                                elif page_doc:
                                    logger.warning(f"Discovered page {page_id} ({page_doc.get('title', 'Unknown')}) has not been synced to Drupal yet")
                            except Exception as e:
                                logger.error(f"Error fetching discovered page {page_id}: {e}")

                    # Export recording
                    result = recording_exporter.export_from_recording_model(recording, audit_uuid, discovered_page_uuids)

                    if result.get('success'):
                        # Update database with Drupal UUID
                        video_uuid = result['uuid']
                        db.recordings.update_one(
                            {'_id': ObjectId(recording_id)},
                            {
                                '$set': {
                                    'drupal_video_uuid': video_uuid,
                                    'drupal_video_nid': result.get('nid'),
                                    'drupal_sync_status': 'synced',
                                    'drupal_last_synced': datetime.now(),
                                    'drupal_error_message': None
                                }
                            }
                        )

                        yield json.dumps({
                            'type': 'success',
                            'current': current_item,
                            'total': total_items,
                            'item': recording.title,
                            'uuid': video_uuid,
                            'nid': result.get('nid')
                        }) + '\n'
                        success_count += 1

                        # Export associated RecordingIssues for this recording
                        recording_issues = list(db.recording_issues.find({'recording_id': recording.recording_id}))
                        if recording_issues:
                            yield json.dumps({
                                'type': 'info',
                                'message': f'Exporting {len(recording_issues)} issues from recording "{recording.title}"'
                            }) + '\n'

                            for issue_doc in recording_issues:
                                try:
                                    from auto_a11y.models import RecordingIssue
                                    rec_issue = RecordingIssue.from_dict(issue_doc)

                                    issue_result = issue_exporter.export_from_recording_issue(
                                        rec_issue,
                                        audit_uuid,
                                        video_uuid
                                    )

                                    if issue_result.get('success'):
                                        yield json.dumps({
                                            'type': 'info',
                                            'message': f'  ✓ Exported issue: {rec_issue.title}'
                                        }) + '\n'
                                    else:
                                        yield json.dumps({
                                            'type': 'warning',
                                            'message': f'  ✗ Failed to export issue "{rec_issue.title}": {issue_result.get("error")}'
                                        }) + '\n'
                                except Exception as issue_err:
                                    logger.error(f"Error exporting recording issue: {issue_err}")
                                    yield json.dumps({
                                        'type': 'warning',
                                        'message': f'  ✗ Error exporting issue: {str(issue_err)}'
                                    }) + '\n'
                    else:
                        # Update database with error
                        db.recordings.update_one(
                            {'_id': ObjectId(recording_id)},
                            {
                                '$set': {
                                    'drupal_sync_status': 'sync_failed',
                                    'drupal_error_message': result.get('error')
                                }
                            }
                        )

                        yield json.dumps({
                            'type': 'error',
                            'current': current_item,
                            'total': total_items,
                            'item': recording.title,
                            'error': result.get('error')
                        }) + '\n'
                        failure_count += 1

                except Exception as e:
                    logger.error(f"Error exporting recording {recording_id}: {e}")
                    yield json.dumps({
                        'type': 'error',
                        'current': current_item,
                        'total': total_items,
                        'item': recording_id,
                        'error': str(e)
                    }) + '\n'
                    failure_count += 1

            # Export issues
            for issue_id in issue_ids:
                current_item += 1

                try:
                    issue_doc = db.issues.find_one({'_id': ObjectId(issue_id)})
                    if not issue_doc:
                        yield json.dumps({
                            'type': 'error',
                            'current': current_item,
                            'total': total_items,
                            'item': issue_id,
                            'error': 'Issue not found'
                        }) + '\n'
                        failure_count += 1
                        continue

                    issue = Issue.from_dict(issue_doc)

                    yield json.dumps({
                        'type': 'progress',
                        'current': current_item,
                        'total': total_items,
                        'item': issue.title,
                        'status': 'exporting'
                    }) + '\n'

                    # Export issue
                    result = issue_exporter.export_from_issue_model(issue, audit_uuid)

                    if result.get('success'):
                        # Update database with Drupal UUID
                        db.issues.update_one(
                            {'_id': ObjectId(issue_id)},
                            {
                                '$set': {
                                    'drupal_uuid': result['uuid'],
                                    'drupal_nid': result.get('nid'),
                                    'drupal_sync_status': 'synced',
                                    'drupal_last_synced': datetime.now(),
                                    'drupal_error_message': None
                                }
                            }
                        )

                        yield json.dumps({
                            'type': 'success',
                            'current': current_item,
                            'total': total_items,
                            'item': issue.title,
                            'uuid': result['uuid'],
                            'nid': result.get('nid')
                        }) + '\n'
                        success_count += 1
                    else:
                        # Update database with error
                        db.issues.update_one(
                            {'_id': ObjectId(issue_id)},
                            {
                                '$set': {
                                    'drupal_sync_status': 'sync_failed',
                                    'drupal_error_message': result.get('error')
                                }
                            }
                        )

                        yield json.dumps({
                            'type': 'error',
                            'current': current_item,
                            'total': total_items,
                            'item': issue.title,
                            'error': result.get('error')
                        }) + '\n'
                        failure_count += 1

                except Exception as e:
                    logger.error(f"Error exporting issue {issue_id}: {e}")
                    yield json.dumps({
                        'type': 'error',
                        'current': current_item,
                        'total': total_items,
                        'item': issue_id,
                        'error': str(e)
                    }) + '\n'
                    failure_count += 1

            # Send completion message
            yield json.dumps({
                'type': 'complete',
                'total': total_items,
                'success_count': success_count,
                'failure_count': failure_count
            }) + '\n'

        except Exception as e:
            logger.error(f"Upload error: {e}")
            yield json.dumps({'type': 'error', 'error': str(e)}) + '\n'

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')


@drupal_sync_bp.route('/projects/<project_id>/discovered-pages')
def list_discovered_pages(project_id):
    """List discovered pages for a project"""
    try:
        db = current_app.db

        # Get discovered pages
        pages = list(db.discovered_pages.find({'project_id': project_id}))

        # Convert to dict
        result = []
        for page_doc in pages:
            page = DiscoveredPage.from_dict(page_doc)
            result.append({
                'id': page.id,
                'title': page.title,
                'url': page.url,
                'interested_because': page.interested_because,
                'page_elements': page.page_elements,
                'drupal_uuid': page.drupal_uuid,
                'drupal_sync_status': page.drupal_sync_status.value,
                'drupal_last_synced': page.drupal_last_synced.isoformat() if page.drupal_last_synced else None,
                'is_synced': page.is_synced,
                'needs_sync': page.needs_sync
            })

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error listing discovered pages: {e}")
        return jsonify({'error': str(e)}), 500


@drupal_sync_bp.route('/projects/<project_id>/recordings')
def list_recordings(project_id):
    """List recordings for a project"""
    try:
        db = current_app.db

        # Get recordings
        recordings = list(db.recordings.find({'project_id': project_id}))

        # Convert to dict
        result = []
        for recording_doc in recordings:
            recording = Recording.from_dict(recording_doc)
            result.append({
                'id': recording.id,
                'title': recording.title,
                'duration': recording.duration,
                'auditor_name': recording.auditor_name,
                'recording_type': recording.recording_type.value,
                'total_issues': recording.total_issues,
                'component_names': recording.component_names,
                'drupal_video_uuid': recording.drupal_video_uuid,
                'drupal_video_nid': recording.drupal_video_nid,
                'drupal_sync_status': recording.drupal_sync_status.value,
                'drupal_last_synced': recording.drupal_last_synced.isoformat() if recording.drupal_last_synced else None,
                'is_synced': recording.is_synced,
                'needs_sync': recording.needs_sync
            })

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        return jsonify({'error': str(e)}), 500


@drupal_sync_bp.route('/projects/<project_id>/sync/import-pages', methods=['POST'])
def import_discovered_pages(project_id):
    """
    Import discovered pages from Drupal for a project.

    Streams progress updates as JSON lines.
    """
    def generate():
        try:
            db = current_app.db

            # Get project
            project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
            if not project_doc:
                yield json.dumps({'type': 'error', 'error': 'Project not found'}) + '\n'
                return

            project = Project.from_dict(project_doc)

            # Get Drupal config
            drupal_config = get_drupal_config()
            if not drupal_config.enabled:
                yield json.dumps({'type': 'error', 'error': 'Drupal integration not enabled'}) + '\n'
                return

            # Initialize Drupal client
            client = DrupalJSONAPIClient(
                base_url=drupal_config.base_url,
                username=drupal_config.username,
                password=drupal_config.password
            )

            # Lookup audit UUID
            yield json.dumps({'type': 'info', 'message': 'Looking up Drupal audit...'}) + '\n'
            audit_uuid = _lookup_audit_uuid(client, project)

            if not audit_uuid:
                yield json.dumps({'type': 'error', 'error': 'Could not find Drupal audit'}) + '\n'
                return

            logger.info(f"[IMPORT DEBUG] Project: {project.name}, Drupal Audit Name: {project.drupal_audit_name}, Audit UUID: {audit_uuid}")
            yield json.dumps({'type': 'info', 'message': f'Found Drupal audit: {project.drupal_audit_name or project.name} (UUID: {audit_uuid})'}) + '\n'

            # Initialize taxonomies and importer
            taxonomies = DiscoveredPageTaxonomies(client)
            importer = DiscoveredPageImporter(client, taxonomies)

            yield json.dumps({'type': 'info', 'message': 'Fetching discovered pages from Drupal...'}) + '\n'

            # Fetch discovered pages from Drupal
            drupal_pages = importer.fetch_discovered_pages_for_audit(audit_uuid)

            logger.info(f"[IMPORT DEBUG] Fetched {len(drupal_pages)} pages from Drupal for audit {audit_uuid}")
            for idx, page in enumerate(drupal_pages, 1):
                logger.info(f"[IMPORT DEBUG] Page {idx}: Title='{page['title']}', UUID={page['uuid']}, URL={page['url']}")

            yield json.dumps({'type': 'info', 'message': f'Found {len(drupal_pages)} discovered pages in Drupal'}) + '\n'

            # Import each page
            imported_count = 0
            updated_count = 0
            skipped_count = 0

            for i, drupal_page in enumerate(drupal_pages, 1):
                try:
                    # Check if page already exists with this Drupal UUID
                    existing_page = db.discovered_pages.find_one({
                        'drupal_uuid': drupal_page['uuid']
                    })

                    if existing_page:
                        # Update existing page
                        page_model = DiscoveredPage.from_dict(existing_page)

                        # Update fields
                        page_model.title = drupal_page['title']
                        page_model.url = drupal_page['url']
                        page_model.interested_because = drupal_page['interested_because']
                        page_model.page_elements = drupal_page['page_elements']
                        page_model.private_notes = drupal_page['private_notes']
                        page_model.public_notes = drupal_page['public_notes']
                        page_model.include_in_report = drupal_page['include_in_report']
                        page_model.audited = drupal_page['audited']
                        page_model.manual_audit = drupal_page['manual_audit']
                        page_model.document_links = drupal_page['document_links']
                        page_model.drupal_sync_status = DrupalSyncStatus.SYNCED
                        page_model.drupal_last_synced = datetime.now()
                        page_model.drupal_error_message = None

                        db.discovered_pages.update_one(
                            {'_id': existing_page['_id']},
                            {'$set': page_model.to_dict()}
                        )

                        updated_count += 1
                        yield json.dumps({
                            'type': 'success',
                            'current': i,
                            'total': len(drupal_pages),
                            'item': f'Updated: {drupal_page["title"]}'
                        }) + '\n'
                    else:
                        # Create new page
                        page_data = importer.import_to_discovered_page_model(drupal_page, project_id)
                        page_model = DiscoveredPage(**page_data)

                        db.discovered_pages.insert_one(page_model.to_dict())

                        imported_count += 1
                        yield json.dumps({
                            'type': 'success',
                            'current': i,
                            'total': len(drupal_pages),
                            'item': f'Imported: {drupal_page["title"]}'
                        }) + '\n'

                except Exception as e:
                    logger.error(f"Error importing page {drupal_page.get('title')}: {e}")
                    skipped_count += 1
                    yield json.dumps({
                        'type': 'error',
                        'current': i,
                        'total': len(drupal_pages),
                        'item': drupal_page.get('title', 'Unknown'),
                        'error': str(e)
                    }) + '\n'

            # Send completion
            yield json.dumps({
                'type': 'complete',
                'imported': imported_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'total': len(drupal_pages)
            }) + '\n'

        except Exception as e:
            logger.error(f"Error importing discovered pages: {e}")
            yield json.dumps({'type': 'error', 'error': str(e)}) + '\n'

    return Response(stream_with_context(generate()), content_type='application/x-ndjson')


@drupal_sync_bp.route('/projects/<project_id>/issues')
def list_issues(project_id):
    """List issues for a project"""
    try:
        db = current_app.db

        # Get issues
        issues = list(db.issues.find({'project_id': project_id}))

        # Convert to dict
        result = []
        for issue_doc in issues:
            issue = Issue.from_dict(issue_doc)
            result.append({
                'id': issue.id,
                'title': issue.title,
                'impact': issue.impact.value,
                'issue_type': issue.issue_type,
                'location_on_page': issue.location_on_page,
                'wcag_criteria': issue.wcag_criteria,
                'source_type': issue.source_type,
                'detection_method': issue.detection_method,
                'status': issue.status,
                'drupal_uuid': issue.drupal_uuid,
                'drupal_nid': issue.drupal_nid,
                'drupal_sync_status': issue.drupal_sync_status.value,
                'drupal_last_synced': issue.drupal_last_synced.isoformat() if issue.drupal_last_synced else None,
                'is_synced': issue.is_synced,
                'needs_sync': issue.needs_sync
            })

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error listing issues: {e}")
        return jsonify({'error': str(e)}), 500


@drupal_sync_bp.route('/projects/<project_id>/sync/import-issues', methods=['POST'])
def import_issues(project_id):
    """
    Import issues from Drupal for a project.

    Streams progress updates as JSON lines.
    """
    def generate():
        try:
            db = current_app.db

            # Get project
            project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
            if not project_doc:
                yield json.dumps({'type': 'error', 'error': 'Project not found'}) + '\n'
                return

            project = Project.from_dict(project_doc)

            # Initialize Drupal client
            client = _get_drupal_client()
            if not client:
                yield json.dumps({'type': 'error', 'error': 'Failed to initialize Drupal client'}) + '\n'
                return

            # Lookup audit UUID
            yield json.dumps({'type': 'info', 'message': 'Looking up Drupal audit...'}) + '\n'
            audit_uuid = _lookup_audit_uuid(client, project)

            if not audit_uuid:
                yield json.dumps({'type': 'error', 'error': 'Could not find Drupal audit'}) + '\n'
                return

            logger.info(f"[IMPORT DEBUG] Project: {project.name}, Drupal Audit Name: {project.drupal_audit_name}, Audit UUID: {audit_uuid}")
            yield json.dumps({'type': 'info', 'message': f'Found Drupal audit: {project.drupal_audit_name or project.name} (UUID: {audit_uuid})'}) + '\n'

            # Initialize importer
            importer = IssueImporter(client)

            yield json.dumps({'type': 'info', 'message': 'Fetching issues from Drupal...'}) + '\n'

            # Fetch issues from Drupal
            drupal_issues = importer.fetch_issues_for_audit(audit_uuid)

            logger.info(f"[IMPORT DEBUG] Fetched {len(drupal_issues)} issues from Drupal for audit {audit_uuid}")
            for idx, issue in enumerate(drupal_issues, 1):
                logger.info(f"[IMPORT DEBUG] Issue {idx}: Title='{issue['title']}', UUID={issue['uuid']}, Impact={issue['impact']}")

            yield json.dumps({'type': 'info', 'message': f'Found {len(drupal_issues)} issues in Drupal'}) + '\n'

            # Import each issue
            imported_count = 0
            updated_count = 0
            skipped_count = 0

            for i, drupal_issue in enumerate(drupal_issues, 1):
                try:
                    yield json.dumps({
                        'type': 'progress',
                        'current': i,
                        'total': len(drupal_issues),
                        'item': drupal_issue['title'],
                        'status': 'importing'
                    }) + '\n'

                    # Check if issue already exists by UUID
                    existing_issue = db.issues.find_one({'drupal_uuid': drupal_issue['uuid']})

                    if existing_issue:
                        # Update existing issue
                        issue_dict = importer.to_database_dict(drupal_issue, project_id)
                        issue_dict['_id'] = existing_issue['_id']

                        db.issues.update_one(
                            {'_id': existing_issue['_id']},
                            {'$set': issue_dict}
                        )

                        yield json.dumps({
                            'type': 'success',
                            'current': i,
                            'total': len(drupal_issues),
                            'item': drupal_issue['title'],
                            'action': 'updated'
                        }) + '\n'
                        updated_count += 1

                    else:
                        # Create new issue
                        issue_dict = importer.to_database_dict(drupal_issue, project_id)
                        db.issues.insert_one(issue_dict)

                        yield json.dumps({
                            'type': 'success',
                            'current': i,
                            'total': len(drupal_issues),
                            'item': drupal_issue['title'],
                            'action': 'imported'
                        }) + '\n'
                        imported_count += 1

                except Exception as e:
                    logger.error(f"Error importing issue {drupal_issue.get('title')}: {e}")
                    skipped_count += 1
                    yield json.dumps({
                        'type': 'error',
                        'current': i,
                        'total': len(drupal_issues),
                        'item': drupal_issue.get('title', 'Unknown'),
                        'error': str(e)
                    }) + '\n'

            # Send completion
            yield json.dumps({
                'type': 'complete',
                'imported': imported_count,
                'updated': updated_count,
                'skipped': skipped_count,
                'total': len(drupal_issues)
            }) + '\n'

        except Exception as e:
            logger.error(f"Error importing issues: {e}")
            yield json.dumps({'type': 'error', 'error': str(e)}) + '\n'

    return Response(stream_with_context(generate()), content_type='application/x-ndjson')
