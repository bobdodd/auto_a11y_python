"""
Discovery Report Generator

Generates reports focused on discovering content requiring manual review:
- Discovery (Disco) issues
- Informational (Info) issues
- Accessible Names touchpoint issues

Identifies pages with forms, videos, questionable typography, and elements
with poor or no accessible names that need manual accessibility inspection.
"""

import logging
import html
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from auto_a11y.models import TestResult, Page, Website, Project
from auto_a11y.core.database import Database
from auto_a11y.reporting.issue_catalog import IssueCatalog

logger = logging.getLogger(__name__)


class DiscoveryReportGenerator:
    """Generates discovery reports in HTML and PDF formats"""

    def __init__(self, database: Database, config: Dict[str, Any]):
        """
        Initialize discovery report generator

        Args:
            database: Database connection
            config: Configuration dict
        """
        self.db = database
        self.config = config
        self.report_dir = Path(config.get('REPORTS_DIR', 'reports'))
        self.report_dir.mkdir(exist_ok=True, parents=True)

    def generate_website_discovery_report(
        self,
        website_id: str,
        format: str = 'html'
    ) -> str:
        """
        Generate discovery report for a website

        Args:
            website_id: Website ID
            format: Output format ('html' or 'pdf')

        Returns:
            Path to generated report
        """
        website = self.db.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")

        project = self.db.get_project(website.project_id)
        pages = self.db.get_pages(website_id)

        # Collect inspection data for all pages
        inspection_data = self._collect_inspection_data(pages)

        # Prepare report data
        report_data = self._prepare_report_data(
            website, project, pages, inspection_data
        )

        # Generate report based on format
        if format == 'html':
            content = self._generate_html_report(report_data)
            extension = 'html'
        elif format == 'pdf':
            content = self._generate_pdf_report(report_data)
            extension = 'pdf'
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        website_name = self._sanitize_filename(website.name or 'website')
        filename = f"discovery_{website_name}_{timestamp}.{extension}"
        filepath = self.report_dir / filename

        if format == 'pdf':
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        logger.info(f"Generated discovery report: {filepath}")
        return str(filepath)

    def generate_project_discovery_report(
        self,
        project_id: str,
        format: str = 'html'
    ) -> str:
        """
        Generate discovery report for entire project

        Args:
            project_id: Project ID
            format: Output format ('html' or 'pdf')

        Returns:
            Path to generated report
        """
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        websites = self.db.get_websites(project_id)

        # Collect data for all websites
        all_pages = []
        for website in websites:
            pages = self.db.get_pages(website.id)
            all_pages.extend(pages)

        # Collect inspection data
        inspection_data = self._collect_inspection_data(all_pages)

        # Prepare report data
        report_data = self._prepare_report_data(
            None, project, all_pages, inspection_data, websites=websites
        )

        # Generate report based on format
        if format == 'html':
            content = self._generate_html_report(report_data)
            extension = 'html'
        elif format == 'pdf':
            content = self._generate_pdf_report(report_data)
            extension = 'pdf'
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = self._sanitize_filename(project.name or 'project')
        filename = f"discovery_{project_name}_{timestamp}.{extension}"
        filepath = self.report_dir / filename

        if format == 'pdf':
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        logger.info(f"Generated discovery report: {filepath}")
        return str(filepath)

    def _collect_inspection_data(self, pages: List[Page]) -> Dict[str, Any]:
        """
        Collect discovery data from pages

        Args:
            pages: List of pages to analyze

        Returns:
            Dictionary with discovery data
        """
        logger.warning("=" * 80)
        logger.warning("DISCOVERY REPORT: _collect_inspection_data() called - CODE UPDATED 2025-10-06 13:50")
        logger.warning(f"Processing {len(pages)} pages for discovery report")
        logger.warning("=" * 80)

        pages_needing_inspection = []

        # Issue type counters
        total_disco_issues = 0
        total_info_issues = 0
        total_accessible_name_issues = 0

        # Issue category tracking
        disco_by_type = defaultdict(int)
        info_by_type = defaultdict(int)
        accessible_name_by_type = defaultdict(int)

        # Track which pages have which issues (for frequency analysis)
        pages_with_disco_issue = defaultdict(set)
        pages_with_info_issue = defaultdict(set)
        pages_with_accessible_name_issue = defaultdict(set)
        total_pages_with_issues = 0

        # Font tracking - aggregate fonts across all pages
        fonts_data = {}  # font_name -> {'sizes': set(), 'pages': set()}

        # Forms tracking - aggregate forms across all pages using formSignature
        forms_data = {}  # form_signature -> {'xpath': str, 'fieldCount': int, 'fieldTypes': dict,
                        #                    'isSearchForm': bool, 'formAction': str, 'formMethod': str,
                        #                    'pages': set(), 'html': str}

        # Navigation tracking - aggregate navigations across all pages using navSignature
        navs_data = {}  # nav_signature -> {'xpath': str, 'linkCount': int, 'navLabel': str,
                       #                    'pages': set(), 'html': str}

        # Aside tracking - aggregate asides across all pages using asideSignature
        asides_data = {}  # aside_signature -> {'xpath': str, 'asideLabel': str,
                         #                      'pages': set(), 'html': str}

        # Section tracking - aggregate sections across all pages using sectionSignature
        sections_data = {}  # section_signature -> {'xpath': str, 'sectionLabel': str,
                           #                        'pages': set(), 'html': str}

        # Header tracking - aggregate headers across all pages using headerSignature
        headers_data = {}  # header_signature -> {'xpath': str, 'headerLabel': str,
                          #                       'pages': set(), 'html': str}

        # Footer tracking - aggregate footers across all pages using footerSignature
        footers_data = {}  # footer_signature -> {'xpath': str, 'footerLabel': str,
                          #                       'pages': set(), 'html': str}

        # Search tracking - aggregate search regions across all pages using searchSignature
        searches_data = {}  # search_signature -> {'xpath': str, 'searchLabel': str,
                           #                       'pages': set(), 'html': str}

        for page in pages:
            test_result = self.db.get_latest_test_result(page.id)
            if not test_result:
                continue

            # Initialize page inspection data
            page_state_desc = ""
            if hasattr(test_result, 'page_state') and test_result.page_state:
                if isinstance(test_result.page_state, dict):
                    page_state_desc = test_result.page_state.get('description', '')
                elif hasattr(test_result.page_state, 'description'):
                    page_state_desc = test_result.page_state.description

            page_data = {
                'page': page,
                'url': page.url,
                'title': page.title or 'Untitled',
                'page_state': page_state_desc,
                'disco_issues': [],
                'info_issues': [],
                'accessible_name_issues': [],
                'issue_summary': [],
                'requires_inspection': False
            }

            # Collect Discovery issues
            if hasattr(test_result, 'discovery') and test_result.discovery:
                for issue in test_result.discovery:
                    issue_dict = issue.to_dict() if hasattr(issue, 'to_dict') else issue
                    page_data['disco_issues'].append(issue_dict)

                    # Track by type and page
                    issue_id = issue_dict.get('id', 'Unknown')
                    disco_by_type[issue_id] += 1
                    pages_with_disco_issue[issue_id].add(page.id)
                    total_disco_issues += 1

                    # Track font data from DiscoFontFound discovery issues
                    # Font data is stored in metadata.fontName and metadata.fontSizes
                    if issue_id == 'fonts_DiscoFontFound' or issue_id == 'DiscoFontFound':
                        metadata = issue_dict.get('metadata', {})
                        font_name = metadata.get('fontName', issue_dict.get('fontName', issue_dict.get('found', 'Unknown')))
                        font_sizes = metadata.get('fontSizes', issue_dict.get('fontSizes', []))
                        logger.warning(f"  >> [DISCOVERY] Found DiscoFontFound: font='{font_name}' with {len(font_sizes)} sizes")
                        if font_name and font_name != 'Unknown':
                            if font_name not in fonts_data:
                                fonts_data[font_name] = {'sizes': set(), 'pages': set()}
                            fonts_data[font_name]['pages'].add(page.url)
                            if font_sizes:
                                fonts_data[font_name]['sizes'].update(font_sizes)

                    # Track form data from DiscoFormOnPage discovery issues
                    # Form data is stored in metadata with formSignature, fieldCount, fieldTypes, etc.
                    if issue_id == 'forms_DiscoFormOnPage' or issue_id == 'DiscoFormOnPage':
                        metadata = issue_dict.get('metadata', {})
                        form_signature = metadata.get('formSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoFormOnPage: signature='{form_signature}'")

                        if form_signature and form_signature != 'unknown':
                            if form_signature not in forms_data:
                                forms_data[form_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'fieldCount': metadata.get('fieldCount', 0),
                                    'fieldTypes': metadata.get('fieldTypes', {}),
                                    'isSearchForm': metadata.get('isSearchForm', False),
                                    'searchContext': metadata.get('searchContext', ''),
                                    'formAction': metadata.get('formAction', ''),
                                    'formMethod': metadata.get('formMethod', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            forms_data[form_signature]['pages'].add(page.url)

                    # Track navigation data from DiscoNavFound discovery issues
                    # Nav data is stored in metadata with navSignature, linkCount, navLabel, etc.
                    if issue_id == 'landmarks_DiscoNavFound' or issue_id == 'DiscoNavFound':
                        metadata = issue_dict.get('metadata', {})
                        nav_signature = metadata.get('navSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoNavFound: signature='{nav_signature}'")

                        if nav_signature and nav_signature != 'unknown':
                            if nav_signature not in navs_data:
                                navs_data[nav_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'linkCount': metadata.get('linkCount', 0),
                                    'navLabel': metadata.get('navLabel', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            navs_data[nav_signature]['pages'].add(page.url)

                    # Track aside data from DiscoAsideFound discovery issues
                    if issue_id == 'landmarks_DiscoAsideFound' or issue_id == 'DiscoAsideFound':
                        metadata = issue_dict.get('metadata', {})
                        aside_signature = metadata.get('asideSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoAsideFound: signature='{aside_signature}'")

                        if aside_signature and aside_signature != 'unknown':
                            if aside_signature not in asides_data:
                                asides_data[aside_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'asideLabel': metadata.get('asideLabel', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            asides_data[aside_signature]['pages'].add(page.url)

                    # Track section data from DiscoSectionFound discovery issues
                    if issue_id == 'landmarks_DiscoSectionFound' or issue_id == 'DiscoSectionFound':
                        metadata = issue_dict.get('metadata', {})
                        section_signature = metadata.get('sectionSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoSectionFound: signature='{section_signature}'")

                        if section_signature and section_signature != 'unknown':
                            if section_signature not in sections_data:
                                sections_data[section_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'sectionLabel': metadata.get('sectionLabel', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            sections_data[section_signature]['pages'].add(page.url)

                    # Track header data from DiscoHeaderFound discovery issues
                    if issue_id == 'landmarks_DiscoHeaderFound' or issue_id == 'DiscoHeaderFound':
                        metadata = issue_dict.get('metadata', {})
                        header_signature = metadata.get('headerSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoHeaderFound: signature='{header_signature}'")

                        if header_signature and header_signature != 'unknown':
                            if header_signature not in headers_data:
                                headers_data[header_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'headerLabel': metadata.get('headerLabel', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            headers_data[header_signature]['pages'].add(page.url)

                    # Track footer data from DiscoFooterFound discovery issues
                    if issue_id == 'landmarks_DiscoFooterFound' or issue_id == 'DiscoFooterFound':
                        metadata = issue_dict.get('metadata', {})
                        footer_signature = metadata.get('footerSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoFooterFound: signature='{footer_signature}'")

                        if footer_signature and footer_signature != 'unknown':
                            if footer_signature not in footers_data:
                                footers_data[footer_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'footerLabel': metadata.get('footerLabel', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            footers_data[footer_signature]['pages'].add(page.url)

                    # Track search data from DiscoSearchFound discovery issues
                    if issue_id == 'landmarks_DiscoSearchFound' or issue_id == 'DiscoSearchFound':
                        metadata = issue_dict.get('metadata', {})
                        search_signature = metadata.get('searchSignature', 'unknown')
                        logger.warning(f"  >> [DISCOVERY] Found DiscoSearchFound: signature='{search_signature}'")

                        if search_signature and search_signature != 'unknown':
                            if search_signature not in searches_data:
                                searches_data[search_signature] = {
                                    'xpath': metadata.get('xpath', issue_dict.get('xpath', '')),
                                    'searchLabel': metadata.get('searchLabel', ''),
                                    'html': metadata.get('html', issue_dict.get('html', '')),
                                    'pages': set()
                                }
                            searches_data[search_signature]['pages'].add(page.url)

            # Collect Info issues
            if hasattr(test_result, 'info') and test_result.info:
                for issue in test_result.info:
                    issue_dict = issue.to_dict() if hasattr(issue, 'to_dict') else issue
                    page_data['info_issues'].append(issue_dict)

                    # Track by type and page
                    issue_id = issue_dict.get('id', 'Unknown')
                    info_by_type[issue_id] += 1
                    pages_with_info_issue[issue_id].add(page.id)
                    total_info_issues += 1

            # Collect Accessible Names and Styles touchpoint issues from violations and warnings
            # Also collect font size data from font-related issues
            for issue_list_name in ['violations', 'warnings']:
                if hasattr(test_result, issue_list_name):
                    issue_list = getattr(test_result, issue_list_name)
                    logger.warning(f"Page {page.url}: Processing {issue_list_name} with {len(issue_list)} items")
                    for issue in issue_list:
                        issue_dict = issue.to_dict() if hasattr(issue, 'to_dict') else issue
                        # Check for category in multiple places:
                        # 1. Top-level 'touchpoint' field (newer format)
                        # 2. metadata.cat field (stored format)
                        # 3. Top-level 'cat' field (older format)
                        metadata = issue_dict.get('metadata', {})
                        category = (issue_dict.get('touchpoint') or
                                   metadata.get('cat') or
                                   issue_dict.get('cat') or '').lower()
                        issue_id = issue_dict.get('id', issue_dict.get('err', metadata.get('err', 'Unknown')))
                        if 'font' in issue_id.lower() or 'font' in category:
                            logger.warning(f"  Found font issue: id='{issue_id}', cat='{category}'")

                        # Check if it's an Accessible Names touchpoint issue
                        if category in ['accessible names', 'accessible_names', 'accessiblenames']:
                            page_data['accessible_name_issues'].append(issue_dict)

                            # Track by type and page (check 'err' field first, then 'id')
                            issue_id = issue_dict.get('err', issue_dict.get('id', 'Unknown'))
                            accessible_name_by_type[issue_id] += 1
                            pages_with_accessible_name_issue[issue_id].add(page.id)
                            total_accessible_name_issues += 1

                        # Check if it's a Styles touchpoint issue (inline styles or style tags)
                        elif category == 'styles':
                            page_data['disco_issues'].append(issue_dict)

                            # Track by type and page (check 'err' field first, then 'id')
                            issue_id = issue_dict.get('err', issue_dict.get('id', 'Unknown'))
                            disco_by_type[issue_id] += 1
                            pages_with_disco_issue[issue_id].add(page.id)
                            total_disco_issues += 1

                        # Check if it's a Fonts touchpoint issue
                        elif category == 'fonts':
                            page_data['disco_issues'].append(issue_dict)

                            # Track by type and page (check 'err' field first, then 'id')
                            issue_id = issue_dict.get('err', issue_dict.get('id', 'Unknown'))
                            disco_by_type[issue_id] += 1
                            pages_with_disco_issue[issue_id].add(page.id)
                            total_disco_issues += 1

                            # Track font data from DiscoFontFound issues
                            # Font data is stored in metadata.fontName and metadata.fontSizes
                            logger.warning(f"  >> Fonts category issue: issue_id='{issue_id}', checking for DiscoFontFound")
                            if issue_id == 'fonts_DiscoFontFound' or issue_id == 'DiscoFontFound':
                                metadata_inner = issue_dict.get('metadata', {})
                                font_name = metadata_inner.get('fontName', issue_dict.get('fontName', issue_dict.get('found', 'Unknown')))
                                font_sizes = metadata_inner.get('fontSizes', issue_dict.get('fontSizes', []))
                                logger.warning(f"  >> [DISCO COLLECTION] Font='{font_name}' with sizes={font_sizes} (type={type(font_sizes)})")
                                if font_name and font_name != 'Unknown':
                                    if font_name not in fonts_data:
                                        fonts_data[font_name] = {'sizes': set(), 'pages': set()}
                                    fonts_data[font_name]['pages'].add(page.url)
                                    if font_sizes:
                                        fonts_data[font_name]['sizes'].update(font_sizes)
                                        logger.warning(f"  >> [DISCO COLLECTION] Added sizes. Font '{font_name}' now has {len(fonts_data[font_name]['sizes'])} sizes")

                        # Check if it's a Landmarks touchpoint issue
                        elif category == 'landmarks':
                            page_data['disco_issues'].append(issue_dict)

                            # Track by type and page (check 'err' field first, then 'id')
                            issue_id = issue_dict.get('err', issue_dict.get('id', 'Unknown'))
                            disco_by_type[issue_id] += 1
                            pages_with_disco_issue[issue_id].add(page.id)
                            total_disco_issues += 1

                            # Track landmark data from various Disco landmark issues
                            metadata_inner = issue_dict.get('metadata', {})

                            # DiscoNavFound
                            if issue_id == 'DiscoNavFound':
                                nav_signature = metadata_inner.get('navSignature', issue_dict.get('navSignature', 'unknown'))
                                if nav_signature and nav_signature != 'unknown':
                                    if nav_signature not in navs_data:
                                        navs_data[nav_signature] = {
                                            'xpath': metadata_inner.get('xpath', issue_dict.get('xpath', '')),
                                            'linkCount': metadata_inner.get('linkCount', issue_dict.get('linkCount', 0)),
                                            'navLabel': metadata_inner.get('navLabel', issue_dict.get('navLabel', '')),
                                            'html': metadata_inner.get('html', issue_dict.get('html', '')),
                                            'pages': set()
                                        }
                                    navs_data[nav_signature]['pages'].add(page.url)

                            # DiscoAsideFound
                            elif issue_id == 'DiscoAsideFound':
                                aside_signature = metadata_inner.get('asideSignature', issue_dict.get('asideSignature', 'unknown'))
                                if aside_signature and aside_signature != 'unknown':
                                    if aside_signature not in asides_data:
                                        asides_data[aside_signature] = {
                                            'xpath': metadata_inner.get('xpath', issue_dict.get('xpath', '')),
                                            'asideLabel': metadata_inner.get('asideLabel', issue_dict.get('asideLabel', '')),
                                            'html': metadata_inner.get('html', issue_dict.get('html', '')),
                                            'pages': set()
                                        }
                                    asides_data[aside_signature]['pages'].add(page.url)

                            # DiscoSectionFound
                            elif issue_id == 'DiscoSectionFound':
                                section_signature = metadata_inner.get('sectionSignature', issue_dict.get('sectionSignature', 'unknown'))
                                if section_signature and section_signature != 'unknown':
                                    if section_signature not in sections_data:
                                        sections_data[section_signature] = {
                                            'xpath': metadata_inner.get('xpath', issue_dict.get('xpath', '')),
                                            'sectionLabel': metadata_inner.get('sectionLabel', issue_dict.get('sectionLabel', '')),
                                            'html': metadata_inner.get('html', issue_dict.get('html', '')),
                                            'pages': set()
                                        }
                                    sections_data[section_signature]['pages'].add(page.url)

                            # DiscoHeaderFound
                            elif issue_id == 'DiscoHeaderFound':
                                header_signature = metadata_inner.get('headerSignature', issue_dict.get('headerSignature', 'unknown'))
                                if header_signature and header_signature != 'unknown':
                                    if header_signature not in headers_data:
                                        headers_data[header_signature] = {
                                            'xpath': metadata_inner.get('xpath', issue_dict.get('xpath', '')),
                                            'headerLabel': metadata_inner.get('headerLabel', issue_dict.get('headerLabel', '')),
                                            'html': metadata_inner.get('html', issue_dict.get('html', '')),
                                            'pages': set()
                                        }
                                    headers_data[header_signature]['pages'].add(page.url)

                            # DiscoFooterFound
                            elif issue_id == 'DiscoFooterFound':
                                footer_signature = metadata_inner.get('footerSignature', issue_dict.get('footerSignature', 'unknown'))
                                if footer_signature and footer_signature != 'unknown':
                                    if footer_signature not in footers_data:
                                        footers_data[footer_signature] = {
                                            'xpath': metadata_inner.get('xpath', issue_dict.get('xpath', '')),
                                            'footerLabel': metadata_inner.get('footerLabel', issue_dict.get('footerLabel', '')),
                                            'html': metadata_inner.get('html', issue_dict.get('html', '')),
                                            'pages': set()
                                        }
                                    footers_data[footer_signature]['pages'].add(page.url)

                            # DiscoSearchFound
                            elif issue_id == 'DiscoSearchFound':
                                search_signature = metadata_inner.get('searchSignature', issue_dict.get('searchSignature', 'unknown'))
                                if search_signature and search_signature != 'unknown':
                                    if search_signature not in searches_data:
                                        searches_data[search_signature] = {
                                            'xpath': metadata_inner.get('xpath', issue_dict.get('xpath', '')),
                                            'searchLabel': metadata_inner.get('searchLabel', issue_dict.get('searchLabel', '')),
                                            'html': metadata_inner.get('html', issue_dict.get('html', '')),
                                            'pages': set()
                                        }
                                    searches_data[search_signature]['pages'].add(page.url)

            # Generate issue summary
            if page_data['disco_issues']:
                page_data['issue_summary'].append(
                    f"{len(page_data['disco_issues'])} items requiring inspection"
                )
            if page_data['info_issues']:
                page_data['issue_summary'].append(
                    f"{len(page_data['info_issues'])} informational notices"
                )
            if page_data['accessible_name_issues']:
                page_data['issue_summary'].append(
                    f"{len(page_data['accessible_name_issues'])} accessible name issues"
                )

            # Determine if page requires inspection
            if (page_data['disco_issues'] or
                page_data['info_issues'] or
                page_data['accessible_name_issues']):
                page_data['requires_inspection'] = True
                pages_needing_inspection.append(page_data)

        # Calculate total pages tested
        total_pages_tested = len([p for p in pages if self.db.get_latest_test_result(p.id)])

        # Identify common issues (appearing on >70% of pages)
        threshold = total_pages_tested * 0.7
        common_disco_issues = {
            issue_id: len(page_set)
            for issue_id, page_set in pages_with_disco_issue.items()
            if len(page_set) > threshold
        }
        common_info_issues = {
            issue_id: len(page_set)
            for issue_id, page_set in pages_with_info_issue.items()
            if len(page_set) > threshold
        }
        common_accessible_name_issues = {
            issue_id: len(page_set)
            for issue_id, page_set in pages_with_accessible_name_issue.items()
            if len(page_set) > threshold
        }

        logger.info(f"Found {len(common_disco_issues)} common discovery issues")
        logger.info(f"Found {len(common_info_issues)} common info issues")
        logger.info(f"Found {len(common_accessible_name_issues)} common accessible name issues")

        # Filter out common issues and issues with dedicated sections from page data
        filtered_pages = []
        for page_data in pages_needing_inspection:
            # Filter disco issues - remove common ones AND those with dedicated sections (fonts, forms, navs)
            page_data['disco_issues'] = [
                issue for issue in page_data['disco_issues']
                if (issue.get('id') not in common_disco_issues and
                    issue.get('id') not in ('fonts_DiscoFontFound', 'DiscoFontFound',
                                           'forms_DiscoFormOnPage', 'DiscoFormOnPage',
                                           'landmarks_DiscoNavFound', 'DiscoNavFound',
                                           'landmarks_DiscoAsideFound', 'DiscoAsideFound',
                                           'landmarks_DiscoSectionFound', 'DiscoSectionFound',
                                           'landmarks_DiscoHeaderFound', 'DiscoHeaderFound',
                                           'landmarks_DiscoFooterFound', 'DiscoFooterFound',
                                           'landmarks_DiscoSearchFound', 'DiscoSearchFound'))
            ]
            # Filter info issues
            page_data['info_issues'] = [
                issue for issue in page_data['info_issues']
                if issue.get('id') not in common_info_issues
            ]
            # Filter accessible name issues
            page_data['accessible_name_issues'] = [
                issue for issue in page_data['accessible_name_issues']
                if issue.get('id') not in common_accessible_name_issues
            ]

            # Regenerate issue summary
            page_data['issue_summary'] = []
            if page_data['disco_issues']:
                page_data['issue_summary'].append(
                    f"{len(page_data['disco_issues'])} items requiring inspection"
                )
            if page_data['info_issues']:
                page_data['issue_summary'].append(
                    f"{len(page_data['info_issues'])} informational notices"
                )
            if page_data['accessible_name_issues']:
                page_data['issue_summary'].append(
                    f"{len(page_data['accessible_name_issues'])} accessible name issues"
                )

            # Only include pages that still have issues after filtering
            if (page_data['disco_issues'] or
                page_data['info_issues'] or
                page_data['accessible_name_issues']):
                filtered_pages.append(page_data)

        # Sort pages by total issue count (descending)
        filtered_pages.sort(
            key=lambda x: (
                len(x['disco_issues']) +
                len(x['info_issues']) +
                len(x['accessible_name_issues'])
            ),
            reverse=True
        )

        logger.warning(f"Filtered from {len(pages_needing_inspection)} to {len(filtered_pages)} pages")
        logger.warning(f"FONTS COLLECTED: {len(fonts_data)} fonts: {list(fonts_data.keys())}")
        logger.warning(f"FORMS COLLECTED: {len(forms_data)} forms: {list(forms_data.keys())}")
        logger.warning(f"NAVS COLLECTED: {len(navs_data)} navigations: {list(navs_data.keys())}")
        logger.warning(f"ASIDES COLLECTED: {len(asides_data)} asides: {list(asides_data.keys())}")
        logger.warning(f"SECTIONS COLLECTED: {len(sections_data)} sections: {list(sections_data.keys())}")
        logger.warning(f"HEADERS COLLECTED: {len(headers_data)} headers: {list(headers_data.keys())}")
        logger.warning(f"FOOTERS COLLECTED: {len(footers_data)} footers: {list(footers_data.keys())}")
        logger.warning(f"SEARCHES COLLECTED: {len(searches_data)} searches: {list(searches_data.keys())}")

        return {
            'pages': filtered_pages,
            'total_pages_needing_inspection': len(pages_needing_inspection),
            'pages_with_unique_issues': len(filtered_pages),
            'total_pages_tested': total_pages_tested,
            'total_disco_issues': total_disco_issues,
            'total_info_issues': total_info_issues,
            'total_accessible_name_issues': total_accessible_name_issues,
            'disco_by_type': dict(disco_by_type),
            'info_by_type': dict(info_by_type),
            'accessible_name_by_type': dict(accessible_name_by_type),
            'common_disco_issues': common_disco_issues,
            'common_info_issues': common_info_issues,
            'common_accessible_name_issues': common_accessible_name_issues,
            'fonts': fonts_data,
            'forms': forms_data,
            'navs': navs_data,
            'asides': asides_data,
            'sections': sections_data,
            'headers': headers_data,
            'footers': footers_data,
            'searches': searches_data
        }

    def _prepare_report_data(
        self,
        website: Optional[Website],
        project: Project,
        pages: List[Page],
        inspection_data: Dict[str, Any],
        websites: Optional[List[Website]] = None
    ) -> Dict[str, Any]:
        """
        Prepare data structure for report generation

        Args:
            website: Website (None for project reports)
            project: Project
            pages: All pages
            inspection_data: Collected inspection data
            websites: List of websites (for project reports)

        Returns:
            Report data dictionary
        """
        # Get documents for the website
        documents_data = []
        if website:
            documents = self.db.get_document_references(website.id)
            # Group by document type
            docs_by_type = {}
            for doc in documents:
                doc_type = doc.document_type_display
                if doc_type not in docs_by_type:
                    docs_by_type[doc_type] = []
                docs_by_type[doc_type].append(doc)
            documents_data = docs_by_type
            logger.warning(f"DOCUMENTS COLLECTED: {len(documents)} documents across {len(docs_by_type)} types")

        report_data = {
            'title': 'Discovery Report',
            'project': project.__dict__ if project else None,
            'website': website.__dict__ if website else None,
            'websites': [w.__dict__ for w in websites] if websites else None,
            'generated_at': datetime.now().isoformat(),
            'generated_at_formatted': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            'statistics': {
                'total_pages': len(pages),
                'total_pages_tested': inspection_data['total_pages_tested'],
                'pages_needing_inspection': inspection_data['total_pages_needing_inspection'],
                'inspection_percentage': (
                    inspection_data['total_pages_needing_inspection'] /
                    inspection_data['total_pages_tested'] * 100
                    if inspection_data['total_pages_tested'] > 0 else 0
                ),
                'total_disco_issues': inspection_data['total_disco_issues'],
                'total_info_issues': inspection_data['total_info_issues'],
                'total_accessible_name_issues': inspection_data['total_accessible_name_issues'],
                'total_issues': (
                    inspection_data['total_disco_issues'] +
                    inspection_data['total_info_issues'] +
                    inspection_data['total_accessible_name_issues']
                )
            },
            'pages': inspection_data['pages'],
            'pages_with_unique_issues': inspection_data.get('pages_with_unique_issues', len(inspection_data['pages'])),
            'issue_breakdown': {
                'disco': inspection_data['disco_by_type'],
                'info': inspection_data['info_by_type'],
                'accessible_names': inspection_data['accessible_name_by_type']
            },
            'common_issues': {
                'disco': inspection_data.get('common_disco_issues', {}),
                'info': inspection_data.get('common_info_issues', {}),
                'accessible_names': inspection_data.get('common_accessible_name_issues', {})
            },
            'fonts': inspection_data.get('fonts', {}),
            'forms': inspection_data.get('forms', {}),
            'navs': inspection_data.get('navs', {}),
            'asides': inspection_data.get('asides', {}),
            'sections': inspection_data.get('sections', {}),
            'headers': inspection_data.get('headers', {}),
            'footers': inspection_data.get('footers', {}),
            'searches': inspection_data.get('searches', {}),
            'documents': documents_data
        }

        return report_data

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """
        Generate HTML format report

        Args:
            data: Report data

        Returns:
            HTML content
        """
        # Generate pages list - ALL pages
        pages_html = ""
        total_pages = len(data['pages'])

        # Log for debugging
        logger.info(f"Generating HTML for {total_pages} pages")

        for idx, page_data in enumerate(data['pages']):
            if idx % 50 == 0 and idx > 0:
                logger.info(f"Processing page {idx + 1}/{total_pages}")
            pages_html += self._generate_page_section_html(page_data, idx)

        logger.info(f"Completed generating HTML for all {total_pages} pages")

        # Generate issue breakdown
        issue_breakdown_html = self._generate_issue_breakdown_html(data['issue_breakdown'])

        # Generate scope info
        if data['website']:
            scope_html = f"""
                <p><strong>Website:</strong> {data['website']['name']}</p>
                <p><strong>URL:</strong> <a href="{data['website']['url']}" target="_blank">{data['website']['url']}</a></p>
            """
        else:
            scope_html = f"""
                <p><strong>Project:</strong> {data['project']['name']}</p>
                <p><strong>Websites:</strong> {len(data['websites']) if data['websites'] else 0}</p>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']}</title>
    {self._get_html_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>{data['title']}</h1>
            <div class="subtitle">Content Requiring Manual Accessibility Review</div>
            <div class="metadata">
                {scope_html}
                <p><strong>Generated:</strong> {data['generated_at_formatted']}</p>
            </div>
        </header>

        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <p>This report identifies pages containing content that requires manual accessibility inspection.
            It focuses on Discovery issues (content requiring review), Informational notices, and
            Accessible Names touchpoint issues that may indicate forms, videos, questionable typography,
            or elements with poor or missing accessible names.</p>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{data['statistics']['pages_needing_inspection']}</div>
                    <div class="stat-label">Pages Needing Inspection</div>
                    <div class="stat-detail">of {data['statistics']['total_pages_tested']} tested ({data['statistics']['inspection_percentage']:.1f}%)</div>
                </div>
                <div class="stat-card disco">
                    <div class="stat-number">{data['statistics']['total_disco_issues']}</div>
                    <div class="stat-label">Discovery Issues</div>
                    <div class="stat-detail">Require manual review</div>
                </div>
                <div class="stat-card info">
                    <div class="stat-number">{data['statistics']['total_info_issues']}</div>
                    <div class="stat-label">Info Items</div>
                    <div class="stat-detail">Worth noting</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number">{data['statistics']['total_accessible_name_issues']}</div>
                    <div class="stat-label">Accessible Name Issues</div>
                    <div class="stat-detail">Forms, links, buttons</div>
                </div>
            </div>
        </section>

        {self._generate_common_issues_html(data['common_issues'], data['statistics']['total_pages_tested'])}

        {self._generate_fonts_html(data.get('fonts', {}))}

        {self._generate_forms_html(data.get('forms', {}), data['statistics']['total_pages_tested'])}

        {self._generate_navs_html(data.get('navs', {}), data['statistics']['total_pages_tested'])}

        {self._generate_asides_html(data.get('asides', {}), data['statistics']['total_pages_tested'])}

        {self._generate_sections_html(data.get('sections', {}), data['statistics']['total_pages_tested'])}

        {self._generate_headers_html(data.get('headers', {}), data['statistics']['total_pages_tested'])}

        {self._generate_footers_html(data.get('footers', {}), data['statistics']['total_pages_tested'])}

        {self._generate_searches_html(data.get('searches', {}), data['statistics']['total_pages_tested'])}

        {self._generate_documents_html(data.get('documents', {}))}

        <section class="issue-breakdown">
            <h2>Issue Breakdown by Type</h2>
            {issue_breakdown_html}
        </section>

        <section class="pages-section">
            <h2>Pages With Unique Issues ({len(data['pages'])} of {data['pages_with_unique_issues']} pages)</h2>
            <p class="section-intro">The following pages contain issues that require manual review.
            Pages are listed in priority order based on total issue count. Click on a page to expand and view details.</p>
            <div class="accordion-controls">
                <button onclick="expandAllAccordions()" class="btn-control">Expand All</button>
                <button onclick="collapseAllAccordions()" class="btn-control">Collapse All</button>
            </div>
            {f'<div class="accordion">{pages_html}</div>' if pages_html else '<p class="no-issues">No pages discovered requiring manual inspection.</p>'}
        </section>

        <script>
        function toggleAccordion(id) {{
            const element = document.getElementById(id);
            const button = document.querySelector('[data-target="#' + id + '"]');
            const icon = button.querySelector('.accordion-icon');

            if (element.style.display === 'none') {{
                element.style.display = 'block';
                button.classList.remove('collapsed');
                icon.textContent = '▲';
            }} else {{
                element.style.display = 'none';
                button.classList.add('collapsed');
                icon.textContent = '▼';
            }}
        }}

        function expandAllAccordions() {{
            const accordions = document.querySelectorAll('.accordion-collapse');
            const buttons = document.querySelectorAll('.accordion-button');
            const icons = document.querySelectorAll('.accordion-icon');

            accordions.forEach(acc => acc.style.display = 'block');
            buttons.forEach(btn => btn.classList.remove('collapsed'));
            icons.forEach(icon => icon.textContent = '▲');
        }}

        function collapseAllAccordions() {{
            const accordions = document.querySelectorAll('.accordion-collapse');
            const buttons = document.querySelectorAll('.accordion-button');
            const icons = document.querySelectorAll('.accordion-icon');

            accordions.forEach(acc => acc.style.display = 'none');
            buttons.forEach(btn => btn.classList.add('collapsed'));
            icons.forEach(icon => icon.textContent = '▼');
        }}
        </script>

        <footer>
            <p>Generated by Auto A11y Python - Discovery Report</p>
            <p>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </footer>
    </div>
</body>
</html>"""

        return html

    def _generate_page_section_html(self, page_data: Dict[str, Any], index: int) -> str:
        """Generate HTML for a single page section as accordion item

        Args:
            page_data: Page data dictionary
            index: Index of this page in the list (for unique ID generation)
        """
        total_issues = (
            len(page_data['disco_issues']) +
            len(page_data['info_issues']) +
            len(page_data['accessible_name_issues'])
        )

        # Generate unique ID for accordion using index
        accordion_id = f"page-{index}"

        # Escape HTML in user-generated content
        title_escaped = html.escape(page_data['title'])
        url_escaped = html.escape(page_data['url'])
        summary_escaped = html.escape(' | '.join(page_data['issue_summary']))

        # Generate issue lists
        disco_html = self._generate_issue_list_html(page_data['disco_issues'], 'Discovery')
        info_html = self._generate_issue_list_html(page_data['info_issues'], 'Informational')
        accessible_name_html = self._generate_issue_list_html(
            page_data['accessible_name_issues'], 'Accessible Names'
        )

        return f"""
        <div class="accordion-item">
            <h3 class="accordion-header" id="heading-{accordion_id}">
                <button class="accordion-button collapsed" type="button"
                        data-target="#{accordion_id}"
                        onclick="toggleAccordion('{accordion_id}')">
                    <div class="accordion-title">
                        <div class="page-title">{title_escaped}</div>
                        <div class="page-url-small">{url_escaped}</div>
                        <div class="page-summary-small">
                            <span class="issue-badge">{total_issues} issues</span>
                            <span class="issue-breakdown-small">{summary_escaped}</span>
                        </div>
                    </div>
                    <span class="accordion-icon">▼</span>
                </button>
            </h3>
            <div id="{accordion_id}" class="accordion-collapse" style="display: none;">
                <div class="accordion-body">
                    <div class="page-url-full">
                        <strong>URL:</strong> <a href="{url_escaped}" target="_blank">{url_escaped}</a>
                    </div>
                    {disco_html}
                    {info_html}
                    {accessible_name_html}
                </div>
            </div>
        </div>
        """

    def _generate_issue_list_html(self, issues: List[Dict], category: str) -> str:
        """Generate HTML for a list of issues"""
        if not issues:
            return ""

        category_class = category.lower().replace(' ', '-')

        issues_html = ""
        for issue in issues:
            issue_id = issue.get('id', 'Unknown')
            description = issue.get('description', 'No description available')

            # Get enriched info from catalog
            catalog_info = IssueCatalog.get_issue(issue_id)
            why_it_matters = catalog_info.get('why_it_matters', '')
            how_to_fix = catalog_info.get('how_to_fix', '')

            issues_html += f"""
            <div class="issue-item">
                <div class="issue-header">
                    <span class="issue-id">{issue_id}</span>
                </div>
                <div class="issue-description">{html.escape(description)}</div>
                {f'<div class="issue-why"><strong>Why it matters:</strong> {html.escape(why_it_matters)}</div>' if why_it_matters else ''}
                {f'<div class="issue-fix"><strong>How to fix:</strong> {html.escape(how_to_fix)}</div>' if how_to_fix else ''}
            </div>
            """

        return f"""
        <div class="issue-category {category_class}">
            <h4>{category} ({len(issues)})</h4>
            <div class="issue-list">
                {issues_html}
            </div>
        </div>
        """

    def _generate_fonts_html(self, fonts_data: Dict[str, Dict]) -> str:
        """Generate HTML section for fonts found across the site"""
        logger.warning(f"_generate_fonts_html called with {len(fonts_data) if fonts_data else 0} fonts")
        if not fonts_data:
            logger.warning("No fonts data - returning empty string")
            return ""

        # Sort fonts by name
        sorted_fonts = sorted(fonts_data.items())

        fonts_html = ""
        for font_name, font_info in sorted_fonts:
            sizes = sorted(font_info['sizes'], key=lambda x: float(x.replace('px', '').replace('rem', '').replace('em', '')))
            pages_count = len(font_info['pages'])

            fonts_html += f"""
            <div class="font-item">
                <div class="font-header">
                    <h3 class="font-name">{html.escape(font_name)}</h3>
                    <span class="font-pages-count">{pages_count} page{'' if pages_count == 1 else 's'}</span>
                </div>
                <div class="font-sizes">
                    <strong>Sizes:</strong> {', '.join(html.escape(s) for s in sizes)}
                </div>
            </div>
            """

        return f"""
        <section class="fonts-section">
            <h2>Fonts Used Across Site</h2>
            <p class="section-intro">The following fonts were detected across {len(fonts_data)} unique font famil{'y' if len(fonts_data) == 1 else 'ies'}.
            Review these for readability and accessibility best practices. Consider using fonts with clear character distinction
            and good readability at various sizes.</p>
            <div class="fonts-grid">
                {fonts_html}
            </div>
        </section>
        """

    def _generate_forms_html(self, forms_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for forms found across the site"""
        logger.warning(f"_generate_forms_html called with {len(forms_data) if forms_data else 0} forms")
        if not forms_data:
            logger.warning("No forms data - returning empty string")
            return ""

        # Sort forms by page count (most common first), then by signature
        sorted_forms = sorted(forms_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        forms_html = ""
        for form_signature, form_info in sorted_forms:
            pages_count = len(form_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            # Build field types summary
            field_types = form_info.get('fieldTypes', {})
            field_summary = ', '.join([f"{count} {ftype}" for ftype, count in field_types.items()])
            if not field_summary:
                field_summary = "unknown fields"

            search_indicator = ""
            if form_info.get('isSearchForm'):
                search_indicator = '<span class="search-badge">🔍 Search Form</span>'

            action_display = form_info.get('formAction', 'unknown')
            if len(action_display) > 50:
                action_display = action_display[:47] + '...'

            # Show page URLs: all pages if <= 3, or just first example if many
            pages_list_html = ""
            if pages_count <= 3:
                # Show all pages
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(form_info['pages'])])
                pages_list_html = f"""
                    <div class="form-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                # Show just first example page for common forms
                # Prioritize home page (root URL) if available
                sorted_pages = sorted(form_info['pages'])
                example_url = sorted_pages[0]

                # Try to find home page / root URL
                for url in sorted_pages:
                    # Check if URL is a root/home page (ends with / or no path after domain)
                    if url.rstrip('/').count('/') == 2:  # http://domain.com or https://domain.com/
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="form-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            forms_html += f"""
            <div class="form-item">
                <div class="form-header">
                    <h3 class="form-signature">Form {html.escape(form_signature)}</h3>
                    {search_indicator}
                    <span class="form-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="form-details">
                    <div class="form-detail-row">
                        <strong>Fields:</strong> {form_info.get('fieldCount', 0)} ({html.escape(field_summary)})
                    </div>
                    <div class="form-detail-row">
                        <strong>Submits to:</strong> {html.escape(action_display)}
                        <span class="form-method">({html.escape(form_info.get('formMethod', 'unknown').upper())})</span>
                    </div>
                    <div class="form-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(form_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="forms-section">
            <h2>Forms Found Across Site</h2>
            <p class="section-intro">The following {len(forms_data)} unique form{'s were' if len(forms_data) != 1 else ' was'} detected.
            Each form has been assigned a signature for tracking across pages. Forms require comprehensive manual testing including
            keyboard navigation, screen reader compatibility, error validation, and field labeling.</p>
            <div class="forms-list">
                {forms_html}
            </div>
        </section>
        """

    def _generate_navs_html(self, navs_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for navigations found across the site"""
        logger.warning(f"_generate_navs_html called with {len(navs_data) if navs_data else 0} navs")
        if not navs_data:
            logger.warning("No navs data - returning empty string")
            return ""

        # Sort navs by page count (most common first), then by signature
        sorted_navs = sorted(navs_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        navs_html = ""
        for nav_signature, nav_info in sorted_navs:
            pages_count = len(nav_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            label_display = nav_info.get('navLabel', '(no label)')
            if not label_display:
                label_display = '(no label)'

            # Show page URLs: all pages if <= 3, or just first example if many
            pages_list_html = ""
            if pages_count <= 3:
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(nav_info['pages'])])
                pages_list_html = f"""
                    <div class="nav-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                # Prioritize home page
                sorted_pages = sorted(nav_info['pages'])
                example_url = sorted_pages[0]
                for url in sorted_pages:
                    if url.rstrip('/').count('/') == 2:
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="nav-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            navs_html += f"""
            <div class="nav-item">
                <div class="nav-header">
                    <h3 class="nav-signature">Nav {html.escape(nav_signature)}</h3>
                    <span class="nav-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="nav-details">
                    <div class="nav-detail-row">
                        <strong>Label:</strong> {html.escape(label_display)}
                    </div>
                    <div class="nav-detail-row">
                        <strong>Links:</strong> {nav_info.get('linkCount', 0)}
                    </div>
                    <div class="nav-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(nav_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="navs-section">
            <h2>Navigation Regions Found Across Site</h2>
            <p class="section-intro">The following {len(navs_data)} unique navigation region{'s were' if len(navs_data) != 1 else ' was'} detected.
            Each navigation has been assigned a signature for tracking across pages. Verify each navigation is keyboard accessible,
            properly labeled (if multiple exist), and provides current page indication.</p>
            <div class="navs-list">
                {navs_html}
            </div>
        </section>
        """

    def _generate_asides_html(self, asides_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for aside/complementary regions found across the site"""
        logger.warning(f"_generate_asides_html called with {len(asides_data) if asides_data else 0} asides")
        if not asides_data:
            logger.warning("No asides data - returning empty string")
            return ""

        sorted_asides = sorted(asides_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        asides_html = ""
        for aside_signature, aside_info in sorted_asides:
            pages_count = len(aside_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            label_display = aside_info.get('asideLabel', '(no label)')
            if not label_display:
                label_display = '(no label)'

            pages_list_html = ""
            if pages_count <= 3:
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(aside_info['pages'])])
                pages_list_html = f"""
                    <div class="aside-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                sorted_pages = sorted(aside_info['pages'])
                example_url = sorted_pages[0]
                for url in sorted_pages:
                    if url.rstrip('/').count('/') == 2:
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="aside-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            asides_html += f"""
            <div class="aside-item">
                <div class="aside-header">
                    <h3 class="aside-signature">Aside {html.escape(aside_signature)}</h3>
                    <span class="aside-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="aside-details">
                    <div class="aside-detail-row">
                        <strong>Label:</strong> {html.escape(label_display)}
                    </div>
                    <div class="aside-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(aside_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="asides-section">
            <h2>Complementary Regions (Aside) Found Across Site</h2>
            <p class="section-intro">The following {len(asides_data)} unique complementary region{'s were' if len(asides_data) != 1 else ' was'} detected.
            Each aside has been assigned a signature for tracking across pages. Verify each contains truly complementary content and is properly labeled when multiple exist.</p>
            <div class="asides-list">
                {asides_html}
            </div>
        </section>
        """

    def _generate_sections_html(self, sections_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for section/region landmarks found across the site"""
        logger.warning(f"_generate_sections_html called with {len(sections_data) if sections_data else 0} sections")
        if not sections_data:
            logger.warning("No sections data - returning empty string")
            return ""

        sorted_sections = sorted(sections_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        sections_html = ""
        for section_signature, section_info in sorted_sections:
            pages_count = len(section_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            label_display = section_info.get('sectionLabel', '(no label)')
            if not label_display:
                label_display = '(no label)'

            pages_list_html = ""
            if pages_count <= 3:
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(section_info['pages'])])
                pages_list_html = f"""
                    <div class="section-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                sorted_pages = sorted(section_info['pages'])
                example_url = sorted_pages[0]
                for url in sorted_pages:
                    if url.rstrip('/').count('/') == 2:
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="section-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            sections_html += f"""
            <div class="section-item">
                <div class="section-header">
                    <h3 class="section-signature">Section {html.escape(section_signature)}</h3>
                    <span class="section-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="section-details">
                    <div class="section-detail-row">
                        <strong>Label:</strong> {html.escape(label_display)}
                    </div>
                    <div class="section-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(section_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="sections-section">
            <h2>Section Regions Found Across Site</h2>
            <p class="section-intro">The following {len(sections_data)} unique section region{'s were' if len(sections_data) != 1 else ' was'} detected.
            Each section has been assigned a signature for tracking across pages. Verify each has a meaningful, unique accessible name and represents a significant content region.</p>
            <div class="sections-list">
                {sections_html}
            </div>
        </section>
        """

    def _generate_headers_html(self, headers_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for header/banner landmarks found across the site"""
        logger.warning(f"_generate_headers_html called with {len(headers_data) if headers_data else 0} headers")
        if not headers_data:
            logger.warning("No headers data - returning empty string")
            return ""

        sorted_headers = sorted(headers_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        headers_html = ""
        for header_signature, header_info in sorted_headers:
            pages_count = len(header_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            label_display = header_info.get('headerLabel', '(no label)')
            if not label_display:
                label_display = '(no label)'

            pages_list_html = ""
            if pages_count <= 3:
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(header_info['pages'])])
                pages_list_html = f"""
                    <div class="header-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                sorted_pages = sorted(header_info['pages'])
                example_url = sorted_pages[0]
                for url in sorted_pages:
                    if url.rstrip('/').count('/') == 2:
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="header-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            headers_html += f"""
            <div class="header-item">
                <div class="header-header">
                    <h3 class="header-signature">Header {html.escape(header_signature)}</h3>
                    <span class="header-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="header-details">
                    <div class="header-detail-row">
                        <strong>Label:</strong> {html.escape(label_display)}
                    </div>
                    <div class="header-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(header_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="headers-section">
            <h2>Banner Regions (Header) Found Across Site</h2>
            <p class="section-intro">The following {len(headers_data)} unique banner region{'s were' if len(headers_data) != 1 else ' was'} detected.
            Each header has been assigned a signature for tracking across pages. Verify there is only one banner per page and it contains site-level content.</p>
            <div class="headers-list">
                {headers_html}
            </div>
        </section>
        """

    def _generate_footers_html(self, footers_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for footer/contentinfo landmarks found across the site"""
        logger.warning(f"_generate_footers_html called with {len(footers_data) if footers_data else 0} footers")
        if not footers_data:
            logger.warning("No footers data - returning empty string")
            return ""

        sorted_footers = sorted(footers_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        footers_html = ""
        for footer_signature, footer_info in sorted_footers:
            pages_count = len(footer_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            label_display = footer_info.get('footerLabel', '(no label)')
            if not label_display:
                label_display = '(no label)'

            pages_list_html = ""
            if pages_count <= 3:
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(footer_info['pages'])])
                pages_list_html = f"""
                    <div class="footer-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                sorted_pages = sorted(footer_info['pages'])
                example_url = sorted_pages[0]
                for url in sorted_pages:
                    if url.rstrip('/').count('/') == 2:
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="footer-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            footers_html += f"""
            <div class="footer-item">
                <div class="footer-header">
                    <h3 class="footer-signature">Footer {html.escape(footer_signature)}</h3>
                    <span class="footer-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="footer-details">
                    <div class="footer-detail-row">
                        <strong>Label:</strong> {html.escape(label_display)}
                    </div>
                    <div class="footer-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(footer_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="footers-section">
            <h2>Contentinfo Regions (Footer) Found Across Site</h2>
            <p class="section-intro">The following {len(footers_data)} unique contentinfo region{'s were' if len(footers_data) != 1 else ' was'} detected.
            Each footer has been assigned a signature for tracking across pages. Verify there is only one contentinfo per page and it contains site-level information.</p>
            <div class="footers-list">
                {footers_html}
            </div>
        </section>
        """

    def _generate_searches_html(self, searches_data: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for search landmarks found across the site"""
        logger.warning(f"_generate_searches_html called with {len(searches_data) if searches_data else 0} searches")
        if not searches_data:
            logger.warning("No searches data - returning empty string")
            return ""

        sorted_searches = sorted(searches_data.items(), key=lambda x: (len(x[1]['pages']), x[0]), reverse=True)

        searches_html = ""
        for search_signature, search_info in sorted_searches:
            pages_count = len(search_info['pages'])
            percentage = (pages_count / total_pages * 100) if total_pages > 0 else 0

            label_display = search_info.get('searchLabel', '(no label)')
            if not label_display:
                label_display = '(no label)'

            pages_list_html = ""
            if pages_count <= 3:
                pages_list = '<br>'.join([f'• <a href="{html.escape(url)}" target="_blank">{html.escape(url)}</a>'
                                          for url in sorted(search_info['pages'])])
                pages_list_html = f"""
                    <div class="search-detail-row">
                        <strong>Found on:</strong><br>
                        {pages_list}
                    </div>
                """
            else:
                sorted_pages = sorted(search_info['pages'])
                example_url = sorted_pages[0]
                for url in sorted_pages:
                    if url.rstrip('/').count('/') == 2:
                        example_url = url
                        break

                pages_list_html = f"""
                    <div class="search-detail-row">
                        <strong>Example page:</strong> <a href="{html.escape(example_url)}" target="_blank">{html.escape(example_url)}</a>
                    </div>
                """

            searches_html += f"""
            <div class="search-item">
                <div class="search-header">
                    <h3 class="search-signature">Search {html.escape(search_signature)}</h3>
                    <span class="search-pages-count">{pages_count} page{'' if pages_count == 1 else 's'} ({percentage:.0f}%)</span>
                </div>
                <div class="search-details">
                    <div class="search-detail-row">
                        <strong>Label:</strong> {html.escape(label_display)}
                    </div>
                    <div class="search-detail-row">
                        <strong>XPath:</strong> <code>{html.escape(search_info.get('xpath', 'unknown'))}</code>
                    </div>
                    {pages_list_html}
                </div>
            </div>
            """

        return f"""
        <section class="searches-section">
            <h2>Search Regions Found Across Site</h2>
            <p class="section-intro">The following {len(searches_data)} unique search region{'s were' if len(searches_data) != 1 else ' was'} detected.
            Each search region has been assigned a signature for tracking across pages. Verify each contains actual search functionality and is properly labeled.</p>
            <div class="searches-list">
                {searches_html}
            </div>
        </section>
        """

    def _generate_documents_html(self, documents_by_type: Dict[str, List]) -> str:
        """Generate HTML section for electronic documents found during scraping"""
        if not documents_by_type:
            return ""

        total_docs = sum(len(docs) for docs in documents_by_type.values())
        logger.warning(f"_generate_documents_html called with {total_docs} documents across {len(documents_by_type)} types")

        documents_html = ""
        for doc_type, docs in sorted(documents_by_type.items()):
            # Group by internal vs external
            internal_docs = [d for d in docs if d.is_internal]
            external_docs = [d for d in docs if not d.is_internal]

            docs_html = ""
            if internal_docs:
                docs_html += "<h4>Internal Documents</h4><ul class='documents-list'>"
                for doc in sorted(internal_docs, key=lambda x: (x.language or 'zzz', x.document_url)):
                    link_text_display = html.escape(doc.link_text) if doc.link_text else html.escape(doc.document_url.split('/')[-1])

                    # Language badge and info
                    language_info = ""
                    if doc.language:
                        confidence_pct = f" ({int(doc.language_confidence * 100)}%)" if doc.language_confidence else ""
                        language_info = f'<span class="lang-badge">{html.escape(doc.language_display)}{confidence_pct}</span>'
                    else:
                        language_info = '<span class="lang-badge lang-unknown">Language Unknown</span>'

                    docs_html += f"""
                    <li class="document-item">
                        <div class="document-header">
                            <a href="{html.escape(doc.document_url)}" target="_blank" class="document-link">
                                {link_text_display}
                            </a>
                            {language_info}
                        </div>
                        <div class="document-meta">
                            <span class="document-referring">Found on: <a href="{html.escape(doc.referring_page_url)}" target="_blank">{html.escape(doc.referring_page_url)}</a></span>
                        </div>
                    </li>
                    """
                docs_html += "</ul>"

            if external_docs:
                docs_html += "<h4>External Documents</h4><ul class='documents-list'>"
                for doc in sorted(external_docs, key=lambda x: (x.language or 'zzz', x.document_url)):
                    link_text_display = html.escape(doc.link_text) if doc.link_text else html.escape(doc.document_url.split('/')[-1])

                    # Language badge and info
                    language_info = ""
                    if doc.language:
                        confidence_pct = f" ({int(doc.language_confidence * 100)}%)" if doc.language_confidence else ""
                        language_info = f'<span class="lang-badge">{html.escape(doc.language_display)}{confidence_pct}</span>'
                    else:
                        language_info = '<span class="lang-badge lang-unknown">Language Unknown</span>'

                    docs_html += f"""
                    <li class="document-item">
                        <div class="document-header">
                            <a href="{html.escape(doc.document_url)}" target="_blank" class="document-link">
                                {link_text_display}
                            </a>
                            {language_info}
                        </div>
                        <div class="document-meta">
                            <span class="document-referring">Found on: <a href="{html.escape(doc.referring_page_url)}" target="_blank">{html.escape(doc.referring_page_url)}</a></span>
                        </div>
                    </li>
                    """
                docs_html += "</ul>"

            documents_html += f"""
            <div class="document-type-section">
                <h3 class="document-type-title">
                    {html.escape(doc_type)}
                    <span class="document-count">({len(docs)} document{'s' if len(docs) != 1 else ''})</span>
                </h3>
                {docs_html}
            </div>
            """

        return f"""
        <section class="documents-section">
            <h2>Electronic Documents Found ({total_docs} total)</h2>
            <p class="section-intro">The following electronic documents were discovered during website scraping.
            Each document should be reviewed for accessibility compliance. Electronic documents like PDFs require specific accessibility features
            such as proper tagging, reading order, alternative text for images, and semantic structure.</p>
            <div class="documents-container">
                {documents_html}
            </div>
        </section>
        """

    def _generate_common_issues_html(self, common_issues: Dict[str, Dict], total_pages: int) -> str:
        """Generate HTML section for common issues appearing on >70% of pages"""

        has_common_issues = (common_issues['disco'] or
                            common_issues['info'] or
                            common_issues['accessible_names'])

        if not has_common_issues:
            return ""

        sections_html = ""

        # Discovery common issues (excluding items with dedicated sections: fonts, forms, navs)
        if common_issues['disco']:
            disco_html = "<ul class='common-issue-list'>"
            has_other_issues = False
            for issue_id, page_count in sorted(common_issues['disco'].items(), key=lambda x: x[1], reverse=True):
                # Skip items with their own dedicated sections
                if issue_id in ('fonts_DiscoFontFound', 'DiscoFontFound',
                               'forms_DiscoFormOnPage', 'DiscoFormOnPage',
                               'landmarks_DiscoNavFound', 'DiscoNavFound',
                               'landmarks_DiscoAsideFound', 'DiscoAsideFound',
                               'landmarks_DiscoSectionFound', 'DiscoSectionFound',
                               'landmarks_DiscoHeaderFound', 'DiscoHeaderFound',
                               'landmarks_DiscoFooterFound', 'DiscoFooterFound',
                               'landmarks_DiscoSearchFound', 'DiscoSearchFound'):
                    continue
                has_other_issues = True
                catalog_info = IssueCatalog.get_issue(issue_id)
                description = catalog_info.get('description', issue_id)
                percentage = (page_count / total_pages * 100) if total_pages > 0 else 0
                disco_html += f"""
                <li>
                    <strong>{html.escape(issue_id)}</strong> - Appears on {page_count} pages ({percentage:.0f}%)
                    <div class="common-issue-desc">{html.escape(description)}</div>
                </li>
                """
            disco_html += "</ul>"

            # Only show this section if there are other disco issues besides fonts/forms
            if has_other_issues:
                sections_html += f"""
                <div class="common-section disco">
                    <h3>Common Discovery Issues</h3>
                    <p class="common-intro">These issues appear on more than 70% of pages and have been filtered from individual page listings:</p>
                    {disco_html}
                </div>
                """

        # Info common issues
        if common_issues['info']:
            info_html = "<ul class='common-issue-list'>"
            for issue_id, page_count in sorted(common_issues['info'].items(), key=lambda x: x[1], reverse=True):
                catalog_info = IssueCatalog.get_issue(issue_id)
                description = catalog_info.get('description', issue_id)
                percentage = (page_count / total_pages * 100) if total_pages > 0 else 0
                info_html += f"""
                <li>
                    <strong>{html.escape(issue_id)}</strong> - Appears on {page_count} pages ({percentage:.0f}%)
                    <div class="common-issue-desc">{html.escape(description)}</div>
                </li>
                """
            info_html += "</ul>"
            sections_html += f"""
            <div class="common-section info">
                <h3>Common Informational Items</h3>
                <p class="common-intro">These items appear on more than 70% of pages and have been filtered from individual page listings:</p>
                {info_html}
            </div>
            """

        # Accessible Names common issues
        if common_issues['accessible_names']:
            an_html = "<ul class='common-issue-list'>"
            for issue_id, page_count in sorted(common_issues['accessible_names'].items(), key=lambda x: x[1], reverse=True):
                catalog_info = IssueCatalog.get_issue(issue_id)
                description = catalog_info.get('description', issue_id)
                percentage = (page_count / total_pages * 100) if total_pages > 0 else 0
                an_html += f"""
                <li>
                    <strong>{html.escape(issue_id)}</strong> - Appears on {page_count} pages ({percentage:.0f}%)
                    <div class="common-issue-desc">{html.escape(description)}</div>
                </li>
                """
            an_html += "</ul>"
            sections_html += f"""
            <div class="common-section accessible-names">
                <h3>Common Accessible Name Issues</h3>
                <p class="common-intro">These issues appear on more than 70% of pages and have been filtered from individual page listings:</p>
                {an_html}
            </div>
            """

        return f"""
        <section class="common-issues-section">
            <h2>Site-Wide Issues</h2>
            <p class="section-intro">The following issues appear on most pages throughout the site. Address these globally rather than page-by-page.</p>
            {sections_html}
        </section>
        """

    def _generate_issue_breakdown_html(self, breakdown: Dict[str, Dict]) -> str:
        """Generate HTML for issue breakdown by type"""

        sections_html = ""

        # Discovery issues (excluding items with dedicated sections: fonts, forms, navs)
        if breakdown['disco']:
            disco_items = sorted(breakdown['disco'].items(), key=lambda x: x[1], reverse=True)
            disco_html = "<ul>"
            for issue_id, count in disco_items[:10]:  # Top 10
                # Skip items with their own dedicated sections
                if issue_id in ('fonts_DiscoFontFound', 'DiscoFontFound',
                               'forms_DiscoFormOnPage', 'DiscoFormOnPage',
                               'landmarks_DiscoNavFound', 'DiscoNavFound',
                               'landmarks_DiscoAsideFound', 'DiscoAsideFound',
                               'landmarks_DiscoSectionFound', 'DiscoSectionFound',
                               'landmarks_DiscoHeaderFound', 'DiscoHeaderFound',
                               'landmarks_DiscoFooterFound', 'DiscoFooterFound',
                               'landmarks_DiscoSearchFound', 'DiscoSearchFound'):
                    continue
                catalog_info = IssueCatalog.get_issue(issue_id)
                description = catalog_info.get('description', issue_id)
                disco_html += f"<li><strong>{issue_id}</strong> ({count}): {description}</li>"
            disco_html += "</ul>"

            # Only show this section if there are other disco issues besides fonts/forms/navs
            if disco_html != "<ul></ul>":
                total_disco = sum(count for id, count in breakdown['disco'].items()
                                 if id not in ('fonts_DiscoFontFound', 'DiscoFontFound',
                                              'forms_DiscoFormOnPage', 'DiscoFormOnPage',
                                              'landmarks_DiscoNavFound', 'DiscoNavFound',
                                              'landmarks_DiscoAsideFound', 'DiscoAsideFound',
                                              'landmarks_DiscoSectionFound', 'DiscoSectionFound',
                                              'landmarks_DiscoHeaderFound', 'DiscoHeaderFound',
                                              'landmarks_DiscoFooterFound', 'DiscoFooterFound',
                                              'landmarks_DiscoSearchFound', 'DiscoSearchFound'))
                sections_html += f"""
                <div class="breakdown-section disco">
                    <h3>Discovery Issues ({total_disco} total)</h3>
                    {disco_html}
                </div>
                """

        # Info issues
        if breakdown['info']:
            info_items = sorted(breakdown['info'].items(), key=lambda x: x[1], reverse=True)
            info_html = "<ul>"
            for issue_id, count in info_items[:10]:  # Top 10
                catalog_info = IssueCatalog.get_issue(issue_id)
                description = catalog_info.get('description', issue_id)
                info_html += f"<li><strong>{issue_id}</strong> ({count}): {description}</li>"
            info_html += "</ul>"

            sections_html += f"""
            <div class="breakdown-section info">
                <h3>Informational Items ({sum(breakdown['info'].values())} total)</h3>
                {info_html}
            </div>
            """

        # Accessible Names issues
        if breakdown['accessible_names']:
            an_items = sorted(breakdown['accessible_names'].items(), key=lambda x: x[1], reverse=True)
            an_html = "<ul>"
            for issue_id, count in an_items[:10]:  # Top 10
                catalog_info = IssueCatalog.get_issue(issue_id)
                description = catalog_info.get('description', issue_id)
                an_html += f"<li><strong>{issue_id}</strong> ({count}): {description}</li>"
            an_html += "</ul>"

            sections_html += f"""
            <div class="breakdown-section accessible-names">
                <h3>Accessible Name Issues ({sum(breakdown['accessible_names'].values())} total)</h3>
                {an_html}
            </div>
            """

        return sections_html if sections_html else "<p>No issues to display.</p>"

    def _generate_pdf_report(self, data: Dict[str, Any]) -> bytes:
        """
        Generate PDF format report

        Args:
            data: Report data

        Returns:
            PDF content as bytes
        """
        try:
            from weasyprint import HTML, CSS
            from io import BytesIO

            # Generate HTML first
            html_content = self._generate_html_report(data)

            # Convert to PDF
            pdf_bytes = HTML(string=html_content).write_pdf()

            return pdf_bytes

        except ImportError:
            logger.error("WeasyPrint not installed. Cannot generate PDF.")
            raise ImportError(
                "WeasyPrint is required for PDF generation. "
                "Install with: pip install weasyprint"
            )

    def _get_html_css(self) -> str:
        """Get CSS styles for HTML reports"""
        return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        header {
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.2em;
            color: #7f8c8d;
            margin-bottom: 15px;
        }

        .metadata {
            color: #666;
            font-size: 0.95em;
        }

        .metadata p {
            margin: 5px 0;
        }

        .metadata a {
            color: #3498db;
            text-decoration: none;
        }

        .metadata a:hover {
            text-decoration: underline;
        }

        h2 {
            color: #2c3e50;
            font-size: 1.8em;
            margin-top: 40px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }

        h3 {
            color: #34495e;
            font-size: 1.3em;
            margin-bottom: 10px;
        }

        h4 {
            color: #555;
            font-size: 1.1em;
            margin-bottom: 10px;
            margin-top: 15px;
        }

        .executive-summary {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .executive-summary p {
            margin-bottom: 20px;
            font-size: 1.05em;
            line-height: 1.7;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-card.disco {
            border-left-color: #9b59b6;
        }

        .stat-card.info {
            border-left-color: #3498db;
        }

        .stat-card.warning {
            border-left-color: #f39c12;
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 1em;
            color: #555;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .stat-detail {
            font-size: 0.85em;
            color: #7f8c8d;
        }

        .issue-breakdown {
            margin-top: 30px;
        }

        .breakdown-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }

        .breakdown-section.disco {
            border-left-color: #9b59b6;
        }

        .breakdown-section.info {
            border-left-color: #3498db;
        }

        .breakdown-section.accessible-names {
            border-left-color: #f39c12;
        }

        .breakdown-section h3 {
            margin-top: 0;
            color: #2c3e50;
        }

        .breakdown-section ul {
            margin-left: 20px;
            margin-top: 15px;
        }

        .breakdown-section li {
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .common-issues-section {
            margin-top: 30px;
            background: #fff8dc;
            padding: 25px;
            border-radius: 8px;
            border: 2px solid #f39c12;
        }

        .common-issues-section h2 {
            color: #856404;
            margin-top: 0;
        }

        .common-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }

        .common-section.disco {
            border-left-color: #9b59b6;
        }

        .common-section.info {
            border-left-color: #3498db;
        }

        .common-section.accessible-names {
            border-left-color: #f39c12;
        }

        .common-section h3 {
            margin-top: 0;
            color: #2c3e50;
        }

        .common-intro {
            color: #666;
            font-style: italic;
            margin-bottom: 15px;
        }

        .common-issue-list {
            list-style: none;
            padding-left: 0;
        }

        .common-issue-list li {
            background: #f8f9fa;
            padding: 12px 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 3px solid #dee2e6;
        }

        .common-issue-desc {
            margin-top: 5px;
            color: #666;
            font-size: 0.9em;
        }

        .pages-section {
            margin-top: 30px;
        }

        .section-intro {
            color: #666;
            font-size: 1.05em;
            margin-bottom: 15px;
            line-height: 1.7;
        }

        .accordion-controls {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
        }

        .btn-control {
            background: #0366d6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: background 0.2s;
        }

        .btn-control:hover {
            background: #0256c7;
        }

        .btn-control:focus {
            outline: 2px solid #0366d6;
            outline-offset: 2px;
        }

        .accordion {
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            overflow: hidden;
        }

        .accordion-item {
            border-bottom: 1px solid #e1e4e8;
        }

        .accordion-item:last-child {
            border-bottom: none;
        }

        .accordion-header {
            margin: 0;
        }

        .accordion-button {
            width: 100%;
            background: #f6f8fa;
            border: none;
            padding: 15px 20px;
            text-align: left;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
            font-size: 1em;
        }

        .accordion-button:hover {
            background: #e9ecef;
        }

        .accordion-button:focus {
            outline: 2px solid #0366d6;
            outline-offset: -2px;
        }

        .accordion-button.collapsed {
            background: #f6f8fa;
        }

        .accordion-title {
            flex: 1;
        }

        .page-title {
            font-size: 1.1em;
            font-weight: 600;
            color: #24292e;
            margin-bottom: 5px;
        }

        .page-url-small {
            font-size: 0.85em;
            color: #0366d6;
            margin-bottom: 5px;
            word-break: break-all;
        }

        .page-summary-small {
            font-size: 0.85em;
            color: #586069;
        }

        .issue-badge {
            background: #e1e4e8;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
            color: #24292e;
            margin-right: 8px;
        }

        .issue-breakdown-small {
            color: #586069;
        }

        .accordion-icon {
            font-size: 0.8em;
            color: #586069;
            margin-left: 15px;
            transition: transform 0.2s;
        }

        .accordion-collapse {
            background: white;
        }

        .accordion-body {
            padding: 20px;
            border-top: 1px solid #e1e4e8;
        }

        .page-url-full {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e1e4e8;
        }

        .page-url-full a {
            color: #0366d6;
            text-decoration: none;
            word-break: break-all;
        }

        .page-url-full a:hover {
            text-decoration: underline;
        }

        .issue-category {
            margin-bottom: 25px;
        }

        .issue-category.discovery h4 {
            color: #9b59b6;
        }

        .issue-category.informational h4 {
            color: #3498db;
        }

        .issue-category.accessible-names h4 {
            color: #f39c12;
        }

        .issue-list {
            margin-top: 10px;
        }

        .issue-item {
            background: #f8f9fa;
            border-left: 3px solid #dee2e6;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }

        .issue-header {
            margin-bottom: 8px;
        }

        .issue-id {
            font-family: 'Courier New', monospace;
            background: #e1e4e8;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: 600;
            color: #24292e;
        }

        .issue-description {
            color: #24292e;
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .issue-why, .issue-fix {
            font-size: 0.9em;
            color: #586069;
            margin-top: 8px;
            padding: 10px;
            background: white;
            border-radius: 4px;
            line-height: 1.6;
        }

        .issue-why strong, .issue-fix strong {
            color: #24292e;
        }

        .no-issues {
            text-align: center;
            padding: 40px 20px;
            color: #666;
            font-size: 1.1em;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .truncation-notice {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 25px;
            margin-top: 30px;
            margin-bottom: 20px;
        }

        .truncation-notice h3 {
            color: #856404;
            margin-bottom: 15px;
            font-size: 1.3em;
        }

        .truncation-notice p {
            color: #856404;
            margin-bottom: 10px;
            line-height: 1.6;
        }

        .truncation-notice p:last-child {
            margin-bottom: 0;
        }

        footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }

        footer p {
            margin: 5px 0;
        }

        @media print {
            .container {
                box-shadow: none;
                max-width: none;
            }

            .page-card {
                page-break-inside: avoid;
            }
        }

        /* Fonts section */
        .fonts-section {
            margin: 40px 0;
        }

        .fonts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .font-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }

        .font-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .font-name {
            font-family: var(--font-family, inherit);
            font-size: 1.3em;
            color: #2c3e50;
            margin: 0;
        }

        .font-pages-count {
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }

        .font-sizes {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .font-sizes strong {
            color: #34495e;
        }

        /* Forms section */
        .forms-section {
            margin: 40px 0;
        }

        .forms-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .form-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #9b59b6;
        }

        .form-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .form-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .search-badge {
            background: #27ae60;
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }

        .form-pages-count {
            background: #9b59b6;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .form-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .form-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .form-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        .form-method {
            color: #777;
            font-size: 0.9em;
            margin-left: 5px;
        }

        /* Navigation section */
        .navs-section {
            margin: 40px 0;
        }

        .navs-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .nav-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #e67e22;
        }

        .nav-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .nav-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .nav-pages-count {
            background: #e67e22;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .nav-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .nav-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .nav-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .nav-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        /* Asides section styles */
        .asides-section {
            margin: 40px 0;
        }

        .asides-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .aside-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }

        .aside-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .aside-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .aside-pages-count {
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .aside-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .aside-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .aside-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .aside-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        /* Sections section styles */
        .sections-section {
            margin: 40px 0;
        }

        .sections-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .section-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #16a085;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .section-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .section-pages-count {
            background: #16a085;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .section-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .section-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .section-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .section-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        /* Headers section styles */
        .headers-section {
            margin: 40px 0;
        }

        .headers-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .header-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
        }

        .header-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .header-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .header-pages-count {
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .header-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .header-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .header-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .header-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        /* Footers section styles */
        .footers-section {
            margin: 40px 0;
        }

        .footers-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .footer-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #9b59b6;
        }

        .footer-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .footer-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .footer-pages-count {
            background: #9b59b6;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .footer-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .footer-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .footer-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .footer-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        /* Searches section styles */
        .searches-section {
            margin: 40px 0;
        }

        .searches-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 20px;
        }

        .search-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #27ae60;
        }

        .search-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .search-signature {
            font-size: 1.2em;
            color: #2c3e50;
            margin: 0;
            font-family: 'Courier New', monospace;
        }

        .search-pages-count {
            background: #27ae60;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
            margin-left: auto;
        }

        .search-details {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .search-detail-row {
            color: #555;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .search-detail-row strong {
            color: #34495e;
            margin-right: 5px;
        }

        .search-detail-row code {
            background: #e8e8e8;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
            color: #c7254e;
        }

        /* Documents section styles */
        .documents-section {
            margin: 40px 0;
        }

        .documents-container {
            margin-top: 20px;
        }

        .document-type-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #f39c12;
            margin-bottom: 20px;
        }

        .document-type-title {
            color: #2c3e50;
            margin: 0 0 15px 0;
            font-size: 1.3em;
        }

        .document-count {
            color: #7f8c8d;
            font-size: 0.85em;
            font-weight: normal;
            margin-left: 8px;
        }

        .document-type-section h4 {
            color: #34495e;
            margin: 15px 0 10px 0;
            font-size: 1.1em;
        }

        .documents-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .document-item {
            padding: 12px;
            margin-bottom: 8px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #f39c12;
        }

        .document-link {
            color: #3498db;
            text-decoration: none;
            font-weight: 500;
        }

        .document-link:hover {
            text-decoration: underline;
        }

        .lang-badge {
            display: inline-block;
            background: #95a5a6;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.75em;
            margin-left: 8px;
        }

        .document-meta {
            margin-top: 5px;
            font-size: 0.85em;
            color: #7f8c8d;
        }

        .document-referring a {
            color: #7f8c8d;
            text-decoration: none;
        }

        .document-referring a:hover {
            color: #3498db;
            text-decoration: underline;
        }
    </style>
        """

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use in filename"""
        import re
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        safe_name = re.sub(r'[_\s]+', '_', safe_name)
        safe_name = safe_name.strip('_')
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        if not safe_name:
            safe_name = 'report'
        return safe_name
