"""
Automated Test Result Deduplication Service

This service handles:
1. Extracting common components from automated test results
2. Deduplicating issues by component signature
3. Creating Discovered Pages for:
   - Common components (reusable UI elements across multiple pages)
   - Individual page URLs with issues

Used during Drupal sync to upload deduplicated automated test results.
"""

import logging
import uuid
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime

from auto_a11y.models import DiscoveredPage
from auto_a11y.core.database import Database

logger = logging.getLogger(__name__)


class AutomatedTestDeduplicationService:
    """
    Service for deduplicating automated test results and creating Discovered Pages.

    This service mirrors the deduplication logic used in Excel/HTML reports but applies
    it to creating Discovered Pages for Drupal export.
    """

    def __init__(self, db: Database):
        """
        Initialize deduplication service.

        Args:
            db: Database instance for querying and creating Discovered Pages
        """
        self.db = db

    def extract_common_components(
        self,
        project_data: Dict[str, Any],
        min_pages: int = 2
    ) -> Dict[str, Dict]:
        """
        Extract common components from automated test discovery results.

        Common components are reusable UI elements (forms, navs, headers, footers, asides, sections)
        that appear on multiple pages with the same structural signature.

        Args:
            project_data: Project report data containing websites, pages, and test results
            min_pages: Minimum number of pages a component must appear on (default: 2)

        Returns:
            Dictionary mapping signature -> component info:
            {
                'signature': {
                    'type': 'Navigation',  # Component type
                    'label': 'Main Navigation',  # Display label
                    'signature': 'nav-main-...',  # Unique signature hash
                    'xpaths_by_page': {page_url: xpath, ...},  # XPath per page
                    'pages': {page_url1, page_url2, ...}  # Set of page URLs
                }
            }
        """
        common_components = {}

        # Iterate through all websites and pages
        for website_data in project_data.get('websites', []):
            for page_result in website_data.get('pages', []):
                page = page_result.get('page', {})
                page_url = page.get('url', '') if isinstance(page, dict) else getattr(page, 'url', '')

                test_result = page_result.get('test_result')
                if not test_result:
                    continue

                # Get discovery items (component discovery results)
                discovery_items = getattr(test_result, 'discovery', []) if hasattr(test_result, 'discovery') else []

                for d in discovery_items:
                    if hasattr(d, 'to_dict'):
                        d_dict = d.to_dict()
                    else:
                        d_dict = d if isinstance(d, dict) else {}

                    issue_id = d_dict.get('id', '')
                    metadata = d_dict.get('metadata', {})

                    # Extract signature and type for each component type
                    signature = None
                    component_type = None
                    label = None

                    if issue_id in ['DiscoFormOnPage', 'forms_DiscoFormOnPage']:
                        signature = metadata.get('formSignature')
                        component_type = 'Form'
                        field_count = metadata.get('fieldCount', 0)
                        label = f"Form ({field_count} fields)"
                    elif issue_id in ['DiscoNavFound', 'landmarks_DiscoNavFound']:
                        signature = metadata.get('navSignature')
                        component_type = 'Navigation'
                        label = metadata.get('navLabel', 'Navigation')
                    elif issue_id in ['DiscoAsideFound', 'landmarks_DiscoAsideFound']:
                        signature = metadata.get('asideSignature')
                        component_type = 'Aside'
                        label = metadata.get('asideLabel', 'Aside')
                    elif issue_id in ['DiscoSectionFound', 'landmarks_DiscoSectionFound']:
                        signature = metadata.get('sectionSignature')
                        component_type = 'Section'
                        label = metadata.get('sectionLabel', 'Section')
                    elif issue_id in ['DiscoHeaderFound', 'landmarks_DiscoHeaderFound']:
                        signature = metadata.get('headerSignature')
                        component_type = 'Header'
                        label = metadata.get('headerLabel', 'Header')

                    if signature and signature != 'unknown':
                        if signature not in common_components:
                            common_components[signature] = {
                                'type': component_type,
                                'label': label,
                                'signature': signature,
                                'xpaths_by_page': {},
                                'pages': set()
                            }

                        xpath = d_dict.get('xpath', '') or metadata.get('xpath', '')
                        common_components[signature]['xpaths_by_page'][page_url] = xpath
                        common_components[signature]['pages'].add(page_url)

        # Filter to only include components that appear on min_pages or more
        filtered_components = {
            sig: comp_data
            for sig, comp_data in common_components.items()
            if len(comp_data['pages']) >= min_pages
        }

        logger.info(f"Extracted {len(filtered_components)} common components (appearing on {min_pages}+ pages)")
        return filtered_components

    def _xpath_is_within(self, issue_xpath: str, component_xpath: str) -> bool:
        """
        Check if an issue's XPath is within a component's XPath.

        Args:
            issue_xpath: XPath of the issue element
            component_xpath: XPath of the component container

        Returns:
            True if issue is within component, False otherwise
        """
        if not issue_xpath or not component_xpath:
            return False

        # Simple check: issue xpath starts with component xpath
        # This works for most cases since child elements have longer xpaths
        return issue_xpath.startswith(component_xpath)

    def collect_pages_with_issues(
        self,
        project_data: Dict[str, Any]
    ) -> Set[str]:
        """
        Collect all unique page URLs that have automated test issues.

        Args:
            project_data: Project report data

        Returns:
            Set of page URLs that have violations, warnings, or info issues
        """
        pages_with_issues = set()

        for website_data in project_data.get('websites', []):
            for page_result in website_data.get('pages', []):
                page = page_result.get('page', {})
                page_url = page.get('url', '') if isinstance(page, dict) else getattr(page, 'url', '')

                test_result = page_result.get('test_result')
                if not test_result:
                    continue

                # Check if page has any issues
                has_issues = False
                for issue_list_attr in ['violations', 'warnings', 'info']:
                    issues = getattr(test_result, issue_list_attr, []) if hasattr(test_result, issue_list_attr) else []
                    if issues:
                        has_issues = True
                        break

                if has_issues:
                    pages_with_issues.add(page_url)

        logger.info(f"Found {len(pages_with_issues)} pages with automated test issues")
        return pages_with_issues

    def create_discovered_pages_for_components(
        self,
        project_id: str,
        common_components: Dict[str, Dict],
        upload_id: Optional[str] = None
    ) -> List[str]:
        """
        Create Discovered Pages for common components.

        Each common component becomes a Discovered Page with:
        - source_type: "common_component"
        - url: "component://{type}/{signature}" (pseudo-URL for component)
        - title: "{type}: {label}"
        - source_component_signature: The component signature
        - source_upload_id: Upload/deduplication run ID
        - interested_because: ["Common Component Across Multiple Pages"]
        - include_in_report: True (these are interesting for manual inspection)

        Args:
            project_id: Project ID
            common_components: Dictionary of common components from extract_common_components()
            upload_id: Optional upload/deduplication run ID (generated if not provided)

        Returns:
            List of created Discovered Page IDs
        """
        if not upload_id:
            upload_id = str(uuid.uuid4())

        created_ids = []

        for signature, comp_data in common_components.items():
            comp_type = comp_data['type']
            label = comp_data['label']
            page_count = len(comp_data['pages'])

            # Use a representative page URL instead of pseudo-URL (Drupal requires valid URLs)
            # Pick the first page where this component appears
            # Add URL fragment with signature to make each component URL unique
            component_pages = sorted(list(comp_data['pages']))
            base_url = component_pages[0] if component_pages else "https://example.com/component"
            component_url = f"{base_url}#component-{signature}"

            # Create title with component type and page count
            title = f"{comp_type}: {label} (on {page_count} pages)"

            # Check if this component Discovered Page already exists
            # Check by URL first (unique due to fragment with signature)
            existing = self.db.get_discovered_page_by_url(project_id, component_url)

            if existing:
                logger.info(f"Discovered Page already exists for component: {title}")
                created_ids.append(existing.id)
                continue

            # Create new Discovered Page
            discovered_page = DiscoveredPage(
                title=title,
                url=component_url,  # Use first page URL as representative
                project_id=project_id,
                source_type="common_component",
                source_component_signature=signature,
                source_upload_id=upload_id,
                interested_because=[],  # Leave empty since taxonomy term doesn't exist
                page_elements=[],  # Components span multiple page elements
                private_notes=f"This {comp_type.lower()} appears on {page_count} pages with the same structure. Signature: {signature}",
                public_notes=f"Found on pages: " + ", ".join(component_pages[:5]) +
                            (f" (and {page_count - 5} more)" if page_count > 5 else ""),
                include_in_report=True,  # Common components are interesting
                audited=False,
                manual_audit=False
            )

            try:
                page_id = self.db.create_discovered_page(discovered_page)
                created_ids.append(page_id)
                logger.info(f"Created Discovered Page for component: {title}")
            except Exception as e:
                logger.error(f"Failed to create Discovered Page for component {title}: {e}")

        logger.info(f"Created {len(created_ids)} Discovered Pages for common components")
        return created_ids

    def create_discovered_pages_for_urls(
        self,
        project_id: str,
        page_urls: Set[str],
        upload_id: Optional[str] = None,
        mark_for_manual_inspection: bool = False
    ) -> List[str]:
        """
        Create Discovered Pages for individual page URLs with automated test issues.

        Each page URL becomes a Discovered Page with:
        - source_type: "automated_test"
        - url: The actual page URL
        - title: Page URL (or extracted from page title if available)
        - source_upload_id: Upload/deduplication run ID
        - interested_because: ["Automated Testing Found Issues"]
        - include_in_report: Based on mark_for_manual_inspection flag

        Args:
            project_id: Project ID
            page_urls: Set of page URLs with issues
            upload_id: Optional upload/deduplication run ID (generated if not provided)
            mark_for_manual_inspection: If True, set include_in_report=True (default: False)

        Returns:
            List of created Discovered Page IDs
        """
        if not upload_id:
            upload_id = str(uuid.uuid4())

        created_ids = []

        for url in page_urls:
            # Check if Discovered Page already exists for this URL
            existing = self.db.get_discovered_page_by_url(project_id, url)
            if existing:
                logger.info(f"Discovered Page already exists for URL: {url}")
                created_ids.append(existing.id)
                continue

            # Create new Discovered Page
            discovered_page = DiscoveredPage(
                title=url,  # Use URL as title (could be improved with page title if available)
                url=url,
                project_id=project_id,
                source_type="automated_test",
                source_upload_id=upload_id,
                interested_because=[],  # Leave empty for now - can add valid taxonomy terms later
                page_elements=[],
                private_notes="This page was flagged because automated testing found accessibility issues.",
                public_notes=None,
                include_in_report=mark_for_manual_inspection,  # Only mark for report if explicitly requested
                audited=False,
                manual_audit=False
            )

            try:
                page_id = self.db.create_discovered_page(discovered_page)
                created_ids.append(page_id)
                logger.info(f"Created Discovered Page for URL: {url}")
            except Exception as e:
                logger.error(f"Failed to create Discovered Page for URL {url}: {e}")

        logger.info(f"Created {len(created_ids)} Discovered Pages for page URLs")
        return created_ids

    def process_automated_test_results(
        self,
        project_id: str,
        project_data: Dict[str, Any],
        upload_id: Optional[str] = None,
        min_component_pages: int = 2,
        mark_pages_for_inspection: bool = False
    ) -> Dict[str, Any]:
        """
        Full processing pipeline for automated test results:
        1. Extract common components
        2. Collect pages with issues
        3. Create Discovered Pages for components
        4. Create Discovered Pages for page URLs

        Args:
            project_id: Project ID
            project_data: Project report data with test results
            upload_id: Optional upload/deduplication run ID
            min_component_pages: Minimum pages for component to be "common" (default: 2)
            mark_pages_for_inspection: Mark page URLs for manual inspection (default: False)

        Returns:
            Dictionary with processing results:
            {
                'upload_id': str,
                'common_components': {...},
                'component_page_ids': [str, ...],
                'pages_with_issues': {url, ...},
                'page_url_ids': [str, ...]
            }
        """
        if not upload_id:
            upload_id = str(uuid.uuid4())

        logger.info(f"Processing automated test results for project {project_id} (upload_id: {upload_id})")

        # Step 1: Extract common components
        common_components = self.extract_common_components(project_data, min_component_pages)

        # Step 2: Collect pages with issues
        pages_with_issues = self.collect_pages_with_issues(project_data)

        # Step 3: Create Discovered Pages for components
        component_page_ids = self.create_discovered_pages_for_components(
            project_id,
            common_components,
            upload_id
        )

        # Step 4: Create Discovered Pages for page URLs
        page_url_ids = self.create_discovered_pages_for_urls(
            project_id,
            pages_with_issues,
            upload_id,
            mark_pages_for_inspection
        )

        results = {
            'upload_id': upload_id,
            'common_components': common_components,
            'component_page_ids': component_page_ids,
            'pages_with_issues': pages_with_issues,
            'page_url_ids': page_url_ids
        }

        logger.info(f"Completed processing: {len(component_page_ids)} components, {len(page_url_ids)} page URLs")
        return results

    def link_violations_to_discovered_pages(
        self,
        project_id: str,
        project_data: Dict[str, Any],
        common_components: Dict[str, Dict]
    ) -> int:
        """
        Link violations in test results to their corresponding Discovered Pages.

        This updates the test_results collection in MongoDB, adding discovered_page_id
        to each violation based on:
        - Component violations: Link to component's Discovered Page by signature
        - Page violations: Link to page URL's Discovered Page

        Args:
            project_id: Project ID
            project_data: Project report data with test results
            common_components: Dictionary of common components from extract_common_components()

        Returns:
            Count of violations that were linked
        """
        linked_count = 0

        # Build a map of component signatures to discovered page IDs
        component_signature_to_page_id = {}
        component_pages = self.db.get_discovered_pages_for_project(
            project_id=project_id,
            source_type="common_component"
        )
        for comp_page in component_pages:
            if comp_page.source_component_signature:
                component_signature_to_page_id[comp_page.source_component_signature] = comp_page.id

        # Build a map of page URLs to discovered page IDs
        url_to_page_id = {}
        url_pages = self.db.get_discovered_pages_for_project(
            project_id=project_id,
            source_type="automated_test"
        )
        for url_page in url_pages:
            url_to_page_id[url_page.url] = url_page.id

        # Iterate through test results and link violations
        for website_data in project_data.get('websites', []):
            for page_result in website_data.get('pages', []):
                page = page_result.get('page', {})
                page_url = page.get('url', '') if isinstance(page, dict) else getattr(page, 'url', '')

                test_result = page_result.get('test_result')
                if not test_result:
                    continue

                # Get the discovered page ID for this page URL
                page_discovered_id = url_to_page_id.get(page_url)

                # Track if we need to update this test result
                needs_update = False

                # Process all violation types
                for violation_list_attr in ['violations', 'warnings', 'info']:
                    violations = getattr(test_result, violation_list_attr, []) if hasattr(test_result, violation_list_attr) else []

                    for violation in violations:
                        # Determine which discovered page this violation belongs to
                        discovered_page_id = None

                        # Check if violation is in a common component
                        violation_xpath = getattr(violation, 'xpath', None) or getattr(violation, 'metadata', {}).get('xpath')

                        if violation_xpath:
                            # Try to match to a component by checking if xpath is within component
                            for signature, comp_data in common_components.items():
                                # Check if this page has this component
                                if page_url in comp_data.get('pages', set()):
                                    comp_xpath = comp_data['xpaths_by_page'].get(page_url, '')
                                    if comp_xpath and self._xpath_is_within(violation_xpath, comp_xpath):
                                        # This violation is in this component
                                        discovered_page_id = component_signature_to_page_id.get(signature)
                                        break

                        # If not in a component, link to page URL discovered page
                        if not discovered_page_id:
                            discovered_page_id = page_discovered_id

                        # Update violation with discovered page reference
                        if discovered_page_id and not getattr(violation, 'discovered_page_id', None):
                            violation.discovered_page_id = discovered_page_id
                            needs_update = True
                            linked_count += 1

                # Update test result in database if any violations were linked
                if needs_update:
                    self.db.test_results.update_one(
                        {'_id': test_result._id},
                        {'$set': {'violations': [v.to_dict() for v in test_result.violations],
                                  'warnings': [v.to_dict() for v in test_result.warnings],
                                  'info': [v.to_dict() for v in test_result.info]}}
                    )

        logger.info(f"Linked {linked_count} violations to discovered pages")
        return linked_count
