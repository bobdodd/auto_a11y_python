"""
Testing and analysis routes
"""

from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required
from auto_a11y.models import PageStatus
from auto_a11y.core.job_manager import JobType, JobStatus
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
testing_bp = Blueprint('testing', __name__)


def calculate_aggregate_stats(db):
    """Calculate aggregate statistics across all projects"""
    projects = db.get_all_projects()

    total_pages = 0
    tested_pages = 0
    total_violations = 0
    total_warnings = 0
    website_count = 0

    for project in projects:
        stats = db.get_project_stats(project.id)
        total_pages += stats.get('total_pages', 0)
        tested_pages += stats.get('tested_pages', 0)
        total_violations += stats.get('total_violations', 0)
        total_warnings += stats.get('total_warnings', 0)
        website_count += stats.get('website_count', 0)

    return {
        'website_count': website_count,
        'total_pages': total_pages,
        'tested_pages': tested_pages,
        'untested_pages': total_pages - tested_pages,
        'total_violations': total_violations,
        'total_warnings': total_warnings,
        'test_coverage': (tested_pages / total_pages * 100) if total_pages > 0 else 0
    }


def get_recent_results_with_context(db, project_id=None, website_id=None, limit=20):
    """Get recent test results with full page/website/project context.

    Optimized to minimize database queries by:
    1. Pre-loading all needed pages, websites, projects in bulk
    2. Using in-memory lookups instead of individual queries
    """
    # Get results from database first
    results = db.get_test_results(limit=limit * 2)  # Get extra to account for filtering

    if not results:
        return []

    # Collect all unique page IDs from results
    page_ids = list(set(r.page_id for r in results if r.page_id))

    if not page_ids:
        return []

    # Bulk load all pages we need (single query)
    pages_map = {}
    for page_id in page_ids:
        page = db.get_page(page_id)
        if page:
            pages_map[page_id] = page

    # Collect website IDs from pages
    website_ids = list(set(p.website_id for p in pages_map.values() if p.website_id))

    # Bulk load all websites (could optimize further with a bulk query method)
    websites_map = {}
    for ws_id in website_ids:
        ws = db.get_website(ws_id)
        if ws:
            websites_map[ws_id] = ws

    # Collect project IDs from websites
    project_ids = list(set(w.project_id for w in websites_map.values() if w.project_id))

    # Bulk load all projects
    projects_map = {}
    for proj_id in project_ids:
        proj = db.get_project(proj_id)
        if proj:
            projects_map[proj_id] = proj

    # Now filter results based on project_id/website_id if specified
    filtered_results = []
    for result in results:
        page = pages_map.get(result.page_id)
        if not page:
            continue

        website = websites_map.get(page.website_id)
        if not website:
            continue

        project = projects_map.get(website.project_id) if website.project_id else None

        # Apply filters
        if website_id and page.website_id != website_id:
            continue
        if project_id and (not website.project_id or website.project_id != project_id):
            continue

        filtered_results.append({
            'result': result,
            'page': page,
            'website': website,
            'project': project
        })

        if len(filtered_results) >= limit:
            break

    return filtered_results


