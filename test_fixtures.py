#!/usr/bin/env python3
"""
Automated Testing Script for Accessibility Fixtures

This script tests all HTML fixtures in the Fixtures folder to ensure
that the accessibility testing tool correctly identifies the issues
that each fixture is designed to demonstrate.
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import uuid
import time

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from auto_a11y.core import Database
from config import Config
from auto_a11y.models import Website, Page, PageStatus, Project, ProjectStatus
from auto_a11y.core.website_manager import WebsiteManager
from auto_a11y.testing.test_runner import TestRunner


class FixtureTestRunner:
    """Runner for testing accessibility fixtures"""

    def __init__(self, fixtures_dir: str = "Fixtures", headless: bool = True):
        self.fixtures_dir = Path(fixtures_dir)
        self.config = Config()

        # Create browser config and apply headless setting
        browser_config = self.config.__dict__.copy()
        browser_config['BROWSER_HEADLESS'] = headless

        self.db = Database(self.config.MONGODB_URI, self.config.DATABASE_NAME)
        self.website_manager = WebsiteManager(self.db, browser_config)
        self.test_runner = TestRunner(self.db, browser_config)
        self.results = []
        self.test_run_id = str(uuid.uuid4())  # Unique ID for this test run

        # Check if AI analysis is available
        self.ai_available = bool(self.config.CLAUDE_API_KEY)
        if not self.ai_available:
            logger.warning("CLAUDE_API_KEY not set - AI_ prefixed tests will be skipped")
        
    def get_all_fixtures(self, category_filter: str = None, type_filter: str = None, code_filter: str = None) -> List[Tuple[Path, str]]:
        """
        Get all HTML fixtures with their expected error codes

        Args:
            category_filter: Only include fixtures from this category (touchpoint folder)
            type_filter: Only include fixtures of this type (Err, Warn, Info, Disco, AI)
            code_filter: Only include fixtures for this specific error code
        """
        fixtures = []

        for html_file in self.fixtures_dir.rglob("*.html"):
            # Apply category filter
            if category_filter and html_file.parent.name != category_filter:
                continue
            # Extract error code from filename
            filename = html_file.stem

            # Skip files that don't follow the naming convention
            # Accept: Err*, Warn*, Info*, Disco*, AI_*, forms_*, or CamelCase issue names
            has_prefix = any(prefix in filename for prefix in ["Err", "Warn", "Info", "Disco", "AI_", "forms_"])
            # Also accept CamelCase names (e.g., VisibleHeadingDoesNotMatchA11yName, RegionLandmarkAccessibleNameIsBlank)
            is_camel_case = filename[0].isupper() and any(c.isupper() for c in filename[1:])

            if not (has_prefix or is_camel_case):
                print(f"⚠️  Skipping {html_file.name} - doesn't follow naming convention")
                continue

            # Extract the base error code (part before the first underscore followed by digits)
            # Examples:
            #   ErrNoAltText_001_violations_basic.html -> ErrNoAltText
            #   AI_ErrAccordionWithoutARIA_002_correct_with_aria.html -> AI_ErrAccordionWithoutARIA
            #   forms_ErrInputMissingLabel_001_violations_basic.html -> forms_ErrInputMissingLabel
            parts = filename.split('_')
            error_code_parts = []
            for i, part in enumerate(parts):
                # Stop when we hit a numeric part (sequence number like 001, 002)
                if part.isdigit():
                    break
                error_code_parts.append(part)

            error_code = '_'.join(error_code_parts) if error_code_parts else filename

            # Apply type filter (Err, Warn, Info, Disco, AI)
            if type_filter:
                if type_filter == 'AI' and not error_code.startswith('AI_'):
                    continue
                elif type_filter != 'AI' and not error_code.startswith(type_filter):
                    continue

            # Apply code filter (exact match on error code)
            if code_filter and error_code != code_filter:
                continue

            fixtures.append((html_file, error_code))

        return sorted(fixtures)
    
    def save_fixture_result_to_db(self, result: Dict) -> str:
        """Save fixture test result to database"""
        try:
            # Create a document for the fixture test result
            doc = {
                "fixture_path": result["fixture"],
                "expected_code": result["expected_code"],
                "found_codes": result["found_codes"],
                "success": result["success"],
                "passed": result["success"],  # Add passed field for fixture validator
                "notes": result["notes"],
                "tested_at": datetime.now(),
                "test_run_id": self.test_run_id
            }

            # Insert into fixture_tests collection
            result_id = self.db.db.fixture_tests.insert_one(doc).inserted_id
            return str(result_id)
        except Exception as e:
            logger.error(f"Failed to save fixture result to database: {e}")
            return None
    
    def extract_fixture_metadata(self, fixture_path: Path) -> Dict:
        """Extract test metadata from fixture HTML file"""
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for test-metadata JSON in the HTML
            import re
            import json
            pattern = r'<script[^>]*id=["\']test-metadata["\'][^>]*>\s*(\{.*?\})\s*</script>'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                metadata_str = match.group(1)
                return json.loads(metadata_str)
        except Exception as e:
            logger.debug(f"Could not extract metadata from {fixture_path}: {e}")

        return {}

    async def test_fixture(self, fixture_path: Path, expected_code: str, fixture_num: int, total_fixtures: int) -> Dict:
        """Test a single fixture file"""
        print(f"\n[{fixture_num}/{total_fixtures}] 📄 Testing: {fixture_path.relative_to(self.fixtures_dir)}")
        print(f"   Expected: {expected_code}")

        # Extract metadata to determine if this is a negative test
        metadata = self.extract_fixture_metadata(fixture_path)
        expected_violation_count = metadata.get('expectedViolationCount', 1)  # Default to 1 (positive test)

        # Discovery items are ALWAYS positive tests (we expect to find them)
        # Negative tests only apply to Err/Warn/Info when expectedViolationCount is 0
        is_discovery = expected_code.startswith('Disco')
        is_negative_test = (expected_violation_count == 0) and not is_discovery

        if is_negative_test:
            print(f"   (Negative test: expecting code NOT to be found)")

        result = {
            "fixture": str(fixture_path.relative_to(self.fixtures_dir)),
            "expected_code": expected_code,
            "found_codes": [],
            "success": False,
            "notes": [],
            "is_negative_test": is_negative_test,
            "expected_violation_count": expected_violation_count
        }

        try:
            # Create a temporary project and website for testing
            project = Project(
                name=f"Fixture Test - {datetime.now().isoformat()}",
                description=f"Testing fixture: {expected_code}",
                status=ProjectStatus.ACTIVE
            )
            project_id = self.db.create_project(project)
            
            # Create website entry
            website = Website(
                project_id=project_id,
                url=f"file://{fixture_path.absolute()}",
                name=f"Fixture: {expected_code}"
            )
            website_id = self.db.create_website(website)
            
            # Create page entry
            page = Page(
                website_id=website_id,
                url=f"file://{fixture_path.absolute()}",
                status=PageStatus.DISCOVERED
            )
            page_id = self.db.create_page(page)

            # Create mock DocumentReference entries if this is a document language test
            # Extract document metadata from test-metadata if present
            if 'documentMetadata' in metadata:
                from auto_a11y.models.document_reference import DocumentReference
                doc_metadata = metadata.get('documentMetadata', {})
                for doc_url, doc_info in doc_metadata.items():
                    # Determine MIME type from URL extension
                    mime_type = 'application/pdf'  # Default to PDF
                    if doc_url.endswith('.doc'):
                        mime_type = 'application/msword'
                    elif doc_url.endswith('.docx'):
                        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    elif doc_url.endswith('.xls'):
                        mime_type = 'application/vnd.ms-excel'
                    elif doc_url.endswith('.xlsx'):
                        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

                    doc_ref = DocumentReference(
                        website_id=website_id,
                        document_url=doc_url,
                        referring_page_url=f"file://{fixture_path.absolute()}",
                        mime_type=mime_type,
                        language=doc_info.get('language'),
                        language_confidence=doc_info.get('confidence', 0.95),
                        is_internal=True,
                        discovered_at=datetime.now()
                    )
                    self.db.add_document_reference(doc_ref)
                print(f"   Created {len(doc_metadata)} mock DocumentReference entries")

            # Run tests on the fixture with timeout
            print("   Running accessibility tests...")

            # Check if this is an AI test and if AI is available
            is_ai_test = expected_code.startswith("AI_")
            if is_ai_test and not self.ai_available:
                print("   ⚠️  Skipping AI_ test (CLAUDE_API_KEY not set)")
                result["notes"].append("Skipped: AI analysis requires CLAUDE_API_KEY environment variable")
                result["success"] = False
                # Still save to DB to track that it was intentionally skipped
                db_id = self.save_fixture_result_to_db(result)
                if db_id:
                    result["db_id"] = db_id
                return result

            # Get the page object
            page_obj = self.db.get_page(page_id)

            try:
                # Determine if AI analysis should run
                run_ai = is_ai_test and self.ai_available

                if run_ai:
                    print("   🤖 Running with AI analysis enabled...")

                # Add a timeout of 30 seconds per fixture (60s for AI tests)
                timeout = 60.0 if run_ai else 30.0
                test_result = await asyncio.wait_for(
                    self.test_runner.test_page(
                        page=page_obj,
                        take_screenshot=False,
                        run_ai_analysis=run_ai
                    ),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                print("   ⏱️  Test timed out after 30 seconds")
                result["notes"].append("Test timed out after 30 seconds")
                test_result = None
            
            if test_result:
                # Collect all violation/warning/info IDs
                all_issues = []

                violations = test_result.get('violations', []) if isinstance(test_result, dict) else (test_result.violations if hasattr(test_result, 'violations') else [])
                for violation in violations:
                        # Extract the error code from the ID (JavaScript returns 'err' field in dicts)
                        issue_id = violation.get('err', '') if isinstance(violation, dict) else (violation.id if hasattr(violation, 'id') else '')
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                warnings = test_result.get('warnings', []) if isinstance(test_result, dict) else (test_result.warnings if hasattr(test_result, 'warnings') else [])
                for warning in warnings:
                        issue_id = warning.get('err', '') if isinstance(warning, dict) else (warning.id if hasattr(warning, 'id') else '')
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                info_items = test_result.get('info', []) if isinstance(test_result, dict) else (test_result.info if hasattr(test_result, 'info') else [])
                for info_item in info_items:
                        issue_id = info_item.get('err', '') if isinstance(info_item, dict) else (info_item.id if hasattr(info_item, 'id') else '')
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                discoveries = test_result.get('discovery', []) if isinstance(test_result, dict) else (test_result.discovery if hasattr(test_result, 'discovery') else [])
                for discovery in discoveries:
                        issue_id = discovery.get('err', '') if isinstance(discovery, dict) else (discovery.id if hasattr(discovery, 'id') else '')
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                result["found_codes"] = list(set(all_issues))  # Remove duplicates

                # Check success based on whether this is a negative test
                code_found = expected_code in result["found_codes"]

                if is_negative_test:
                    # Negative test: success if code is NOT found
                    if not code_found:
                        result["success"] = True
                        print(f"   ✅ Success! Code correctly NOT found: {expected_code}")
                    else:
                        print(f"   ❌ Failed! Code should NOT be found but was: {expected_code}")
                        result["notes"].append(f"Negative test failure: {expected_code} should not be present")
                else:
                    # Positive test: success if code IS found
                    if code_found:
                        result["success"] = True
                        print(f"   ✅ Success! Found expected code: {expected_code}")
                    else:
                        print(f"   ❌ Failed! Expected code not found: {expected_code}")
                        print(f"   Found codes: {', '.join(result['found_codes']) if result['found_codes'] else 'None'}")

                # Note any additional issues found (excluding the expected code)
                extra_codes = [code for code in result["found_codes"] if code != expected_code]
                if extra_codes:
                    result["notes"].append(f"Additional issues found: {', '.join(extra_codes)}")
                    
            else:
                print("   ❌ Failed to run tests on fixture")
                result["notes"].append("Test execution failed")
                
            # Clean up test data
            self.db.delete_project(project_id)
            
        except Exception as e:
            print(f"   ❌ Error testing fixture: {e}")
            result["notes"].append(f"Error: {str(e)}")
        
        # Save result to database
        db_id = self.save_fixture_result_to_db(result)
        if db_id:
            result["db_id"] = db_id
            
        return result
    
    def get_recent_test_runs(self, limit: int = 5):
        """Get recent test runs from database"""
        try:
            runs = list(self.db.db.fixture_test_runs.find().sort("completed_at", -1).limit(limit))
            return runs
        except Exception as e:
            logger.error(f"Failed to get recent test runs: {e}")
            return []
    
    def display_test_history(self):
        """Display test run history"""
        runs = self.get_recent_test_runs(10)
        if not runs:
            print("No previous test runs found.")
            return
        
        print("\n" + "=" * 80)
        print("📊 FIXTURE TEST HISTORY")
        print("=" * 80)
        
        for run in runs:
            completed = run.get("completed_at", datetime.now())
            duration = run.get("duration_seconds", 0)
            total = run.get("total_fixtures", 0)
            passed = run.get("passed", 0)
            failed = run.get("failed", 0)
            success_rate = run.get("success_rate", 0)
            
            print(f"\n🔹 Test Run: {run.get('_id', 'Unknown')}")
            print(f"   Date: {completed.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   Results: {passed}/{total} passed ({success_rate:.1f}%)")
            if failed > 0:
                print(f"   ❌ {failed} fixtures failed")
        
        print("\n" + "=" * 80)
    
    def save_test_run_summary(self, total: int, passed: int, failed: int, duration: float):
        """Save test run summary to database"""
        try:
            summary = {
                "_id": self.test_run_id,
                "started_at": datetime.now() - timedelta(seconds=duration),
                "completed_at": datetime.now(),
                "duration_seconds": duration,
                "total_fixtures": total,
                "passed": passed,
                "failed": failed,
                "success_rate": (passed / total * 100) if total > 0 else 0,
                "fixture_results": [r.get("db_id") for r in self.results if r.get("db_id")]
            }
            
            # Insert into fixture_test_runs collection
            self.db.db.fixture_test_runs.insert_one(summary)
            logger.info(f"Test run summary saved with ID: {self.test_run_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save test run summary: {e}")
            return False
    
    async def run_all_tests(self, category_filter: str = None, type_filter: str = None, code_filter: str = None, limit: int = None) -> None:
        """
        Run tests on all fixtures

        Args:
            category_filter: Only test fixtures from this category
            type_filter: Only test fixtures of this type
            code_filter: Only test fixtures for this error code
            limit: Maximum number of fixtures to test
        """
        start_time = time.time()

        print("=" * 80)
        print("🧪 ACCESSIBILITY FIXTURE TEST SUITE")
        print(f"📝 Test Run ID: {self.test_run_id}")
        print("=" * 80)

        # Display filters if any
        filters_active = []
        if category_filter:
            filters_active.append(f"Category: {category_filter}")
        if type_filter:
            filters_active.append(f"Type: {type_filter}")
        if code_filter:
            filters_active.append(f"Code: {code_filter}")
        if limit:
            filters_active.append(f"Limit: {limit}")

        if filters_active:
            print("\n🔍 ACTIVE FILTERS:")
            for f in filters_active:
                print(f"   • {f}")

        # Display AI analysis status
        if self.ai_available:
            print("🤖 AI Analysis: ENABLED (CLAUDE_API_KEY found)")
        else:
            print("⚠️  AI Analysis: DISABLED (CLAUDE_API_KEY not set)")
            print("   AI_ prefixed tests will be skipped")

        fixtures = self.get_all_fixtures(category_filter, type_filter, code_filter)

        # Apply limit if specified
        if limit and limit < len(fixtures):
            fixtures = fixtures[:limit]

        print(f"\nFound {len(fixtures)} fixtures to test\n")

        # Group fixtures by error code to track pass/fail per code
        fixtures_by_code = {}
        for fixture_path, expected_code in fixtures:
            if expected_code not in fixtures_by_code:
                fixtures_by_code[expected_code] = []
            fixtures_by_code[expected_code].append(fixture_path)

        print(f"Grouped into {len(fixtures_by_code)} unique error codes\n")

        success_count = 0
        failure_count = 0

        # Group fixtures by category
        categories = {}
        for fixture_path, expected_code in fixtures:
            category = fixture_path.parent.name
            if category not in categories:
                categories[category] = []
            categories[category].append((fixture_path, expected_code))

        # Test fixtures by category
        fixture_num = 0
        for category, category_fixtures in sorted(categories.items()):
            print(f"\n{'=' * 60}")
            print(f"📁 Category: {category} ({len(category_fixtures)} fixtures)")
            print(f"{'=' * 60}")

            for fixture_path, expected_code in category_fixtures:
                fixture_num += 1
                result = await self.test_fixture(fixture_path, expected_code, fixture_num, len(fixtures))
                self.results.append(result)

                if result["success"]:
                    success_count += 1
                else:
                    failure_count += 1

                # Show running totals every 10 fixtures
                if fixture_num % 10 == 0:
                    print(f"\n   ➡️  Progress: {fixture_num}/{len(fixtures)} tested | ✅ {success_count} passed | ❌ {failure_count} failed")
        
        # Calculate per-error-code success
        # An error code is only considered passing if ALL its fixtures pass
        error_code_status = {}
        for expected_code, fixture_paths in fixtures_by_code.items():
            # Get results for all fixtures of this error code
            code_results = [r for r in self.results if r["expected_code"] == expected_code]
            all_passed = all(r["success"] for r in code_results)
            error_code_status[expected_code] = {
                "passed": all_passed,
                "total_fixtures": len(fixture_paths),
                "passed_fixtures": sum(1 for r in code_results if r["success"]),
                "results": code_results
            }

        passing_codes = sum(1 for status in error_code_status.values() if status["passed"])
        failing_codes = len(error_code_status) - passing_codes

        # Count skipped AI tests separately
        skipped_ai_count = sum(1 for r in self.results if
                               'AI_' in r['expected_code'] and
                               any('Skipped: AI analysis requires' in str(note) for note in r.get('notes', [])))

        actual_failure_count = failure_count - skipped_ai_count

        # Count AI codes that were skipped
        skipped_ai_codes = set()
        for r in self.results:
            if 'AI_' in r['expected_code'] and any('Skipped: AI analysis requires' in str(note) for note in r.get('notes', [])):
                skipped_ai_codes.add(r['expected_code'])

        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total fixtures tested: {len(fixtures)}")
        print(f"  ✅ Passed: {success_count}")
        if skipped_ai_count > 0:
            print(f"  ⚠️  Skipped (no API key): {skipped_ai_count}")
            print(f"  ❌ Failed: {actual_failure_count}")
        else:
            print(f"  ❌ Failed: {failure_count}")
        print(f"  Success rate: {(success_count/len(fixtures)*100):.1f}%")
        print(f"\nUnique error codes tested: {len(fixtures_by_code)}")
        print(f"  ✅ Passing codes (all fixtures pass): {passing_codes}")
        if len(skipped_ai_codes) > 0:
            print(f"  ⚠️  Skipped AI codes (no API key): {len(skipped_ai_codes)}")
            actual_failing_codes = failing_codes - len(skipped_ai_codes)
            print(f"  ❌ Failing codes (one or more fixtures fail): {actual_failing_codes}")
        else:
            print(f"  ❌ Failing codes (one or more fixtures fail): {failing_codes}")
        print(f"  Code success rate: {(passing_codes/len(fixtures_by_code)*100):.1f}%")

        # List failures by error code (excluding skipped AI codes)
        actual_failing_codes = failing_codes - len(skipped_ai_codes) if len(skipped_ai_codes) > 0 else failing_codes

        if actual_failing_codes > 0:
            print("\n" + "=" * 80)
            print("❌ FAILED ERROR CODES")
            print("=" * 80)
            print("\nNote: An error code is marked as failing if ANY of its fixtures fail.")
            print("All fixtures must pass for the error code to be enabled in production.\n")

            for error_code in sorted(error_code_status.keys()):
                # Skip AI codes that were skipped due to no API key
                if error_code in skipped_ai_codes:
                    continue

                status = error_code_status[error_code]
                if not status["passed"]:
                    print(f"\n❌ {error_code}")
                    print(f"   Fixtures: {status['passed_fixtures']}/{status['total_fixtures']} passed")

                    # Show which specific fixtures failed
                    for result in status["results"]:
                        if not result["success"]:
                            print(f"   📄 {result['fixture']}")
                            print(f"      Expected: {result['expected_code']}")
                            print(f"      Found: {', '.join(result['found_codes']) if result['found_codes'] else 'None'}")
                            if result["notes"]:
                                for note in result["notes"]:
                                    print(f"      Note: {note}")

        # Optionally list skipped AI codes separately
        if len(skipped_ai_codes) > 0:
            print("\n" + "=" * 80)
            print("⚠️  SKIPPED AI ERROR CODES (No API Key)")
            print("=" * 80)
            print(f"\nThese {len(skipped_ai_codes)} AI_ tests require CLAUDE_API_KEY environment variable:")
            for ai_code in sorted(skipped_ai_codes):
                status = error_code_status[ai_code]
                print(f"  • {ai_code} ({status['total_fixtures']} fixture{'s' if status['total_fixtures'] > 1 else ''})")
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Save to database
        db_saved = self.save_test_run_summary(len(fixtures), success_count, failure_count, duration)
        if db_saved:
            print(f"\n💾 Results saved to database with Test Run ID: {self.test_run_id}")
        
        # Also save results to JSON file for reference
        results_file = Path("fixture_test_results.json")
        with open(results_file, "w") as f:
            json.dump({
                "test_run_id": self.test_run_id,
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "summary": {
                    "total": len(fixtures),
                    "passed": success_count,
                    "failed": failure_count,
                    "success_rate": f"{(success_count/len(fixtures)*100):.1f}%"
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"📝 Detailed results also saved to: {results_file}")
        print(f"⏱️  Total test duration: {duration:.1f} seconds")
        
        # Return exit code based on results
        return 0 if failure_count == 0 else 1


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test accessibility fixtures')
    parser.add_argument('--category', help='Test only fixtures in this category (touchpoint folder name)')
    parser.add_argument('--type', choices=['Err', 'Warn', 'Info', 'Disco', 'AI'], help='Test only fixtures of this type (Err, Warn, Info, Disco, AI)')
    parser.add_argument('--code', help='Test only fixtures for this specific error code (e.g., ErrNoAlt)')
    parser.add_argument('--limit', type=int, help='Limit number of fixtures to test')
    parser.add_argument('--fixture', help='Test only a specific fixture file')
    parser.add_argument('--history', action='store_true', help='Show test run history')
    parser.add_argument('--run-id', help='View details of a specific test run')
    parser.add_argument('--visible', action='store_true', help='Run browser in visible mode (not headless)')
    args = parser.parse_args()

    # Create runner with headless mode (default True, unless --visible flag is set)
    runner = FixtureTestRunner(headless=not args.visible)
    
    # Handle history display
    if args.history:
        runner.display_test_history()
        sys.exit(0)
    
    # Handle specific run details
    if args.run_id:
        # Query specific test run from database
        try:
            run = runner.db.db.fixture_test_runs.find_one({"_id": args.run_id})
            if run:
                print(f"\n📋 Test Run Details: {args.run_id}")
                print(f"   Completed: {run.get('completed_at', 'Unknown')}")
                print(f"   Duration: {run.get('duration_seconds', 0):.1f} seconds")
                print(f"   Total Fixtures: {run.get('total_fixtures', 0)}")
                print(f"   Passed: {run.get('passed', 0)}")
                print(f"   Failed: {run.get('failed', 0)}")
                print(f"   Success Rate: {run.get('success_rate', 0):.1f}%")
                
                # Show failed fixtures from this run
                if run.get('failed', 0) > 0:
                    print("\n❌ Failed Fixtures:")
                    failed_results = runner.db.db.fixture_tests.find({
                        "test_run_id": args.run_id,
                        "success": False
                    })
                    for result in failed_results:
                        print(f"   - {result.get('fixture_path', 'Unknown')}")
                        print(f"     Expected: {result.get('expected_code', 'Unknown')}")
                        print(f"     Found: {', '.join(result.get('found_codes', []))}")
            else:
                print(f"❌ Test run not found: {args.run_id}")
        except Exception as e:
            print(f"❌ Error retrieving test run: {e}")
        sys.exit(0)
    
    if args.fixture:
        # Test single fixture
        fixture_path = Path("Fixtures") / args.fixture
        if not fixture_path.exists():
            print(f"❌ Fixture not found: {args.fixture}")
            sys.exit(1)
        
        expected_code = fixture_path.stem
        result = await runner.test_fixture(fixture_path, expected_code, 1, 1)
        
        if result["success"]:
            print("\n✅ Test passed!")
            sys.exit(0)
        else:
            print("\n❌ Test failed!")
            sys.exit(1)
    else:
        # Run normal test suite with optional filters
        exit_code = await runner.run_all_tests(
            category_filter=args.category,
            type_filter=args.type,
            code_filter=args.code,
            limit=args.limit
        )
        sys.exit(exit_code)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())