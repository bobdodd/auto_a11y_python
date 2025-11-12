"""
Discovered Page Exporter

Handles exporting discovered pages from Auto A11y to Drupal via JSON:API.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DiscoveredPageExporter:
    """
    Export discovered pages to Drupal.

    Handles creating and updating discovered_page content in Drupal,
    including taxonomy term lookups and field formatting.
    """

    def __init__(self, client, taxonomies):
        """
        Initialize exporter.

        Args:
            client: DrupalJSONAPIClient instance
            taxonomies: DiscoveredPageTaxonomies instance
        """
        self.client = client
        self.taxonomies = taxonomies

    def export_discovered_page(
        self,
        title: str,
        url: str,
        audit_uuid: str,
        interested_because: List[str] = None,
        page_elements: List[str] = None,
        private_notes: Optional[str] = None,
        public_notes: Optional[str] = None,
        include_in_report: bool = True,
        document_links: List[Dict[str, str]] = None,
        existing_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export a discovered page to Drupal.

        Args:
            title: Page title
            url: Page URL
            audit_uuid: UUID of parent audit in Drupal
            interested_because: List of "interested because" term names
            page_elements: List of "page elements" term names
            private_notes: Private notes HTML
            public_notes: Public notes HTML
            include_in_report: Whether to include in report
            document_links: List of document link dicts with 'uri' and 'title'
            existing_uuid: If provided, UPDATE existing page instead of creating new

        Returns:
            Dict with 'success', 'uuid', 'nid', and optional 'error' keys

        Raises:
            Exception: If export fails
        """
        try:
            # Build the JSON:API payload
            payload = self._build_payload(
                title=title,
                url=url,
                audit_uuid=audit_uuid,
                interested_because=interested_because or [],
                page_elements=page_elements or [],
                private_notes=private_notes,
                public_notes=public_notes,
                include_in_report=include_in_report,
                document_links=document_links or []
            )

            # Create or update
            if existing_uuid:
                # Verify the entity exists before attempting PATCH
                try:
                    logger.info(f"Checking if discovered_page exists (UUID: {existing_uuid})")
                    self.client.get(f"node/discovered_page/{existing_uuid}")
                    logger.info(f"Updating discovered page '{title}' (UUID: {existing_uuid})")

                    # Add UUID to payload for PATCH
                    if 'data' in payload and isinstance(payload['data'], dict):
                        payload['data']['id'] = existing_uuid

                    response = self.client.patch("node/discovered_page", existing_uuid, payload)
                except Exception as e:
                    # Entity doesn't exist, create new instead
                    logger.warning(f"discovered_page UUID {existing_uuid} not found in Drupal, creating new: {e}")
                    response = self.client.post("node/discovered_page", payload)
            else:
                logger.info(f"Creating discovered page '{title}' at {url}")
                response = self.client.post("node/discovered_page", payload)

            # Extract result
            data = response.get('data', {})
            uuid = data.get('id')
            nid = data.get('attributes', {}).get('drupal_internal__nid')

            logger.info(f"Successfully exported discovered page: UUID={uuid}, NID={nid}")

            return {
                'success': True,
                'uuid': uuid,
                'nid': nid,
                'response': data
            }

        except Exception as e:
            logger.error(f"Failed to export discovered page '{title}': {e}")

            # Try to get detailed error from response
            error_detail = str(e)
            if hasattr(e, 'response'):
                try:
                    error_data = e.response.json()
                    if 'errors' in error_data:
                        error_messages = [err.get('detail', err.get('title', '')) for err in error_data['errors']]
                        error_detail = '; '.join(error_messages)
                except:
                    pass

            return {
                'success': False,
                'error': error_detail
            }

    def export_from_page_model(self, page, project_id: str, audit_uuid: str) -> Dict[str, Any]:
        """
        Export a discovered page from a Page model instance.

        Args:
            page: Page model instance with discovery fields populated
            project_id: Auto A11y project ID (for logging)
            audit_uuid: Drupal audit UUID to link to

        Returns:
            Dict with 'success', 'uuid', and optional 'error' keys
        """
        return self.export_discovered_page(
            title=page.title or page.url,
            url=page.url,
            audit_uuid=audit_uuid,
            interested_because=page.discovery_reasons,
            page_elements=page.discovery_areas,
            private_notes=page.discovery_notes_private,
            public_notes=page.discovery_notes_public,
            include_in_report=True,
            existing_uuid=page.drupal_discovered_page_uuid
        )

    def export_from_discovered_page_model(self, discovered_page, audit_uuid: str) -> Dict[str, Any]:
        """
        Export from a DiscoveredPage model instance.

        Args:
            discovered_page: DiscoveredPage model instance
            audit_uuid: Drupal audit UUID to link to

        Returns:
            Dict with 'success', 'uuid', and optional 'error' keys
        """
        return self.export_discovered_page(
            title=discovered_page.title,
            url=discovered_page.url,
            audit_uuid=audit_uuid,
            interested_because=discovered_page.interested_because,
            page_elements=discovered_page.page_elements,
            private_notes=discovered_page.private_notes,
            public_notes=discovered_page.public_notes,
            include_in_report=discovered_page.include_in_report,
            document_links=discovered_page.document_links,
            existing_uuid=discovered_page.drupal_uuid
        )

    def batch_export(
        self,
        pages: List[Any],
        audit_uuid: str,
        batch_size: int = 10,
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Export multiple discovered pages in batches.

        Args:
            pages: List of Page or DiscoveredPage model instances
            audit_uuid: Drupal audit UUID to link to
            batch_size: Number of pages to export per batch
            continue_on_error: Whether to continue if individual exports fail

        Returns:
            Dict with 'total', 'success_count', 'failure_count', 'results' keys
        """
        results = []
        success_count = 0
        failure_count = 0

        for i, page in enumerate(pages):
            logger.info(f"Exporting page {i+1}/{len(pages)}")

            try:
                # Detect page type and export
                if hasattr(page, 'discovery_reasons'):
                    # Page model
                    result = self.export_from_page_model(page, '', audit_uuid)
                else:
                    # DiscoveredPage model
                    result = self.export_from_discovered_page_model(page, audit_uuid)

                results.append(result)

                if result.get('success'):
                    success_count += 1
                else:
                    failure_count += 1

            except Exception as e:
                logger.error(f"Unexpected error exporting page: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'page_url': getattr(page, 'url', 'unknown')
                })
                failure_count += 1

                if not continue_on_error:
                    break

        return {
            'total': len(pages),
            'success_count': success_count,
            'failure_count': failure_count,
            'results': results
        }

    def _build_payload(
        self,
        title: str,
        url: str,
        audit_uuid: str,
        interested_because: List[str],
        page_elements: List[str],
        private_notes: Optional[str],
        public_notes: Optional[str],
        include_in_report: bool,
        document_links: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Build JSON:API payload for discovered_page.

        Args:
            title: Page title
            url: Page URL
            audit_uuid: Parent audit UUID
            interested_because: List of term names
            page_elements: List of term names
            private_notes: Private notes HTML
            public_notes: Public notes HTML
            include_in_report: Include in report flag
            document_links: List of document link dicts

        Returns:
            JSON:API payload dict
        """
        # Lookup taxonomy term UUIDs
        interested_uuids = self.taxonomies.lookup_interested_because_uuids(interested_because)
        element_uuids = self.taxonomies.lookup_page_elements_uuids(page_elements)

        # Build attributes
        attributes = {
            'title': title,
            'field_page_url': {
                'uri': url,
                'title': '',
                'options': []
            },
            'field_include_in_report': include_in_report,
            'field_audited': False,  # Not audited yet by default
            'field_manual_audit': False
        }

        # Add private notes if provided
        if private_notes:
            attributes['field_notes_in_discovery'] = [
                {
                    'value': private_notes,
                    'format': 'formatted_text'
                }
            ]

        # Add public notes if provided
        if public_notes:
            attributes['field_public_note_on_page'] = {
                'value': public_notes,
                'format': 'formatted_text'
            }

        # Add document links if provided
        if document_links:
            attributes['field_document_links_on_page'] = [
                {
                    'uri': link.get('uri', ''),
                    'title': link.get('title', ''),
                    'options': []
                }
                for link in document_links
            ]

        # Build relationships
        relationships = {
            'field_parent_audit_discovery': {
                'data': {
                    'type': 'node--audit',
                    'id': audit_uuid
                }
            }
        }

        # Add interested_because taxonomy if terms provided
        if interested_uuids:
            relationships['field_interested_because'] = {
                'data': [
                    {
                        'type': 'taxonomy_term--interested_in_because',
                        'id': uuid
                    }
                    for uuid in interested_uuids
                ]
            }

        # Add page_elements taxonomy if terms provided
        if element_uuids:
            relationships['field_relevant_page_elements'] = {
                'data': [
                    {
                        'type': 'taxonomy_term--page_elements',
                        'id': uuid
                    }
                    for uuid in element_uuids
                ]
            }

        # Build final payload
        payload = {
            'data': {
                'type': 'node--discovered_page',
                'attributes': attributes,
                'relationships': relationships
            }
        }

        return payload

    def validate_export_data(
        self,
        title: str,
        url: str,
        audit_uuid: str,
        interested_because: List[str] = None,
        page_elements: List[str] = None
    ) -> Dict[str, Any]:
        """
        Validate data before export.

        Args:
            title: Page title
            url: Page URL
            audit_uuid: Audit UUID
            interested_because: Term names to validate
            page_elements: Term names to validate

        Returns:
            Dict with 'valid', 'errors', 'warnings' keys
        """
        errors = []
        warnings = []

        # Check required fields
        if not title:
            errors.append("Title is required")

        if not url:
            errors.append("URL is required")

        if not audit_uuid:
            errors.append("Audit UUID is required")

        # Validate URL format
        if url and not url.startswith(('http://', 'https://')):
            warnings.append(f"URL doesn't start with http:// or https://: {url}")

        # Validate taxonomy terms
        if interested_because:
            valid, invalid = self.taxonomies.validate_term_names(
                self.taxonomies.INTERESTED_BECAUSE,
                interested_because
            )
            if invalid:
                warnings.append(f"Invalid 'interested_because' terms: {invalid}")

        if page_elements:
            valid, invalid = self.taxonomies.validate_term_names(
                self.taxonomies.PAGE_ELEMENTS,
                page_elements
            )
            if invalid:
                warnings.append(f"Invalid 'page_elements' terms: {invalid}")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