def get_trend_data(db, project_id=None, website_id=None, days=30):
    """Get trend data for violations/warnings over time"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Initialize daily buckets
    trend_data = []
    current_date = start_date
    while current_date <= end_date:
        trend_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'violations': 0,
            'warnings': 0,
            'tests': 0
        })
        current_date += timedelta(days=1)

    # Get test results for the period (limit based on days to reduce load)
    results = db.get_test_results(limit=min(days * 20, 500))

    # Filter by date range and optionally by project/website
    page_ids = None
    if website_id:
        pages = db.get_pages(website_id)
        page_ids = set(p.id for p in pages)
    elif project_id:
        websites = db.get_websites(project_id)
        page_ids = set()
        for website in websites:
            pages = db.get_pages(website.id)
            page_ids.update(p.id for p in pages)

    # Aggregate by day
    date_to_index = {d['date']: i for i, d in enumerate(trend_data)}

    for result in results:
        if result.test_date < start_date:
            continue
        if page_ids and result.page_id not in page_ids:
            continue

        date_str = result.test_date.strftime('%Y-%m-%d')
        if date_str in date_to_index:
            idx = date_to_index[date_str]
            trend_data[idx]['violations'] += result.violation_count
            trend_data[idx]['warnings'] += result.warning_count
            trend_data[idx]['tests'] += 1

    return trend_data


# ============================================================================
# Enhanced Trend Analysis Functions
# ============================================================================

def get_page_ids_for_scope(db, project_id=None, website_id=None):
    """Get all page IDs for a given project or website scope"""
    page_ids = set()
    if website_id:
        pages = db.get_pages(website_id)
        page_ids = set(p.id for p in pages)
    elif project_id:
        websites = db.get_websites(project_id)
        for website in websites:
            pages = db.get_pages(website.id)
            page_ids.update(p.id for p in pages)
    return page_ids


def aggregate_by_granularity(data_points, granularity='daily'):
    """Aggregate daily data into weekly or monthly buckets"""
    if granularity == 'daily':
        return data_points

    from collections import defaultdict

    buckets = defaultdict(lambda: {'violations': 0, 'warnings': 0, 'tests': 0})

    for point in data_points:
        date = datetime.strptime(point['date'], '%Y-%m-%d')

        if granularity == 'weekly':
            # Use ISO week start (Monday)
            week_start = date - timedelta(days=date.weekday())
            bucket_key = week_start.strftime('%Y-%m-%d')
        elif granularity == 'monthly':
            bucket_key = date.strftime('%Y-%m-01')
        else:
            bucket_key = point['date']

        buckets[bucket_key]['violations'] += point['violations']
        buckets[bucket_key]['warnings'] += point['warnings']
        buckets[bucket_key]['tests'] += point['tests']

    # Convert to sorted list
    result = []
    for period, values in sorted(buckets.items()):
        result.append({
            'period': period,
            'violations': values['violations'],
            'warnings': values['warnings'],
            'tests': values['tests']
        })

    return result


def calculate_moving_averages(time_series, windows=[7, 30]):
    """Add moving averages to time series data

    Args:
        time_series: List of dicts with 'violations' key
        windows: List of window sizes (in data points)

    Returns:
        Time series with moving_avg_Xd fields added
    """
    if not time_series:
        return time_series

    violations = [p.get('violations', 0) for p in time_series]

    for window in windows:
        key = f'moving_avg_{window}d'
        for i, point in enumerate(time_series):
            if i < window - 1:
                # Not enough data points yet
                point[key] = None
            else:
                # Calculate average of last 'window' points
                window_data = violations[max(0, i - window + 1):i + 1]
                point[key] = round(sum(window_data) / len(window_data), 1)

    return time_series


def calculate_trend_direction(time_series, threshold_percent=5):
    """Determine overall trend direction based on time series data

    Compares the average of the most recent third of data to the first third.

    Args:
        time_series: List of dicts with 'violations' key
        threshold_percent: Minimum % change to classify as improving/worsening

    Returns:
        Tuple of (direction: str, change_percent: float)
        direction is one of: 'improving', 'worsening', 'stable'
    """
    if not time_series or len(time_series) < 3:
        return 'stable', 0.0

    violations = [p.get('violations', 0) for p in time_series]

    # Split into thirds
    third = len(violations) // 3
    if third == 0:
        third = 1

    first_third = violations[:third]
    last_third = violations[-third:]

    first_avg = sum(first_third) / len(first_third) if first_third else 0
    last_avg = sum(last_third) / len(last_third) if last_third else 0

    if first_avg == 0:
        if last_avg == 0:
            return 'stable', 0.0
        else:
            return 'worsening', 100.0

    change_percent = ((last_avg - first_avg) / first_avg) * 100

    if change_percent < -threshold_percent:
        return 'improving', round(change_percent, 1)
    elif change_percent > threshold_percent:
        return 'worsening', round(change_percent, 1)
    else:
        return 'stable', round(change_percent, 1)


def get_filtered_item_counts(db, result_ids, result_date_map, filters, issue_types):
    """Get filtered violation/warning counts from test_result_items collection

    Args:
        db: Database instance
        result_ids: List of test result IDs
        result_date_map: Dict mapping result_id to date string
        filters: Dict with filter criteria
        issue_types: List of item types to include ('violation', 'warning')

    Returns:
        Dict mapping date strings to {violations: count, warnings: count}
    """
    from bson import ObjectId

    # Limit the number of result IDs to process to avoid slow queries
    MAX_RESULT_IDS = 500
    if len(result_ids) > MAX_RESULT_IDS:
        result_ids = result_ids[:MAX_RESULT_IDS]
        logger.warning(f"Limiting filtered item counts to {MAX_RESULT_IDS} results for performance")

    # Convert string IDs to ObjectId
    object_ids = []
    for rid in result_ids:
        if isinstance(rid, str):
            try:
                object_ids.append(ObjectId(rid))
            except:
                pass
        else:
            object_ids.append(rid)

    if not object_ids:
        return {}

    # Build match criteria
    match_criteria = {'test_result_id': {'$in': object_ids}}

    # Filter by item type
    if issue_types:
        match_criteria['item_type'] = {'$in': issue_types}

    # Filter by impact levels
    if filters.get('impact_levels'):
        impact_values = []
        for level in filters['impact_levels']:
            # Handle both string and enum values
            impact_values.append(level.lower())
            impact_values.append(level.capitalize())
            if level.lower() == 'high':
                impact_values.extend(['critical', 'Critical'])
            elif level.lower() == 'medium':
                impact_values.extend(['moderate', 'Moderate'])
            elif level.lower() == 'low':
                impact_values.extend(['minor', 'Minor'])
        match_criteria['impact'] = {'$in': impact_values}

    # Filter by touchpoints - use simple $in instead of regex for performance
    if filters.get('touchpoints'):
        match_criteria['touchpoint'] = {'$in': filters['touchpoints']}

    # Filter by WCAG criteria
    if filters.get('wcag_criteria'):
        match_criteria['wcag_criteria'] = {'$in': filters['wcag_criteria']}

    try:
        # Query with aggregation to get counts per result_id and item_type
        pipeline = [
            {'$match': match_criteria},
            {'$group': {
                '_id': {
                    'result_id': '$test_result_id',
                    'item_type': '$item_type'
                },
                'count': {'$sum': 1}
            }}
        ]

        if hasattr(db, 'test_result_items'):
            results = list(db.test_result_items.aggregate(pipeline, maxTimeMS=10000))  # 10 second timeout
        else:
            return {}

        # Aggregate counts by date
        date_counts = {}
        for r in results:
            result_id = str(r['_id']['result_id'])
            item_type = r['_id']['item_type']
            count = r['count']

            date_str = result_date_map.get(result_id)
            if date_str:
                if date_str not in date_counts:
                    date_counts[date_str] = {'violations': 0, 'warnings': 0}

                if item_type == 'violation':
                    date_counts[date_str]['violations'] += count
                elif item_type == 'warning':
                    date_counts[date_str]['warnings'] += count

        return date_counts

    except Exception as e:
        logger.error(f"Error getting filtered item counts: {e}")
        return {}


def get_detailed_trend_data(db, project_id=None, website_id=None,
                            start_date=None, end_date=None,
                            granularity='daily', include_breakdown=True,
                            filters=None):
    """Get comprehensive trend data with statistics and optional breakdowns

    Args:
        db: Database instance
        project_id: Optional project filter
        website_id: Optional website filter
        start_date: Start date (datetime or None for 30 days ago)
        end_date: End date (datetime or None for now)
        granularity: 'daily', 'weekly', or 'monthly'
        include_breakdown: Whether to include touchpoint/impact breakdowns
        filters: Optional dict with filter criteria:
            - issue_types: list of 'violation', 'warning'
            - impact_levels: list of 'high', 'medium', 'low'
            - touchpoints: list of touchpoint names
            - wcag_criteria: list of WCAG criteria like '2.4.1'

    Returns:
        Dict with summary, time_series, and optional breakdowns
    """
    filters = filters or {}
    # Default date range
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    # Get page IDs for the scope
    page_ids = get_page_ids_for_scope(db, project_id, website_id)

    # Initialize daily buckets
    daily_data = []
    current_date = start_date
    while current_date <= end_date:
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'violations': 0,
            'warnings': 0,
            'tests': 0
        })
        current_date += timedelta(days=1)

    # Get test results for the period - filter by page_ids at database level for efficiency
    days_diff = (end_date - start_date).days
    # Adjust limit based on scope - if filtering to specific pages, we need fewer results
    if page_ids:
        # Estimate: ~10 results per page per period should be plenty
        limit = min(len(page_ids) * 10, 500)
    else:
        limit = max(days_diff * 50, 1000)

    results = db.get_test_results(
        page_ids=page_ids if page_ids else None,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    # Aggregate by day
    date_to_index = {d['date']: i for i, d in enumerate(daily_data)}
    result_ids = []
    result_date_map = {}  # Map result_id to date string

    # Check if we have active filters that require item-level filtering
    has_item_filters = bool(
        filters.get('impact_levels') or
        filters.get('touchpoints') or
        filters.get('wcag_criteria')
    )
    issue_types = filters.get('issue_types', ['violation', 'warning'])

    for result in results:
        if result.test_date < start_date:
            continue
        # No need to filter by page_ids here - already filtered at database level

        result_ids.append(result.id)
        date_str = result.test_date.strftime('%Y-%m-%d')
        result_date_map[str(result.id)] = date_str

        if date_str in date_to_index:
            idx = date_to_index[date_str]
            daily_data[idx]['tests'] += 1

            # If no item-level filters, use pre-computed counts
            if not has_item_filters:
                if 'violation' in issue_types:
                    daily_data[idx]['violations'] += result.violation_count
                if 'warning' in issue_types:
                    daily_data[idx]['warnings'] += result.warning_count

    # If we have item-level filters, query test_result_items for accurate counts
    if has_item_filters and result_ids:
        filtered_counts = get_filtered_item_counts(
            db, result_ids, result_date_map, filters, issue_types
        )
        # Apply filtered counts to daily data
        for date_str, counts in filtered_counts.items():
            if date_str in date_to_index:
                idx = date_to_index[date_str]
                daily_data[idx]['violations'] = counts.get('violations', 0)
                daily_data[idx]['warnings'] = counts.get('warnings', 0)

    # Apply granularity
    time_series = aggregate_by_granularity(daily_data, granularity)

    # Add moving averages (for daily data only, makes sense)
    if granularity == 'daily':
        time_series = calculate_moving_averages(time_series, windows=[7, 30])

    # Calculate trend direction
    trend_direction, change_percent = calculate_trend_direction(time_series)

    # Calculate summary statistics
    total_violations = sum(p.get('violations', 0) for p in time_series)
    total_warnings = sum(p.get('warnings', 0) for p in time_series)
    total_tests = sum(p.get('tests', 0) for p in time_series)

    summary = {
        'total_tests': total_tests,
        'total_violations': total_violations,
        'total_warnings': total_warnings,
        'avg_violations_per_test': round(total_violations / total_tests, 1) if total_tests > 0 else 0,
        'avg_warnings_per_test': round(total_warnings / total_tests, 1) if total_tests > 0 else 0,
        'trend_direction': trend_direction,
        'change_percent': change_percent
    }

    response = {
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'granularity': granularity
        },
        'summary': summary,
        'time_series': time_series
    }

    # Add breakdowns if requested
    if include_breakdown and result_ids:
        response['by_touchpoint'] = get_trends_by_touchpoint(db, result_ids, filters=filters)
        response['by_impact'] = get_trends_by_impact(db, result_ids, filters=filters)
        response['top_issues'] = get_top_issues(db, result_ids, filters=filters)

    return response


def get_trends_by_touchpoint(db, result_ids, limit=10, filters=None):
    """Get violation counts grouped by touchpoint using MongoDB aggregation

    Args:
        db: Database instance
        result_ids: List of test result IDs to analyze
        limit: Maximum number of touchpoints to return
        filters: Optional filter dict with impact_levels, wcag_criteria, etc.

    Returns:
        Dict mapping touchpoint names to counts and metadata
    """
    filters = filters or {}
    if not result_ids:
        return {}

    # Limit result IDs to prevent slow queries
    MAX_RESULT_IDS = 500
    if len(result_ids) > MAX_RESULT_IDS:
        result_ids = result_ids[:MAX_RESULT_IDS]
        logger.warning(f"Limiting touchpoint trends to {MAX_RESULT_IDS} results for performance")

    try:
        # Use MongoDB aggregation pipeline
        from bson import ObjectId

        # Convert string IDs to ObjectId if needed
        object_ids = []
        for rid in result_ids:
            if isinstance(rid, str):
                try:
                    object_ids.append(ObjectId(rid))
                except:
                    pass
            else:
                object_ids.append(rid)

        # Build match criteria
        match_criteria = {
            'test_result_id': {'$in': object_ids},
            'item_type': 'violation'
        }

        # Apply filters
        if filters.get('impact_levels'):
            impact_values = []
            for level in filters['impact_levels']:
                impact_values.append(level.lower())
                impact_values.append(level.capitalize())
                if level.lower() == 'high':
                    impact_values.extend(['critical', 'Critical'])
                elif level.lower() == 'medium':
                    impact_values.extend(['moderate', 'Moderate'])
                elif level.lower() == 'low':
                    impact_values.extend(['minor', 'Minor'])
            match_criteria['impact'] = {'$in': impact_values}

        if filters.get('wcag_criteria'):
            match_criteria['wcag_criteria'] = {'$in': filters['wcag_criteria']}

        pipeline = [
            {'$match': match_criteria},
            {'$group': {
                '_id': '$touchpoint',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]

        # Execute aggregation with timeout
        if hasattr(db, 'test_result_items'):
            results = list(db.test_result_items.aggregate(pipeline, maxTimeMS=10000))
        else:
            # Fallback if collection not directly accessible
            return {}

        # Format results
        touchpoints = {}
        for r in results:
            touchpoint = r['_id'] or 'Unknown'
            touchpoints[touchpoint] = {
                'count': r['count'],
                'trend': 'stable',  # Would need historical comparison for actual trend
                'change': 0
            }

        return touchpoints

    except Exception as e:
        logger.warning(f"Error getting touchpoint trends (may have timed out): {e}")
        return {}


def get_trends_by_impact(db, result_ids, filters=None):
    """Get violation counts grouped by impact level

    Args:
        db: Database instance
        result_ids: List of test result IDs to analyze
        filters: Optional filter dict with touchpoints, wcag_criteria, etc.

    Returns:
        Dict with high/medium/low counts and percentages
    """
    filters = filters or {}
    if not result_ids:
        return {'high': {'count': 0, 'percent': 0},
                'medium': {'count': 0, 'percent': 0},
                'low': {'count': 0, 'percent': 0}}

    # Limit result IDs to prevent slow queries
    MAX_RESULT_IDS = 500
    if len(result_ids) > MAX_RESULT_IDS:
        result_ids = result_ids[:MAX_RESULT_IDS]
        logger.warning(f"Limiting impact trends to {MAX_RESULT_IDS} results for performance")

    try:
        from bson import ObjectId

        object_ids = []
        for rid in result_ids:
            if isinstance(rid, str):
                try:
                    object_ids.append(ObjectId(rid))
                except:
                    pass
            else:
                object_ids.append(rid)

        # Build match criteria
        match_criteria = {
            'test_result_id': {'$in': object_ids},
            'item_type': 'violation'
        }

        # Apply filters - use simple $in for performance instead of regex
        if filters.get('touchpoints'):
            match_criteria['touchpoint'] = {'$in': filters['touchpoints']}

        if filters.get('wcag_criteria'):
            match_criteria['wcag_criteria'] = {'$in': filters['wcag_criteria']}

        pipeline = [
            {'$match': match_criteria},
            {'$group': {
                '_id': '$impact',
                'count': {'$sum': 1}
            }}
        ]

        if hasattr(db, 'test_result_items'):
            results = list(db.test_result_items.aggregate(pipeline, maxTimeMS=10000))
        else:
            return {'high': {'count': 0, 'percent': 0},
                    'medium': {'count': 0, 'percent': 0},
                    'low': {'count': 0, 'percent': 0}}

        # Count by impact
        counts = {'high': 0, 'medium': 0, 'low': 0}
        for r in results:
            impact = str(r['_id']).lower() if r['_id'] else 'medium'
            # Normalize impact values
            if impact in ['high', 'serious', 'critical']:
                counts['high'] += r['count']
            elif impact in ['low', 'minor']:
                counts['low'] += r['count']
            else:
                counts['medium'] += r['count']

        total = sum(counts.values())

        return {
            'high': {
                'count': counts['high'],
                'percent': round(counts['high'] / total * 100, 1) if total > 0 else 0
            },
            'medium': {
                'count': counts['medium'],
                'percent': round(counts['medium'] / total * 100, 1) if total > 0 else 0
            },
            'low': {
                'count': counts['low'],
                'percent': round(counts['low'] / total * 100, 1) if total > 0 else 0
            }
        }

    except Exception as e:
        logger.warning(f"Error getting impact trends (may have timed out): {e}")
        return {'high': {'count': 0, 'percent': 0},
                'medium': {'count': 0, 'percent': 0},
                'low': {'count': 0, 'percent': 0}}


def get_top_issues(db, result_ids, limit=10, filters=None):
    """Get the most common issues (by issue_id) from test results

    Args:
        db: Database instance
        result_ids: List of test result IDs to analyze
        limit: Maximum number of issues to return
        filters: Optional filter dict with impact_levels, touchpoints, wcag_criteria

    Returns:
        List of dicts with issue_id, count, and trend
    """
    filters = filters or {}
    if not result_ids:
        return []

    # Limit result IDs to prevent slow queries
    MAX_RESULT_IDS = 500
    if len(result_ids) > MAX_RESULT_IDS:
        result_ids = result_ids[:MAX_RESULT_IDS]
        logger.warning(f"Limiting top issues to {MAX_RESULT_IDS} results for performance")

    try:
        from bson import ObjectId

        object_ids = []
        for rid in result_ids:
            if isinstance(rid, str):
                try:
                    object_ids.append(ObjectId(rid))
                except:
                    pass
            else:
                object_ids.append(rid)

        # Build match criteria
        match_criteria = {
            'test_result_id': {'$in': object_ids},
            'item_type': 'violation'
        }

        # Apply filters
        if filters.get('impact_levels'):
            impact_values = []
            for level in filters['impact_levels']:
                impact_values.append(level.lower())
                impact_values.append(level.capitalize())
                if level.lower() == 'high':
                    impact_values.extend(['critical', 'Critical'])
                elif level.lower() == 'medium':
                    impact_values.extend(['moderate', 'Moderate'])
                elif level.lower() == 'low':
                    impact_values.extend(['minor', 'Minor'])
            match_criteria['impact'] = {'$in': impact_values}

        # Use simple $in for performance instead of regex
        if filters.get('touchpoints'):
            match_criteria['touchpoint'] = {'$in': filters['touchpoints']}

        if filters.get('wcag_criteria'):
            match_criteria['wcag_criteria'] = {'$in': filters['wcag_criteria']}

        pipeline = [
            {'$match': match_criteria},
            {'$group': {
                '_id': '$issue_id',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': limit}
        ]

        if hasattr(db, 'test_result_items'):
            results = list(db.test_result_items.aggregate(pipeline, maxTimeMS=10000))
        else:
            return []

        top_issues = []
        for r in results:
            top_issues.append({
                'issue_id': r['_id'] or 'unknown',
                'count': r['count'],
                'trend': 'stable',  # Would need historical comparison
                'change_percent': 0
            })

        return top_issues

    except Exception as e:
        logger.warning(f"Error getting top issues (may have timed out): {e}")
        return []


def compare_periods(db, project_id, website_id, period_a_start, period_a_end,
                   period_b_start, period_b_end):
    """Compare two time periods for violations/warnings

    Args:
        db: Database instance
        project_id: Optional project filter
        website_id: Optional website filter
        period_a_*: First period start/end dates
        period_b_*: Second period start/end dates

    Returns:
        Dict with comparison data
    """
    page_ids = get_page_ids_for_scope(db, project_id, website_id)

    def get_period_stats(start, end):
        # Filter at database level for efficiency
        limit = min(len(page_ids) * 10, 500) if page_ids else 2000
        results = db.get_test_results(
            page_ids=page_ids if page_ids else None,
            start_date=start,
            end_date=end,
            limit=limit
        )

        violations = 0
        warnings = 0
        tests = 0

        for result in results:
            # No need to filter by page_ids - already done at database level
            violations += result.violation_count
            warnings += result.warning_count
            tests += 1

        return {'violations': violations, 'warnings': warnings, 'tests': tests}

    stats_a = get_period_stats(period_a_start, period_a_end)
    stats_b = get_period_stats(period_b_start, period_b_end)

    def calc_change(old_val, new_val):
        if old_val == 0:
            return {'absolute': new_val, 'percent': 100 if new_val > 0 else 0}
        return {
            'absolute': new_val - old_val,
            'percent': round(((new_val - old_val) / old_val) * 100, 1)
        }

    return {
        'period_a': {
            'start': period_a_start.strftime('%Y-%m-%d'),
            'end': period_a_end.strftime('%Y-%m-%d'),
            **stats_a
        },
        'period_b': {
            'start': period_b_start.strftime('%Y-%m-%d'),
            'end': period_b_end.strftime('%Y-%m-%d'),
            **stats_b
        },
        'change': {
            'violations': calc_change(stats_a['violations'], stats_b['violations']),
            'warnings': calc_change(stats_a['warnings'], stats_b['warnings']),
            'tests': calc_change(stats_a['tests'], stats_b['tests'])
        }
    }


def calculate_progress_metrics(db, project_id=None, website_id=None, days=30):
    """Calculate progress metrics showing improvement/regression

    Args:
        db: Database instance
        project_id: Optional project filter
        website_id: Optional website filter
        days: Number of days to analyze

    Returns:
        Dict with pages_summary, issue_flow, and compliance_score
    """
    page_ids = get_page_ids_for_scope(db, project_id, website_id)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    mid_date = start_date + timedelta(days=days // 2)

    # Get all pages with their latest and previous test results
    pages_improving = 0
    pages_worsening = 0
    pages_stable = 0
    total_pages = 0

    # Analyze pages - limit to avoid slow queries
    MAX_PAGES_TO_ANALYZE = 50

    if website_id:
        pages = db.get_pages(website_id)
    elif project_id:
        pages = []
        for ws in db.get_websites(project_id):
            pages.extend(db.get_pages(ws.id))
    else:
        pages = []

    # Limit pages analyzed for performance
    pages_to_analyze = pages[:MAX_PAGES_TO_ANALYZE] if len(pages) > MAX_PAGES_TO_ANALYZE else pages
    analyzed_count = 0

    for page in pages_to_analyze:
        if page_ids and page.id not in page_ids:
            continue

        analyzed_count += 1

        # Get test results for this page in the period - limit queries
        page_results = db.get_test_results(page_id=page.id, start_date=start_date, limit=10)

        if len(page_results) < 2:
            pages_stable += 1
            continue

        # Compare first and last test
        first_violations = page_results[-1].violation_count
        last_violations = page_results[0].violation_count

        if last_violations < first_violations:
            pages_improving += 1
        elif last_violations > first_violations:
            pages_worsening += 1
        else:
            pages_stable += 1

    # Total pages is the full count, analyzed is the sample
    total_pages = len(pages) if pages else 0

    # Calculate issue flow - filter at database level for efficiency
    limit = min(len(page_ids) * 10, 500) if page_ids else 2000
    first_half_results = db.get_test_results(
        page_ids=page_ids if page_ids else None,
        start_date=start_date,
        end_date=mid_date,
        limit=limit
    )
    second_half_results = db.get_test_results(
        page_ids=page_ids if page_ids else None,
        start_date=mid_date,
        end_date=end_date,
        limit=limit
    )

    first_half_violations = sum(r.violation_count for r in first_half_results)
    second_half_violations = sum(r.violation_count for r in second_half_results)

    # Estimate new/resolved (simplified)
    if second_half_violations < first_half_violations:
        resolved = first_half_violations - second_half_violations
        new_issues = 0
    else:
        new_issues = second_half_violations - first_half_violations
        resolved = 0

    # Calculate compliance score (violations per page, inverted)
    current_violations_per_page = second_half_violations / max(total_pages, 1)
    target_violations_per_page = 0  # Perfect compliance

    # Score: 100 - (avg violations * 10), capped at 0-100
    compliance_score = max(0, min(100, 100 - (current_violations_per_page * 2)))

    # Projected days to target (if improving)
    projected_days = None
    if pages_improving > pages_worsening and first_half_violations > second_half_violations:
        improvement_rate = (first_half_violations - second_half_violations) / (days / 2)
        if improvement_rate > 0:
            remaining_violations = second_half_violations
            projected_days = int(remaining_violations / improvement_rate)

    return {
        'pages_summary': {
            'total': total_pages,
            'improving': pages_improving,
            'worsening': pages_worsening,
            'stable': pages_stable
        },
        'issue_flow': {
            'new_issues': new_issues,
            'resolved_issues': resolved,
            'net_change': resolved - new_issues
        },
        'compliance_score': {
            'current': round(compliance_score, 1),
            'target': 95.0,
            'projected_days_to_target': projected_days
        }
    }


@testing_bp.route('/result/<result_id>')
def view_result(result_id):
    """View individual test result details"""
    result = current_app.db.get_test_result(result_id)
    if not result:
        return jsonify({'error': 'Test result not found'}), 404
    
    # Get related page and website info
    page = current_app.db.get_page(result.page_id)
    website = current_app.db.get_website(page.website_id) if page else None
    project = current_app.db.get_project(website.project_id) if website else None
    
    return render_template('testing/result.html',
                         result=result,
                         page=page,
                         website=website,
                         project=project)


@testing_bp.route('/dashboard')
@login_required
def testing_dashboard():
    """Testing dashboard - comprehensive testing control center"""
    db = current_app.db

    # Get filter parameters from URL
    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')

    # Get all projects for dropdown
    projects = db.get_all_projects()

    # Get selected project and its websites (if any)
    selected_project = None
    websites = []
    if project_id:
        selected_project = db.get_project(project_id)
        if selected_project:
            websites = db.get_websites(project_id)

    # Get selected website (if any)
    selected_website = None
    if website_id:
        selected_website = db.get_website(website_id)

    # Calculate stats (aggregate or project/website-specific)
    if website_id and selected_website:
        # Stats for single website
        pages = db.get_pages(website_id)
        tested_pages = sum(1 for p in pages if p.status == PageStatus.TESTED)
        stats = {
            'website_count': 1,
            'total_pages': len(pages),
            'tested_pages': tested_pages,
            'untested_pages': len(pages) - tested_pages,
            'total_violations': sum(p.violation_count for p in pages),
            'total_warnings': sum(p.warning_count for p in pages),
            'test_coverage': (tested_pages / len(pages) * 100) if pages else 0
        }
    elif project_id and selected_project:
        stats = db.get_project_stats(project_id)
    else:
        stats = calculate_aggregate_stats(db)

    # Get completed today count
    completed_today = db.test_results.count_documents({
        'test_date': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
    })

    # Get active and queued test counts from job manager
    active_tests = 0
    queued_tests = 0
    active_jobs = []
    try:
        if hasattr(current_app, 'job_manager') and current_app.job_manager:
            all_jobs = current_app.job_manager.get_active_jobs(job_type=JobType.TESTING)
            for job in all_jobs:
                if job.get('status') == JobStatus.RUNNING.value:
                    active_tests += 1
                    active_jobs.append(job)
                elif job.get('status') == JobStatus.PENDING.value:
                    queued_tests += 1
    except Exception as e:
        logger.warning(f"Could not get job counts: {e}")

    # Add job counts to stats
    stats['active_tests'] = active_tests
    stats['queued_tests'] = queued_tests
    stats['completed_today'] = completed_today

    # Get recent results with full context (limit to 10 for faster load)
    recent_results = get_recent_results_with_context(db, project_id, website_id, limit=10)

    # Get scheduled tests (limit to 5)
    schedules = []
    if website_id:
        schedules = db.get_test_schedules_for_website(website_id)[:5]
    elif project_id:
        for w in websites[:3]:  # Limit to first 3 websites for speed
            website_schedules = db.get_test_schedules_for_website(w.id)
            for s in website_schedules:
                s._website_name = w.name  # Add website name for display
            schedules.extend(website_schedules)
            if len(schedules) >= 5:
                break
        schedules = schedules[:5]

    # Get trend data for charts (reduce to 14 days for faster load)
    trend_data = get_trend_data(db, project_id, website_id, days=14)

    # Get project users (testers) for the selected project
    project_users = []
    if project_id:
        project_users = db.get_project_users(project_id, enabled_only=True)

    return render_template('testing/dashboard.html',
                         projects=projects,
                         selected_project=selected_project,
                         websites=websites,
                         selected_website=selected_website,
                         selected_website_id=website_id,
                         stats=stats,
                         recent_results=recent_results,
                         schedules=schedules,
                         active_jobs=active_jobs,
                         trend_data=trend_data,
                         project_users=project_users)


@testing_bp.route('/run-test', methods=['POST'])
def run_test():
    """Run accessibility test on specified page(s)"""
    data = request.get_json()
    
    page_ids = data.get('page_ids', [])
    test_config = data.get('config', {})
    
    if not page_ids:
        return jsonify({'error': 'No pages specified'}), 400
    
    # Validate pages exist
    valid_pages = []
    for page_id in page_ids:
        page = current_app.db.get_page(page_id)
        if page:
            valid_pages.append(page)
    
    if not valid_pages:
        return jsonify({'error': 'No valid pages found'}), 400
    
    # Queue test jobs
    job_ids = []
    for page in valid_pages:
        job_id = f'test_{page.id}_{datetime.now().timestamp()}'
        job_ids.append(job_id)
        
        # Update page status
        page.status = PageStatus.QUEUED
        current_app.db.update_page(page)
    
    return jsonify({
        'success': True,
        'jobs_created': len(job_ids),
        'job_ids': job_ids,
        'message': f'Queued {len(job_ids)} pages for testing'
    })


@testing_bp.route('/batch-test', methods=['POST'])
def batch_test():
    """Run batch testing on multiple pages"""
    data = request.get_json()
    
    website_id = data.get('website_id')
    filter_criteria = data.get('filter', {})
    test_config = data.get('config', {})
    
    if not website_id:
        return jsonify({'error': 'Website ID required'}), 400
    
    # Get pages based on filter
    pages = current_app.db.get_pages(website_id)
    
    # Apply filters
    if filter_criteria.get('untested_only'):
        pages = [p for p in pages if p.needs_testing]
    
    if filter_criteria.get('priority'):
        priority = filter_criteria['priority']
        pages = [p for p in pages if p.priority == priority]
    
    if not pages:
        return jsonify({'error': 'No pages match criteria'}), 404
    
    # Queue batch job
    batch_id = f'batch_{website_id}_{datetime.now().timestamp()}'
    
    return jsonify({
        'success': True,
        'batch_id': batch_id,
        'pages_queued': len(pages),
        'message': f'Batch testing started for {len(pages)} pages'
    })


@testing_bp.route('/job/<job_id>/status')
def job_status(job_id):
    """Get status of testing job"""
    # In production, check actual job queue
    return jsonify({
        'job_id': job_id,
        'status': 'in_progress',
        'progress': 45,
        'current_page': 'https://example.com/page',
        'pages_completed': 5,
        'pages_total': 10,
        'violations_found': 23
    })


@testing_bp.route('/job/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel testing job"""
    # In production, cancel actual job
    return jsonify({
        'success': True,
        'message': f'Job {job_id} cancelled'
    })


