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
    InteractiveAnalyzer
)
from auto_a11y.models import Violation, ImpactLevel

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """Main Claude AI analyzer for comprehensive accessibility analysis"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """
        Initialize Claude analyzer
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        # Initialize client
        config = ClaudeConfig(api_key=api_key, model=model)
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
        analyses: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run AI analyses on a web page
        
        Args:
            screenshot: Page screenshot bytes
            html: Page HTML content
            analyses: List of analyses to run (default: all)
            
        Returns:
            Combined analysis results
        """
        if analyses is None:
            analyses = ['headings', 'reading_order', 'language', 'interactive']
        
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
            finding = self._create_finding(analysis_type, issue, result)
            if finding:
                findings.append(finding)
        
        # Special processing for specific analyzers
        if analysis_type == 'headings' and 'visual_headings' in result:
            # Check for visual headings not in HTML
            visual = result.get('visual_headings', [])
            html_headings = result.get('html_headings', [])
            html_texts = [h.get('text', '').lower() for h in html_headings]
            
            for vh in visual:
                if vh.get('text', '').lower() not in html_texts:
                    violation = Violation(
                        id='AI_ErrVisualHeadingNotMarked',
                        impact=ImpactLevel.HIGH,
                        category='headings',
                        description=f"Text '{vh.get('text', '')}' appears to be a heading but is not marked up as one",
                        failure_summary=f"Use <h{vh.get('appears_to_be_level', 2)}> tag for this heading",
                        metadata={
                            'ai_detected': True,
                            'ai_confidence': 0.8,
                            'ai_analysis_type': 'headings',
                            'visual_text': vh.get('text', ''),
                            'suggested_level': vh.get('appears_to_be_level', 2)
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
        Create a Violation from an AI-detected issue
        
        Args:
            analysis_type: Type of analysis
            issue: Issue dictionary
            full_result: Complete analysis result
            
        Returns:
            Violation object or None
        """
        try:
            # Map issue types to AI issue codes and impact levels
            issue_map = {
                'visual_not_marked': ('AI_ErrVisualHeadingNotMarked', ImpactLevel.HIGH),
                'wrong_level': ('AI_ErrHeadingLevelMismatch', ImpactLevel.MEDIUM),
                'reading_order': ('AI_ErrReadingOrderMismatch', ImpactLevel.HIGH),
                'modal_issue': ('AI_WarnModalAccessibility', ImpactLevel.HIGH),
                'missing_lang': ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM),
                'wrong_lang': ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM),
                'unmarked_foreign': ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM),
                'animation_issue': ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM),
                'infinite_animation': ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM),
                'no_pause_control': ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM),
                'interactive_issue': ('AI_ErrInteractiveElementIssue', ImpactLevel.HIGH),
                'non_semantic_button': ('AI_ErrInteractiveElementIssue', ImpactLevel.HIGH),
                'missing_aria': ('AI_ErrInteractiveElementIssue', ImpactLevel.HIGH),
                'visual_cue': ('AI_InfoVisualCue', ImpactLevel.LOW)
            }
            
            issue_type = issue.get('type', 'unknown')
            issue_code, impact = issue_map.get(issue_type, ('AI_ErrInteractiveElementIssue', ImpactLevel.MEDIUM))
            
            # Build metadata with AI-specific information
            metadata = {
                'ai_detected': True,
                'ai_confidence': 0.85,
                'ai_analysis_type': analysis_type
            }
            
            # Add issue-specific metadata
            if 'current_level' in issue:
                metadata['current_level'] = issue['current_level']
            if 'suggested_level' in issue:
                metadata['suggested_level'] = issue['suggested_level']
            if 'visual_text' in issue:
                metadata['visual_text'] = issue['visual_text']
            if 'heading_text' in issue:
                metadata['heading_text'] = issue['heading_text']
            
            violation = Violation(
                id=issue_code,
                impact=impact,
                category=analysis_type,
                description=issue.get('description', 'AI-detected accessibility issue'),
                element=issue.get('element') or issue.get('element_description'),
                html=issue.get('related_html'),
                failure_summary=issue.get('fix') or issue.get('suggested_fix'),
                metadata=metadata
            )
            
            # Add visual location if available
            if 'location' in issue or 'approximate_location' in issue:
                violation.metadata['visual_location'] = issue.get('location') or issue.get('approximate_location')
            
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
            base_type = finding.category  # Get analyzer name
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