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
    
    def __init__(self, fixtures_dir: str = "Fixtures"):
        self.fixtures_dir = Path(fixtures_dir)
        self.config = Config()
        self.db = Database(self.config.MONGODB_URI, self.config.DATABASE_NAME)
        self.website_manager = WebsiteManager(self.db, self.config.__dict__)
        self.test_runner = TestRunner(self.db, self.config.__dict__)
        self.results = []
        self.test_run_id = str(uuid.uuid4())  # Unique ID for this test run
        
    def get_all_fixtures(self) -> List[Tuple[Path, str]]:
        """Get all HTML fixtures with their expected error codes"""
        fixtures = []

        for html_file in self.fixtures_dir.rglob("*.html"):
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
    
    async def test_fixture(self, fixture_path: Path, expected_code: str, fixture_num: int, total_fixtures: int) -> Dict:
        """Test a single fixture file"""
        print(f"\n[{fixture_num}/{total_fixtures}] 📄 Testing: {fixture_path.relative_to(self.fixtures_dir)}")
        print(f"   Expected: {expected_code}")
        
        result = {
            "fixture": str(fixture_path.relative_to(self.fixtures_dir)),
            "expected_code": expected_code,
            "found_codes": [],
            "success": False,
            "notes": []
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
            
            # Run tests on the fixture with timeout
            print("   Running accessibility tests...")
            # Get the page object
            page_obj = self.db.get_page(page_id)
            
            try:
                # Add a timeout of 30 seconds per fixture
                test_result = await asyncio.wait_for(
                    self.test_runner.test_page(
                        page=page_obj,
                        take_screenshot=False,
                        run_ai_analysis=expected_code.startswith("AI_")  # Run AI for AI_ prefixed tests
                    ),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                print("   ⏱️  Test timed out after 30 seconds")
                result["notes"].append("Test timed out after 30 seconds")
                test_result = None
            
            if test_result:
                # Collect all violation/warning/info IDs
                all_issues = []
                
                if hasattr(test_result, 'violations'):
                    for violation in test_result.violations:
                        # Extract the error code from the ID
                        issue_id = violation.id if hasattr(violation, 'id') else ''
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                if hasattr(test_result, 'warnings'):
                    for warning in test_result.warnings:
                        issue_id = warning.id if hasattr(warning, 'id') else ''
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                if hasattr(test_result, 'info'):
                    for info_item in test_result.info:
                        issue_id = info_item.id if hasattr(info_item, 'id') else ''
                        if '_' in issue_id:
                            parts = issue_id.split('_')
                            for i, part in enumerate(parts):
                                if part.startswith(('Err', 'Warn', 'Info', 'Disco', 'AI')):
                                    code = '_'.join(parts[i:])
                                    all_issues.append(code)
                                    break
                        else:
                            all_issues.append(issue_id)
                
                if hasattr(test_result, 'discovery'):
                    for discovery in test_result.discovery:
                        issue_id = discovery.id if hasattr(discovery, 'id') else ''
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
                
                # Check if expected code was found
                if expected_code in result["found_codes"]:
                    result["success"] = True
                    print(f"   ✅ Success! Found expected code: {expected_code}")
                else:
                    print(f"   ❌ Failed! Expected code not found: {expected_code}")
                    print(f"   Found codes: {', '.join(result['found_codes']) if result['found_codes'] else 'None'}")
                    
                # Note any additional issues found
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
    
    async def run_all_tests(self) -> None:
        """Run tests on all fixtures"""
        start_time = time.time()

        print("=" * 80)
        print("🧪 ACCESSIBILITY FIXTURE TEST SUITE")
        print(f"📝 Test Run ID: {self.test_run_id}")
        print("=" * 80)

        fixtures = self.get_all_fixtures()
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

        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total fixtures tested: {len(fixtures)}")
        print(f"  ✅ Passed: {success_count}")
        print(f"  ❌ Failed: {failure_count}")
        print(f"  Success rate: {(success_count/len(fixtures)*100):.1f}%")
        print(f"\nUnique error codes tested: {len(fixtures_by_code)}")
        print(f"  ✅ Passing codes (all fixtures pass): {passing_codes}")
        print(f"  ❌ Failing codes (one or more fixtures fail): {failing_codes}")
        print(f"  Code success rate: {(passing_codes/len(fixtures_by_code)*100):.1f}%")

        # List failures by error code
        if failing_codes > 0:
            print("\n" + "=" * 80)
            print("❌ FAILED ERROR CODES")
            print("=" * 80)
            print("\nNote: An error code is marked as failing if ANY of its fixtures fail.")
            print("All fixtures must pass for the error code to be enabled in production.\n")

            for error_code in sorted(error_code_status.keys()):
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
    parser.add_argument('--category', help='Test only fixtures in this category')
    parser.add_argument('--limit', type=int, help='Limit number of fixtures to test')
    parser.add_argument('--fixture', help='Test only a specific fixture file')
    parser.add_argument('--history', action='store_true', help='Show test run history')
    parser.add_argument('--run-id', help='View details of a specific test run')
    args = parser.parse_args()
    
    runner = FixtureTestRunner()
    
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
        if args.category or args.limit:
            print(f"🔍 Running with filters: category={args.category}, limit={args.limit}")
            # TODO: Implement category and limit filters in run_all_tests
        
        exit_code = await runner.run_all_tests()
        sys.exit(exit_code)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())