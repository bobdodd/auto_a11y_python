"""
Report formatters for different output formats
"""

import json
import csv
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging
from io import StringIO

logger = logging.getLogger(__name__)


class BaseFormatter:
    """Base class for report formatters"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize formatter with config"""
        self.config = config
        self.extension = 'txt'
    
    def format_page_report(self, data: Dict[str, Any]) -> str:
        """Format page report data"""
        raise NotImplementedError
    
    def format_website_report(self, data: Dict[str, Any]) -> str:
        """Format website report data"""
        raise NotImplementedError
    
    def format_project_report(self, data: Dict[str, Any]) -> str:
        """Format project report data"""
        raise NotImplementedError
    
    def format_summary_report(self, data: Dict[str, Any]) -> str:
        """Format summary report data"""
        raise NotImplementedError


class HTMLFormatter(BaseFormatter):
    """HTML report formatter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.extension = 'html'
    
    def format_all_projects_report(self, data: Dict[str, Any]) -> str:
        """Format report for all projects as HTML"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('title', 'All Projects Accessibility Report')}</title>
    {self._get_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>{data.get('title', 'All Projects Accessibility Report')}</h1>
            <div class="metadata">
                <p><strong>Total Projects:</strong> {data['summary']['total_projects']}</p>
                <p><strong>Generated:</strong> {data['generated_at']}</p>
            </div>
        </header>
        
        <section class="summary">
            <h2>Overall Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{data['summary']['total_projects']}</h3>
                    <p>Projects</p>
                </div>
                <div class="stat-card">
                    <h3>{data['summary']['total_websites']}</h3>
                    <p>Websites</p>
                </div>
                <div class="stat-card">
                    <h3>{data['summary']['total_pages']}</h3>
                    <p>Total Pages</p>
                </div>
                <div class="stat-card">
                    <h3>{data['summary']['total_tested']}</h3>
                    <p>Pages Tested</p>
                </div>
                <div class="stat-card violation">
                    <h3>{data['summary']['total_violations']}</h3>
                    <p>Total Violations</p>
                </div>
                <div class="stat-card warning">
                    <h3>{data['summary']['total_warnings']}</h3>
                    <p>Total Warnings</p>
                </div>
            </div>
        </section>
        
        <section class="projects">
            <h2>Projects Breakdown</h2>
            {"".join(self._format_project_section(p) for p in data['projects'])}
        </section>
        
        {self._get_footer()}
    </div>
</body>
</html>"""
        
        return html
    
    def _format_project_section(self, project_data: Dict[str, Any]) -> str:
        """Format a single project section for all projects report"""
        project = project_data['project']
        stats = project_data['stats']
        
        websites_html = ""
        for website_data in project_data['websites']:
            website = website_data['website']
            websites_html += f"""
            <div class="website-item">
                <h4>{website.get('name', website.get('url', 'Unknown'))}</h4>
                <p>Pages: {website_data['pages']} | Tested: {website_data['tested']} | 
                   Violations: {website_data['violations']} | Warnings: {website_data['warnings']}</p>
            </div>
            """
        
        return f"""
        <div class="project-section">
            <h3>{project.get('name', 'Unnamed Project')}</h3>
            <p>{project.get('description', '')}</p>
            <div class="project-stats">
                <span>Websites: {stats['website_count']}</span>
                <span>Pages: {stats['total_pages']}</span>
                <span>Tested: {stats['tested_pages']}</span>
                <span>Coverage: {stats['test_coverage']:.1f}%</span>
            </div>
            <div class="websites-list">
                {websites_html if websites_html else '<p>No websites in this project</p>'}
            </div>
        </div>
        """
    
    def format_page_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report for a page"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - {data['page']['url']}</title>
    {self._get_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>Accessibility Report</h1>
            <div class="metadata">
                <p><strong>Page:</strong> <a href="{data['page']['url']}" target="_blank">{data['page']['url']}</a></p>
                <p><strong>Website:</strong> {data['website']['name']}</p>
                <p><strong>Project:</strong> {data['project']['name']}</p>
                <p><strong>Generated:</strong> {data['generated_at']}</p>
            </div>
        </header>
        
        {self._format_summary_section(data['statistics'])}
        
        {self._format_violations_section(data.get('violations', []))}
        
        {self._format_warnings_section(data.get('warnings', []))}
        
        {self._format_info_section(data.get('info', []))}
        
        {self._format_discovery_section(data.get('discovery', []))}
        
        {self._format_ai_findings_section(data.get('ai_findings', []))}
        
        {self._format_passes_section(data.get('passes', []))}
        
        <footer>
            <p>Generated by Auto A11y Python - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def format_website_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report for a website"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Accessibility Report - {data['website']['name']}</title>
    {self._get_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>Website Accessibility Report</h1>
            <div class="metadata">
                <p><strong>Website:</strong> {data['website']['name']} ({data['website'].get('url', data['website'].get('base_url', ''))})</p>
                <p><strong>Project:</strong> {data['project']['name']}</p>
                <p><strong>Pages Tested:</strong> {data['statistics']['total_pages']}</p>
                <p><strong>Generated:</strong> {data['generated_at']}</p>
            </div>
        </header>
        
        <section class="summary">
            <h2>Summary</h2>
            <div class="stats-grid">
                <div class="stat-card violations">
                    <h3>{data['statistics']['total_violations']}</h3>
                    <p>Total Violations</p>
                </div>
                <div class="stat-card warnings">
                    <h3>{data['statistics']['total_warnings']}</h3>
                    <p>Total Warnings</p>
                </div>
                <div class="stat-card passes">
                    <h3>{data['statistics']['total_passes']}</h3>
                    <p>Total Passes</p>
                </div>
                <div class="stat-card average">
                    <h3>{data['statistics']['average_violations']:.1f}</h3>
                    <p>Avg Violations/Page</p>
                </div>
            </div>
        </section>
        
        {self._format_violation_types_section(data['violation_types'])}
        
        {self._format_pages_table(data['pages'])}
        
        <footer>
            <p>Generated by Auto A11y Python - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def format_project_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report for a project"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Accessibility Report - {data['project']['name']}</title>
    {self._get_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>Project Accessibility Report</h1>
            <div class="metadata">
                <p><strong>Project:</strong> {data['project']['name']}</p>
                <p><strong>Description:</strong> {data['project'].get('description', 'N/A')}</p>
                <p><strong>Generated:</strong> {data['generated_at']}</p>
            </div>
        </header>
        
        <section class="summary">
            <h2>Project Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{data['statistics']['total_websites']}</h3>
                    <p>Websites</p>
                </div>
                <div class="stat-card">
                    <h3>{data['statistics']['total_pages']}</h3>
                    <p>Pages Tested</p>
                </div>
            </div>
            <h3>Test Results Summary</h3>
            <div class="stats-grid">
                <div class="stat-card violations">
                    <h3>{data['statistics'].get('total_violations', 0)}</h3>
                    <p>Errors</p>
                </div>
                <div class="stat-card warnings">
                    <h3>{data['statistics'].get('total_warnings', 0)}</h3>
                    <p>Warnings</p>
                </div>
                <div class="stat-card info">
                    <h3>{data['statistics'].get('total_info', 0)}</h3>
                    <p>Info Notes</p>
                </div>
                <div class="stat-card discovery">
                    <h3>{data['statistics'].get('total_discovery', 0)}</h3>
                    <p>Discovery</p>
                </div>
                <div class="stat-card passes">
                    <h3>{data['statistics'].get('total_passes', 0)}</h3>
                    <p>Passed</p>
                </div>
            </div>
        </section>
        
        {self._format_websites_section(data['websites'])}
        
        <footer>
            <p>Generated by Auto A11y Python - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def format_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        
        projects_html = ""
        for project in data['projects']:
            projects_html += f"""
            <tr>
                <td>{project['name']}</td>
                <td>{project['websites']}</td>
                <td>{project['pages_tested']}</td>
                <td class="violations">{project['violations']}</td>
            </tr>"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Executive Summary</title>
    {self._get_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>Accessibility Executive Summary</h1>
            <p class="generated">Generated: {data['generated_at']}</p>
        </header>
        
        <section class="overview">
            <h2>Overview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{len(data['projects'])}</h3>
                    <p>Projects</p>
                </div>
                <div class="stat-card">
                    <h3>{data['total_pages_tested']}</h3>
                    <p>Pages Tested</p>
                </div>
                <div class="stat-card violations">
                    <h3>{data['total_violations']}</h3>
                    <p>Total Violations</p>
                </div>
            </div>
        </section>
        
        <section class="projects">
            <h2>Projects</h2>
            <table>
                <thead>
                    <tr>
                        <th>Project</th>
                        <th>Websites</th>
                        <th>Pages Tested</th>
                        <th>Violations</th>
                    </tr>
                </thead>
                <tbody>
                    {projects_html}
                </tbody>
            </table>
        </section>
        
        <footer>
            <p>Generated by Auto A11y Python - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    def _get_footer(self) -> str:
        """Get footer for HTML reports"""
        return """
        <footer>
            <p>Generated by Auto A11y - Accessibility Testing Tool</p>
            <p>Report generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </footer>
        """
    
    def _get_css(self) -> str:
        """Get CSS styles for HTML reports"""
        return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        header {
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 { color: #007bff; margin-bottom: 10px; }
        h2 { color: #333; margin: 20px 0 15px; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px; }
        h3 { color: #555; margin: 15px 0 10px; }
        
        .metadata {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .metadata p { margin: 5px 0; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        .stat-card h3 {
            font-size: 2em;
            color: #007bff;
            margin: 0;
        }
        .stat-card.violations h3 { color: #dc3545; }
        .stat-card.warnings h3 { color: #ffc107; }
        .stat-card.passes h3 { color: #28a745; }
        
        .violation, .warning, .pass, .ai-finding {
            background: #fff;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .warning { border-left-color: #ffc107; }
        .pass { border-left-color: #28a745; }
        .ai-finding { border-left-color: #6f42c1; }
        
        .violation h4, .warning h4, .pass h4, .ai-finding h4 {
            margin-bottom: 10px;
            color: #333;
        }
        
        .impact {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }
        .impact.critical { background: #dc3545; color: white; }
        .impact.serious { background: #fd7e14; color: white; }
        .impact.moderate { background: #ffc107; color: #333; }
        .impact.minor { background: #6c757d; color: white; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        th {
            background: #f8f9fa;
            font-weight: bold;
            color: #495057;
        }
        tr:hover { background: #f8f9fa; }
        
        .code {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            margin: 10px 0;
        }
        
        footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
        }
        
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
        """
    
    def _format_summary_section(self, stats: Dict) -> str:
        """Format summary statistics section"""
        return f"""
        <section class="summary">
            <h2>Summary</h2>
            <div class="stats-grid">
                <div class="stat-card violations">
                    <h3>{stats['violations']}</h3>
                    <p>Violations</p>
                </div>
                <div class="stat-card warnings">
                    <h3>{stats['warnings']}</h3>
                    <p>Warnings</p>
                </div>
                <div class="stat-card passes">
                    <h3>{stats['passes']}</h3>
                    <p>Passes</p>
                </div>
                <div class="stat-card">
                    <h3>{stats['duration_ms']}ms</h3>
                    <p>Test Duration</p>
                </div>
            </div>
        </section>"""
    
    def _format_violations_section(self, violations: List[Dict]) -> str:
        """Format violations section"""
        if not violations:
            return ""
        
        html = "<section class='violations'><h2>Violations</h2>"
        for v in violations:
            impact_class = v.get('impact', 'moderate').lower()
            html += f"""
            <div class="violation">
                <h4>{v.get('rule_id', 'Unknown')}
                    <span class="impact {impact_class}">{v.get('impact', 'moderate').upper()}</span>
                </h4>
                <p><strong>Description:</strong> {v.get('description', 'No description')}</p>
                <p><strong>WCAG:</strong> {', '.join(v.get('wcag_criteria', []))}</p>
                <p><strong>Elements:</strong> {v.get('node_count', 0)} affected</p>
                {self._format_fix(v.get('suggested_fix'))}
            </div>"""
        html += "</section>"
        return html
    
    def _format_warnings_section(self, warnings: List[Dict]) -> str:
        """Format warnings section"""
        if not warnings:
            return ""
        
        html = "<section class='warnings'><h2>Warnings</h2>"
        for w in warnings:
            html += f"""
            <div class="warning">
                <h4>{w.get('rule_id', 'Unknown')}</h4>
                <p>{w.get('description', 'No description')}</p>
            </div>"""
        html += "</section>"
        return html
    
    def _format_info_section(self, info_items: List[Dict]) -> str:
        """Format info section"""
        if not info_items:
            return ""
        
        html = "<section class='info'><h2>Information Notes</h2>"
        for item in info_items:
            html += f"""
            <div class="info-item">
                <h4>{item.get('id', 'Unknown')}</h4>
                <p><strong>Description:</strong> {item.get('description', 'No description')}</p>
                <p><strong>Category:</strong> {item.get('category', 'General')}</p>
                {f"<p><strong>WCAG:</strong> {', '.join(item.get('wcag_criteria', []))}</p>" if item.get('wcag_criteria') else ""}
            </div>"""
        html += "</section>"
        return html
    
    def _format_discovery_section(self, discovery_items: List[Dict]) -> str:
        """Format discovery section"""
        if not discovery_items:
            return ""
        
        html = "<section class='discovery'><h2>Discovery Items</h2>"
        html += "<p><em>These items require manual inspection to ensure accessibility.</em></p>"
        for item in discovery_items:
            html += f"""
            <div class="discovery-item">
                <h4>{item.get('id', 'Unknown')}</h4>
                <p><strong>Description:</strong> {item.get('description', 'No description')}</p>
                <p><strong>Category:</strong> {item.get('category', 'General')}</p>
                {f"<p><strong>Location:</strong> <code>{item.get('xpath', 'Not specified')}</code></p>" if item.get('xpath') else ""}
            </div>"""
        html += "</section>"
        return html
    
    def _format_ai_findings_section(self, findings: List) -> str:
        """Format AI findings section"""
        if not findings:
            return ""
        
        html = "<section class='ai-findings'><h2>AI Analysis Findings</h2>"
        for f in findings:
            severity_class = f.severity.value.lower() if hasattr(f, 'severity') else 'moderate'
            html += f"""
            <div class="ai-finding">
                <h4>{f.type if hasattr(f, 'type') else 'AI Finding'}
                    <span class="impact {severity_class}">{f.severity.value.upper() if hasattr(f, 'severity') else 'MODERATE'}</span>
                </h4>
                <p><strong>Description:</strong> {f.description if hasattr(f, 'description') else 'No description'}</p>
                <p><strong>Confidence:</strong> {f.confidence * 100 if hasattr(f, 'confidence') else 85:.0f}%</p>
                {self._format_fix(f.suggested_fix if hasattr(f, 'suggested_fix') else None)}
            </div>"""
        html += "</section>"
        return html
    
    def _format_passes_section(self, passes: List[Dict]) -> str:
        """Format passes section"""
        if not passes:
            return ""
        
        html = "<section class='passes'><h2>Passes</h2><ul>"
        for p in passes[:10]:  # Show first 10 passes
            html += f"<li>{p.get('rule_id', 'Unknown')}: {p.get('description', 'Passed')}</li>"
        if len(passes) > 10:
            html += f"<li>... and {len(passes) - 10} more</li>"
        html += "</ul></section>"
        return html
    
    def _format_fix(self, fix: str) -> str:
        """Format suggested fix"""
        if not fix:
            return ""
        return f'<p><strong>Suggested Fix:</strong> {fix}</p>'
    
    def _format_violation_types_section(self, violation_types: Dict) -> str:
        """Format violation types section"""
        html = "<section class='violation-types'><h2>Violation Types</h2><table>"
        html += "<thead><tr><th>Rule</th><th>Count</th><th>Description</th><th>Pages Affected</th></tr></thead><tbody>"
        
        sorted_types = sorted(violation_types.items(), key=lambda x: x[1]['count'], reverse=True)
        for rule_id, info in sorted_types[:20]:  # Show top 20
            pages_summary = f"{len(set(info['pages']))} pages"
            html += f"""
            <tr>
                <td>{rule_id}</td>
                <td>{info['count']}</td>
                <td>{info['description']}</td>
                <td>{pages_summary}</td>
            </tr>"""
        
        html += "</tbody></table></section>"
        return html
    
    def _format_pages_table(self, page_results: List[Dict]) -> str:
        """Format pages table"""
        html = "<section class='pages'><h2>Pages</h2><table>"
        html += "<thead><tr><th>Page</th><th>Violations</th><th>Warnings</th><th>Last Tested</th></tr></thead><tbody>"
        
        for pr in page_results:
            page = pr['page']
            test = pr['test_result']
            html += f"""
            <tr>
                <td><a href="{page.url}" target="_blank">{page.url}</a></td>
                <td class="violations">{test.violation_count}</td>
                <td class="warnings">{test.warning_count}</td>
                <td>{test.test_date}</td>
            </tr>"""
        
        html += "</tbody></table></section>"
        return html
    
    def _format_websites_section(self, websites: List[Dict]) -> str:
        """Format websites section with detailed test results"""
        html = "<section class='websites'><h2>Websites</h2>"
        
        for wd in websites:
            website = wd['website']
            pages = wd['pages']
            
            # Calculate totals for all categories
            total_violations = 0
            total_warnings = 0
            total_info = 0
            total_discovery = 0
            total_passes = 0
            
            all_violations = []
            all_warnings = []
            all_info = []
            all_discovery = []
            
            for p in pages:
                test_result = p['test_result']
                if hasattr(test_result, 'violation_count'):
                    total_violations += test_result.violation_count
                    total_warnings += test_result.warning_count
                    total_info += test_result.info_count
                    total_discovery += test_result.discovery_count
                    total_passes += test_result.pass_count
                    
                    # Collect all issues for detailed display
                    for v in test_result.violations:
                        all_violations.append({'page': p['page'].url, 'issue': v})
                    for w in test_result.warnings:
                        all_warnings.append({'page': p['page'].url, 'issue': w})
                    for i in test_result.info:
                        all_info.append({'page': p['page'].url, 'issue': i})
                    for d in test_result.discovery:
                        all_discovery.append({'page': p['page'].url, 'issue': d})
            
            # Website header with all statistics
            html += f"""
            <div class="website">
                <h3>{website.name}</h3>
                <p><a href="{website.url}" target="_blank">{website.url}</a></p>
                <div class="stats-grid" style="margin: 20px 0;">
                    <div class="stat-card violations">
                        <h4>{total_violations}</h4>
                        <p>Errors</p>
                    </div>
                    <div class="stat-card warnings">
                        <h4>{total_warnings}</h4>
                        <p>Warnings</p>
                    </div>
                    <div class="stat-card info">
                        <h4>{total_info}</h4>
                        <p>Info</p>
                    </div>
                    <div class="stat-card discovery">
                        <h4>{total_discovery}</h4>
                        <p>Discovery</p>
                    </div>
                    <div class="stat-card passes">
                        <h4>{total_passes}</h4>
                        <p>Passed</p>
                    </div>
                </div>
                
                <p><strong>Pages Tested:</strong> {len(pages)}</p>
                """
            
            # Add detailed issues if they exist
            if all_violations:
                html += "<h4>Errors (Violations)</h4><ul>"
                for item in all_violations[:10]:  # Show first 10
                    issue = item['issue']
                    html += f"<li><strong>{issue.id if hasattr(issue, 'id') else 'Unknown'}:</strong> {issue.description if hasattr(issue, 'description') else 'No description'} - <em>{item['page']}</em></li>"
                if len(all_violations) > 10:
                    html += f"<li><em>... and {len(all_violations) - 10} more errors</em></li>"
                html += "</ul>"
            
            if all_warnings:
                html += "<h4>Warnings</h4><ul>"
                for item in all_warnings[:10]:  # Show first 10
                    issue = item['issue']
                    html += f"<li><strong>{issue.id if hasattr(issue, 'id') else 'Unknown'}:</strong> {issue.description if hasattr(issue, 'description') else 'No description'} - <em>{item['page']}</em></li>"
                if len(all_warnings) > 10:
                    html += f"<li><em>... and {len(all_warnings) - 10} more warnings</em></li>"
                html += "</ul>"
            
            if all_info:
                html += "<h4>Information Notes</h4><ul>"
                for item in all_info[:5]:  # Show first 5
                    issue = item['issue']
                    html += f"<li><strong>{issue.id if hasattr(issue, 'id') else 'Unknown'}:</strong> {issue.description if hasattr(issue, 'description') else 'No description'} - <em>{item['page']}</em></li>"
                if len(all_info) > 5:
                    html += f"<li><em>... and {len(all_info) - 5} more info notes</em></li>"
                html += "</ul>"
            
            if all_discovery:
                html += "<h4>Discovery Items</h4><ul>"
                for item in all_discovery[:5]:  # Show first 5
                    issue = item['issue']
                    html += f"<li><strong>{issue.id if hasattr(issue, 'id') else 'Unknown'}:</strong> {issue.description if hasattr(issue, 'description') else 'No description'} - <em>{item['page']}</em></li>"
                if len(all_discovery) > 5:
                    html += f"<li><em>... and {len(all_discovery) - 5} more discovery items</em></li>"
                html += "</ul>"
            
            html += "</div>"
        
        html += "</section>"
        return html


class JSONFormatter(BaseFormatter):
    """JSON report formatter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.extension = 'json'
    
    def format_page_report(self, data: Dict[str, Any]) -> str:
        """Generate JSON report for a page"""
        return json.dumps(data, indent=2, default=str)
    
    def format_website_report(self, data: Dict[str, Any]) -> str:
        """Generate JSON report for a website"""
        return json.dumps(data, indent=2, default=str)
    
    def format_project_report(self, data: Dict[str, Any]) -> str:
        """Generate JSON report for a project"""
        return json.dumps(data, indent=2, default=str)
    
    def format_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate JSON summary report"""
        return json.dumps(data, indent=2, default=str)


class CSVFormatter(BaseFormatter):
    """CSV report formatter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.extension = 'csv'
    
    def format_page_report(self, data: Dict[str, Any]) -> str:
        """Generate CSV report for a page"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Type', 'Rule ID', 'Description', 'Impact', 'WCAG', 'Elements', 'Fix'])
        
        # Write violations
        for v in data['violations']:
            writer.writerow([
                'Violation',
                v.get('rule_id', ''),
                v.get('description', ''),
                v.get('impact', ''),
                ', '.join(v.get('wcag_criteria', [])),
                v.get('node_count', 0),
                v.get('suggested_fix', '')
            ])
        
        # Write warnings
        for w in data['warnings']:
            writer.writerow([
                'Warning',
                w.get('rule_id', ''),
                w.get('description', ''),
                '',
                '',
                w.get('node_count', 0),
                ''
            ])
        
        return output.getvalue()
    
    def format_website_report(self, data: Dict[str, Any]) -> str:
        """Generate CSV report for a website"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Page URL', 'Violations', 'Warnings', 'Passes', 'Last Tested'])
        
        # Write page data
        for pr in data['pages']:
            page = pr['page']
            test = pr['test_result']
            writer.writerow([
                page.url,
                test.violation_count,
                test.warning_count,
                test.pass_count,
                test.test_date
            ])
        
        return output.getvalue()
    
    def format_project_report(self, data: Dict[str, Any]) -> str:
        """Generate CSV report for a project"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Website', 'URL', 'Pages', 'Total Violations', 'Total Warnings'])
        
        # Write website data
        for wd in data['websites']:
            website = wd['website']
            pages = wd['pages']
            
            total_violations = sum(p['test_result'].violation_count for p in pages)
            total_warnings = sum(p['test_result'].warning_count for p in pages)
            
            writer.writerow([
                website.name,
                website.url,
                len(pages),
                total_violations,
                total_warnings
            ])
        
        return output.getvalue()
    
    def format_summary_report(self, data: Dict[str, Any]) -> str:
        """Generate CSV summary report"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Project', 'Websites', 'Pages Tested', 'Violations'])
        
        # Write project data
        for project in data['projects']:
            writer.writerow([
                project['name'],
                project['websites'],
                project['pages_tested'],
                project['violations']
            ])
        
        return output.getvalue()


class ExcelFormatter(BaseFormatter):
    """Excel report formatter"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.extension = 'xlsx'
        # Import openpyxl here to avoid import errors if not needed
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
            self.Workbook = Workbook
            self.Font = Font
            self.Fill = Fill
            self.PatternFill = PatternFill
            self.Alignment = Alignment
            self.Border = Border
            self.Side = Side
            self.get_column_letter = get_column_letter
            self.has_openpyxl = True
        except ImportError:
            logger.warning("openpyxl not installed - Excel export will return JSON")
            self.has_openpyxl = False
    
    def _get_styles(self):
        """Get common Excel styles"""
        if not self.has_openpyxl:
            return {}
        
        return {
            'header': {
                'font': self.Font(bold=True, color="FFFFFF", size=12),
                'fill': self.PatternFill(start_color="007BFF", end_color="007BFF", fill_type="solid"),
                'alignment': self.Alignment(horizontal="center", vertical="center"),
                'border': self.Border(
                    left=self.Side(style='thin'),
                    right=self.Side(style='thin'),
                    top=self.Side(style='thin'),
                    bottom=self.Side(style='thin')
                )
            },
            'subheader': {
                'font': self.Font(bold=True, size=11),
                'fill': self.PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid"),
                'alignment': self.Alignment(horizontal="left", vertical="center")
            },
            'violation': {
                'fill': self.PatternFill(start_color="FFE5E5", end_color="FFE5E5", fill_type="solid")
            },
            'warning': {
                'fill': self.PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")
            },
            'info': {
                'fill': self.PatternFill(start_color="D1ECF1", end_color="D1ECF1", fill_type="solid")
            },
            'discovery': {
                'fill': self.PatternFill(start_color="E6E0FF", end_color="E6E0FF", fill_type="solid")
            },
            'pass': {
                'fill': self.PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
            },
            'critical': {
                'font': self.Font(color="DC3545", bold=True)
            },
            'serious': {
                'font': self.Font(color="FD7E14", bold=True)
            },
            'moderate': {
                'font': self.Font(color="FFC107")
            },
            'minor': {
                'font': self.Font(color="6C757D")
            }
        }
    
    def format_page_report(self, data: Dict[str, Any]) -> bytes:
        """Generate Excel report for a page"""
        if not self.has_openpyxl:
            return json.dumps(data, indent=2, default=str).encode('utf-8')
        
        wb = self.Workbook()
        styles = self._get_styles()
        
        # Summary Sheet
        ws_summary = wb.active
        ws_summary.title = "Summary"
        self._create_summary_sheet(ws_summary, data, styles)
        
        # Violations Sheet
        if data.get('violations'):
            ws_violations = wb.create_sheet("Violations")
            self._create_violations_sheet(ws_violations, data['violations'], styles)
        
        # Warnings Sheet
        if data.get('warnings'):
            ws_warnings = wb.create_sheet("Warnings")
            self._create_warnings_sheet(ws_warnings, data['warnings'], styles)
        
        # Info Sheet
        if data.get('info'):
            ws_info = wb.create_sheet("Info")
            self._create_info_sheet(ws_info, data['info'], styles)
        
        # Discovery Sheet
        if data.get('discovery'):
            ws_discovery = wb.create_sheet("Discovery")
            self._create_discovery_sheet(ws_discovery, data['discovery'], styles)
        
        # AI Findings Sheet
        if data.get('ai_findings'):
            ws_ai = wb.create_sheet("AI Findings")
            self._create_ai_findings_sheet(ws_ai, data['ai_findings'], styles)
        
        # Passes Sheet
        if data.get('passes'):
            ws_passes = wb.create_sheet("Passes")
            self._create_passes_sheet(ws_passes, data['passes'], styles)
        
        # Save to bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def format_website_report(self, data: Dict[str, Any]) -> bytes:
        """Generate Excel report for a website"""
        if not self.has_openpyxl:
            return json.dumps(data, indent=2, default=str).encode('utf-8')
        
        wb = self.Workbook()
        styles = self._get_styles()
        
        # Summary Sheet
        ws_summary = wb.active
        ws_summary.title = "Website Summary"
        self._create_website_summary_sheet(ws_summary, data, styles)
        
        # Pages Sheet
        if data.get('pages'):
            ws_pages = wb.create_sheet("Pages")
            self._create_pages_sheet(ws_pages, data['pages'], styles)
        
        # Violation Types Sheet
        if data.get('violation_types'):
            ws_types = wb.create_sheet("Violation Types")
            self._create_violation_types_sheet(ws_types, data['violation_types'], styles)
        
        # Save to bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def format_project_report(self, data: Dict[str, Any]) -> bytes:
        """Generate Excel report for a project"""
        if not self.has_openpyxl:
            return json.dumps(data, indent=2, default=str).encode('utf-8')
        
        wb = self.Workbook()
        styles = self._get_styles()
        
        # Project Summary Sheet
        ws_summary = wb.active
        ws_summary.title = "Project Summary"
        self._create_project_summary_sheet(ws_summary, data, styles)
        
        # Websites Sheet
        if data.get('websites'):
            ws_websites = wb.create_sheet("Websites")
            self._create_websites_sheet(ws_websites, data['websites'], styles)
        
        # Save to bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def format_all_projects_report(self, data: Dict[str, Any]) -> bytes:
        """Generate Excel report for all projects"""
        if not self.has_openpyxl:
            return json.dumps(data, indent=2, default=str).encode('utf-8')
        
        wb = self.Workbook()
        styles = self._get_styles()
        
        # Overall Summary Sheet
        ws_summary = wb.active
        ws_summary.title = "Overall Summary"
        self._create_all_projects_summary_sheet(ws_summary, data, styles)
        
        # Projects Breakdown Sheet
        if data.get('projects'):
            ws_projects = wb.create_sheet("Projects Breakdown")
            self._create_projects_breakdown_sheet(ws_projects, data['projects'], styles)
        
        # Save to bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def format_summary_report(self, data: Dict[str, Any]) -> bytes:
        """Generate Excel summary report"""
        if not self.has_openpyxl:
            return json.dumps(data, indent=2, default=str).encode('utf-8')
        
        wb = self.Workbook()
        styles = self._get_styles()
        
        # Executive Summary Sheet
        ws = wb.active
        ws.title = "Executive Summary"
        
        # Headers
        headers = ['Project', 'Websites', 'Pages Tested', 'Violations', 'Warnings']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        # Data
        row = 2
        for project in data.get('projects', []):
            ws.cell(row=row, column=1, value=project.get('name', ''))
            ws.cell(row=row, column=2, value=project.get('websites', 0))
            ws.cell(row=row, column=3, value=project.get('pages_tested', 0))
            
            violations_cell = ws.cell(row=row, column=4, value=project.get('violations', 0))
            if project.get('violations', 0) > 0:
                violations_cell.fill = styles['violation']['fill']
            
            warnings_cell = ws.cell(row=row, column=5, value=project.get('warnings', 0))
            if project.get('warnings', 0) > 0:
                warnings_cell.fill = styles['warning']['fill']
            
            row += 1
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
        
        # Save to bytes
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()
    
    def _create_summary_sheet(self, ws, data, styles):
        """Create page summary sheet"""
        # Title
        ws.merge_cells('A1:E1')
        title_cell = ws['A1']
        title_cell.value = f"Accessibility Report - {data.get('page', {}).get('url', 'Unknown')}"
        title_cell.font = self.Font(bold=True, size=14)
        title_cell.alignment = self.Alignment(horizontal="center")
        
        # Metadata
        row = 3
        ws.cell(row=row, column=1, value="Website:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=data.get('website', {}).get('name', ''))
        row += 1
        ws.cell(row=row, column=1, value="Project:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=data.get('project', {}).get('name', ''))
        row += 1
        ws.cell(row=row, column=1, value="Generated:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=data.get('generated_at', ''))
        
        # Statistics
        row = 7
        ws.cell(row=row, column=1, value="Summary Statistics").font = self.Font(bold=True, size=12)
        row += 1
        
        stats = data.get('statistics', {})
        ws.cell(row=row, column=1, value="Violations:")
        ws.cell(row=row, column=2, value=stats.get('violations', 0))
        if stats.get('violations', 0) > 0:
            ws.cell(row=row, column=2).fill = styles['violation']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Warnings:")
        ws.cell(row=row, column=2, value=stats.get('warnings', 0))
        if stats.get('warnings', 0) > 0:
            ws.cell(row=row, column=2).fill = styles['warning']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Passes:")
        ws.cell(row=row, column=2, value=stats.get('passes', 0))
        ws.cell(row=row, column=2).fill = styles['pass']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Test Duration (ms):")
        ws.cell(row=row, column=2, value=stats.get('duration_ms', 0))
        
        self._auto_adjust_columns(ws)
    
    def _create_violations_sheet(self, ws, violations, styles):
        """Create violations sheet"""
        headers = ['Rule ID', 'Description', 'Impact', 'WCAG Criteria', 'Elements Affected', 'Suggested Fix']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for v in violations:
            ws.cell(row=row, column=1, value=v.get('rule_id', ''))
            ws.cell(row=row, column=2, value=v.get('description', ''))
            
            impact = v.get('impact', 'moderate')
            impact_cell = ws.cell(row=row, column=3, value=impact.upper())
            if impact.lower() in styles:
                impact_cell.font = styles[impact.lower()]['font']
            
            ws.cell(row=row, column=4, value=', '.join(v.get('wcag_criteria', [])))
            ws.cell(row=row, column=5, value=v.get('node_count', 0))
            ws.cell(row=row, column=6, value=v.get('suggested_fix', ''))
            
            # Apply row coloring
            for col in range(1, 7):
                ws.cell(row=row, column=col).fill = styles['violation']['fill']
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_warnings_sheet(self, ws, warnings, styles):
        """Create warnings sheet"""
        headers = ['Rule ID', 'Description', 'Elements Affected']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for w in warnings:
            ws.cell(row=row, column=1, value=w.get('rule_id', ''))
            ws.cell(row=row, column=2, value=w.get('description', ''))
            ws.cell(row=row, column=3, value=w.get('node_count', 0))
            
            # Apply row coloring
            for col in range(1, 4):
                ws.cell(row=row, column=col).fill = styles['warning']['fill']
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_info_sheet(self, ws, info_items, styles):
        """Create info sheet"""
        headers = ['ID', 'Description', 'Category', 'WCAG Criteria', 'Location']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for item in info_items:
            ws.cell(row=row, column=1, value=item.get('id', ''))
            ws.cell(row=row, column=2, value=item.get('description', ''))
            ws.cell(row=row, column=3, value=item.get('category', ''))
            ws.cell(row=row, column=4, value=', '.join(item.get('wcag_criteria', [])))
            ws.cell(row=row, column=5, value=item.get('xpath', ''))
            
            # Apply info coloring (blue)
            for col in range(1, 6):
                ws.cell(row=row, column=col).fill = styles['info']['fill']
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_discovery_sheet(self, ws, discovery_items, styles):
        """Create discovery sheet"""
        headers = ['ID', 'Description', 'Category', 'Location', 'Manual Check Required']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for item in discovery_items:
            ws.cell(row=row, column=1, value=item.get('id', ''))
            ws.cell(row=row, column=2, value=item.get('description', ''))
            ws.cell(row=row, column=3, value=item.get('category', ''))
            ws.cell(row=row, column=4, value=item.get('xpath', ''))
            ws.cell(row=row, column=5, value='Yes')
            
            # Apply discovery coloring (purple)
            for col in range(1, 6):
                cell = ws.cell(row=row, column=col)
                if 'discovery' in styles:
                    cell.fill = styles['discovery']['fill']
                else:
                    # Use a purple-ish color if not defined
                    from openpyxl.styles import PatternFill
                    cell.fill = PatternFill(start_color="E6E0FF", end_color="E6E0FF", fill_type="solid")
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_ai_findings_sheet(self, ws, findings, styles):
        """Create AI findings sheet"""
        headers = ['Type', 'Description', 'Severity', 'Confidence', 'Suggested Fix']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for f in findings:
            ws.cell(row=row, column=1, value=getattr(f, 'type', 'AI Finding'))
            ws.cell(row=row, column=2, value=getattr(f, 'description', ''))
            
            severity = getattr(f, 'severity', None)
            if severity:
                severity_value = severity.value if hasattr(severity, 'value') else str(severity)
                severity_cell = ws.cell(row=row, column=3, value=severity_value.upper())
                if severity_value.lower() in styles:
                    severity_cell.font = styles[severity_value.lower()]['font']
            
            confidence = getattr(f, 'confidence', 0.85)
            ws.cell(row=row, column=4, value=f"{confidence * 100:.0f}%")
            ws.cell(row=row, column=5, value=getattr(f, 'suggested_fix', ''))
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_passes_sheet(self, ws, passes, styles):
        """Create passes sheet"""
        headers = ['Rule ID', 'Description']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for p in passes:
            ws.cell(row=row, column=1, value=p.get('rule_id', ''))
            ws.cell(row=row, column=2, value=p.get('description', 'Passed'))
            
            # Apply row coloring
            for col in range(1, 3):
                ws.cell(row=row, column=col).fill = styles['pass']['fill']
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_website_summary_sheet(self, ws, data, styles):
        """Create website summary sheet"""
        # Title
        ws.merge_cells('A1:D1')
        title_cell = ws['A1']
        title_cell.value = f"Website Report - {data.get('website', {}).get('name', 'Unknown')}"
        title_cell.font = self.Font(bold=True, size=14)
        title_cell.alignment = self.Alignment(horizontal="center")
        
        # Statistics
        row = 3
        stats = data.get('statistics', {})
        
        ws.cell(row=row, column=1, value="Total Pages:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=stats.get('total_pages', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Total Violations:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=stats.get('total_violations', 0))
        ws.cell(row=row, column=2).fill = styles['violation']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Total Warnings:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=stats.get('total_warnings', 0))
        ws.cell(row=row, column=2).fill = styles['warning']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Average Violations/Page:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=f"{stats.get('average_violations', 0):.1f}")
        
        self._auto_adjust_columns(ws)
    
    def _create_pages_sheet(self, ws, pages, styles):
        """Create pages sheet"""
        headers = ['Page URL', 'Violations', 'Warnings', 'Passes', 'Last Tested']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for pr in pages:
            page = pr.get('page', {})
            test = pr.get('test_result', {})
            
            ws.cell(row=row, column=1, value=page.get('url', ''))
            
            violations_cell = ws.cell(row=row, column=2, value=test.get('violation_count', 0))
            if test.get('violation_count', 0) > 0:
                violations_cell.fill = styles['violation']['fill']
            
            warnings_cell = ws.cell(row=row, column=3, value=test.get('warning_count', 0))
            if test.get('warning_count', 0) > 0:
                warnings_cell.fill = styles['warning']['fill']
            
            ws.cell(row=row, column=4, value=test.get('pass_count', 0))
            ws.cell(row=row, column=5, value=str(test.get('test_date', '')))
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_violation_types_sheet(self, ws, violation_types, styles):
        """Create violation types sheet"""
        headers = ['Rule ID', 'Count', 'Description', 'Pages Affected']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        sorted_types = sorted(violation_types.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for rule_id, info in sorted_types:
            ws.cell(row=row, column=1, value=rule_id)
            ws.cell(row=row, column=2, value=info['count'])
            ws.cell(row=row, column=3, value=info.get('description', ''))
            ws.cell(row=row, column=4, value=len(set(info.get('pages', []))))
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_project_summary_sheet(self, ws, data, styles):
        """Create project summary sheet"""
        # Title
        ws.merge_cells('A1:D1')
        title_cell = ws['A1']
        title_cell.value = f"Project Report - {data.get('project', {}).get('name', 'Unknown')}"
        title_cell.font = self.Font(bold=True, size=14)
        title_cell.alignment = self.Alignment(horizontal="center")
        
        # Statistics
        row = 3
        stats = data.get('statistics', {})
        
        ws.cell(row=row, column=1, value="Total Websites:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=stats.get('total_websites', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Total Pages:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=stats.get('total_pages', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Total Violations:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=stats.get('total_violations', 0))
        ws.cell(row=row, column=2).fill = styles['violation']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Average Violations/Page:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=f"{stats.get('average_violations_per_page', 0):.1f}")
        
        self._auto_adjust_columns(ws)
    
    def _create_websites_sheet(self, ws, websites, styles):
        """Create websites sheet"""
        headers = ['Website Name', 'URL', 'Pages', 'Total Violations', 'Total Warnings']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for wd in websites:
            website = wd.get('website', {})
            pages = wd.get('pages', [])
            
            # Handle test_result as object or dict
            total_violations = 0
            total_warnings = 0
            for p in pages:
                test_result = p.get('test_result')
                if test_result:
                    if hasattr(test_result, 'violation_count'):
                        # It's an object
                        total_violations += test_result.violation_count
                        total_warnings += test_result.warning_count
                    elif isinstance(test_result, dict):
                        # It's a dictionary
                        total_violations += test_result.get('violation_count', 0)
                        total_warnings += test_result.get('warning_count', 0)
            
            # Handle website as object or dict
            if hasattr(website, 'name'):
                # It's an object
                ws.cell(row=row, column=1, value=website.name or '')
                ws.cell(row=row, column=2, value=getattr(website, 'url', None) or getattr(website, 'base_url', ''))
            else:
                # It's a dictionary
                ws.cell(row=row, column=1, value=website.get('name', ''))
                ws.cell(row=row, column=2, value=website.get('url', website.get('base_url', '')))
            ws.cell(row=row, column=3, value=len(pages))
            
            violations_cell = ws.cell(row=row, column=4, value=total_violations)
            if total_violations > 0:
                violations_cell.fill = styles['violation']['fill']
            
            warnings_cell = ws.cell(row=row, column=5, value=total_warnings)
            if total_warnings > 0:
                warnings_cell.fill = styles['warning']['fill']
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _create_all_projects_summary_sheet(self, ws, data, styles):
        """Create all projects summary sheet"""
        # Title
        ws.merge_cells('A1:F1')
        title_cell = ws['A1']
        title_cell.value = "All Projects Accessibility Report"
        title_cell.font = self.Font(bold=True, size=14)
        title_cell.alignment = self.Alignment(horizontal="center")
        
        # Overall Statistics
        row = 3
        summary = data.get('summary', {})
        
        ws.cell(row=row, column=1, value="Overall Statistics").font = self.Font(bold=True, size=12)
        row += 1
        
        ws.cell(row=row, column=1, value="Total Projects:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=summary.get('total_projects', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Total Websites:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=summary.get('total_websites', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Total Pages:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=summary.get('total_pages', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Pages Tested:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=summary.get('total_tested', 0))
        row += 1
        
        ws.cell(row=row, column=1, value="Total Violations:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=summary.get('total_violations', 0))
        ws.cell(row=row, column=2).fill = styles['violation']['fill']
        row += 1
        
        ws.cell(row=row, column=1, value="Total Warnings:").font = self.Font(bold=True)
        ws.cell(row=row, column=2, value=summary.get('total_warnings', 0))
        ws.cell(row=row, column=2).fill = styles['warning']['fill']
        
        self._auto_adjust_columns(ws)
    
    def _create_projects_breakdown_sheet(self, ws, projects, styles):
        """Create projects breakdown sheet"""
        headers = ['Project Name', 'Description', 'Websites', 'Total Pages', 'Tested Pages', 'Coverage %', 'Violations', 'Warnings']
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            self._apply_style(cell, styles['header'])
        
        row = 2
        for project_data in projects:
            project = project_data.get('project', {})
            stats = project_data.get('stats', {})
            
            ws.cell(row=row, column=1, value=project.get('name', ''))
            ws.cell(row=row, column=2, value=project.get('description', ''))
            ws.cell(row=row, column=3, value=stats.get('website_count', 0))
            ws.cell(row=row, column=4, value=stats.get('total_pages', 0))
            ws.cell(row=row, column=5, value=stats.get('tested_pages', 0))
            ws.cell(row=row, column=6, value=f"{stats.get('test_coverage', 0):.1f}%")
            
            violations = sum(w.get('violations', 0) for w in project_data.get('websites', []))
            violations_cell = ws.cell(row=row, column=7, value=violations)
            if violations > 0:
                violations_cell.fill = styles['violation']['fill']
            
            warnings = sum(w.get('warnings', 0) for w in project_data.get('websites', []))
            warnings_cell = ws.cell(row=row, column=8, value=warnings)
            if warnings > 0:
                warnings_cell.fill = styles['warning']['fill']
            
            row += 1
        
        self._auto_adjust_columns(ws)
    
    def _apply_style(self, cell, style):
        """Apply style dictionary to a cell"""
        for attr, value in style.items():
            setattr(cell, attr, value)
    
    def _auto_adjust_columns(self, ws):
        """Auto-adjust column widths"""
        for column in ws.columns:
            max_length = 0
            column_letter = self.get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width


class PDFFormatter(BaseFormatter):
    """PDF report formatter (uses HTML + conversion)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.extension = 'pdf'
        self.html_formatter = HTMLFormatter(config)
        
        # Try to import weasyprint
        try:
            from weasyprint import HTML, CSS
            self.HTML = HTML
            self.CSS = CSS
            self.has_weasyprint = True
        except ImportError:
            logger.warning("weasyprint not installed - PDF generation will fall back to HTML")
            self.has_weasyprint = False
    
    def format_page_report(self, data: Dict[str, Any]) -> bytes:
        """Generate PDF for page report"""
        html_content = self.html_formatter.format_page_report(data)
        return self._convert_to_pdf(html_content)
    
    def format_website_report(self, data: Dict[str, Any]) -> bytes:
        """Generate PDF for website report"""
        html_content = self.html_formatter.format_website_report(data)
        return self._convert_to_pdf(html_content)
    
    def format_project_report(self, data: Dict[str, Any]) -> bytes:
        """Generate PDF for project report"""
        html_content = self.html_formatter.format_project_report(data)
        return self._convert_to_pdf(html_content)
    
    def format_all_projects_report(self, data: Dict[str, Any]) -> bytes:
        """Generate PDF for all projects report"""
        html_content = self.html_formatter.format_all_projects_report(data)
        return self._convert_to_pdf(html_content)
    
    def format_summary_report(self, data: Dict[str, Any]) -> bytes:
        """Generate PDF for summary report"""
        html_content = self.html_formatter.format_summary_report(data)
        return self._convert_to_pdf(html_content)
    
    def _convert_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML content to PDF bytes"""
        if self.has_weasyprint:
            try:
                # Add some PDF-specific CSS for better rendering
                pdf_css = self.CSS(string='''
                    @page {
                        size: A4;
                        margin: 1cm;
                    }
                    body {
                        font-size: 10pt;
                    }
                    .container {
                        max-width: 100%;
                        box-shadow: none;
                    }
                    table {
                        page-break-inside: avoid;
                    }
                    .violation, .warning, .pass, .ai-finding {
                        page-break-inside: avoid;
                    }
                ''')
                
                # Create PDF from HTML
                pdf_document = self.HTML(string=html_content).render(stylesheets=[pdf_css])
                pdf_bytes = pdf_document.write_pdf()
                
                return pdf_bytes
            except Exception as e:
                logger.error(f"Failed to generate PDF with weasyprint: {e}")
                # Fall back to returning HTML as bytes
                return html_content.encode('utf-8')
        else:
            # If weasyprint is not available, return HTML as bytes
            logger.warning("PDF generation not available - returning HTML content")
            return html_content.encode('utf-8')
    
    def save_pdf(self, html_content: str, filepath: Path):
        """
        Save HTML as PDF
        
        This method is deprecated - use the format methods that return bytes instead
        """
        pdf_bytes = self._convert_to_pdf(html_content)
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)