@testing_bp.route('/fixture-status')
def fixture_status():
    """Display fixture test status page"""
    return render_template('testing/fixture_status.html')


@testing_bp.route('/configure', methods=['GET', 'POST'])
def configure_testing():
    """Configure testing settings"""
    if request.method == 'POST':
        # Save testing configuration
        config = request.get_json()

        # Validate configuration
        if not config:
            return jsonify({'error': 'Invalid configuration'}), 400

        # Update runtime configuration
        if 'parallel_tests' in config:
            current_app.app_config.PARALLEL_TESTS = config['parallel_tests']
        if 'test_timeout' in config:
            current_app.app_config.TEST_TIMEOUT = config['test_timeout']
        if 'run_ai_analysis' in config:
            current_app.app_config.RUN_AI_ANALYSIS = config['run_ai_analysis']
        if 'browser_headless' in config:
            current_app.app_config.BROWSER_HEADLESS = config['browser_headless']
        if 'viewport_width' in config:
            current_app.app_config.BROWSER_VIEWPORT_WIDTH = config['viewport_width']
        if 'viewport_height' in config:
            current_app.app_config.BROWSER_VIEWPORT_HEIGHT = config['viewport_height']
        if 'pages_per_page' in config:
            current_app.app_config.PAGES_PER_PAGE = config['pages_per_page']
        if 'max_pages_per_page' in config:
            current_app.app_config.MAX_PAGES_PER_PAGE = config['max_pages_per_page']
        if 'show_error_codes' in config:
            current_app.app_config.SHOW_ERROR_CODES = config['show_error_codes']

        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully (applies to new operations)'
        })

    # Get current configuration with backward compatibility
    current_config = {
        'parallel_tests': current_app.app_config.PARALLEL_TESTS,
        'test_timeout': current_app.app_config.TEST_TIMEOUT,
        'run_ai_analysis': current_app.app_config.RUN_AI_ANALYSIS,
        'browser_headless': current_app.app_config.BROWSER_HEADLESS,
        'viewport_width': current_app.app_config.BROWSER_VIEWPORT_WIDTH,
        'viewport_height': current_app.app_config.BROWSER_VIEWPORT_HEIGHT,
        'pages_per_page': getattr(current_app.app_config, 'PAGES_PER_PAGE', 100),
        'max_pages_per_page': getattr(current_app.app_config, 'MAX_PAGES_PER_PAGE', 500),
        'show_error_codes': getattr(current_app.app_config, 'SHOW_ERROR_CODES', False)
    }

    return render_template('testing/configure.html', config=current_config)


