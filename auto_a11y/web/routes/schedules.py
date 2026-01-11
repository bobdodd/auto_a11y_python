"""
Routes for managing test schedules (scheduled accessibility testing)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import current_user
from datetime import datetime
from zoneinfo import ZoneInfo
from auto_a11y.models import (
    TestSchedule, ScheduleType, AITestMode, ScheduleRunStatus,
    ScheduleTestConfig, PresetConfig
)
from auto_a11y.core.scheduler import get_scheduler_service
import logging

logger = logging.getLogger(__name__)

schedules_bp = Blueprint('schedules', __name__)


@schedules_bp.route('/websites/<website_id>/schedules')
def list_schedules(website_id):
    """List all schedules for a website"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    project = current_app.db.get_project(website.project_id)

    # Get all schedules
    schedules = current_app.db.get_test_schedules_for_website(website_id)

    return render_template('schedules/list.html',
                         website=website,
                         project=project,
                         schedules=schedules)


@schedules_bp.route('/websites/<website_id>/schedules/create', methods=['GET', 'POST'])
def create_schedule(website_id):
    """Create a new schedule"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    project = current_app.db.get_project(website.project_id)

    if request.method == 'POST':
        try:
            data = request.form

            # Parse schedule type
            schedule_type_str = data.get('schedule_type', 'daily')
            schedule_type = ScheduleType(schedule_type_str)

            # Parse preset config
            preset_config = PresetConfig(
                time=data.get('time', '02:00'),
                day_of_week=int(data.get('day_of_week', 0)),
                day_of_month=int(data.get('day_of_month', 1)),
                timezone=data.get('timezone', 'America/Toronto')
            )

            # Parse scheduled datetime for one-time
            scheduled_datetime = None
            if schedule_type == ScheduleType.ONE_TIME:
                date_str = data.get('scheduled_date', '')
                time_str = data.get('scheduled_time', '02:00')
                if date_str:
                    datetime_str = f"{date_str} {time_str}"
                    scheduled_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                    # Apply timezone
                    tz = ZoneInfo(preset_config.timezone)
                    scheduled_datetime = scheduled_datetime.replace(tzinfo=tz)

            # Parse AI pages mode
            ai_pages_mode_str = data.get('ai_pages_mode', 'all')
            ai_pages_mode = AITestMode(ai_pages_mode_str)

            # Parse selected AI page IDs
            ai_page_ids = []
            if ai_pages_mode == AITestMode.SELECTED:
                ai_page_ids = request.form.getlist('ai_page_ids')

            # Parse enabled touchpoints
            enabled_touchpoints = request.form.getlist('enabled_touchpoints')

            # Parse project user IDs
            project_user_ids = request.form.getlist('project_user_ids')

            # Create test config
            test_config = ScheduleTestConfig(
                run_ai_tests=data.get('run_ai_tests') == 'on',
                run_javascript_tests=data.get('run_javascript_tests', 'on') == 'on',
                run_python_tests=data.get('run_python_tests', 'on') == 'on',
                enabled_touchpoints=enabled_touchpoints,
                ai_pages_mode=ai_pages_mode,
                ai_page_ids=ai_page_ids,
                take_screenshots=data.get('take_screenshots', 'on') == 'on'
            )

            # Create schedule
            schedule = TestSchedule(
                website_id=website_id,
                name=data.get('name', '').strip(),
                description=data.get('description', '').strip() or None,
                schedule_type=schedule_type,
                scheduled_datetime=scheduled_datetime,
                cron_expression=data.get('cron_expression', '').strip() or None,
                preset_config=preset_config,
                test_config=test_config,
                project_user_ids=project_user_ids,
                enabled=data.get('enabled') == 'on',
                created_by=current_user.id if current_user.is_authenticated else None
            )

            # Save to database
            schedule_id = current_app.db.create_test_schedule(schedule)

            # Register with scheduler if enabled
            scheduler = get_scheduler_service()
            if scheduler and schedule.enabled:
                schedule = current_app.db.get_test_schedule(schedule_id)
                scheduler._register_schedule_with_apscheduler(schedule)

            flash(f'Schedule "{schedule.name}" created successfully', 'success')
            return redirect(url_for('schedules.list_schedules', website_id=website_id))

        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            flash(f'Error creating schedule: {str(e)}', 'error')

    # Get pages for AI selection
    pages = current_app.db.get_pages(website_id)

    # Get project users
    project_users = current_app.db.get_project_users(project.id, enabled_only=True)

    # Get touchpoints from touchpoint_tests mapping
    from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING
    touchpoints = list(TOUCHPOINT_TEST_MAPPING.keys())

    return render_template('schedules/form.html',
                         website=website,
                         project=project,
                         schedule=None,
                         pages=pages,
                         project_users=project_users,
                         touchpoints=touchpoints,
                         schedule_types=ScheduleType,
                         ai_modes=AITestMode,
                         is_edit=False)


@schedules_bp.route('/websites/<website_id>/schedules/<schedule_id>')
def view_schedule(website_id, schedule_id):
    """View schedule details"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    schedule = current_app.db.get_test_schedule(schedule_id)
    if not schedule:
        flash('Schedule not found', 'error')
        return redirect(url_for('schedules.list_schedules', website_id=website_id))

    project = current_app.db.get_project(website.project_id)

    # Get scheduler status
    scheduler = get_scheduler_service()
    scheduler_status = scheduler.get_job_status(schedule_id) if scheduler else {"status": "scheduler_not_available"}

    # Get next run times
    next_runs = scheduler.get_next_run_times(schedule_id, 5) if scheduler else []

    return render_template('schedules/view.html',
                         website=website,
                         project=project,
                         schedule=schedule,
                         scheduler_status=scheduler_status,
                         next_runs=next_runs)


