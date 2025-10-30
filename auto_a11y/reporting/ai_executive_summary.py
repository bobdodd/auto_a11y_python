"""
AI-powered executive summary generator for accessibility reports
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from auto_a11y.ai.claude_client import ClaudeClient, ClaudeConfig

logger = logging.getLogger(__name__)


class AIExecutiveSummaryGenerator:
    """Generate intelligent executive summaries using Claude AI"""
    
    def __init__(self, claude_client: Optional[ClaudeClient] = None):
        """
        Initialize AI executive summary generator
        
        Args:
            claude_client: Claude AI client instance
        """
        self.claude_client = claude_client
        
    def generate_executive_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive executive summary using Claude AI
        
        Args:
            report_data: Complete report data including test results
            
        Returns:
            Dictionary containing AI-generated insights
        """
        if not self.claude_client:
            return self._get_fallback_summary(report_data)
        
        try:
            # Prepare data for Claude
            analysis_prompt = self._create_analysis_prompt(report_data)
            
            # Get AI analysis using sync client
            response = self._get_claude_response(analysis_prompt)
            
            # Parse and structure the response
            return self._parse_ai_response(response, report_data)
            
        except Exception as e:
            logger.error(f"Failed to generate AI executive summary: {e}")
            return self._get_fallback_summary(report_data)
    
    def _get_claude_response(self, prompt: str) -> str:
        """Get response from Claude using sync client"""
        try:
            # Use the sync client directly
            message = self.claude_client.sync_client.messages.create(
                model=self.claude_client.config.model,
                max_tokens=self.claude_client.config.max_tokens,
                temperature=self.claude_client.config.temperature,
                system=self.claude_client.system_prompt,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract text from response
            if hasattr(message, 'content') and len(message.content) > 0:
                response_text = message.content[0].text
                logger.info(f"Claude response length: {len(response_text)} chars")
                logger.debug(f"Claude response preview: {response_text[:200]}...")
                return response_text
            else:
                return str(message)
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise
    
    def _create_analysis_prompt(self, report_data: Dict[str, Any]) -> str:
        """Create detailed prompt for Claude analysis"""
        
        stats = report_data.get('statistics', {})
        
        # Collect all issues for analysis
        all_violations = []
        all_warnings = []
        critical_issues = []
        
        for website_data in report_data.get('websites', []):
            for page_data in website_data.get('pages', []):
                test_result = page_data.get('test_result')
                if test_result and hasattr(test_result, 'violations'):
                    for v in test_result.violations:
                        violation_info = {
                            'description': v.description if hasattr(v, 'description') else '',
                            'impact': v.impact.value if hasattr(v, 'impact') and hasattr(v.impact, 'value') else 'unknown',
                            'wcag': v.wcag_criteria if hasattr(v, 'wcag_criteria') else [],
                            'category': v.category if hasattr(v, 'category') else 'general'
                        }
                        all_violations.append(violation_info)
                        
                        if violation_info['impact'] == 'high':
                            critical_issues.append(violation_info)
                
                if test_result and hasattr(test_result, 'warnings'):
                    for w in test_result.warnings:
                        warning_info = {
                            'description': w.description if hasattr(w, 'description') else '',
                            'impact': w.impact.value if hasattr(w, 'impact') and hasattr(w.impact, 'value') else 'unknown',
                            'category': w.category if hasattr(w, 'category') else 'general'
                        }
                        all_warnings.append(warning_info)
        
        # Check if any pages were tested with multi-state or responsive breakpoints
        testing_notes = []
        for website_data in report_data.get('websites', []):
            for page_data in website_data.get('pages', []):
                test_result = page_data.get('test_result')
                if test_result:
                    if hasattr(test_result, 'session_id') and test_result.session_id:
                        testing_notes.append("Some pages tested in multiple states (e.g., with/without cookie banners)")
                        break

        testing_context = "\n".join(f"- {note}" for note in set(testing_notes)) if testing_notes else ""

        prompt = f"""
        Analyze the following accessibility test results and provide a comprehensive executive summary.

        PROJECT INFORMATION:
        - Project: {report_data.get('project', {}).get('name', 'Unknown')}
        - Description: {report_data.get('project', {}).get('description', 'No description')}
        - Total Websites: {stats.get('total_websites', 0)}
        - Total Pages Tested: {stats.get('total_pages', 0)}
        {f'''
        TESTING CONTEXT:
        {testing_context}
        ''' if testing_context else ''}

        TEST RESULTS SUMMARY:
        - Total Violations (Errors): {stats.get('total_violations', 0)}
        - Total Warnings: {stats.get('total_warnings', 0)}
        - Total Info Items: {stats.get('total_info', 0)}
        - Total Discovery Items: {stats.get('total_discovery', 0)}
        - Total Passed Tests: {stats.get('total_passes', 0)}
        - High Impact Issues: {len(critical_issues)}
        
        CRITICAL ISSUES FOUND:
        {json.dumps(critical_issues[:10], indent=2) if critical_issues else 'No critical issues found'}
        
        TOP VIOLATION PATTERNS:
        {self._get_violation_patterns(all_violations)}
        
        Please provide a comprehensive executive summary that includes:
        
        1. **Overall Accessibility Assessment**: Rate the overall accessibility quality (Excellent, Good, Fair, Poor, Critical) and explain why.
        
        2. **Key Strengths**: What accessibility features are working well?
        
        3. **Critical Risk Areas**: What are the most serious accessibility barriers that need immediate attention?
        
        4. **Show Stoppers**: Are there any issues that completely block access for users with disabilities?
        
        5. **Accessibility Maturity Assessment**: Where is this organization on their accessibility journey?
           - Just Starting: Basic awareness, many fundamental issues
           - Developing: Some progress made, but significant gaps remain
           - Maturing: Good foundation, working on refinements
           - Advanced: Strong accessibility culture, minor issues only
           - Leading: Exemplary accessibility, could be a model for others
        
        6. **User Impact Analysis**: Which user groups are most affected by the current issues?
           - Vision impairments (blind, low vision, color blind)
           - Motor impairments (keyboard-only, limited mobility)
           - Hearing impairments
           - Cognitive impairments
        
        7. **Legal Risk Assessment**: What is the level of legal/compliance risk?
        
        8. **Recommended Prioritization**: What should be fixed first, second, and third?
        
        9. **Strategic Recommendations**: 
           - Quick wins (can be fixed immediately)
           - Short-term goals (1-3 months)
           - Long-term strategy (3-12 months)
        
        10. **Training Needs**: What training would benefit the team?
        
        Respond with ONLY a valid JSON object. Do not include any text before or after the JSON.
        The response must start with {{ and end with }}
        Be specific, actionable, and constructive in your recommendations.
        
        Required JSON structure:
        {{
          "overall_assessment": {{"rating": "string", "explanation": "string"}},
          "key_strengths": ["array of strings"],
          "critical_risks": ["array of strings"],
          "show_stoppers": ["array of strings"],
          "maturity_assessment": {{"level": "string", "description": "string"}},
          "user_impact": {{"vision": "string", "motor": "string", "hearing": "string", "cognitive": "string"}},
          "legal_risk": {{"level": "string", "explanation": "string"}},
          "prioritization": ["array of strings"],
          "recommendations": {{
            "quick_wins": ["array of strings"],
            "short_term": ["array of strings"],
            "long_term": ["array of strings"]
          }},
          "training_needs": ["array of strings"]
        }}
        """
        
        return prompt
    
    def _get_violation_patterns(self, violations: List[Dict]) -> str:
        """Analyze and summarize violation patterns"""
        if not violations:
            return "No violations to analyze"
        
        # Count violations by category
        category_counts = {}
        for v in violations:
            category = v.get('category', 'general')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Sort by count
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Format top patterns
        patterns = []
        for category, count in sorted_categories[:5]:
            patterns.append(f"- {category}: {count} issues")
        
        return "\n".join(patterns)
    
    def _parse_ai_response(self, response: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response into structured format"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                ai_analysis = json.loads(response)
            else:
                # Extract JSON from response if wrapped in text
                import re
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    try:
                        ai_analysis = json.loads(json_match.group())
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from Claude response: {e}")
                        logger.debug(f"Response was: {response[:500]}...")
                        # Fallback to text parsing
                        ai_analysis = self._parse_text_response(response)
                else:
                    # Fallback to text parsing
                    logger.info("No JSON found in response, using text parser")
                    ai_analysis = self._parse_text_response(response)
            
            # Ensure all required fields are present
            return {
                'overall_assessment': ai_analysis.get('overall_assessment', {
                    'rating': 'Unknown',
                    'explanation': 'Assessment not available'
                }),
                'key_strengths': ai_analysis.get('key_strengths', []),
                'critical_risks': ai_analysis.get('critical_risks', []),
                'show_stoppers': ai_analysis.get('show_stoppers', []),
                'maturity_assessment': ai_analysis.get('maturity_assessment', {
                    'level': 'Unknown',
                    'description': 'Assessment not available'
                }),
                'user_impact': ai_analysis.get('user_impact', {}),
                'legal_risk': ai_analysis.get('legal_risk', {
                    'level': 'Unknown',
                    'explanation': 'Assessment not available'
                }),
                'prioritization': ai_analysis.get('prioritization', []),
                'recommendations': ai_analysis.get('recommendations', {
                    'quick_wins': [],
                    'short_term': [],
                    'long_term': []
                }),
                'training_needs': ai_analysis.get('training_needs', []),
                'generated_at': datetime.now().isoformat(),
                'ai_model': 'Claude Opus 4.1'
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._get_fallback_summary(report_data)
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse unstructured text response into structured format"""
        # This is a fallback parser for non-JSON responses
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            if line.startswith('**') and line.endswith('**'):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.strip('*').strip().lower().replace(' ', '_')
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _get_fallback_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic summary when AI is not available"""
        stats = report_data.get('statistics', {})
        total_issues = stats.get('total_violations', 0) + stats.get('total_warnings', 0)
        
        # Determine overall rating based on issue count
        if total_issues == 0:
            rating = "Excellent"
            explanation = "No accessibility issues detected."
        elif total_issues < 10:
            rating = "Good"
            explanation = f"Minor accessibility issues found ({total_issues} total)."
        elif total_issues < 50:
            rating = "Fair"
            explanation = f"Moderate accessibility issues found ({total_issues} total)."
        elif total_issues < 100:
            rating = "Poor"
            explanation = f"Significant accessibility issues found ({total_issues} total)."
        else:
            rating = "Critical"
            explanation = f"Critical accessibility issues found ({total_issues} total)."
        
        return {
            'overall_assessment': {
                'rating': rating,
                'explanation': explanation
            },
            'key_strengths': [
                f"{stats.get('total_passes', 0)} accessibility tests passed",
                f"{stats.get('total_pages', 0)} pages tested comprehensively"
            ],
            'critical_risks': [
                f"{stats.get('total_violations', 0)} violations need to be addressed",
                f"{stats.get('total_warnings', 0)} warnings should be reviewed"
            ],
            'show_stoppers': [],
            'maturity_assessment': {
                'level': 'Developing' if total_issues > 50 else 'Maturing',
                'description': 'Based on automated testing results'
            },
            'user_impact': {
                'vision': 'Review image alt text and color contrast',
                'motor': 'Check keyboard navigation',
                'hearing': 'Verify video captions',
                'cognitive': 'Simplify complex interactions'
            },
            'legal_risk': {
                'level': 'Medium' if total_issues > 50 else 'Low',
                'explanation': 'Based on issue count and severity'
            },
            'prioritization': [
                'Fix high-impact violations first',
                'Address form and navigation issues',
                'Improve color contrast and text alternatives'
            ],
            'recommendations': {
                'quick_wins': [
                    'Add missing alt text to images',
                    'Fix empty links and buttons',
                    'Add page language attributes'
                ],
                'short_term': [
                    'Improve keyboard navigation',
                    'Fix heading hierarchy',
                    'Address color contrast issues'
                ],
                'long_term': [
                    'Implement comprehensive testing process',
                    'Train development team on accessibility',
                    'Establish accessibility governance'
                ]
            },
            'training_needs': [
                'WCAG 2.1 fundamentals',
                'Accessible coding practices',
                'Assistive technology awareness'
            ],
            'generated_at': datetime.now().isoformat(),
            'ai_model': 'Fallback (AI not available)'
        }
    
    def format_executive_summary_html(self, ai_summary: Dict[str, Any]) -> str:
        """Format AI executive summary as HTML"""
        
        assessment = ai_summary.get('overall_assessment', {})
        maturity = ai_summary.get('maturity_assessment', {})
        legal_risk = ai_summary.get('legal_risk', {})
        recommendations = ai_summary.get('recommendations', {})
        
        # Determine color based on rating
        rating_colors = {
            'Excellent': '#28a745',
            'Good': '#5cb85c', 
            'Fair': '#ffc107',
            'Poor': '#ff6b6b',
            'Critical': '#dc3545'
        }
        rating_color = rating_colors.get(assessment.get('rating', 'Unknown'), '#6c757d')
        
        html = f"""
        <section class="executive-summary-analysis">
            
            <div class="assessment-card" style="border-left: 5px solid {rating_color};">
                <h3>Overall Accessibility Assessment</h3>
                <div class="rating-display">
                    <span class="rating-value" style="color: {rating_color}; font-size: 2em; font-weight: bold;">
                        {assessment.get('rating', 'Unknown')}
                    </span>
                    <p>{assessment.get('explanation', '')}</p>
                </div>
            </div>
            
            <div class="summary-grid">
                <div class="summary-section">
                    <h3>✅ Key Strengths</h3>
                    <ul>
                        {"".join(f"<li>{strength}</li>" for strength in ai_summary.get('key_strengths', []))}
                    </ul>
                </div>
                
                <div class="summary-section critical">
                    <h3>⚠️ Critical Risk Areas</h3>
                    <ul>
                        {"".join(f"<li>{risk}</li>" for risk in ai_summary.get('critical_risks', []))}
                    </ul>
                </div>
            </div>
            
            {self._format_show_stoppers(ai_summary.get('show_stoppers', []))}
            
            <div class="maturity-section">
                <h3>Accessibility Maturity Level</h3>
                <div class="maturity-indicator">
                    <div class="maturity-scale">
                        <span class="level {'active' if maturity.get('level') == 'Just Starting' else ''}">Just Starting</span>
                        <span class="level {'active' if maturity.get('level') == 'Developing' else ''}">Developing</span>
                        <span class="level {'active' if maturity.get('level') == 'Maturing' else ''}">Maturing</span>
                        <span class="level {'active' if maturity.get('level') == 'Advanced' else ''}">Advanced</span>
                        <span class="level {'active' if maturity.get('level') == 'Leading' else ''}">Leading</span>
                    </div>
                    <p class="maturity-description">{maturity.get('description', '')}</p>
                </div>
            </div>
            
            <div class="impact-analysis">
                <h3>User Impact Analysis</h3>
                <div class="impact-grid">
                    {self._format_user_impact(ai_summary.get('user_impact', {}))}
                </div>
            </div>
            
            <div class="legal-risk-section" style="border-color: {self._get_risk_color(legal_risk.get('level', 'Unknown'))};">
                <h3>Legal & Compliance Risk</h3>
                <div class="risk-level">
                    <span class="risk-badge" style="background: {self._get_risk_color(legal_risk.get('level', 'Unknown'))};">
                        {legal_risk.get('level', 'Unknown')} Risk
                    </span>
                    <p>{legal_risk.get('explanation', '')}</p>
                </div>
            </div>
            
            <div class="prioritization-section">
                <h3>Recommended Prioritization</h3>
                <ol class="priority-list">
                    {"".join(f'<li class="priority-item">{item}</li>' for item in ai_summary.get('prioritization', []))}
                </ol>
            </div>
            
            <div class="recommendations-section">
                <h3>Strategic Recommendations</h3>
                
                <div class="recommendation-category">
                    <h4>🎯 Quick Wins (Immediate)</h4>
                    <ul>
                        {"".join(f"<li>{item}</li>" for item in recommendations.get('quick_wins', []))}
                    </ul>
                </div>
                
                <div class="recommendation-category">
                    <h4>📅 Short-term Goals (1-3 months)</h4>
                    <ul>
                        {"".join(f"<li>{item}</li>" for item in recommendations.get('short_term', []))}
                    </ul>
                </div>
                
                <div class="recommendation-category">
                    <h4>🎯 Long-term Strategy (3-12 months)</h4>
                    <ul>
                        {"".join(f"<li>{item}</li>" for item in recommendations.get('long_term', []))}
                    </ul>
                </div>
            </div>
            
            <div class="training-section">
                <h3>Recommended Training</h3>
                <ul class="training-list">
                    {"".join(f'<li class="training-item">{item}</li>' for item in ai_summary.get('training_needs', []))}
                </ul>
            </div>
        </section>
        """
        
        return html
    
    def _format_show_stoppers(self, show_stoppers: List) -> str:
        """Format show stopper issues"""
        if not show_stoppers:
            return ""
        
        items = "".join(f"<li class='show-stopper-item'>{item}</li>" for item in show_stoppers)
        return f"""
        <div class="show-stoppers-alert">
            <h3>🚫 Show Stoppers - Immediate Action Required</h3>
            <ul class="show-stoppers-list">
                {items}
            </ul>
        </div>
        """
    
    def _format_user_impact(self, impact: Dict[str, str]) -> str:
        """Format user impact analysis"""
        impact_html = ""
        icons = {
            'vision': '👁️',
            'motor': '✋',
            'hearing': '👂',
            'cognitive': '🧠'
        }
        
        for key, value in impact.items():
            icon = icons.get(key, '👤')
            impact_html += f"""
            <div class="impact-item">
                <span class="impact-icon">{icon}</span>
                <div class="impact-details">
                    <strong>{key.title()} Impairments</strong>
                    <p>{value}</p>
                </div>
            </div>
            """
        
        return impact_html
    
    def _get_risk_color(self, level: str) -> str:
        """Get color for risk level"""
        colors = {
            'Low': '#28a745',
            'Medium': '#ffc107',
            'High': '#ff6b6b',
            'Critical': '#dc3545'
        }
        return colors.get(level, '#6c757d')
    
    def get_ai_summary_css(self) -> str:
        """Get CSS styles for executive summary analysis"""
        return """
        .executive-summary-analysis {
            padding: 0;
            margin: 0;
        }
        
        .assessment-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin: 2rem 0;
        }
        
        .summary-section {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .summary-section.critical {
            border-left: 4px solid #ff6b6b;
        }
        
        .maturity-scale {
            display: flex;
            justify-content: space-between;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .maturity-scale .level {
            padding: 0.5rem 1rem;
            border-radius: 4px;
            color: #6c757d;
            font-size: 0.875rem;
        }
        
        .maturity-scale .level.active {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        
        .show-stoppers-alert {
            background: #fff5f5;
            border: 2px solid #dc3545;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }
        
        .impact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }
        
        .impact-item {
            display: flex;
            align-items: start;
            gap: 1rem;
            padding: 1rem;
            background: white;
            border-radius: 8px;
        }
        
        .impact-icon {
            font-size: 2rem;
        }
        
        .legal-risk-section {
            background: white;
            border: 2px solid;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }
        
        .risk-badge {
            padding: 0.5rem 1rem;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 1rem;
        }
        
        .recommendation-category {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .recommendation-category h4 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .training-section {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-top: 2rem;
        }
        
        .priority-list {
            counter-reset: priority;
            list-style: none;
            padding: 0;
        }
        
        .priority-item {
            counter-increment: priority;
            padding: 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 4px;
            position: relative;
            padding-left: 3rem;
        }
        
        .priority-item::before {
            content: counter(priority);
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            background: #667eea;
            color: white;
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        """