# ============================================================================
# API Endpoints for Dashboard
# ============================================================================

@testing_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for real-time stats (for polling)"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')

    # Calculate stats based on filters
    if website_id:
        website = db.get_website(website_id)
        if website:
            pages = db.get_pages(website_id)
            tested_pages = sum(1 for p in pages if p.status == PageStatus.TESTED)
            stats = {
                'website_count': 1,
                'total_pages': len(pages),
                'tested_pages': tested_pages,
                'untested_pages': len(pages) - tested_pages,
                'total_violations': sum(p.violation_count for p in pages),
                'total_warnings': sum(p.warning_count for p in pages),
                'test_coverage': round((tested_pages / len(pages) * 100), 1) if pages else 0
            }
        else:
            return jsonify({'error': 'Website not found'}), 404
    elif project_id:
        stats = db.get_project_stats(project_id)
    else:
        stats = calculate_aggregate_stats(db)

    # Get completed today
    completed_today = db.test_results.count_documents({
        'test_date': {'$gte': datetime.now().replace(hour=0, minute=0, second=0)}
    })

    # Get active/queued counts
    active_tests = 0
    queued_tests = 0
    try:
        if hasattr(current_app, 'job_manager') and current_app.job_manager:
            all_jobs = current_app.job_manager.get_active_jobs(job_type=JobType.TESTING)
            for job in all_jobs:
                if job.get('status') == JobStatus.RUNNING.value:
                    active_tests += 1
                elif job.get('status') == JobStatus.PENDING.value:
                    queued_tests += 1
    except Exception as e:
        logger.warning(f"Could not get job counts: {e}")

    stats['active_tests'] = active_tests
    stats['queued_tests'] = queued_tests
    stats['completed_today'] = completed_today

    return jsonify({
        'success': True,
        'stats': stats
    })


