"""
Main Claude AI analyzer for accessibility testing
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from auto_a11y.ai.claude_client import ClaudeClient, ClaudeConfig
from auto_a11y.ai.analysis_modules import (
    HeadingAnalyzer,
    ReadingOrderAnalyzer,
    ModalAnalyzer,
    LanguageAnalyzer,
    AnimationAnalyzer,
    InteractiveAnalyzer,
    generate_xpath
)
from auto_a11y.models import Violation, ImpactLevel

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Main Claude AI analyzer for comprehensive accessibility analysis"""
    
    def __init__(self, api_key: str, model: str = None):
        """
        Initialize Claude analyzer
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use (defaults to config)
        """
        # Get config values
        try:
            from config import config as app_config
            if model is None:
                model = getattr(app_config, 'CLAUDE_MODEL', 'claude-opus-4-20250514')
            max_tokens = getattr(app_config, 'CLAUDE_MAX_TOKENS', 16000)
            budget_tokens = getattr(app_config, 'CLAUDE_BUDGET_TOKENS', 10000)
            use_thinking = getattr(app_config, 'CLAUDE_USE_THINKING', True)
            logger.info(f"Using CLAUDE_MODEL from config: {model}, thinking: {use_thinking}")
        except Exception as e:
            if model is None:
                model = 'claude-opus-4-20250514'
            max_tokens = 16000
            budget_tokens = 10000
            use_thinking = True
            logger.warning(f"Could not get Claude config, using defaults: {model}")
        
        # Initialize client with extended thinking support
        config = ClaudeConfig(
            api_key=api_key, 
            model=model,
            max_tokens=max_tokens,
            budget_tokens=budget_tokens,
            use_extended_thinking=use_thinking
        )
        self.client = ClaudeClient(config)
        
        # Initialize analyzers
        self.heading_analyzer = HeadingAnalyzer(self.client)
        self.reading_order_analyzer = ReadingOrderAnalyzer(self.client)
        self.modal_analyzer = ModalAnalyzer(self.client)
        self.language_analyzer = LanguageAnalyzer(self.client)
        self.animation_analyzer = AnimationAnalyzer(self.client)
        self.interactive_analyzer = InteractiveAnalyzer(self.client)
        
        logger.info(f"Claude analyzer initialized with model: {model}")
    
    async def analyze_page(
        self,
        screenshot: bytes,
        html: str,
        analyses: Optional[List[str]] = None,
        test_config = None
    ) -> Dict[str, Any]:
        """
        Run AI analyses on a web page
        
        Args:
            screenshot: Page screenshot bytes
            html: Page HTML content
            analyses: List of analyses to run (default: all)
            test_config: TestConfiguration instance for enable/disable
            
        Returns:
            Combined analysis results
        """
        # Get test configuration
        if test_config is None:
            from auto_a11y.config.test_config import get_test_config
            test_config = get_test_config()
        
        # Check if AI tests are enabled globally
        if not test_config.config.get("global", {}).get("run_ai_tests", True):
            logger.info("AI tests are disabled globally")
            return {
                'timestamp': datetime.now().isoformat(),
                'analyses_run': [],
                'findings': [],
                'raw_results': {},
                'message': 'AI tests disabled'
            }
        
        # Filter analyses based on configuration
        if analyses is None:
            analyses = ['headings', 'reading_order', 'language', 'interactive']
        
        # Filter based on configuration
        enabled_analyses = []
        for analysis in analyses:
            if test_config.is_ai_test_enabled(analysis):
                enabled_analyses.append(analysis)
            else:
                logger.debug(f"Skipping disabled AI analysis: {analysis}")
        
        analyses = enabled_analyses
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'analyses_run': analyses,
            'findings': [],
            'raw_results': {}
        }
        
        tasks = []
        
        # Create analysis tasks
        if 'headings' in analyses:
            tasks.append(('headings', self.heading_analyzer.analyze(screenshot, html)))
        
        if 'reading_order' in analyses:
            tasks.append(('reading_order', self.reading_order_analyzer.analyze(screenshot, html)))
        
        if 'modals' in analyses:
            tasks.append(('modals', self.modal_analyzer.analyze(screenshot, html)))
        
        if 'language' in analyses:
            tasks.append(('language', self.language_analyzer.analyze(screenshot, html)))
        
        if 'animations' in analyses:
            tasks.append(('animations', self.animation_analyzer.analyze(html)))
        
        if 'interactive' in analyses:
            tasks.append(('interactive', self.interactive_analyzer.analyze(screenshot, html)))
        
        # Run analyses in parallel
        for name, task in tasks:
            try:
                result = await task
                results['raw_results'][name] = result
                
                # Process findings into AIFinding objects
                findings = self._process_findings(name, result)
                results['findings'].extend(findings)
                
            except Exception as e:
                logger.error(f"Analysis '{name}' failed: {e}")
                results['raw_results'][name] = {'error': str(e)}
        
        # Add summary
        results['summary'] = self._generate_summary(results['findings'])
        
        return results
    
    def _process_findings(self, analysis_type: str, result: Dict[str, Any]) -> List[Violation]:
        """
        Process raw analysis results into Violation objects
        
        Args:
            analysis_type: Type of analysis
            result: Raw analysis result
            
        Returns:
            List of AI findings
        """
        findings = []
        
        if 'error' in result:
            return findings
        
        # Process issues from each analyzer
        issues = result.get('issues', [])
        
        for issue in issues:
            logger.warning(f"AI issue raw data: {issue}")
            finding = self._create_finding(analysis_type, issue, result)
            if finding:
                logger.warning(f"AI finding metadata: {finding.metadata}")
                findings.append(finding)
        
        # Special processing for specific analyzers
        if analysis_type == 'headings' and 'visual_headings' in result:
            # Check for visual headings not in HTML
            visual = result.get('visual_headings', [])
            html_headings = result.get('html_headings', [])
            html_texts = [h.get('text', '').lower() for h in html_headings]
            
            for vh in visual:
                if vh.get('text', '').lower() not in html_texts:
                    # Generate xpath if we have element info
                    xpath = None
                    if vh.get('likely_element'):
                        xpath = generate_xpath(
                            vh.get('likely_element', 'div'),
                            vh.get('element_id'),
                            vh.get('element_class'),
                            element_text=None,  # Don't use text to avoid duplicates
                            element_index=None,
                            use_text=False
                        )
                    
                    violation = Violation(
                        id='AI_ErrVisualHeadingNotMarked',
                        impact=ImpactLevel.HIGH,
                        touchpoint='headings',
                        description=f"Text '{vh.get('text', '')}' appears to be a heading but is not marked up as one",
                        failure_summary=f"Use <h{vh.get('appears_to_be_level', 2)}> tag for this heading",
                        xpath=xpath,
                        element=vh.get('likely_element'),
                        html=vh.get('element_html'),
                        metadata={
                            'ai_detected': True,
                            'ai_confidence': 0.8,
                            'ai_analysis_type': 'headings',
                            'visual_text': vh.get('text', ''),  # Key used in template placeholder
                            'suggested_level': vh.get('appears_to_be_level', 2),
                            'element_class': vh.get('element_class'),
                            'element_id': vh.get('element_id'),
                            'visual_location': vh.get('approximate_location')
                        }
                    )
                    findings.append(violation)
        
        return findings
    
    def _create_finding(
        self,
        analysis_type: str,
        issue: Dict[str, Any],
        full_result: Dict[str, Any]
    ) -> Optional[Violation]:
        """
        Create a Violation from an AI-detected issue.
        
        The AI analyzers now return specific error codes in the 'err' field.
        
        Args:
            analysis_type: Type of analysis
            issue: Issue dictionary with 'err', 'type', 'description', etc.
            full_result: Complete analysis result
            
        Returns:
            Violation object or None
        """
        try:
            # Get error code directly from AI response (new approach)
            # AI analyzers now return specific codes like AI_ErrVisualHeadingNotMarked
            issue_code = issue.get('err')
            issue_type = issue.get('type', 'err')  # 'err', 'warn', or 'info'
            
            # Determine impact from issue type
            if issue_type == 'err':
                impact = ImpactLevel.HIGH
            elif issue_type == 'warn':
                impact = ImpactLevel.MEDIUM
            else:
                impact = ImpactLevel.LOW
            
            # Fallback if AI didn't provide error code
            if not issue_code:
                fallback_codes = {
                    'headings': 'AI_ErrHeadingIssue',
                    'reading_order': 'AI_ErrReadingOrderMismatch',
                    'modals': 'AI_ErrDialogMissingRole',
                    'language': 'AI_WarnForeignTextUnmarked',
                    'animations': 'AI_WarnNoReducedMotion',
                    'interactive': 'AI_ErrNonSemanticButton'
                }
                issue_code = fallback_codes.get(analysis_type, 'AI_ErrAccessibilityIssue')
            
            # Build metadata - copy all issue fields plus AI-specific info
            metadata = {
                'ai_detected': True,
                'ai_confidence': 0.85,
                'ai_analysis_type': analysis_type,
                **{k: v for k, v in issue.items() if k not in ('err', 'type')}
            }
            
            # Ensure key fields for template placeholders
            metadata['element_tag'] = issue.get('element_tag', 'div')
            metadata['element_text'] = issue.get('element_text', '')
            metadata['visual_text'] = issue.get('visual_text', '')
            metadata['heading_text'] = issue.get('heading_text', '')
            metadata['suggested_level'] = issue.get('suggested_level', '')
            metadata['current_level'] = issue.get('current_level', '')
            
            # Generate XPath from element info
            element_tag = issue.get('element_tag', 'div')
            element_id = issue.get('element_id')
            element_class = issue.get('element_class')
            
            # Clean None/null string values
            if element_id and str(element_id).lower() in ['none', 'null', '']:
                element_id = None
            if element_class and str(element_class).lower() in ['none', 'null', '']:
                element_class = None
            
            xpath = generate_xpath(element_tag, element_id, element_class)
            
            # Map analysis type to touchpoint
            from auto_a11y.core.touchpoints import TouchpointID
            ai_to_touchpoint_map = {
                'headings': TouchpointID.HEADINGS,
                'reading_order': TouchpointID.FOCUS_MANAGEMENT,
                'modals': TouchpointID.DIALOGS,
                'language': TouchpointID.LANGUAGE,
                'animations': TouchpointID.ANIMATION,
                'interactive': TouchpointID.EVENT_HANDLING
            }
            
            touchpoint_id = ai_to_touchpoint_map.get(analysis_type)
            touchpoint_value = touchpoint_id.value if touchpoint_id else analysis_type
            
            violation = Violation(
                id=issue_code,
                impact=impact,
                touchpoint=touchpoint_value,
                description=issue.get('description', 'AI-detected accessibility issue'),
                element=element_tag,
                html=issue.get('element_html'),
                xpath=xpath,
                failure_summary=issue.get('fix') or issue.get('suggested_fix'),
                metadata=metadata
            )
            
            return violation
            
        except Exception as e:
            logger.error(f"Failed to create finding: {e}")
            return None
    
    def _generate_summary(self, findings: List[Violation]) -> Dict[str, Any]:
        """
        Generate summary of AI findings
        
        Args:
            findings: List of AI findings
            
        Returns:
            Summary dictionary
        """
        high = sum(1 for f in findings if f.impact == ImpactLevel.HIGH)
        medium = sum(1 for f in findings if f.impact == ImpactLevel.MEDIUM)
        low = sum(1 for f in findings if f.impact == ImpactLevel.LOW)
        
        return {
            'total_findings': len(findings),
            'by_impact': {
                'high': high,
                'medium': medium,
                'low': low
            },
            'by_type': self._count_by_type(findings),
            'requires_immediate_attention': high > 0,
            'ai_confidence_avg': sum(f.metadata.get('ai_confidence', 0.85) for f in findings) / len(findings) if findings else 0
        }
    
    def _count_by_type(self, findings: List[Violation]) -> Dict[str, int]:
        """Count findings by type"""
        counts = {}
        for finding in findings:
            base_type = finding.touchpoint  # Get analyzer name
            counts[base_type] = counts.get(base_type, 0) + 1
        return counts
    
    async def analyze_batch(
        self,
        pages: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple pages in batch
        
        Args:
            pages: List of page data (screenshot, html, url)
            max_concurrent: Max concurrent analyses
            
        Returns:
            List of analysis results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_limit(page_data):
            async with semaphore:
                return await self.analyze_page(
                    page_data['screenshot'],
                    page_data['html'],
                    page_data.get('analyses')
                )
        
        tasks = [analyze_with_limit(page) for page in pages]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def estimate_cost(self, html_length: int, num_analyses: int = 4) -> float:
        """
        Estimate API cost for analysis
        
        Args:
            html_length: Length of HTML content
            num_analyses: Number of analyses to run
            
        Returns:
            Estimated cost in USD
        """
        # Rough estimates based on Claude pricing
        tokens_per_analysis = (html_length // 4) + 2000  # HTML + prompt
        total_tokens = tokens_per_analysis * num_analyses
        
        # Claude Opus pricing (as of 2024)
        input_cost_per_1k = 0.015
        output_cost_per_1k = 0.075
        
        estimated_input = total_tokens / 1000
        estimated_output = 2000 * num_analyses / 1000  # Assume 2k output per analysis
        
        cost = (estimated_input * input_cost_per_1k) + (estimated_output * output_cost_per_1k)
        
        return round(cost, 2)