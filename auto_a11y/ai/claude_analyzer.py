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
from auto_a11y.models import AIFinding, ImpactLevel

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
    
    def _process_findings(self, analysis_type: str, result: Dict[str, Any]) -> List[AIFinding]:
        """
        Process raw analysis results into AIFinding objects
        
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
                    finding = AIFinding(
                        type='visual_heading_not_marked',
                        severity=ImpactLevel.SERIOUS,
                        description=f"Text '{vh.get('text', '')}' appears to be a heading but is not marked up as one",
                        suggested_fix=f"Use <h{vh.get('appears_to_be_level', 2)}> tag for this heading",
                        confidence=0.8
                    )
                    findings.append(finding)
        
        return findings
    
    def _create_finding(
        self,
        analysis_type: str,
        issue: Dict[str, Any],
        full_result: Dict[str, Any]
    ) -> Optional[AIFinding]:
        """
        Create an AIFinding from an issue
        
        Args:
            analysis_type: Type of analysis
            issue: Issue dictionary
            full_result: Complete analysis result
            
        Returns:
            AIFinding object or None
        """
        try:
            # Map issue types to severity levels
            severity_map = {
                'visual_not_marked': ImpactLevel.SERIOUS,
                'wrong_level': ImpactLevel.MODERATE,
                'missing_role': ImpactLevel.CRITICAL,
                'missing_label': ImpactLevel.CRITICAL,
                'no_close': ImpactLevel.SERIOUS,
                'missing_lang': ImpactLevel.CRITICAL,
                'wrong_lang': ImpactLevel.SERIOUS,
                'unmarked_foreign': ImpactLevel.MODERATE,
                'infinite_animation': ImpactLevel.SERIOUS,
                'no_pause_control': ImpactLevel.SERIOUS,
                'no_reduced_motion': ImpactLevel.MODERATE,
                'non_semantic_button': ImpactLevel.SERIOUS,
                'missing_aria': ImpactLevel.SERIOUS,
                'no_focus_indicator': ImpactLevel.CRITICAL
            }
            
            issue_type = issue.get('type', 'unknown')
            severity = severity_map.get(issue_type, ImpactLevel.MODERATE)
            
            finding = AIFinding(
                type=f"{analysis_type}_{issue_type}",
                severity=severity,
                description=issue.get('description', 'AI-detected accessibility issue'),
                suggested_fix=issue.get('fix') or issue.get('suggested_fix'),
                confidence=0.85,  # Default confidence
                related_html=issue.get('element') or issue.get('element_description')
            )
            
            # Add visual location if available
            if 'location' in issue or 'approximate_location' in issue:
                finding.visual_location = {
                    'description': issue.get('location') or issue.get('approximate_location')
                }
            
            return finding
            
        except Exception as e:
            logger.error(f"Failed to create finding: {e}")
            return None
    
    def _generate_summary(self, findings: List[AIFinding]) -> Dict[str, Any]:
        """
        Generate summary of AI findings
        
        Args:
            findings: List of AI findings
            
        Returns:
            Summary dictionary
        """
        critical = sum(1 for f in findings if f.severity == ImpactLevel.CRITICAL)
        serious = sum(1 for f in findings if f.severity == ImpactLevel.SERIOUS)
        moderate = sum(1 for f in findings if f.severity == ImpactLevel.MODERATE)
        minor = sum(1 for f in findings if f.severity == ImpactLevel.MINOR)
        
        return {
            'total_findings': len(findings),
            'by_severity': {
                'critical': critical,
                'serious': serious,
                'moderate': moderate,
                'minor': minor
            },
            'by_type': self._count_by_type(findings),
            'requires_immediate_attention': critical > 0,
            'ai_confidence_avg': sum(f.confidence for f in findings) / len(findings) if findings else 0
        }
    
    def _count_by_type(self, findings: List[AIFinding]) -> Dict[str, int]:
        """Count findings by type"""
        counts = {}
        for finding in findings:
            base_type = finding.type.split('_')[0]  # Get analyzer name
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