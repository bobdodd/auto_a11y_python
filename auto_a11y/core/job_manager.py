"""
Database-backed job management system for concurrent operations
Supports multi-user SaaS architecture with proper state management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
from pymongo import MongoClient, UpdateOne
from pymongo.errors import DuplicateKeyError
import json

logger = logging.getLogger(__name__)


class JobType(Enum):
    """Types of jobs in the system"""
    DISCOVERY = "discovery"
    TESTING = "testing"
    REPORT_GENERATION = "report_generation"
    BULK_TEST = "bulk_test"


class JobStatus(Enum):
    """Job status states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CANCELLING = "cancelling"  # Transitional state


class JobManager:
    """
    Database-backed job manager for handling concurrent operations
    across multiple users and sessions
    """
    
    _instance = None  # Single global instance
    
    def __new__(cls, database):
        """Singleton pattern - single global instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            logger.info("Created global JobManager singleton instance")
        return cls._instance
    
    def __init__(self, database):
        """
        Initialize job manager with database connection
        
        Args:
            database: Database instance
        """
        # Only initialize once per instance
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.db = database
        self.collection = database.db['jobs']
        self._indexes_created = False
        self._cleanup_task = None
        
        # Try to create indexes but don't fail if it doesn't work
        try:
            self._ensure_indexes()
        except Exception as e:
            logger.warning(f"Could not create indexes during init: {e}")
        
        self._initialized = True
    
    def _ensure_indexes(self):
        """Create necessary indexes for job collection"""
        if self._indexes_created:
            return
        
        try:
            # Index for job lookups
            self.collection.create_index('job_id', unique=True)
            
            # Index for finding active jobs by type and status
            self.collection.create_index([
                ('job_type', 1),
                ('status', 1),
                ('created_at', -1)
            ])
            
            # Index for user-specific queries (for multi-tenancy)
            self.collection.create_index([
                ('user_id', 1),
                ('status', 1),
                ('created_at', -1)
            ])
            
            # Index for website/project specific queries
            self.collection.create_index([
                ('website_id', 1),
                ('status', 1)
            ])
            
            # Index for cleanup queries
            self.collection.create_index([
                ('status', 1),
                ('updated_at', 1)
            ])
            
            # TTL index to auto-delete old completed jobs after 7 days
            self.collection.create_index(
                'completed_at',
                expireAfterSeconds=7 * 24 * 60 * 60
            )
            
            self._indexes_created = True
            logger.info("Job collection indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating job indexes: {e}")
            # Don't fail, indexes will be created lazily if needed
    
    def create_job(
        self,
        job_id: str,
        job_type: JobType,
        website_id: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new job in the database
        
        Args:
            job_id: Unique job identifier
            job_type: Type of job
            website_id: Associated website ID
            project_id: Associated project ID
            user_id: User who initiated the job
            session_id: Session ID for tracking
            metadata: Additional job metadata
            
        Returns:
            Created job document
        """
        job_doc = {
            'job_id': job_id,
            'job_type': job_type.value,
            'status': JobStatus.PENDING.value,
            'website_id': website_id,
            'project_id': project_id,
            'user_id': user_id,
            'session_id': session_id,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'progress': {
                'current': 0,
                'total': 0,
                'message': 'Job created',
                'details': {}
            },
            'metadata': metadata or {},
            'error': None,
            'result': None,
            'cancellation_requested': False,
            'cancellation_requested_at': None,
            'cancellation_requested_by': None,
            'lock_holder': None,
            'lock_acquired_at': None
        }
        
        # Ensure indexes are created before first insert
        if not self._indexes_created:
            try:
                self._ensure_indexes()
            except Exception as e:
                logger.warning(f"Could not create indexes: {e}")
        
        try:
            self.collection.insert_one(job_doc)
            logger.info(f"Created job {job_id} of type {job_type.value}")
            return job_doc
        except DuplicateKeyError:
            logger.error(f"Job {job_id} already exists")
            raise ValueError(f"Job {job_id} already exists")
        except Exception as e:
            logger.error(f"Error creating job {job_id}: {e}")
            raise
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        result: Optional[Any] = None
    ) -> bool:
        """
        Update job status and related fields
        
        Args:
            job_id: Job identifier
            status: New status
            progress: Progress update
            error: Error message if failed
            result: Job result if completed
            
        Returns:
            True if updated successfully
        """
        update_doc = {
            '$set': {
                'status': status.value,
                'updated_at': datetime.now()
            }
        }
        
        if status == JobStatus.RUNNING and not progress:
            update_doc['$setOnInsert'] = {'started_at': datetime.now()}
        elif status == JobStatus.RUNNING:
            update_doc['$set']['started_at'] = datetime.now()
        
        if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            update_doc['$set']['completed_at'] = datetime.now()
        
        if progress:
            update_doc['$set']['progress'] = progress
        
        if error:
            update_doc['$set']['error'] = error
        
        if result is not None:
            # Convert result to JSON-serializable format
            try:
                if hasattr(result, '__dict__'):
                    result = result.__dict__
                update_doc['$set']['result'] = result
            except Exception as e:
                logger.error(f"Error serializing result: {e}")
                update_doc['$set']['result'] = str(result)
        
        result = self.collection.update_one(
            {'job_id': job_id},
            update_doc
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated job {job_id} status to {status.value}")
            return True
        return False
    
    def update_job_progress(
        self,
        job_id: str,
        current: int,
        total: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update job progress
        
        Args:
            job_id: Job identifier
            current: Current progress value
            total: Total progress value
            message: Progress message
            details: Additional progress details
            
        Returns:
            True if updated successfully
        """
        progress = {
            'current': current,
            'total': total,
            'message': message,
            'details': details or {},
            'percentage': (current / total * 100) if total > 0 else 0
        }
        
        logger.debug(f"Updating job {job_id} progress in database")
        
        try:
            result = self.collection.update_one(
                {'job_id': job_id},
                {
                    '$set': {
                        'progress': progress,
                        'updated_at': datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.debug(f"Successfully updated progress for job {job_id}")
            else:
                logger.warning(f"No document modified for job {job_id} - job may not exist")
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update progress for job {job_id}: {e}")
            return False
    
    def request_cancellation(
        self,
        job_id: str,
        requested_by: Optional[str] = None
    ) -> bool:
        """
        Request job cancellation
        
        Args:
            job_id: Job identifier
            requested_by: User requesting cancellation
            
        Returns:
            True if cancellation requested successfully
        """
        # First check current job status
        job = self.collection.find_one({'job_id': job_id})
        if not job:
            logger.error(f"Job {job_id} not found for cancellation")
            return False
        
        current_status = job.get('status')
        logger.info(f"Attempting to cancel job {job_id} with current status: {current_status}")
        
        # Only cancel if job is pending or running
        if current_status not in [JobStatus.PENDING.value, JobStatus.RUNNING.value]:
            logger.warning(f"Cannot cancel job {job_id} with status {current_status}")
            return False
        
        result = self.collection.update_one(
            {'job_id': job_id},
            {
                '$set': {
                    'cancellation_requested': True,
                    'cancellation_requested_at': datetime.now(),
                    'cancellation_requested_by': requested_by,
                    'status': JobStatus.CANCELLING.value,
                    'updated_at': datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Cancellation requested for job {job_id} by {requested_by}")
            return True
        else:
            logger.error(f"Failed to update job {job_id} for cancellation")
            return False
    
    def is_cancellation_requested(self, job_id: str) -> bool:
        """
        Check if cancellation has been requested for a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancellation requested
        """
        job = self.collection.find_one(
            {'job_id': job_id},
            {'cancellation_requested': 1, 'status': 1}
        )
        
        if job:
            return (job.get('cancellation_requested', False) or 
                   job.get('status') in [JobStatus.CANCELLING.value, JobStatus.CANCELLED.value])
        return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job document or None
        """
        return self.collection.find_one({'job_id': job_id})
    
    def get_active_jobs(
        self,
        job_type: Optional[JobType] = None,
        website_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active jobs with optional filters
        
        Args:
            job_type: Filter by job type
            website_id: Filter by website
            user_id: Filter by user
            
        Returns:
            List of active jobs
        """
        query = {
            'status': {'$in': [JobStatus.PENDING.value, JobStatus.RUNNING.value]}
        }
        
        if job_type:
            query['job_type'] = job_type.value
        
        if website_id:
            query['website_id'] = website_id
        
        if user_id:
            query['user_id'] = user_id
        
        return list(self.collection.find(query).sort('created_at', -1))
    
    def acquire_job_lock(
        self,
        job_id: str,
        lock_holder: str,
        lock_timeout: int = 300
    ) -> bool:
        """
        Acquire a lock on a job for exclusive processing
        
        Args:
            job_id: Job identifier
            lock_holder: Identifier of the lock holder (e.g., worker ID)
            lock_timeout: Lock timeout in seconds
            
        Returns:
            True if lock acquired
        """
        lock_expiry = datetime.now() + timedelta(seconds=lock_timeout)
        
        result = self.collection.update_one(
            {
                'job_id': job_id,
                '$or': [
                    {'lock_holder': None},
                    {'lock_acquired_at': {'$lt': datetime.now() - timedelta(seconds=lock_timeout)}}
                ]
            },
            {
                '$set': {
                    'lock_holder': lock_holder,
                    'lock_acquired_at': datetime.now(),
                    'lock_expiry': lock_expiry
                }
            }
        )
        
        return result.modified_count > 0
    
    def release_job_lock(self, job_id: str, lock_holder: str) -> bool:
        """
        Release a job lock
        
        Args:
            job_id: Job identifier
            lock_holder: Identifier of the lock holder
            
        Returns:
            True if lock released
        """
        result = self.collection.update_one(
            {
                'job_id': job_id,
                'lock_holder': lock_holder
            },
            {
                '$set': {
                    'lock_holder': None,
                    'lock_acquired_at': None,
                    'lock_expiry': None
                }
            }
        )
        
        return result.modified_count > 0
    
    def cleanup_stale_jobs(self, stale_after_hours: int = 24) -> int:
        """
        Clean up stale jobs that haven't been updated
        
        Args:
            stale_after_hours: Hours after which a running job is considered stale
            
        Returns:
            Number of jobs cleaned up
        """
        stale_time = datetime.now() - timedelta(hours=stale_after_hours)
        
        result = self.collection.update_many(
            {
                'status': JobStatus.RUNNING.value,
                'updated_at': {'$lt': stale_time}
            },
            {
                '$set': {
                    'status': JobStatus.FAILED.value,
                    'error': 'Job timed out - no updates for extended period',
                    'completed_at': datetime.now()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Cleaned up {result.modified_count} stale jobs")
        
        return result.modified_count
    
    def start_cleanup_task(self):
        """Start the cleanup task if not already running"""
        if self._cleanup_task is None or self._cleanup_task.done():
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(self._cleanup_old_jobs())
                logger.info("Started job cleanup task")
            except RuntimeError:
                # No running loop - cleanup will be handled manually
                logger.debug("No event loop available for cleanup task")
    
    async def _cleanup_old_jobs(self):
        """Background task to periodically clean up old jobs"""
        while True:
            try:
                # Clean up stale running jobs every hour
                await asyncio.sleep(3600)
                self.cleanup_stale_jobs()
                
                # Clean up cancelled jobs older than 1 hour
                one_hour_ago = datetime.now() - timedelta(hours=1)
                result = self.collection.delete_many({
                    'status': JobStatus.CANCELLED.value,
                    'completed_at': {'$lt': one_hour_ago}
                })
                
                if result.deleted_count > 0:
                    logger.info(f"Deleted {result.deleted_count} old cancelled jobs")
                    
            except asyncio.CancelledError:
                logger.info("Job cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in job cleanup task: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    def get_job_statistics(
        self,
        user_id: Optional[str] = None,
        website_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get job statistics for monitoring
        
        Args:
            user_id: Filter by user
            website_id: Filter by website
            hours: Hours to look back
            
        Returns:
            Statistics dictionary
        """
        since = datetime.now() - timedelta(hours=hours)
        
        pipeline = [
            {
                '$match': {
                    'created_at': {'$gte': since}
                }
            }
        ]
        
        if user_id:
            pipeline[0]['$match']['user_id'] = user_id
        
        if website_id:
            pipeline[0]['$match']['website_id'] = website_id
        
        pipeline.extend([
            {
                '$group': {
                    '_id': {
                        'job_type': '$job_type',
                        'status': '$status'
                    },
                    'count': {'$sum': 1},
                    'avg_duration': {
                        '$avg': {
                            '$subtract': [
                                '$completed_at',
                                '$started_at'
                            ]
                        }
                    }
                }
            }
        ])
        
        results = list(self.collection.aggregate(pipeline))
        
        # Format statistics
        stats = {
            'total_jobs': sum(r['count'] for r in results),
            'by_type': {},
            'by_status': {}
        }
        
        for result in results:
            job_type = result['_id']['job_type']
            status = result['_id']['status']
            
            if job_type not in stats['by_type']:
                stats['by_type'][job_type] = {}
            stats['by_type'][job_type][status] = result['count']
            
            if status not in stats['by_status']:
                stats['by_status'][status] = 0
            stats['by_status'][status] += result['count']
        
        return stats