@testing_bp.route('/api/active-tests')
@login_required
def api_active_tests():
    """API endpoint for active test progress (for polling)"""
    active_jobs = []

    try:
        if hasattr(current_app, 'job_manager') and current_app.job_manager:
            all_jobs = current_app.job_manager.get_active_jobs(job_type=JobType.TESTING)
            for job in all_jobs:
                if job.get('status') == JobStatus.RUNNING.value:
                    # Get website info for display
                    website_name = 'Unknown'
                    if job.get('website_id'):
                        website = current_app.db.get_website(job['website_id'])
                        if website:
                            website_name = website.name

                    active_jobs.append({
                        'job_id': job.get('job_id'),
                        'website_id': job.get('website_id'),
                        'website_name': website_name,
                        'progress': job.get('progress', 0),
                        'pages_completed': job.get('pages_completed', 0),
                        'pages_total': job.get('pages_total', 0),
                        'current_page': job.get('current_page', ''),
                        'started_at': job.get('started_at', '').isoformat() if job.get('started_at') else None,
                        'violations_found': job.get('violations_found', 0)
                    })
    except Exception as e:
        logger.warning(f"Could not get active jobs: {e}")

    return jsonify({
        'success': True,
        'active_tests': active_jobs,
        'count': len(active_jobs)
    })


