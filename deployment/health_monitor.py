"""
Health Monitoring System
Provides HTTP endpoint for health checks and system metrics
"""

import os
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger


class HealthMonitor:
    """
    Monitors system health and provides metrics
    """

    def __init__(self):
        """Initialize health monitor"""
        self.audit_logger = AuditLogger()
        self.start_time = datetime.now()
        self.last_iteration_time = None
        self.iteration_count = 0
        self.error_count = 0
        self.task_counts = {
            'total_processed': 0,
            'total_executed': 0,
            'emails_checked': 0,
            'social_mentions_checked': 0
        }

    def update_iteration(self, stats: Dict[str, Any]):
        """Update metrics from iteration stats"""
        self.last_iteration_time = datetime.now()
        self.iteration_count += 1

        self.task_counts['total_processed'] += stats.get('inbox_processed', 0)
        self.task_counts['total_executed'] += stats.get('needs_action_processed', 0)
        self.task_counts['emails_checked'] += stats.get('emails_checked', 0)
        self.task_counts['social_mentions_checked'] += stats.get('social_mentions_checked', 0)
        self.error_count += stats.get('errors', 0)

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': memory.used / (1024 * 1024),
                'memory_total_mb': memory.total / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024 * 1024 * 1024),
                'disk_total_gb': disk.total / (1024 * 1024 * 1024)
            }
        except Exception as e:
            return {'error': str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """Get complete health status"""
        uptime = (datetime.now() - self.start_time).total_seconds()

        # Determine health status
        status = 'healthy'
        issues = []

        # Check if iterations are happening
        if self.last_iteration_time:
            seconds_since_last = (datetime.now() - self.last_iteration_time).total_seconds()
            if seconds_since_last > 300:  # 5 minutes
                status = 'unhealthy'
                issues.append(f'No iteration in {int(seconds_since_last)} seconds')

        # Check error rate
        if self.iteration_count > 0:
            error_rate = (self.error_count / self.iteration_count) * 100
            if error_rate > 10:
                status = 'degraded'
                issues.append(f'High error rate: {error_rate:.1f}%')

        # Get system metrics
        system_metrics = self.get_system_metrics()

        # Check resource usage
        if system_metrics.get('cpu_percent', 0) > 90:
            status = 'degraded'
            issues.append('High CPU usage')

        if system_metrics.get('memory_percent', 0) > 90:
            status = 'degraded'
            issues.append('High memory usage')

        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_uptime(uptime),
            'iterations': {
                'total': self.iteration_count,
                'last_iteration': self.last_iteration_time.isoformat() if self.last_iteration_time else None,
                'error_count': self.error_count
            },
            'tasks': self.task_counts,
            'system': system_metrics,
            'issues': issues
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")

        return " ".join(parts)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoint"""

    health_monitor = None

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_health_response()
        elif self.path == '/metrics':
            self.send_metrics_response()
        elif self.path == '/':
            self.send_dashboard_response()
        else:
            self.send_error(404, "Not Found")

    def send_health_response(self):
        """Send health check response"""
        if not self.health_monitor:
            self.send_error(500, "Health monitor not initialized")
            return

        health = self.health_monitor.get_health_status()

        # Set HTTP status based on health
        status_code = 200
        if health['status'] == 'degraded':
            status_code = 200  # Still operational
        elif health['status'] == 'unhealthy':
            status_code = 503  # Service unavailable

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(health, indent=2).encode())

    def send_metrics_response(self):
        """Send metrics response"""
        if not self.health_monitor:
            self.send_error(500, "Health monitor not initialized")
            return

        health = self.health_monitor.get_health_status()

        # Prometheus-style metrics
        metrics = []
        metrics.append(f"# HELP goldtier_uptime_seconds System uptime in seconds")
        metrics.append(f"# TYPE goldtier_uptime_seconds gauge")
        metrics.append(f"goldtier_uptime_seconds {health['uptime_seconds']}")
        metrics.append("")

        metrics.append(f"# HELP goldtier_iterations_total Total number of iterations")
        metrics.append(f"# TYPE goldtier_iterations_total counter")
        metrics.append(f"goldtier_iterations_total {health['iterations']['total']}")
        metrics.append("")

        metrics.append(f"# HELP goldtier_errors_total Total number of errors")
        metrics.append(f"# TYPE goldtier_errors_total counter")
        metrics.append(f"goldtier_errors_total {health['iterations']['error_count']}")
        metrics.append("")

        metrics.append(f"# HELP goldtier_tasks_processed_total Total tasks processed")
        metrics.append(f"# TYPE goldtier_tasks_processed_total counter")
        metrics.append(f"goldtier_tasks_processed_total {health['tasks']['total_processed']}")
        metrics.append("")

        metrics.append(f"# HELP goldtier_cpu_percent CPU usage percentage")
        metrics.append(f"# TYPE goldtier_cpu_percent gauge")
        metrics.append(f"goldtier_cpu_percent {health['system'].get('cpu_percent', 0)}")
        metrics.append("")

        metrics.append(f"# HELP goldtier_memory_percent Memory usage percentage")
        metrics.append(f"# TYPE goldtier_memory_percent gauge")
        metrics.append(f"goldtier_memory_percent {health['system'].get('memory_percent', 0)}")

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()

        self.wfile.write("\n".join(metrics).encode())

    def send_dashboard_response(self):
        """Send HTML dashboard response"""
        if not self.health_monitor:
            self.send_error(500, "Health monitor not initialized")
            return

        health = self.health_monitor.get_health_status()

        # Status color
        status_color = {
            'healthy': '#28a745',
            'degraded': '#ffc107',
            'unhealthy': '#dc3545'
        }.get(health['status'], '#6c757d')

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gold Tier Employee - Health Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .status {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            background-color: {status_color};
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .issues {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 6px;
            margin-top: 20px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Gold Tier Autonomous Employee</h1>
        <p>Status: <span class="status">{health['status'].upper()}</span></p>
        <p>Uptime: {health['uptime_formatted']}</p>

        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Iterations</div>
                <div class="metric-value">{health['iterations']['total']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Tasks Processed</div>
                <div class="metric-value">{health['tasks']['total_processed']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Tasks Executed</div>
                <div class="metric-value">{health['tasks']['total_executed']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Emails Checked</div>
                <div class="metric-value">{health['tasks']['emails_checked']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Social Mentions</div>
                <div class="metric-value">{health['tasks']['social_mentions_checked']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Errors</div>
                <div class="metric-value">{health['iterations']['error_count']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">CPU Usage</div>
                <div class="metric-value">{health['system'].get('cpu_percent', 0):.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Memory Usage</div>
                <div class="metric-value">{health['system'].get('memory_percent', 0):.1f}%</div>
            </div>
        </div>

        {'<div class="issues"><strong>Issues:</strong><ul>' + ''.join([f'<li>{issue}</li>' for issue in health['issues']]) + '</ul></div>' if health['issues'] else ''}

        <p class="timestamp">Last updated: {health['timestamp']}<br>Auto-refresh every 10 seconds</p>
    </div>
</body>
</html>
"""

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class HealthCheckServer:
    """HTTP server for health checks"""

    def __init__(self, health_monitor: HealthMonitor, port: int = 8080):
        """Initialize health check server"""
        self.health_monitor = health_monitor
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """Start health check server in background thread"""
        HealthCheckHandler.health_monitor = self.health_monitor

        self.server = HTTPServer(('0.0.0.0', self.port), HealthCheckHandler)

        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        print(f"[Health Monitor] HTTP server started on port {self.port}")
        print(f"[Health Monitor] Dashboard: http://localhost:{self.port}/")
        print(f"[Health Monitor] Health check: http://localhost:{self.port}/health")
        print(f"[Health Monitor] Metrics: http://localhost:{self.port}/metrics")

    def stop(self):
        """Stop health check server"""
        if self.server:
            self.server.shutdown()
            print("[Health Monitor] HTTP server stopped")


if __name__ == "__main__":
    # Test health monitor
    monitor = HealthMonitor()

    # Simulate some activity
    monitor.update_iteration({
        'inbox_processed': 5,
        'needs_action_processed': 3,
        'emails_checked': 2,
        'social_mentions_checked': 1,
        'errors': 0
    })

    # Start server
    server = HealthCheckServer(monitor, port=8080)
    server.start()

    print("\nHealth monitor running. Press Ctrl+C to stop.")
    print("Open http://localhost:8080/ in your browser")

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        server.stop()
