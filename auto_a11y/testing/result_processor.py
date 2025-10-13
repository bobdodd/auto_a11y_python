"""
Process and transform JavaScript test results into structured data
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from auto_a11y.models import TestResult, Violation, ImpactLevel
from auto_a11y.reporting.issue_descriptions import get_issue_description, get_wcag_link
from auto_a11y.reporting.issue_descriptions_enhanced import get_detailed_issue_description
from auto_a11y.reporting.wcag_mapper import get_wcag_criteria, enrich_wcag_criteria
from auto_a11y.core.touchpoints import TouchpointMapper

logger = logging.getLogger(__name__)


class ResultProcessor:
    """Processes raw JavaScript test results into structured format"""
    
    # Map error codes to WCAG criteria
    WCAG_MAPPING = {
        # Images
        'ErrNoAlt': ['1.1.1'],
        'ErrEmptyAlt': ['1.1.1'],
        'ErrAltTooLong': ['1.1.1'],
        'ErrRedundantAlt': ['1.1.1'],
        
        # Headings
        'ErrEmptyHeading': ['1.3.1', '2.4.6'],
        'ErrSkippedHeadingLevel': ['1.3.1'],
        'ErrMultipleH1': ['1.3.1'],
        'WarnHeadingInsideDisplayNone': ['1.3.1'],
        'WarnHeadingOver60CharsLong': ['2.4.6'],
        
        # Forms
        'ErrNoLabel': ['1.3.1', '3.3.2', '4.1.2'],
        'ErrEmptyLabel': ['3.3.2'],
        'ErrNoFieldset': ['1.3.1'],
        'ErrMissingRequired': ['3.3.2'],
        'ErrPlaceholderAsLabel': ['3.3.2'],
        
        # Landmarks
        'ErrNoMainLandmark': ['1.3.1', '2.4.1'],
        'ErrMultipleBanners': ['1.3.1'],
        'ErrMultipleContentinfo': ['1.3.1'],
        
        # Color
        'ErrInsufficientContrast': ['1.4.3'],
        'ErrLinkContrast': ['1.4.3'],
        
        # Language
        'ErrNoPageLanguage': ['3.1.1'],
        'ErrInvalidLanguageCode': ['3.1.1'],
        
        # Page Title
        'ErrNoPageTitle': ['2.4.2'],
        'ErrEmptyPageTitle': ['2.4.2'],
        
        # Focus
        'ErrNoFocusIndicator': ['2.4.7'],
        'ErrInvalidTabindex': ['2.4.3'],
    }
    
    # Map error codes to impact levels
    IMPACT_MAPPING = {
        # High - blocks access completely or significant barriers
        'ErrNoAlt': ImpactLevel.HIGH,
        'ErrNoLabel': ImpactLevel.HIGH,
        'ErrNoPageTitle': ImpactLevel.HIGH,
        'ErrNoPageLanguage': ImpactLevel.HIGH,
        'ErrEmptyHeading': ImpactLevel.HIGH,
        'ErrSkippedHeadingLevel': ImpactLevel.HIGH,
        'ErrInsufficientContrast': ImpactLevel.HIGH,
        'ErrNoMainLandmark': ImpactLevel.HIGH,
        'ErrEmptyLabel': ImpactLevel.HIGH,
        
        # Medium - noticeable issues
        'ErrMultipleH1': ImpactLevel.MEDIUM,
        'ErrAltTooLong': ImpactLevel.MEDIUM,
        'ErrPlaceholderAsLabel': ImpactLevel.MEDIUM,
        'ErrInvalidTabindex': ImpactLevel.MEDIUM,
        
        # Low - small issues
        'WarnHeadingOver60CharsLong': ImpactLevel.LOW,
        'ErrRedundantAlt': ImpactLevel.LOW,
        'WarnHeadingInsideDisplayNone': ImpactLevel.LOW,
    }
    
    def process_test_results(
        self,
        page_id: str,
        raw_results: Dict[str, Dict[str, Any]],
        screenshot_path: Optional[str] = None,
        duration_ms: int = 0,
        ai_findings: Optional[List[Any]] = None,
        ai_analysis_results: Optional[Dict[str, Any]] = None
    ) -> TestResult:
        """
        Process raw JavaScript test results and AI findings into TestResult model
        
        Args:
            page_id: Page ID
            raw_results: Raw results from JavaScript tests
            screenshot_path: Path to screenshot
            duration_ms: Test duration in milliseconds
            ai_findings: AI-detected accessibility issues
            ai_analysis_results: Raw AI analysis results
            
        Returns:
            Processed TestResult
        """
        violations = []  # _Err issues
        warnings = []    # _Warn issues  
        info = []        # _Info issues
        discovery = []   # _Disco issues
        passes = []
        checks = []  # Track all accessibility checks performed
        
        # Track applicability statistics
        total_applicable_checks = 0
        total_passed_checks = 0
        total_failed_checks = 0
        not_applicable_tests = []
        
        # Initialize AI data if not provided
        if ai_findings is None:
            ai_findings = []
        if ai_analysis_results is None:
            ai_analysis_results = {}
        
        # Process each test's results
        for test_name, test_result in raw_results.items():
            if 'error' in test_result and test_result['error']:
                logger.warning(f"Test {test_name} had execution error: {test_result['error']}")
                continue
            
            # Check if this test uses the new structure with applicability
            if 'applicable' in test_result:
                # New structure with applicability tracking
                if not test_result['applicable']:
                    # Test was not applicable
                    not_applicable_tests.append({
                        'test_name': test_result.get('test_name', test_name),
                        'reason': test_result.get('not_applicable_reason', 'No applicable elements')
                    })
                    logger.debug(f"Test {test_name} not applicable: {test_result.get('not_applicable_reason')}")
                else:
                    # Test was applicable - process results
                    if 'elements_tested' in test_result:
                        total_applicable_checks += test_result['elements_tested']
                    if 'elements_passed' in test_result:
                        total_passed_checks += test_result['elements_passed']
                    if 'elements_failed' in test_result:
                        total_failed_checks += test_result['elements_failed']
                    
                    # Store check information
                    if 'checks' in test_result:
                        for check in test_result['checks']:
                            # Keep original check data for now (will be replaced by summary later)
                            check['test_name'] = test_name.title()
                            checks.append(check)
            
            # Process errors and warnings (works with both old and new structure)
            all_issues = []
            if 'errors' in test_result and test_result['errors']:
                all_issues.extend(test_result['errors'])
            if 'warnings' in test_result and test_result['warnings']:
                all_issues.extend(test_result['warnings'])
            
            # Categorize issues based on their ID pattern
            for issue in all_issues:
                processed = self._process_violation(issue, test_name, 'unknown')
                if processed:
                    # Categorize based on ID pattern or type field
                    issue_type = issue.get('type', '')
                    
                    # First check explicit type field
                    if issue_type == 'disco':
                        discovery.append(processed)
                        # Don't count discovery items in pass/fail
                        continue
                    elif issue_type == 'info':
                        info.append(processed)
                        # Don't count info items in pass/fail
                        continue
                    
                    # Then check ID pattern
                    if '_Err' in processed.id or issue_type == 'err':
                        violations.append(processed)
                    elif '_Warn' in processed.id or issue_type == 'warn':
                        warnings.append(processed)
                    elif '_Info' in processed.id:
                        info.append(processed)
                        # Don't count in pass/fail
                    elif '_Disco' in processed.id:
                        discovery.append(processed)
                        # Don't count in pass/fail
                    else:
                        # Default to warnings if pattern not recognized
                        warnings.append(processed)
            
            # Process passes
            if 'passes' in test_result and test_result['passes']:
                passes.extend(test_result['passes'])
        
        # NOTE: We'll replace the checks list with a touchpoint summary later
        # Process AI findings
        if ai_findings:
            # Group AI findings by analysis type
            ai_checks_by_type = {}
            
            for finding in ai_findings:
                # Enhance AI violation with catalog descriptions
                enhanced_finding = self.enhance_ai_violation(finding)
                
                # Categorize based on ID prefix
                if enhanced_finding.id.startswith('AI_Err'):
                    violations.append(enhanced_finding)
                elif enhanced_finding.id.startswith('AI_Warn'):
                    warnings.append(enhanced_finding)
                elif enhanced_finding.id.startswith('AI_Info'):
                    info.append(enhanced_finding)
                else:
                    warnings.append(enhanced_finding)
                
                # Track for check statistics
                analysis_type = finding.metadata.get('ai_analysis_type', 'AI Analysis')
                if analysis_type not in ai_checks_by_type:
                    ai_checks_by_type[analysis_type] = {
                        'passed': 0,
                        'failed': 0,
                        'total': 0
                    }
                
                # Count as failed check (since it's an issue)
                ai_checks_by_type[analysis_type]['failed'] += 1
                ai_checks_by_type[analysis_type]['total'] += 1
                total_failed_checks += 1
                total_applicable_checks += 1
            
            # Add AI checks to the checks list
            for analysis_type, stats in ai_checks_by_type.items():
                # Map AI analysis types directly to touchpoint IDs
                from auto_a11y.core.touchpoints import TouchpointID
                ai_to_touchpoint_map = {
                    'headings': TouchpointID.HEADINGS,
                    'reading_order': TouchpointID.FOCUS_MANAGEMENT,  # Reading order relates to focus/tab order
                    'modals': TouchpointID.DIALOGS,
                    'language': TouchpointID.LANGUAGE,
                    'animations': TouchpointID.ANIMATION,
                    'interactive': TouchpointID.EVENT_HANDLING  # Interactive elements need proper event handling
                }
                
                # Get the touchpoint for this AI analysis
                touchpoint_id = ai_to_touchpoint_map.get(analysis_type)
                
                if touchpoint_id:
                    from auto_a11y.core.touchpoints import get_touchpoint
                    touchpoint = get_touchpoint(touchpoint_id)
                    test_name = touchpoint.name if touchpoint else analysis_type.title()
                else:
                    # If no touchpoint found, use the analysis type
                    test_name = analysis_type.title()
                
                # Map analysis types to readable descriptions
                check_descriptions = {
                    'headings': 'Visual heading structure analysis',
                    'reading_order': 'Reading order consistency check',
                    'modals': 'Modal dialog accessibility check',
                    'language': 'Language declaration check',
                    'animations': 'Animation and motion check',
                    'interactive': 'Interactive element keyboard accessibility'
                }
                
                checks.append({
                    'test_name': test_name,
                    'description': check_descriptions.get(analysis_type, f'{analysis_type} analysis'),
                    'wcag': self._get_ai_wcag_criteria(analysis_type),
                    'total': stats['total'],
                    'passed': stats['passed'],
                    'failed': stats['failed']
                })
            
            # If AI analysis ran but found no issues, add a passing check
            if ai_analysis_results and not ai_findings:
                for analysis_type in ai_analysis_results.keys():
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
                    
                    # Get the touchpoint for this AI analysis
                    touchpoint_id = ai_to_touchpoint_map.get(analysis_type)
                    
                    if touchpoint_id:
                        from auto_a11y.core.touchpoints import get_touchpoint
                        touchpoint = get_touchpoint(touchpoint_id)
                        test_name = touchpoint.name if touchpoint else analysis_type.title()
                    else:
                        test_name = analysis_type.title()
                    
                    check_descriptions = {
                        'headings': 'Visual heading structure analysis',
                        'reading_order': 'Reading order consistency check',
                        'modals': 'Modal dialog accessibility check',
                        'language': 'Language declaration check',
                        'animations': 'Animation and motion check',
                        'interactive': 'Interactive element keyboard accessibility'
                    }
                    
                    checks.append({
                        'test_name': test_name,
                        'description': check_descriptions.get(analysis_type, f'{analysis_type} analysis'),
                        'wcag': self._get_ai_wcag_criteria(analysis_type),
                        'total': 1,
                        'passed': 1,
                        'failed': 0
                    })
                    total_passed_checks += 1
                    total_applicable_checks += 1
        
        # Sort all issue lists by touchpoint first, then by ID/title
        sorted_violations = sorted(violations, key=lambda x: (x.touchpoint, x.id))
        sorted_warnings = sorted(warnings, key=lambda x: (x.touchpoint, x.id))
        sorted_info = sorted(info, key=lambda x: (x.touchpoint, x.id))
        sorted_discovery = sorted(discovery, key=lambda x: (x.touchpoint, x.id))
        
        # Create touchpoint summary for Test Check Details
        # This aggregates all issues by touchpoint to create a summary that matches Latest Test Results
        touchpoint_summary = {}
        all_issues = violations + warnings + info + discovery
        
        # Count issues by touchpoint
        for issue in all_issues:
            touchpoint = issue.touchpoint
            if touchpoint not in touchpoint_summary:
                touchpoint_summary[touchpoint] = {
                    'test_name': touchpoint.replace('_', ' ').title(),
                    'description': f'Accessibility checks for {touchpoint.replace("_", " ").lower()}',
                    'wcag': set(),
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'violations': 0,
                    'warnings': 0,
                    'info': 0,
                    'discovery': 0
                }
            
            # Count issue types
            if issue in violations:
                touchpoint_summary[touchpoint]['violations'] += 1
                touchpoint_summary[touchpoint]['failed'] += 1
            elif issue in warnings:
                touchpoint_summary[touchpoint]['warnings'] += 1
                touchpoint_summary[touchpoint]['failed'] += 1
            elif issue in info:
                touchpoint_summary[touchpoint]['info'] += 1
                # Info items don't count as failures
            elif issue in discovery:
                touchpoint_summary[touchpoint]['discovery'] += 1
                # Discovery items don't count as failures
            
            touchpoint_summary[touchpoint]['total'] += 1
            
            # Collect WCAG criteria
            if hasattr(issue, 'wcag_criteria') and issue.wcag_criteria:
                for criterion in issue.wcag_criteria:
                    touchpoint_summary[touchpoint]['wcag'].add(criterion)
        
        # Replace the checks list with our touchpoint summary
        # This ensures Test Check Details shows a summary of Latest Test Results
        checks = []  # Clear any previous checks
        for touchpoint_data in touchpoint_summary.values():
            # Convert WCAG set to sorted list
            touchpoint_data['wcag'] = sorted(list(touchpoint_data['wcag']))
            
            # For the summary, total = number of issues found
            # failed = violations + warnings
            # passed = 0 (we're showing issues, not elements tested)
            
            checks.append(touchpoint_data)
        
        # Sort checks by touchpoint name
        sorted_checks = sorted(checks, key=lambda x: x.get('test_name', ''))
        
        # Create test result
        test_result = TestResult(
            page_id=page_id,
            test_date=datetime.now(),
            duration_ms=duration_ms,
            violations=sorted_violations,
            warnings=sorted_warnings,
            info=sorted_info,
            discovery=sorted_discovery,
            passes=passes,
            screenshot_path=screenshot_path,
            js_test_results=raw_results,
            metadata={
                'test_count': len(raw_results),
                'tests_run': list(raw_results.keys()),
                'applicable_checks': total_applicable_checks,
                'passed_checks': total_passed_checks,
                'failed_checks': total_failed_checks,
                'not_applicable_tests': not_applicable_tests,
                'checks': sorted_checks
            }
        )
        
        return test_result
    
    def _process_violation(
        self,
        violation_data: Dict[str, Any],
        source_test: str,
        violation_type: str
    ) -> Optional[Violation]:
        """
        Process individual violation into Violation model
        
        Args:
            violation_data: Raw violation data from JavaScript
            source_test: Name of test that found violation
            violation_type: 'error' or 'warning'
            
        Returns:
            Violation object or None
        """
        try:
            error_code = violation_data.get('err', 'UnknownError')
            violation_id = f"{source_test}_{error_code}"
            
            # Try to get enhanced detailed description using actual metadata
            # Pass violation_id (with test prefix) and the full violation data
            logger.debug(f"Getting description for {violation_id} with metadata: {violation_data}")
            enhanced_desc = get_detailed_issue_description(violation_id, violation_data)
            
            if enhanced_desc:
                # Use enhanced description with context-specific details
                impact_str = enhanced_desc.get('impact', 'Medium')
                impact = ImpactLevel.HIGH if impact_str == 'High' else (
                    ImpactLevel.MEDIUM if impact_str == 'Medium' else ImpactLevel.LOW
                )
                description = enhanced_desc.get('what', '')
                # Keep full WCAG descriptions, not just numbers
                wcag_full = enhanced_desc.get('wcag', [])
                # Also extract just numbers for backward compatibility
                wcag_criteria = [c.split()[0] for c in wcag_full] if wcag_full else []
                help_url = get_wcag_link(wcag_criteria[0]) if wcag_criteria else self._get_help_url(error_code)
                failure_summary = enhanced_desc.get('remediation', '')
                
                # Store all enhanced details in metadata
                # The enhanced_desc already has placeholders replaced with actual values
                #
                # IMPORTANT: For threshold violations, the original description from the test
                # contains actual measured values (e.g., "outline is 1.5px" vs "outline is too small").
                # We prefer the original description as the title when it contains specific measurements.
                original_desc = violation_data.get('description', '')
                use_original_as_title = any(pattern in original_desc for pattern in [
                    '(', 'px', ':1', 'alpha=', '°', '%'  # Patterns indicating measured values
                ])

                metadata = {
                    'title': original_desc if use_original_as_title else enhanced_desc.get('title', ''),
                    'what': original_desc if use_original_as_title else enhanced_desc.get('what', ''),
                    'why': enhanced_desc.get('why', ''),
                    'who': enhanced_desc.get('who', ''),
                    'impact_detail': enhanced_desc.get('impact', ''),
                    'wcag_full': wcag_full,
                    'full_remediation': enhanced_desc.get('remediation', ''),
                    **violation_data  # Include all original metadata from JS tests
                }
            else:
                # Try original description mapping
                detailed_desc = get_issue_description(violation_id)
                
                if detailed_desc:
                    # Use detailed description if available
                    impact = ImpactLevel[detailed_desc.impact.name]
                    description = detailed_desc.what
                    wcag_criteria = detailed_desc.wcag
                    help_url = get_wcag_link(wcag_criteria[0]) if wcag_criteria else self._get_help_url(error_code)
                    failure_summary = detailed_desc.remediation
                    
                    # Store additional details in metadata
                    metadata = {
                        'title': detailed_desc.title,
                        'why': detailed_desc.why,
                        'who': detailed_desc.who,
                        'full_remediation': detailed_desc.remediation
                    }
                else:
                    # Fall back to original mapping
                    if error_code in self.IMPACT_MAPPING:
                        impact = self.IMPACT_MAPPING[error_code]
                    elif violation_type == 'warning':
                        impact = ImpactLevel.LOW
                    else:
                        impact = ImpactLevel.MEDIUM
                    
                    # Try to get WCAG from mapper first, then fallback to hardcoded mapping
                    wcag_criteria = get_wcag_criteria(error_code)
                    if not wcag_criteria:
                        wcag_criteria = self.WCAG_MAPPING.get(error_code, [])
                    # Enrich the criteria with full names
                    wcag_full = enrich_wcag_criteria(wcag_criteria) if wcag_criteria else []
                    description = self._get_error_description(error_code)
                    help_url = self._get_help_url(error_code)
                    failure_summary = self._get_failure_summary(error_code, violation_data)
                    # Include original violation data in metadata
                    metadata = {
                        'wcag_full': wcag_full,
                        **violation_data
                    }
            
            # Map category to touchpoint
            old_category = violation_data.get('cat', source_test)
            
            # First try to map by error code
            touchpoint_id = TouchpointMapper.get_touchpoint_for_error_code(error_code)
            if not touchpoint_id:
                # Fall back to category mapping
                touchpoint_id = TouchpointMapper.get_touchpoint_for_category(old_category)
            
            touchpoint_value = touchpoint_id.value if touchpoint_id else old_category
            
            # Create violation
            violation = Violation(
                id=violation_id,
                impact=impact,
                touchpoint=touchpoint_value,
                description=description,
                help_url=help_url,
                xpath=violation_data.get('xpath'),
                element=violation_data.get('element'),
                html=violation_data.get('html'),
                failure_summary=failure_summary,
                wcag_criteria=wcag_criteria
            )
            
            # Always add metadata (may be enriched later in pages.py)
            violation.metadata = metadata

            return violation
            
        except Exception as e:
            logger.error(f"Failed to process violation: {e}")
            return None
    
    def _get_error_description(self, error_code: str) -> str:
        """
        Get human-readable description for error code
        
        Args:
            error_code: Error code
            
        Returns:
            Description string
        """
        descriptions = {
            'ErrNoAlt': 'Image is missing alt text',
            'ErrEmptyAlt': 'Image alt text is empty',
            'ErrAltTooLong': 'Image alt text is too long (over 125 characters)',
            'ErrRedundantAlt': 'Image alt text contains redundant words like "image of"',
            'ErrEmptyHeading': 'Heading is empty',
            'ErrSkippedHeadingLevel': 'Heading level is skipped in hierarchy',
            'ErrMultipleH1': 'Multiple H1 elements found on page',
            'ErrNoLabel': 'Form input is missing a label',
            'ErrEmptyLabel': 'Form label is empty',
            'ErrNoFieldset': 'Radio/checkbox group is missing fieldset',
            'ErrNoMainLandmark': 'Page is missing main landmark',
            'ErrInsufficientContrast': 'Text color contrast is insufficient',
            'ErrNoPageLanguage': 'Page is missing language declaration',
            'ErrNoPageTitle': 'Page is missing title element',
            'ErrNoFocusIndicator': 'Element lacks visible focus indicator',
            'ErrInvalidTabindex': 'Invalid tabindex value',
        }
        
        return descriptions.get(error_code, f'Accessibility issue: {error_code}')
    
    def _get_ai_wcag_criteria(self, analysis_type: str) -> List[str]:
        """
        Get WCAG criteria for AI analysis types
        
        Args:
            analysis_type: Type of AI analysis (headings, reading_order, etc.)
            
        Returns:
            List of WCAG criteria
        """
        wcag_map = {
            'headings': ['1.3.1', '2.4.6'],  # Info and Relationships, Headings and Labels
            'reading_order': ['1.3.2', '2.4.3'],  # Meaningful Sequence, Focus Order
            'modals': ['2.1.2', '4.1.2', '2.4.3'],  # No Keyboard Trap, Name/Role/Value, Focus Order
            'language': ['3.1.1', '3.1.2'],  # Language of Page, Language of Parts
            'animations': ['2.2.2', '2.3.1'],  # Pause/Stop/Hide, Three Flashes
            'interactive': ['2.1.1', '4.1.2']  # Keyboard, Name/Role/Value
        }
        return wcag_map.get(analysis_type, ['4.1.2'])  # Default to Name/Role/Value
    
    def enhance_ai_violation(self, violation: Violation) -> Violation:
        """
        Enhance an AI-detected violation with catalog descriptions
        
        Args:
            violation: AI-detected Violation object
            
        Returns:
            Enhanced Violation object
        """
        try:
            # Get enhanced description using the AI issue ID
            enhanced_desc = get_detailed_issue_description(violation.id, violation.metadata)
            
            if enhanced_desc:
                # Update violation with enhanced description
                violation.description = enhanced_desc.get('what', violation.description)
                violation.failure_summary = enhanced_desc.get('remediation', violation.failure_summary)
                
                # Update impact level if provided
                impact_str = enhanced_desc.get('impact', '')
                if impact_str:
                    violation.impact = ImpactLevel.HIGH if impact_str == 'High' else (
                        ImpactLevel.MEDIUM if impact_str == 'Medium' else ImpactLevel.LOW
                    )
                
                # Add WCAG criteria
                wcag_full = enhanced_desc.get('wcag', [])
                violation.wcag_criteria = [c.split()[0] for c in wcag_full] if wcag_full else []
                
                # Enhance metadata with catalog info
                violation.metadata.update({
                    'title': enhanced_desc.get('title', ''),
                    'what': enhanced_desc.get('what', ''),
                    'why': enhanced_desc.get('why', ''),
                    'who': enhanced_desc.get('who', ''),
                    'impact_detail': enhanced_desc.get('impact', ''),
                    'wcag_full': wcag_full,
                    'full_remediation': enhanced_desc.get('remediation', '')
                })
                
                # Add help URL if we have WCAG criteria
                if violation.wcag_criteria:
                    violation.help_url = get_wcag_link(violation.wcag_criteria[0])
            
            return violation
            
        except Exception as e:
            logger.error(f"Failed to enhance AI violation {violation.id}: {e}")
            return violation
    
    def _get_help_url(self, error_code: str) -> str:
        """
        Get help URL for error code
        
        Args:
            error_code: Error code
            
        Returns:
            Help URL
        """
        # Map to WCAG documentation
        wcag_base = "https://www.w3.org/WAI/WCAG21/Understanding/"
        
        wcag_urls = {
            'ErrNoAlt': f"{wcag_base}non-text-content.html",
            'ErrEmptyHeading': f"{wcag_base}headings-and-labels.html",
            'ErrNoLabel': f"{wcag_base}labels-or-instructions.html",
            'ErrInsufficientContrast': f"{wcag_base}contrast-minimum.html",
            'ErrNoPageLanguage': f"{wcag_base}language-of-page.html",
            'ErrNoPageTitle': f"{wcag_base}page-titled.html",
        }
        
        return wcag_urls.get(error_code, "https://www.w3.org/WAI/WCAG21/quickref/")
    
    def _get_failure_summary(self, error_code: str, violation_data: Dict[str, Any]) -> str:
        """
        Get failure summary for violation
        
        Args:
            error_code: Error code
            violation_data: Violation data
            
        Returns:
            Failure summary
        """
        element = violation_data.get('element', 'Element')
        
        summaries = {
            'ErrNoAlt': f'{element} must have an alt attribute',
            'ErrEmptyAlt': f'{element} alt attribute must not be empty for informative images',
            'ErrEmptyHeading': f'{element} must contain text content',
            'ErrNoLabel': f'{element} must have an associated label',
            'ErrInsufficientContrast': 'Text must have sufficient color contrast against background',
            'ErrNoPageLanguage': 'HTML element must have a lang attribute',
            'ErrNoPageTitle': 'Page must have a title element',
        }
        
        return summaries.get(error_code, f'Fix the {error_code} issue')
    
    def calculate_score(self, test_result: TestResult) -> Dict[str, Any]:
        """
        Calculate accessibility score from test results using applicability-aware scoring
        
        Args:
            test_result: Test result
            
        Returns:
            Score dictionary with compliance information
        """
        # Get applicability data from metadata if available
        metadata = test_result.metadata if hasattr(test_result, 'metadata') else {}
        applicable_checks = metadata.get('applicable_checks', 0)
        passed_checks = metadata.get('passed_checks', 0)
        failed_checks = metadata.get('failed_checks', 0)
        not_applicable_tests = metadata.get('not_applicable_tests', [])
        
        # Fall back to counting issues if no applicability data
        if applicable_checks == 0:
            # Old method for backward compatibility
            # Only count violations and warnings, NOT info or discovery
            total_issues = len(test_result.violations) + len(test_result.warnings)
            high_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.HIGH)
            medium_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.MEDIUM)
            
            # Simple scoring algorithm
            if high_count > 0:
                score = 0  # Fail if any high impact issues
            elif medium_count > 0:
                score = max(0, 50 - (medium_count * 10))
            elif total_issues > 0:
                score = max(0, 100 - (total_issues * 5))
            else:
                score = 100
                
            return {
                'score': score,
                'grade': self._get_grade(score),
                'high_issues': high_count,
                'medium_issues': medium_count,
                'total_issues': total_issues,
                'passes': len(test_result.passes),
                'method': 'legacy'
            }
        
        # New applicability-aware scoring
        if applicable_checks == 0:
            # No applicable tests - perfect score
            score = 100
            reason = 'No applicable accessibility tests'
        else:
            # Calculate score based on pass rate
            score = round((passed_checks / applicable_checks) * 100, 1)
            reason = f'{passed_checks} of {applicable_checks} checks passed'
        
        # Count issue severities (only violations and warnings count for scoring)
        # Discovery and Info items are excluded from scoring
        high_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.HIGH)
        medium_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.MEDIUM)
        low_count = sum(1 for v in test_result.violations if v.impact == ImpactLevel.LOW)
        
        # Info and Discovery counts for reporting only (not used in score)
        info_count = len(test_result.info) if hasattr(test_result, 'info') else 0
        discovery_count = len(test_result.discovery) if hasattr(test_result, 'discovery') else 0
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'reason': reason,
            'high_issues': high_count,
            'medium_issues': medium_count,
            'low_issues': low_count,
            'total_issues': len(test_result.violations) + len(test_result.warnings),
            'info_count': info_count,  # Not used in scoring
            'discovery_count': discovery_count,  # Not used in scoring
            'passes': len(test_result.passes),
            'applicable_checks': applicable_checks,
            'passed_checks': passed_checks,
            'failed_checks': failed_checks,
            'not_applicable_count': len(not_applicable_tests),
            'not_applicable_tests': not_applicable_tests,
            'method': 'applicability-aware'
        }
    
    def _get_grade(self, score: int) -> str:
        """Get letter grade from score"""
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
    
