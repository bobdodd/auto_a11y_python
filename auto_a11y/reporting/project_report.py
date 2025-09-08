"""
Project-level Accessibility Report Generator
Aggregates data from multiple websites in a project
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from auto_a11y.models import Project, Website, Page, PageStatus

logger = logging.getLogger(__name__)


class ProjectReport:
    """Generates project-level accessibility reports"""
    
    def __init__(self, database, project: Project, websites: List[Website], pages_by_website: Dict[str, List[Page]]):
        """
        Initialize project report
        
        Args:
            database: Database instance
            project: Project object
            websites: List of websites in the project
            pages_by_website: Dictionary mapping website_id to list of pages
        """
        self.database = database
        self.project = project
        self.websites = websites
        self.pages_by_website = pages_by_website
        self.report_data = None
    
    def generate(self) -> Dict[str, Any]:
        """
        Generate the project-level report
        
        Returns:
            Report data dictionary
        """
        logger.info(f"Generating project-level report for {self.project.name}")
        
        # Calculate aggregate statistics
        total_pages = 0
        tested_pages = 0
        pages_with_issues = 0
        total_violations = 0
        total_warnings = 0
        
        website_summaries = []
        
        for website in self.websites:
            pages = self.pages_by_website.get(website.id, [])
            
            website_tested = sum(1 for p in pages if p.status == PageStatus.TESTED)
            website_issues = sum(1 for p in pages if p.has_issues)
            website_violations = sum(p.violation_count for p in pages)
            website_warnings = sum(p.warning_count for p in pages)
            
            website_summaries.append({
                'id': website.id,
                'name': website.name,
                'url': website.url,
                'total_pages': len(pages),
                'tested_pages': website_tested,
                'pages_with_issues': website_issues,
                'total_violations': website_violations,
                'total_warnings': website_warnings,
                'test_coverage': (website_tested / len(pages) * 100) if pages else 0
            })
            
            total_pages += len(pages)
            tested_pages += website_tested
            pages_with_issues += website_issues
            total_violations += website_violations
            total_warnings += website_warnings
        
        # Generate report data
        self.report_data = {
            'report_type': 'project_accessibility',
            'project': {
                'id': self.project.id,
                'name': self.project.name,
                'description': self.project.description,
                'status': self.project.status.value,
                'config': self.project.config
            },
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'website_count': len(self.websites),
                'total_pages': total_pages,
                'tested_pages': tested_pages,
                'pages_with_issues': pages_with_issues,
                'total_violations': total_violations,
                'total_warnings': total_warnings,
                'test_coverage': (tested_pages / total_pages * 100) if total_pages else 0
            },
            'websites': website_summaries,
            'wcag_level': self.project.config.get('wcag_level', 'AA')
        }
        
        logger.info(f"Project report generated with {len(self.websites)} websites and {total_pages} pages")
        return self.report_data
    
    def to_html(self) -> str:
        """
        Generate HTML report
        
        Returns:
            HTML string
        """
        if not self.report_data:
            self.generate()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Accessibility Report - {self.project.name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .website-card {{
            margin-bottom: 20px;
            border-left: 4px solid #007bff;
        }}
        .website-card:hover {{
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stat-card {{
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
            margin-bottom: 10px;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9rem;
        }}
        .progress-bar-animated {{
            animation: progress-bar-stripes 1s linear infinite;
        }}
        .severity-high {{
            color: #dc3545;
        }}
        .severity-medium {{
            color: #ffc107;
        }}
        .severity-low {{
            color: #28a745;
        }}
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <h1>Project Accessibility Report</h1>
                <div class="mb-3">
                    <h3>{self.project.name}</h3>
                    <p class="text-muted">
                        {self.project.description or 'No description'}<br>
                        <strong>WCAG Level:</strong> {self.report_data['wcag_level']}<br>
                        <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Overall Summary -->
        <div class="row mb-4">
            <div class="col-12">
                <h4>Overall Summary</h4>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-value">{self.report_data['summary']['website_count']}</div>
                    <div class="stat-label">Websites</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-value">{self.report_data['summary']['total_pages']}</div>
                    <div class="stat-label">Total Pages</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-value">{self.report_data['summary']['tested_pages']}</div>
                    <div class="stat-label">Tested Pages</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-value text-danger">{self.report_data['summary']['total_violations']}</div>
                    <div class="stat-label">Violations</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-value text-warning">{self.report_data['summary']['total_warnings']}</div>
                    <div class="stat-label">Warnings</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="stat-card">
                    <div class="stat-value">{self.report_data['summary']['test_coverage']:.1f}%</div>
                    <div class="stat-label">Coverage</div>
                </div>
            </div>
        </div>
        
        <!-- Test Coverage Progress -->
        <div class="row mb-4">
            <div class="col-12">
                <h5>Overall Test Coverage</h5>
                <div class="progress" style="height: 30px;">
                    <div class="progress-bar {'bg-success' if self.report_data['summary']['test_coverage'] >= 80 else 'bg-warning' if self.report_data['summary']['test_coverage'] >= 50 else 'bg-danger'}" 
                         role="progressbar" 
                         style="width: {self.report_data['summary']['test_coverage']}%"
                         aria-valuenow="{self.report_data['summary']['test_coverage']}"
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        {self.report_data['summary']['test_coverage']:.1f}%
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Website Breakdowns -->
        <div class="row">
            <div class="col-12">
                <h4>Website Breakdown</h4>
            </div>
        </div>
        
        <div class="row">
"""
        
        # Add website cards
        for website in self.report_data['websites']:
            coverage_color = 'success' if website['test_coverage'] >= 80 else 'warning' if website['test_coverage'] >= 50 else 'danger'
            
            html += f"""
            <div class="col-md-6 col-lg-4">
                <div class="card website-card">
                    <div class="card-body">
                        <h5 class="card-title">
                            {website['name']}
                            <a href="{website['url']}" target="_blank" class="float-end">
                                <i class="bi bi-box-arrow-up-right"></i>
                            </a>
                        </h5>
                        <p class="card-text text-muted small">{website['url']}</p>
                        
                        <div class="mb-3">
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar bg-{coverage_color}" 
                                     role="progressbar" 
                                     style="width: {website['test_coverage']}%">
                                    {website['test_coverage']:.0f}% tested
                                </div>
                            </div>
                        </div>
                        
                        <div class="row text-center">
                            <div class="col-4">
                                <div class="fw-bold">{website['total_pages']}</div>
                                <small class="text-muted">Pages</small>
                            </div>
                            <div class="col-4">
                                <div class="fw-bold text-danger">{website['total_violations']}</div>
                                <small class="text-muted">Violations</small>
                            </div>
                            <div class="col-4">
                                <div class="fw-bold text-warning">{website['total_warnings']}</div>
                                <small class="text-muted">Warnings</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
"""
        
        html += """
        </div>
        
        <!-- Issues Summary -->
        <div class="row mt-4">
            <div class="col-12">
                <h4>Issues Overview</h4>
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> 
                    This report aggregates accessibility testing results across all websites in the project.
                    For detailed issue information, please view individual website reports.
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def to_json(self) -> str:
        """
        Generate JSON report
        
        Returns:
            JSON string
        """
        if not self.report_data:
            self.generate()
        
        return json.dumps(self.report_data, indent=2, default=str)
    
    def save(self, format: str = 'html') -> str:
        """
        Save report to file
        
        Args:
            format: Output format (html, json)
            
        Returns:
            Path to saved file
        """
        # Get reports directory
        reports_dir = None
        
        # Try getting from Flask current_app if available
        try:
            from flask import current_app
            if current_app and hasattr(current_app, 'app_config'):
                reports_dir = Path(current_app.app_config.REPORTS_DIR)
        except:
            pass
        
        # Fall back to environment variable or default
        if not reports_dir:
            import os
            reports_dir_str = os.environ.get('REPORTS_DIR', '/Users/bob3/Desktop/auto_a11y_python/reports')
            reports_dir = Path(reports_dir_str)
        
        # Ensure directory exists
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"project_report_{self.project.id}_{timestamp}.{format}"
        filepath = reports_dir / filename
        
        # Generate content based on format
        if format == 'html':
            content = self.to_html()
        elif format == 'json':
            content = self.to_json()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Project report saved to {filepath}")
        return str(filepath)