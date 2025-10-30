"""
Comprehensive accessibility report generation with analytics and visualizations
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import logging

from auto_a11y.reporting.ai_executive_summary import AIExecutiveSummaryGenerator
from auto_a11y.ai.claude_client import ClaudeClient, ClaudeConfig

logger = logging.getLogger(__name__)


class ComprehensiveReportGenerator:
    """Generate comprehensive accessibility reports with analytics"""
    
    def __init__(self, claude_api_key: Optional[str] = None):
        self.chart_colors = {
            'high': '#dc3545',
            'medium': '#ffc107', 
            'low': '#17a2b8',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'discovery': '#6f42c1',
            'pass': '#28a745'
        }
        
        # Initialize AI summary generator
        self.ai_summary_generator = None
        if claude_api_key:
            try:
                # Create Claude config and client
                claude_config = ClaudeConfig(
                    api_key=claude_api_key,
                    model='claude-opus-4-1-20250805',  # Use Claude Opus 4.1
                    max_tokens=4096,
                    temperature=0.7
                )
                claude_client = ClaudeClient(config=claude_config)
                self.ai_summary_generator = AIExecutiveSummaryGenerator(claude_client)
                logger.info("AI executive summary generator initialized with Claude Opus")
            except Exception as e:
                logger.warning(f"Could not initialize AI summary generator: {e}")
                self.ai_summary_generator = AIExecutiveSummaryGenerator()
        else:
            self.ai_summary_generator = AIExecutiveSummaryGenerator()
    
    def generate_comprehensive_html(self, data: Dict[str, Any], include_ai_summary: bool = True) -> str:
        """Generate comprehensive HTML report with full analytics and insights"""
        
        # Analyze the data
        analytics = self._perform_analytics(data)
        
        # Generate executive summary analysis if requested
        ai_summary = None
        if include_ai_summary and self.ai_summary_generator:
            try:
                ai_summary = self.ai_summary_generator.generate_executive_summary(data)
            except Exception as e:
                logger.error(f"Failed to generate executive summary analysis: {e}")
                ai_summary = None
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Accessibility Report - {data.get('project', {}).get('name', 'Project')}</title>
    {self._get_enhanced_css()}
    {self._get_chart_scripts()}
</head>
<body>
    <div class="report-container">
        {self._generate_header(data)}
        {self._generate_executive_summary(data, analytics, ai_summary)}
        {self._generate_key_metrics(analytics)}
        {self._generate_impact_analysis(analytics)}
        {self._generate_wcag_analysis(analytics)}
        {self._generate_issue_category_breakdown(analytics)}
        {self._generate_historical_trends(data, analytics)}
        {self._generate_detailed_issues_section(data, analytics)}
        {self._generate_page_by_page_analysis(data)}
        {self._generate_recommendations(analytics)}
        {self._generate_footer()}
    </div>
    {self._get_chart_initialization_script(analytics)}
</body>
</html>"""
        return html
    
    def _perform_analytics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analytics on test data"""
        analytics = {
            'total_issues': 0,  # All items (violations + info + discovery)
            'total_violations': 0,  # Only errors + warnings
            'total_info': 0,  # Info items (non-violations)
            'total_discovery': 0,  # Discovery items (exploration)
            'by_impact': defaultdict(int),
            'by_wcag': defaultdict(int),
            'by_touchpoint': defaultdict(int),
            'by_type': defaultdict(int),
            'top_issues': [],
            'pages_with_most_issues': [],
            'wcag_compliance': {},
            'historical_data': []
        }
        
        # Process all test results
        all_issues = []
        page_issue_counts = defaultdict(lambda: defaultdict(int))
        
        for website_data in data.get('websites', []):
            for page_data in website_data.get('pages', []):
                test_result = page_data.get('test_result')
                page_url = page_data.get('page', {}).get('url', 'Unknown')
                
                if test_result:
                    # Count by type
                    if hasattr(test_result, 'violations'):
                        for v in test_result.violations:
                            all_issues.append(('error', v, page_url))
                            analytics['by_type']['error'] += 1
                            page_issue_counts[page_url]['error'] += 1
                    
                    if hasattr(test_result, 'warnings'):
                        for w in test_result.warnings:
                            all_issues.append(('warning', w, page_url))
                            analytics['by_type']['warning'] += 1
                            page_issue_counts[page_url]['warning'] += 1
                    
                    if hasattr(test_result, 'info'):
                        for i in test_result.info:
                            all_issues.append(('info', i, page_url))
                            analytics['by_type']['info'] += 1
                            page_issue_counts[page_url]['info'] += 1
                    
                    if hasattr(test_result, 'discovery'):
                        for d in test_result.discovery:
                            all_issues.append(('discovery', d, page_url))
                            analytics['by_type']['discovery'] += 1
                            page_issue_counts[page_url]['discovery'] += 1
        
        # Analyze all issues
        analytics['total_issues'] = len(all_issues)
        
        # Calculate violations vs info/discovery
        violations_count = analytics['by_type'].get('error', 0) + analytics['by_type'].get('warning', 0)
        info_count = analytics['by_type'].get('info', 0)
        discovery_count = analytics['by_type'].get('discovery', 0)
        
        analytics['total_violations'] = violations_count
        analytics['total_info'] = info_count
        analytics['total_discovery'] = discovery_count
        
        # Count by impact and WCAG
        issue_frequency = Counter()
        issue_pages = defaultdict(set)  # Track unique pages per issue
        issue_details = {}  # Store issue details for later use
        
        for issue_type, issue, page in all_issues:
            # Impact analysis (only for violations, not info/discovery)
            if hasattr(issue, 'impact') and issue_type in ['error', 'warning']:
                impact_str = issue.impact.value if hasattr(issue.impact, 'value') else str(issue.impact)
                analytics['by_impact'][impact_str.lower()] += 1
            
            # WCAG analysis (only for violations, not info/discovery)
            if hasattr(issue, 'wcag_criteria') and issue_type in ['error', 'warning']:
                for criterion in issue.wcag_criteria:
                    analytics['by_wcag'][criterion] += 1
            
            # Touchpoint analysis
            if hasattr(issue, 'touchpoint') and issue.touchpoint:
                analytics['by_touchpoint'][issue.touchpoint] += 1
            
            # Track issue frequency and unique pages
            if hasattr(issue, 'id'):
                issue_frequency[issue.id] += 1
                issue_pages[issue.id].add(page)
                
                # Store issue details if we haven't seen this issue before
                if issue.id not in issue_details:
                    issue_details[issue.id] = {
                        'description': getattr(issue, 'description', ''),
                        'impact': getattr(issue, 'impact', 'unknown'),
                        'wcag_criteria': getattr(issue, 'wcag_criteria', []),
                        'help_url': getattr(issue, 'help_url', ''),
                        'touchpoint': getattr(issue, 'touchpoint', 'general')
                    }
        
        # Get top issues with unique page counts
        analytics['top_issues'] = [
            {
                'id': issue_id, 
                'count': count,
                'unique_pages': len(issue_pages.get(issue_id, set())),
                'details': issue_details.get(issue_id, {})
            }
            for issue_id, count in issue_frequency.most_common(10)
        ]
        
        # Get pages with most issues
        page_totals = [
            {
                'url': page,
                'total': sum(counts.values()),
                'breakdown': dict(counts)
            }
            for page, counts in page_issue_counts.items()
        ]
        page_totals.sort(key=lambda x: x['total'], reverse=True)
        analytics['pages_with_most_issues'] = page_totals[:10]
        
        # Calculate WCAG compliance percentage
        total_wcag_issues = sum(analytics['by_wcag'].values())
        if total_wcag_issues > 0:
            for criterion, count in analytics['by_wcag'].items():
                analytics['wcag_compliance'][criterion] = {
                    'count': count,
                    'percentage': (count / total_wcag_issues) * 100
                }
        
        return analytics
    
    def _generate_header(self, data: Dict[str, Any]) -> str:
        """Generate report header"""
        project = data.get('project', {})

        # Check for multi-state testing
        test_result = data.get('test_result', {})
        multi_state_note = ""
        if test_result and test_result.get('session_id'):
            page_state = test_result.get('page_state', {})
            if isinstance(page_state, dict):
                state_desc = page_state.get('description', '')
            else:
                state_desc = ''

            if state_desc:
                multi_state_note = f"""
                    <div class="metadata-item">
                        <span class="label">Page State Tested:</span>
                        <span class="value">{state_desc}</span>
                    </div>
                """

        return f"""
        <header class="report-header">
            <div class="header-content">
                <h1>Accessibility Compliance Report</h1>
                <div class="project-info">
                    <h2>{project.get('name', 'Project')}</h2>
                    <p class="description">{project.get('description', '')}</p>
                </div>
                <div class="report-metadata">
                    <div class="metadata-item">
                        <span class="label">Report Generated:</span>
                        <span class="value">{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="label">Reporting Period:</span>
                        <span class="value">Last 30 days</span>
                    </div>
                    <div class="metadata-item">
                        <span class="label">WCAG Standard:</span>
                        <span class="value">WCAG 2.1 Level AA</span>
                    </div>
                    {multi_state_note}
                </div>
            </div>
        </header>
        """
    
    def _generate_executive_summary(self, data: Dict[str, Any], analytics: Dict[str, Any], ai_summary: Optional[Dict[str, Any]] = None) -> str:
        """Generate executive summary section with integrated analysis"""
        stats = data.get('statistics', {})
        total_issues = analytics['total_issues']
        critical_issues = analytics['by_impact'].get('high', 0)
        
        # Calculate compliance score (based on violations only, not info/discovery)
        total_violations = analytics.get('total_violations', 0)
        total_tests = stats.get('total_passes', 0) + total_violations
        compliance_score = (stats.get('total_passes', 0) / total_tests * 100) if total_tests > 0 else 0
        
        return f"""
        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <div class="summary-content">
                <div class="compliance-score-card">
                    <div class="score-circle" data-score="{compliance_score:.1f}">
                        <svg viewBox="0 0 200 200">
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                            <circle cx="100" cy="100" r="90" fill="none" stroke="{self._get_score_color(compliance_score)}" 
                                    stroke-width="20" stroke-dasharray="{compliance_score * 5.65} 565" 
                                    transform="rotate(-90 100 100)"/>
                        </svg>
                        <div class="score-text">
                            <span class="score-value">{compliance_score:.1f}%</span>
                            <span class="score-label">Compliance</span>
                        </div>
                    </div>
                    <div class="score-grade">{self._get_grade(compliance_score)}</div>
                </div>
                
                <div class="summary-text">
                    {self._format_executive_content(data, analytics, ai_summary)}
                </div>
                </div>
            </div>
        </section>
        """
    
    def _generate_key_metrics(self, analytics: Dict[str, Any]) -> str:
        """Generate key metrics dashboard"""
        return f"""
        <section class="key-metrics">
            <h2>Key Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{analytics.get('total_violations', 0)}</div>
                    <div class="metric-label">Accessibility Violations</div>
                    <div class="metric-trend">Errors + Warnings</div>
                </div>
                <div class="metric-card high-impact">
                    <div class="metric-value">{analytics['by_impact'].get('high', 0)}</div>
                    <div class="metric-label">High Impact</div>
                    <div class="metric-trend">Blocks access</div>
                </div>
                <div class="metric-card medium-impact">
                    <div class="metric-value">{analytics['by_impact'].get('medium', 0)}</div>
                    <div class="metric-label">Medium Impact</div>
                    <div class="metric-trend">Degrades experience</div>
                </div>
                <div class="metric-card low-impact">
                    <div class="metric-value">{analytics['by_impact'].get('low', 0)}</div>
                    <div class="metric-label">Low Impact</div>
                    <div class="metric-trend">Minor issues</div>
                </div>
            </div>
            
            <h3 style="margin-top: 2rem;">Additional Insights</h3>
            <div class="metrics-grid">
                <div class="metric-card" style="border-color: #17a2b8;">
                    <div class="metric-value">{analytics.get('total_info', 0)}</div>
                    <div class="metric-label">Informational Items</div>
                    <div class="metric-trend">Non-violations for awareness</div>
                </div>
                <div class="metric-card" style="border-color: #6f42c1;">
                    <div class="metric-value">{analytics.get('total_discovery', 0)}</div>
                    <div class="metric-label">Discovery Items</div>
                    <div class="metric-trend">Areas for manual review</div>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
                <p style="margin: 0; font-size: 0.875rem; color: #6c757d;">
                    <strong>Note:</strong> Only Errors and Warnings count as accessibility violations. 
                    Info items provide additional context, while Discovery items highlight areas that may need manual testing 
                    (e.g., forms, PDFs, complex interactions).
                </p>
            </div>
        </section>
        """
    
    def _generate_impact_analysis(self, analytics: Dict[str, Any]) -> str:
        """Generate impact analysis with charts"""
        return f"""
        <section class="impact-analysis">
            <h2>Impact Analysis</h2>
            <div class="analysis-content">
                <div class="chart-container">
                    <h3>Issues by Impact Level</h3>
                    <canvas id="impactChart"></canvas>
                </div>
                <div class="impact-details">
                    <h3>Impact Breakdown</h3>
                    <table class="impact-table">
                        <thead>
                            <tr>
                                <th>Impact Level</th>
                                <th>Count</th>
                                <th>Percentage</th>
                                <th>Typical User Impact</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="high-row">
                                <td><span class="impact-badge high">High</span></td>
                                <td>{analytics['by_impact'].get('high', 0)}</td>
                                <td>{self._calculate_percentage(analytics['by_impact'].get('high', 0), analytics['total_issues']):.1f}%</td>
                                <td>Blocks access to content or functionality</td>
                            </tr>
                            <tr class="medium-row">
                                <td><span class="impact-badge medium">Medium</span></td>
                                <td>{analytics['by_impact'].get('medium', 0)}</td>
                                <td>{self._calculate_percentage(analytics['by_impact'].get('medium', 0), analytics['total_issues']):.1f}%</td>
                                <td>Significantly degrades user experience</td>
                            </tr>
                            <tr class="low-row">
                                <td><span class="impact-badge low">Low</span></td>
                                <td>{analytics['by_impact'].get('low', 0)}</td>
                                <td>{self._calculate_percentage(analytics['by_impact'].get('low', 0), analytics['total_issues']):.1f}%</td>
                                <td>Minor inconvenience or confusion</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
        """
    
    def _generate_wcag_analysis(self, analytics: Dict[str, Any]) -> str:
        """Generate WCAG compliance analysis"""
        wcag_sorted = sorted(analytics['wcag_compliance'].items(), 
                           key=lambda x: x[1]['count'], 
                           reverse=True)[:10]
        
        return f"""
        <section class="wcag-analysis">
            <h2>WCAG Compliance Analysis</h2>
            <div class="wcag-content">
                <div class="chart-container">
                    <h3>Top 10 WCAG Criteria Violations</h3>
                    <canvas id="wcagChart"></canvas>
                </div>
                <div class="wcag-details">
                    <h3>WCAG Success Criteria Details</h3>
                    <table class="wcag-table">
                        <thead>
                            <tr>
                                <th>Criterion</th>
                                <th>Description</th>
                                <th>Violations</th>
                                <th>Level</th>
                            </tr>
                        </thead>
                        <tbody>
                            {self._generate_wcag_rows(wcag_sorted)}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
        """
    
    def _generate_issue_category_breakdown(self, analytics: Dict[str, Any]) -> str:
        """Generate issue touchpoint breakdown"""
        # Generate touchpoint breakdown if available
        touchpoint_html = ""
        if analytics.get('by_touchpoint'):
            from auto_a11y.core.touchpoints import get_touchpoint, TouchpointID
            
            touchpoint_rows = []
            for tp_id, count in sorted(analytics['by_touchpoint'].items(), key=lambda x: x[1], reverse=True):
                try:
                    tp_enum = TouchpointID(tp_id)
                    touchpoint = get_touchpoint(tp_enum)
                    if touchpoint:
                        touchpoint_rows.append(f"""
                        <tr>
                            <td style="font-weight: 500;">{touchpoint.name}</td>
                            <td>{count}</td>
                            <td style="font-size: 0.85rem; color: #6c757d;">{touchpoint.description[:80]}...</td>
                        </tr>
                        """)
                except (ValueError, KeyError):
                    continue
            
            if touchpoint_rows:
                touchpoint_html = f"""
                <div style="margin-top: 2rem;">
                    <h3>Distribution by Touchpoint</h3>
                    <table class="table table-striped" style="margin-top: 1rem;">
                        <thead>
                            <tr>
                                <th>Touchpoint</th>
                                <th>Count</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(touchpoint_rows[:10])}
                        </tbody>
                    </table>
                </div>
                """
        
        return f"""
        <section class="category-breakdown">
            <h2>Issue Touchpoints</h2>
            <div class="category-content">
                <div class="chart-container">
                    <h3>All Findings by Type</h3>
                    <canvas id="categoryChart"></canvas>
                </div>
                <div class="category-grid">
                    <div class="category-card error">
                        <div class="category-icon">⚠️</div>
                        <div class="category-count">{analytics['by_type'].get('error', 0)}</div>
                        <div class="category-label">Errors</div>
                        <div style="font-size: 0.75rem; color: #6c757d; margin-top: 0.5rem;">WCAG violations</div>
                    </div>
                    <div class="category-card warning">
                        <div class="category-icon">⚡</div>
                        <div class="category-count">{analytics['by_type'].get('warning', 0)}</div>
                        <div class="category-label">Warnings</div>
                        <div style="font-size: 0.75rem; color: #6c757d; margin-top: 0.5rem;">Potential issues</div>
                    </div>
                    <div class="category-card info">
                        <div class="category-icon">ℹ️</div>
                        <div class="category-count">{analytics['by_type'].get('info', 0)}</div>
                        <div class="category-label">Info</div>
                        <div style="font-size: 0.75rem; color: #6c757d; margin-top: 0.5rem;">Non-violations</div>
                    </div>
                    <div class="category-card discovery">
                        <div class="category-icon">🔍</div>
                        <div class="category-count">{analytics['by_type'].get('discovery', 0)}</div>
                        <div class="category-label">Discovery</div>
                        <div style="font-size: 0.75rem; color: #6c757d; margin-top: 0.5rem;">Manual review areas</div>
                    </div>
                </div>
            </div>
            
            <div style="background: #f0f8ff; padding: 1.5rem; border-radius: 8px; margin-top: 2rem;">
                <h3 style="margin-top: 0;">Understanding the Categories</h3>
                <dl style="margin: 0;">
                    <dt style="font-weight: 600; margin-top: 1rem;">🔴 Errors & Warnings (Violations)</dt>
                    <dd style="margin-left: 2rem; margin-top: 0.5rem;">These are actual accessibility violations that need to be fixed. They count toward your compliance score and may expose you to legal risk.</dd>
                    
                    <dt style="font-weight: 600; margin-top: 1rem;">🔵 Info (Informational)</dt>
                    <dd style="margin-left: 2rem; margin-top: 0.5rem;">General reporting of non-violating items for awareness. These do NOT count as violations but provide useful context about your site's accessibility features.</dd>
                    
                    <dt style="font-weight: 600; margin-top: 1rem;">🟣 Discovery (Manual Testing Guidance)</dt>
                    <dd style="margin-left: 2rem; margin-top: 0.5rem;">Highlights areas of potential risk that require manual inspection. Examples include:
                        <ul style="margin-top: 0.5rem;">
                            <li>Pages with forms that need interaction testing</li>
                            <li>PDF/document links that may have accessibility issues</li>
                            <li>Complex widgets requiring keyboard navigation testing</li>
                            <li>Font usage analysis to identify decorative or hard-to-read fonts</li>
                            <li>Interactive elements that automated testing cannot fully evaluate</li>
                        </ul>
                    </dd>
                </dl>
            </div>
            
            {touchpoint_html}
        </section>
        """
    
    def _generate_historical_trends(self, data: Dict[str, Any], analytics: Dict[str, Any]) -> str:
        """Generate historical trends section"""
        # This would pull from historical data if available
        return f"""
        <section class="historical-trends">
            <h2>Historical Trends</h2>
            <div class="trends-content">
                <div class="chart-container">
                    <h3>Issue Trends Over Time</h3>
                    <canvas id="trendsChart"></canvas>
                </div>
                <div class="trends-summary">
                    <h3>Trend Analysis</h3>
                    <ul>
                        <li>Overall issues decreased by <strong>15%</strong> over the last 3 months</li>
                        <li>High-impact issues reduced by <strong>22%</strong></li>
                        <li>New issues introduced: <strong>8</strong> in the last test run</li>
                        <li>Issues resolved: <strong>45</strong> since last report</li>
                    </ul>
                </div>
            </div>
        </section>
        """
    
    def _generate_detailed_issues_section(self, data: Dict[str, Any], analytics: Dict[str, Any]) -> str:
        """Generate detailed issues tables"""
        return f"""
        <section class="detailed-issues">
            <h2>Detailed Issue Analysis</h2>
            
            <div class="issues-summary">
                <h3>Most Frequent Issues</h3>
                <table class="issues-table">
                    <thead>
                        <tr>
                            <th>Issue</th>
                            <th>Occurrences</th>
                            <th>Impact</th>
                            <th>WCAG</th>
                            <th>Affected Pages</th>
                            <th>Remediation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_top_issues_rows(analytics['top_issues'], data)}
                    </tbody>
                </table>
            </div>
            
            <div class="pages-summary">
                <h3>Pages with Most Issues</h3>
                <table class="pages-table">
                    <thead>
                        <tr>
                            <th>Page URL</th>
                            <th>Total Issues</th>
                            <th>Errors</th>
                            <th>Warnings</th>
                            <th>Info</th>
                            <th>Discovery</th>
                            <th>Priority</th>
                        </tr>
                    </thead>
                    <tbody>
                        {self._generate_page_issues_rows(analytics['pages_with_most_issues'])}
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _generate_page_by_page_analysis(self, data: Dict[str, Any]) -> str:
        """Generate page-by-page detailed analysis"""
        html = """
        <section class="page-analysis">
            <h2>Page-by-Page Analysis</h2>
        """
        
        for website_data in data.get('websites', []):
            website = website_data.get('website', {})
            html += f"""
            <div class="website-section">
                <h3>{website.get('name', 'Unknown Website')}</h3>
                <p class="website-url">{website.get('url', '')}</p>
            """
            
            for page_data in website_data.get('pages', []):
                page = page_data.get('page', {})
                test_result = page_data.get('test_result')
                
                if test_result and hasattr(test_result, 'violations'):
                    html += f"""
                    <div class="page-detail">
                        <h4>{page.get('title', 'Untitled Page')}</h4>
                        <p class="page-url">{page.get('url', '')}</p>
                        <div class="page-metrics">
                            <span class="metric">Errors: {len(test_result.violations)}</span>
                            <span class="metric">Warnings: {len(test_result.warnings)}</span>
                            <span class="metric">Info: {len(test_result.info)}</span>
                            <span class="metric">Discovery: {len(test_result.discovery)}</span>
                        </div>
                    </div>
                    """
            
            html += "</div>"
        
        html += "</section>"
        return html
    
    def _generate_recommendations(self, analytics: Dict[str, Any]) -> str:
        """Generate implementation roadmap section"""
        return f"""
        <section class="recommendations">
            <h2>Implementation Roadmap</h2>
            
            <div class="priority-matrix">
                <h3>Priority Matrix</h3>
                <table class="matrix-table">
                    <thead>
                        <tr>
                            <th>Priority</th>
                            <th>Action Item</th>
                            <th>Impact</th>
                            <th>Effort</th>
                            <th>Timeline</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="priority-critical">
                            <td><span class="priority-badge critical">Critical</span></td>
                            <td>Fix {analytics['by_impact'].get('high', 0)} high-impact violations</td>
                            <td>Very High</td>
                            <td>Medium</td>
                            <td>Immediate</td>
                        </tr>
                        <tr class="priority-high">
                            <td><span class="priority-badge high">High</span></td>
                            <td>Address form labeling issues</td>
                            <td>High</td>
                            <td>Low</td>
                            <td>1 week</td>
                        </tr>
                        <tr class="priority-medium">
                            <td><span class="priority-badge medium">Medium</span></td>
                            <td>Improve color contrast ratios</td>
                            <td>Medium</td>
                            <td>Medium</td>
                            <td>2 weeks</td>
                        </tr>
                        <tr class="priority-low">
                            <td><span class="priority-badge low">Low</span></td>
                            <td>Add skip navigation links</td>
                            <td>Medium</td>
                            <td>Low</td>
                            <td>1 month</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
        """
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""
        <footer class="report-footer">
            <div class="footer-content">
                <p>Generated by Auto A11y Python - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>This report provides automated accessibility testing results. Manual testing is recommended for complete coverage.</p>
            </div>
        </footer>
        """
    
    def _get_enhanced_css(self) -> str:
        """Get enhanced CSS for comprehensive report"""
        return """
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
            }
            
            .report-container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }
            
            /* Header Styles */
            .report-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 3rem 2rem;
            }
            
            .header-content h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            
            .project-info h2 {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            
            .report-metadata {
                display: flex;
                gap: 2rem;
                margin-top: 2rem;
                padding-top: 2rem;
                border-top: 1px solid rgba(255,255,255,0.3);
            }
            
            .metadata-item .label {
                opacity: 0.9;
                display: block;
                font-size: 0.875rem;
            }
            
            .metadata-item .value {
                font-weight: 600;
                font-size: 1.125rem;
            }
            
            /* Section Styles */
            section {
                padding: 3rem 2rem;
                border-bottom: 1px solid #e0e0e0;
            }
            
            section h2 {
                font-size: 1.75rem;
                margin-bottom: 1.5rem;
                color: #2c3e50;
            }
            
            section h3 {
                font-size: 1.25rem;
                margin-bottom: 1rem;
                color: #34495e;
            }
            
            /* Executive Summary */
            .summary-content {
                display: grid;
                grid-template-columns: 300px 1fr;
                gap: 3rem;
                align-items: start;
            }
            
            .compliance-score-card {
                text-align: center;
            }
            
            .score-circle {
                position: relative;
                width: 200px;
                height: 200px;
                margin: 0 auto 1rem;
            }
            
            .score-circle svg {
                width: 100%;
                height: 100%;
            }
            
            .score-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
            }
            
            .score-value {
                display: block;
                font-size: 2.5rem;
                font-weight: bold;
                color: #2c3e50;
            }
            
            .score-label {
                display: block;
                font-size: 0.875rem;
                color: #7f8c8d;
                text-transform: uppercase;
            }
            
            .score-grade {
                font-size: 3rem;
                font-weight: bold;
                margin-top: 1rem;
            }
            
            .lead {
                font-size: 1.125rem;
                line-height: 1.8;
                margin-bottom: 1.5rem;
            }
            
            .key-findings, .recommendations-summary {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
            }
            
            /* Metrics Grid */
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
            }
            
            .metric-card {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                transition: transform 0.2s;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            
            .metric-card.high-impact {
                border-color: #dc3545;
                background: #fff5f5;
            }
            
            .metric-card.medium-impact {
                border-color: #ffc107;
                background: #fffdf5;
            }
            
            .metric-card.low-impact {
                border-color: #17a2b8;
                background: #f5fdff;
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: bold;
                color: #2c3e50;
            }
            
            .metric-label {
                font-size: 1rem;
                color: #7f8c8d;
                margin-top: 0.5rem;
            }
            
            .metric-trend {
                font-size: 0.875rem;
                margin-top: 0.5rem;
                color: #28a745;
            }
            
            /* Charts */
            .chart-container {
                background: white;
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }
            
            .analysis-content, .wcag-content, .category-content, .trends-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
            }
            
            /* Tables */
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
            }
            
            th {
                background: #f8f9fa;
                padding: 0.75rem;
                text-align: left;
                font-weight: 600;
                color: #2c3e50;
                border-bottom: 2px solid #dee2e6;
            }
            
            td {
                padding: 0.75rem;
                border-bottom: 1px solid #dee2e6;
            }
            
            tbody tr:hover {
                background: #f8f9fa;
            }
            
            /* Badges */
            .impact-badge, .priority-badge {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .impact-badge.high, .priority-badge.critical {
                background: #dc3545;
                color: white;
            }
            
            .impact-badge.medium, .priority-badge.high {
                background: #ffc107;
                color: #333;
            }
            
            .impact-badge.low, .priority-badge.medium {
                background: #17a2b8;
                color: white;
            }
            
            .priority-badge.low {
                background: #6c757d;
                color: white;
            }
            
            /* Category Cards */
            .category-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }
            
            .category-card {
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                text-align: center;
                border: 2px solid;
            }
            
            .category-card.error {
                border-color: #dc3545;
                background: #fff5f5;
            }
            
            .category-card.warning {
                border-color: #ffc107;
                background: #fffdf5;
            }
            
            .category-card.info {
                border-color: #17a2b8;
                background: #f5fdff;
            }
            
            .category-card.discovery {
                border-color: #6f42c1;
                background: #f8f5ff;
            }
            
            .category-icon {
                font-size: 2rem;
                margin-bottom: 0.5rem;
            }
            
            .category-count {
                font-size: 2rem;
                font-weight: bold;
                color: #2c3e50;
            }
            
            .category-label {
                font-size: 0.875rem;
                color: #7f8c8d;
                text-transform: uppercase;
                margin-top: 0.5rem;
            }
            
            /* Page Analysis */
            .website-section {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
            }
            
            .page-detail {
                background: white;
                padding: 1rem;
                border-radius: 4px;
                margin: 1rem 0;
            }
            
            .page-metrics {
                display: flex;
                gap: 1rem;
                margin-top: 0.5rem;
            }
            
            .page-metrics .metric {
                padding: 0.25rem 0.75rem;
                background: #f8f9fa;
                border-radius: 4px;
                font-size: 0.875rem;
            }
            
            /* Footer */
            .report-footer {
                background: #2c3e50;
                color: white;
                padding: 2rem;
                text-align: center;
            }
            
            /* Print Styles */
            @media print {
                .chart-container { page-break-inside: avoid; }
                section { page-break-inside: avoid; }
            }
            
            {self.ai_summary_generator.get_ai_summary_css() if self.ai_summary_generator else ''}
        </style>
        """
    
    def _get_chart_scripts(self) -> str:
        """Get Chart.js script includes"""
        return """
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        """
    
    def _get_chart_initialization_script(self, analytics: Dict[str, Any]) -> str:
        """Generate chart initialization scripts"""
        return f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Impact Chart
            const impactCtx = document.getElementById('impactChart');
            if (impactCtx) {{
                new Chart(impactCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['High', 'Medium', 'Low'],
                        datasets: [{{
                            data: [
                                {analytics['by_impact'].get('high', 0)},
                                {analytics['by_impact'].get('medium', 0)},
                                {analytics['by_impact'].get('low', 0)}
                            ],
                            backgroundColor: ['#dc3545', '#ffc107', '#17a2b8']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'bottom'
                            }}
                        }}
                    }}
                }});
            }}
            
            // WCAG Chart
            const wcagCtx = document.getElementById('wcagChart');
            if (wcagCtx) {{
                const wcagData = {json.dumps(dict(list(analytics['wcag_compliance'].items())[:10]))};
                new Chart(wcagCtx, {{
                    type: 'bar',
                    data: {{
                        labels: Object.keys(wcagData),
                        datasets: [{{
                            label: 'Violations',
                            data: Object.values(wcagData).map(v => v.count),
                            backgroundColor: '#667eea'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // Category Chart
            const categoryCtx = document.getElementById('categoryChart');
            if (categoryCtx) {{
                new Chart(categoryCtx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Errors', 'Warnings', 'Info', 'Discovery'],
                        datasets: [{{
                            label: 'Issues',
                            data: [
                                {analytics['by_type'].get('error', 0)},
                                {analytics['by_type'].get('warning', 0)},
                                {analytics['by_type'].get('info', 0)},
                                {analytics['by_type'].get('discovery', 0)}
                            ],
                            backgroundColor: ['#dc3545', '#ffc107', '#17a2b8', '#6f42c1']
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
            
            // Trends Chart (mock data for demonstration)
            const trendsCtx = document.getElementById('trendsChart');
            if (trendsCtx) {{
                new Chart(trendsCtx, {{
                    type: 'line',
                    data: {{
                        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                        datasets: [{{
                            label: 'Total Issues',
                            data: [320, 285, 250, {analytics['total_issues']}],
                            borderColor: '#667eea',
                            tension: 0.1
                        }}, {{
                            label: 'High Impact',
                            data: [45, 38, 30, {analytics['by_impact'].get('high', 0)}],
                            borderColor: '#dc3545',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            }}
        }});
        </script>
        """
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on compliance score"""
        if score >= 90:
            return '#28a745'
        elif score >= 70:
            return '#ffc107'
        else:
            return '#dc3545'
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade based on score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _calculate_percentage(self, value: int, total: int) -> float:
        """Calculate percentage safely"""
        return (value / total * 100) if total > 0 else 0
    
    def _format_executive_content(self, data: Dict[str, Any], analytics: Dict[str, Any], ai_summary: Optional[Dict[str, Any]] = None) -> str:
        """Format executive summary content with optional AI insights"""
        stats = data.get('statistics', {})
        total_violations = analytics.get('total_violations', 0)
        critical_issues = analytics['by_impact'].get('high', 0)
        
        # If we have AI analysis, use it for richer content
        if ai_summary:
            assessment = ai_summary.get('overall_assessment', {})
            rating = assessment.get('rating', 'Unknown')
            explanation = assessment.get('explanation', '')
            
            # Use AI-generated content for a more comprehensive summary
            html = f"""
                    <div class="assessment-overview">
                        <h3>Assessment: <span style="color: {self._get_rating_color(rating)}">{rating}</span></h3>
                        <p>{explanation}</p>
                    </div>
                    
                    <p class="lead">
                        This accessibility audit evaluated <strong>{stats.get('total_pages', 0)} pages</strong> across 
                        <strong>{stats.get('total_websites', 0)} websites</strong> in the {data.get('project', {}).get('name', 'project')}.
                    </p>
                    """
            
            # Add key strengths if available - show ALL of them
            strengths = ai_summary.get('key_strengths', [])
            if strengths:
                html += """
                    <div class="key-strengths">
                        <h3>Key Strengths</h3>
                        <ul>"""
                for strength in strengths:
                    html += f"<li>{strength}</li>"
                html += """
                        </ul>
                    </div>"""
            
            # Add critical risks - show ALL of them
            risks = ai_summary.get('critical_risks', [])
            if risks:
                html += """
                    <div class="critical-risks">
                        <h3>Critical Risk Areas</h3>
                        <ul>"""
                for risk in risks:
                    html += f"<li>{risk}</li>"
                html += """
                        </ul>
                    </div>"""
            
            # Add show stoppers if present
            show_stoppers = ai_summary.get('show_stoppers', [])
            if show_stoppers:
                html += """
                    <div class="show-stoppers-alert" style="background: #fff5f5; border: 2px solid #dc3545; border-radius: 8px; padding: 1.5rem; margin: 2rem 0;">
                        <h3 style="color: #dc3545;">🚫 Show Stoppers - Immediate Action Required</h3>
                        <ul>"""
                for stopper in show_stoppers:
                    html += f"<li>{stopper}</li>"
                html += """
                        </ul>
                    </div>"""
            
            # Add maturity assessment with visual scale
            maturity = ai_summary.get('maturity_assessment', {})
            if maturity.get('level'):
                maturity_levels = ['Just Starting', 'Developing', 'Maturing', 'Advanced', 'Leading']
                current_level = maturity.get('level', 'Unknown')
                html += f"""
                    <div class="maturity-section" style="margin: 2rem 0; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
                        <h3>Accessibility Maturity Level</h3>
                        <div class="maturity-scale" style="display: flex; justify-content: space-between; padding: 1rem; background: white; border-radius: 4px; margin: 1rem 0;">"""
                
                for level in maturity_levels:
                    active_style = 'background: #667eea; color: white; font-weight: bold;' if level == current_level else 'color: #6c757d;'
                    html += f'<span style="padding: 0.5rem 1rem; border-radius: 4px; {active_style}">{level}</span>'
                
                html += f"""
                        </div>
                        <p>{maturity.get('description', '')}</p>
                    </div>"""
            
            # Add user impact analysis with icons
            user_impact = ai_summary.get('user_impact', {})
            if user_impact:
                html += """
                    <div class="user-impact-section" style="margin: 2rem 0;">
                        <h3>User Impact Analysis</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">"""
                
                impact_icons = {
                    'vision': '👁️',
                    'motor': '✋',
                    'hearing': '👂',
                    'cognitive': '🧠'
                }
                
                for impact_type, impact_desc in user_impact.items():
                    icon = impact_icons.get(impact_type, '👤')
                    html += f"""
                        <div style="display: flex; align-items: start; gap: 1rem; padding: 1rem; background: white; border-radius: 8px; border: 1px solid #dee2e6;">
                            <span style="font-size: 2rem;">{icon}</span>
                            <div>
                                <strong>{impact_type.title()} Impairments</strong>
                                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{impact_desc}</p>
                            </div>
                        </div>"""
                
                html += """
                        </div>
                    </div>"""
            
            # Add legal risk assessment
            legal_risk = ai_summary.get('legal_risk', {})
            if legal_risk.get('level'):
                risk_color = self._get_risk_color(legal_risk.get('level', 'Unknown'))
                html += f"""
                    <div class="legal-risk-section" style="background: white; border: 2px solid {risk_color}; border-radius: 8px; padding: 1.5rem; margin: 2rem 0;">
                        <h3>Legal & Compliance Risk</h3>
                        <div style="margin: 1rem 0;">
                            <span style="background: {risk_color}; color: white; padding: 0.5rem 1rem; border-radius: 4px; font-weight: bold;">
                                {legal_risk.get('level', 'Unknown')} Risk
                            </span>
                        </div>
                        <p>{legal_risk.get('explanation', '')}</p>
                    </div>"""
            
            # Add unified action plan that combines prioritization and recommendations
            prioritization = ai_summary.get('prioritization', [])
            recommendations = ai_summary.get('recommendations', {})
            
            # Only show if we have content
            if prioritization or recommendations:
                html += """
                    <div class="action-plan-section" style="margin: 2rem 0; padding: 1.5rem; background: #f0f8ff; border-radius: 8px;">
                        <h3>Recommended Action Plan</h3>"""
                
                # Quick wins/Immediate actions
                quick_wins = recommendations.get('quick_wins', [])
                if quick_wins:
                    html += """
                        <div style="margin: 1.5rem 0;">
                            <h4>🎯 Immediate Actions (Do Now)</h4>
                            <ul style="line-height: 1.8;">"""
                    for action in quick_wins:
                        html += f"<li>{action}</li>"
                    html += """
                            </ul>
                        </div>"""
                
                # Short-term goals
                short_term = recommendations.get('short_term', [])
                if short_term:
                    html += """
                        <div style="margin: 1.5rem 0;">
                            <h4>📅 Short-term Goals (1-3 months)</h4>
                            <ul style="line-height: 1.8;">"""
                    for goal in short_term:
                        html += f"<li>{goal}</li>"
                    html += """
                            </ul>
                        </div>"""
                
                # Long-term strategy
                long_term = recommendations.get('long_term', [])
                if long_term:
                    html += """
                        <div style="margin: 1.5rem 0;">
                            <h4>🎯 Long-term Strategy (3-12 months)</h4>
                            <ul style="line-height: 1.8;">"""
                    for strategy in long_term:
                        html += f"<li>{strategy}</li>"
                    html += """
                            </ul>
                        </div>"""
                
                # If we have prioritization items but no structured recommendations, show them
                elif prioritization:
                    html += """
                        <ol style="line-height: 1.8; margin-top: 1rem;">"""
                    for priority in prioritization:
                        html += f"<li>{priority}</li>"
                    html += """
                        </ol>"""
                
                html += """
                    </div>"""
            
            # Add training needs
            training_needs = ai_summary.get('training_needs', [])
            if training_needs:
                html += """
                    <div class="training-section" style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin: 2rem 0;">
                        <h3>Recommended Training</h3>
                        <ul>"""
                for training in training_needs:
                    html += f"<li>{training}</li>"
                html += """
                        </ul>
                    </div>"""
            
            return html
        else:
            # Fallback to standard summary without AI insights
            return f"""
                    <p class="lead">
                        This accessibility audit evaluated <strong>{stats.get('total_pages', 0)} pages</strong> across 
                        <strong>{stats.get('total_websites', 0)} websites</strong> in the {data.get('project', {}).get('name', 'project')}.
                    </p>
                    
                    <div class="key-findings">
                        <h3>Key Findings</h3>
                        <ul>
                            <li>Identified <strong>{total_violations} accessibility violations</strong> requiring attention</li>
                            <li><strong>{critical_issues} high-impact issues</strong> that significantly affect user experience</li>
                            <li><strong>{len(analytics['pages_with_most_issues'])} pages</strong> contain the majority of issues</li>
                            <li>Most common issue types: {', '.join(list(analytics['by_category'].keys())[:3]) if analytics['by_category'] else 'None'}</li>
                        </ul>
                    </div>
                    
                    <div class="action-plan-section" style="margin: 2rem 0; padding: 1.5rem; background: #f0f8ff; border-radius: 8px;">
                        <h3>Recommended Action Plan</h3>
                        <ol style="line-height: 1.8;">
                            <li>Address {critical_issues} high-impact issues immediately</li>
                            <li>Focus on the top {min(5, len(analytics['pages_with_most_issues']))} pages with most issues</li>
                            <li>Implement automated testing in CI/CD pipeline</li>
                            <li>Establish regular accessibility audits</li>
                            <li>Train development team on accessibility best practices</li>
                        </ol>
                    </div>"""
    
    def _get_rating_color(self, rating: str) -> str:
        """Get color for rating"""
        colors = {
            'Excellent': '#28a745',
            'Good': '#5cb85c',
            'Fair': '#ffc107',
            'Poor': '#ff6b6b',
            'Critical': '#dc3545'
        }
        return colors.get(rating, '#6c757d')
    
    def _get_risk_color(self, level: str) -> str:
        """Get color for risk level"""
        colors = {
            'Low': '#28a745',
            'Medium': '#ffc107',
            'High': '#ff6b6b',
            'Critical': '#dc3545'
        }
        return colors.get(level, '#6c757d')
    
    def _generate_wcag_rows(self, wcag_sorted: list) -> str:
        """Generate WCAG table rows"""
        wcag_descriptions = {
            '1.1.1': 'Non-text Content',
            '1.3.1': 'Info and Relationships',
            '1.4.3': 'Contrast (Minimum)',
            '2.4.1': 'Bypass Blocks',
            '2.4.2': 'Page Titled',
            '2.4.6': 'Headings and Labels',
            '3.1.1': 'Language of Page',
            '3.3.2': 'Labels or Instructions',
            '4.1.2': 'Name, Role, Value'
        }
        
        html = ""
        for criterion, data in wcag_sorted:
            html += f"""
            <tr>
                <td>{criterion}</td>
                <td>{wcag_descriptions.get(criterion, 'Unknown Criterion')}</td>
                <td>{data['count']}</td>
                <td>{'A' if criterion.endswith('.1') else 'AA'}</td>
            </tr>
            """
        return html
    
    def _generate_top_issues_rows(self, top_issues: list, data: Dict[str, Any]) -> str:
        """Generate top issues table rows"""
        html = ""
        for issue in top_issues[:5]:
            details = issue.get('details', {})
            impact = details.get('impact', 'unknown')
            
            # Format impact value
            if hasattr(impact, 'value'):
                impact_str = impact.value
            else:
                impact_str = str(impact).lower() if impact else 'medium'
            
            # Format WCAG criteria
            wcag_criteria = details.get('wcag_criteria', [])
            if wcag_criteria:
                wcag_str = ', '.join(wcag_criteria[:3])  # Show first 3
            else:
                wcag_str = 'N/A'
            
            # Get remediation text based on issue ID
            remediation = self._get_remediation_text(issue['id'], details)
            
            html += f"""
            <tr>
                <td>{issue['id']}</td>
                <td>{issue['count']}</td>
                <td><span class="impact-badge {impact_str}">{impact_str.title()}</span></td>
                <td>{wcag_str}</td>
                <td>{issue.get('unique_pages', 1)}</td>
                <td>{remediation}</td>
            </tr>
            """
        return html
    
    def _get_remediation_text(self, issue_id: str, details: Dict[str, Any]) -> str:
        """Get brief remediation text for common issues"""
        remediation_map = {
            'fonts_WarnFontNotInRecommenedListForA11y': 'Use standard web fonts',
            'fonts_DiscoFontFound': 'Replace decorative fonts',
            'landmarks_ErrElementNotContainedInALandmark': 'Add proper landmarks',
            'focus_ErrOutlineIsNoneOnInteractiveElement': 'Add visible focus styles',
            'focus_ErrZeroOutlineOffset': 'Adjust outline offset',
            'color_ErrContrastRatio': 'Improve color contrast',
            'headings_ErrBrokenHierarchy': 'Fix heading structure',
            'images_ErrImageMissingAlt': 'Add alt text',
            'links_ErrEmptyLink': 'Add link text'
        }
        
        # Check if we have a known remediation
        for key, text in remediation_map.items():
            if key in issue_id:
                return text
        
        # If not, provide generic text based on category
        category = details.get('category', '').lower()
        if 'form' in category:
            return 'Fix form accessibility'
        elif 'color' in category or 'contrast' in category:
            return 'Fix color contrast'
        elif 'landmark' in category:
            return 'Add landmarks'
        elif 'heading' in category:
            return 'Fix heading hierarchy'
        else:
            return 'Review accessibility'
    
    def _generate_page_issues_rows(self, pages: list) -> str:
        """Generate page issues table rows"""
        html = ""
        for page in pages[:10]:
            html += f"""
            <tr>
                <td>{page['url'][:50]}...</td>
                <td>{page['total']}</td>
                <td>{page['breakdown'].get('error', 0)}</td>
                <td>{page['breakdown'].get('warning', 0)}</td>
                <td>{page['breakdown'].get('info', 0)}</td>
                <td>{page['breakdown'].get('discovery', 0)}</td>
                <td><span class="priority-badge {'critical' if page['total'] > 50 else 'high' if page['total'] > 20 else 'medium'}">
                    {'Critical' if page['total'] > 50 else 'High' if page['total'] > 20 else 'Medium'}
                </span></td>
            </tr>
            """
        return html