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
        # Get model from config if not provided
        if model is None:
            try:
                from config import config as app_config
                model = getattr(app_config, 'CLAUDE_MODEL', 'claude-3-opus-20240229')
                logger.info(f"Using CLAUDE_MODEL from config: {model}")
            except Exception as e:
                model = 'claude-3-opus-20240229'
                logger.warning(f"Could not get CLAUDE_MODEL from config, using default: {model}")
        
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
        Create a Violation from an AI-detected issue
        
        Args:
            analysis_type: Type of analysis
            issue: Issue dictionary
            full_result: Complete analysis result
            
        Returns:
            Violation object or None
        """
        try:
            # Get more specific issue code based on the actual failure
            issue_code, impact = self._determine_specific_issue_code(analysis_type, issue)
            
            if not issue_code:
                # Fall back to generic code if we can't determine specific issue
                issue_code = 'AI_ErrInteractiveElementIssue'
                impact = ImpactLevel.MEDIUM
            
            # Build metadata with AI-specific information
            metadata = {
                'ai_detected': True,
                'ai_confidence': 0.85,
                'ai_analysis_type': analysis_type
            }
            
            # Add metadata keys that match template placeholders
            # For buttons/interactive elements
            metadata['element_tag'] = issue.get('element_tag') or issue.get('tag', 'div')
            
            # Get actual element text, not the issue description
            # element_text should be the visible text IN the element, not a description ABOUT it
            element_text = issue.get('element_text', '')
            
            # Clean up element_text - remove None, null, or description-like text
            if element_text:
                element_text = str(element_text).strip()
                
                # Check if this looks like a description rather than actual element text
                # Descriptions tend to be long and contain certain keywords
                description_keywords = ['lacks', 'contains', 'should', 'does not', 'implementation', 
                                      'likely', 'appears', 'missing', 'button uses', 'uses div']
                
                if (len(element_text) > 100 or 
                    any(word in element_text.lower() for word in description_keywords) or
                    element_text.lower() in ['none', 'null', 'undefined']):
                    # This is probably a description or placeholder, not actual text
                    # Try alternatives
                    element_text = issue.get('text', issue.get('visual_text', ''))
                    if not element_text or element_text.lower() in ['none', 'null', 'undefined']:
                        element_text = ''  # No actual text found
            else:
                element_text = ''
            
            metadata['element_text'] = element_text
            
            # For headings
            metadata['visual_text'] = issue.get('visual_text', issue.get('text', ''))
            metadata['heading_text'] = issue.get('heading_text', issue.get('text', ''))
            
            # Add issue-specific metadata
            if 'current_level' in issue:
                metadata['current_level'] = issue['current_level']
            if 'suggested_level' in issue:
                metadata['suggested_level'] = issue['suggested_level']
            if 'element_class' in issue:
                metadata['element_class'] = issue['element_class']
            if 'element_id' in issue:
                metadata['element_id'] = issue['element_id']
            if 'approximate_location' in issue:
                metadata['visual_location'] = issue['approximate_location']
            
            # Additional metadata for specific issue types
            metadata['heading_level'] = issue.get('level', issue.get('heading_level', ''))
            metadata['next_level'] = issue.get('next_level', '')
            
            # Generate xpath - always try to generate something
            xpath = None
            
            # Get element info from various possible fields
            element_tag = issue.get('element_tag') or issue.get('tag') or issue.get('element')
            element_id = issue.get('element_id')
            element_class = issue.get('element_class')
            
            # Clean up None/null values
            if element_id and str(element_id).lower() in ['none', 'null', 'undefined', '']:
                element_id = None
            if element_class and str(element_class).lower() in ['none', 'null', 'undefined', '']:
                element_class = None
            if element_tag and str(element_tag).lower() in ['none', 'null', 'undefined', '']:
                element_tag = None
                
            # Try to infer element type from issue type if not provided
            if not element_tag:
                issue_type = issue.get('type', '')
                if 'modal' in issue_type or 'dialog' in issue_type:
                    element_tag = 'div'  # Most modals are divs
                elif 'button' in issue_type:
                    element_tag = 'button'
                elif 'link' in issue_type:
                    element_tag = 'a'
                elif 'heading' in issue_type:
                    element_tag = 'h2'  # Default heading level
                elif 'form' in issue_type or 'input' in issue_type:
                    element_tag = 'input'
                else:
                    # Default to div for unknown elements
                    element_tag = 'div'
            
            # Get element index if provided
            element_index = issue.get('element_index')
            if element_index and str(element_index).lower() in ['none', 'null', 'undefined', '']:
                element_index = None
            elif element_index:
                try:
                    element_index = int(element_index)
                except (ValueError, TypeError):
                    element_index = None
            
            # Generate XPath without text to avoid duplicates
            # Always generate something, even if it's generic
            xpath = generate_xpath(element_tag, element_id, element_class, 
                                 element_text=None, element_index=element_index, use_text=False)
            
            # Clean up description to avoid formatting issues
            description = issue.get('description', 'AI-detected accessibility issue')
            if description:
                # Remove any stray quotes or problematic characters
                description = description.replace('""', '"').replace("''", "'")
                # Ensure quotes are balanced
                if description.count('"') % 2 != 0:
                    description = description.replace('"', "'")
            
            # Get element descriptor
            element = issue.get('element_tag') or issue.get('element') or issue.get('element_description', '')
            if element and str(element).lower() in ['none', 'null', 'various']:
                element = issue.get('element_tag', 'element')
            
            # Map AI analysis types directly to touchpoint IDs
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
                description=description,
                element=element,
                html=issue.get('element_html') or issue.get('related_html'),
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
    
    def _determine_specific_issue_code(
        self,
        analysis_type: str,
        issue: Dict[str, Any]
    ) -> tuple[Optional[str], Optional[ImpactLevel]]:
        """
        Determine the specific AI issue code based on the analysis type and issue details
        
        Args:
            analysis_type: Type of analysis performed
            issue: Issue dictionary with details
            
        Returns:
            Tuple of (issue_code, impact_level)
        """
        issue_type = issue.get('type', '')
        description = issue.get('description', '').lower()
        element = issue.get('element_tag', '').lower()
        
        # Interactive element issues - most specific matching
        if analysis_type == 'interactive':
            # Check for specific interactive patterns
            if 'button' in description or 'click' in description:
                if 'div' in element or 'span' in element:
                    return ('AI_ErrNonSemanticButton', ImpactLevel.HIGH)
                elif 'keyboard' not in description and 'onclick' in description:
                    return ('AI_ErrClickableWithoutKeyboard', ImpactLevel.HIGH)
            
            if 'toggle' in description or 'expand' in description or 'collapse' in description:
                if 'aria-expanded' not in description:
                    return ('AI_ErrToggleWithoutState', ImpactLevel.HIGH)
            
            if 'menu' in description or 'navigation' in description:
                if 'aria' not in description:
                    return ('AI_ErrMenuWithoutARIA', ImpactLevel.HIGH)
            
            if 'tab' in description:
                if 'aria-selected' not in description and 'role' not in description:
                    return ('AI_ErrTabsWithoutARIA', ImpactLevel.HIGH)
            
            if 'accordion' in description:
                return ('AI_ErrAccordionWithoutARIA', ImpactLevel.HIGH)
            
            if 'carousel' in description or 'slider' in description:
                return ('AI_ErrCarouselWithoutARIA', ImpactLevel.HIGH)
            
            if 'tooltip' in description:
                return ('AI_WarnTooltipIssue', ImpactLevel.MEDIUM)
            
            if 'dropdown' in description:
                return ('AI_ErrDropdownWithoutARIA', ImpactLevel.HIGH)
            
            if 'dialog' in description or 'modal' in description:
                return ('AI_ErrDialogWithoutARIA', ImpactLevel.HIGH)
            
            # Generic interactive issue fallback
            return ('AI_ErrInteractiveElementIssue', ImpactLevel.HIGH)
        
        # Heading issues
        elif analysis_type == 'headings':
            if issue_type == 'visual_not_marked':
                return ('AI_ErrVisualHeadingNotMarked', ImpactLevel.HIGH)
            elif issue_type == 'wrong_level':
                return ('AI_ErrHeadingLevelMismatch', ImpactLevel.MEDIUM)
            elif 'empty' in description:
                return ('AI_ErrEmptyHeading', ImpactLevel.HIGH)
            elif 'skip' in description:
                return ('AI_ErrSkippedHeading', ImpactLevel.HIGH)
        
        # Reading order issues
        elif analysis_type == 'reading_order':
            return ('AI_ErrReadingOrderMismatch', ImpactLevel.HIGH)
        
        # Modal/Dialog issues
        elif analysis_type == 'modals':
            if 'focus' in description:
                return ('AI_ErrModalFocusTrap', ImpactLevel.HIGH)
            else:
                return ('AI_ErrDialogWithoutARIA', ImpactLevel.HIGH)
        
        # Language issues
        elif analysis_type == 'language':
            if issue_type in ['missing_lang', 'wrong_lang', 'unmarked_foreign']:
                return ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM)
        
        # Animation issues
        elif analysis_type == 'animations':
            if 'infinite' in description or 'pause' in description:
                return ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM)
        
        # Default mapping for unrecognized patterns
        issue_map = {
            'visual_not_marked': ('AI_ErrVisualHeadingNotMarked', ImpactLevel.HIGH),
            'wrong_level': ('AI_ErrHeadingLevelMismatch', ImpactLevel.MEDIUM),
            'reading_order': ('AI_ErrReadingOrderMismatch', ImpactLevel.HIGH),
            'modal_issue': ('AI_ErrDialogWithoutARIA', ImpactLevel.HIGH),
            'missing_lang': ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM),
            'wrong_lang': ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM),
            'unmarked_foreign': ('AI_WarnMixedLanguage', ImpactLevel.MEDIUM),
            'animation_issue': ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM),
            'infinite_animation': ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM),
            'no_pause_control': ('AI_WarnProblematicAnimation', ImpactLevel.MEDIUM),
            'interactive_issue': ('AI_ErrInteractiveElementIssue', ImpactLevel.HIGH),
            'non_semantic_button': ('AI_ErrNonSemanticButton', ImpactLevel.HIGH),
            'missing_aria': ('AI_ErrInteractiveElementIssue', ImpactLevel.HIGH),
            'visual_cue': ('AI_InfoVisualCue', ImpactLevel.LOW)
        }
        
        return issue_map.get(issue_type, (None, None))
    
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