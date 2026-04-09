"""
CEO Briefing CLI Tool
Command-line interface for generating and managing CEO briefings
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from reporting.ceo_briefing_generator import CEOBriefingGenerator
from reporting.ceo_briefing_email_sender import CEOBriefingEmailSender
from reporting.metrics_aggregator import MetricsAggregator


def generate_briefing(args):
    """Generate briefing without sending"""
    print("="*60)
    print("GENERATING CEO BRIEFING")
    print("="*60)
    print()

    generator = CEOBriefingGenerator()

    # Parse end date if provided
    end_date = None
    if args.date:
        try:
            end_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"[ERROR] Invalid date format: {args.date}")
            print("Use format: YYYY-MM-DD")
            return 1

    # Generate briefing
    result = generator.generate_weekly_briefing(end_date)

    print("[SUCCESS] Briefing generated!")
    print()
    print("Files created:")
    print(f"  HTML: {result['html_path']}")
    print(f"  Text: {result['text_path']}")
    print(f"  JSON: {result['json_path']}")
    print()
    print(f"Period: {result['period']['start']} to {result['period']['end']}")
    print()

    if args.open:
        import webbrowser
        webbrowser.open(result['html_path'])
        print("[INFO] Opening HTML report in browser...")

    return 0


def send_briefing(args):
    """Generate and send briefing via email"""
    print("="*60)
    print("GENERATING AND SENDING CEO BRIEFING")
    print("="*60)
    print()

    sender = CEOBriefingEmailSender()

    # Parse end date if provided
    end_date = None
    if args.date:
        try:
            end_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"[ERROR] Invalid date format: {args.date}")
            print("Use format: YYYY-MM-DD")
            return 1

    # Send briefing
    result = sender.send_weekly_briefing(end_date)

    if result['success']:
        print("[SUCCESS] Briefing sent!")
        print()
        print(f"Recipients: {', '.join(result['recipients'])}")
        print()
        print("Files created:")
        print(f"  HTML: {result['briefing']['html_path']}")
        print(f"  Text: {result['briefing']['text_path']}")
        print(f"  JSON: {result['briefing']['json_path']}")
        return 0
    else:
        print(f"[ERROR] {result['message']}")
        if 'note' in result:
            print(f"Note: {result['note']}")
        return 1


def show_metrics(args):
    """Show current metrics without generating report"""
    print("="*60)
    print("CURRENT METRICS")
    print("="*60)
    print()

    aggregator = MetricsAggregator()

    # Get metrics for specified period
    if args.days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

    metrics = aggregator.get_weekly_metrics(start_date, end_date)

    print(f"Period: {metrics['period']['start']} to {metrics['period']['end']}")
    print()

    print("System:")
    print(f"  Total iterations: {metrics['system']['total_iterations']}")
    print(f"  Uptime: {metrics['system']['uptime_hours']:.1f} hours")
    print()

    print("Tasks:")
    print(f"  Total processed: {metrics['tasks']['total_processed']}")
    print(f"  Total executed: {metrics['tasks']['total_executed']}")
    print(f"  Success rate: {metrics['tasks']['success_rate']:.1f}%")
    print()

    print("Odoo:")
    print(f"  Customers created: {metrics['odoo']['customers_created']}")
    print(f"  Leads created: {metrics['odoo']['leads_created']}")
    print()

    print("Email:")
    print(f"  Emails received: {metrics['email']['emails_received']}")
    print(f"  Auto-responses sent: {metrics['email']['emails_responded']}")
    print(f"  Response rate: {metrics['email']['response_rate']:.1f}%")
    print()

    print("Social Media:")
    print(f"  Mentions detected: {metrics['social_media']['mentions_detected']}")
    print(f"  Leads generated: {metrics['social_media']['leads_generated']}")
    print()

    print("Errors:")
    print(f"  Total errors: {metrics['errors']['total_errors']}")
    print(f"  Critical errors: {metrics['errors']['critical_errors']}")
    print(f"  Warnings: {metrics['errors']['warnings']}")
    print()

    return 0


def list_briefings(args):
    """List all generated briefings"""
    print("="*60)
    print("GENERATED BRIEFINGS")
    print("="*60)
    print()

    briefings_dir = Path(__file__).parent.parent / "Briefings"

    if not briefings_dir.exists():
        print("[INFO] No briefings directory found")
        return 0

    html_files = sorted(briefings_dir.glob('ceo_briefing_*.html'), reverse=True)

    if not html_files:
        print("[INFO] No briefings found")
        return 0

    print(f"Found {len(html_files)} briefing(s):")
    print()

    for html_file in html_files:
        # Extract date from filename
        date_str = html_file.stem.replace('ceo_briefing_', '')
        try:
            date = datetime.strptime(date_str, '%Y%m%d')
            date_formatted = date.strftime('%B %d, %Y')
        except:
            date_formatted = date_str

        size_kb = html_file.stat().st_size / 1024

        print(f"  {date_formatted}")
        print(f"    HTML: {html_file}")
        print(f"    Size: {size_kb:.1f} KB")
        print()

    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CEO Briefing Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate briefing for current week
  python ceo_briefing_cli.py generate

  # Generate and open in browser
  python ceo_briefing_cli.py generate --open

  # Generate for specific date
  python ceo_briefing_cli.py generate --date 2026-04-08

  # Send briefing via email
  python ceo_briefing_cli.py send

  # Show current metrics
  python ceo_briefing_cli.py metrics

  # Show metrics for last 30 days
  python ceo_briefing_cli.py metrics --days 30

  # List all generated briefings
  python ceo_briefing_cli.py list
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate briefing without sending')
    generate_parser.add_argument('--date', help='End date (YYYY-MM-DD)')
    generate_parser.add_argument('--open', action='store_true', help='Open HTML report in browser')

    # Send command
    send_parser = subparsers.add_parser('send', help='Generate and send briefing via email')
    send_parser.add_argument('--date', help='End date (YYYY-MM-DD)')

    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Show current metrics')
    metrics_parser.add_argument('--days', type=int, default=7, help='Number of days to analyze (default: 7)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all generated briefings')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'generate':
        return generate_briefing(args)
    elif args.command == 'send':
        return send_briefing(args)
    elif args.command == 'metrics':
        return show_metrics(args)
    elif args.command == 'list':
        return list_briefings(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