@schedules_bp.route('/websites/<website_id>/schedules/<schedule_id>/edit', methods=['GET', 'POST'])
def edit_schedule(website_id, schedule_id):
    """Edit an existing schedule"""
    website = current_app.db.get_website(website_id)
    if not website:
        flash('Website not found', 'error')
        return redirect(url_for('index'))

    schedule = current_app.db.get_test_schedule(schedule_id)
    if not schedule:
        flash('Schedule not found', 'error')
        return redirect(url_for('schedules.list_schedules', website_id=website_id))

    project = current_app.db.get_project(website.project_id)

    if request.method == 'POST':
        try:
            data = request.form

            # Update schedule fields
            schedule.name = data.get('name', '').strip()
            schedule.description = data.get('description', '').strip() or None

            # Parse schedule type
            schedule_type_str = data.get('schedule_type', 'daily')
            schedule.schedule_type = ScheduleType(schedule_type_str)

            # Parse preset config
            schedule.preset_config = PresetConfig(
                time=data.get('time', '02:00'),
                day_of_week=int(data.get('day_of_week', 0)),
                day_of_month=int(data.get('day_of_month', 1)),
                timezone=data.get('timezone', 'America/Toronto')
            )

            # Parse scheduled datetime for one-time
            if schedule.schedule_type == ScheduleType.ONE_TIME:
                date_str = data.get('scheduled_date', '')
                time_str = data.get('scheduled_time', '02:00')
                if date_str:
                    datetime_str = f"{date_str} {time_str}"
                    scheduled_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                    tz = ZoneInfo(schedule.preset_config.timezone)
                    schedule.scheduled_datetime = scheduled_datetime.replace(tzinfo=tz)
            else:
                schedule.scheduled_datetime = None

            schedule.cron_expression = data.get('cron_expression', '').strip() or None

            # Parse AI pages mode
            ai_pages_mode_str = data.get('ai_pages_mode', 'all')
            ai_pages_mode = AITestMode(ai_pages_mode_str)

            # Parse selected AI page IDs
            ai_page_ids = []
            if ai_pages_mode == AITestMode.SELECTED:
                ai_page_ids = request.form.getlist('ai_page_ids')

            # Parse enabled touchpoints
            enabled_touchpoints = request.form.getlist('enabled_touchpoints')

            # Parse project user IDs
            project_user_ids = request.form.getlist('project_user_ids')

            # Update test config
            schedule.test_config = ScheduleTestConfig(
                run_ai_tests=data.get('run_ai_tests') == 'on',
                run_javascript_tests=data.get('run_javascript_tests', 'on') == 'on',
                run_python_tests=data.get('run_python_tests', 'on') == 'on',
                enabled_touchpoints=enabled_touchpoints,
                ai_pages_mode=ai_pages_mode,
                ai_page_ids=ai_page_ids,
                take_screenshots=data.get('take_screenshots', 'on') == 'on'
            )

            schedule.project_user_ids = project_user_ids
            schedule.enabled = data.get('enabled') == 'on'

            # Save to database
            current_app.db.update_test_schedule(schedule)

            # Update scheduler
            scheduler = get_scheduler_service()
            if scheduler:
                if schedule.enabled:
                    scheduler._register_schedule_with_apscheduler(schedule)
                else:
                    scheduler.remove_from_apscheduler(schedule_id)

            flash(f'Schedule "{schedule.name}" updated successfully', 'success')
            return redirect(url_for('schedules.view_schedule', website_id=website_id, schedule_id=schedule_id))

        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            flash(f'Error updating schedule: {str(e)}', 'error')

    # Get pages for AI selection
    pages = current_app.db.get_pages(website_id)

    # Get project users
    project_users = current_app.db.get_project_users(project.id, enabled_only=True)

    # Get touchpoints from touchpoint_tests mapping
    from auto_a11y.config.touchpoint_tests import TOUCHPOINT_TEST_MAPPING
    touchpoints = list(TOUCHPOINT_TEST_MAPPING.keys())

    return render_template('schedules/form.html',
                         website=website,
                         project=project,
                         schedule=schedule,
                         pages=pages,
                         project_users=project_users,
                         touchpoints=touchpoints,
                         schedule_types=ScheduleType,
                         ai_modes=AITestMode,
                         is_edit=True)


