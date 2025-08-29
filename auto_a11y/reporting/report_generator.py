"""
Main report generator for accessibility test results
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import re

from auto_a11y.models import TestResult, Page, Website, Project, ImpactLevel
from auto_a11y.core.database import Database
from auto_a11y.reporting.formatters import (
    HTMLFormatter,
    JSONFormatter,
    ExcelFormatter,
    CSVFormatter,
    PDFFormatter
)

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates accessibility reports in multiple formats"""
    
    def __init__(self, database: Database, config: Dict[str, Any]):
        """
        Initialize report generator
        
        Args:
            database: Database connection
            config: Report configuration
        """
        self.db = database
        self.config = config
        self.report_dir = Path(config.get('REPORTS_DIR', 'reports'))
        self.report_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize formatters
        self.formatters = {
            'html': HTMLFormatter(config),
            'json': JSONFormatter(config),
            'xlsx': ExcelFormatter(config),
            'excel': ExcelFormatter(config),  # alias
            'csv': CSVFormatter(config),
            'pdf': PDFFormatter(config)
        }
    
    def _sanitize_filename(self, name: str, max_length: int = 50) -> str:
        """
        Sanitize a string to be safe for use in filenames
        
        Args:
            name: The name to sanitize
            max_length: Maximum length of the sanitized name
            
        Returns:
            A sanitized filename-safe string
        """
        # Remove or replace unsafe characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Replace multiple spaces/underscores with single underscore
        safe_name = re.sub(r'[_\s]+', '_', safe_name)
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        # Truncate if too long
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]
        # If empty after sanitization, use a default
        if not safe_name:
            safe_name = 'report'
        return safe_name
    
    def generate_page_report(
        self,
        page_id: str,
        format: str = 'html',
        include_ai: bool = True
    ) -> str:
        """
        Generate report for a single page
        
        Args:
            page_id: Page ID
            format: Output format (html, json, csv, pdf)
            include_ai: Include AI findings
            
        Returns:
            Path to generated report
        """
        # Get page and test results
        page = self.db.get_page(page_id)
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        website = self.db.get_website(page.website_id)
        project = self.db.get_project(website.project_id)
        test_result = self.db.get_latest_test_result(page_id)
        
        if not test_result:
            raise ValueError(f"No test results found for page {page_id}")
        
        # Prepare report data
        report_data = self._prepare_page_report_data(
            page, website, project, test_result, include_ai
        )
        
        # Generate report
        formatter = self.formatters.get(format)
        if not formatter:
            raise ValueError(f"Unsupported format: {format}")
        
        # Create filename with page URL
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a safe filename from the page URL
        page_name = page.url.replace('https://', '').replace('http://', '')
        page_name = self._sanitize_filename(page_name)
        filename = f"page_{page_name}_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content
        content = formatter.format_page_report(report_data)
        
        # Save report
        if format == 'pdf':
            # PDF returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        elif format in ['xlsx', 'excel']:
            # Excel returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated {format} report: {filepath}")
        return str(filepath)
    
    def generate_website_report(
        self,
        website_id: str,
        format: str = 'html',
        include_ai: bool = True
    ) -> str:
        """
        Generate report for entire website
        
        Args:
            website_id: Website ID
            format: Output format
            include_ai: Include AI findings
            
        Returns:
            Path to generated report
        """
        website = self.db.get_website(website_id)
        if not website:
            raise ValueError(f"Website {website_id} not found")
        
        project = self.db.get_project(website.project_id)
        pages = self.db.get_pages(website_id)
        
        # Get test results for all pages
        page_results = []
        for page in pages:
            test_result = self.db.get_latest_test_result(page.id)
            if test_result:
                page_results.append({
                    'page': page.__dict__ if hasattr(page, '__dict__') else page,
                    'test_result': test_result
                })
        
        # Prepare report data
        report_data = self._prepare_website_report_data(
            website, project, page_results, include_ai
        )
        
        # Generate report
        formatter = self.formatters.get(format)
        if not formatter:
            raise ValueError(f"Unsupported format: {format}")
        
        # Create filename with website name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a safe filename from the website name
        website_name = website.name or website.url.replace('https://', '').replace('http://', '')
        website_name = self._sanitize_filename(website_name)
        filename = f"website_{website_name}_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content
        content = formatter.format_website_report(report_data)
        
        # Save report
        if format == 'pdf':
            # PDF returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        elif format in ['xlsx', 'excel']:
            # Excel returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated {format} report: {filepath}")
        return str(filepath)
    
    def generate_all_projects_report(
        self,
        format: str = 'html',
        include_ai: bool = True
    ) -> str:
        """
        Generate report for all projects
        
        Args:
            format: Output format (html, xlsx, json)
            include_ai: Include AI analysis results
            
        Returns:
            Path to generated report file
        """
        logger.info(f"Generating all projects report in {format} format")
        
        # Get all projects
        projects = self.db.get_projects()
        
        if not projects:
            raise ValueError("No projects found")
        
        # Collect data for all projects
        all_projects_data = []
        total_stats = {
            'total_projects': len(projects),
            'total_websites': 0,
            'total_pages': 0,
            'total_tested': 0,
            'total_violations': 0,
            'total_warnings': 0
        }
        
        for project in projects:
            websites = self.db.get_websites(project.id)
            project_data = {
                'project': project.__dict__,
                'websites': [],
                'stats': self.db.get_project_stats(project.id)
            }
            
            for website in websites:
                pages = self.db.get_pages(website.id)
                website_data = {
                    'website': website.__dict__,
                    'pages': len(pages),
                    'tested': sum(1 for p in pages if p.status.value == 'tested'),
                    'violations': sum(p.violation_count for p in pages),
                    'warnings': sum(p.warning_count for p in pages)
                }
                project_data['websites'].append(website_data)
                
                # Update totals
                total_stats['total_websites'] += 1
                total_stats['total_pages'] += len(pages)
                total_stats['total_tested'] += website_data['tested']
                total_stats['total_violations'] += website_data['violations']
                total_stats['total_warnings'] += website_data['warnings']
            
            all_projects_data.append(project_data)
        
        # Prepare report data
        report_data = {
            'title': 'All Projects Accessibility Report',
            'projects': all_projects_data,
            'summary': total_stats,
            'generated_at': datetime.now().isoformat()
        }
        
        # Generate report
        formatter = self.formatters.get(format)
        if not formatter:
            raise ValueError(f"Unsupported format: {format}")
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"all_projects_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content based on format  
        if format in ['xlsx', 'excel']:
            # For Excel, use the proper Excel formatter
            content = formatter.format_all_projects_report(report_data)
        elif format == 'html':
            # For HTML, use the all projects formatter
            content = formatter.format_all_projects_report(report_data)
        elif format == 'pdf':
            # For PDF, use the PDF formatter
            content = formatter.format_all_projects_report(report_data)
        else:
            content = json.dumps(report_data, indent=2, default=str)
        
        self._save_report(filepath, content, format)
        
        logger.info(f"All projects report generated: {filepath}")
        return str(filepath)
    
    def _save_report(self, filepath: Path, content, format: str):
        """Save report content to file"""
        if format == 'json':
            filepath = filepath.with_suffix('.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == 'html':
            filepath = filepath.with_suffix('.html')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format in ['xlsx', 'excel']:
            filepath = filepath.with_suffix('.xlsx')
            # Excel content is bytes
            with open(filepath, 'wb') as f:
                f.write(content)
        elif format == 'pdf':
            filepath = filepath.with_suffix('.pdf')
            # PDF content is bytes
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def generate_project_report(
        self,
        project_id: str,
        format: str = 'html'
    ) -> str:
        """
        Generate report for entire project
        
        Args:
            project_id: Project ID
            format: Output format
            
        Returns:
            Path to generated report
        """
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        websites = self.db.get_websites(project_id)
        
        # Collect data for all websites
        website_data = []
        for website in websites:
            pages = self.db.get_pages(website.id)
            
            page_results = []
            for page in pages:
                test_result = self.db.get_latest_test_result(page.id)
                if test_result:
                    page_results.append({
                        'page': page.__dict__ if hasattr(page, '__dict__') else page,
                        'test_result': test_result
                    })
            
            website_data.append({
                'website': website.__dict__ if hasattr(website, '__dict__') else website,
                'pages': page_results
            })
        
        # Prepare report data
        report_data = self._prepare_project_report_data(project, website_data)
        
        # Generate report
        formatter = self.formatters.get(format)
        if not formatter:
            raise ValueError(f"Unsupported format: {format}")
        
        # Create filename with project name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create a safe filename from the project name
        project_name = self._sanitize_filename(project.name)
        filename = f"project_{project_name}_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content
        content = formatter.format_project_report(report_data)
        
        # Save report
        if format == 'pdf':
            # PDF returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        elif format in ['xlsx', 'excel']:
            # Excel returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated {format} report: {filepath}")
        return str(filepath)
    
    def _prepare_page_report_data(
        self,
        page: Page,
        website: Website,
        project: Project,
        test_result: TestResult,
        include_ai: bool
    ) -> Dict[str, Any]:
        """Prepare data for page report"""
        
        # Calculate statistics
        stats = self._calculate_page_stats(test_result, include_ai)
        
        return {
            'page': page.__dict__,
            'website': website.__dict__,
            'project': project.__dict__,
            'test_result': test_result.__dict__,
            'violations': [v.to_dict() for v in test_result.violations],
            'warnings': [w.to_dict() for w in test_result.warnings],
            'info': [i.to_dict() for i in test_result.info],
            'discovery': [d.to_dict() for d in test_result.discovery],
            'passes': test_result.passes,
            'ai_findings': [f.to_dict() for f in test_result.ai_findings] if include_ai else [],
            'statistics': stats,
            'generated_at': datetime.now().isoformat(),
            'wcag_levels': self._group_by_wcag_level(test_result.violations)
        }
    
    def _prepare_website_report_data(
        self,
        website: Website,
        project: Project,
        page_results: List[Dict],
        include_ai: bool
    ) -> Dict[str, Any]:
        """Prepare data for website report"""
        
        # Calculate aggregate statistics
        total_violations = sum(pr['test_result'].violation_count for pr in page_results)
        total_warnings = sum(pr['test_result'].warning_count for pr in page_results)
        total_passes = sum(pr['test_result'].pass_count for pr in page_results)
        
        # Group violations by type
        violation_types = {}
        for pr in page_results:
            for v in pr['test_result'].violations:
                vtype = v.id if hasattr(v, 'id') else 'unknown'
                if vtype not in violation_types:
                    violation_types[vtype] = {
                        'count': 0,
                        'pages': [],
                        'description': v.description if hasattr(v, 'description') else '',
                        'wcag': v.wcag_criteria if hasattr(v, 'wcag_criteria') else []
                    }
                violation_types[vtype]['count'] += 1
                violation_types[vtype]['pages'].append(pr['page'].get('url', 'Unknown') if isinstance(pr['page'], dict) else pr['page'].url)
        
        # Sort pages by violation count
        page_results.sort(
            key=lambda x: x['test_result'].violation_count,
            reverse=True
        )
        
        return {
            'website': website.__dict__,
            'project': project.__dict__,
            'pages': page_results,
            'statistics': {
                'total_pages': len(page_results),
                'total_violations': total_violations,
                'total_warnings': total_warnings,
                'total_passes': total_passes,
                'average_violations': total_violations / len(page_results) if page_results else 0
            },
            'violation_types': violation_types,
            'generated_at': datetime.now().isoformat()
        }
    
    def _prepare_project_report_data(
        self,
        project: Project,
        website_data: List[Dict]
    ) -> Dict[str, Any]:
        """Prepare data for project report"""
        
        # Calculate aggregate statistics for all categories
        total_websites = len(website_data)
        total_pages = sum(len(wd['pages']) for wd in website_data)
        total_violations = 0
        total_warnings = 0
        total_info = 0
        total_discovery = 0
        total_passes = 0
        
        for wd in website_data:
            for pr in wd['pages']:
                test_result = pr['test_result']
                if hasattr(test_result, 'violation_count'):
                    total_violations += test_result.violation_count
                    total_warnings += test_result.warning_count
                    total_info += test_result.info_count
                    total_discovery += test_result.discovery_count
                    total_passes += test_result.pass_count
        
        return {
            'project': project.__dict__,
            'websites': website_data,
            'statistics': {
                'total_websites': total_websites,
                'total_pages': total_pages,
                'total_violations': total_violations,
                'total_warnings': total_warnings,
                'total_info': total_info,
                'total_discovery': total_discovery,
                'total_passes': total_passes,
                'average_violations_per_page': total_violations / total_pages if total_pages else 0,
                'average_warnings_per_page': total_warnings / total_pages if total_pages else 0
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_page_stats(
        self,
        test_result: TestResult,
        include_ai: bool
    ) -> Dict[str, Any]:
        """Calculate statistics for a page"""
        
        stats = {
            'total_issues': test_result.violation_count + test_result.warning_count,
            'violations': test_result.violation_count,
            'warnings': test_result.warning_count,
            'passes': test_result.pass_count,
            'duration_ms': test_result.duration_ms
        }
        
        if include_ai and test_result.ai_findings:
            ai_critical = sum(1 for f in test_result.ai_findings 
                            if f.severity == ImpactLevel.CRITICAL)
            ai_serious = sum(1 for f in test_result.ai_findings
                           if f.severity == ImpactLevel.SERIOUS)
            
            stats['ai_findings'] = {
                'total': len(test_result.ai_findings),
                'critical': ai_critical,
                'serious': ai_serious
            }
        
        return stats
    
    def _group_by_wcag_level(self, violations: List[Dict]) -> Dict[str, List]:
        """Group violations by WCAG level"""
        
        levels = {'A': [], 'AA': [], 'AAA': []}
        
        for violation in violations:
            wcag_criteria = violation.get('wcag_criteria', [])
            for criterion in wcag_criteria:
                if 'Level A' in criterion:
                    levels['A'].append(violation)
                elif 'Level AA' in criterion:
                    levels['AA'].append(violation)
                elif 'Level AAA' in criterion:
                    levels['AAA'].append(violation)
        
        return levels
    
    def generate_summary_report(
        self,
        project_id: Optional[str] = None,
        format: str = 'html'
    ) -> str:
        """
        Generate executive summary report
        
        Args:
            project_id: Optional project filter
            format: Output format
            
        Returns:
            Path to generated report
        """
        # Get all projects or specific project
        if project_id:
            projects = [self.db.get_project(project_id)]
        else:
            projects = self.db.get_all_projects()
        
        summary_data = {
            'projects': [],
            'total_violations': 0,
            'total_pages_tested': 0,
            'most_common_issues': {},
            'generated_at': datetime.now().isoformat()
        }
        
        for project in projects:
            if not project:
                continue
                
            websites = self.db.get_websites(project.id)
            project_stats = {
                'name': project.name,
                'websites': len(websites),
                'pages_tested': 0,
                'violations': 0
            }
            
            for website in websites:
                pages = self.db.get_pages(website.id)
                for page in pages:
                    if page.last_tested:
                        project_stats['pages_tested'] += 1
                        project_stats['violations'] += page.violation_count
                        summary_data['total_violations'] += page.violation_count
                        summary_data['total_pages_tested'] += 1
            
            summary_data['projects'].append(project_stats)
        
        # Generate report
        formatter = self.formatters.get(format)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"summary_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        content = formatter.format_summary_report(summary_data)
        
        if format == 'pdf':
            formatter.save_pdf(content, filepath)
        elif format in ['xlsx', 'excel']:
            # Excel returns bytes, write in binary mode
            with open(filepath, 'wb') as f:
                f.write(content)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated summary report: {filepath}")
        return str(filepath)