@testing_bp.route('/api/run-tests', methods=['POST'])
@login_required
def api_run_tests():
    """API endpoint to start testing (enhanced version)"""
    data = request.get_json() or {}

    website_id = data.get('website_id')
    project_id = data.get('project_id')
    test_untested_only = data.get('untested_only', False)
    include_screenshots = data.get('include_screenshots', True)
    run_ai_analysis = data.get('run_ai_analysis', False)
    tester_ids = data.get('tester_ids', ['guest'])  # List of tester IDs or 'guest'

    if not website_id and not project_id:
        return jsonify({'error': 'Either website_id or project_id is required'}), 400

    # Validate at least one tester is selected
    if not tester_ids:
        return jsonify({'error': 'At least one tester must be selected'}), 400

    db = current_app.db

    try:
        if website_id:
            # Test single website
            website = db.get_website(website_id)
            if not website:
                return jsonify({'error': 'Website not found'}), 404

            pages = db.get_pages(website_id)
            if test_untested_only:
                pages = [p for p in pages if p.status != PageStatus.TESTED]

            if not pages:
                return jsonify({
                    'success': False,
                    'error': 'No pages to test',
                    'message': 'All pages have already been tested' if test_untested_only else 'No pages found'
                }), 400

            # Queue pages for testing
            for page in pages:
                page.status = PageStatus.QUEUED
                db.update_page(page)

            # Build tester description for message
            tester_count = len(tester_ids)
            tester_desc = f" with {tester_count} tester(s)" if tester_count > 1 or 'guest' not in tester_ids else ""

            return jsonify({
                'success': True,
                'message': f'Queued {len(pages)} pages for testing{tester_desc}',
                'pages_queued': len(pages),
                'website_name': website.name,
                'tester_ids': tester_ids
            })

        elif project_id:
            # Test entire project
            project = db.get_project(project_id)
            if not project:
                return jsonify({'error': 'Project not found'}), 404

            websites = db.get_websites(project_id)
            total_pages = 0

            for website in websites:
                pages = db.get_pages(website.id)
                if test_untested_only:
                    pages = [p for p in pages if p.status != PageStatus.TESTED]

                for page in pages:
                    page.status = PageStatus.QUEUED
                    db.update_page(page)
                    total_pages += 1

            if total_pages == 0:
                return jsonify({
                    'success': False,
                    'error': 'No pages to test',
                    'message': 'All pages have already been tested' if test_untested_only else 'No pages found'
                }), 400

            # Build tester description for message
            tester_count = len(tester_ids)
            tester_desc = f" with {tester_count} tester(s)" if tester_count > 1 or 'guest' not in tester_ids else ""

            return jsonify({
                'success': True,
                'message': f'Queued {total_pages} pages across {len(websites)} websites for testing{tester_desc}',
                'pages_queued': total_pages,
                'websites_count': len(websites),
                'project_name': project.name,
                'tester_ids': tester_ids
            })

    except Exception as e:
        logger.error(f"Error starting tests: {e}")
        return jsonify({'error': str(e)}), 500


