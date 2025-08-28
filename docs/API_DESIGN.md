# API Design Documentation

## Table of Contents
1. [API Overview](#api-overview)
2. [RESTful Endpoints](#restful-endpoints)
3. [WebSocket Events](#websocket-events)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Authentication](#authentication)
7. [Rate Limiting](#rate-limiting)

## API Overview

The Auto A11y Python API follows RESTful principles with WebSocket support for real-time updates during testing.

### Base URL
```
http://localhost:5000/api/v1
```

### Content Type
All requests and responses use JSON:
```
Content-Type: application/json
```

## RESTful Endpoints

### Projects

#### Create Project
```http
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "My Website Audit",
  "description": "Accessibility audit for corporate website",
  "config": {
    "wcag_level": "AA",
    "include_best_practices": true
  }
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "My Website Audit",
  "description": "Accessibility audit for corporate website",
  "created_at": "2024-01-15T10:30:00Z",
  "status": "active",
  "websites": []
}
```

#### List Projects
```http
GET /api/v1/projects
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `status` (string): Filter by status (active|archived|all)

**Response:**
```json
{
  "projects": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### Get Project
```http
GET /api/v1/projects/{project_id}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "My Website Audit",
  "description": "Accessibility audit for corporate website",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-16T14:20:00Z",
  "status": "active",
  "websites": [
    {
      "id": "507f1f77bcf86cd799439012",
      "name": "Main Website",
      "url": "https://example.com",
      "page_count": 150,
      "last_tested": "2024-01-16T14:20:00Z"
    }
  ],
  "statistics": {
    "total_pages": 150,
    "pages_tested": 145,
    "violations": 423,
    "warnings": 156
  }
}
```

#### Update Project
```http
PUT /api/v1/projects/{project_id}
```

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "config": {
    "wcag_level": "AAA"
  }
}
```

#### Delete Project
```http
DELETE /api/v1/projects/{project_id}
```

### Websites

#### Add Website to Project
```http
POST /api/v1/projects/{project_id}/websites
```

**Request Body:**
```json
{
  "name": "Corporate Site",
  "url": "https://example.com",
  "scraping_config": {
    "max_pages": 500,
    "max_depth": 3,
    "follow_external": false,
    "include_subdomains": true,
    "respect_robots": true,
    "request_delay": 1.0
  }
}
```

#### Discover Pages
```http
POST /api/v1/websites/{website_id}/discover
```

**Request Body:**
```json
{
  "strategy": "crawl",  // or "sitemap" or "manual"
  "config": {
    "start_url": "https://example.com",
    "max_pages": 100
  }
}
```

**Response:**
```json
{
  "job_id": "job_123456",
  "status": "started",
  "message": "Page discovery started",
  "websocket_channel": "/ws/jobs/job_123456"
}
```

### Pages

#### List Pages
```http
GET /api/v1/websites/{website_id}/pages
```

**Query Parameters:**
- `status` (string): tested|untested|error|all
- `has_violations` (bool): Filter by violation presence

**Response:**
```json
{
  "pages": [
    {
      "id": "507f1f77bcf86cd799439013",
      "url": "https://example.com/about",
      "title": "About Us",
      "discovered_at": "2024-01-15T11:00:00Z",
      "last_tested": "2024-01-16T14:00:00Z",
      "status": "tested",
      "violation_count": 5,
      "warning_count": 2
    }
  ]
}
```

#### Add Page Manually
```http
POST /api/v1/websites/{website_id}/pages
```

**Request Body:**
```json
{
  "url": "https://example.com/special-page",
  "priority": "high"
}
```

### Testing

#### Run Tests on Page
```http
POST /api/v1/pages/{page_id}/test
```

**Request Body:**
```json
{
  "config": {
    "run_js_tests": true,
    "run_ai_analysis": true,
    "ai_prompts": ["headings", "reading_order", "modals"],
    "viewport": {
      "width": 1920,
      "height": 1080
    },
    "wait_for": "networkidle2"
  }
}
```

**Response:**
```json
{
  "job_id": "test_789012",
  "status": "queued",
  "websocket_channel": "/ws/tests/test_789012"
}
```

#### Run Batch Tests
```http
POST /api/v1/websites/{website_id}/test
```

**Request Body:**
```json
{
  "page_ids": ["id1", "id2", "id3"],  // or "all"
  "config": {
    "parallel": 5,
    "continue_on_error": true
  }
}
```

#### Get Test Result
```http
GET /api/v1/test-results/{result_id}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439014",
  "page_id": "507f1f77bcf86cd799439013",
  "test_date": "2024-01-16T14:00:00Z",
  "duration_ms": 3456,
  "violations": [
    {
      "id": "image-alt",
      "impact": "critical",
      "description": "Images must have alternate text",
      "help_url": "https://dequeuniversity.com/rules/axe/4.8/image-alt",
      "nodes": [
        {
          "xpath": "/html/body/img[1]",
          "html": "<img src=\"logo.png\">",
          "failure_summary": "Fix any of the following: Image does not have an alt attribute"
        }
      ]
    }
  ],
  "warnings": [...],
  "passes": [...],
  "ai_findings": [
    {
      "type": "heading_mismatch",
      "severity": "serious",
      "description": "Visual heading 'Welcome' at coordinates (100, 200) is not marked up as a heading",
      "suggested_fix": "Wrap text in appropriate heading tag (likely <h2>)",
      "confidence": 0.95
    }
  ],
  "screenshot": "data:image/png;base64,..."
}
```

### Reports

#### Generate Report
```http
POST /api/v1/projects/{project_id}/reports
```

**Request Body:**
```json
{
  "format": "xlsx",  // or "html" or "json" or "pdf"
  "include": {
    "executive_summary": true,
    "detailed_findings": true,
    "screenshots": false,
    "remediation_guidance": true
  },
  "filters": {
    "min_impact": "moderate",
    "categories": ["images", "forms", "headings"]
  }
}
```

**Response:**
```json
{
  "report_id": "report_345678",
  "status": "generating",
  "download_url": "/api/v1/reports/report_345678/download",
  "expires_at": "2024-01-17T14:00:00Z"
}
```

#### Download Report
```http
GET /api/v1/reports/{report_id}/download
```

Returns the file with appropriate content-type.

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.send(JSON.stringify({
  action: 'subscribe',
  channels: ['jobs/job_123456', 'tests/test_789012']
}));
```

### Event Types

#### Page Discovery Events
```json
{
  "event": "discovery.progress",
  "data": {
    "job_id": "job_123456",
    "pages_found": 45,
    "pages_queued": 120,
    "current_depth": 2,
    "status": "crawling"
  }
}
```

```json
{
  "event": "discovery.page_found",
  "data": {
    "url": "https://example.com/new-page",
    "title": "New Page",
    "linked_from": "https://example.com/index"
  }
}
```

#### Testing Events
```json
{
  "event": "test.started",
  "data": {
    "test_id": "test_789012",
    "page_url": "https://example.com/about",
    "timestamp": "2024-01-16T14:00:00Z"
  }
}
```

```json
{
  "event": "test.progress",
  "data": {
    "test_id": "test_789012",
    "phase": "running_js_tests",  // or "taking_screenshot", "ai_analysis"
    "progress_percent": 45
  }
}
```

```json
{
  "event": "test.violation_found",
  "data": {
    "test_id": "test_789012",
    "violation": {
      "id": "color-contrast",
      "impact": "serious",
      "count": 3
    }
  }
}
```

```json
{
  "event": "test.completed",
  "data": {
    "test_id": "test_789012",
    "result_id": "507f1f77bcf86cd799439014",
    "summary": {
      "violations": 12,
      "warnings": 5,
      "passes": 45
    }
  }
}
```

## Data Models

### Project Model
```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ProjectStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PAUSED = "paused"

@dataclass
class Project:
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: ProjectStatus
    websites: List['Website']
    config: dict
```

### Website Model
```python
@dataclass
class Website:
    id: str
    project_id: str
    name: str
    url: str
    created_at: datetime
    last_tested: Optional[datetime]
    page_count: int
    scraping_config: 'ScrapingConfig'
```

### Page Model
```python
class PageStatus(Enum):
    DISCOVERED = "discovered"
    TESTING = "testing"
    TESTED = "tested"
    ERROR = "error"

@dataclass
class Page:
    id: str
    website_id: str
    url: str
    title: Optional[str]
    discovered_at: datetime
    last_tested: Optional[datetime]
    status: PageStatus
    violation_count: int
    warning_count: int
    priority: str  # high, medium, low
```

### Test Result Model
```python
class ImpactLevel(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SERIOUS = "serious"
    CRITICAL = "critical"

@dataclass
class Violation:
    id: str
    impact: ImpactLevel
    description: str
    help_url: str
    nodes: List['NodeViolation']
    
@dataclass
class TestResult:
    id: str
    page_id: str
    test_date: datetime
    duration_ms: int
    violations: List[Violation]
    warnings: List[Violation]
    passes: List[dict]
    ai_findings: List['AIFinding']
    screenshot_url: Optional[str]
    metadata: dict
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid project name",
    "details": {
      "field": "name",
      "reason": "Name must be between 3 and 100 characters"
    }
  },
  "request_id": "req_abc123"
}
```

### Error Codes
- `VALIDATION_ERROR` - Invalid input data
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource already exists
- `UNAUTHORIZED` - Authentication required
- `FORBIDDEN` - Insufficient permissions
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error
- `SERVICE_UNAVAILABLE` - Temporary unavailability

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

## Authentication

### API Key Authentication
```http
GET /api/v1/projects
Authorization: Bearer YOUR_API_KEY
```

### Session Authentication
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2024-01-17T14:00:00Z",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "role": "admin"
  }
}
```

## Rate Limiting

### Default Limits
- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Testing**: 10 concurrent tests
- **Scraping**: 1 request/second per domain

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642428000
```

### Rate Limit Response
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "retry_after": 3600
  }
}
```

## Pagination

### Request Parameters
```
?page=2&limit=50&sort=created_at:desc
```

### Response Format
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 245,
    "pages": 5,
    "has_next": true,
    "has_prev": true,
    "next_url": "/api/v1/resource?page=3&limit=50",
    "prev_url": "/api/v1/resource?page=1&limit=50"
  }
}
```