@schedules_bp.route('/websites/<website_id>/schedules/<schedule_id>/delete', methods=['POST'])
def delete_schedule(website_id, schedule_id):
    """Delete a schedule"""
    schedule = current_app.db.get_test_schedule(schedule_id)
    if not schedule:
        flash('Schedule not found', 'error')
        return redirect(url_for('schedules.list_schedules', website_id=website_id))

    # Remove from scheduler
    scheduler = get_scheduler_service()
    if scheduler:
        scheduler.remove_from_apscheduler(schedule_id)

    # Delete from database
    current_app.db.delete_test_schedule(schedule_id)

    flash(f'Schedule "{schedule.name}" deleted', 'success')
    return redirect(url_for('schedules.list_schedules', website_id=website_id))


@schedules_bp.route('/websites/<website_id>/schedules/<schedule_id>/toggle', methods=['POST'])
def toggle_schedule(website_id, schedule_id):
    """Enable or disable a schedule"""
    schedule = current_app.db.get_test_schedule(schedule_id)
    if not schedule:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Schedule not found'}), 404
        flash('Schedule not found', 'error')
        return redirect(url_for('schedules.list_schedules', website_id=website_id))

    # Toggle enabled state
    new_state = not schedule.enabled

    # Update database
    current_app.db.toggle_test_schedule(schedule_id, new_state)

    # Update scheduler
    scheduler = get_scheduler_service()
    if scheduler:
        if new_state:
            schedule = current_app.db.get_test_schedule(schedule_id)
            scheduler._register_schedule_with_apscheduler(schedule)
        else:
            scheduler.remove_from_apscheduler(schedule_id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'enabled': new_state,
            'message': f"Schedule {'enabled' if new_state else 'disabled'}"
        })

    flash(f'Schedule {"enabled" if new_state else "disabled"}', 'success')
    return redirect(url_for('schedules.list_schedules', website_id=website_id))


@schedules_bp.route('/websites/<website_id>/schedules/<schedule_id>/run-now', methods=['POST'])
def run_now(website_id, schedule_id):
    """Trigger immediate execution of a schedule"""
    schedule = current_app.db.get_test_schedule(schedule_id)
    if not schedule:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Schedule not found'}), 404
        flash('Schedule not found', 'error')
        return redirect(url_for('schedules.list_schedules', website_id=website_id))

    # Trigger immediate execution
    scheduler = get_scheduler_service()
    if scheduler:
        job_id = scheduler.run_now(schedule_id)
        if job_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'message': 'Test run started'
                })
            flash('Test run started', 'success')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Failed to start test run'}), 500
            flash('Failed to start test run', 'error')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Scheduler not available'}), 500
        flash('Scheduler not available', 'error')

    return redirect(url_for('schedules.view_schedule', website_id=website_id, schedule_id=schedule_id))


@schedules_bp.route('/websites/<website_id>/schedules/<schedule_id>/preview')
def preview_runs(website_id, schedule_id):
    """Preview next run times for a schedule"""
    schedule = current_app.db.get_test_schedule(schedule_id)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404

    scheduler = get_scheduler_service()
    if not scheduler:
        return jsonify({'error': 'Scheduler not available'}), 500

    count = request.args.get('count', 5, type=int)
    next_runs = scheduler.get_next_run_times(schedule_id, count)

    return jsonify({
        'schedule_id': schedule_id,
        'next_runs': [dt.isoformat() for dt in next_runs]
    })
