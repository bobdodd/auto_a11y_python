"""
Database connection and repository management
"""

from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection
from bson import ObjectId
from datetime import datetime
import logging

from auto_a11y.models import (
    Project, Website, Page, TestResult,
    ProjectStatus, ProjectType, PageStatus,
    Recording, RecordingIssue, RecordingType,
    DocumentReference, DiscoveryRun,
    PageSetupScript, ScriptExecutionSession,
    WebsiteUser, ProjectUser
)

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection and operations"""
    
    def __init__(self, connection_uri: str, database_name: str):
        """
        Initialize database connection
        
        Args:
            connection_uri: MongoDB connection URI
            database_name: Name of database to use
        """
        self.client = MongoClient(connection_uri)
        self.db: MongoDatabase = self.client[database_name]
        
        # Collections
        self.projects: Collection = self.db.projects
        self.websites: Collection = self.db.websites
        self.pages: Collection = self.db.pages
        self.test_results: Collection = self.db.test_results
        self.test_result_items: Collection = self.db.test_result_items  # NEW: Detailed violations/warnings
        self.document_references: Collection = self.db.document_references
        self.discovery_runs: Collection = self.db.discovery_runs
        self.issue_documentation_status: Collection = self.db.issue_documentation_status
        self.page_setup_scripts: Collection = self.db.page_setup_scripts  # Page training scripts
        self.script_execution_sessions: Collection = self.db.script_execution_sessions  # Session tracking
        self.website_users: Collection = self.db.website_users  # Test users for authenticated testing (deprecated)
        self.project_users: Collection = self.db.project_users  # Test users at project level
        self.recordings: Collection = self.db.recordings  # Manual audit recordings from Dictaphone
        self.recording_issues: Collection = self.db.recording_issues  # Issues from manual audits
        self.discovered_pages: Collection = self.db.discovered_pages  # Discovered pages for Drupal export

        # Create indexes
        self._create_indexes()
        
        logger.info(f"Connected to MongoDB database: {database_name}")
    
    def _create_indexes(self):
        """Create database indexes for performance"""
        # Projects
        self.projects.create_index("name")
        self.projects.create_index("status")
        self.projects.create_index("project_type")
        self.projects.create_index([("project_type", 1), ("status", 1)])
        
        # Websites
        self.websites.create_index("project_id")
        self.websites.create_index("url")
        
        # Pages
        self.pages.create_index("website_id")
        self.pages.create_index("url")
        self.pages.create_index("status")
        self.pages.create_index([("website_id", 1), ("url", 1)], unique=True)
        
        # Test results
        self.test_results.create_index("page_id")
        self.test_results.create_index("test_date")
        # Multi-state testing indexes
        self.test_results.create_index("session_id")
        self.test_results.create_index([("page_id", 1), ("session_id", 1), ("state_sequence", 1)])
        self.test_results.create_index([("session_id", 1), ("state_sequence", 1)])

        # Test result items (NEW: detailed violations/warnings)
        self.test_result_items.create_index("test_result_id")
        self.test_result_items.create_index([("page_id", 1), ("test_date", -1)])
        self.test_result_items.create_index([("item_type", 1), ("test_result_id", 1)])
        self.test_result_items.create_index([("issue_id", 1), ("test_result_id", 1)])
        self.test_result_items.create_index([("touchpoint", 1), ("test_result_id", 1)])
        # Compound index for common queries
        self.test_result_items.create_index([
            ("test_result_id", 1),
            ("item_type", 1),
            ("issue_id", 1)
        ])

        # Document references
        self.document_references.create_index("website_id")
        self.document_references.create_index("document_url")
        self.document_references.create_index([("website_id", 1), ("document_url", 1)])
        
        # Discovery runs
        self.discovery_runs.create_index("website_id")
        self.discovery_runs.create_index("started_at")
        self.discovery_runs.create_index("is_latest")

        # Issue documentation status
        self.issue_documentation_status.create_index("issue_code", unique=True)
        self.discovery_runs.create_index([("website_id", 1), ("is_latest", 1)])

        # Update pages index for discovery run
        self.pages.create_index("discovery_run_id")
        self.pages.create_index("is_in_latest_discovery")

        # Page setup scripts
        self.page_setup_scripts.create_index("page_id")
        self.page_setup_scripts.create_index("website_id")  # NEW: For website-level scripts
        self.page_setup_scripts.create_index([("website_id", 1), ("scope", 1), ("enabled", 1)])
        self.page_setup_scripts.create_index([("page_id", 1), ("enabled", 1)])
        self.page_setup_scripts.create_index("created_date")

        # Script execution sessions
        self.script_execution_sessions.create_index("session_id", unique=True)
        self.script_execution_sessions.create_index("website_id")
        self.script_execution_sessions.create_index([("website_id", 1), ("started_at", -1)])

        # Website users (test users for authenticated testing)
        self.website_users.create_index("website_id")
        self.website_users.create_index([("website_id", 1), ("username", 1)], unique=True)
        self.website_users.create_index([("website_id", 1), ("enabled", 1)])
        self.website_users.create_index("roles")

        # Project users (test users at project level)
        self.project_users.create_index("project_id")
        self.project_users.create_index([("project_id", 1), ("username", 1)], unique=True)
        self.project_users.create_index([("project_id", 1), ("enabled", 1)])
        self.project_users.create_index("roles")

        # Recordings (manual audit recordings)
        self.recordings.create_index("recording_id", unique=True)
        self.recordings.create_index("project_id")
        self.recordings.create_index("recorded_date")
        self.recordings.create_index("recording_type")
        self.recordings.create_index("component_names")  # For component-specific queries
        self.recordings.create_index([("project_id", 1), ("recorded_date", -1)])
        self.recordings.create_index("drupal_video_uuid")  # For Drupal sync
        self.recordings.create_index("drupal_sync_status")

        # Discovered pages (for Drupal export)
        self.discovered_pages.create_index("project_id")
        self.discovered_pages.create_index("url")
        self.discovered_pages.create_index([("project_id", 1), ("url", 1)], unique=True)
        self.discovered_pages.create_index("source_type")
        self.discovered_pages.create_index("drupal_uuid")  # For Drupal sync
        self.discovered_pages.create_index("drupal_sync_status")

        # Recording issues
        self.recording_issues.create_index("recording_id")
        self.recording_issues.create_index("project_id")
        self.recording_issues.create_index("impact")
        self.recording_issues.create_index("status")
        self.recording_issues.create_index("component_names")  # For component-specific queries
        self.recording_issues.create_index([("recording_id", 1), ("impact", 1)])
        self.recording_issues.create_index([("project_id", 1), ("status", 1)])
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Ping the database
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_indexes(self):
        """Public method to create indexes"""
        self._create_indexes()
    
    def close(self):
        """Close database connection"""
        self.client.close()
        logger.info("Database connection closed")
    
    # Project operations
    
    def create_project(self, project: Project) -> str:
        """Create new project"""
        result = self.projects.insert_one(project.to_dict())
        project._id = result.inserted_id
        logger.info(f"Created project: {project.name} ({project.id})")
        return project.id
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        doc = self.projects.find_one({"_id": ObjectId(project_id)})
        return Project.from_dict(doc) if doc else None
    
    def get_projects(
        self, 
        status: Optional[ProjectStatus] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Project]:
        """Get projects with optional filtering"""
        query = {}
        if status:
            query["status"] = status.value
        
        docs = self.projects.find(query).limit(limit).skip(skip)
        return [Project.from_dict(doc) for doc in docs]
    
    def get_all_projects(self) -> List[Project]:
        """Get all projects"""
        docs = self.projects.find()
        return [Project.from_dict(doc) for doc in docs]
    
    def update_project(self, project: Project) -> bool:
        """Update existing project"""
        project.update_timestamp()
        result = self.projects.replace_one(
            {"_id": project._id},
            project.to_dict()
        )
        return result.modified_count > 0
    
    def delete_project(self, project_id: str) -> bool:
        """Delete project and related data"""
        # Delete related data
        websites = self.get_websites(project_id)
        for website in websites:
            self.delete_website(website.id)
        
        # Delete project
        result = self.projects.delete_one({"_id": ObjectId(project_id)})
        logger.info(f"Deleted project: {project_id}")
        return result.deleted_count > 0
    
    # Website operations
    
    def create_website(self, website: Website) -> str:
        """Create new website"""
        result = self.websites.insert_one(website.to_dict())
        website._id = result.inserted_id
        
        # Add to project's website list
        self.projects.update_one(
            {"_id": ObjectId(website.project_id)},
            {"$push": {"website_ids": website.id}}
        )
        
        logger.info(f"Created website: {website.url} ({website.id})")
        return website.id
    
    def get_website(self, website_id: str) -> Optional[Website]:
        """Get website by ID"""
        doc = self.websites.find_one({"_id": ObjectId(website_id)})
        return Website.from_dict(doc) if doc else None
    
    def get_websites(self, project_id: str) -> List[Website]:
        """Get all websites for a project"""
        docs = self.websites.find({"project_id": project_id})
        return [Website.from_dict(doc) for doc in docs]
    
    def update_website(self, website: Website) -> bool:
        """Update existing website"""
        result = self.websites.replace_one(
            {"_id": website._id},
            website.to_dict()
        )
        return result.modified_count > 0
    
    def delete_website(self, website_id: str) -> bool:
        """Delete website and related data"""
        website = self.get_website(website_id)
        if not website:
            return False
        
        # Delete related pages and test results
        pages = self.get_pages(website_id)
        for page in pages:
            self.delete_page(page.id)
        
        # Remove from project's website list
        self.projects.update_one(
            {"_id": ObjectId(website.project_id)},
            {"$pull": {"website_ids": website_id}}
        )
        
        # Delete website
        result = self.websites.delete_one({"_id": ObjectId(website_id)})
        logger.info(f"Deleted website: {website_id}")
        return result.deleted_count > 0
    
    # Page operations
    
    def create_page(self, page: Page) -> str:
        """Create new page"""
        # Check if page already exists
        existing = self.pages.find_one({
            "website_id": page.website_id,
            "url": page.url
        })
        
        if existing:
            page._id = existing["_id"]
            return str(existing["_id"])
        
        result = self.pages.insert_one(page.to_dict())
        page._id = result.inserted_id
        
        # Update website page count
        self.websites.update_one(
            {"_id": ObjectId(page.website_id)},
            {"$inc": {"page_count": 1}}
        )
        
        return page.id
    
    def get_page(self, page_id: str) -> Optional[Page]:
        """Get page by ID"""
        doc = self.pages.find_one({"_id": ObjectId(page_id)})
        return Page.from_dict(doc) if doc else None
    
    def get_page_by_url(self, website_id: str, url: str) -> Optional[Page]:
        """Get page by URL"""
        doc = self.pages.find_one({
            "website_id": website_id,
            "url": url
        })
        return Page.from_dict(doc) if doc else None
    
    def get_pages(
        self,
        website_id: str,
        status: Optional[PageStatus] = None,
        limit: int = 1000,
        skip: int = 0,
        latest_only: bool = True
    ) -> List[Page]:
        """Get pages for a website"""
        query = {"website_id": website_id}
        if status:
            query["status"] = status.value
        
        # By default, only return pages from latest discovery for testing
        if latest_only:
            query["is_in_latest_discovery"] = True
        
        docs = self.pages.find(query).limit(limit).skip(skip)
        return [Page.from_dict(doc) for doc in docs]
    
    def update_page(self, page: Page) -> bool:
        """Update existing page"""
        result = self.pages.replace_one(
            {"_id": page._id},
            page.to_dict()
        )
        return result.modified_count > 0
    
    def delete_page(self, page_id: str) -> bool:
        """Delete page and related test results"""
        # Delete test results
        self.test_results.delete_many({"page_id": page_id})
        
        # Update website page count
        page = self.get_page(page_id)
        if page:
            self.websites.update_one(
                {"_id": ObjectId(page.website_id)},
                {"$inc": {"page_count": -1}}
            )
        
        # Delete page
        result = self.pages.delete_one({"_id": ObjectId(page_id)})
        return result.deleted_count > 0
    
    def bulk_create_pages(self, pages: List[Page]) -> int:
        """Create multiple pages efficiently"""
        if not pages:
            return 0
        
        # Filter out existing pages
        new_pages = []
        for page in pages:
            existing = self.pages.find_one({
                "website_id": page.website_id,
                "url": page.url
            })
            if not existing:
                new_pages.append(page.to_dict())
        
        if not new_pages:
            return 0
        
        insert_result = self.pages.insert_many(new_pages)
        
        # Update website page count
        if new_pages:
            website_id = new_pages[0]["website_id"]
            # website_id is already a string, need to find by string ID
            update_result = self.websites.update_one(
                {"_id": ObjectId(website_id)},
                {"$inc": {"page_count": len(new_pages)}}
            )
            logger.info(f"Updated website {website_id} page count by {len(new_pages)}, modified={update_result.modified_count}")
        
        return len(insert_result.inserted_ids)
    
    # Test result operations

    def _create_test_result_items(self, test_result_id: ObjectId, test_result: TestResult) -> int:
        """
        Create individual test result item documents (violations, warnings, etc.)

        Args:
            test_result_id: ObjectId of the test result summary document
            test_result: TestResult object containing all items

        Returns:
            Number of items inserted
        """
        items = []

        # Convert violations to items
        for violation in test_result.violations:
            items.append({
                'test_result_id': test_result_id,
                'page_id': test_result.page_id,
                'test_date': test_result.test_date,
                'item_type': 'violation',
                'issue_id': violation.id,
                'impact': violation.impact.value if hasattr(violation.impact, 'value') else str(violation.impact),
                'touchpoint': violation.touchpoint,
                'xpath': violation.xpath,
                'element': violation.element,
                'html': violation.html,
                'description': violation.description,
                'failure_summary': violation.failure_summary,
                'wcag_criteria': violation.wcag_criteria if violation.wcag_criteria else [],
                'help_url': violation.help_url,
                'metadata': violation.metadata if violation.metadata else {}
            })

        # Convert warnings to items
        for warning in test_result.warnings:
            items.append({
                'test_result_id': test_result_id,
                'page_id': test_result.page_id,
                'test_date': test_result.test_date,
                'item_type': 'warning',
                'issue_id': warning.id,
                'impact': warning.impact.value if hasattr(warning.impact, 'value') else str(warning.impact),
                'touchpoint': warning.touchpoint,
                'xpath': warning.xpath,
                'element': warning.element,
                'html': warning.html,
                'description': warning.description,
                'failure_summary': warning.failure_summary,
                'wcag_criteria': warning.wcag_criteria if warning.wcag_criteria else [],
                'help_url': warning.help_url,
                'metadata': warning.metadata if warning.metadata else {}
            })

        # Convert info items
        for info in test_result.info:
            items.append({
                'test_result_id': test_result_id,
                'page_id': test_result.page_id,
                'test_date': test_result.test_date,
                'item_type': 'info',
                'issue_id': info.id,
                'impact': info.impact.value if hasattr(info.impact, 'value') else str(info.impact),
                'touchpoint': info.touchpoint,
                'xpath': info.xpath,
                'element': info.element,
                'html': info.html,
                'description': info.description,
                'metadata': info.metadata if info.metadata else {}
            })

        # Convert discovery items
        for discovery in test_result.discovery:
            items.append({
                'test_result_id': test_result_id,
                'page_id': test_result.page_id,
                'test_date': test_result.test_date,
                'item_type': 'discovery',
                'issue_id': discovery.id,
                'impact': discovery.impact.value if hasattr(discovery.impact, 'value') else str(discovery.impact),
                'touchpoint': discovery.touchpoint,
                'xpath': discovery.xpath,
                'element': discovery.element,
                'html': discovery.html,
                'description': discovery.description,
                'metadata': discovery.metadata if discovery.metadata else {}
            })

        # Convert passes
        for passed in test_result.passes:
            items.append({
                'test_result_id': test_result_id,
                'page_id': test_result.page_id,
                'test_date': test_result.test_date,
                'item_type': 'pass',
                'issue_id': passed.get('id'),
                'touchpoint': passed.get('touchpoint'),
                'xpath': passed.get('xpath'),
                'element': passed.get('element'),
                'html': passed.get('html'),
                'description': passed.get('description'),
                'metadata': passed.get('metadata', {})
            })

        # Batch insert all items
        if items:
            result = self.test_result_items.insert_many(items, ordered=False)
            logger.info(f"Created {len(result.inserted_ids)} test result items for test_result {test_result_id}")
            return len(result.inserted_ids)

        return 0

    def create_test_result(self, test_result: TestResult) -> str:
        """
        Create new test result using split schema (summary + items)

        NEW APPROACH:
        - Stores summary (counts, metadata) in test_results collection
        - Stores individual items in test_result_items collection
        - No size limit issues since each item is a separate document
        - All raw data preserved

        POLICY: Never truncates violations/warnings/passes data.
        """
        # Create summary document (counts only, no arrays)
        summary = {
            'page_id': test_result.page_id,
            'test_date': test_result.test_date,
            'duration_ms': test_result.duration_ms,

            # Counts only (not arrays)
            'violation_count': test_result.violation_count,
            'warning_count': test_result.warning_count,
            'info_count': test_result.info_count,
            'discovery_count': test_result.discovery_count,
            'pass_count': test_result.pass_count,

            # AI findings (usually small, keep in summary)
            'ai_findings': test_result.ai_findings,

            # Screenshot info
            'screenshot_path': test_result.screenshot_path,

            # Test metadata (includes applicable_checks, passed_checks, etc.)
            'metadata': test_result.metadata if hasattr(test_result, 'metadata') and test_result.metadata else {},

            # Multi-state testing fields
            'session_id': test_result.session_id if hasattr(test_result, 'session_id') else None,
            'state_sequence': test_result.state_sequence if hasattr(test_result, 'state_sequence') else 0,
            'page_state': test_result.page_state if hasattr(test_result, 'page_state') else None,
            'related_result_ids': test_result.related_result_ids if hasattr(test_result, 'related_result_ids') else [],

            # Metadata
            '_has_detailed_items': True,
            '_items_collection': 'test_result_items'
        }

        try:
            # Insert summary document
            result = self.test_results.insert_one(summary)
            test_result._id = result.inserted_id
            test_result_id = result.inserted_id

            logger.info(f"Created test result summary for page: {test_result.page_id}")

            # Create detailed item documents
            items_count = self._create_test_result_items(test_result_id, test_result)
            logger.info(f"Created {items_count} detailed items for test result {test_result_id}")

        except Exception as e:
            # If anything fails, log error and create error result
            logger.error(f"Error creating test result for page {test_result.page_id}: {e}")

            # Create minimal error result
            error_result = {
                'page_id': test_result.page_id,
                'test_date': test_result.test_date,
                'duration_ms': test_result.duration_ms,
                'violation_count': 1,
                'warning_count': 0,
                'info_count': 0,
                'discovery_count': 0,
                'pass_count': 0,
                'violations': [{
                    'id': 'ErrTestResultCreationFailed',
                    'impact': 'high',
                    'touchpoint': 'system',
                    'description': f'Failed to create test result: {str(e)}',
                    'xpath': '/',
                    'element': 'DOCUMENT'
                }],
                'warnings': [],
                'info': [],
                'discovery': [],
                'passes': [],
                'ai_findings': [],
                'screenshot_path': test_result.screenshot_path,
                'error': str(e)
            }

            result = self.test_results.insert_one(error_result)
            test_result._id = result.inserted_id

        # Update page with latest test info
        page = self.get_page(test_result.page_id)
        if page:
            page.last_tested = test_result.test_date
            page.status = PageStatus.TESTED
            page.violation_count = test_result.violation_count
            page.warning_count = test_result.warning_count
            page.info_count = test_result.info_count
            page.discovery_count = test_result.discovery_count
            page.pass_count = test_result.pass_count
            page.test_duration_ms = test_result.duration_ms
            self.update_page(page)

        logger.info(f"Created test result for page: {test_result.page_id}")
        return test_result.id

    def _get_test_result_items(self, test_result_id: ObjectId, item_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get test result items from the test_result_items collection

        Args:
            test_result_id: ObjectId of the test result
            item_type: Optional filter by item type (violation, warning, info, discovery, pass)

        Returns:
            List of item dictionaries
        """
        query = {'test_result_id': test_result_id}
        if item_type:
            query['item_type'] = item_type

        items = list(self.test_result_items.find(query))
        return items

    def get_test_result(self, result_id: str) -> Optional[TestResult]:
        """
        Get test result by ID

        Supports both old schema (with arrays) and new schema (with separate items)
        """
        doc = self.test_results.find_one({"_id": ObjectId(result_id)})
        if not doc:
            return None

        # Check if this uses the new schema (split items)
        if doc.get('_has_detailed_items'):
            # Load items from test_result_items collection
            test_result_id = doc['_id']
            items = self._get_test_result_items(test_result_id)

            # Group items by type
            violations = []
            warnings = []
            info = []
            discovery = []
            passes = []

            for item in items:
                item_data = {
                    'id': item.get('issue_id'),
                    'impact': item.get('impact'),
                    'touchpoint': item.get('touchpoint'),
                    'xpath': item.get('xpath'),
                    'element': item.get('element'),
                    'html': item.get('html'),
                    'description': item.get('description'),
                    'metadata': item.get('metadata', {})
                }

                item_type = item.get('item_type')
                if item_type == 'violation':
                    item_data['failure_summary'] = item.get('failure_summary')
                    item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                    item_data['help_url'] = item.get('help_url')
                    violations.append(item_data)
                elif item_type == 'warning':
                    item_data['failure_summary'] = item.get('failure_summary')
                    item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                    item_data['help_url'] = item.get('help_url')
                    warnings.append(item_data)
                elif item_type == 'info':
                    info.append(item_data)
                elif item_type == 'discovery':
                    discovery.append(item_data)
                elif item_type == 'pass':
                    passes.append(item_data)

            # Add arrays back to doc for TestResult.from_dict()
            doc['violations'] = violations
            doc['warnings'] = warnings
            doc['info'] = info
            doc['discovery'] = discovery
            doc['passes'] = passes

        # Old schema already has arrays, just use as-is
        return TestResult.from_dict(doc)
    
    def get_latest_test_result(self, page_id: str) -> Optional[TestResult]:
        """
        Get most recent test result for a page

        Supports both old schema (with arrays) and new schema (with separate items)
        """
        doc = self.test_results.find_one(
            {"page_id": page_id},
            sort=[("test_date", -1)]
        )
        if not doc:
            return None

        # Check if this uses the new schema (split items)
        if doc.get('_has_detailed_items'):
            # Load items from test_result_items collection
            test_result_id = doc['_id']
            items = self._get_test_result_items(test_result_id)

            # Group items by type
            violations = []
            warnings = []
            info = []
            discovery = []
            passes = []

            for item in items:
                item_data = {
                    'id': item.get('issue_id'),
                    'impact': item.get('impact'),
                    'touchpoint': item.get('touchpoint'),
                    'xpath': item.get('xpath'),
                    'element': item.get('element'),
                    'html': item.get('html'),
                    'description': item.get('description'),
                    'metadata': item.get('metadata', {})
                }

                item_type = item.get('item_type')
                if item_type == 'violation':
                    item_data['failure_summary'] = item.get('failure_summary')
                    item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                    item_data['help_url'] = item.get('help_url')
                    violations.append(item_data)
                elif item_type == 'warning':
                    item_data['failure_summary'] = item.get('failure_summary')
                    item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                    item_data['help_url'] = item.get('help_url')
                    warnings.append(item_data)
                elif item_type == 'info':
                    info.append(item_data)
                elif item_type == 'discovery':
                    discovery.append(item_data)
                elif item_type == 'pass':
                    passes.append(item_data)

            # Add arrays back to doc for TestResult.from_dict()
            doc['violations'] = violations
            doc['warnings'] = warnings
            doc['info'] = info
            doc['discovery'] = discovery
            doc['passes'] = passes

        # Old schema already has arrays, just use as-is
        return TestResult.from_dict(doc)
    
    def get_test_results(
        self,
        page_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[TestResult]:
        """Get test results with optional filtering"""
        query = {}
        if page_id:
            query["page_id"] = page_id
        if start_date or end_date:
            query["test_date"] = {}
            if start_date:
                query["test_date"]["$gte"] = start_date
            if end_date:
                query["test_date"]["$lte"] = end_date

        docs = self.test_results.find(query).limit(limit).skip(skip).sort("test_date", -1)
        results = []
        for doc in docs:
            # Check if this uses the new schema (split items)
            if doc.get('_has_detailed_items'):
                # Load items from test_result_items collection
                test_result_id = doc['_id']
                items = self._get_test_result_items(test_result_id)

                # Group items by type
                violations = []
                warnings = []
                info = []
                discovery = []
                passes = []

                for item in items:
                    item_data = {
                        'id': item.get('issue_id'),
                        'impact': item.get('impact'),
                        'touchpoint': item.get('touchpoint'),
                        'xpath': item.get('xpath'),
                        'element': item.get('element'),
                        'html': item.get('html'),
                        'description': item.get('description'),
                        'metadata': item.get('metadata', {})
                    }

                    item_type = item.get('item_type')
                    if item_type == 'violation':
                        item_data['failure_summary'] = item.get('failure_summary')
                        item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                        item_data['help_url'] = item.get('help_url')
                        violations.append(item_data)
                    elif item_type == 'warning':
                        item_data['failure_summary'] = item.get('failure_summary')
                        item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                        item_data['help_url'] = item.get('help_url')
                        warnings.append(item_data)
                    elif item_type == 'info':
                        info.append(item_data)
                    elif item_type == 'discovery':
                        discovery.append(item_data)
                    elif item_type == 'pass':
                        passes.append(item_data)

                # Add arrays back to doc
                doc['violations'] = violations
                doc['warnings'] = warnings
                doc['info'] = info
                doc['discovery'] = discovery
                doc['passes'] = passes

            # Old schema already has arrays, or we just loaded them
            results.append(TestResult.from_dict(doc))

        return results
    
    def delete_test_result(self, result_id: str) -> bool:
        """Delete test result"""
        result = self.test_results.delete_one({"_id": ObjectId(result_id)})
        return result.deleted_count > 0

    # Multi-state test result methods

    def get_test_results_by_session(self, session_id: str) -> List[TestResult]:
        """
        Get all test results for a script execution session

        Args:
            session_id: Script execution session ID

        Returns:
            List of test results ordered by state_sequence
        """
        docs = self.test_results.find({"session_id": session_id}).sort("state_sequence", 1)
        results = []
        for doc in docs:
            # Check if this uses the new schema (split items)
            if doc.get('_has_detailed_items'):
                # Load items from test_result_items collection
                test_result_id = doc['_id']
                items = self._get_test_result_items(test_result_id)

                # Group items by type
                violations = []
                warnings = []
                info = []
                discovery = []
                passes = []

                for item in items:
                    item_data = {
                        'id': item.get('issue_id'),
                        'impact': item.get('impact'),
                        'touchpoint': item.get('touchpoint'),
                        'xpath': item.get('xpath'),
                        'element': item.get('element'),
                        'html': item.get('html'),
                        'description': item.get('description'),
                        'metadata': item.get('metadata', {})
                    }

                    item_type = item.get('item_type')
                    if item_type == 'violation':
                        item_data['failure_summary'] = item.get('failure_summary')
                        item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                        item_data['help_url'] = item.get('help_url')
                        violations.append(item_data)
                    elif item_type == 'warning':
                        item_data['failure_summary'] = item.get('failure_summary')
                        item_data['wcag_criteria'] = item.get('wcag_criteria', [])
                        item_data['help_url'] = item.get('help_url')
                        warnings.append(item_data)
                    elif item_type == 'info':
                        info.append(item_data)
                    elif item_type == 'discovery':
                        discovery.append(item_data)
                    elif item_type == 'pass':
                        passes.append(item_data)

                # Add arrays back to doc for TestResult.from_dict()
                doc['violations'] = violations
                doc['warnings'] = warnings
                doc['info'] = info
                doc['discovery'] = discovery
                doc['passes'] = passes

            # Old schema already has arrays, or we just added them
            result = TestResult.from_dict(doc)
            results.append(result)
        return results

    def get_test_results_by_page_and_session(
        self,
        page_id: str,
        session_id: str
    ) -> List[TestResult]:
        """
        Get all test results for a specific page in a session

        Args:
            page_id: Page ID
            session_id: Script execution session ID

        Returns:
            List of test results ordered by state_sequence
        """
        docs = self.test_results.find({
            "page_id": page_id,
            "session_id": session_id
        }).sort("state_sequence", 1)
        return [TestResult.from_dict(doc) for doc in docs]

    def get_related_test_results(self, result_id: str) -> List[TestResult]:
        """
        Get all test results related to a specific result

        Args:
            result_id: Test result ID

        Returns:
            List of related test results
        """
        # First get the result to find its related IDs
        result = self.get_test_result(result_id)
        if not result or not result.related_result_ids:
            return []

        # Get all related results
        object_ids = [ObjectId(rid) for rid in result.related_result_ids]
        docs = self.test_results.find({"_id": {"$in": object_ids}}).sort("state_sequence", 1)
        return [TestResult.from_dict(doc) for doc in docs]

    def get_latest_test_results_per_state(
        self,
        page_id: str,
        limit: int = 1
    ) -> Dict[int, TestResult]:
        """
        Get the most recent test result for each state sequence

        Args:
            page_id: Page ID
            limit: Number of test runs to consider (default: most recent)

        Returns:
            Dictionary of {state_sequence: TestResult}
        """
        # Get all test results for page, grouped by session
        pipeline = [
            {"$match": {"page_id": page_id}},
            {"$sort": {"test_date": -1}},
            {"$group": {
                "_id": {"session_id": "$session_id", "state_sequence": "$state_sequence"},
                "latest": {"$first": "$$ROOT"}
            }},
            {"$limit": limit * 10}  # Get more than we need to handle multiple sequences
        ]

        results = self.test_results.aggregate(pipeline)
        state_results = {}

        for doc in results:
            result = TestResult.from_dict(doc['latest'])
            state_seq = result.state_sequence
            # Only keep the most recent for each state
            if state_seq not in state_results or result.test_date > state_results[state_seq].test_date:
                state_results[state_seq] = result

        return state_results

    # Query methods for reporting

    def get_violations_by_issue(self, test_result_id: str, item_type: str = 'violation') -> Dict[str, List[Dict[str, Any]]]:
        """
        Get violations grouped by issue_id for deduplication in reports

        Args:
            test_result_id: Test result ID
            item_type: Type of items to get (violation, warning, info, discovery, pass)

        Returns:
            Dictionary of {issue_id: [list of items]}
        """
        items = self._get_test_result_items(ObjectId(test_result_id), item_type=item_type)

        grouped = {}
        for item in items:
            issue_id = item.get('issue_id')
            if issue_id not in grouped:
                grouped[issue_id] = []
            grouped[issue_id].append(item)

        return grouped

    def count_violations_by_type(self, test_result_id: str) -> Dict[str, int]:
        """
        Get counts of violations grouped by issue_id using aggregation

        Args:
            test_result_id: Test result ID

        Returns:
            Dictionary of {issue_id: count}
        """
        pipeline = [
            {'$match': {
                'test_result_id': ObjectId(test_result_id),
                'item_type': 'violation'
            }},
            {'$group': {
                '_id': '$issue_id',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]

        results = self.test_result_items.aggregate(pipeline)
        return {item['_id']: item['count'] for item in results}

    def get_violations_by_touchpoint(self, test_result_id: str) -> Dict[str, int]:
        """
        Get violation counts grouped by touchpoint

        Args:
            test_result_id: Test result ID

        Returns:
            Dictionary of {touchpoint: count}
        """
        pipeline = [
            {'$match': {
                'test_result_id': ObjectId(test_result_id),
                'item_type': 'violation'
            }},
            {'$group': {
                '_id': '$touchpoint',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]

        results = self.test_result_items.aggregate(pipeline)
        return {item['_id']: item['count'] for item in results}

    def get_sample_violations(self, test_result_id: str, issue_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get sample violations for a specific issue (for displaying in reports)

        Args:
            test_result_id: Test result ID
            issue_id: Issue ID to get samples for
            limit: Maximum number of samples to return

        Returns:
            List of sample violation items
        """
        items = list(self.test_result_items.find({
            'test_result_id': ObjectId(test_result_id),
            'item_type': 'violation',
            'issue_id': issue_id
        }).limit(limit))

        return items

    # Statistics
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a project"""
        websites = self.get_websites(project_id)
        
        total_pages = 0
        tested_pages = 0
        total_violations = 0
        total_warnings = 0
        
        for website in websites:
            pages = self.get_pages(website.id)
            total_pages += len(pages)
            
            for page in pages:
                if page.status == PageStatus.TESTED:
                    tested_pages += 1
                    total_violations += page.violation_count
                    total_warnings += page.warning_count
        
        return {
            "website_count": len(websites),
            "total_pages": total_pages,
            "tested_pages": tested_pages,
            "untested_pages": total_pages - tested_pages,
            "total_violations": total_violations,
            "total_warnings": total_warnings,
            "test_coverage": (tested_pages / total_pages * 100) if total_pages > 0 else 0
        }
    
    # Document Reference methods
    def add_document_reference(self, doc_ref: 'DocumentReference') -> str:
        """Add or update a document reference"""
        from auto_a11y.models import DocumentReference
        
        # Check if this document already exists for this website
        existing = self.document_references.find_one({
            'website_id': doc_ref.website_id,
            'document_url': doc_ref.document_url
        })
        
        if existing:
            # Update existing reference
            self.document_references.update_one(
                {'_id': existing['_id']},
                {
                    '$set': {
                        'last_seen': doc_ref.last_seen,
                        'via_redirect': doc_ref.via_redirect or existing.get('via_redirect', False)
                    },
                    '$inc': {'seen_count': 1},
                    '$addToSet': {'referring_pages': doc_ref.referring_page_url}
                }
            )
            return str(existing['_id'])
        else:
            # Add new reference
            doc_data = doc_ref.to_dict()
            doc_data['referring_pages'] = [doc_ref.referring_page_url]
            result = self.document_references.insert_one(doc_data)
            return str(result.inserted_id)
    
    def get_document_references(self, website_id: str, internal_only: bool = None) -> List['DocumentReference']:
        """Get document references for a website"""
        from auto_a11y.models import DocumentReference
        
        query = {'website_id': website_id}
        if internal_only is not None:
            query['is_internal'] = internal_only
        
        docs = self.document_references.find(query)
        return [DocumentReference.from_dict(doc) for doc in docs]
    
    def get_all_document_references(self, project_id: str = None) -> List['DocumentReference']:
        """Get all document references, optionally filtered by project"""
        from auto_a11y.models import DocumentReference
        
        if project_id:
            # Get all websites for the project first
            websites = self.get_websites(project_id)
            website_ids = [w.id for w in websites]
            docs = self.document_references.find({'website_id': {'$in': website_ids}})
        else:
            docs = self.document_references.find({})
        
        return [DocumentReference.from_dict(doc) for doc in docs]
    
    def delete_document_references(self, website_id: str) -> bool:
        """Delete all document references for a website"""
        result = self.document_references.delete_many({'website_id': website_id})
        return result.deleted_count > 0
    
    # Discovery Run methods
    def create_discovery_run(self, discovery_run: 'DiscoveryRun') -> str:
        """Create a new discovery run"""
        from auto_a11y.models import DiscoveryRun
        
        # Mark all previous runs for this website as not latest
        self.discovery_runs.update_many(
            {'website_id': discovery_run.website_id},
            {'$set': {'is_latest': False}}
        )
        
        # Insert new discovery run
        result = self.discovery_runs.insert_one(discovery_run.to_dict())
        discovery_run._id = result.inserted_id
        logger.info(f"Created discovery run {discovery_run.id} for website {discovery_run.website_id}")
        return discovery_run.id
    
    def get_discovery_run(self, discovery_run_id: str) -> Optional['DiscoveryRun']:
        """Get a discovery run by ID"""
        from auto_a11y.models import DiscoveryRun
        
        doc = self.discovery_runs.find_one({'_id': ObjectId(discovery_run_id)})
        return DiscoveryRun.from_dict(doc) if doc else None
    
    def get_latest_discovery_run(self, website_id: str) -> Optional['DiscoveryRun']:
        """Get the latest discovery run for a website"""
        from auto_a11y.models import DiscoveryRun
        
        doc = self.discovery_runs.find_one({
            'website_id': website_id,
            'is_latest': True
        })
        return DiscoveryRun.from_dict(doc) if doc else None
    
    def get_discovery_runs(self, website_id: str) -> List['DiscoveryRun']:
        """Get all discovery runs for a website, ordered by date descending"""
        from auto_a11y.models import DiscoveryRun
        
        docs = self.discovery_runs.find({'website_id': website_id}).sort('started_at', -1)
        return [DiscoveryRun.from_dict(doc) for doc in docs]
    
    def update_discovery_run(self, discovery_run: 'DiscoveryRun') -> bool:
        """Update a discovery run"""
        result = self.discovery_runs.update_one(
            {'_id': discovery_run._id},
            {'$set': discovery_run.to_dict()}
        )
        return result.modified_count > 0
    
    def bulk_create_pages_with_discovery(self, pages: List[Page], discovery_run_id: str) -> int:
        """Create multiple pages with discovery run tracking"""
        if not pages:
            return 0
        
        # Get existing pages for this website
        website_id = pages[0].website_id
        existing_urls = set()
        for doc in self.pages.find({'website_id': website_id}, {'url': 1}):
            existing_urls.add(doc['url'])
        
        # Mark all existing pages as not in latest discovery
        self.pages.update_many(
            {'website_id': website_id},
            {'$set': {'is_in_latest_discovery': False}}
        )
        
        # Process new and existing pages
        new_pages = []
        updated_count = 0
        
        for page in pages:
            page.discovery_run_id = discovery_run_id
            page.is_in_latest_discovery = True
            
            if page.url in existing_urls:
                # Update existing page
                self.pages.update_one(
                    {'website_id': website_id, 'url': page.url},
                    {'$set': {
                        'discovery_run_id': discovery_run_id,
                        'is_in_latest_discovery': True,
                        'discovered_at': page.discovered_at,
                        'title': page.title,
                        'depth': page.depth,
                        'status': page.status.value if hasattr(page.status, 'value') else page.status,
                        'error_reason': page.error_reason
                    }}
                )
                updated_count += 1
            else:
                # New page
                new_pages.append(page.to_dict())
        
        # Insert new pages
        if new_pages:
            insert_result = self.pages.insert_many(new_pages)
            
            # Update website page count
            self.websites.update_one(
                {"_id": ObjectId(website_id)},
                {"$inc": {"page_count": len(new_pages)}}
            )
            logger.info(f"Added {len(new_pages)} new pages, updated {updated_count} existing pages")
            
            return len(insert_result.inserted_ids) + updated_count
        
        return updated_count
    
    def get_pages_for_testing(self, website_id: str, status: Optional[PageStatus] = None) -> List[Page]:
        """Get pages for testing (only from latest discovery)"""
        query = {
            'website_id': website_id,
            'is_in_latest_discovery': True
        }
        
        if status:
            query['status'] = status.value
        
        docs = self.pages.find(query)
        return [Page.from_dict(doc) for doc in docs]
    
    def compare_discoveries(self, website_id: str, old_run_id: str, new_run_id: str) -> Dict[str, Any]:
        """Compare two discovery runs to find added/removed pages"""
        
        # Get pages from old discovery
        old_pages = set()
        for doc in self.pages.find({'website_id': website_id, 'discovery_run_id': old_run_id}, {'url': 1}):
            old_pages.add(doc['url'])
        
        # Get pages from new discovery
        new_pages = set()
        for doc in self.pages.find({'website_id': website_id, 'discovery_run_id': new_run_id}, {'url': 1}):
            new_pages.add(doc['url'])
        
        # Calculate differences
        pages_added = new_pages - old_pages
        pages_removed = old_pages - new_pages
        pages_unchanged = old_pages & new_pages
        
        return {
            'pages_added': list(pages_added),
            'pages_removed': list(pages_removed),
            'pages_unchanged': list(pages_unchanged),
            'added_count': len(pages_added),
            'removed_count': len(pages_removed),
            'unchanged_count': len(pages_unchanged)
        }

    # Issue Documentation Status Methods

    def get_issue_documentation_status(self, issue_code: str) -> Optional[Dict[str, Any]]:
        """Get documentation status for an issue code"""
        return self.issue_documentation_status.find_one({'issue_code': issue_code})

    def set_issue_production_ready(self, issue_code: str, production_ready: bool, updated_by: str = "system") -> bool:
        """Set the production_ready flag for an issue code"""
        from datetime import datetime

        result = self.issue_documentation_status.update_one(
            {'issue_code': issue_code},
            {
                '$set': {
                    'production_ready': production_ready,
                    'updated_by': updated_by,
                    'updated_at': datetime.now()
                },
                '$setOnInsert': {
                    'issue_code': issue_code,
                    'created_at': datetime.now()
                }
            },
            upsert=True
        )

        return result.modified_count > 0 or result.upserted_id is not None

    def get_all_issue_documentation_statuses(self) -> Dict[str, bool]:
        """Get all issue documentation statuses as a dict of issue_code -> production_ready"""
        statuses = {}
        for doc in self.issue_documentation_status.find():
            statuses[doc['issue_code']] = doc.get('production_ready', False)
        return statuses

    def get_production_ready_issues(self) -> List[str]:
        """Get list of issue codes marked as production ready"""
        docs = self.issue_documentation_status.find({'production_ready': True})
        return [doc['issue_code'] for doc in docs]

    def get_not_production_ready_issues(self) -> List[str]:
        """Get list of issue codes not marked as production ready"""
        docs = self.issue_documentation_status.find({'production_ready': {'$ne': True}})
        return [doc['issue_code'] for doc in docs]

    # Page Setup Script Methods

    def create_page_setup_script(self, script: 'PageSetupScript') -> str:
        """
        Create a new page setup script

        Args:
            script: PageSetupScript object

        Returns:
            Script ID as string
        """
        from auto_a11y.models import PageSetupScript

        result = self.page_setup_scripts.insert_one(script.to_dict())
        script._id = result.inserted_id
        logger.info(f"Created page setup script: {script.name} ({script.id}) for page {script.page_id}")
        return script.id

    def get_page_setup_script(self, script_id: str) -> Optional['PageSetupScript']:
        """
        Get a page setup script by ID

        Args:
            script_id: Script ID

        Returns:
            PageSetupScript object or None
        """
        from auto_a11y.models import PageSetupScript

        doc = self.page_setup_scripts.find_one({"_id": ObjectId(script_id)})
        return PageSetupScript.from_dict(doc) if doc else None

    def get_page_setup_scripts_for_page(self, page_id: str, enabled_only: bool = False) -> List['PageSetupScript']:
        """
        Get all setup scripts for a page

        Args:
            page_id: Page ID
            enabled_only: If True, only return enabled scripts

        Returns:
            List of PageSetupScript objects
        """
        from auto_a11y.models import PageSetupScript

        query = {"page_id": page_id}
        if enabled_only:
            query["enabled"] = True

        docs = self.page_setup_scripts.find(query).sort("created_date", -1)
        return [PageSetupScript.from_dict(doc) for doc in docs]

    def get_enabled_script_for_page(self, page_id: str) -> Optional['PageSetupScript']:
        """
        Get the enabled setup script for a page (returns first enabled script)

        Args:
            page_id: Page ID

        Returns:
            PageSetupScript object or None
        """
        from auto_a11y.models import PageSetupScript

        doc = self.page_setup_scripts.find_one(
            {"page_id": page_id, "enabled": True},
            sort=[("created_date", -1)]
        )
        return PageSetupScript.from_dict(doc) if doc else None

    def update_page_setup_script(self, script: 'PageSetupScript') -> bool:
        """
        Update an existing page setup script

        Args:
            script: PageSetupScript object with updates

        Returns:
            True if updated successfully
        """
        if not script._id:
            logger.error("Cannot update script without _id")
            return False

        script.update_timestamp()

        # Get dict and remove _id (can't update _id in MongoDB)
        update_data = script.to_dict()
        if '_id' in update_data:
            del update_data['_id']

        logger.debug(f"Updating script {script._id} with data keys: {list(update_data.keys())}")

        try:
            result = self.page_setup_scripts.update_one(
                {"_id": script._id},
                {"$set": update_data}
            )
        except Exception as e:
            logger.error(f"MongoDB update error: {e}")
            logger.error(f"Script ID: {script._id}, type: {type(script._id)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

        if result.modified_count > 0:
            logger.info(f"Updated page setup script: {script.name} ({script.id})")
            return True
        return False

    def delete_page_setup_script(self, script_id: str) -> bool:
        """
        Delete a page setup script

        Args:
            script_id: Script ID

        Returns:
            True if deleted successfully
        """
        result = self.page_setup_scripts.delete_one({"_id": ObjectId(script_id)})

        if result.deleted_count > 0:
            logger.info(f"Deleted page setup script: {script_id}")
            return True
        return False

    def enable_page_setup_script(self, script_id: str, enabled: bool = True) -> bool:
        """
        Enable or disable a page setup script

        Args:
            script_id: Script ID
            enabled: True to enable, False to disable

        Returns:
            True if updated successfully
        """
        result = self.page_setup_scripts.update_one(
            {"_id": ObjectId(script_id)},
            {
                "$set": {
                    "enabled": enabled,
                    "last_modified": datetime.now()
                }
            }
        )

        if result.modified_count > 0:
            logger.info(f"{'Enabled' if enabled else 'Disabled'} page setup script: {script_id}")
            return True
        return False

    def update_script_execution_stats(
        self,
        script_id: str,
        success: bool,
        duration_ms: int
    ) -> bool:
        """
        Update execution statistics for a script

        Args:
            script_id: Script ID
            success: Whether execution was successful
            duration_ms: Execution duration in milliseconds

        Returns:
            True if updated successfully
        """
        # Get current stats
        script = self.get_page_setup_script(script_id)
        if not script:
            return False

        stats = script.execution_stats

        # Update stats
        stats.last_executed = datetime.now()
        if success:
            stats.success_count += 1
        else:
            stats.failure_count += 1

        # Update average duration (rolling average)
        total_executions = stats.success_count + stats.failure_count
        if total_executions > 0:
            stats.average_duration_ms = int(
                (stats.average_duration_ms * (total_executions - 1) + duration_ms) / total_executions
            )

        # Save updated stats
        result = self.page_setup_scripts.update_one(
            {"_id": ObjectId(script_id)},
            {"$set": {"execution_stats": stats.to_dict()}}
        )

        return result.modified_count > 0

    def get_scripts_for_website(
        self,
        website_id: str,
        scope: Optional[str] = None,
        enabled_only: bool = True
    ) -> List['PageSetupScript']:
        """
        Get scripts for a website (any scope or specific scope)

        Args:
            website_id: Website ID
            scope: Optional scope filter ("website", "page", "test_run")
            enabled_only: If True, only return enabled scripts

        Returns:
            List of PageSetupScript objects
        """
        from auto_a11y.models import PageSetupScript

        query = {"website_id": website_id}
        if scope:
            query["scope"] = scope
        if enabled_only:
            query["enabled"] = True

        docs = self.page_setup_scripts.find(query).sort("created_date", -1)
        return [PageSetupScript.from_dict(doc) for doc in docs]

    def get_scripts_for_page_v2(
        self,
        page_id: str,
        website_id: str,
        enabled_only: bool = True
    ) -> List['PageSetupScript']:
        """
        Get all applicable scripts for a page (both page-level and website-level)

        Args:
            page_id: Page ID
            website_id: Website ID
            enabled_only: If True, only return enabled scripts

        Returns:
            List of PageSetupScript objects (website-level + page-level)
        """
        from auto_a11y.models import PageSetupScript, ScriptScope

        query_filter = {"enabled": True} if enabled_only else {}

        # Get website-level scripts
        website_query = {
            "website_id": website_id,
            "scope": ScriptScope.WEBSITE.value,
            **query_filter
        }
        website_scripts = list(self.page_setup_scripts.find(website_query))

        # Get page-level scripts
        page_query = {
            "page_id": page_id,
            "scope": ScriptScope.PAGE.value,
            **query_filter
        }
        page_scripts = list(self.page_setup_scripts.find(page_query))

        # Combine and return
        all_scripts = website_scripts + page_scripts
        return [PageSetupScript.from_dict(doc) for doc in all_scripts]

    # Script Execution Session Methods

    def create_script_session(self, session: 'ScriptExecutionSession') -> str:
        """
        Create a new script execution session

        Args:
            session: ScriptExecutionSession object

        Returns:
            Session ID as string
        """
        from auto_a11y.models import ScriptExecutionSession

        result = self.script_execution_sessions.insert_one(session.to_dict())
        session._id = result.inserted_id
        logger.info(f"Created script execution session: {session.session_id} for website {session.website_id}")
        return session.session_id

    def get_script_session(self, session_id: str) -> Optional['ScriptExecutionSession']:
        """
        Get a script execution session by session ID

        Args:
            session_id: Session ID (UUID string)

        Returns:
            ScriptExecutionSession object or None
        """
        from auto_a11y.models import ScriptExecutionSession

        doc = self.script_execution_sessions.find_one({"session_id": session_id})
        return ScriptExecutionSession.from_dict(doc) if doc else None

    def update_script_session(self, session: 'ScriptExecutionSession') -> bool:
        """
        Update an existing script execution session

        Args:
            session: ScriptExecutionSession object with updates

        Returns:
            True if updated successfully
        """
        if not session._id:
            logger.error("Cannot update session without _id")
            return False

        result = self.script_execution_sessions.update_one(
            {"_id": session._id},
            {"$set": session.to_dict()}
        )

        if result.modified_count > 0:
            logger.info(f"Updated script execution session: {session.session_id}")
            return True
        return False

    def get_latest_session_for_website(self, website_id: str) -> Optional['ScriptExecutionSession']:
        """
        Get the most recent session for a website

        Args:
            website_id: Website ID

        Returns:
            ScriptExecutionSession object or None
        """
        from auto_a11y.models import ScriptExecutionSession

        doc = self.script_execution_sessions.find_one(
            {"website_id": website_id},
            sort=[("started_at", -1)]
        )
        return ScriptExecutionSession.from_dict(doc) if doc else None

    # ==================== Website Users ====================

    def create_website_user(self, user: 'WebsiteUser') -> str:
        """
        Create a new website user for authenticated testing

        Args:
            user: WebsiteUser object

        Returns:
            User ID as string
        """
        from auto_a11y.models import WebsiteUser

        result = self.website_users.insert_one(user.to_dict())
        user._id = result.inserted_id
        logger.info(f"Created website user: {user.username} for website {user.website_id}")
        return str(result.inserted_id)

    def get_website_user(self, user_id: str) -> Optional['WebsiteUser']:
        """
        Get a website user by ID

        Args:
            user_id: User ID

        Returns:
            WebsiteUser object or None
        """
        from auto_a11y.models import WebsiteUser

        doc = self.website_users.find_one({"_id": ObjectId(user_id)})
        return WebsiteUser.from_dict(doc) if doc else None

    def get_website_users(self, website_id: str, enabled_only: bool = False, role: Optional[str] = None) -> List['WebsiteUser']:
        """
        Get all users for a website

        Args:
            website_id: Website ID
            enabled_only: If True, only return enabled users
            role: If specified, only return users with this role

        Returns:
            List of WebsiteUser objects
        """
        from auto_a11y.models import WebsiteUser

        query = {"website_id": website_id}
        if enabled_only:
            query["enabled"] = True
        if role:
            query["roles"] = role

        docs = self.website_users.find(query).sort("display_name", 1)
        return [WebsiteUser.from_dict(doc) for doc in docs]

    def get_website_user_by_username(self, website_id: str, username: str) -> Optional['WebsiteUser']:
        """
        Get a website user by username

        Args:
            website_id: Website ID
            username: Username

        Returns:
            WebsiteUser object or None
        """
        from auto_a11y.models import WebsiteUser

        doc = self.website_users.find_one({
            "website_id": website_id,
            "username": username
        })
        return WebsiteUser.from_dict(doc) if doc else None

    def update_website_user(self, user: 'WebsiteUser') -> bool:
        """
        Update a website user

        Args:
            user: WebsiteUser object

        Returns:
            True if updated successfully
        """
        if not user._id:
            logger.error("Cannot update user without _id")
            return False

        user.update_timestamp()

        # Get dict and remove _id (can't update _id in MongoDB)
        update_data = user.to_dict()
        if '_id' in update_data:
            del update_data['_id']

        result = self.website_users.update_one(
            {"_id": user._id},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            logger.info(f"Updated website user: {user.username} ({user.id})")
            return True
        return False

    def delete_website_user(self, user_id: str) -> bool:
        """
        Delete a website user

        Args:
            user_id: User ID

        Returns:
            True if deleted successfully
        """
        result = self.website_users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            logger.info(f"Deleted website user: {user_id}")
            return True
        return False

    def get_user_roles_for_website(self, website_id: str) -> List[str]:
        """
        Get all unique roles used by users in a website

        Args:
            website_id: Website ID

        Returns:
            List of unique role names
        """
        pipeline = [
            {"$match": {"website_id": website_id}},
            {"$unwind": "$roles"},
            {"$group": {"_id": "$roles"}},
            {"$sort": {"_id": 1}}
        ]

        results = self.website_users.aggregate(pipeline)
        return [doc["_id"] for doc in results]

    # Project user operations (test users at project level)

    def create_project_user(self, user: ProjectUser) -> str:
        """Create a new project user for authenticated testing"""
        result = self.project_users.insert_one(user.to_dict())
        user._id = result.inserted_id
        logger.info(f"Created project user: {user.username} for project {user.project_id}")
        return str(result.inserted_id)

    def get_project_user(self, user_id: str) -> Optional[ProjectUser]:
        """Get a project user by ID"""
        from auto_a11y.models import ProjectUser
        doc = self.project_users.find_one({"_id": ObjectId(user_id)})
        return ProjectUser.from_dict(doc) if doc else None

    def get_project_users(self, project_id: str, enabled_only: bool = False, role: Optional[str] = None) -> List[ProjectUser]:
        """Get all users for a project"""
        from auto_a11y.models import ProjectUser
        query = {"project_id": project_id}
        if enabled_only:
            query["enabled"] = True
        if role:
            query["roles"] = role
        docs = self.project_users.find(query).sort("display_name", 1)
        return [ProjectUser.from_dict(doc) for doc in docs]

    def get_project_user_by_username(self, project_id: str, username: str) -> Optional[ProjectUser]:
        """Get a project user by username"""
        from auto_a11y.models import ProjectUser
        doc = self.project_users.find_one({"project_id": project_id, "username": username})
        return ProjectUser.from_dict(doc) if doc else None

    def update_project_user(self, user: ProjectUser) -> bool:
        """Update a project user"""
        if not user._id:
            logger.error("Cannot update user without _id")
            return False
        user.update_timestamp()
        update_data = user.to_dict()
        if '_id' in update_data:
            del update_data['_id']
        result = self.project_users.update_one({"_id": user._id}, {"$set": update_data})
        if result.modified_count > 0:
            logger.info(f"Updated project user: {user.username}")
            return True
        return False

    def delete_project_user(self, user_id: str) -> bool:
        """Delete a project user"""
        result = self.project_users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            logger.info(f"Deleted project user: {user_id}")
            return True
        return False

    def get_user_roles_for_project(self, project_id: str) -> List[str]:
        """Get all unique roles used by users in a project"""
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$unwind": "$roles"},
            {"$group": {"_id": "$roles"}},
            {"$sort": {"_id": 1}}
        ]
        results = self.project_users.aggregate(pipeline)
        return [doc["_id"] for doc in results]

    # Recording operations (Manual audits from Dictaphone)

    def create_recording(self, recording: Recording) -> str:
        """Create new recording"""
        result = self.recordings.insert_one(recording.to_dict())
        recording._id = result.inserted_id
        logger.info(f"Created recording: {recording.recording_id} ({recording.id})")
        return recording.id

    def get_recording(self, recording_id: str) -> Optional[Recording]:
        """Get recording by MongoDB ID"""
        doc = self.recordings.find_one({"_id": ObjectId(recording_id)})
        return Recording.from_dict(doc) if doc else None

    def get_recording_by_recording_id(self, recording_id: str) -> Optional[Recording]:
        """Get recording by recording_id field (e.g., 'NED-A')"""
        doc = self.recordings.find_one({"recording_id": recording_id})
        return Recording.from_dict(doc) if doc else None

    def get_recordings(
        self,
        project_id: Optional[str] = None,
        recording_type: Optional[RecordingType] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Recording]:
        """Get recordings with optional filtering"""
        query = {}
        if project_id:
            query["project_id"] = project_id
        if recording_type:
            query["recording_type"] = recording_type.value

        docs = self.recordings.find(query).sort("recorded_date", -1).limit(limit).skip(skip)
        return [Recording.from_dict(doc) for doc in docs]

    def get_recordings_for_project(self, project_id: str) -> List[Recording]:
        """Get all recordings for a project"""
        docs = self.recordings.find({"project_id": project_id}).sort("recorded_date", -1)
        return [Recording.from_dict(doc) for doc in docs]

    def update_recording(self, recording: Recording) -> bool:
        """Update existing recording"""
        recording.updated_at = datetime.now()
        result = self.recordings.replace_one(
            {"_id": recording._id},
            recording.to_dict()
        )
        return result.modified_count > 0

    def delete_recording(self, recording_id: str) -> bool:
        """Delete recording and related issues"""
        # Get recording to find recording_id field
        recording = self.get_recording(recording_id)
        if recording:
            # Delete related issues
            self.recording_issues.delete_many({"recording_id": recording.recording_id})

        # Delete recording
        result = self.recordings.delete_one({"_id": ObjectId(recording_id)})
        logger.info(f"Deleted recording: {recording_id}")
        return result.deleted_count > 0

    def get_recording_count(self, project_id: Optional[str] = None) -> int:
        """Get total count of recordings"""
        query = {}
        if project_id:
            query["project_id"] = project_id
        return self.recordings.count_documents(query)

    # Recording Issue operations

    def create_recording_issue(self, issue: RecordingIssue) -> str:
        """Create new recording issue"""
        result = self.recording_issues.insert_one(issue.to_dict())
        issue._id = result.inserted_id
        return issue.id

    def create_recording_issues_bulk(self, issues: List[RecordingIssue]) -> List[str]:
        """Create multiple recording issues at once"""
        if not issues:
            return []

        docs = [issue.to_dict() for issue in issues]
        result = self.recording_issues.insert_many(docs)

        # Update issue objects with their new IDs
        for issue, inserted_id in zip(issues, result.inserted_ids):
            issue._id = inserted_id

        logger.info(f"Created {len(issues)} recording issues")
        return [str(id) for id in result.inserted_ids]

    def get_recording_issue(self, issue_id: str) -> Optional[RecordingIssue]:
        """Get recording issue by ID"""
        doc = self.recording_issues.find_one({"_id": ObjectId(issue_id)})
        return RecordingIssue.from_dict(doc) if doc else None

    def get_recording_issues(
        self,
        recording_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 1000,
        skip: int = 0
    ) -> List[RecordingIssue]:
        """Get recording issues with optional filtering"""
        query = {}
        if recording_id:
            query["recording_id"] = recording_id
        if project_id:
            query["project_id"] = project_id
        if status:
            query["status"] = status

        docs = self.recording_issues.find(query).limit(limit).skip(skip)
        return [RecordingIssue.from_dict(doc) for doc in docs]

    def get_recording_issues_for_recording(self, recording_id: str) -> List[RecordingIssue]:
        """Get all issues for a specific recording"""
        docs = self.recording_issues.find({"recording_id": recording_id})
        return [RecordingIssue.from_dict(doc) for doc in docs]

    def update_recording_issue(self, issue: RecordingIssue) -> bool:
        """Update existing recording issue"""
        issue.updated_at = datetime.now()
        result = self.recording_issues.replace_one(
            {"_id": issue._id},
            issue.to_dict()
        )
        return result.modified_count > 0

    def delete_recording_issue(self, issue_id: str) -> bool:
        """Delete recording issue"""
        result = self.recording_issues.delete_one({"_id": ObjectId(issue_id)})
        return result.deleted_count > 0

    def get_recording_issue_count(
        self,
        recording_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> int:
        """Get total count of recording issues"""
        query = {}
        if recording_id:
            query["recording_id"] = recording_id
        if project_id:
            query["project_id"] = project_id
        return self.recording_issues.count_documents(query)

    def update_recording_issue_status(self, issue_id: str, status: str) -> bool:
        """Update status of a recording issue"""
        result = self.recording_issues.update_one(
            {"_id": ObjectId(issue_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now()
                }
            }
        )
        return result.modified_count > 0
