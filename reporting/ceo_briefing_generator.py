"""
CEO Briefing Generator
Creates professional weekly executive reports
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
sys.path.append(str(Path(__file__).parent.parent))

from reporting.metrics_aggregator import MetricsAggregator


class CEOBriefingGenerator:
    """
    Generates CEO briefing reports in HTML and text formats
    """

    def __init__(self):
        """Initialize briefing generator"""
        self.project_root = Path(__file__).parent.parent
        self.briefings_dir = self.project_root / "Briefings"
        self.briefings_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_aggregator = MetricsAggregator()

    def generate_weekly_briefing(self, end_date: datetime = None) -> Dict[str, Any]:
        """
        Generate weekly CEO briefing

        Args:
            end_date: End of reporting period (defaults to now)

        Returns:
            Dictionary with report paths and metadata
        """
        if end_date is None:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=7)

        # Get metrics with comparison
        comparison = self.metrics_aggregator.get_comparison_metrics(start_date, end_date)

        # Generate report content
        html_content = self._generate_html_report(comparison)
        text_content = self._generate_text_report(comparison)

        # Save reports
        timestamp = end_date.strftime('%Y%m%d')
        html_path = self.briefings_dir / f"ceo_briefing_{timestamp}.html"
        text_path = self.briefings_dir / f"ceo_briefing_{timestamp}.txt"
        json_path = self.briefings_dir / f"ceo_briefing_{timestamp}.json"

        html_path.write_text(html_content, encoding='utf-8')
        text_path.write_text(text_content, encoding='utf-8')
        json_path.write_text(json.dumps(comparison, indent=2), encoding='utf-8')

        return {
            'html_path': str(html_path),
            'text_path': str(text_path),
            'json_path': str(json_path),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }

    def _generate_html_report(self, comparison: Dict[str, Any]) -> str:
        """Generate HTML version of the report"""
        current = comparison['current']
        previous = comparison['previous']
        changes = comparison['changes']

        # Format period
        start_date = datetime.fromisoformat(current['period']['start'])
        end_date = datetime.fromisoformat(current['period']['end'])
        period_str = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

        # Helper function for change indicators
        def change_indicator(value: float) -> str:
            if value > 0:
                return f'<span style="color: #28a745;">▲ {value:+.1f}%</span>'
            elif value < 0:
                return f'<span style="color: #dc3545;">▼ {value:+.1f}%</span>'
            else:
                return '<span style="color: #6c757d;">— 0%</span>'

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CEO Weekly Briefing - {period_str}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .header-info {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .metric-change {{
            font-size: 14px;
        }}
        .summary-box {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .highlight {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 CEO Weekly Briefing</h1>

        <div class="header-info">
            <strong>Reporting Period:</strong> {period_str}<br>
            <strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br>
            <strong>System:</strong> Gold Tier Autonomous Employee
        </div>

        <div class="summary-box">
            <h3 style="margin-top: 0;">Executive Summary</h3>
            <p>
                This week, the autonomous employee processed <strong>{current['tasks']['total_executed']}</strong> tasks,
                created <strong>{current['odoo']['customers_created']}</strong> new customers and
                <strong>{current['odoo']['leads_created']}</strong> leads in the CRM.
                The system maintained <strong>{current['system']['uptime_hours']:.1f} hours</strong> of uptime
                with <strong>{current['errors']['total_errors']}</strong> errors reported.
            </p>
        </div>

        <h2>📈 Key Performance Indicators</h2>

        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Tasks Executed</div>
                <div class="metric-value">{current['tasks']['total_executed']}</div>
                <div class="metric-change">vs last week: {change_indicator(changes.get('tasks_change', 0))}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">New Customers</div>
                <div class="metric-value">{current['odoo']['customers_created']}</div>
                <div class="metric-change">vs last week: {change_indicator(changes.get('customers_change', 0))}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">New Leads</div>
                <div class="metric-value">{current['odoo']['leads_created']}</div>
                <div class="metric-change">vs last week: {change_indicator(changes.get('leads_change', 0))}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">System Uptime</div>
                <div class="metric-value">{current['system']['uptime_hours']:.1f}h</div>
                <div class="metric-change">Total hours operational</div>
            </div>
        </div>

        <h2>📧 Email Operations</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>This Week</th>
                <th>Last Week</th>
            </tr>
            <tr>
                <td>Emails Received</td>
                <td>{current['email']['emails_received']}</td>
                <td>{previous['email']['emails_received']}</td>
            </tr>
            <tr>
                <td>Auto-Responses Sent</td>
                <td>{current['email']['emails_responded']}</td>
                <td>{previous['email']['emails_responded']}</td>
            </tr>
            <tr>
                <td>Response Rate</td>
                <td>{current['email']['response_rate']:.1f}%</td>
                <td>{previous['email']['response_rate']:.1f}%</td>
            </tr>
        </table>

        <h2>📱 Social Media Engagement</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>This Week</th>
                <th>Last Week</th>
            </tr>
            <tr>
                <td>Mentions Detected</td>
                <td>{current['social_media']['mentions_detected']}</td>
                <td>{previous['social_media']['mentions_detected']}</td>
            </tr>
            <tr>
                <td>Leads Generated</td>
                <td>{current['social_media']['leads_generated']}</td>
                <td>{previous['social_media']['leads_generated']}</td>
            </tr>
        </table>

        <h2>🔧 System Health</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>This Week</th>
                <th>Last Week</th>
            </tr>
            <tr>
                <td>Total Iterations</td>
                <td>{current['system']['total_iterations']}</td>
                <td>{previous['system']['total_iterations']}</td>
            </tr>
            <tr>
                <td>Errors</td>
                <td>{current['errors']['total_errors']}</td>
                <td>{previous['errors']['total_errors']}</td>
            </tr>
            <tr>
                <td>Warnings</td>
                <td>{current['errors']['warnings']}</td>
                <td>{previous['errors']['warnings']}</td>
            </tr>
            <tr>
                <td>Critical Issues</td>
                <td>{current['errors']['critical_errors']}</td>
                <td>{previous['errors']['critical_errors']}</td>
            </tr>
        </table>

        {self._generate_highlights_section(current, changes)}

        <div class="footer">
            <p>This report was automatically generated by the Gold Tier Autonomous Employee system.</p>
            <p>For detailed metrics and real-time monitoring, visit the health dashboard at http://localhost:8080/</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_text_report(self, comparison: Dict[str, Any]) -> str:
        """Generate plain text version of the report"""
        current = comparison['current']
        previous = comparison['previous']
        changes = comparison['changes']

        # Format period
        start_date = datetime.fromisoformat(current['period']['start'])
        end_date = datetime.fromisoformat(current['period']['end'])
        period_str = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

        text = f"""
{'='*60}
CEO WEEKLY BRIEFING
{'='*60}