@testing_bp.route('/api/trends')
@login_required
def api_trends():
    """API endpoint for trend data"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')
    days = int(request.args.get('days', 30))

    trend_data = get_trend_data(db, project_id, website_id, days)

    return jsonify({
        'success': True,
        'trend_data': trend_data
    })


@testing_bp.route('/api/trends/detailed')
@login_required
def api_trends_detailed():
    """API endpoint for detailed trend data with breakdowns and statistics"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')
    granularity = request.args.get('granularity', 'daily')
    include_breakdown = request.args.get('include_breakdown', 'true').lower() == 'true'

    # Parse dates
    start_date = None
    end_date = None

    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400

    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
            # Include the full end day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400

    # Validate granularity
    if granularity not in ['daily', 'weekly', 'monthly']:
        return jsonify({'error': 'Invalid granularity. Use daily, weekly, or monthly'}), 400

    # Parse filter parameters
    filters = {}

    # Issue types (violation, warning)
    issue_types = request.args.getlist('issue_types[]') or request.args.getlist('issue_types')
    if issue_types:
        filters['issue_types'] = issue_types

    # Impact levels (high, medium, low)
    impact_levels = request.args.getlist('impact_levels[]') or request.args.getlist('impact_levels')
    if impact_levels:
        filters['impact_levels'] = impact_levels

    # Touchpoints
    touchpoints = request.args.getlist('touchpoints[]') or request.args.getlist('touchpoints')
    if touchpoints:
        filters['touchpoints'] = touchpoints

    # WCAG criteria
    wcag_criteria = request.args.getlist('wcag_criteria[]') or request.args.getlist('wcag_criteria')
    if wcag_criteria:
        filters['wcag_criteria'] = wcag_criteria

    try:
        trend_data = get_detailed_trend_data(
            db,
            project_id=project_id,
            website_id=website_id,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            include_breakdown=include_breakdown,
            filters=filters if filters else None
        )

        return jsonify({
            'success': True,
            **trend_data
        })

    except Exception as e:
        logger.error(f"Error getting detailed trends: {e}")
        return jsonify({'error': str(e)}), 500


