# Database-Backed Job Architecture Migration

## Overview

This document describes the migration from in-memory job tracking to a database-backed job management system for the aut_11y_python accessibility checker. This architecture change addresses the scraping abort issues and prepares the system for multi-user SaaS deployment.

## Problem Statement

The previous architecture had several issues:
1. **Thread Context Isolation**: Jobs running in ThreadPoolExecutor couldn't communicate cancellation status back to the Flask request handlers
2. **Memory State Loss**: Server restarts lost all job state
3. **No Multi-User Support**: In-memory state couldn't support concurrent users
4. **Race Conditions**: Job cleanup happened immediately, causing cancellation requests to fail

## New Architecture

### Core Components

#### 1. JobManager (`auto_a11y/core/job_manager.py`)
- **Purpose**: Centralized database-backed job management
- **Features**:
  - Persistent job storage in MongoDB
  - Atomic cancellation requests
  - Job locking for distributed processing
  - Automatic cleanup of stale jobs
  - Job statistics and monitoring

#### 2. ScrapingJob (`auto_a11y/core/scraping_job.py`)
- **Purpose**: Database-backed scraping job implementation
- **Features**:
  - Real-time progress updates to database
  - Cancellation checking via database queries
  - User and session tracking
  - Detailed status and error reporting

#### 3. Updated WebsiteManager
- **Changes**:
  - Removed in-memory `_shared_active_jobs` dictionary
  - Uses JobManager for all job operations
  - Supports user_id and session_id for multi-tenancy

## Database Schema

### Jobs Collection
```javascript
{
  job_id: String (unique),
  job_type: String (discovery|testing|report_generation|bulk_test),
  status: String (pending|running|completed|failed|cancelled|cancelling),
  website_id: String,
  project_id: String,
  user_id: String,        // For multi-tenancy
  session_id: String,     // For session tracking
  created_at: Date,
  updated_at: Date,
  started_at: Date,
  completed_at: Date,
  progress: {
    current: Number,
    total: Number,
    message: String,
    percentage: Number,
    details: Object
  },
  metadata: Object,
  error: String,
  result: Object,
  cancellation_requested: Boolean,
  cancellation_requested_at: Date,
  cancellation_requested_by: String,
  lock_holder: String,    // For distributed processing
  lock_acquired_at: Date,
  lock_expiry: Date
}
```

### Indexes
- `job_id` (unique)
- `job_type, status, created_at` (compound)
- `user_id, status, created_at` (compound)
- `website_id, status` (compound)
- `status, updated_at` (compound)
- `completed_at` (TTL - 7 days)

## Key Improvements

### 1. Reliable Cancellation
- Cancellation requests are stored in the database
- Jobs check cancellation status via database queries
- No dependency on thread-local state

### 2. Multi-User Support
- Each job tracks `user_id` and `session_id`
- Users can only see/cancel their own jobs
- Ready for authentication integration

### 3. Distributed Processing
- Job locking mechanism prevents duplicate processing
- Multiple workers can process jobs concurrently
- Automatic lock expiry for crashed workers

### 4. Monitoring & Analytics
- Job statistics aggregation
- Performance metrics tracking
- Historical data retention

## Migration Steps

### Phase 1: Core Implementation ✅
- [x] Create JobManager class
- [x] Create database-backed ScrapingJob
- [x] Update WebsiteManager to use JobManager
- [x] Update routes to use new system

### Phase 2: Enhanced Features (In Progress)
- [ ] Add user authentication integration
- [ ] Implement job priorities
- [ ] Add job queuing with rate limiting
- [ ] Create admin dashboard for job monitoring

### Phase 3: Production Readiness
- [ ] Add comprehensive logging
- [ ] Implement job retry logic
- [ ] Add monitoring alerts
- [ ] Performance optimization

## Usage Examples

### Starting a Discovery Job
```python
from auto_a11y.core.job_manager import JobManager
from auto_a11y.core.scraping_job import ScrapingJob

# In the Flask route
job_manager = JobManager(database)
job = ScrapingJob(
    job_manager=job_manager,
    website_id=website_id,
    job_id=job_id,
    max_pages=100,
    user_id=current_user.id,
    session_id=session.id
)

# Run asynchronously
await job.run(database, browser_config)
```

### Cancelling a Job
```python
# In the cancellation route
job_manager = JobManager(database)
success = job_manager.request_cancellation(
    job_id=job_id,
    requested_by=current_user.id
)
```

### Checking Job Status
```python
# Get job status
job = job_manager.get_job(job_id)
if job:
    status = job['status']
    progress = job['progress']
    error = job.get('error')
```

## Benefits

1. **Reliability**: Jobs persist across server restarts
2. **Scalability**: Ready for horizontal scaling
3. **Observability**: Complete job history and metrics
4. **Multi-tenancy**: Built-in user isolation
5. **Maintainability**: Clear separation of concerns

## Future Enhancements

1. **WebSocket Updates**: Real-time progress updates to UI
2. **Job Chaining**: Dependencies between jobs
3. **Scheduled Jobs**: Cron-like job scheduling
4. **Resource Limits**: Per-user job quotas
5. **Cost Tracking**: Usage-based billing support

## Testing

### Unit Tests Required
- JobManager CRUD operations
- Cancellation mechanism
- Lock acquisition/release
- Cleanup processes

### Integration Tests Required
- End-to-end discovery with cancellation
- Concurrent job processing
- Server restart recovery
- Multi-user isolation

## Rollback Plan

If issues arise, the system can be reverted by:
1. Restoring the original `website_manager.py`
2. Restoring the original `scraper.py` with embedded ScrapingJob
3. Removing the new files (job_manager.py, scraping_job.py)
4. Dropping the jobs collection from MongoDB

## Monitoring

Key metrics to track:
- Job completion rate
- Average job duration by type
- Cancellation success rate
- Lock contention frequency
- Database query performance

## Conclusion

This database-backed architecture provides a robust foundation for the aut_11y_python system to scale from a single-user tool to a multi-tenant SaaS platform. The immediate benefit is reliable job cancellation, with the long-term benefit of supporting concurrent users and distributed processing.