Reporting Period: {period_str}
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
System: Gold Tier Autonomous Employee

{'='*60}
EXECUTIVE SUMMARY
{'='*60}

This week, the autonomous employee processed {current['tasks']['total_executed']} tasks,
created {current['odoo']['customers_created']} new customers and {current['odoo']['leads_created']} leads in the CRM.
The system maintained {current['system']['uptime_hours']:.1f} hours of uptime with
{current['errors']['total_errors']} errors reported.

{'='*60}
KEY PERFORMANCE INDICATORS
{'='*60}

Tasks Executed:     {current['tasks']['total_executed']}  (vs last week: {changes.get('tasks_change', 0):+.1f}%)
New Customers:      {current['odoo']['customers_created']}  (vs last week: {changes.get('customers_change', 0):+.1f}%)
New Leads:          {current['odoo']['leads_created']}  (vs last week: {changes.get('leads_change', 0):+.1f}%)
System Uptime:      {current['system']['uptime_hours']:.1f} hours

{'='*60}
EMAIL OPERATIONS
{'='*60}

                        This Week    Last Week
Emails Received:        {current['email']['emails_received']:>10}    {previous['email']['emails_received']:>10}
Auto-Responses Sent:    {current['email']['emails_responded']:>10}    {previous['email']['emails_responded']:>10}
Response Rate:          {current['email']['response_rate']:>9.1f}%    {previous['email']['response_rate']:>9.1f}%

{'='*60}
SOCIAL MEDIA ENGAGEMENT
{'='*60}

                        This Week    Last Week
Mentions Detected:      {current['social_media']['mentions_detected']:>10}    {previous['social_media']['mentions_detected']:>10}
Leads Generated:        {current['social_media']['leads_generated']:>10}    {previous['social_media']['leads_generated']:>10}

{'='*60}
SYSTEM HEALTH
{'='*60}

                        This Week    Last Week
Total Iterations:       {current['system']['total_iterations']:>10}    {previous['system']['total_iterations']:>10}
Errors:                 {current['errors']['total_errors']:>10}    {previous['errors']['total_errors']:>10}
Warnings:               {current['errors']['warnings']:>10}    {previous['errors']['warnings']:>10}
Critical Issues:        {current['errors']['critical_errors']:>10}    {previous['errors']['critical_errors']:>10}

{'='*60}

This report was automatically generated by the Gold Tier Autonomous Employee system.
For detailed metrics and real-time monitoring, visit: http://localhost:8080/

{'='*60}
"""
        return text

    def _generate_highlights_section(self, current: Dict[str, Any], changes: Dict[str, Any]) -> str:
        """Generate highlights and notable events section"""
        highlights = []

        # Check for significant improvements
        if changes.get('tasks_change', 0) > 20:
            highlights.append(f"Task processing increased by {changes['tasks_change']:.1f}% - excellent productivity!")

        if changes.get('customers_change', 0) > 20:
            highlights.append(f"Customer acquisition up {changes['customers_change']:.1f}% - strong growth!")

        # Check for concerns
        if changes.get('errors_change', 0) > 50:
            highlights.append(f"Error rate increased by {changes['errors_change']:.1f}% - requires attention")

        if current['errors']['critical_errors'] > 0:
            highlights.append(f"{current['errors']['critical_errors']} critical errors detected - immediate review recommended")

        # Check for perfect performance
        if current['errors']['total_errors'] == 0:
            highlights.append("Zero errors this week - perfect system performance!")

        if not highlights:
            return ""

        html = '<div class="highlight"><h3 style="margin-top: 0;">📌 Highlights & Notable Events</h3><ul>'
        for highlight in highlights:
            html += f'<li>{highlight}</li>'
        html += '</ul></div>'

        return html


if __name__ == "__main__":
    # Test briefing generator
    generator = CEOBriefingGenerator()

    print("="*60)
    print("CEO BRIEFING GENERATOR TEST")
    print("="*60)
    print()

    # Generate briefing
    result = generator.generate_weekly_briefing()

    print("Briefing generated successfully!")
    print(f"  HTML: {result['html_path']}")
    print(f"  Text: {result['text_path']}")
    print(f"  JSON: {result['json_path']}")
    print(f"  Period: {result['period']['start']} to {result['period']['end']}")
    print()

    print("[SUCCESS] CEO briefing generator working correctly!")
