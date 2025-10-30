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

from auto_a11y.core.database import Database


class StaticHTMLReportGenerator:
    """Generates self-contained multi-page static HTML accessibility reports"""

    def __init__(self, database: Database, output_dir: Optional[Path] = None):
        """
        Initialize the static HTML report generator

        Args:
            database: Database manager instance
            output_dir: Base directory for generated reports (defaults to reports/ in project root)
        """
        self.db = database
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / 'reports'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 template environment - set to templates directory so relative paths work
        template_dir = Path(__file__).parent.parent / 'web' / 'templates'
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

        # Add custom filters
        self._setup_template_filters()

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

            pages_data.append({
                'id': page_id,
                'title': page.title or 'Untitled Page',
                'url': page.url,
                'test_date': latest_result.test_date.strftime('%Y-%m-%d %H:%M:%S') if latest_result.test_date else None,
                'score': score,
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
                }
            })

        return pages_data

    def _calculate_page_score(self, test_result) -> float:
        """Calculate accessibility score for a page using result_processor's scoring logic"""
        from auto_a11y.testing.result_processor import ResultProcessor

        processor = ResultProcessor(None)
        score_data = processor.calculate_score(test_result)

        return score_data['score']

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
