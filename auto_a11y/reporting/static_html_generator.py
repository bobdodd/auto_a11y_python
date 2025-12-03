"""
Static HTML Report Generator

Generates multi-page static HTML reports that can be viewed offline.
Includes index, summary, and individual page detail HTML files.
Packages everything into a downloadable ZIP file.
"""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import jinja2
from flask_babel import force_locale, lazy_gettext

from auto_a11y.core.database import Database
from auto_a11y.reporting.issue_catalog import IssueCatalog


class StaticHTMLReportGenerator:
    """Generates self-contained multi-page static HTML accessibility reports"""

    def __init__(self, database: Database, output_dir: Optional[Path] = None, language: str = 'en'):
        """
        Initialize the static HTML report generator

        Args:
            database: Database manager instance
            output_dir: Base directory for generated reports (defaults to reports/ in project root)
            language: Language code for translations ('en' or 'fr', defaults to 'en')
        """
        self.db = database
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / 'reports'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.language = language

        # Setup Jinja2 template environment - set to templates directory so relative paths work
        template_dir = Path(__file__).parent.parent / 'web' / 'templates'
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            extensions=['jinja2.ext.i18n']
        )

        # Configure Jinja2 for Flask-Babel translations
        # These callables will be replaced by force_locale context manager
        self.template_env.install_gettext_callables(
            gettext=lambda x: x,
            ngettext=lambda s, p, n: s if n == 1 else p,
            newstyle=True
        )

        # Add custom filters
        self._setup_template_filters()

    def _get_translations(self) -> Dict[str, Dict[str, str]]:
        """Get translations for both EN and FR languages"""
        translations = {
            'en': {
                # Index page
                'deduplicated_report': 'Deduplicated Accessibility Report',
                'issues_grouped_by_components': 'Issues grouped by common components',
                'accessibility_score': 'Accessibility Score',
                'compliance_score': 'Compliance Score',
                'violations': 'Violations',
                'warnings': 'Warnings',
                'info_items': 'Info Items',
                'components': 'Components',
                'pages': 'Pages',
                'common_components': 'Common Components',
                'click_component_to_view': 'Click a component to view its deduplicated issues',
                'pages_with_non_component_issues': 'Pages with Non-Component Issues',
                'issues_not_in_components': 'Issues not associated with common components, organized by page',
                'search_pages': 'Search pages...',
                'no_common_components': 'No common components found',

                # Component detail page
                'component_deduplicated_issues': 'Component Deduplicated Issues',
                'back_to_index': 'Back to Index',
                'found_on': 'Found on',
                'page_s': 'page(s)',
                'deduplicated_issue_s': 'deduplicated issue(s)',
                'no_issues_found': 'No issues found for this component',

                # Page detail / unassigned page
                'index': 'Index',
                'untitled_page': 'Untitled Page',
                'status': 'Status',
                'tested': 'Tested',
                'last_tested': 'Last Tested',
                'recently': 'Recently',
                'issues_found': 'Issues Found',
                'errors': 'Errors',
                'score': 'Score',
                'full_page_accessibility_score': 'Full Page Accessibility Score',
                'all_issues_full_page': 'All issues (full page)',
                'non_component_issues_score': 'Non-Component Issues Score',
                'issues_not_in_common_components': 'Issues not in common components',
                'compliance_score': 'Compliance Score',
                'tests_passed': 'tests passed',
                'n_a': 'N/A',
                'no_data_available': 'No data available',
                'filter_test_results': 'Filter Test Results',
                'clear_all_filters': 'Clear All Filters',
                'active_filters': 'Active Filters',
                'showing': 'Showing',
                'of': 'of',
                'items': 'items',
                'issue_type': 'Issue Type',
                'impact_level': 'Impact Level',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low',
                'issue_touchpoint': 'Issue Touchpoint',
                'all_touchpoints': 'All Touchpoints',
                'general': 'General',

                # Impact levels (all variations)
                'critical': 'Critical',
                'high': 'High',
                'serious': 'Serious',
                'moderate': 'Moderate',
                'medium': 'Medium',
                'minor': 'Minor',
                'low': 'Low',
                'quick_search': 'Quick Search',
                'search_in_issues': 'Search in issue descriptions, error codes, or XPaths...',
                'search_placeholder': 'Search in issue descriptions, error codes, or XPaths...',
                'non_component_issues_for_page': 'Non-Component Issues for This Page',
                'issues_not_part_of_common': 'Issues not part of common components',
                'informational': 'Informational',
                'discovery': 'Discovery',

                # Issue details
                'instance': 'Instance',
                'guest': 'Guest',
                'about_this_issue': 'About this issue:',
                'what_the_issue_is': 'What the issue is:',
                'why_this_is_important': 'Why this is important:',
                'who_it_affects': 'Who it affects:',
                'how_to_remediate': 'How to remediate:',
                'relevant_test_criteria': 'Relevant test criteria:',
                'wcag_success_criteria': 'WCAG Success Criteria:',
                'touchpoint': 'Touchpoint',
                'impact': 'Impact',
                'more_about': 'More about',
                'ways_to_meet': 'Ways to meet',
                'affected_pages': 'Affected Pages',
                'show_all_pages': 'Show all',
                'element_details': 'Element Details:',
                'element': 'Element',
                'xpath': 'XPath',
                'location': 'Location',
                'responsive_breakpoint': 'Responsive Breakpoint',
                'px_width': 'px width',
                'css_state': 'CSS State',
                'code_snippet': 'Code Snippet',
                'rule': 'Rule',
                'help': 'Help',
                'how_to_fix': 'How to fix:',

                # Component types
                'form': 'Form',
                'navigation': 'Navigation',
                'aside': 'Aside',
                'section': 'Section',
                'header': 'Header',

                # Touchpoints
                'fonts': 'Fonts',
                'headings': 'Headings',
                'images': 'Images',
                'landmarks': 'Landmarks',
                'links': 'Links',
                'color_contrast': 'Color Contrast',
                'tabindex': 'Tab Index',

                # User roles
                'no login': 'Guest (no login)',

                # Misc
                'language': 'Language',
                'violation_s': 'violation(s)',
                'warning_s': 'warning(s)',
                'info': 'info',
                'hidden': 'hidden',
                'text': 'text',
                'search': 'search',
            },
            'fr': {
                # Index page
                'deduplicated_report': 'Rapport d\'accessibilité dédupliqué',
                'issues_grouped_by_components': 'Problèmes regroupés par composants communs',
                'accessibility_score': 'Score d\'accessibilité',
                'compliance_score': 'Score de conformité',
                'violations': 'Violations',
                'warnings': 'Avertissements',
                'info_items': 'Éléments informatifs',
                'components': 'Composants',
                'pages': 'Pages',
                'common_components': 'Composants communs',
                'click_component_to_view': 'Cliquez sur un composant pour afficher ses problèmes dédupliqués',
                'pages_with_non_component_issues': 'Pages avec problèmes hors composants',
                'issues_not_in_components': 'Problèmes non associés aux composants communs, organisés par page',
                'search_pages': 'Rechercher des pages...',
                'no_common_components': 'Aucun composant commun trouvé',

                # Component detail page
                'component_deduplicated_issues': 'Problèmes dédupliqués du composant',
                'back_to_index': 'Retour à l\'index',
                'found_on': 'Trouvé sur',
                'page_s': 'page(s)',
                'deduplicated_issue_s': 'problème(s) dédupliqué(s)',
                'no_issues_found': 'Aucun problème trouvé pour ce composant',

                # Page detail / unassigned page
                'index': 'Index',
                'untitled_page': 'Page sans titre',
                'status': 'Statut',
                'tested': 'Testé',
                'last_tested': 'Dernier test',
                'recently': 'Récemment',
                'issues_found': 'Problèmes trouvés',
                'errors': 'Erreurs',
                'score': 'Score',
                'full_page_accessibility_score': 'Score d\'accessibilité de la page complète',
                'all_issues_full_page': 'Tous les problèmes (page complète)',
                'non_component_issues_score': 'Score des problèmes hors composants',
                'issues_not_in_common_components': 'Problèmes non présents dans les composants communs',
                'compliance_score': 'Score de conformité',
                'tests_passed': 'tests réussis',
                'n_a': 'N/D',
                'no_data_available': 'Aucune donnée disponible',
                'filter_test_results': 'Filtrer les résultats',
                'clear_all_filters': 'Effacer tous les filtres',
                'active_filters': 'Filtres actifs',
                'showing': 'Affichage',
                'of': 'sur',
                'items': 'éléments',
                'issue_type': 'Type de problème',
                'impact_level': 'Niveau d\'impact',
                'high': 'Élevé',
                'medium': 'Moyen',
                'low': 'Faible',
                'issue_touchpoint': 'Point de contact',
                'all_touchpoints': 'Tous les points de contact',
                'general': 'Général',

                # Impact levels (all variations)
                'critical': 'Critique',
                'high': 'Élevé',
                'serious': 'Grave',
                'moderate': 'Modéré',
                'medium': 'Moyen',
                'minor': 'Mineur',
                'low': 'Faible',
                'quick_search': 'Recherche rapide',
                'search_in_issues': 'Rechercher dans les descriptions, codes d\'erreur ou XPath...',
                'search_placeholder': 'Rechercher dans les descriptions, codes d\'erreur ou XPath...',
                'non_component_issues_for_page': 'Problèmes hors composants pour cette page',
                'issues_not_part_of_common': 'Problèmes ne faisant pas partie de composants communs',
                'informational': 'Informatif',
                'discovery': 'Découverte',

                # Issue details
                'instance': 'Instance',
                'guest': 'Invité',
                'about_this_issue': 'À propos de ce problème :',
                'what_the_issue_is': 'En quoi consiste le problème :',
                'why_this_is_important': 'Pourquoi c\'est important :',
                'who_it_affects': 'Qui est affecté :',
                'how_to_remediate': 'Comment corriger :',
                'relevant_test_criteria': 'Critères de test pertinents :',
                'wcag_success_criteria': 'Critères de succès WCAG :',
                'touchpoint': 'Point de contact',
                'impact': 'Impact',
                'more_about': 'En savoir plus sur',
                'ways_to_meet': 'Comment satisfaire',
                'affected_pages': 'Pages affectées',
                'show_all_pages': 'Afficher toutes',
                'element_details': 'Détails de l\'élément :',
                'element': 'Élément',
                'xpath': 'XPath',
                'location': 'Emplacement',
                'responsive_breakpoint': 'Point d\'arrêt responsive',
                'px_width': 'px de largeur',
                'css_state': 'État CSS',
                'code_snippet': 'Extrait de code',
                'rule': 'Règle',
                'help': 'Aide',
                'how_to_fix': 'Comment corriger :',

                # Component types
                'form': 'Formulaire',
                'navigation': 'Navigation',
                'aside': 'Aparté',
                'section': 'Section',
                'header': 'En-tête',

                # Touchpoints
                'fonts': 'Polices',
                'headings': 'Titres',
                'images': 'Images',
                'landmarks': 'Points de repère',
                'links': 'Liens',
                'color_contrast': 'Contraste des couleurs',
                'tabindex': 'Index de tabulation',

                # User roles
                'no login': 'Invité (sans connexion)',

                # Misc
                'language': 'Langue',
                'violation_s': 'violation(s)',
                'warning_s': 'avertissement(s)',
                'info': 'info',
                'hidden': 'caché',
                'text': 'texte',
                'search': 'recherche',
            }
        }
        return translations

    def _setup_template_filters(self):
        """Setup custom Jinja2 filters"""

        def error_code_only(code: str) -> str:
            """Extract error code from full violation ID"""
            if ':' in code:
                return code.split(':')[1]
            return code

        def wcag_name(criterion: str) -> str:
            """Extract WCAG criterion name from full string"""
            parts = criterion.split()
            return parts[0] if parts else criterion

        def wcag_understanding_url(criterion_code: str) -> str:
            """Generate WCAG Understanding URL"""
            return f"https://www.w3.org/WAI/WCAG22/Understanding/{criterion_code}"

        def wcag_quickref_url(criterion_code: str) -> str:
            """Generate WCAG Quick Reference URL"""
            return f"https://www.w3.org/WAI/WCAG22/quickref/#{criterion_code}"

        # Register filters
        self.template_env.filters['error_code_only'] = error_code_only
        self.template_env.filters['wcag_name'] = wcag_name
        self.template_env.filters['wcag_understanding_url'] = wcag_understanding_url
        self.template_env.filters['wcag_quickref_url'] = wcag_quickref_url

    def _read_embedded_assets(self) -> dict:
        """Read Bootstrap CSS and JS files for embedding inline"""
        import re
        static_dir = Path(__file__).parent.parent / 'web' / 'static'

        assets = {}
        try:
            # Read Bootstrap CSS
            bootstrap_css_path = static_dir / 'css' / 'bootstrap.min.css'
            bootstrap_css = bootstrap_css_path.read_text(encoding='utf-8')
            # Remove source map reference to prevent browser from trying to load it
            bootstrap_css = bootstrap_css.replace('/*# sourceMappingURL=bootstrap.min.css.map */', '')
            assets['bootstrap_css'] = bootstrap_css

            # Read Bootstrap Icons CSS
            bootstrap_icons_path = static_dir / 'css' / 'bootstrap-icons.css'
            bootstrap_icons_css = bootstrap_icons_path.read_text(encoding='utf-8')
            # Replace font file URLs with empty string to prevent 404 errors
            # The icons won't display but there won't be console errors
            bootstrap_icons_css = re.sub(
                r'src:\s*url\([^)]+\)(\s*format\([^)]+\))?(,\s*url\([^)]+\)(\s*format\([^)]+\))?)*;',
                'src: url("");',
                bootstrap_icons_css
            )
            assets['bootstrap_icons_css'] = bootstrap_icons_css

            # Read Bootstrap JS
            bootstrap_js_path = static_dir / 'js' / 'bootstrap.bundle.min.js'
            bootstrap_js = bootstrap_js_path.read_text(encoding='utf-8')
            # Remove source map reference to prevent browser from trying to load it
            bootstrap_js = bootstrap_js.replace('//# sourceMappingURL=bootstrap.bundle.min.js.map', '')
            assets['bootstrap_js'] = bootstrap_js

        except Exception as e:
            logger.error(f"Failed to read embedded assets: {e}")
            # Return empty strings if files can't be read
            assets = {
                'bootstrap_css': '',
                'bootstrap_icons_css': '',
                'bootstrap_js': ''
            }

        return assets

    def generate_report(
        self,
        page_ids: List[str],
        project_name: str = "Accessibility Report",
        website_url: Optional[str] = None,
        wcag_level: str = "AA",
        touchpoints_tested: Optional[List[str]] = None,
        include_screenshots: bool = True,
        include_discovery: bool = True,
        ai_tests_enabled: bool = True
    ) -> Path:
        """
        Generate complete static HTML report

        Args:
            page_ids: List of page IDs to include in report
            project_name: Name of the project
            website_url: Base URL of the website
            wcag_level: WCAG conformance level (A, AA, AAA)
            touchpoints_tested: List of touchpoints included in testing
            include_screenshots: Whether to include page screenshots
            include_discovery: Whether to include discovery items
            ai_tests_enabled: Whether AI tests were enabled

        Returns:
            Path to generated ZIP file
        """
        # Create temporary directory for report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = self.output_dir / f'static_report_{timestamp}'
        report_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Collect data for all pages
            pages_data = self._collect_pages_data(page_ids, include_discovery)

            # Sort pages alphabetically by title for consistent ordering across all reports
            pages_data = sorted(pages_data, key=lambda p: p['title'].lower())

            # Generate summary statistics
            summary = self._generate_summary_stats(pages_data)

            # Create directory structure
            self._create_directory_structure(report_dir)

            # Copy static assets
            self._copy_assets(report_dir, include_screenshots, pages_data if include_screenshots else None)

            # Generate HTML files
            self._generate_index_html(report_dir, pages_data, summary, project_name,
                                     website_url, wcag_level, touchpoints_tested)

            self._generate_page_detail_htmls(report_dir, pages_data, project_name,
                                            wcag_level, touchpoints_tested)

            # Create manifest
            self._create_manifest(report_dir, pages_data, summary, project_name,
                                website_url, wcag_level, touchpoints_tested, ai_tests_enabled)

            # Package as ZIP
            zip_path = self._package_as_zip(report_dir, timestamp)

            return zip_path

        finally:
            # Clean up temporary directory
            if report_dir.exists():
                shutil.rmtree(report_dir)

    def _collect_pages_data(self, page_ids: List[str], include_discovery: bool) -> List[Dict[str, Any]]:
        """
        Collect all data for pages to be included in report

        Args:
            page_ids: List of page IDs
            include_discovery: Whether to include discovery items

        Returns:
            List of page data dictionaries
        """
        pages_data = []

        for page_id in page_ids:
            # Get page from database
            page = self.db.get_page(page_id)
            if not page:
                continue

            # Get latest test result
            latest_result = self.db.get_latest_test_result(page_id)
            if not latest_result:
                # Include page even without results
                pages_data.append({
                    'id': page_id,
                    'title': page.title or 'Untitled Page',
                    'url': page.url,
                    'test_date': None,
                    'score': 0,
                    'screenshot_path': page.screenshot_path,
                    'violations': [],
                    'warnings': [],
                    'informational': [],
                    'discovery': [],
                    'issues': {
                        'errors': 0,
                        'warnings': 0,
                        'info': 0,
                        'discovery': 0
                    }
                })
                continue

            # Organize issues by severity - TestResult already has them separated
            violations = []
            warnings = []
            informational = []
            discovery = []

            # Process violations (errors)
            for violation in latest_result.violations or []:
                violations.append({
                    'id': violation.id,
                    'description': violation.description,
                    'touchpoint': violation.touchpoint,
                    'impact': violation.impact.value if hasattr(violation.impact, 'value') else violation.impact,
                    'xpath': violation.xpath,
                    'html_snippet': violation.html,
                    'metadata': violation.metadata,
                    'wcag_criteria': violation.wcag_criteria
                })

            # Process warnings
            for warning in latest_result.warnings or []:
                warnings.append({
                    'id': warning.id,
                    'description': warning.description,
                    'touchpoint': warning.touchpoint,
                    'impact': warning.impact.value if hasattr(warning.impact, 'value') else warning.impact,
                    'xpath': warning.xpath,
                    'html_snippet': warning.html,
                    'metadata': warning.metadata,
                    'wcag_criteria': warning.wcag_criteria
                })

            # Process info items
            for info_item in latest_result.info or []:
                informational.append({
                    'id': info_item.id,
                    'description': info_item.description,
                    'touchpoint': info_item.touchpoint,
                    'impact': info_item.impact.value if hasattr(info_item.impact, 'value') else info_item.impact,
                    'xpath': info_item.xpath,
                    'html_snippet': info_item.html,
                    'metadata': info_item.metadata,
                    'wcag_criteria': info_item.wcag_criteria
                })

            # Process discovery items (if included)
            if include_discovery:
                for disco_item in latest_result.discovery or []:
                    discovery.append({
                        'id': disco_item.id,
                        'description': disco_item.description,
                        'touchpoint': disco_item.touchpoint,
                        'impact': disco_item.impact.value if hasattr(disco_item.impact, 'value') else disco_item.impact,
                        'xpath': disco_item.xpath,
                        'html_snippet': disco_item.html,
                        'metadata': disco_item.metadata,
                        'wcag_criteria': disco_item.wcag_criteria
                    })

            # Calculate score
            score = self._calculate_page_score(latest_result)

            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(latest_result)

            # Check for multi-state testing
            state_results = []
            if hasattr(latest_result, 'session_id') and latest_result.session_id:
                # Get all state results for this session
                all_session_results = self.db.get_test_results_by_session(latest_result.session_id)

                # Process each state
                for state_result in all_session_results:
                    state_violations = []
                    state_warnings = []

                    # Process violations for this state
                    for violation in state_result.violations or []:
                        state_violations.append({
                            'id': violation.id,
                            'description': violation.description,
                            'touchpoint': violation.touchpoint,
                            'impact': violation.impact.value if hasattr(violation.impact, 'value') else violation.impact,
                            'xpath': violation.xpath,
                            'html_snippet': violation.html,
                            'metadata': violation.metadata,
                            'wcag_criteria': violation.wcag_criteria
                        })

                    # Process warnings for this state
                    for warning in state_result.warnings or []:
                        state_warnings.append({
                            'id': warning.id,
                            'description': warning.description,
                            'touchpoint': warning.touchpoint,
                            'impact': warning.impact.value if hasattr(warning.impact, 'value') else warning.impact,
                            'xpath': warning.xpath,
                            'html_snippet': warning.html,
                            'metadata': warning.metadata,
                            'wcag_criteria': warning.wcag_criteria
                        })

                    # Get state description - handle both object and dict
                    state_description = f"State {state_result.state_sequence if hasattr(state_result, 'state_sequence') else 0}"
                    if hasattr(state_result, 'page_state') and state_result.page_state:
                        if isinstance(state_result.page_state, dict):
                            state_description = state_result.page_state.get('description', state_description)
                        elif hasattr(state_result.page_state, 'description'):
                            state_description = state_result.page_state.description

                    state_data = {
                        'sequence': state_result.state_sequence if hasattr(state_result, 'state_sequence') else 0,
                        'description': state_description,
                        'violations': state_violations,
                        'warnings': state_warnings,
                        'issues': {
                            'errors': len(state_violations),
                            'warnings': len(state_warnings)
                        }
                    }
                    state_results.append(state_data)

                # Sort by sequence
                state_results.sort(key=lambda s: s['sequence'])

            pages_data.append({
                'id': page_id,
                'title': page.title or 'Untitled Page',
                'url': page.url,
                'test_date': latest_result.test_date.strftime('%Y-%m-%d %H:%M:%S') if latest_result.test_date else None,
                'score': score,
                'compliance_score': compliance_score,
                'screenshot_path': page.screenshot_path,
                'violations': violations,
                'warnings': warnings,
                'informational': informational,
                'discovery': discovery,
                'issues': {
                    'errors': len(violations),
                    'warnings': len(warnings),
                    'info': len(informational),
                    'discovery': len(discovery)
                },
                'states': state_results  # Add multi-state results
            })

        return pages_data

    def _calculate_page_score(self, test_result) -> float:
        """Calculate accessibility score for a page using result_processor's scoring logic"""
        from auto_a11y.testing.result_processor import ResultProcessor

        processor = ResultProcessor()
        score_data = processor.calculate_score(test_result)

        return score_data['score']

    def _calculate_compliance_score(self, test_result) -> Dict[str, Any]:
        """Calculate compliance score (percentage of tests with zero violations)"""
        # Get unique test codes that have violations/warnings
        failed_test_codes = set()

        # Extract test codes from violations
        for v in test_result.violations or []:
            test_code = v.id if hasattr(v, 'id') else ''
            if test_code:
                # Extract base code (before underscore if present)
                base_code = test_code.split('_')[0] if '_' in test_code else test_code
                failed_test_codes.add(base_code)

        # Extract test codes from warnings
        for w in test_result.warnings or []:
            test_code = w.id if hasattr(w, 'id') else ''
            if test_code:
                base_code = test_code.split('_')[0] if '_' in test_code else test_code
                failed_test_codes.add(base_code)

        # Count total tests run from metadata
        total_tests = test_result.metadata.get('test_count', 0) if hasattr(test_result, 'metadata') and test_result.metadata else 0
        failed_tests = len(failed_test_codes)
        passed_tests = max(0, total_tests - failed_tests)

        return {
            'score': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_tests': total_tests
        }

    def _generate_summary_stats(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics across all pages"""
        total_errors = sum(p['issues']['errors'] for p in pages_data)
        total_warnings = sum(p['issues']['warnings'] for p in pages_data)
        total_info = sum(p['issues']['info'] for p in pages_data)
        total_discovery = sum(p['issues']['discovery'] for p in pages_data)

        pages_with_errors = sum(1 for p in pages_data if p['issues']['errors'] > 0)
        pages_with_warnings = sum(1 for p in pages_data if p['issues']['warnings'] > 0)
        pages_with_info = sum(1 for p in pages_data if p['issues']['info'] > 0)
        pages_with_discovery = sum(1 for p in pages_data if p['issues']['discovery'] > 0)

        scores = [p['score'] for p in pages_data if p['score'] > 0]
        average_score = sum(scores) / len(scores) if scores else 0.0

        # Determine compliance level
        if total_errors == 0:
            compliance_level = 'pass'
        elif average_score >= 70:
            compliance_level = 'partial'
        else:
            compliance_level = 'fail'

        # Calculate top issues
        top_issues = self._calculate_top_issues(pages_data)

        # Group by touchpoint
        by_touchpoint = self._group_by_touchpoint(pages_data)

        # Group by WCAG
        by_wcag = self._group_by_wcag(pages_data)

        return {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_info': total_info,
            'total_discovery': total_discovery,
            'pages_with_errors': pages_with_errors,
            'pages_with_warnings': pages_with_warnings,
            'pages_with_info': pages_with_info,
            'pages_with_discovery': pages_with_discovery,
            'average_score': average_score,
            'compliance_level': compliance_level,
            'top_issues': top_issues,
            'by_touchpoint': by_touchpoint,
            'by_wcag': by_wcag,
            'recommendations': self._generate_recommendations(total_errors, total_warnings, average_score)
        }

    def _calculate_top_issues(self, pages_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """Calculate top issues across all pages"""
        issue_counts = {}

        for page in pages_data:
            for issue_list in [page['violations'], page['warnings'], page['informational']]:
                for issue in issue_list:
                    code = issue['id']
                    if code not in issue_counts:
                        issue_counts[code] = {
                            'title': issue.get('metadata', {}).get('title', code),
                            'count': 0,
                            'pages': set(),
                            'severity': 'error' if issue in page['violations'] else 'warning',
                            'impact': issue.get('impact', 'medium')
                        }
                    issue_counts[code]['count'] += 1
                    issue_counts[code]['pages'].add(page['id'])

        # Sort by count and convert to list
        top_issues = sorted(issue_counts.values(), key=lambda x: x['count'], reverse=True)[:limit]

        # Convert sets to counts
        for issue in top_issues:
            issue['pages'] = len(issue['pages'])

        return top_issues

    def _group_by_touchpoint(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        """Group issues by touchpoint"""
        touchpoint_stats = {}

        for page in pages_data:
            for issue_list, severity in [
                (page['violations'], 'errors'),
                (page['warnings'], 'warnings'),
                (page['informational'], 'info')
            ]:
                for issue in issue_list:
                    touchpoint = issue.get('touchpoint', 'general')
                    if touchpoint not in touchpoint_stats:
                        touchpoint_stats[touchpoint] = {'errors': 0, 'warnings': 0, 'info': 0}
                    touchpoint_stats[touchpoint][severity] += 1

        return touchpoint_stats

    def _group_by_wcag(self, pages_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group issues by WCAG principle"""
        # This would require WCAG mapping - placeholder for now
        return {}

    def _generate_recommendations(self, errors: int, warnings: int, score: float) -> List[Dict[str, str]]:
        """Generate priority recommendations"""
        recommendations = []

        if errors > 0:
            recommendations.append({
                'title': 'Fix Critical Errors',
                'description': f'Address all {errors} error-level issues first as these represent serious accessibility barriers.'
            })

        if warnings > 0:
            recommendations.append({
                'title': 'Review Warnings',
                'description': f'Review and fix {warnings} warning-level issues to improve accessibility.'
            })

        if score < 70:
            recommendations.append({
                'title': 'Improve Overall Score',
                'description': f'Current average score is {score:.1f}%. Aim for at least 80% to ensure good accessibility.'
            })

        return recommendations

    def _create_directory_structure(self, report_dir: Path):
        """Create directory structure for static report"""
        (report_dir / 'pages').mkdir(exist_ok=True)
        (report_dir / 'assets' / 'css').mkdir(parents=True, exist_ok=True)
        (report_dir / 'assets' / 'js').mkdir(parents=True, exist_ok=True)
        (report_dir / 'assets' / 'images' / 'screenshots').mkdir(parents=True, exist_ok=True)
        (report_dir / 'assets' / 'fonts').mkdir(parents=True, exist_ok=True)
        (report_dir / 'data').mkdir(exist_ok=True)

    def _copy_assets(self, report_dir: Path, include_screenshots: bool, pages_data: Optional[List[Dict[str, Any]]]):
        """Copy CSS, JS, fonts, and images to report directory"""
        static_dir = Path(__file__).parent.parent / 'web' / 'static'

        # Copy CSS files
        css_files = ['bootstrap.min.css', 'bootstrap-icons.css', 'custom.css']
        for css_file in css_files:
            src = static_dir / 'css' / css_file
            if src.exists():
                shutil.copy(src, report_dir / 'assets' / 'css' / css_file)

        # Copy JS files
        js_files = ['bootstrap.bundle.min.js', 'filters.js', 'navigation.js', 'search.js']
        for js_file in js_files:
            src = static_dir / 'js' / js_file
            if src.exists():
                shutil.copy(src, report_dir / 'assets' / 'js' / js_file)

        # Copy fonts (Bootstrap Icons)
        fonts_dir = static_dir / 'fonts'
        if fonts_dir.exists():
            for font_file in fonts_dir.glob('*'):
                shutil.copy(font_file, report_dir / 'assets' / 'fonts' / font_file.name)

        # Copy screenshots
        if include_screenshots and pages_data:
            screenshots_dir = Path(__file__).parent.parent.parent / 'screenshots'
            for page in pages_data:
                if page.get('screenshot_path'):
                    screenshot_file = screenshots_dir / page['screenshot_path']
                    if screenshot_file.exists():
                        shutil.copy(
                            screenshot_file,
                            report_dir / 'assets' / 'images' / 'screenshots' / screenshot_file.name
                        )

    def _generate_index_html(self, report_dir: Path, pages_data: List[Dict[str, Any]],
                            summary: Dict[str, Any], project_name: str, website_url: Optional[str],
                            wcag_level: str, touchpoints_tested: Optional[List[str]]):
        """Generate index.html file"""
        template = self.template_env.get_template('static_report/index.html')

        with force_locale(self.language):
            html = template.render(
                pages=pages_data,
                summary=summary,
                project_name=project_name,
                website_url=website_url,
                wcag_level=wcag_level,
                touchpoints_tested=touchpoints_tested or [],
                generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                current_page='index',
                asset_path='assets/',
                index_path=''
            )

        (report_dir / 'index.html').write_text(html, encoding='utf-8')

    def _generate_summary_html(self, report_dir: Path, pages_data: List[Dict[str, Any]],
                               summary: Dict[str, Any], project_name: str, website_url: Optional[str],
                               wcag_level: str, touchpoints_tested: Optional[List[str]],
                               ai_tests_enabled: bool):
        """Generate summary.html file"""
        template = self.template_env.get_template('static_report/summary.html')

        with force_locale(self.language):
            html = template.render(
                pages=pages_data,
                summary=summary,
                project_name=project_name,
                website_url=website_url,
                wcag_level=wcag_level,
                touchpoints_tested=touchpoints_tested or [],
                ai_tests_enabled=ai_tests_enabled,
                generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                current_page='summary',
                asset_path='assets/',
                index_path='',
                report_version='1.0.0'
            )

        (report_dir / 'summary.html').write_text(html, encoding='utf-8')

    def _generate_page_detail_htmls(self, report_dir: Path, pages_data: List[Dict[str, Any]],
                                    project_name: str, wcag_level: str,
                                    touchpoints_tested: Optional[List[str]]):
        """Generate individual page detail HTML files with inlined CSS/JS"""
        template = self.template_env.get_template('static_report/page_detail.html')

        # Read CSS and JS files to inline them
        static_dir = Path(__file__).parent.parent / 'web' / 'static'
        import urllib.request

        # Read Bootstrap CSS - use CDN if local file doesn't exist
        bootstrap_css = ''
        bootstrap_css_path = static_dir / 'css' / 'bootstrap.min.css'
        if bootstrap_css_path.exists():
            bootstrap_css = bootstrap_css_path.read_text(encoding='utf-8')
        else:
            # Fetch from CDN
            try:
                with urllib.request.urlopen('https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css') as response:
                    bootstrap_css = response.read().decode('utf-8')
            except Exception as e:
                print(f"Warning: Could not fetch Bootstrap CSS from CDN: {e}")

        # Read Bootstrap Icons CSS - use CDN if local file doesn't exist
        bootstrap_icons_css = ''
        bootstrap_icons_path = static_dir / 'css' / 'bootstrap-icons.css'
        if bootstrap_icons_path.exists():
            bootstrap_icons_css = bootstrap_icons_path.read_text(encoding='utf-8')
        else:
            # Fetch from CDN
            try:
                with urllib.request.urlopen('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css') as response:
                    bootstrap_icons_css = response.read().decode('utf-8')
            except Exception as e:
                print(f"Warning: Could not fetch Bootstrap Icons CSS from CDN: {e}")

        # Read Bootstrap JS - use CDN if local file doesn't exist
        bootstrap_js = ''
        bootstrap_js_path = static_dir / 'js' / 'bootstrap.bundle.min.js'
        if bootstrap_js_path.exists():
            bootstrap_js = bootstrap_js_path.read_text(encoding='utf-8')
        else:
            # Fetch from CDN
            try:
                with urllib.request.urlopen('https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js') as response:
                    bootstrap_js = response.read().decode('utf-8')
            except Exception as e:
                print(f"Warning: Could not fetch Bootstrap JS from CDN: {e}")

        # Read filters.js
        filters_js = ''
        filters_js_path = static_dir / 'js' / 'filters.js'
        if filters_js_path.exists():
            filters_js = filters_js_path.read_text(encoding='utf-8')

        for index, page in enumerate(pages_data, start=1):
            # Collect all unique touchpoints for filters
            all_touchpoints = set()
            for issue_list in [page['violations'], page['warnings'], page['informational'], page['discovery']]:
                for issue in issue_list:
                    all_touchpoints.add(issue.get('touchpoint', 'general'))

            # Create navigation context
            navigation = {
                'previous': pages_data[index - 2] if index > 1 else None,
                'next': pages_data[index] if index < len(pages_data) else None,
                'pages': [{'number': i + 1, 'title': p['title'], 'current': i + 1 == index}
                         for i, p in enumerate(pages_data)]
            }

            if navigation['previous']:
                navigation['previous']['number'] = index - 1
            if navigation['next']:
                navigation['next']['number'] = index + 1

            with force_locale(self.language):
                html = template.render(
                    page=page,
                    violations=page['violations'],
                    warnings=page['warnings'],
                    informational=page['informational'],
                    discovery=page['discovery'],
                    errors_count=page['issues']['errors'],
                    warnings_count=page['issues']['warnings'],
                    info_count=page['issues']['info'],
                    discovery_count=page['issues']['discovery'],
                    compliance_score=page.get('compliance_score'),
                    all_touchpoints=sorted(all_touchpoints),
                    navigation=navigation,
                    project_name=project_name,
                    wcag_level=wcag_level,
                    touchpoints_tested=touchpoints_tested or [],
                    generation_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    asset_path='../assets/',
                    index_path='../',
                    # Inlined CSS and JS
                    bootstrap_css=bootstrap_css,
                    bootstrap_icons_css=bootstrap_icons_css,
                    bootstrap_js=bootstrap_js,
                    filters_js=filters_js,
                    inline_mode=True
                )

            filename = f'page_{str(index).zfill(3)}.html'
            (report_dir / 'pages' / filename).write_text(html, encoding='utf-8')

    def _create_manifest(self, report_dir: Path, pages_data: List[Dict[str, Any]],
                        summary: Dict[str, Any], project_name: str, website_url: Optional[str],
                        wcag_level: str, touchpoints_tested: Optional[List[str]], ai_tests_enabled: bool):
        """Create manifest.json with report metadata"""
        manifest = {
            'report_id': f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'generated_at': datetime.now().isoformat(),
            'generator_version': '1.0.0',
            'project': {
                'name': project_name,
                'url': website_url
            },
            'test_config': {
                'wcag_level': wcag_level,
                'touchpoints_tested': touchpoints_tested or [],
                'ai_tests_enabled': ai_tests_enabled
            },
            'statistics': {
                'total_pages': len(pages_data),
                'pages_tested': len(pages_data),
                'total_issues': summary['total_errors'] + summary['total_warnings'] + summary['total_info'],
                'errors': summary['total_errors'],
                'warnings': summary['total_warnings'],
                'info': summary['total_info'],
                'discovery': summary['total_discovery'],
                'average_score': summary['average_score']
            },
            'pages': [
                {
                    'id': p['id'],
                    'title': p['title'],
                    'url': p['url'],
                    'file': f'pages/page_{str(i + 1).zfill(3)}.html',
                    'score': p['score'],
                    'issues': p['issues']
                }
                for i, p in enumerate(pages_data)
            ]
        }

        (report_dir / 'data' / 'manifest.json').write_text(
            json.dumps(manifest, indent=2),
            encoding='utf-8'
        )

    def _package_as_zip(self, source_dir: Path, timestamp: str) -> Path:
        """Package report directory as ZIP file"""
        zip_filename = f'accessibility_report_{timestamp}.zip'
        zip_path = self.output_dir / zip_filename

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

        return zip_path

    def generate_project_deduplicated_report(
        self,
        project_id: Optional[str] = None,
        website_id: Optional[str] = None
    ) -> Path:
        """
        Generate deduplicated offline HTML report for an entire project or specific website.
        Groups issues by common components and allows filtering by component.

        Args:
            project_id: ID of the project to generate report for (optional if website_id provided)
            website_id: ID of specific website to generate report for (optional)

        Returns:
            Path to generated ZIP file
        """
        from auto_a11y.reporting.issue_catalog import IssueCatalog

        # Determine scope
        if website_id:
            # Generate for specific website
            website = self.db.get_website(website_id)
            if not website:
                raise ValueError(f"Website {website_id} not found")

            project = None
            if website.project_id:
                project = self.db.get_project(website.project_id)

            websites = [website]
            # Use project name if available, otherwise use website name
            project_name = project.name if project else website.name
        elif project_id:
            # Generate for entire project
            project = self.db.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")

            websites = self.db.get_websites(project_id)
            project_name = project.name
        else:
            # Generate for all projects
            project = None
            projects = self.db.get_projects()
            websites = []
            for p in projects:
                websites.extend(self.db.get_websites(p.id))
            project_name = "All_Projects"

        # Collect all data from websites and pages
        project_data = {
            'project': project,
            'websites': []
        }

        for website in websites:
            website_data = {
                'website': website,
                'pages': []
            }

            # Get all pages for this website
            pages = self.db.get_pages(website.id)

            for page in pages:
                # Get latest test result for this page
                test_result = self.db.get_latest_test_result(page.id)
                if test_result:
                    website_data['pages'].append({
                        'page': page,
                        'test_result': test_result
                    })

            if website_data['pages']:
                project_data['websites'].append(website_data)

        # Extract common components
        common_components = self._extract_common_components(project_data)

        # Deduplicate issues by component
        deduplicated_issues = self._deduplicate_issues_by_component(project_data, common_components)

        # Group issues by component
        issues_by_component = self._group_issues_by_component(deduplicated_issues, common_components)

        # Note: Issue counts will be calculated after pages_with_unassigned is created
        total_pages = sum(len(wd['pages']) for wd in project_data['websites'])

        # Calculate overall site scores (average across all pages)
        all_page_scores = []
        all_compliance_scores = []

        for website_data in project_data['websites']:
            for page_result in website_data['pages']:
                test_result = page_result.get('test_result')
                if test_result:
                    # Get accessibility score
                    page_score = self._calculate_page_score(test_result)
                    all_page_scores.append(page_score)

                    # Get compliance score (passed / total checks)
                    violations_list = test_result.violations if hasattr(test_result, 'violations') else []
                    warnings_list = test_result.warnings if hasattr(test_result, 'warnings') else []
                    info_list = test_result.info if hasattr(test_result, 'info') else []

                    total_tests = len(violations_list) + len(warnings_list) + len(info_list)
                    passed_tests = total_tests - len(violations_list)

                    if total_tests > 0:
                        compliance_score = (passed_tests / total_tests) * 100
                        all_compliance_scores.append(compliance_score)

        # Calculate averages
        overall_accessibility_score = sum(all_page_scores) / len(all_page_scores) if all_page_scores else 0
        overall_compliance_score = sum(all_compliance_scores) / len(all_compliance_scores) if all_compliance_scores else 0

        # Create temporary directory for report
        import tempfile
        import shutil

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temp_dir = Path(tempfile.mkdtemp(prefix='dedup_report_'))

        try:
            # Create directory structure
            (temp_dir / 'components').mkdir(exist_ok=True)
            (temp_dir / 'pages').mkdir(exist_ok=True)
            (temp_dir / 'assets' / 'css').mkdir(parents=True, exist_ok=True)
            (temp_dir / 'assets' / 'js').mkdir(parents=True, exist_ok=True)

            # Copy assets
            self._copy_dedup_assets(temp_dir)

            # Group unassigned issues by page
            pages_with_unassigned = self._group_unassigned_by_page(
                project_data, issues_by_component.get('unassigned', []), common_components
            )

            # Calculate statistics based on actual deduplicated issues that will be displayed
            # Count issues in components
            total_violations = 0
            total_warnings = 0
            total_info = 0

            for component_signature, component_issues in issues_by_component.items():
                if component_signature != 'unassigned':
                    for issue in component_issues:
                        if issue['type'] == 'violation':
                            total_violations += 1
                        elif issue['type'] == 'warning':
                            total_warnings += 1
                        elif issue['type'] == 'info':
                            total_info += 1

            # Count issues in unassigned (non-component) pages
            for page_data in pages_with_unassigned:
                total_violations += len(page_data['issues']['violations'])
                total_warnings += len(page_data['issues']['warnings'])
                total_info += len(page_data['issues']['info'])

            # Generate index page
            self._generate_dedup_index(
                temp_dir, project, project_name, common_components,
                issues_by_component, pages_with_unassigned,
                total_violations, total_warnings, total_info, total_pages,
                overall_accessibility_score, overall_compliance_score
            )

            # Generate component detail pages
            self._generate_component_pages(
                temp_dir, common_components, issues_by_component
            )

            # Generate page detail pages for unassigned issues
            self._generate_page_detail_pages(
                temp_dir, pages_with_unassigned, project, project_name, generation_date
            )

            # Package as ZIP
            safe_project_name = project_name.replace(' ', '_')
            zip_filename = f'{safe_project_name}_deduplicated_{timestamp}.zip'
            zip_path = self.output_dir / zip_filename

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)

            return zip_path
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _extract_common_components(self, data: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Extract common components (forms, navs, asides, sections, headers) from discovery issues.

        Args:
            data: Project report data

        Returns:
            Dictionary mapping signature -> component info with xpaths per page
        """
        common_components = {}

        # Iterate through all websites and pages
        for website_data in data.get('websites', []):
            website = website_data.get('website', {})

            for page_result in website_data.get('pages', []):
                page = page_result.get('page', {})
                page_url = page.url if hasattr(page, 'url') else page.get('url', '')

                test_result = page_result.get('test_result')
                if not test_result:
                    continue

                # Get discovery items
                discovery_items = test_result.discovery if hasattr(test_result, 'discovery') else []

                for d in discovery_items:
                    if hasattr(d, 'to_dict'):
                        d_dict = d.to_dict()
                    else:
                        d_dict = d if isinstance(d, dict) else {}

                    issue_id = d_dict.get('id', '')
                    metadata = d_dict.get('metadata', {})

                    # Extract signature and xpath for different component types
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

        # Filter to only include components that appear on 2+ pages
        filtered_components = {
            sig: comp_data
            for sig, comp_data in common_components.items()
            if len(comp_data['pages']) >= 2
        }

        return filtered_components

    def _deduplicate_issues_by_component(
        self,
        data: Dict[str, Any],
        common_components: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate issues by grouping them by component signature and rule ID.

        Args:
            data: Project report data
            common_components: Dictionary of common components

        Returns:
            List of deduplicated issue dictionaries
        """
        from auto_a11y.reporting.issue_catalog import IssueCatalog

        # Track unique issues: (rule_id, component_signature_or_xpath) -> issue data
        unique_issues = {}

        # Iterate through all websites and their pages
        for website_data in data.get('websites', []):
            for page_result in website_data.get('pages', []):
                page = page_result.get('page', {})
                page_url = page.url if hasattr(page, 'url') else page.get('url', '')

                test_result = page_result.get('test_result')
                if not test_result:
                    continue

                # Process all issue types except discovery
                for issue_type, issue_list_attr in [('violation', 'violations'),
                                                      ('warning', 'warnings'),
                                                      ('info', 'info')]:
                    issues = getattr(test_result, issue_list_attr, []) if hasattr(test_result, issue_list_attr) else []

                    for issue in issues:
                        if hasattr(issue, 'to_dict'):
                            issue_dict = issue.to_dict()
                        else:
                            issue_dict = issue if isinstance(issue, dict) else {}

                        # Enrich with catalog information in both EN and FR for client-side switching
                        with force_locale('en'):
                            issue_dict_en = IssueCatalog.enrich_issue(issue_dict if isinstance(issue, dict) else {})

                        with force_locale('fr'):
                            issue_dict_fr = IssueCatalog.enrich_issue(issue_dict if isinstance(issue, dict) else {})

                        # Use the current language version for primary data
                        issue_dict = issue_dict_en if self.language == 'en' else issue_dict_fr

                        rule_id = issue_dict.get('id', '')
                        issue_xpath = issue_dict.get('xpath', '')

                        # Get authenticated user info
                        metadata = issue_dict.get('metadata', {})
                        auth_user = metadata.get('authenticated_user', {})
                        user_name = auth_user.get('display_name', '') if auth_user else 'Guest'
                        user_roles = auth_user.get('roles', []) if auth_user else []

                        # Find which common component contains this issue
                        component_signature = None
                        component_type = None
                        component_label = None

                        for signature, comp_data in common_components.items():
                            comp_xpath = comp_data['xpaths_by_page'].get(page_url)
                            if comp_xpath and self._xpath_is_within(issue_xpath, comp_xpath):
                                component_signature = signature
                                component_type = comp_data['type']
                                component_label = comp_data['label']
                                break

                        # Create deduplication key
                        if component_signature:
                            dedup_key = (rule_id, component_signature)
                        else:
                            dedup_key = (rule_id, issue_xpath)

                        # Initialize or update issue data
                        if dedup_key not in unique_issues:
                            # Get enriched metadata for both languages
                            issue_metadata = issue_dict.get('metadata', {})
                            issue_metadata_en = issue_dict_en.get('metadata', {})
                            issue_metadata_fr = issue_dict_fr.get('metadata', {})

                            unique_issues[dedup_key] = {
                                'type': issue_type,
                                'rule_id': rule_id,
                                'description': issue_dict.get('description', ''),
                                'impact': issue_dict.get('impact', 'moderate'),
                                'wcag': ', '.join(issue_dict.get('wcag', [])),
                                'wcag_full': issue_metadata.get('wcag_full', []),
                                'touchpoint': issue_dict.get('touchpoint', ''),
                                'element': issue_dict.get('element', ''),
                                'xpath': issue_xpath,
                                'component_signature': component_signature,
                                'component_type': component_type,
                                'component_label': component_label,
                                # Enriched content from IssueCatalog - both languages
                                'description_en': issue_dict_en.get('description', ''),
                                'description_fr': issue_dict_fr.get('description', ''),
                                'why_en': issue_metadata_en.get('why', ''),
                                'why_fr': issue_metadata_fr.get('why', ''),
                                'who_en': issue_metadata_en.get('who', ''),
                                'who_fr': issue_metadata_fr.get('who', ''),
                                'full_remediation_en': issue_metadata_en.get('full_remediation', ''),
                                'full_remediation_fr': issue_metadata_fr.get('full_remediation', ''),
                                'pages': set(),
                                'test_users': set(),
                                'user_roles': set()
                            }

                        # Add page and user info
                        unique_issues[dedup_key]['pages'].add(page_url)
                        if user_name:
                            unique_issues[dedup_key]['test_users'].add(user_name)
                        if user_roles:
                            for role in user_roles:
                                unique_issues[dedup_key]['user_roles'].add(role)
                        if not auth_user:
                            unique_issues[dedup_key]['user_roles'].add('no login')

        # Convert to list and add page count
        result = []
        for issue_data in unique_issues.values():
            issue_data['pages'] = sorted(list(issue_data['pages']))
            issue_data['page_count'] = len(issue_data['pages'])
            issue_data['test_users'] = sorted(list(issue_data['test_users']))
            issue_data['user_roles'] = sorted(list(issue_data['user_roles']))
            result.append(issue_data)

        # Sort by impact (high -> medium -> low) then by type then by rule_id
        impact_order = {'critical': 0, 'high': 1, 'serious': 1, 'moderate': 2, 'medium': 2, 'minor': 3, 'low': 3}
        type_order = {'violation': 0, 'warning': 1, 'info': 2}

        result.sort(key=lambda x: (
            type_order.get(x['type'], 99),
            impact_order.get(x['impact'].lower(), 99),
            x['rule_id']
        ))

        return result

    def _xpath_is_within(self, issue_xpath: str, component_xpath: str) -> bool:
        """
        Check if an issue's XPath is within a component's XPath.

        Args:
            issue_xpath: XPath of the issue
            component_xpath: XPath of the component

        Returns:
            True if issue_xpath is within or equal to component_xpath
        """
        if not issue_xpath or not component_xpath:
            return False

        # Normalize xpaths by removing trailing slashes
        issue_xpath = issue_xpath.rstrip('/')
        component_xpath = component_xpath.rstrip('/')

        # Check if issue xpath starts with component xpath
        return issue_xpath == component_xpath or issue_xpath.startswith(component_xpath + '/')

    def _group_issues_by_component(
        self,
        deduplicated_issues: List[Dict[str, Any]],
        common_components: Dict[str, Dict]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group deduplicated issues by their component signature.

        Args:
            deduplicated_issues: List of deduplicated issues
            common_components: Dictionary of common components

        Returns:
            Dictionary mapping component signature -> list of issues
        """
        grouped = {}

        for issue in deduplicated_issues:
            component_sig = issue.get('component_signature')
            if component_sig:
                if component_sig not in grouped:
                    grouped[component_sig] = []
                grouped[component_sig].append(issue)
            else:
                # Issues without components go into 'unassigned' group
                if 'unassigned' not in grouped:
                    grouped['unassigned'] = []
                grouped['unassigned'].append(issue)

        return grouped

    def _copy_dedup_assets(self, report_dir: Path):
        """Copy CSS and JS assets to report directory"""
        static_dir = Path(__file__).parent.parent / 'web' / 'static'

        # Copy CSS files
        css_files = ['bootstrap.min.css', 'bootstrap-icons.css']
        for css_file in css_files:
            src = static_dir / 'css' / css_file
            if src.exists():
                shutil.copy(src, report_dir / 'assets' / 'css' / css_file)

        # Copy custom CSS (if exists)
        custom_css = static_dir / 'css' / 'custom.css'
        if custom_css.exists():
            shutil.copy(custom_css, report_dir / 'assets' / 'css' / 'custom.css')

        # Copy JS files
        js_files = ['bootstrap.bundle.min.js']
        for js_file in js_files:
            src = static_dir / 'js' / js_file
            if src.exists():
                shutil.copy(src, report_dir / 'assets' / 'js' / js_file)

    def _generate_dedup_index(
        self,
        report_dir: Path,
        project: Any,
        project_name: str,
        common_components: Dict[str, Dict],
        issues_by_component: Dict[str, List[Dict[str, Any]]],
        pages_with_unassigned: List[Dict[str, Any]],
        total_violations: int,
        total_warnings: int,
        total_info: int,
        total_pages: int,
        overall_accessibility_score: float,
        overall_compliance_score: float
    ):
        """Generate the index page for deduplicated report"""

        # Prepare components data with issue counts
        components_with_issues = []
        for signature, comp_data in common_components.items():
            issues = issues_by_component.get(signature, [])

            # Count issues by type
            violations = sum(1 for i in issues if i['type'] == 'violation')
            warnings = sum(1 for i in issues if i['type'] == 'warning')
            info_count = sum(1 for i in issues if i['type'] == 'info')

            # Calculate score for this component
            component_score = self._calculate_dedup_score(issues)

            # Create safe filename
            import re
            safe_sig = re.sub(r'[^a-zA-Z0-9_-]', '_', signature)

            components_with_issues.append({
                'signature': signature,
                'safe_signature': safe_sig,
                'type': comp_data['type'],
                'label': comp_data['label'],
                'page_count': len(comp_data['pages']),
                'violations': violations,
                'warnings': warnings,
                'info': info_count,
                'total_issues': len(issues),
                'score': component_score
            })

        # Sort by type then by violation count
        type_order = {'Navigation': 0, 'Header': 1, 'Footer': 2, 'Form': 3, 'Aside': 4, 'Section': 5}
        components_with_issues.sort(
            key=lambda x: (type_order.get(x['type'], 99), -x['violations'], -x['total_issues'])
        )

        # Get translations
        all_translations = self._get_translations()
        translations_en = all_translations['en']
        translations_fr = all_translations['fr']
        t = all_translations[self.language]  # Current language translations

        # Read embedded assets for standalone HTML
        embedded_assets = self._read_embedded_assets()

        # Render template
        template = self.template_env.get_template('static_report/dedup_index.html')

        with force_locale(self.language):
            html = template.render(
                asset_path='assets/',
                project=project,
                project_name=project_name,
                components_with_issues=components_with_issues,
                pages_with_unassigned=pages_with_unassigned,
                total_violations=total_violations,
                total_warnings=total_warnings,
                total_info=total_info,
                total_components=len(common_components),
                total_pages=total_pages,
                overall_accessibility_score=overall_accessibility_score,
                overall_compliance_score=overall_compliance_score,
                report_date=datetime.now(),
                # Translation support
                language=self.language,
                translations_en=translations_en,
                translations_fr=translations_fr,
                translations_json=json.dumps({'en': translations_en, 'fr': translations_fr}),
                t=t,
                # Embedded assets for standalone HTML
                bootstrap_css=embedded_assets['bootstrap_css'],
                bootstrap_icons_css=embedded_assets['bootstrap_icons_css'],
                bootstrap_js=embedded_assets['bootstrap_js']
            )

        # Write to file
        (report_dir / 'index.html').write_text(html, encoding='utf-8')

    def _generate_component_pages(
        self,
        report_dir: Path,
        common_components: Dict[str, Dict],
        issues_by_component: Dict[str, List[Dict[str, Any]]]
    ):
        """Generate individual component detail pages"""
        template = self.template_env.get_template('static_report/dedup_component.html')

        import re

        # Get translations
        all_translations = self._get_translations()
        translations_en = all_translations['en']
        translations_fr = all_translations['fr']
        t = all_translations[self.language]

        # Read embedded assets for standalone HTML
        embedded_assets = self._read_embedded_assets()

        # Generate page for each component
        for signature, comp_data in common_components.items():
            issues = issues_by_component.get(signature, [])

            # Calculate score for this component
            component_score = self._calculate_dedup_score(issues)

            # Create safe filename
            safe_sig = re.sub(r'[^a-zA-Z0-9_-]', '_', signature)

            with force_locale(self.language):
                html = template.render(
                    asset_path='../assets/',
                    component_type=comp_data['type'],
                    component_label=comp_data['label'],
                    component_signature=signature,
                    page_count=len(comp_data['pages']),
                    pages=sorted(list(comp_data['pages'])),
                    issues=issues,
                    total_issues=len(issues),
                    component_score=component_score,
                    report_date=datetime.now(),
                    # Translation support
                    language=self.language,
                    translations_en=translations_en,
                    translations_fr=translations_fr,
                    translations_json=json.dumps({'en': translations_en, 'fr': translations_fr}),
                    t=t,
                    # Embedded assets for standalone HTML
                    bootstrap_css=embedded_assets['bootstrap_css'],
                    bootstrap_icons_css=embedded_assets['bootstrap_icons_css'],
                    bootstrap_js=embedded_assets['bootstrap_js']
                )

            # Write to file
            (report_dir / 'components' / f'{safe_sig}.html').write_text(html, encoding='utf-8')

        # Note: Unassigned issues are now handled by _generate_page_detail_pages()
        # which creates individual page files in the pages/ directory

    def _calculate_dedup_score(self, issues: List[Dict[str, Any]]) -> float:
        """
        Calculate accessibility score for deduplicated issues.
        Uses similar logic to ResultProcessor but adapted for deduplicated data.

        Args:
            issues: List of deduplicated issues (violations only count toward score)

        Returns:
            Score as a percentage (0-100)
        """
        if not issues:
            return 100.0

        # Count violations only
        violations = [i for i in issues if i.get('type') == 'violation']

        if not violations:
            return 100.0

        # Weight by impact
        impact_weights = {
            'critical': 5,
            'serious': 5,
            'high': 5,
            'moderate': 3,
            'medium': 3,
            'minor': 1,
            'low': 1
        }

        total_weight = 0
        for issue in violations:
            impact = issue.get('impact', 'moderate')
            # Handle both string and enum formats
            if hasattr(impact, 'name'):
                impact = impact.name.lower()
            else:
                impact = str(impact).replace('IMPACT_LEVEL.', '').replace('ImpactLevel.', '').lower()
            weight = impact_weights.get(impact, 3)
            total_weight += weight

        # Calculate score (diminishing returns for more issues)
        # Using formula: 100 - (min(total_weight, 100))
        score = max(0, 100 - total_weight)

        return float(score)

    def _calculate_score_from_violations(self, violations: List) -> float:
        """
        Calculate accessibility score from raw violation objects (TestResult violations).

        Args:
            violations: List of violation objects from TestResult

        Returns:
            Score as a percentage (0-100)
        """
        if not violations:
            return 100.0

        # Weight by impact
        impact_weights = {
            'critical': 5,
            'serious': 5,
            'high': 5,
            'moderate': 3,
            'medium': 3,
            'minor': 1,
            'low': 1
        }

        total_weight = 0
        for issue in violations:
            impact = issue.impact if hasattr(issue, 'impact') else 'moderate'
            # Handle both string and enum formats
            if hasattr(impact, 'name'):
                impact = impact.name.lower()
            else:
                impact = str(impact).replace('IMPACT_LEVEL.', '').replace('ImpactLevel.', '').lower()
            weight = impact_weights.get(impact, 3)
            total_weight += weight

        # Calculate score (diminishing returns for more issues)
        # Using formula: 100 - (min(total_weight, 100))
        score = max(0, 100 - total_weight)

        return float(score)

    def _group_unassigned_by_page(
        self,
        project_data: Dict[str, Any],
        unassigned_issues: List[Dict[str, Any]],
        common_components: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """
        Group unassigned issues by page and prepare page data for index.

        Args:
            project_data: Project report data
            unassigned_issues: List of unassigned issues
            common_components: Dictionary of common components for filtering

        Returns:
            List of page data dictionaries with issue counts
        """
        import hashlib

        # Group issues by page URL
        issues_by_page = {}
        for issue in unassigned_issues:
            for page_url in issue['pages']:
                if page_url not in issues_by_page:
                    issues_by_page[page_url] = []
                issues_by_page[page_url].append(issue)

        # Create page data list
        pages_with_unassigned = []
        for page_url in issues_by_page.keys():
            # Find page metadata and actual test results from project_data
            page_title = None
            page_test_date = None
            page_score = 0
            compliance_score = None
            errors_count = 0
            warnings_count = 0
            info_count = 0
            discovery_count = 0
            original_metadata = {}
            total_page_violations = 0
            total_page_warnings = 0
            # Get actual non-deduplicated violations/warnings/info/discovery for this page only
            page_violations = []
            page_warnings = []
            page_info = []
            page_discovery = []

            for website_data in project_data.get('websites', []):
                for page_result in website_data.get('pages', []):
                    page = page_result.get('page', {})
                    if page.url == page_url:
                        page_title = page.title if hasattr(page, 'title') else None
                        page_test_date = page_result.get('test_date')

                        # Get the actual test result with individual instances
                        test_result = page_result.get('test_result')
                        if test_result:
                            # Calculate page score from the full test result
                            page_score = self._calculate_page_score(test_result)
                            # Save metadata for score calculation later
                            original_metadata = test_result.metadata if hasattr(test_result, 'metadata') else {}
                            # Access TestResult object attributes
                            violations_list = test_result.violations if hasattr(test_result, 'violations') else []
                            warnings_list = test_result.warnings if hasattr(test_result, 'warnings') else []
                            info_list = test_result.info if hasattr(test_result, 'info') else []
                            discovery_list = test_result.discovery if hasattr(test_result, 'discovery') else []

                            # Store totals for score calculation later
                            total_page_violations = len(violations_list)
                            total_page_warnings = len(warnings_list)

                            total_tests = len(violations_list) + len(warnings_list) + len(info_list)
                            passed_tests = total_tests - len(violations_list)
                            if total_tests > 0:
                                compliance_score = {
                                    'score': (passed_tests / total_tests) * 100,
                                    'passed_tests': passed_tests,
                                    'total_tests': total_tests
                                }

                            # Get full issue counts from test result
                            errors_count = len(violations_list)
                            warnings_count = len(warnings_list)
                            info_count = len(info_list)
                            discovery_count = len(discovery_list)

                            # Filter to only non-component issues for this page
                            # Match the logic from _extract_common_components to identify which issues
                            # are NOT part of common components
                            for issue in violations_list:
                                # Check if this issue's xpath matches any common component
                                is_component_issue = False
                                issue_xpath = issue.xpath if hasattr(issue, 'xpath') else ''

                                # Check against all common components for this page
                                if issue_xpath:
                                    for signature, comp_data in common_components.items():
                                        comp_xpath = comp_data['xpaths_by_page'].get(page_url)
                                        if comp_xpath and self._xpath_is_within(issue_xpath, comp_xpath):
                                            is_component_issue = True
                                            break

                                # Only include non-component issues
                                if not is_component_issue:
                                    page_violations.append(issue)

                            # For warnings, info, and discovery, also filter to non-component only
                            for issue in warnings_list:
                                is_component_issue = False
                                issue_xpath = issue.xpath if hasattr(issue, 'xpath') else ''

                                if issue_xpath:
                                    for signature, comp_data in common_components.items():
                                        comp_xpath = comp_data['xpaths_by_page'].get(page_url)
                                        if comp_xpath and self._xpath_is_within(issue_xpath, comp_xpath):
                                            is_component_issue = True
                                            break

                                if not is_component_issue:
                                    page_warnings.append(issue)

                            for issue in info_list:
                                is_component_issue = False
                                issue_xpath = issue.xpath if hasattr(issue, 'xpath') else ''

                                if issue_xpath:
                                    for signature, comp_data in common_components.items():
                                        comp_xpath = comp_data['xpaths_by_page'].get(page_url)
                                        if comp_xpath and self._xpath_is_within(issue_xpath, comp_xpath):
                                            is_component_issue = True
                                            break

                                if not is_component_issue:
                                    page_info.append(issue)

                            for issue in discovery_list:
                                is_component_issue = False
                                issue_xpath = issue.xpath if hasattr(issue, 'xpath') else ''

                                if issue_xpath:
                                    for signature, comp_data in common_components.items():
                                        comp_xpath = comp_data['xpaths_by_page'].get(page_url)
                                        if comp_xpath and self._xpath_is_within(issue_xpath, comp_xpath):
                                            is_component_issue = True
                                            break

                                if not is_component_issue:
                                    page_discovery.append(issue)

                        break
                if page_title:
                    break

            # Create safe URL for filename
            safe_url = hashlib.md5(page_url.encode()).hexdigest()[:12]

            # Calculate score for non-component issues on this page
            # Use the same scoring system as online test reporting (ResultProcessor.calculate_score)
            # Create a synthetic TestResult with only the filtered non-component issues
            if test_result and hasattr(test_result, 'metadata'):
                from types import SimpleNamespace

                # Adjust metadata to reflect the reduced number of violations
                # The scoring algorithm uses: score = (passed_checks / applicable_checks) * 100
                original_metadata = test_result.metadata if hasattr(test_result, 'metadata') else {}

                # Calculate how many violations and warnings were removed
                original_violations = len(violations_list)
                original_warnings = len(warnings_list)
                filtered_violations = len(page_violations)
                filtered_warnings = len(page_warnings)

                removed_violations = original_violations - filtered_violations
                removed_warnings = original_warnings - filtered_warnings
                removed_total = removed_violations + removed_warnings

                # Adjust the metadata counts
                # If we removed violations, that means those checks now pass (they were in components)
                adjusted_metadata = dict(original_metadata)
                adjusted_failed_checks = adjusted_metadata.get('failed_checks', 0) - removed_total
                adjusted_passed_checks = adjusted_metadata.get('passed_checks', 0) + removed_total
                # applicable_checks stays the same - same tests were run

                adjusted_metadata['failed_checks'] = max(0, adjusted_failed_checks)
                adjusted_metadata['passed_checks'] = adjusted_passed_checks

                # Create synthetic test result with only non-component issues
                synthetic_result = SimpleNamespace(
                    violations=page_violations,
                    warnings=page_warnings,
                    info=page_info,
                    discovery=page_discovery,
                    passes=test_result.passes if hasattr(test_result, 'passes') else [],
                    metadata=adjusted_metadata  # Use adjusted metadata
                )

                # Use the SAME scoring method as for full page score
                dedup_page_score = self._calculate_page_score(synthetic_result)
            else:
                # Fallback if no test_result available
                dedup_page_score = 100.0 if not page_violations else 0.0

            pages_with_unassigned.append({
                'url': page_url,
                'title': page_title,
                'safe_url': safe_url,
                'test_date': page_test_date,
                'score': page_score,  # Original full page score
                'dedup_score': dedup_page_score,  # Score for non-component issues only
                'compliance_score': compliance_score,
                'errors_count': errors_count,
                'warnings_count': warnings_count,
                'info_count': info_count,
                'discovery_count': discovery_count,
                'violations': len(page_violations),  # Use actual filtered non-component issue counts
                'warnings': len(page_warnings),
                'info': len(page_info),
                'total_issues': len(page_violations) + len(page_warnings) + len(page_info) + len(page_discovery),
                'issues': {
                    'violations': page_violations,  # Use actual test result issues, not deduplicated
                    'warnings': page_warnings,
                    'info': page_info,
                    'discovery': page_discovery
                }
            })

        # Sort alphabetically by title (fallback to URL if no title)
        pages_with_unassigned.sort(key=lambda x: (x.get('title') or x['url']).lower())

        return pages_with_unassigned

    def _generate_page_detail_pages(
        self,
        report_dir: Path,
        pages_with_unassigned: List[Dict[str, Any]],
        project: Any,
        project_name: str,
        generation_date: str
    ):
        """Generate individual page detail pages for unassigned issues"""
        template = self.template_env.get_template('static_report/dedup_unassigned.html')

        wcag_level = project.wcag_level if project and hasattr(project, 'wcag_level') else 'AA'

        # Get translations
        all_translations = self._get_translations()
        translations_en = all_translations['en']
        translations_fr = all_translations['fr']
        t = all_translations[self.language]

        # Read embedded assets for standalone HTML
        embedded_assets = self._read_embedded_assets()

        for page_data in pages_with_unassigned:
            # Create page object for template
            from types import SimpleNamespace
            page = SimpleNamespace(
                title=page_data.get('title', 'Untitled Page'),
                url=page_data['url'],
                score=page_data.get('score', 0),
                test_date=page_data.get('test_date', 'Recently')
            )

            # Enrich issues in both EN and FR for client-side switching
            def enrich_issue_bilingual(issue):
                """Convert issue object to dict with bilingual enrichment"""
                # Convert issue object to dict
                issue_dict = {
                    'id': issue.id if hasattr(issue, 'id') else '',
                    'description': issue.description if hasattr(issue, 'description') else '',
                    'impact': issue.impact if hasattr(issue, 'impact') else 'moderate',
                    'xpath': issue.xpath if hasattr(issue, 'xpath') else '',
                    'html_snippet': issue.html if hasattr(issue, 'html') else '',
                    'touchpoint': issue.touchpoint if hasattr(issue, 'touchpoint') else '',
                    'failure_summary': issue.failure_summary if hasattr(issue, 'failure_summary') else '',
                    'metadata': {}
                }

                # Copy metadata if present
                if hasattr(issue, 'metadata') and issue.metadata:
                    issue_dict['metadata'] = dict(issue.metadata)

                # Enrich with IssueCatalog in both languages
                with force_locale('en'):
                    enriched_en = IssueCatalog.enrich_issue(issue_dict.copy())

                with force_locale('fr'):
                    enriched_fr = IssueCatalog.enrich_issue(issue_dict.copy())

                # DEBUG: Log what we got
                if issue_dict.get('id') == 'ErrAriaLabelMayNotBeFoundByVoiceControl':
                    logger.warning("=" * 60)
                    logger.warning(f"DEBUG BILINGUAL ENRICHMENT - Issue ID: {issue_dict.get('id')}")
                    logger.warning(f"EN description_full: {enriched_en.get('description_full', 'N/A')[:80]}")
                    logger.warning(f"FR description_full: {enriched_fr.get('description_full', 'N/A')[:80]}")
                    logger.warning(f"Same? {enriched_en.get('description_full') == enriched_fr.get('description_full')}")
                    logger.warning("=" * 60)

                # Merge bilingual fields into the issue_dict
                issue_dict['description_en'] = enriched_en.get('description_full', enriched_en.get('description', ''))
                issue_dict['description_fr'] = enriched_fr.get('description_full', enriched_fr.get('description', ''))

                # Store bilingual metadata fields - IssueCatalog.enrich_issue() returns these exact field names
                issue_dict['metadata']['what_en'] = enriched_en['description_full']
                issue_dict['metadata']['what_fr'] = enriched_fr['description_full']
                issue_dict['metadata']['what_generic_en'] = enriched_en['description_full']
                issue_dict['metadata']['what_generic_fr'] = enriched_fr['description_full']
                issue_dict['metadata']['why_en'] = enriched_en['why_it_matters']
                issue_dict['metadata']['why_fr'] = enriched_fr['why_it_matters']
                issue_dict['metadata']['who_en'] = enriched_en['who_it_affects']
                issue_dict['metadata']['who_fr'] = enriched_fr['who_it_affects']
                issue_dict['metadata']['full_remediation_en'] = enriched_en['how_to_fix']
                issue_dict['metadata']['full_remediation_fr'] = enriched_fr['how_to_fix']
                issue_dict['metadata']['wcag_full'] = enriched_en['wcag_full']

                # Copy other metadata fields that might exist
                if hasattr(issue, 'metadata') and issue.metadata:
                    if hasattr(issue.metadata, 'authenticated_user'):
                        issue_dict['metadata']['authenticated_user'] = issue.metadata.authenticated_user
                    if hasattr(issue.metadata, 'breakpoint'):
                        issue_dict['metadata']['breakpoint'] = issue.metadata.breakpoint
                    if hasattr(issue.metadata, 'pseudoclass'):
                        issue_dict['metadata']['pseudoclass'] = issue.metadata.pseudoclass

                return issue_dict

            # Enrich all issues
            violations_enriched = [enrich_issue_bilingual(v) for v in page_data['issues']['violations']]
            warnings_enriched = [enrich_issue_bilingual(w) for w in page_data['issues']['warnings']]
            info_enriched = [enrich_issue_bilingual(i) for i in page_data['issues']['info']]
            discovery_enriched = [enrich_issue_bilingual(d) for d in page_data['issues']['discovery']]

            html = template.render(
                page=page,
                page_url=page_data['url'],
                page_title=page_data.get('title'),
                violations=violations_enriched,
                warnings=warnings_enriched,
                info=info_enriched,
                discovery=discovery_enriched,
                total_issues=page_data['total_issues'],
                errors_count=page_data.get('errors_count', 0),
                warnings_count=page_data.get('warnings_count', 0),
                info_count=page_data.get('info_count', 0),
                discovery_count=page_data.get('discovery_count', 0),
                compliance_score=page_data.get('compliance_score'),
                dedup_score=page_data.get('dedup_score', 0),  # Score for non-component issues
                report_date=datetime.now(),
                generation_date=generation_date,
                project_name=project_name,
                wcag_level=wcag_level,
                # Translation support
                language=self.language,
                translations_en=translations_en,
                translations_fr=translations_fr,
                translations_json=json.dumps({'en': translations_en, 'fr': translations_fr}),
                t=t,
                # Embedded assets for standalone HTML
                bootstrap_css=embedded_assets['bootstrap_css'],
                bootstrap_icons_css=embedded_assets['bootstrap_icons_css'],
                bootstrap_js=embedded_assets['bootstrap_js']
            )

            # Write to file
            (report_dir / 'pages' / f"{page_data['safe_url']}.html").write_text(html, encoding='utf-8')
