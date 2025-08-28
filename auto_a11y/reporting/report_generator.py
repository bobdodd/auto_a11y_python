"""
Main report generator for accessibility test results
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from auto_a11y.models import TestResult, Page, Website, Project, ImpactLevel
from auto_a11y.core.database import Database
from auto_a11y.reporting.formatters import (
    HTMLFormatter,
    JSONFormatter, 
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
            'csv': CSVFormatter(config),
            'pdf': PDFFormatter(config)
        }
    
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
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"page_{page_id}_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content
        content = formatter.format_page_report(report_data)
        
        # Save report
        if format == 'pdf':
            formatter.save_pdf(content, filepath)
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
                    'page': page,
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
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"website_{website_id}_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content
        content = formatter.format_website_report(report_data)
        
        # Save report
        if format == 'pdf':
            formatter.save_pdf(content, filepath)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated {format} report: {filepath}")
        return str(filepath)
    
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
                        'page': page,
                        'test_result': test_result
                    })
            
            website_data.append({
                'website': website,
                'pages': page_results
            })
        
        # Prepare report data
        report_data = self._prepare_project_report_data(project, website_data)
        
        # Generate report
        formatter = self.formatters.get(format)
        if not formatter:
            raise ValueError(f"Unsupported format: {format}")
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"project_{project_id}_{timestamp}.{formatter.extension}"
        filepath = self.report_dir / filename
        
        # Generate content
        content = formatter.format_project_report(report_data)
        
        # Save report
        if format == 'pdf':
            formatter.save_pdf(content, filepath)
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
            'violations': test_result.violations,
            'warnings': test_result.warnings,
            'passes': test_result.passes,
            'ai_findings': test_result.ai_findings if include_ai else [],
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
                vtype = v.get('rule_id', 'unknown')
                if vtype not in violation_types:
                    violation_types[vtype] = {
                        'count': 0,
                        'pages': [],
                        'description': v.get('description', ''),
                        'wcag': v.get('wcag_criteria', [])
                    }
                violation_types[vtype]['count'] += 1
                violation_types[vtype]['pages'].append(pr['page'].url)
        
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
        
        # Calculate aggregate statistics
        total_websites = len(website_data)
        total_pages = sum(len(wd['pages']) for wd in website_data)
        total_violations = sum(
            pr['test_result'].violation_count 
            for wd in website_data 
            for pr in wd['pages']
        )
        
        return {
            'project': project.__dict__,
            'websites': website_data,
            'statistics': {
                'total_websites': total_websites,
                'total_pages': total_pages,
                'total_violations': total_violations,
                'average_violations_per_page': total_violations / total_pages if total_pages else 0
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
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Generated summary report: {filepath}")
        return str(filepath)