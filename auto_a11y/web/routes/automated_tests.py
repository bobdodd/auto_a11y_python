"""
Routes for Automated Tests management
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from bson import ObjectId
from datetime import datetime
import logging

from auto_a11y.core.database import Database
from auto_a11y.models import Project
from auto_a11y.reporting.report_generator import ReportGenerator
from auto_a11y.reporting.deduplication_service import AutomatedTestDeduplicationService
from auto_a11y.drupal import (
    DrupalJSONAPIClient,
    DiscoveredPageExporter,
    DiscoveredPageTaxonomies,
    WCAGChapterCache,
    IssueExporter
)
from auto_a11y.drupal.config import get_drupal_config
from auto_a11y.web.routes.pages import enrich_test_result_with_catalog

logger = logging.getLogger(__name__)

bp = Blueprint('automated_tests', __name__, url_prefix='/automated_tests')


@bp.route('/projects/<project_id>/filter-options')
def get_filter_options(project_id):
    """Get available filter options for automated tests."""
    db = current_app.db

    # Get project
    project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
    if not project_doc:
        return jsonify({'error': 'Project not found'}), 404

    # Get all websites and pages for this project
    websites = db.get_websites(project_id)

    pages_list = []
    unique_touchpoints = set()
    unique_wcag_criteria = set()
    total_issues = 0

    for website in websites:
        pages = db.get_pages(website.id)

        for page in pages:
            test_result = db.get_latest_test_result(page.id)
            if test_result:
                # Add page to list
                pages_list.append({
                    'url': page.url,
                    'title': page.title or page.url
                })

                # Collect all violations/warnings/info
                all_violations = (
                    test_result.violations +
                    test_result.warnings +
                    test_result.info
                )

                total_issues += len(all_violations)

                # Extract unique touchpoints and WCAG criteria
                for violation in all_violations:
                    if violation.touchpoint:
                        unique_touchpoints.add(violation.touchpoint)
                    if violation.wcag_criteria:
                        for criterion in violation.wcag_criteria:
                            unique_wcag_criteria.add(criterion)

    return jsonify({
        'pages': pages_list,
        'touchpoints': sorted(unique_touchpoints),
        'wcag_criteria': sorted(unique_wcag_criteria),
        'total_pages': len(pages_list),
        'total_issues': total_issues
    })


@bp.route('/projects/<project_id>')
def project_automated_tests(project_id):
    """View automated test results for a project with filtering options."""
    db = current_app.db

    # Get project
    project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
    if not project_doc:
        return "Project not found", 404

    project = Project.from_dict(project_doc)

    # Get all websites and pages for this project
    websites = db.get_websites(project_id)

    # Collect all test results with page info
    test_results_data = []
    unique_touchpoints = set()
    unique_wcag_criteria = set()

    for website in websites:
        pages = db.get_pages(website.id)

        for page in pages:
            test_result = db.get_latest_test_result(page.id)
            if test_result:
                # Collect all violations/warnings/info
                all_violations = (
                    test_result.violations +
                    test_result.warnings +
                    test_result.info
                )

                # Extract unique touchpoints and WCAG criteria
                for violation in all_violations:
                    if violation.touchpoint:
                        unique_touchpoints.add(violation.touchpoint)
                    if violation.wcag_criteria:
                        for criterion in violation.wcag_criteria:
                            unique_wcag_criteria.add(criterion)

                test_results_data.append({
                    'page': page,
                    'website': website,
                    'test_result': test_result,
                    'violation_count': len(test_result.violations),
                    'warning_count': len(test_result.warnings),
                    'info_count': len(test_result.info),
                    'total_issues': len(all_violations)
                })

    # Sort touchpoints and WCAG criteria for display
    touchpoints = sorted(unique_touchpoints)
    wcag_criteria = sorted(unique_wcag_criteria)

    return render_template(
        'automated_tests/list.html',
        project=project,
        test_results_data=test_results_data,
        touchpoints=touchpoints,
        wcag_criteria=wcag_criteria
    )


@bp.route('/projects/<project_id>/filter', methods=['POST'])
def filter_test_results(project_id):
    """Filter test results based on user criteria."""
    db = current_app.db

    # Get filter criteria from request
    filters = request.json
    page_urls = filters.get('page_urls', [])  # List of page URLs to include
    touchpoints = filters.get('touchpoints', [])  # List of touchpoints to include
    wcag_criteria = filters.get('wcag_criteria', [])  # List of WCAG criteria to include
    impact_levels = filters.get('impact_levels', [])  # List of impact levels to include

    # Get all websites and pages
    websites = db.get_websites(project_id)

    filtered_results = []

    for website in websites:
        pages = db.get_pages(website.id)

        for page in pages:
            # Filter by page URL if specified
            if page_urls and page.url not in page_urls:
                continue

            test_result = db.get_latest_test_result(page.id)
            if not test_result:
                continue

            # Filter violations
            all_violations = (
                test_result.violations +
                test_result.warnings +
                test_result.info
            )

            filtered_violations = []
            for violation in all_violations:
                # Filter by touchpoint
                if touchpoints and violation.touchpoint not in touchpoints:
                    continue

                # Filter by WCAG criteria
                if wcag_criteria:
                    if not violation.wcag_criteria:
                        continue
                    if not any(wc in wcag_criteria for wc in violation.wcag_criteria):
                        continue

                # Filter by impact level
                if impact_levels and violation.impact.value not in impact_levels:
                    continue

                filtered_violations.append(violation)

            # Only include pages with matching violations
            if filtered_violations:
                filtered_results.append({
                    'page_url': page.url,
                    'page_title': page.title or page.url,
                    'website_name': website.name,
                    'violation_count': len(filtered_violations),
                    'violations': [v.to_dict() for v in filtered_violations]
                })

    return jsonify({
        'results': filtered_results,
        'total_pages': len(filtered_results),
        'total_violations': sum(r['violation_count'] for r in filtered_results)
    })


@bp.route('/projects/<project_id>/upload', methods=['POST'])
def upload_to_drupal(project_id):
    """
    Upload filtered automated test results to Drupal with streaming progress.

    This endpoint:
    1. Applies filters to test results
    2. Runs deduplication on filtered results to find common components
    3. Creates/updates Discovered Pages (components + URLs)
    4. Links violations to discovered pages
    5. Uploads issues to Drupal with discovered page references
    """

    # IMPORTANT: Read request data BEFORE creating generator
    # Cannot call request.get_json() inside generator function
    filters = request.get_json() or {}
    page_urls = filters.get('page_urls', [])
    touchpoints = filters.get('touchpoints', [])
    wcag_criteria = filters.get('wcag_criteria', [])
    impact_levels = filters.get('impact_levels', [])
    min_component_pages = filters.get('min_component_pages', 2)

    def generate():
        import json

        def emit(event_type, message, percent=None, results=None):
            """Helper to emit SSE events"""
            data = {'type': event_type, 'message': message}
            if percent is not None:
                data['percent'] = percent
            if results is not None:
                data['results'] = results
            return f"data: {json.dumps(data)}\n\n"

        try:
            db = current_app.db

            # Get project
            yield emit('info', 'Loading project...')
            project_doc = db.projects.find_one({'_id': ObjectId(project_id)})
            if not project_doc:
                yield emit('error', 'Project not found')
                return

            project = Project.from_dict(project_doc)

            # Check Drupal configuration
            if not project.drupal_audit_name:
                yield emit('error', 'Project does not have Drupal audit configured')
                return

            yield emit('progress', 'Preparing test results...', 5)

            # Step 1: Generate comprehensive report data (with filtering)
            logger.info(f"Generating report data for project {project_id}")
            report_gen = ReportGenerator(db, config={})
            websites = db.get_websites(project_id)

            # Prepare website data with test results
            website_data = []
            for website in websites:
                pages = db.get_pages(website.id)
                page_results = []

                for page in pages:
                    # Apply page URL filter
                    if page_urls and page.url not in page_urls:
                        continue

                    test_result = db.get_latest_test_result(page.id)
                    if test_result:
                        # Enrich test result with catalog data (adds what/why/who/how to metadata)
                        test_result = enrich_test_result_with_catalog(test_result)

                        # Apply violation-level filters
                        if touchpoints or wcag_criteria or impact_levels:
                            # Filter violations
                            filtered_violations = []
                            filtered_warnings = []
                            filtered_info = []

                            for v_list, target_list in [
                                (test_result.violations, filtered_violations),
                                (test_result.warnings, filtered_warnings),
                                (test_result.info, filtered_info)
                            ]:
                                for violation in v_list:
                                    # Filter by touchpoint
                                    if touchpoints and violation.touchpoint not in touchpoints:
                                        continue

                                    # Filter by WCAG criteria
                                    if wcag_criteria:
                                        if not violation.wcag_criteria:
                                            continue
                                        if not any(wc in wcag_criteria for wc in violation.wcag_criteria):
                                            continue

                                    # Filter by impact level
                                    if impact_levels and violation.impact.value not in impact_levels:
                                        continue

                                    target_list.append(violation)

                            # Replace test result violations with filtered ones
                            test_result.violations = filtered_violations
                            test_result.warnings = filtered_warnings
                            test_result.info = filtered_info

                        # Only include if there are violations after filtering
                        if test_result.violations or test_result.warnings or test_result.info:
                            page_results.append({
                                'page': page,
                                'test_result': test_result
                            })

                if page_results:
                    website_data.append({
                        'website': website,
                        'pages': page_results
                    })

            # Prepare full project report data
            report_data = report_gen._prepare_project_report_data(project, website_data)

            # Step 2: Process automated test results with deduplication
            yield emit('progress', 'Deduplicating test results and creating Discovered Pages...', 20)
            logger.info("Deduplicating test results and creating Discovered Pages")
            dedup_service = AutomatedTestDeduplicationService(db)

            dedup_results = dedup_service.process_automated_test_results(
                project_id=project_id,
                project_data=report_data,
                min_component_pages=min_component_pages,
                mark_pages_for_inspection=False
            )

            yield emit('success', f"Found {len(dedup_results['common_components'])} common components")

            # Step 3: Link violations to discovered pages
            yield emit('progress', 'Linking violations to discovered pages...', 30)
            logger.info("Linking violations to discovered pages")
            linked_count = dedup_service.link_violations_to_discovered_pages(
                project_id=project_id,
                project_data=report_data,
                common_components=dedup_results['common_components']
            )

            yield emit('success', f"Linked {linked_count} violations to discovered pages")

            # Step 4: Get Drupal configuration and initialize clients
            yield emit('progress', 'Initializing Drupal connection...', 40)
            logger.info("Initializing Drupal clients")
            drupal_config = get_drupal_config()

            # Initialize Drupal client
            client = DrupalJSONAPIClient(
                base_url=drupal_config.base_url,
                username=drupal_config.username,
                password=drupal_config.password
            )

            # Get audit UUID
            audit_uuid = None
            try:
                audits_response = client.get('node/audit', params={'filter[title]': project.drupal_audit_name})
                if audits_response and 'data' in audits_response and len(audits_response['data']) > 0:
                    audit_uuid = audits_response['data'][0]['id']
            except Exception as e:
                logger.error(f"Error fetching audit UUID: {e}")
                yield emit('error', f'Could not find audit "{project.drupal_audit_name}" in Drupal')
                return

            if not audit_uuid:
                yield emit('error', f'Audit "{project.drupal_audit_name}" not found in Drupal')
                return

            # Initialize exporters
            taxonomies = DiscoveredPageTaxonomies(client)
            page_exporter = DiscoveredPageExporter(client, taxonomies)
            wcag_cache = WCAGChapterCache(client, taxonomies.cache)
            issue_exporter = IssueExporter(client, taxonomies.cache, wcag_cache)

            # Step 5: Upload Discovered Pages to Drupal
            yield emit('progress', 'Uploading Discovered Pages to Drupal...', 50)
            logger.info("Uploading Discovered Pages to Drupal")
            all_page_ids = dedup_results['component_page_ids'] + dedup_results['page_url_ids']
            pages_synced = 0
            pages_failed = 0

            for idx, page_id in enumerate(all_page_ids, 1):
                try:
                    page_doc = db.discovered_pages.find_one({'_id': ObjectId(page_id)})
                    if not page_doc:
                        pages_failed += 1
                        continue

                    from auto_a11y.models import DiscoveredPage, DrupalSyncStatus
                    page = DiscoveredPage.from_dict(page_doc)

                    # Export page
                    result = page_exporter.export_from_discovered_page_model(page, audit_uuid)

                    if result.get('success'):
                        # Update database with Drupal UUID
                        db.discovered_pages.update_one(
                            {'_id': ObjectId(page_id)},
                            {
                                '$set': {
                                    'drupal_uuid': result['uuid'],
                                    'drupal_sync_status': DrupalSyncStatus.SYNCED.value,
                                    'drupal_last_synced': datetime.now(),
                                    'drupal_error_message': None
                                }
                            }
                        )
                        pages_synced += 1
                    else:
                        db.discovered_pages.update_one(
                            {'_id': ObjectId(page_id)},
                            {
                                '$set': {
                                    'drupal_sync_status': DrupalSyncStatus.SYNC_FAILED.value,
                                    'drupal_error_message': result.get('error', 'Unknown error')
                                }
                            }
                        )
                        pages_failed += 1
                except Exception as e:
                    logger.error(f"Error syncing discovered page {page_id}: {e}")
                    pages_failed += 1

                # Update progress every 10 pages or at the end
                if idx % 10 == 0 or idx == len(all_page_ids):
                    percent = 50 + int((idx / len(all_page_ids)) * 20)  # 50-70%
                    yield emit('progress', f'Uploaded {idx}/{len(all_page_ids)} discovered pages...', percent)

            yield emit('success', f"Discovered Pages synced: {pages_synced}, failed: {pages_failed}")

            # Step 6: Upload Issues to Drupal with discovered page references
            yield emit('progress', 'Uploading issues to Drupal...', 70)
            logger.info("Uploading issues to Drupal")

            issues_created = 0
            issues_updated = 0
            issues_failed = 0

            # Count total violations first for progress tracking
            total_violations = 0
            for website_data in report_data.get('websites', []):
                for page_result in website_data.get('pages', []):
                    test_result = page_result.get('test_result')
                    if test_result:
                        total_violations += len(test_result.violations + test_result.warnings + test_result.info)

            violation_idx = 0

            # Process all test results and upload violations as issues
            for website_data in report_data.get('websites', []):
                for page_result in website_data.get('pages', []):
                    page = page_result.get('page')
                    test_result = page_result.get('test_result')

                    if not test_result:
                        continue

                    # Process all violation types
                    all_violations = (
                        test_result.violations +
                        test_result.warnings +
                        test_result.info
                    )

                    for violation in all_violations:
                        violation_idx += 1

                        # Get discovered page UUID for this violation
                        discovered_page_uuid = None
                        if violation.discovered_page_id:
                            disc_page = db.get_discovered_page_by_id(violation.discovered_page_id)
                            if disc_page and disc_page.drupal_uuid:
                                discovered_page_uuid = disc_page.drupal_uuid

                        # Check if issue already exists using unique_id
                        # Each violation instance has a unique_id field that is a UUID
                        existing_issue = db.drupal_issues.find_one({
                            'unique_id': violation.unique_id,
                            'project_id': project_id
                        })

                        existing_uuid = existing_issue.get('drupal_uuid') if existing_issue else None

                        try:
                            # Handle WCAG criteria - check if already UUIDs or need conversion
                            wcag_uuids = None
                            if violation.wcag_criteria:
                                # Check if first item looks like a UUID (contains dashes and is 36 chars)
                                first_crit = violation.wcag_criteria[0]
                                if len(first_crit) == 36 and first_crit.count('-') == 4:
                                    # Already UUIDs, use as-is
                                    wcag_uuids = violation.wcag_criteria
                                else:
                                    # WCAG criteria numbers, convert to UUIDs
                                    wcag_uuids = wcag_cache.lookup_uuids(violation.wcag_criteria)

                            # Build description HTML from metadata fields (enriched by catalog)
                            # Match the format used in deduplicated offline report
                            import html
                            description_parts = []
                            metadata = violation.metadata if hasattr(violation, 'metadata') and violation.metadata else {}

                            # DEBUG: Log metadata keys
                            logger.info(f"Processing violation {violation.id}: metadata keys = {list(metadata.keys()) if metadata else 'NO METADATA'}")
                            if metadata:
                                logger.info(f"  what={bool(metadata.get('what'))}, why={bool(metadata.get('why'))}, who={bool(metadata.get('who'))}, full_remediation={bool(metadata.get('full_remediation'))}")

                            # What the issue is
                            what_text = metadata.get('what', violation.description)
                            if what_text:
                                description_parts.append(f"<div><strong>What the issue is:</strong></div>\n<p>{html.escape(what_text)}</p>")

                            # Why this is important
                            if metadata.get('why'):
                                description_parts.append(f"<div><strong>Why this is important:</strong></div>\n<p>{html.escape(metadata['why'])}</p>")

                            # Who it affects
                            if metadata.get('who'):
                                description_parts.append(f"<div><strong>Who it affects:</strong></div>\n<p>{html.escape(metadata['who'])}</p>")

                            # How to remediate (use full_remediation which is always set)
                            remediation = metadata.get('full_remediation', '') or metadata.get('how', '')
                            if remediation:
                                description_parts.append(f"<div><strong>How to remediate:</strong></div>\n<div style=\"white-space: pre-wrap; word-wrap: break-word;\">{html.escape(remediation)}</div>")

                            description = "\n".join(description_parts) if description_parts else violation.description
                            logger.info(f"Built description with {len(description_parts)} parts, total length: {len(description)}")

                            # Upload issue to Drupal
                            result = issue_exporter.export_issue(
                                title=violation.description[:255],
                                description=description,
                                audit_uuid=audit_uuid,
                                impact=violation.impact.value,
                                issue_type=violation.touchpoint,
                                location_on_page=violation.metadata.get('location_on_page', ''),
                                wcag_criteria=wcag_uuids,
                                xpath=violation.xpath or violation.metadata.get('xpath'),
                                url=page.url if hasattr(page, 'url') else page.get('url'),
                                existing_uuid=existing_uuid,
                                discovered_page_uuid=discovered_page_uuid
                            )

                            if result.get('success'):
                                # Store/update issue reference in database using unique_id
                                db.drupal_issues.update_one(
                                    {'unique_id': violation.unique_id, 'project_id': project_id},
                                    {
                                        '$set': {
                                            'drupal_uuid': result['uuid'],
                                            'drupal_id': result.get('id'),
                                            'updated_at': datetime.now(),
                                            'discovered_page_id': violation.discovered_page_id
                                        },
                                        '$setOnInsert': {
                                            'unique_id': violation.unique_id,
                                            'violation_id': violation.id,  # Keep for reference
                                            'project_id': project_id,
                                            'created_at': datetime.now()
                                        }
                                    },
                                    upsert=True
                                )

                                if existing_uuid:
                                    issues_updated += 1
                                else:
                                    issues_created += 1
                            else:
                                issues_failed += 1
                                logger.error(f"Failed to upload issue: {result.get('error')}")

                        except Exception as e:
                            issues_failed += 1
                            logger.error(f"Error uploading issue: {e}")

                        # Update progress every 10 issues or at the end
                        if violation_idx % 10 == 0 or violation_idx == total_violations:
                            percent = 70 + int((violation_idx / total_violations) * 25)  # 70-95%
                            yield emit('progress', f'Uploaded {violation_idx}/{total_violations} issues...', percent)

            yield emit('success', f"Issues created: {issues_created}, updated: {issues_updated}, failed: {issues_failed}")

            # Complete!
            yield emit('complete', 'Upload complete!', 100, results={
                'upload_id': dedup_results['upload_id'],
                'common_components': len(dedup_results['common_components']),
                'component_discovered_pages': len(dedup_results['component_page_ids']),
                'url_discovered_pages': len(dedup_results['page_url_ids']),
                'violations_linked': linked_count,
                'discovered_pages_synced': pages_synced,
                'discovered_pages_failed': pages_failed,
                'issues_created': issues_created,
                'issues_updated': issues_updated,
                'issues_failed': issues_failed
            })

        except Exception as e:
            logger.error(f"Error uploading automated test results: {e}", exc_info=True)
            yield emit('error', f'Upload failed: {str(e)}')

    return current_app.response_class(generate(), mimetype='text/event-stream')
