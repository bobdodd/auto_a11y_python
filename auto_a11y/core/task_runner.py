"""
Simple async task runner for background jobs
In production, this would be replaced with Celery or similar
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import uuid

logger = logging.getLogger(__name__)


class TaskRunner:
    """Simple in-memory task runner"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize task runner"""
        if self._initialized:
            return
        
        self.tasks: Dict[str, Task] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._initialized = True
    
    def start(self):
        """Start task runner"""
        if not self.loop:
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        
        logger.info("Task runner started")
    
    def stop(self):
        """Stop task runner"""
        # Cancel all running tasks
        for task_id, task in self.tasks.items():
            if task.status == 'running':
                task.cancel()
        
        self.executor.shutdown(wait=True)
        logger.info("Task runner stopped")
    
    def submit_task(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        task_id: Optional[str] = None
    ) -> str:
        """
        Submit a task for execution
        
        Args:
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            task_id: Optional task ID
            
        Returns:
            Task ID
        """
        if kwargs is None:
            kwargs = {}
        
        # Generate task ID if not provided
        if not task_id:
            task_id = str(uuid.uuid4())
        
        # Create task
        task = Task(task_id, func, args, kwargs)
        self.tasks[task_id] = task
        
        # Run task
        if asyncio.iscoroutinefunction(func):
            # Async function
            asyncio.create_task(self._run_async_task(task))
        else:
            # Sync function - run in thread pool
            self.loop.run_in_executor(self.executor, self._run_sync_task, task)
        
        logger.info(f"Submitted task: {task_id}")
        return task_id
    
    async def _run_async_task(self, task: 'Task'):
        """Run async task"""
        task.status = 'running'
        task.started_at = datetime.now()
        
        try:
            task.result = await task.func(*task.args, **task.kwargs)
            task.status = 'completed'
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.status = 'failed'
            task.error = str(e)
        finally:
            task.completed_at = datetime.now()
    
    def _run_sync_task(self, task: 'Task'):
        """Run sync task"""
        task.status = 'running'
        task.started_at = datetime.now()
        
        try:
            task.result = task.func(*task.args, **task.kwargs)
            task.status = 'completed'
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            task.status = 'failed'
            task.error = str(e)
        finally:
            task.completed_at = datetime.now()
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status or None
        """
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            'task_id': task.task_id,
            'status': task.status,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error': task.error,
            'result': task.result if task.status == 'completed' else None
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if cancelled
        """
        task = self.tasks.get(task_id)
        if not task or task.status != 'running':
            return False
        
        task.cancel()
        return True
    
    def cleanup_completed_tasks(self, max_age_seconds: int = 3600):
        """
        Clean up old completed tasks
        
        Args:
            max_age_seconds: Maximum age in seconds
        """
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in ['completed', 'failed', 'cancelled']:
                if task.completed_at:
                    age = (now - task.completed_at).total_seconds()
                    if age > max_age_seconds:
                        to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old tasks")


class Task:
    """Represents a background task"""
    
    def __init__(self, task_id: str, func: Callable, args: tuple, kwargs: dict):
        """
        Initialize task
        
        Args:
            task_id: Task ID
            func: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
        """
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = 'pending'
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Any = None
        self.error: Optional[str] = None
        self._cancelled = False
    
    def cancel(self):
        """Cancel task"""
        self._cancelled = True
        self.status = 'cancelled'
        self.completed_at = datetime.now()


# Global task runner instance
task_runner = TaskRunner()