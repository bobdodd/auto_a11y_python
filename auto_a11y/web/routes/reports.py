"""
Report generation routes
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, url_for, flash, redirect
from auto_a11y.models import PageStatus
from auto_a11y.reporting import ReportGenerator, PageStructureReport
from auto_a11y.reporting.discovery_report import DiscoveryReportGenerator
from datetime import datetime
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)
reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/dashboard')
def reports_dashboard():
    """Reports dashboard"""
    # Get available reports
    reports_dir = current_app.app_config.REPORTS_DIR
    report_files = list(reports_dir.glob('*.xlsx')) + list(reports_dir.glob('*.html')) + list(reports_dir.glob('*.json')) + list(reports_dir.glob('*.pdf'))
    
    reports = []
    for file in sorted(report_files, key=lambda x: x.stat().st_mtime, reverse=True)[:20]:
        # Extract project name from filename if available
        filename_parts = file.stem.split('_')
        if len(filename_parts) > 1 and not filename_parts[0].isdigit():
            # Likely a project name, use it
            display_name = ' '.join(filename_parts[:-1]).replace('_', ' ').title()
        else:
            display_name = file.stem.replace('_', ' ').title()
            
        # Try to determine project name from filename
        project_name = None
        if 'all_projects' in file.stem.lower():
            project_name = 'All Projects'
        elif '_' in file.stem:
            # Try to extract project name from filename pattern
            name_parts = file.stem.split('_')
            if len(name_parts) > 2:
                # Skip timestamp parts at the end
                project_name = ' '.join(name_parts[:-2]).replace('_', ' ').title()
        
        reports.append({
            'filename': file.name,
            'name': display_name,
            'size_kb': file.stat().st_size,  # Pass bytes, template uses filesizeformat
            'created_at': datetime.fromtimestamp(file.stat().st_mtime),
            'type': file.suffix[1:].lower(),
            'project_name': project_name
        })
    
    # Get all projects for the dropdown
    projects = current_app.db.get_projects()
    
    # Get all websites for the dropdown
    websites = []
    for project in projects:
        project_websites = current_app.db.get_websites(project.id)
        for website in project_websites:
            websites.append({
                'id': str(website.id),
                'name': website.name,
                'project_id': str(project.id),
                'project_name': project.name
            })
    
    return render_template('reports/dashboard.html', 
                         reports=reports, 
                         projects=projects,
                         websites=websites)


@reports_bp.route('/generate', methods=['POST'])
def generate_report():
    """Generate accessibility report"""
    data = request.get_json()
    
    project_id = data.get('project_id')
    website_id = data.get('website_id')
    report_type = data.get('type', 'xlsx')
    report_name = data.get('name', f'Accessibility Report {datetime.now().strftime("%Y-%m-%d")}')
    include_options = {
        'violations': data.get('include_violations', True),
        'warnings': data.get('include_warnings', True),
        'ai': data.get('include_ai', True),
        'screenshots': data.get('include_screenshots', False),
        'summary': data.get('include_summary', True)
    }
    
    # Determine scope
    scope = 'all'
    scope_id = None
    
    if project_id:
        project = current_app.db.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        scope = 'project'
        scope_id = project_id
    elif website_id:
        website = current_app.db.get_website(website_id)
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        scope = 'website'
        scope_id = website_id
    
    try:
        # Initialize report generator
        from auto_a11y.reporting import ReportGenerator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report based on scope and type
        if report_type == 'excel' or report_type == 'xlsx':
            if scope == 'all':
                # Generate report for all projects
                report_path = generator.generate_all_projects_report(format='xlsx')
            elif scope == 'project':
                report_path = generator.generate_project_report(project_id=scope_id, format='xlsx')
            else:
                report_path = generator.generate_website_report(website_id=scope_id, format='xlsx')
        elif report_type == 'pdf':
            # Generate PDF report
            if scope == 'all':
                report_path = generator.generate_all_projects_report(format='pdf')
            elif scope == 'project':
                report_path = generator.generate_project_report(project_id=scope_id, format='pdf')
            else:
                report_path = generator.generate_website_report(website_id=scope_id, format='pdf')
        elif report_type == 'json':
            # Generate JSON report
            if scope == 'all':
                report_path = generator.generate_all_projects_report(format='json')
            elif scope == 'project':
                report_path = generator.generate_project_report(project_id=scope_id, format='json')
            else:
                report_path = generator.generate_website_report(website_id=scope_id, format='json')
        else:
            # HTML report
            if scope == 'all':
                report_path = generator.generate_all_projects_report(format='html')
            elif scope == 'project':
                report_path = generator.generate_project_report(project_id=scope_id, format='html')
            else:
                report_path = generator.generate_website_report(website_id=scope_id, format='html')
        
        # Store report metadata (in production, this would be saved to database)
        report_id = f'report_{scope}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'message': f'Report generated successfully',
            'download_url': url_for('reports.download_report', filename=Path(report_path).name)
        })
        
    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/report/<report_id>/status')
def report_status(report_id):
    """Check report generation status"""
    # In production, check actual job status
    return jsonify({
        'report_id': report_id,
        'status': 'generating',
        'progress': 75,
        'message': 'Generating report...'
    })


@reports_bp.route('/download/<filename>')
def download_report(filename):
    """Download generated report"""
    reports_dir = current_app.app_config.REPORTS_DIR
    file_path = reports_dir / filename
    
    if not file_path.exists():
        return jsonify({'error': 'Report not found'}), 404
    
    # Security check - ensure file is in reports directory
    if not file_path.resolve().parent == reports_dir.resolve():
        return jsonify({'error': 'Invalid file path'}), 403
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )


@reports_bp.route('/project/<project_id>/summary')
def project_summary(project_id):
    """Generate project summary report"""
    project = current_app.db.get_project(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    stats = current_app.db.get_project_stats(project_id)
    websites = current_app.db.get_websites(project_id)
    
    # Get violation breakdown
    violation_summary = {
        'by_touchpoint': {},
        'by_severity': {
            'critical': 0,
            'serious': 0,
            'moderate': 0,
            'minor': 0
        },
        'top_issues': []
    }
    
    # Aggregate data from all test results
    for website in websites:
        pages = current_app.db.get_pages(website.id)
        for page in pages:
            if page.status == PageStatus.TESTED:
                result = current_app.db.get_latest_test_result(page.id)
                if result:
                    for violation in result.violations:
                        # Count by touchpoint
                        if violation.touchpoint not in violation_summary['by_touchpoint']:
                            violation_summary['by_touchpoint'][violation.touchpoint] = 0
                        violation_summary['by_touchpoint'][violation.touchpoint] += 1
                        
                        # Count by severity
                        violation_summary['by_severity'][violation.impact.value] += 1
    
    return render_template('reports/project_summary.html',
                         project=project,
                         stats=stats,
                         websites=websites,
                         violation_summary=violation_summary)


@reports_bp.route('/export-csv', methods=['POST'])
def export_csv():
    """Export data as CSV"""
    data = request.get_json()
    
    export_type = data.get('type')  # violations, pages, summary
    filters = data.get('filters', {})
    
    # Generate CSV based on type
    # This would be implemented with actual CSV generation
    
    return jsonify({
        'success': True,
        'message': 'CSV export started',
        'download_url': '/reports/download/export.csv'
    })


@reports_bp.route('/generate/page/<page_id>', methods=['POST'])
def generate_page_report(page_id):
    """Generate report for a single page"""
    format = request.form.get('format', 'html')
    include_ai = request.form.get('include_ai', 'true') == 'true'
    
    try:
        # Initialize report generator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report
        report_path = generator.generate_page_report(
            page_id=page_id,
            format=format,
            include_ai=include_ai
        )
        
        # Return file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=Path(report_path).name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate page report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('pages.view_page', page_id=page_id))


@reports_bp.route('/generate/website/<website_id>', methods=['POST'])
def generate_website_report(website_id):
    """Generate report for entire website"""
    format = request.form.get('format', 'html')
    include_ai = request.form.get('include_ai', 'true') == 'true'
    
    try:
        # Initialize report generator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report
        report_path = generator.generate_website_report(
            website_id=website_id,
            format=format,
            include_ai=include_ai
        )
        
        # Return file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=Path(report_path).name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate website report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('websites.view_website', website_id=website_id))


@reports_bp.route('/generate/project/<project_id>', methods=['POST'])
def generate_project_report(project_id):
    """Generate report for entire project"""
    format = request.form.get('format', 'html')
    
    try:
        # Initialize report generator
        generator = ReportGenerator(current_app.db, current_app.app_config.__dict__)
        
        # Generate report
        report_path = generator.generate_project_report(
            project_id=project_id,
            format=format
        )
        
        # Return file for download
        return send_file(
            report_path,
            as_attachment=True,
            download_name=Path(report_path).name
        )
        
    except Exception as e:
        logger.error(f"Failed to generate project report: {e}")
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('projects.view_project', project_id=project_id))


@reports_bp.route('/generate/page-structure/<website_id>', methods=['POST'])
def generate_page_structure_report(website_id):
    """Generate site structure tree report for website"""
    format = request.form.get('format', 'html')

    try:
        # Get website and pages
        website = current_app.db.get_website(website_id)
        if not website:
            return jsonify({'error': 'Website not found'}), 404

        # Get project if available
        project = None
        if website.project_id:
            project = current_app.db.get_project(website.project_id)

        pages = current_app.db.get_pages(website_id)
        if not pages:
            return jsonify({'error': 'No pages found for website'}), 404

        # Generate report with project information
        report = PageStructureReport(current_app.db, website, pages, project)
        report.generate()

        # Save report in requested format
        report_path = report.save(format)
        report_path = Path(report_path)

        # Return file
        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_path.name,
            mimetype={
                'html': 'text/html',
                'json': 'application/json',
                'csv': 'text/csv',
                'pdf': 'application/pdf'
            }.get(format, 'application/octet-stream')
        )

    except Exception as e:
        logger.error(f"Failed to generate page structure report: {e}")
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/generate/discovery/website/<website_id>', methods=['POST'])
def generate_discovery_website_report(website_id):
    """Generate discovery report for a website"""
    format = request.form.get('format', 'html')

    try:
        # Initialize discovery report generator
        generator = DiscoveryReportGenerator(
            current_app.db,
            current_app.app_config.__dict__
        )

        # Generate report (saves to reports directory)
        report_path = generator.generate_website_discovery_report(
            website_id=website_id,
            format=format
        )

        # Flash success message and redirect to dashboard
        flash(f'Discovery report generated successfully!', 'success')
        return redirect(url_for('reports.reports_dashboard'))

    except Exception as e:
        logger.error(f"Failed to generate discovery report: {e}", exc_info=True)
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('reports.reports_dashboard'))


@reports_bp.route('/generate/discovery/project/<project_id>', methods=['POST'])
def generate_discovery_project_report(project_id):
    """Generate discovery report for an entire project"""
    format = request.form.get('format', 'html')

    try:
        # Initialize discovery report generator
        generator = DiscoveryReportGenerator(
            current_app.db,
            current_app.app_config.__dict__
        )

        # Generate report (saves to reports directory)
        report_path = generator.generate_project_discovery_report(
            project_id=project_id,
            format=format
        )

        # Flash success message and redirect to dashboard
        flash(f'Discovery report generated successfully!', 'success')
        return redirect(url_for('reports.reports_dashboard'))

    except Exception as e:
        logger.error(f"Failed to generate discovery report: {e}", exc_info=True)
        flash(f'Failed to generate report: {str(e)}', 'error')
        return redirect(url_for('reports.reports_dashboard'))