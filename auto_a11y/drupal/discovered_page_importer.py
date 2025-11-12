"""
Discovered Page Importer

Handles importing discovered pages from Drupal to Auto A11y via JSON:API.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from auto_a11y.models.page import DrupalSyncStatus

logger = logging.getLogger(__name__)


class DiscoveredPageImporter:
    """
    Import discovered pages from Drupal.

    Handles fetching discovered_page content from Drupal and converting
    it to Auto A11y DiscoveredPage or Page model format.
    """

    def __init__(self, client, taxonomies):
        """
        Initialize importer.

        Args:
            client: DrupalJSONAPIClient instance
            taxonomies: DiscoveredPageTaxonomies instance
        """
        self.client = client
        self.taxonomies = taxonomies

    def fetch_discovered_pages_for_audit(
        self,
        audit_uuid: str,
        include_relationships: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch all discovered pages for an audit.

        Args:
            audit_uuid: Drupal audit UUID
            include_relationships: Whether to include relationship data

        Returns:
            List of discovered page dicts with converted data
        """
        try:
            logger.info(f"Fetching discovered pages for audit {audit_uuid}")

            # Build query params
            params = {
                'filter[field_parent_audit_discovery.id]': audit_uuid,
                'sort': 'created'
            }

            if include_relationships:
                params['include'] = 'field_interested_because,field_relevant_page_elements,field_parent_audit_discovery'

            # Fetch pages (may need pagination)
            all_pages = []
            page_limit = 50
            offset = 0

            while True:
                params['page[limit]'] = page_limit
                params['page[offset]'] = offset

                response = self.client.get('node/discovered_page', params=params)
                pages = response.get('data', [])

                if not pages:
                    break

                # Convert each page
                for page_data in pages:
                    converted = self._convert_drupal_page(page_data, response.get('included', []))
                    all_pages.append(converted)

                offset += page_limit

                # If we got fewer than page_limit, we're done
                if len(pages) < page_limit:
                    break

            logger.info(f"Fetched {len(all_pages)} discovered pages")
            return all_pages

        except Exception as e:
            logger.error(f"Failed to fetch discovered pages: {e}")
            raise

    def fetch_single_page(self, page_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single discovered page by UUID.

        Args:
            page_uuid: Drupal discovered_page UUID

        Returns:
            Converted page dict or None if not found
        """
        try:
            logger.info(f"Fetching discovered page {page_uuid}")

            response = self.client.get(
                f'node/discovered_page/{page_uuid}',
                params={'include': 'field_interested_because,field_relevant_page_elements'}
            )

            page_data = response.get('data')
            if not page_data:
                return None

            return self._convert_drupal_page(page_data, response.get('included', []))

        except Exception as e:
            logger.error(f"Failed to fetch discovered page: {e}")
            return None

    def import_to_discovered_page_model(
        self,
        drupal_page: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """
        Convert Drupal discovered_page to DiscoveredPage model dict.

        Args:
            drupal_page: Converted Drupal page dict
            project_id: Auto A11y project ID to link to

        Returns:
            Dict suitable for creating DiscoveredPage model instance
        """
        return {
            'title': drupal_page['title'],
            'url': drupal_page['url'],
            'project_id': project_id,
            'source_type': 'drupal_import',
            'source_page_id': None,
            'source_website_id': None,
            'interested_because': drupal_page['interested_because'],
            'page_elements': drupal_page['page_elements'],
            'private_notes': drupal_page['private_notes'],
            'public_notes': drupal_page['public_notes'],
            'include_in_report': drupal_page['include_in_report'],
            'audited': drupal_page['audited'],
            'manual_audit': drupal_page['manual_audit'],
            'screenshot_paths': [],
            'document_links': drupal_page['document_links'],
            'drupal_uuid': drupal_page['uuid'],
            'drupal_sync_status': DrupalSyncStatus.SYNCED,
            'drupal_last_synced': datetime.now(),
            'drupal_error_message': None
        }

    def sync_to_page_model(
        self,
        drupal_page: Dict[str, Any],
        page_instance
    ) -> bool:
        """
        Sync Drupal discovered_page data to an existing Page model instance.

        Updates the page instance in place with Drupal data.

        Args:
            drupal_page: Converted Drupal page dict
            page_instance: Page model instance to update

        Returns:
            True if updates were made
        """
        updated = False

        # Update discovery fields if different
        if page_instance.is_flagged_for_discovery != True:
            page_instance.is_flagged_for_discovery = True
            updated = True

        if page_instance.discovery_reasons != drupal_page['interested_because']:
            page_instance.discovery_reasons = drupal_page['interested_because']
            updated = True

        if page_instance.discovery_areas != drupal_page['page_elements']:
            page_instance.discovery_areas = drupal_page['page_elements']
            updated = True

        if page_instance.discovery_notes_private != drupal_page['private_notes']:
            page_instance.discovery_notes_private = drupal_page['private_notes']
            updated = True

        if page_instance.discovery_notes_public != drupal_page['public_notes']:
            page_instance.discovery_notes_public = drupal_page['public_notes']
            updated = True

        # Update Drupal sync fields
        if page_instance.drupal_discovered_page_uuid != drupal_page['uuid']:
            page_instance.drupal_discovered_page_uuid = drupal_page['uuid']
            updated = True

        if page_instance.drupal_sync_status.value != 'synced':
            from ..models.page import DrupalSyncStatus
            page_instance.drupal_sync_status = DrupalSyncStatus.SYNCED
            updated = True

        if updated:
            page_instance.drupal_last_synced = datetime.now()
            page_instance.drupal_error_message = None

        return updated

    def _convert_drupal_page(
        self,
        page_data: Dict[str, Any],
        included: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert Drupal JSON:API page data to simplified dict.

        Args:
            page_data: Drupal JSON:API data object
            included: Included relationship data

        Returns:
            Simplified page dict
        """
        attributes = page_data.get('attributes', {})
        relationships = page_data.get('relationships', {})

        # Extract basic fields
        uuid = page_data.get('id')
        nid = attributes.get('drupal_internal__nid')
        title = attributes.get('title', '')
        url_field = attributes.get('field_page_url', {})
        url = url_field.get('uri', '') if url_field else ''

        include_in_report = attributes.get('field_include_in_report', True)
        audited = attributes.get('field_audited', False)
        manual_audit = attributes.get('field_manual_audit', False)

        # Extract notes
        private_notes_list = attributes.get('field_notes_in_discovery', [])
        private_notes = private_notes_list[0].get('value', '') if private_notes_list else None

        public_note_field = attributes.get('field_public_note_on_page', {})
        public_notes = public_note_field.get('value', '') if public_note_field else None

        # Extract document links
        doc_links_raw = attributes.get('field_document_links_on_page', [])
        document_links = [
            {'uri': link.get('uri', ''), 'title': link.get('title', '')}
            for link in doc_links_raw
        ] if doc_links_raw else []

        # Extract taxonomy terms from relationships
        interested_because_terms = []
        page_elements_terms = []

        # Get interested_because term UUIDs from relationship
        interested_rel = relationships.get('field_interested_because', {}).get('data', [])
        if interested_rel:
            interested_uuids = [term.get('id') for term in interested_rel if term.get('id')]
            interested_because_terms = self.taxonomies.lookup_interested_because_names(interested_uuids)

        # Get page_elements term UUIDs from relationship
        elements_rel = relationships.get('field_relevant_page_elements', {}).get('data', [])
        if elements_rel:
            element_uuids = [term.get('id') for term in elements_rel if term.get('id')]
            page_elements_terms = self.taxonomies.lookup_page_elements_names(element_uuids)

        # Build converted dict
        return {
            'uuid': uuid,
            'nid': nid,
            'title': title,
            'url': url,
            'include_in_report': include_in_report,
            'audited': audited,
            'manual_audit': manual_audit,
            'private_notes': private_notes,
            'public_notes': public_notes,
            'document_links': document_links,
            'interested_because': interested_because_terms,
            'page_elements': page_elements_terms,
            'created': attributes.get('created'),
            'changed': attributes.get('changed')
        }

    def match_with_existing_pages(
        self,
        drupal_pages: List[Dict[str, Any]],
        existing_pages: List[Any]
    ) -> Dict[str, Any]:
        """
        Match Drupal discovered pages with existing scraped pages by URL.

        Args:
            drupal_pages: List of converted Drupal page dicts
            existing_pages: List of Page model instances

        Returns:
            Dict with 'matched', 'unmatched_drupal', 'unmatched_local' lists
        """
        # Build URL lookup for existing pages
        existing_by_url = {page.url: page for page in existing_pages}
        drupal_by_url = {page['url']: page for page in drupal_pages}

        # Find matches
        matched = []
        unmatched_drupal = []
        unmatched_local = list(existing_pages)

        for drupal_page in drupal_pages:
            url = drupal_page['url']
            existing_page = existing_by_url.get(url)

            if existing_page:
                matched.append({
                    'drupal': drupal_page,
                    'local': existing_page
                })
                # Remove from unmatched list
                if existing_page in unmatched_local:
                    unmatched_local.remove(existing_page)
            else:
                unmatched_drupal.append(drupal_page)

        return {
            'matched': matched,
            'unmatched_drupal': unmatched_drupal,
            'unmatched_local': unmatched_local
        }
