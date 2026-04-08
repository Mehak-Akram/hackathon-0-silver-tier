"""
Task Processor
Reads and processes tasks from the Inbox folder
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.audit_logger_simple import AuditLogger
from src.risk_engine_simple import RiskEngine

class TaskProcessor:
    """
    Processes tasks from Inbox folder and routes them for execution
    """

    def __init__(self, inbox_path: str = None):
        """Initialize task processor"""
        self.inbox_path = Path(inbox_path or os.getenv('INBOX_PATH', './Inbox'))
        self.needs_action_path = Path('./Needs_Action')
        self.pending_approval_path = Path('./Pending_Approval')
        self.rejected_path = Path('./Rejected')

        # Ensure directories exist
        for path in [self.inbox_path, self.needs_action_path,
                     self.pending_approval_path, self.rejected_path]:
            path.mkdir(parents=True, exist_ok=True)

        self.audit_logger = AuditLogger()
        self.risk_engine = RiskEngine()

    def scan_inbox(self) -> List[Path]:
        """
        Scan inbox for new tasks

        Returns:
            List of task file paths
        """
        tasks = []

        # Look for JSON and TXT files
        for pattern in ['*.json', '*.txt', '*.md']:
            tasks.extend(self.inbox_path.glob(pattern))

        return sorted(tasks, key=lambda p: p.stat().st_mtime)

    def read_task(self, task_path: Path) -> Optional[Dict[str, Any]]:
        """
        Read and parse task file

        Args:
            task_path: Path to task file

        Returns:
            Task dictionary or None if invalid
        """
        try:
            content = task_path.read_text(encoding='utf-8')

            # Try to parse as JSON
            if task_path.suffix == '.json':
                task = json.loads(content)
            else:
                # Plain text - create structured task
                task = {
                    'type': 'text_task',
                    'content': content,
                    'source': 'inbox',
                    'timestamp': datetime.now().isoformat()
                }

            # Add metadata
            task['file_name'] = task_path.name
            task['file_path'] = str(task_path)

            return task

        except Exception as e:
            self.audit_logger.log_event(
                event_type='task_read_error',
                details={'file': str(task_path), 'error': str(e)},
                severity='error'
            )
            return None

    def classify_task(self, task: Dict[str, Any]) -> str:
        """
        Classify task type based on content

        Args:
            task: Task dictionary

        Returns:
            Task classification (email, social_media, odoo, general)
        """
        content = str(task.get('content', '')).lower()
        task_type = task.get('type', '').lower()

        # Check explicit type
        if task_type in ['email', 'social_media', 'odoo', 'crm']:
            return task_type

        # Classify by keywords
        if any(word in content for word in ['email', 'send message', 'contact']):
            return 'email'

        if any(word in content for word in ['facebook', 'twitter', 'instagram', 'post', 'social']):
            return 'social_media'

        if any(word in content for word in ['customer', 'lead', 'crm', 'odoo', 'invoice']):
            return 'odoo'

        return 'general'

    def assess_risk(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk level of task

        Args:
            task: Task dictionary

        Returns:
            Risk assessment result
        """
        task_type = self.classify_task(task)
        content = task.get('content', '')

        # Use simple risk engine
        risk_level, risk_score = self.risk_engine.assess_risk(
            task_type,
            {'content': content, 'source': task.get('source', 'unknown')}
        )

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'task_type': task_type
        }

    def route_task(self, task: Dict[str, Any], risk_assessment: Dict[str, Any]) -> str:
        """
        Route task to appropriate folder based on risk

        Args:
            task: Task dictionary
            risk_assessment: Risk assessment result

        Returns:
            Destination folder name
        """
        risk_level = risk_assessment.get('risk_level', 'medium')

        if risk_level == 'high':
            return 'pending_approval'
        elif risk_level == 'medium':
            return 'needs_action'
        else:
            return 'needs_action'

    def move_task(self, task_path: Path, destination: str) -> Path:
        """
        Move task file to destination folder

        Args:
            task_path: Source task path
            destination: Destination folder name

        Returns:
            New task path
        """
        dest_map = {
            'needs_action': self.needs_action_path,
            'pending_approval': self.pending_approval_path,
            'rejected': self.rejected_path
        }

        dest_path = dest_map.get(destination, self.needs_action_path)
        new_path = dest_path / task_path.name

        # Handle name conflicts
        counter = 1
        while new_path.exists():
            stem = task_path.stem
            suffix = task_path.suffix
            new_path = dest_path / f"{stem}_{counter}{suffix}"
            counter += 1

        task_path.rename(new_path)
        return new_path

    def process_task(self, task_path: Path) -> Dict[str, Any]:
        """
        Process a single task

        Args:
            task_path: Path to task file

        Returns:
            Processing result
        """
        # Read task
        task = self.read_task(task_path)
        if not task:
            return {
                'success': False,
                'error': 'Failed to read task',
                'file': str(task_path)
            }

        # Classify task
        task_type = self.classify_task(task)
        task['classified_type'] = task_type

        # Assess risk
        risk_assessment = self.assess_risk(task)

        # Route task
        destination = self.route_task(task, risk_assessment)

        # Move task
        new_path = self.move_task(task_path, destination)

        # Log processing
        self.audit_logger.log_event(
            event_type='task_processed',
            details={
                'file': task_path.name,
                'type': task_type,
                'risk_level': risk_assessment.get('risk_level'),
                'destination': destination,
                'new_path': str(new_path)
            },
            severity='info'
        )

        return {
            'success': True,
            'task': task,
            'risk_assessment': risk_assessment,
            'destination': destination,
            'new_path': str(new_path)
        }

    def process_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Process all tasks in inbox

        Returns:
            List of processing results
        """
        tasks = self.scan_inbox()
        results = []

        for task_path in tasks:
            result = self.process_task(task_path)
            results.append(result)

        return results