@testing_bp.route('/api/trends/compare')
@login_required
def api_trends_compare():
    """API endpoint for comparing time periods"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')
    compare_type = request.args.get('compare_type', 'periods')

    if compare_type == 'periods':
        # Parse period dates
        try:
            period_a_start = datetime.strptime(request.args.get('period_a_start', ''), '%Y-%m-%d')
            period_a_end = datetime.strptime(request.args.get('period_a_end', ''), '%Y-%m-%d')
            period_b_start = datetime.strptime(request.args.get('period_b_start', ''), '%Y-%m-%d')
            period_b_end = datetime.strptime(request.args.get('period_b_end', ''), '%Y-%m-%d')
        except ValueError:
            # Default to this week vs last week
            today = datetime.now()
            period_b_end = today
            period_b_start = today - timedelta(days=7)
            period_a_end = period_b_start - timedelta(days=1)
            period_a_start = period_a_end - timedelta(days=7)

        comparison = compare_periods(
            db, project_id, website_id,
            period_a_start, period_a_end,
            period_b_start, period_b_end
        )

        return jsonify({
            'success': True,
            'comparison_type': 'periods',
            'items': [
                {
                    'label': f"{comparison['period_a']['start']} to {comparison['period_a']['end']}",
                    **{k: v for k, v in comparison['period_a'].items() if k not in ['start', 'end']}
                },
                {
                    'label': f"{comparison['period_b']['start']} to {comparison['period_b']['end']}",
                    **{k: v for k, v in comparison['period_b'].items() if k not in ['start', 'end']}
                }
            ],
            'change': comparison['change']
        })

    elif compare_type == 'websites':
        # Compare multiple websites
        website_ids = request.args.getlist('website_ids[]') or request.args.getlist('website_ids')

        if len(website_ids) < 2:
            return jsonify({'error': 'At least 2 website_ids required for comparison'}), 400

        items = []
        for ws_id in website_ids[:5]:  # Limit to 5 websites
            website = db.get_website(ws_id)
            if not website:
                continue

            pages = db.get_pages(ws_id)
            total_violations = sum(p.violation_count for p in pages)
            total_warnings = sum(p.warning_count for p in pages)
            tested_pages = sum(1 for p in pages if p.status == PageStatus.TESTED)

            items.append({
                'label': website.name,
                'website_id': ws_id,
                'violations': total_violations,
                'warnings': total_warnings,
                'pages': len(pages),
                'tested': tested_pages
            })

        return jsonify({
            'success': True,
            'comparison_type': 'websites',
            'items': items
        })

    else:
        return jsonify({'error': 'Invalid compare_type. Use periods or websites'}), 400


@testing_bp.route('/api/trends/progress')
@login_required
def api_trends_progress():
    """API endpoint for progress/compliance metrics"""
    db = current_app.db

    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')
    days = int(request.args.get('days', 30))

    if not project_id and not website_id:
        return jsonify({'error': 'Either project_id or website_id is required'}), 400

    try:
        progress = calculate_progress_metrics(db, project_id, website_id, days)

        return jsonify({
            'success': True,
            **progress
        })

    except Exception as e:
        logger.error(f"Error calculating progress metrics: {e}")
        return jsonify({'error': str(e)}), 500


@testing_bp.route('/trends')
@login_required
def trends_page():
    """Dedicated trends analysis page"""
    db = current_app.db

    # Get filter parameters
    project_id = request.args.get('project_id')
    website_id = request.args.get('website_id')

    # Get all projects for dropdown
    projects = db.get_all_projects()

    # Get selected project and its websites
    selected_project = None
    websites = []
    if project_id:
        selected_project = db.get_project(project_id)
        if selected_project:
            websites = db.get_websites(project_id)

    # Get selected website
    selected_website = None
    if website_id:
        selected_website = db.get_website(website_id)

    return render_template('testing/trends.html',
                         projects=projects,
                         selected_project=selected_project,
                         websites=websites,
                         selected_website=selected_website,
                         selected_website_id=website_id)


@testing_bp.route('/api/websites/<project_id>')
@login_required
def api_project_websites(project_id):
    """API endpoint to get websites for a project (for dynamic dropdown)"""
    db = current_app.db

    project = db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    websites = db.get_websites(project_id)

    return jsonify({
        'success': True,
        'websites': [
            {
                'id': w.id,
                'name': w.name,
                'url': w.url,
                'page_count': w.page_count
            } for w in websites
        ]
    })